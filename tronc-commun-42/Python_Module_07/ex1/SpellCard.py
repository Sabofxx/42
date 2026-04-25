from ex0.Card import Card


class SpellCard(Card):
    """Instant magic effect card."""

    def __init__(
        self, name: str, cost: int,
        rarity: str, effect_type: str
    ) -> None:
        super().__init__(name, cost, rarity)
        self.effect_type = effect_type

    def play(self, game_state: dict) -> dict:
        """Play spell card."""
        effects = {
            "damage": f"Deal {self.cost} damage"
                      " to target",
            "heal": f"Restore {self.cost} health",
            "buff": "Boost ally stats",
            "debuff": "Weaken enemy stats",
        }
        effect = effects.get(
            self.effect_type, "Unknown effect"
        )
        return {
            "card_played": self.name,
            "mana_used": self.cost,
            "effect": effect,
        }

    def get_card_info(self) -> dict:
        info = super().get_card_info()
        info["type"] = "Spell"
        info["effect_type"] = self.effect_type
        return info

    def resolve_effect(
        self, targets: list
    ) -> dict:
        """Resolve spell effect on targets."""
        return {
            "spell": self.name,
            "effect_type": self.effect_type,
            "targets": targets,
            "resolved": True,
        }
