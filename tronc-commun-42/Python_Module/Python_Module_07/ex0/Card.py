from abc import ABC, abstractmethod


class Card(ABC):
    """Abstract base class for all cards."""

    def __init__(
        self, name: str, cost: int, rarity: str
    ) -> None:
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def play(self, game_state: dict) -> dict:
        """Play this card."""
        pass

    def get_card_info(self) -> dict:
        """Return card information."""
        return {
            "name": self.name,
            "cost": self.cost,
            "rarity": self.rarity,
        }

    def is_playable(
        self, available_mana: int
    ) -> bool:
        """Check if card can be played."""
        return available_mana >= self.cost
