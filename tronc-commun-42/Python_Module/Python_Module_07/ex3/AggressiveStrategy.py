from typing import List

from ex3.GameStrategy import GameStrategy


class AggressiveStrategy(GameStrategy):
    """Aggressive game strategy."""

    def execute_turn(
        self, hand: List, battlefield: List
    ) -> dict:
        played = []
        mana_used = 0
        damage = 0
        sorted_hand = sorted(
            hand, key=lambda c: c.cost
        )
        for card in sorted_hand:
            info = card.get_card_info()
            played.append(card.name)
            mana_used += card.cost
            if info.get("type") == "Creature":
                damage += info.get("attack", 0)
            elif info.get("type") == "Spell":
                damage += card.cost
        return {
            "strategy": self.get_strategy_name(),
            "actions": {
                "cards_played": played,
                "mana_used": mana_used,
                "targets_attacked": [
                    "Enemy Player"
                ],
                "damage_dealt": damage,
            },
        }

    def get_strategy_name(self) -> str:
        return "AggressiveStrategy"

    def prioritize_targets(
        self, available_targets: List
    ) -> List:
        return sorted(
            available_targets,
            key=lambda t: t.get("health", 0)
        )
