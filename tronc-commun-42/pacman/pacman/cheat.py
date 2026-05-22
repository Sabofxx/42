"""Cheat mode (shared - A handles logic, B shows overlay)."""

from __future__ import annotations

from typing import Dict


class CheatMode:
    """Cheat mode manager."""

    def __init__(self) -> None:
        self.invincible = False
        self.ghosts_frozen = False
        self.speed_multiplier = 1.0
        self.pending_skip = False
        self.extra_lives = 0
        self.pending_power_up = False

    def toggle_invincibility(self) -> bool:
        """Toggle invincibility mode."""

        self.invincible = not self.invincible
        return self.invincible

    def skip_level(self) -> bool:
        """Request a level skip."""

        self.pending_skip = True
        return True

    def freeze_ghosts(self) -> bool:
        """Toggle ghost freeze."""

        self.ghosts_frozen = not self.ghosts_frozen
        return self.ghosts_frozen

    def add_life(self) -> bool:
        """Add one extra life."""

        self.extra_lives += 1
        return True

    def double_speed(self) -> bool:
        """Toggle doubled speed."""

        self.speed_multiplier = 2.0 if self.speed_multiplier == 1.0 else 1.0
        return self.speed_multiplier == 2.0

    def trigger_power_up(self) -> bool:
        """Request an on-demand frighten of all ghosts (for peer review)."""

        self.pending_power_up = True
        return True

    def consume_power_up_request(self) -> bool:
        """Return and clear a pending power-up request."""

        if not self.pending_power_up:
            return False
        self.pending_power_up = False
        return True

    def get_active_cheats(self) -> Dict[str, bool]:
        """Get list of active cheats."""

        return {
            "invincible": self.invincible,
            "ghosts_frozen": self.ghosts_frozen,
            "double_speed": self.speed_multiplier > 1.0,
            "skip_level": self.pending_skip,
            "extra_lives": self.extra_lives > 0,
        }

    def toggle_cheat_by_key(self, key: str) -> None:
        """Toggle cheat by single-character key."""

        mapping = {
            "i": self.toggle_invincibility,
            "l": self.skip_level,
            "f": self.freeze_ghosts,
            "+": self.add_life,
            "s": self.double_speed,
            "p": self.trigger_power_up,
        }
        action = mapping.get(key.lower())
        if action is not None:
            action()

    def consume_skip_request(self) -> bool:
        """Return and clear the pending skip request."""

        if not self.pending_skip:
            return False
        self.pending_skip = False
        return True
