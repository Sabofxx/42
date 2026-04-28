from abc import ABC, abstractmethod


class Combatable(ABC):
    """Abstract combat interface."""

    @abstractmethod
    def attack(self, target: str) -> dict:
        pass

    @abstractmethod
    def defend(self, incoming_damage: int) -> dict:
        pass

    @abstractmethod
    def get_combat_stats(self) -> dict:
        pass
