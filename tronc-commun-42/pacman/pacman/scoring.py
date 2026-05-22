"""Scoring system."""

from __future__ import annotations

from typing import Dict


class Scoring:
    """Manages game scoring."""

    def __init__(self, config: Dict) -> None:
        self.points_per_pacgum = int(config.get("points_per_pacgum", 10))
        self.points_per_super_pacgum = int(
            config.get("points_per_super_pacgum", 50)
        )
        self.points_per_ghost = int(config.get("points_per_ghost", 200))
        self.score = 0
        self.ghost_multiplier = 1

    def add_pacgum(self) -> int:
        """Add score for eating a pacgum (does NOT reset chain — classic rule).
        """

        self.score += self.points_per_pacgum
        return self.points_per_pacgum

    def add_super_pacgum(self) -> int:
        """Add score for eating a super-pacgum.

        Resets the multiplier so the upcoming chain restarts at 200.
        """

        self.score += self.points_per_super_pacgum
        self.reset_ghost_multiplier()
        return self.points_per_super_pacgum

    def add_ghost(self) -> int:
        """Add score for eating a ghost."""

        points = self.points_per_ghost * self.ghost_multiplier
        self.score += points
        self.ghost_multiplier = min(self.ghost_multiplier * 2, 8)
        return points

    def reset_ghost_multiplier(self) -> None:
        """Reset ghost multiplier."""

        self.ghost_multiplier = 1
