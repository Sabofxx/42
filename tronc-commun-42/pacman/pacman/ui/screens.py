"""Game state screens: pause, game over / victory, name entry, etc."""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from pacman.highscore import HighscoreManager


class _ScreenBase:
    """Shared helpers for full-screen UI panels."""

    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        self.screen = screen
        self.config = config
        self.title_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.font = pygame.font.SysFont("consolas", 24, bold=True)
        self.small_font = pygame.font.SysFont("consolas", 18)

    def _draw_centered_text(
        self,
        text: str,
        font: pygame.font.Font,
        y: int,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.screen.get_width() // 2, y))
        self.screen.blit(surface, rect)

    def _fill_overlay(self, alpha: int = 200) -> None:
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        self.screen.blit(overlay, (0, 0))


class PauseScreen(_ScreenBase):
    """Pause overlay with resume / quit options."""

    OPTIONS = ("Resume", "Return to Menu", "Quit")

    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        super().__init__(screen, config)
        self.selection = 0

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Return 'resume', 'menu' or 'quit' when chosen."""

        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selection = (self.selection - 1) % len(self.OPTIONS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selection = (self.selection + 1) % len(self.OPTIONS)
        elif event.key == pygame.K_ESCAPE:
            return "resume"
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return ("resume", "menu", "quit")[self.selection]
        return None

    def render(self) -> None:
        self._fill_overlay(160)
        self._draw_centered_text("PAUSED", self.title_font, 220, (255, 255, 0))
        for index, label in enumerate(self.OPTIONS):
            color = (255, 255, 0) if index == self.selection else (200, 200, 200)
            prefix = ">  " if index == self.selection else "   "
            self._draw_centered_text(prefix + label, self.font, 320 + index * 40, color)


class NameEntryScreen(_ScreenBase):
    """Prompt player for a highscore name."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: dict,
        score: int,
    ) -> None:
        super().__init__(screen, config)
        self.score = int(score)
        self.buffer: str = ""

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Return the validated name when ENTER is pressed."""

        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return HighscoreManager.validate_name(self.buffer)
        if event.key == pygame.K_BACKSPACE:
            self.buffer = self.buffer[:-1]
            return None
        if event.key == pygame.K_ESCAPE:
            return HighscoreManager.validate_name(self.buffer or "Player")
        unicode_char = getattr(event, "unicode", "")
        if unicode_char and len(self.buffer) < 10:
            if unicode_char.isalnum() or unicode_char == " ":
                self.buffer += unicode_char
        return None

    def render(self) -> None:
        self.screen.fill((0, 0, 30))
        self._draw_centered_text("NEW HIGHSCORE!", self.title_font, 180, (255, 255, 0))
        self._draw_centered_text(f"Score: {self.score}", self.font, 250)
        self._draw_centered_text("Enter your name:", self.font, 320)
        display = self.buffer + ("_" if len(self.buffer) < 10 else "")
        self._draw_centered_text(display, self.title_font, 380, (255, 255, 255))
        self._draw_centered_text(
            "10 chars max - letters, digits, space - Enter to confirm",
            self.small_font,
            self.screen.get_height() - 40,
            (140, 140, 200),
        )


class GameOverScreen(_ScreenBase):
    """Game-over / victory message before name entry."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: dict,
        is_victory: bool,
        score: int,
    ) -> None:
        super().__init__(screen, config)
        self.is_victory = is_victory
        self.score = int(score)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type != pygame.KEYDOWN:
            return None
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            return "continue"
        if event.key == pygame.K_ESCAPE:
            return "menu"
        return None

    def render(self) -> None:
        self.screen.fill((0, 0, 20))
        title_text = "YOU WIN!" if self.is_victory else "GAME OVER"
        color = (0, 255, 120) if self.is_victory else (255, 80, 80)
        self._draw_centered_text(title_text, self.title_font, 220, color)
        self._draw_centered_text(f"Final score: {self.score}", self.font, 300)
        self._draw_centered_text(
            "Press ENTER to continue",
            self.small_font,
            self.screen.get_height() - 40,
            (140, 140, 200),
        )


class InstructionsScreen(_ScreenBase):
    """Display controls and rules."""

    LINES = (
        "Controls:",
        "  Arrow keys or WASD - move Pac-Man",
        "  ESC                - pause / resume",
        "",
        "Rules:",
        "  Eat all pacgums to clear the level",
        "  Avoid the four ghosts at all costs",
        "  Eat a super-pacgum to frighten the ghosts",
        "  Eat frightened ghosts for bonus points",
        "",
        "Cheats (during play):",
        "  I = invincibility   L = skip level",
        "  F = freeze ghosts   + = +1 life      S = speed x2",
    )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            return "menu"
        return None

    def render(self) -> None:
        self.screen.fill((0, 0, 30))
        self._draw_centered_text("INSTRUCTIONS", self.title_font, 80, (255, 255, 0))
        for index, line in enumerate(self.LINES):
            self._draw_centered_text(line, self.font, 160 + index * 32)
        self._draw_centered_text(
            "Press any key to return",
            self.small_font,
            self.screen.get_height() - 40,
            (140, 140, 200),
        )


class HighscoresScreen(_ScreenBase):
    """Display the top 10 highscores."""

    def __init__(
        self,
        screen: pygame.Surface,
        config: dict,
        highscores: List[Tuple[str, int]],
    ) -> None:
        super().__init__(screen, config)
        self.highscores = list(highscores)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            return "menu"
        return None

    def render(self) -> None:
        self.screen.fill((0, 0, 30))
        self._draw_centered_text(
            "TOP 10 HIGHSCORES",
            self.title_font,
            80,
            (255, 255, 0),
        )
        if not self.highscores:
            self._draw_centered_text(
                "No highscores yet - play a game!", self.font, 250
            )
        else:
            for index, (name, score) in enumerate(self.highscores[:10]):
                line = f"{index + 1:2d}. {name:<10s}  {score:>8d}"
                self._draw_centered_text(line, self.font, 160 + index * 32)
        self._draw_centered_text(
            "Press any key to return",
            self.small_font,
            self.screen.get_height() - 40,
            (140, 140, 200),
        )
