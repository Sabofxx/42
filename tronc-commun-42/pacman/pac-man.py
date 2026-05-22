#!/usr/bin/env python3
"""Pac-Man game entry point.

Usage:
    python3 pac-man.py [config.json]
"""

from __future__ import annotations

import sys
import traceback
from typing import Any, Dict, Optional


def _log(message: str) -> None:
    """Print a clear top-level error message."""

    print(f"[pac-man] {message}", file=sys.stderr)


def _load_config(path: str) -> Dict[str, Any]:
    """Parse and validate the config file (defaults on error)."""

    from pacman.config import parse_config

    return parse_config(path)


def _run(config: Dict[str, Any]) -> int:
    """Run the full game (menus, gameplay, highscores)."""

    import pygame

    from pacman.game import Game, GameMode
    from pacman.highscore import HighscoreManager
    from pacman.ui.menu import MainMenu, MenuItem
    from pacman.ui.renderer import Renderer
    from pacman.ui.screens import (
        GameOverScreen,
        HighscoresScreen,
        InstructionsScreen,
        NameEntryScreen,
        PauseScreen,
    )
    from pacman.ui.window import GameWindow

    window = GameWindow(
        int(config.get("window_width", 672)),
        int(config.get("window_height", 756)),
        title="Pac-Man",
        fps=int(config.get("fps", 60)),
    )
    renderer = Renderer(window.screen, config)
    menu = MainMenu(window.screen, config)
    highscores = HighscoreManager(str(config.get("highscore_filename", "highscores.json")))
    menu.set_highscores(highscores.get_top_10())

    state = "menu"
    game: Optional[Game] = None
    pause_screen: Optional[PauseScreen] = None
    game_over: Optional[GameOverScreen] = None
    name_entry: Optional[NameEntryScreen] = None
    instructions = InstructionsScreen(window.screen, config)
    scores_screen = HighscoresScreen(window.screen, config, highscores.get_top_10())
    running = True

    while running:
        dt = window.tick()
        if not window.handle_events():
            running = False
            break
        events = window.events

        if state == "menu":
            for event in events:
                choice = menu.handle_event(event)
                if choice == MenuItem.START_GAME:
                    try:
                        game = Game(config)
                        state = "play"
                    except Exception as exc:
                        _log(f"Could not start game: {exc}")
                        game = None
                        state = "menu"
                elif choice == MenuItem.HIGHSCORES:
                    scores_screen = HighscoresScreen(
                        window.screen, config, highscores.get_top_10()
                    )
                    state = "highscores"
                elif choice == MenuItem.INSTRUCTIONS:
                    state = "instructions"
                elif choice == MenuItem.EXIT:
                    running = False
            menu.render()
        elif state == "play" and game is not None:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pause_screen = PauseScreen(window.screen, config)
                        state = "pause"
                    elif event.unicode and event.unicode.lower() in (
                        "i", "l", "f", "+", "s", "p"
                    ):
                        game.cheats.toggle_cheat_by_key(event.unicode.lower())
            if state == "play":
                direction = window.get_input()
                game.update(dt, direction)
                game_state = game.get_state()
                renderer.render_game(game_state, dt)
                renderer.render_cheat_overlay(game.cheats.get_active_cheats())
                if game_state.mode in (GameMode.GAMEOVER, GameMode.WIN):
                    game_over = GameOverScreen(
                        window.screen,
                        config,
                        is_victory=(game_state.mode == GameMode.WIN),
                        score=game_state.score,
                    )
                    state = "gameover"
        elif state == "pause" and pause_screen is not None and game is not None:
            for event in events:
                action = pause_screen.handle_event(event)
                if action == "resume":
                    state = "play"
                elif action == "menu":
                    game = None
                    state = "menu"
                elif action == "quit":
                    running = False
            renderer.render_game(game.get_state(), 0.0)
            pause_screen.render()
        elif state == "gameover" and game_over is not None and game is not None:
            for event in events:
                action = game_over.handle_event(event)
                if action == "continue":
                    score = game.get_state().score
                    if score > 0:
                        name_entry = NameEntryScreen(window.screen, config, score)
                        state = "name_entry"
                    else:
                        game = None
                        state = "menu"
                elif action == "menu":
                    game = None
                    state = "menu"
            game_over.render()
        elif state == "name_entry" and name_entry is not None and game is not None:
            for event in events:
                name = name_entry.handle_event(event)
                if name is not None:
                    highscores.add_score(name, game.get_state().score)
                    menu.set_highscores(highscores.get_top_10())
                    game = None
                    name_entry = None
                    state = "menu"
            name_entry.render()
        elif state == "instructions":
            for event in events:
                if instructions.handle_event(event):
                    state = "menu"
            instructions.render()
        elif state == "highscores":
            for event in events:
                if scores_screen.handle_event(event):
                    state = "menu"
            scores_screen.render()
        else:
            state = "menu"
            menu.render()

        renderer.flip()

    window.close()
    return 0


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""

    args = list(sys.argv[1:]) if argv is None else list(argv)
    debug = "--debug" in args
    args = [a for a in args if a != "--debug"]

    if len(args) != 1:
        _log("Usage: python3 pac-man.py <config.json>")
        return 1
    config_path = args[0]
    if not config_path.lower().endswith(".json"):
        _log("Configuration file must have a .json extension.")
        return 1

    try:
        config = _load_config(config_path)
    except Exception as exc:
        _log(f"Failed to load config '{config_path}': {exc}")
        return 1

    try:
        return _run(config)
    except KeyboardInterrupt:
        return 0
    except SystemExit:
        raise
    except Exception as exc:
        _log(f"Unrecoverable error: {exc}")
        if debug:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
