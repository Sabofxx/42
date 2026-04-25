from typing import Optional, Union

from ex0.Card import Card
from ex0.CreatureCard import CreatureCard
from ex1.SpellCard import SpellCard
from ex1.ArtifactCard import ArtifactCard
from ex3.CardFactory import CardFactory


class FantasyCardFactory(CardFactory):
    """Fantasy-themed card factory."""

    def create_creature(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        if isinstance(name_or_power, str):
            if name_or_power == "goblin":
                return CreatureCard(
                    "Goblin Warrior", 2,
                    "Common", 3, 2
                )
            return CreatureCard(
                name_or_power, 4,
                "Rare", 5, 4
            )
        power = name_or_power if name_or_power else 5
        return CreatureCard(
            "Fire Dragon", 5,
            "Legendary", power + 2, power
        )

    def create_spell(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        if isinstance(name_or_power, str):
            return SpellCard(
                name_or_power, 3,
                "Common", "damage"
            )
        return SpellCard(
            "Fireball", 3, "Common", "damage"
        )

    def create_artifact(
        self,
        name_or_power: Optional[
            Union[str, int]
        ] = None
    ) -> Card:
        if isinstance(name_or_power, str):
            return ArtifactCard(
                name_or_power, 2,
                "Rare", 5, "+1 mana per turn"
            )
        return ArtifactCard(
            "Mana Ring", 2, "Rare",
            5, "+1 mana per turn"
        )

    def create_themed_deck(
        self, size: int
    ) -> dict:
        cards = []
        for i in range(size):
            if i % 3 == 0:
                cards.append(
                    self.create_creature()
                )
            elif i % 3 == 1:
                cards.append(self.create_spell())
            else:
                cards.append(
                    self.create_artifact()
                )
        return {
            "cards": cards,
            "size": len(cards),
            "theme": "Fantasy",
        }

    def get_supported_types(self) -> dict:
        return {
            "creatures": ["dragon", "goblin"],
            "spells": ["fireball"],
            "artifacts": ["mana_ring"],
        }
