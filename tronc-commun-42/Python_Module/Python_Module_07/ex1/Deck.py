import random
from typing import List

from ex0.Card import Card


class Deck:
    """Deck management system."""

    def __init__(self) -> None:
        self.cards: List[Card] = []

    def add_card(self, card: Card) -> None:
        """Add a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card_name: str) -> bool:
        """Remove a card by name."""
        for i, card in enumerate(self.cards):
            if card.name == card_name:
                self.cards.pop(i)
                return True
        return False

    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def draw_card(self) -> Card:
        """Draw the top card."""
        if not self.cards:
            raise ValueError("Deck is empty")
        return self.cards.pop(0)

    def get_deck_stats(self) -> dict:
        """Get deck statistics."""
        if not self.cards:
            return {
                "total_cards": 0,
                "avg_cost": 0,
            }
        creatures = 0
        spells = 0
        artifacts = 0
        for card in self.cards:
            info = card.get_card_info()
            card_type = info.get("type", "")
            if card_type == "Creature":
                creatures += 1
            elif card_type == "Spell":
                spells += 1
            elif card_type == "Artifact":
                artifacts += 1
        total = sum(c.cost for c in self.cards)
        avg = round(total / len(self.cards), 1)
        return {
            "total_cards": len(self.cards),
            "creatures": creatures,
            "spells": spells,
            "artifacts": artifacts,
            "avg_cost": avg,
        }
