from ex0.Card import Card


class CreatureCard(Card):
    """Concrete creature card implementation."""

    def __init__(
        self, name: str, cost: int,
        rarity: str, attack: int, health: int
    ) -> None:
        super().__init__(name, cost, rarity)
        if attack <= 0 or health <= 0:
            raise ValueError(
                "Attack and health must be positive"
            )
        self.attack = attack
        self.health = health

    def play(self, game_state: dict) -> dict:
        """Summon creature to battlefield."""
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": (
                "Creature summoned to battlefield"
            ),
        }

    def get_card_info(self) -> dict:
        """Return creature card info."""
        info = super().get_card_info()
        info["type"] = "Creature"
        info["attack"] = self.attack
        info["health"] = self.health
        return info

    def attack_target(self, target: str) -> dict:
        """Attack a target."""
        return {
            "attacker": self.name,
            "target": target,
            "damage_dealt": self.attack,
            "combat_resolved": True,
        }
