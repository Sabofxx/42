from typing import Dict, List

from ex4.TournamentCard import TournamentCard


class TournamentPlatform:
    """Tournament management platform."""

    def __init__(self) -> None:
        self.cards: Dict[str, TournamentCard] = {}
        self.matches_played: int = 0

    def register_card(
        self, card: TournamentCard
    ) -> str:
        card_id = (
            card.name.lower().replace(" ", "_")
            + "_001"
        )
        self.cards[card_id] = card
        return card_id

    def create_match(
        self, card1_id: str, card2_id: str
    ) -> dict:
        c1 = self.cards[card1_id]
        c2 = self.cards[card2_id]
        if c1.attack_power >= c2.attack_power:
            winner_id = card1_id
            loser_id = card2_id
            winner = c1
            loser = c2
        else:
            winner_id = card2_id
            loser_id = card1_id
            winner = c2
            loser = c1
        winner.update_wins(1)
        loser.update_losses(1)
        self.matches_played += 1
        return {
            "winner": winner_id,
            "loser": loser_id,
            "winner_rating": winner.rating,
            "loser_rating": loser.rating,
        }

    def get_leaderboard(self) -> List[dict]:
        sorted_cards = sorted(
            self.cards.items(),
            key=lambda x: x[1].rating,
            reverse=True,
        )
        board = []
        for rank, (cid, card) in enumerate(
            sorted_cards, 1
        ):
            info = card.get_rank_info()
            board.append({
                "rank": rank,
                "name": card.name,
                "rating": info["rating"],
                "record": info["record"],
            })
        return board

    def generate_tournament_report(self) -> dict:
        total = len(self.cards)
        if total == 0:
            return {
                "total_cards": 0,
                "matches_played": 0,
                "avg_rating": 0,
                "platform_status": "inactive",
            }
        avg = sum(
            c.rating for c in self.cards.values()
        ) // total
        return {
            "total_cards": total,
            "matches_played": self.matches_played,
            "avg_rating": avg,
            "platform_status": "active",
        }
