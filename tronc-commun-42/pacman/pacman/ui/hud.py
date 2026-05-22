"""In-game HUD overlay (thin wrapper around the renderer's HUD)."""

from __future__ import annotations

import pygame


class HUD:
    """Heads-up display for score, lives, level and time."""

    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        self.screen = screen
        self.config = config
        self.font = pygame.font.SysFont("consolas", 20, bold=True)

    def render(
        self,
        score: int,
        lives: int,
        level: int,
        time_left: float,
    ) -> None:
        """Draw the HUD bar at the top of the window."""

        bar = pygame.Rect(0, 0, self.screen.get_width(), 56)
        pygame.draw.rect(self.screen, (20, 20, 40), bar)
        pygame.draw.line(
            self.screen,
            (80, 80, 160),
            (0, bar.bottom - 2),
            (self.screen.get_width(), bar.bottom - 2),
            2,
        )
        text = (
            f"SCORE {score:06d}   LIVES {lives}   LEVEL {level}   "
            f"TIME {max(0, int(time_left)):3d}s"
        )
        surface = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(
            surface, (16, (bar.height - surface.get_height()) // 2)
        )
