from typing import Optional
from models.zone import Zone
from models.connection import Connection


class Network:
    def __init__(self, nb_drones: int) -> None:
        self.nb_drones = nb_drones
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.adjacency: dict[str, list[Connection]] = {}
        self.start_zone: Optional[str] = None
        self.end_zone: Optional[str] = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone
        if zone.name not in self.adjacency:
            self.adjacency[zone.name] = []
        if zone.is_start:
            self.start_zone = zone.name
        if zone.is_end:
            self.end_zone = zone.name

    def add_connection(self, conn: Connection) -> None:
        self.connections.append(conn)
        if conn.zone1_name not in self.adjacency:
            self.adjacency[conn.zone1_name] = []
        if conn.zone2_name not in self.adjacency:
            self.adjacency[conn.zone2_name] = []
        self.adjacency[conn.zone1_name].append(conn)
        self.adjacency[conn.zone2_name].append(conn)

    def get_neighbors(self, zone_name: str) -> list[tuple[str, Connection]]:
        result: list[tuple[str, Connection]] = []
        for conn in self.adjacency.get(zone_name, []):
            neighbor = conn.other(zone_name)
            result.append((neighbor, conn))
        return result

    def get_connection(
        self, zone1: str, zone2: str
    ) -> Optional[Connection]:
        for conn in self.adjacency.get(zone1, []):
            if conn.other(zone1) == zone2:
                return conn
        return None
