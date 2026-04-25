from typing import Optional
from models.network import Network
from models.drone import Drone, DroneState
from models.zone import ZoneType


class Simulation:
    def __init__(
        self, network: Network, drone_paths: list[list[str]]
    ) -> None:
        self.network = network
        self.drones: list[Drone] = []
        self.turn_log: list[str] = []
        self.turn_delivered: list[int] = []
        self.total_turns = 0

        start = network.start_zone
        if start is None:
            raise ValueError("Network has no start zone")

        for i in range(network.nb_drones):
            drone = Drone(i + 1, start)
            if i < len(drone_paths):
                drone.path = drone_paths[i]
            self.drones.append(drone)

    def _zone_occupancy(self, zone_name: str) -> int:
        count = 0
        for d in self.drones:
            if d.state == DroneState.DELIVERED:
                continue
            if d.state == DroneState.IN_TRANSIT:
                continue
            if d.current_zone == zone_name:
                count += 1
        return count

    def _link_usage(
        self, zone1: str, zone2: str,
        planned_moves: list[tuple[int, str, str]],
    ) -> int:
        conn = self.network.get_connection(zone1, zone2)
        if conn is None:
            return 0
        count = 0
        for d in self.drones:
            if d.state == DroneState.IN_TRANSIT:
                if d.transit_connection == conn.key:
                    count += 1
        for _, from_z, to_z in planned_moves:
            c = self.network.get_connection(from_z, to_z)
            if c and c.key == conn.key:
                count += 1
        return count

    def _plan_arrivals(self) -> list[tuple[int, str]]:
        arrivals: list[tuple[int, str]] = []
        for i, d in enumerate(self.drones):
            if d.state == DroneState.IN_TRANSIT and d.transit_target:
                arrivals.append((i, d.transit_target))
        return arrivals

    def _plan_departures(
        self, arrivals: list[tuple[int, str]]
    ) -> list[tuple[int, str, str]]:
        departing_from: dict[str, int] = {}
        for i, _ in arrivals:
            d = self.drones[i]
            zone = d.current_zone
            departing_from[zone] = departing_from.get(zone, 0) + 1

        arriving_at: dict[str, int] = {}
        for _, dest in arrivals:
            arriving_at[dest] = arriving_at.get(dest, 0) + 1

        moves: list[tuple[int, str, str]] = []
        move_departures: dict[str, int] = {}
        move_arrivals: dict[str, int] = {}

        sorted_drones = sorted(
            range(len(self.drones)),
            key=lambda i: (
                len(self.drones[i].path) - self.drones[i].path_index
                if self.drones[i].path else 999
            ),
        )

        for i in sorted_drones:
            d = self.drones[i]
            if d.state != DroneState.WAITING and d.state != DroneState.MOVING:
                continue
            if d.state == DroneState.IN_TRANSIT:
                continue
            if d.state == DroneState.DELIVERED:
                continue

            target = d.next_zone
            if target is None:
                continue

            target_zone = self.network.zones.get(target)
            if target_zone is None:
                continue
            if target_zone.zone_type == ZoneType.BLOCKED:
                continue

            conn = self.network.get_connection(d.current_zone, target)
            if conn is None:
                continue

            link_used = self._link_usage(d.current_zone, target, moves)
            if link_used >= conn.max_link_capacity:
                continue

            if not target_zone.is_end:
                current_occ = self._zone_occupancy(target)
                extra_arriving = (
                    arriving_at.get(target, 0)
                    + move_arrivals.get(target, 0)
                )
                extra_departing = move_departures.get(target, 0)
                net_occ = current_occ + extra_arriving - extra_departing
                if net_occ >= target_zone.max_drones:
                    if target_zone.movement_cost == 2:
                        pass
                    else:
                        continue

            if target_zone.movement_cost == 2:
                current_occ = self._zone_occupancy(target)
                extra_arriving = move_arrivals.get(target, 0)
                if current_occ + extra_arriving >= target_zone.max_drones:
                    if not target_zone.is_end:
                        continue

            moves.append((i, d.current_zone, target))
            move_departures[d.current_zone] = (
                move_departures.get(d.current_zone, 0) + 1
            )
            if target_zone.movement_cost < 2:
                move_arrivals[target] = (
                    move_arrivals.get(target, 0) + 1
                )

        return moves

    def _execute_turn(self) -> Optional[str]:
        arrivals = self._plan_arrivals()
        departures = self._plan_departures(arrivals)

        if not arrivals and not departures:
            all_done = all(
                d.state == DroneState.DELIVERED for d in self.drones
            )
            if all_done:
                return None
            has_pending = any(
                d.state in (DroneState.WAITING, DroneState.MOVING)
                for d in self.drones
            )
            if has_pending:
                return ""
            return None

        movements: list[str] = []

        for i, dest in arrivals:
            d = self.drones[i]
            d.current_zone = dest
            d.transit_target = None
            d.transit_connection = None
            d.state = DroneState.MOVING
            d.advance()
            movements.append(f"{d.label}-{dest}")
            end_zone = self.network.end_zone
            if dest == end_zone:
                d.state = DroneState.DELIVERED

        for i, from_z, to_z in departures:
            d = self.drones[i]
            target_zone = self.network.zones[to_z]

            if target_zone.movement_cost == 2:
                conn = self.network.get_connection(from_z, to_z)
                conn_name = f"{from_z}-{to_z}" if conn is None else (
                    f"{conn.zone1_name}-{conn.zone2_name}"
                )
                d.state = DroneState.IN_TRANSIT
                d.transit_target = to_z
                d.transit_connection = conn.key if conn else ""
                d.current_zone = from_z
                movements.append(f"{d.label}-{conn_name}")
            else:
                d.current_zone = to_z
                d.state = DroneState.MOVING
                d.advance()
                movements.append(f"{d.label}-{to_z}")
                end_zone = self.network.end_zone
                if to_z == end_zone:
                    d.state = DroneState.DELIVERED

        if movements:
            return " ".join(movements)
        return ""

    def run(self) -> list[str]:
        max_turns = self.network.nb_drones * 200
        turns: list[str] = []

        for _ in range(max_turns):
            all_done = all(
                d.state == DroneState.DELIVERED for d in self.drones
            )
            if all_done:
                break

            result = self._execute_turn()
            if result is None:
                break
            if result:
                turns.append(result)
                delivered = sum(
                    1 for d in self.drones
                    if d.state == DroneState.DELIVERED
                )
                self.turn_delivered.append(delivered)
            self.total_turns += 1

        self.turn_log = turns
        return turns
