"""Unit tests for the engine modules."""

from __future__ import annotations

from pathlib import Path

from pacman.cheat import CheatMode
from pacman.config import parse_config
from pacman.entities.ghost import Ghost, GhostBehavior, GhostState  # noqa: F401
from pacman.entities.player import Player
from pacman.game import Game, GameMode
from pacman.maze_loader import (
    PACGUM,
    SPAWN_PACMAN,
    SUPER_PACGUM,
    WALL,
    convert_maze_to_tiles,
    generate_maze,
)
from pacman.scoring import Scoring


def test_parse_config_with_comments(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        "\n".join(
            [
                "# comment line",
                "{",
                '  "lives": 5,',
                '  "width": 25,',
                '  "unknown_key": 123',
                "}",
            ]
        ),
        encoding="utf-8",
    )
    cfg = parse_config(str(config_path))
    assert cfg["lives"] == 5
    assert cfg["width"] == 25
    assert "unknown_key" not in cfg


def test_parse_config_missing_file_uses_defaults(tmp_path: Path) -> None:
    cfg = parse_config(str(tmp_path / "missing.json"))
    assert cfg["lives"] == 3
    assert cfg["width"] == 21


def test_parse_config_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{ not json")
    cfg = parse_config(str(bad))
    assert cfg["lives"] == 3


def test_scoring_multiplier_and_reset() -> None:
    scoring = Scoring(
        {
            "points_per_pacgum": 10,
            "points_per_super_pacgum": 50,
            "points_per_ghost": 200,
        }
    )
    assert scoring.add_ghost() == 200
    assert scoring.add_ghost() == 400
    assert scoring.add_ghost() == 800
    assert scoring.add_ghost() == 1600
    scoring.reset_ghost_multiplier()
    assert scoring.add_ghost() == 200


def test_cheat_toggles() -> None:
    cheats = CheatMode()
    assert cheats.toggle_invincibility() is True
    assert cheats.toggle_invincibility() is False
    cheats.add_life()
    cheats.add_life()
    assert cheats.extra_lives == 2
    cheats.double_speed()
    assert cheats.speed_multiplier == 2.0
    cheats.toggle_cheat_by_key("F")
    assert cheats.ghosts_frozen is True


def test_maze_conversion_doubles_grid() -> None:
    raw = generate_maze(7, 7, seed=42)
    tiles, spawns = convert_maze_to_tiles(raw)
    assert len(tiles) == 15
    assert len(tiles[0]) == 15
    # Border is always wall.
    assert tiles[0][0] == WALL
    assert tiles[-1][-1] == WALL
    # Pac-Man spawn exists.
    assert any(SPAWN_PACMAN in row for row in tiles)
    # At least one super pacgum.
    assert any(SUPER_PACGUM in row for row in tiles)
    assert spawns and len(spawns) == 5


def test_player_blocked_by_wall() -> None:
    grid = [
        [WALL, WALL, WALL],
        [WALL, PACGUM, WALL],
        [WALL, WALL, WALL],
    ]
    player = Player(1, 1)
    player.set_direction(1, 0)
    player.update(1.0, grid, {"player_speed": 5.0})
    assert player.pos == (1, 1)


def test_ghost_chases_player() -> None:
    grid = [
        [WALL, WALL, WALL, WALL, WALL],
        [WALL, PACGUM, PACGUM, PACGUM, WALL],
        [WALL, PACGUM, PACGUM, PACGUM, WALL],
        [WALL, PACGUM, PACGUM, PACGUM, WALL],
        [WALL, WALL, WALL, WALL, WALL],
    ]
    ghost = Ghost(1, 1, 0, GhostBehavior.CHASE)
    for _ in range(20):
        ghost.update(0.1, grid, (3, 3), {"ghost_speed": 4.0})
    assert ghost.pos != (1, 1)


def test_ghost_frightened_then_normal() -> None:
    ghost = Ghost(1, 1, 0, GhostBehavior.CHASE)
    ghost.set_state(GhostState.FRIGHTENED, duration=0.05)
    grid = [[PACGUM, PACGUM], [PACGUM, PACGUM]]
    ghost.update(0.2, grid, (1, 1), {"ghost_speed": 4.0})
    assert ghost.state == GhostState.NORMAL


def test_game_smoke_update(tmp_path: Path) -> None:
    cfg = parse_config("config.json")
    game = Game(cfg)
    for _ in range(50):
        game.update(0.05, (0, 1))
    state = game.get_state()
    assert state.level >= 1
    assert state.lives > 0
    assert state.mode in (GameMode.PLAY, GameMode.GAMEOVER, GameMode.WIN)


def test_game_pacgum_collection() -> None:
    cfg = parse_config("config.json")
    game = Game(cfg)
    initial = game._remaining_pacgums
    for _ in range(80):
        game.update(0.05, (0, 1))
    assert game._remaining_pacgums <= initial
    assert game.score >= 0


def test_eaten_ghost_does_not_kill_player() -> None:
    """A ghost in EATEN state sharing the player's tile must not cost a life."""

    cfg = parse_config("config.json")
    game = Game(cfg)
    # Bypass spawn grace so collisions count.
    game._respawn_grace = 0.0
    lives_before = game._player.lives
    ghost = game._ghosts[0]
    ghost.x, ghost.y = game._player.pos
    ghost.set_state(GhostState.FRIGHTENED, duration=10.0)
    game._handle_collisions()
    assert ghost.state == GhostState.EATEN
    # Force another frame where the eaten ghost still overlaps the player.
    ghost.x, ghost.y = game._player.pos
    game._handle_collisions()
    assert game._player.lives == lives_before
