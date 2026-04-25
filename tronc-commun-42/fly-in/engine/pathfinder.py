import heapq
from typing import Optional
from models.network import Network
from models.zone import ZoneType


class Pathfinder:
    def __init__(self, network: Network) -> None:
        self.network = network
        self._blocked: set[str] = set()
        for name, zone in network.zones.items():
            if zone.zone_type == ZoneType.BLOCKED:
                self._blocked.add(name)

    def _get_weight(self, zone_name: str) -> int:
        zone = self.network.zones[zone_name]
        if zone.zone_type == ZoneType.PRIORITY:
            return 0
        if zone.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def _find_all_paths_bfs(self, max_paths: int = 50) -> list[list[str]]:
        start = self.network.start_zone
        end = self.network.end_zone
        if start is None or end is None:
            return []

        paths: list[list[str]] = []
        node_usage: dict[str, int] = {}

        for _ in range(max_paths):
            path = self._dijkstra(node_usage)
            if path is None:
                break
            paths.append(path)
            for zone_name in path[1:-1]:
                node_usage[zone_name] = node_usage.get(zone_name, 0) + 1

        return paths

    def _dijkstra(
        self,
        node_usage: dict[str, int],
    ) -> Optional[list[str]]:
        start = self.network.start_zone
        end = self.network.end_zone
        if start is None or end is None:
            return None

        dist: dict[str, float] = {start: 0.0}
        prev: dict[str, Optional[str]] = {start: None}
        pq: list[tuple[float, int, str]] = [(0.0, 0, start)]
        counter = 1

        while pq:
            d, _, current = heapq.heappop(pq)
            if current == end:
                path: list[str] = []
                node: Optional[str] = end
                while node is not None:
                    path.append(node)
                    node = prev[node]
                path.reverse()
                return path

            if d > dist.get(current, float("inf")):
                continue

            for neighbor_name, conn in self.network.get_neighbors(current):
                if neighbor_name in self._blocked:
                    continue

                neighbor_zone = self.network.zones[neighbor_name]
                if neighbor_zone.movement_cost < 0:
                    continue

                if not neighbor_zone.is_start and not neighbor_zone.is_end:
                    used = node_usage.get(neighbor_name, 0)
                    if used >= neighbor_zone.max_drones:
                        continue

                w = self._get_weight(neighbor_name)
                new_dist = d + w
                if new_dist < dist.get(neighbor_name, float("inf")):
                    dist[neighbor_name] = new_dist
                    prev[neighbor_name] = current
                    heapq.heappush(pq, (new_dist, counter, neighbor_name))
                    counter += 1

        return None

    def find_augmenting_paths(self) -> list[list[str]]:
        return self._find_all_paths_bfs()

    def assign_drones(self) -> list[list[str]]:
        paths = self.find_augmenting_paths()
        if not paths:
            return []

        nb_drones = self.network.nb_drones

        if len(paths) == 1:
            return [paths[0][1:] for _ in range(nb_drones)]

        path_costs: list[int] = []
        for path in paths:
            cost = 0
            for zone_name in path[1:]:
                zone = self.network.zones[zone_name]
                mc = zone.movement_cost
                cost += mc if mc > 0 else 1
            path_costs.append(cost)

        drone_paths: list[list[str]] = []
        path_load: list[int] = [0] * len(paths)

        for _ in range(nb_drones):
            best_idx = 0
            best_finish = float("inf")
            for i in range(len(paths)):
                finish_time = path_costs[i] + path_load[i]
                if finish_time < best_finish or (
                    finish_time == best_finish
                    and path_costs[i] < path_costs[best_idx]
                ):
                    best_finish = finish_time
                    best_idx = i
            drone_paths.append(paths[best_idx][1:])
            path_load[best_idx] += 1

        return drone_paths
