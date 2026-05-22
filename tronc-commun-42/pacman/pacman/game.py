"""Main game engine and loop."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Tuple

from pacman.cheat import CheatMode
from pacman.entities.ghost import Ghost, GhostState
from pacman.entities.player import Player
from pacman.maze_loader import (
    CORRIDOR,
    PACGUM,
    SUPER_PACGUM,
    TileGrid,
    convert_maze_to_tiles,
    generate_maze,
)
from pacman.scoring import Scoring


class GameMode(Enum):
    """Game mode states."""

    PLAY = "play"
    PAUSE = "pause"
    GAMEOVER = "gameover"
    WIN = "win"


@dataclass
class FloatingEffect:
    """A short-lived visual effect (score popup, ghost-eaten badge)."""

    text: str
    x: float
    y: float
    color: Tuple[int, int, int]
    time_left: float
    lifetime: float


@dataclass(frozen=True)
class GameState:
    """Read-only game state interface for UI."""

    score: int = 0
    lives: int = 0
    level: int = 0
    time_left: float = 0.0
    pacman: Player = field(default_factory=lambda: Player(0, 0, 3))
    ghosts: List[Ghost] = field(default_factory=list)
    grid: TileGrid = field(default_factory=list)
    mode: GameMode = GameMode.PLAY
    ready_time_left: float = 0.0
    frightened_time_left: float = 0.0
    effects: List[FloatingEffect] = field(default_factory=list)
    eat_freeze: float = 0.0


class Game:
    """Main game engine."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.scoring = Scoring(config)
        self.cheats = CheatMode()
        self.max_levels = int(config.get("num_levels", 10))
        self.level = 1
        self.mode = GameMode.PLAY
        self.time_left = float(config.get("level_max_time", 90))
        self._rng = random.Random(int(config.get("seed", 42)))
        self._current_seed = int(config.get("seed", 42))
        self._grid: TileGrid = []
        self._maze: List[List[int]] = []
        self._remaining_pacgums = 0
        self._spawn_positions: List[Tuple[int, int]] = []
        self._player = Player(0, 0, int(config.get("lives", 3)))
        self._ghosts: List[Ghost] = []
        self._respawn_grace = 0.0
        self._effects: List[FloatingEffect] = []
        self._eat_freeze = 0.0
        self._load_level(self.level, self._current_seed)

    @property
    def score(self) -> int:
        """Return the current score."""

        return self.scoring.score

    def _load_level(self, level: int, seed: int) -> None:
        """Load a level, maze, player and ghosts.

        Robust to maze generation/conversion failures: falls back to a
        minimal corridor grid so the game still launches.
        """

        import sys as _sys

        width = int(self.config.get("width", 21))
        height = int(self.config.get("height", 21))
        lives = self._player.lives if self._player else int(
            self.config.get("lives", 3)
        )
        try:
            self._maze = generate_maze(
                width,
                height,
                seed,
                bool(self.config.get("perfect_maze", False)),
            )
            self._grid, self._spawn_positions = convert_maze_to_tiles(
                self._maze
            )
        except Exception as exc:
            print(
                f"[game] Level generation failed: {exc}. Using empty grid.",
                file=_sys.stderr,
            )
            self._maze = []
            self._grid, self._spawn_positions = [], []

        if self._spawn_positions:
            player_spawn = self._spawn_positions[0]
        else:
            player_spawn = (width // 2, height // 2)

        self._player = Player(player_spawn[0], player_spawn[1], lives)
        self._ghosts = Ghost.get_all_ghosts()
        grid_w = len(self._grid[0]) if self._grid else 0
        grid_h = len(self._grid) if self._grid else 0
        scatter_corners = [
            (grid_w - 2, 1),
            (1, 1),
            (grid_w - 2, grid_h - 2),
            (1, grid_h - 2),
        ]
        for index, ghost in enumerate(self._ghosts):
            ghost.scatter_target = scatter_corners[index % 4]
        for ghost, spawn in zip(self._ghosts, self._spawn_positions[1:]):
            ghost.respawn(spawn)
            ghost.scatter_target = scatter_corners[ghost.ghost_id % 4]

        self.time_left = float(self.config.get("level_max_time", 90))
        self._remaining_pacgums = self._count_pacgums()
        self._respawn_grace = 2.0
        self.level = level
        self.mode = GameMode.PLAY

    def _count_pacgums(self) -> int:
        """Count remaining pacgums and super-pacgums."""

        total = 0
        for row in self._grid:
            for tile in row:
                if tile in (PACGUM, SUPER_PACGUM):
                    total += 1
        return total

    def _tile_at(self, x: int, y: int) -> str:
        """Return the tile name at the given position."""

        if y < 0 or x < 0 or y >= len(self._grid) or x >= len(self._grid[y]):
            return "WALL"
        return self._grid[y][x]

    def _apply_cheats(self) -> None:
        """Apply cheat effects that affect the engine state."""

        if self.cheats.extra_lives > 0:
            self._player.lives += self.cheats.extra_lives
            self.cheats.extra_lives = 0

    def _apply_pacgum_pickup(self) -> None:
        """Handle pacgum or super-pacgum pickups."""

        tile = self._tile_at(self._player.x, self._player.y)
        if tile == PACGUM:
            self._grid[self._player.y][self._player.x] = CORRIDOR
            self.scoring.add_pacgum()
            self._remaining_pacgums = max(0, self._remaining_pacgums - 1)
        elif tile == SUPER_PACGUM:
            self._grid[self._player.y][self._player.x] = CORRIDOR
            self.scoring.add_super_pacgum()
            self._remaining_pacgums = max(0, self._remaining_pacgums - 1)
            for ghost in self._ghosts:
                ghost.set_state(
                    GhostState.FRIGHTENED,
                    float(self.config.get("frightened_duration", 10.0)),
                )

    def _handle_collisions(self) -> None:
        """Handle player and ghost collisions."""

        for ghost in self._ghosts:
            if ghost.pos != self._player.pos:
                continue
            if ghost.state == GhostState.EATEN:
                # Eaten ghost is returning to its spawn; it cannot hurt the
                # player even while it sits on the same tile this frame.
                continue
            if ghost.state == GhostState.FRIGHTENED:
                points = self.scoring.add_ghost()
                ghost.set_state(
                    GhostState.EATEN,
                    float(self.config.get("respawn_delay", 5.0)),
                )
                self._spawn_eat_effect(ghost.pos, points)
                # Brief freeze so the popup is readable; classic arcade does
                # the same so the player sees the score they just earned.
                self._eat_freeze = max(self._eat_freeze, 0.5)
                continue
            if self.cheats.invincible or self._respawn_grace > 0.0:
                continue
            if self._player.lose_life():
                self.mode = GameMode.GAMEOVER
                return
            if self._spawn_positions:
                self._player.respawn(self._spawn_positions[0])
                for index, other in enumerate(self._ghosts, start=1):
                    if index < len(self._spawn_positions):
                        other.respawn(self._spawn_positions[index])
            self._respawn_grace = 2.0
            return

    def _spawn_eat_effect(
        self, pos: Tuple[int, int], points: int
    ) -> None:
        """Emit a score popup floating up from a ghost-eaten tile."""

        self._effects.append(
            FloatingEffect(
                text=f"+{points}",
                x=float(pos[0]),
                y=float(pos[1]),
                color=(0, 255, 200),
                time_left=0.9,
                lifetime=0.9,
            )
        )

    def _update_effects(self, dt: float) -> None:
        """Advance and prune floating-text effects."""

        survivors: List[FloatingEffect] = []
        for effect in self._effects:
            effect.time_left -= dt
            effect.y -= dt * 1.5
            if effect.time_left > 0.0:
                survivors.append(effect)
        self._effects = survivors

    def _handle_level_complete(self) -> None:
        """Advance to the next level when all pacgums are eaten."""

        if self._remaining_pacgums > 0:
            return
        if not self.next_level():
            self.mode = GameMode.WIN

    def get_state(self) -> GameState:
        """Return the current read-only game state for UI."""

        frightened_remaining = 0.0
        for ghost in self._ghosts:
            if ghost.state == GhostState.FRIGHTENED:
                frightened_remaining = max(
                    frightened_remaining, ghost.state_time_left
                )

        return GameState(
            score=self.score,
            lives=self._player.lives,
            level=self.level,
            time_left=self.time_left,
            pacman=self._player,
            ghosts=self._ghosts,
            grid=self._grid,
            mode=self.mode,
            ready_time_left=self._respawn_grace,
            frightened_time_left=frightened_remaining,
            effects=list(self._effects),
            eat_freeze=self._eat_freeze,
        )

    def update(self, dt: float, input_dir: Tuple[int, int] = (0, 0)) -> None:
        """Main game update loop."""

        if self.mode != GameMode.PLAY:
            return

        if self.cheats.consume_skip_request():
            self.next_level()
            return

        if self.cheats.consume_power_up_request():
            for ghost in self._ghosts:
                ghost.set_state(
                    GhostState.FRIGHTENED,
                    float(self.config.get("frightened_duration", 10.0)),
                )

        self._apply_cheats()

        # During an eat-freeze pause, only animate effects so the score popup
        # is visible; entities are otherwise frozen for ~0.5s.
        if self._eat_freeze > 0.0:
            self._eat_freeze = max(0.0, self._eat_freeze - dt)
            self._update_effects(dt)
            return

        if input_dir != (0, 0):
            self._player.set_direction(*input_dir)

        update_config = dict(self.config)
        # Per-level difficulty scaling: ghosts +5% speed each level (capped),
        # frightened duration shrinks slightly. Classic arcade behaviour.
        level_factor = 1.0 + 0.05 * min(self.level - 1, 8)
        update_config["player_speed"] = (
            float(self.config.get("player_speed", 5.0))
            * self.cheats.speed_multiplier
        )
        update_config["ghost_speed"] = (
            float(self.config.get("ghost_speed", 4.0))
            * level_factor
            * self.cheats.speed_multiplier
        )
        update_config["frightened_duration"] = max(
            2.0,
            float(self.config.get("frightened_duration", 10.0))
            * (1.0 - 0.05 * min(self.level - 1, 8)),
        )

        self._player.update(dt, self._grid, update_config)

        if self._respawn_grace > 0.0:
            self._respawn_grace = max(0.0, self._respawn_grace - dt)

        if not self.cheats.ghosts_frozen and self._respawn_grace == 0.0:
            player_dir = self._player.dir
            for ghost in self._ghosts:
                ghost.update(
                    dt,
                    self._grid,
                    self._player.pos,
                    update_config,
                    player_dir,
                )

        self._apply_pacgum_pickup()
        self._handle_collisions()

        self._update_effects(dt)
        # Reset ghost-eaten multiplier once no ghost is frightened or eaten:
        # the chain belongs to a single super-pacgum, not to the whole game.
        if all(g.state == GhostState.NORMAL for g in self._ghosts):
            self.scoring.reset_ghost_multiplier()
        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left == 0.0:
            self.restart_level()
            return

        self._handle_level_complete()

    def set_mode(self, mode: GameMode) -> None:
        """Set game mode (PLAY, PAUSE, etc)."""

        self.mode = mode

    def next_level(self) -> bool:
        """Advance to next level."""

        if self.level >= self.max_levels:
            return False

        self.level += 1
        self._current_seed = self._rng.randint(0, 1_000_000)
        self._load_level(self.level, self._current_seed)
        return True

    def restart_level(self) -> None:
        """Restart current level."""

        self._load_level(self.level, self._current_seed)
