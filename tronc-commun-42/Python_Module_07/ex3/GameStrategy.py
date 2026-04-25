from abc import ABC, abstractmethod
from typing import List


class GameStrategy(ABC):
    """Abstract strategy interface."""

    @abstractmethod
    def execute_turn(
        self, hand: List, battlefield: List
    ) -> dict:
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        pass

    @abstractmethod
    def prioritize_targets(
        self, available_targets: List
    ) -> List:
        pass
