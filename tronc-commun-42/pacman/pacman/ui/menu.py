"""Main menu and navigation."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Tuple

import pygame


class MenuItem(Enum):
    """Main menu options."""

    START_GAME = 0
    HIGHSCORES = 1
    INSTRUCTIONS = 2
    EXIT = 3


_LABELS = {
    MenuItem.START_GAME: "Start Game",
    MenuItem.HIGHSCORES: "Highscores",
    MenuItem.INSTRUCTIONS: "Instructions",
    MenuItem.EXIT: "Exit",
}


class MainMenu:
    """Main menu controller and renderer."""

    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        self.screen = screen
        self.config = config
        self.items = list(MenuItem)
        self.selection = 0
        self.highscores: List[Tuple[str, int]] = []
        self.title_font = pygame.font.SysFont("consolas", 64, bold=True)
        self.font = pygame.font.SysFont("consolas", 28, bold=True)
        self.score_font = pygame.font.SysFont("consolas", 18, bold=True)
        self.hint_font = pygame.font.SysFont("consolas", 16)

    def set_highscores(self, highscores: List[Tuple[str, int]]) -> None:
        """Refresh the embedded top scores."""

        self.highscores = list(highscores)

    def move(self, delta: int) -> None:
        """Move the selection cursor (wraps)."""

        self.selection = (self.selection + delta) % len(self.items)

    def handle_event(self, event: pygame.event.Event) -> Optional[MenuItem]:
        """Process one pygame event. Return chosen item on ENTER."""

        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.move(-1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.move(1)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return self.items[self.selection]
        elif event.key == pygame.K_ESCAPE:
            return MenuItem.EXIT
        return None

    def handle_input(self, direction: Tuple[int, int]) -> Optional[MenuItem]:
        """Legacy direction-based navigation."""

        if direction == (0, -1):
            self.move(-1)
        elif direction == (0, 1):
            self.move(1)
        return None

    def render(self) -> None:
        """Draw the menu."""

        self.screen.fill((0, 0, 20))
        title = self.title_font.render("PAC-MAN", True, (255, 255, 0))
        title_rect = title.get_rect(
            center=(self.screen.get_width() // 2, 120)
        )
        self.screen.blit(title, title_rect)

        start_y = 260
        for index, item in enumerate(self.items):
            selected = index == self.selection
            color = (255, 255, 0) if selected else (200, 200, 200)
            prefix = ">  " if selected else "   "
            text = self.font.render(prefix + _LABELS[item], True, color)
            rect = text.get_rect(
                center=(self.screen.get_width() // 2, start_y + index * 50)
            )
            self.screen.blit(text, rect)

        if self.highscores:
            scores_y = start_y + len(self.items) * 50 + 30
            label = self.score_font.render(
                "highscores:", True, (200, 200, 200)
            )
            self.screen.blit(
                label,
                label.get_rect(center=(self.screen.get_width() // 2, scores_y)),
            )
            for index, (name, score) in enumerate(self.highscores[:5]):
                line = f"{index + 1}. {name} - {score} pts"
                surface = self.score_font.render(line, True, (255, 255, 0))
                rect = surface.get_rect(
                    center=(
                        self.screen.get_width() // 2,
                        scores_y + 26 + index * 22,
                    )
                )
                self.screen.blit(surface, rect)

        hint = self.hint_font.render(
            "Up/Down to move - Enter to select - Esc to quit",
            True,
            (140, 140, 200),
        )
        hint_rect = hint.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() - 40,
            )
        )
        self.screen.blit(hint, hint_rect)
