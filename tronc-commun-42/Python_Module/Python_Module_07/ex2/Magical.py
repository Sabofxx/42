from abc import ABC, abstractmethod
from typing import List


class Magical(ABC):
    """Abstract magic interface."""

    @abstractmethod
    def cast_spell(
        self, spell_name: str, targets: List[str]
    ) -> dict:
        pass

    @abstractmethod
    def channel_mana(self, amount: int) -> dict:
        pass

    @abstractmethod
    def get_magic_stats(self) -> dict:
        pass
