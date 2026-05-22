"""Tests for highscore and UI helpers (non-interactive)."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # noqa: E402

from pacman.highscore import HighscoreManager  # noqa: E402


def test_validate_name_basic() -> None:
    assert HighscoreManager.validate_name("AB!@#cd") == "ABcd"
    assert HighscoreManager.validate_name("") == "Player"
    assert HighscoreManager.validate_name("VeryLongPlayerName") == "VeryLongPl"
    assert HighscoreManager.validate_name("  hello  ") == "hello"


def test_highscore_persistence(tmp_path: Path) -> None:
    file = tmp_path / "scores.json"
    manager = HighscoreManager(str(file))
    assert manager.get_top_10() == []
    rank = manager.add_score("Alice", 500)
    assert rank == 1
    manager.add_score("Bob", 1000)
    top = manager.get_top_10()
    assert top[0] == ("Bob", 1000)
    # Reload from disk.
    again = HighscoreManager(str(file))
    assert again.get_top_10() == [("Bob", 1000), ("Alice", 500)]


def test_highscore_accepts_zero_score(tmp_path: Path) -> None:
    file = tmp_path / "scores.json"
    manager = HighscoreManager(str(file))
    rank = manager.add_score("Zero", 0)
    assert rank == 1
    assert manager.get_top_10() == [("Zero", 0)]


def test_highscore_corruption_recovery(tmp_path: Path) -> None:
    file = tmp_path / "scores.json"
    file.write_text("{not json", encoding="utf-8")
    manager = HighscoreManager(str(file))
    assert manager.get_top_10() == []


def test_highscore_keeps_top_10(tmp_path: Path) -> None:
    file = tmp_path / "scores.json"
    manager = HighscoreManager(str(file))
    for i in range(15):
        manager.add_score(f"P{i}", i * 100)
    top = manager.get_top_10()
    assert len(top) == 10
    assert top[0][1] == 1400


def test_ui_modules_import() -> None:
    # Must initialize a display before pygame.font usage.
    import pygame
    from typing import Any

    pygame.display.init()
    pygame.font.init()
    screen: Any = pygame.display.set_mode((100, 100))
    from pacman.ui.hud import HUD
    from pacman.ui.menu import MainMenu
    from pacman.ui.renderer import Renderer
    from pacman.ui.screens import (
        GameOverScreen,
        HighscoresScreen,
        InstructionsScreen,
        NameEntryScreen,
        PauseScreen,
    )

    assert HUD(screen, {}) is not None
    assert MainMenu(screen, {}) is not None
    assert Renderer(screen, {}) is not None
    assert PauseScreen(screen, {}) is not None
    assert NameEntryScreen(screen, {}, 100) is not None
    assert GameOverScreen(screen, {}, True, 100) is not None
    assert InstructionsScreen(screen, {}) is not None
    assert HighscoresScreen(screen, {}, []) is not None
    pygame.display.quit()
