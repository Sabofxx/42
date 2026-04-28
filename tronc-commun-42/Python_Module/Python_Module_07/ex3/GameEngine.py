from typing import Optional, List

from ex0.Card import Card
from ex3.CardFactory import CardFactory
from ex3.GameStrategy import GameStrategy


class GameEngine:
    """Game orchestrator."""

    def __init__(self) -> None:
        self.factory: Optional[CardFactory] = None
        self.strategy: Optional[GameStrategy] = None
        self.hand: List[Card] = []
        self.turns: int = 0
        self.total_damage: int = 0

    def configure_engine(
        self, factory: CardFactory,
        strategy: GameStrategy
    ) -> None:
        self.factory = factory
        self.strategy = strategy

    def simulate_turn(self) -> dict:
        if not self.factory or not self.strategy:
            return {"error": "Engine not configured"}
        if not self.hand:
            self.hand = [
                self.factory.create_creature(),
                self.factory.create_creature(
                    "goblin"
                ),
                self.factory.create_spell(),
            ]
        result = self.strategy.execute_turn(
            self.hand, []
        )
        self.turns += 1
        dmg = result["actions"]["damage_dealt"]
        self.total_damage += dmg
        self.hand = []
        return result

    def get_engine_status(self) -> dict:
        strategy_name = ""
        if self.strategy:
            strategy_name = (
                self.strategy.get_strategy_name()
            )
        return {
            "turns_simulated": self.turns,
            "strategy_used": strategy_name,
            "total_damage": self.total_damage,
            "cards_created": 3,
        }
