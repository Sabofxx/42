from enum import Enum
from typing import Optional


class DroneState(Enum):
    WAITING = "waiting"
    MOVING = "moving"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Drone:
    def __init__(self, drone_id: int, start_zone: str) -> None:
        self.drone_id = drone_id
        self.current_zone = start_zone
        self.state = DroneState.WAITING
        self.path: list[str] = []
        self.path_index: int = 0
        self.transit_target: Optional[str] = None
        self.transit_connection: Optional[str] = None

    @property
    def label(self) -> str:
        return f"D{self.drone_id}"

    @property
    def next_zone(self) -> Optional[str]:
        if self.path_index < len(self.path):
            return self.path[self.path_index]
        return None

    def advance(self) -> None:
        self.path_index += 1

    def __repr__(self) -> str:
        return f"Drone({self.label}, at={self.current_zone})"
