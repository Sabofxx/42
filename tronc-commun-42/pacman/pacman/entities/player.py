"""Player (Pac-Man) entity."""

from __future__ import annotations

from typing import Sequence, Tuple


def _is_blocked(
    grid: Sequence[Sequence[object]],
    current_x: int,
    current_y: int,
    dx: int,
    dy: int,
) -> bool:
    """Return True when a move is blocked by a wall or maze border."""

    target_x = current_x + dx
    target_y = current_y + dy

    if target_y < 0 or target_x < 0:
        return True
    if target_y >= len(grid) or target_x >= len(grid[target_y]):
        return True

    current_cell = grid[current_y][current_x]
    target_cell = grid[target_y][target_x]

    if isinstance(current_cell, int):
        if dx == 1 and current_cell & 2:
            return True
        if dx == -1 and current_cell & 8:
            return True
        if dy == 1 and current_cell & 4:
            return True
        if dy == -1 and current_cell & 1:
            return True
        return False

    return target_cell in ("WALL", "WALL_42")


class Player:
    """Represents the Pac-Man player."""

    def __init__(self, x: int, y: int, lives: int = 3) -> None:
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        self.lives = lives
        self.direction_x = 0
        self.direction_y = 0
        self.buffered_x = 0
        self.buffered_y = 0
        self._move_progress = 0.0

    @property
    def pos(self) -> Tuple[int, int]:
        """Return the current grid position."""

        return self.x, self.y

    @property
    def dir(self) -> Tuple[int, int]:
        """Return the current movement direction."""

        return self.direction_x, self.direction_y

    @property
    def visual_pos(self) -> Tuple[float, float]:
        """Return the continuous (float) position used for rendering."""

        progress = max(0.0, min(0.999, self._move_progress))
        return (
            self.x + self.direction_x * progress,
            self.y + self.direction_y * progress,
        )

    def set_direction(self, dx: int, dy: int) -> None:
        """Buffer next direction input."""

        if abs(dx) + abs(dy) != 1:
            return
        self.buffered_x = dx
        self.buffered_y = dy

    def update(
        self,
        dt: float,
        grid: Sequence[Sequence[object]],
        config: dict,
    ) -> None:
        """Update player position and check collisions."""

        if not grid or not grid[0]:
            return

        if self.buffered_x or self.buffered_y:
            if not _is_blocked(
                grid,
                self.x,
                self.y,
                self.buffered_x,
                self.buffered_y,
            ):
                if (
                    self.direction_x != self.buffered_x
                    or self.direction_y != self.buffered_y
                ):
                    # Visual snap-safety: drop any partial motion in the
                    # old direction so the sprite cannot leap diagonally.
                    self._move_progress = 0.0
                self.direction_x = self.buffered_x
                self.direction_y = self.buffered_y
                self.buffered_x = 0
                self.buffered_y = 0

        speed = float(config.get("player_speed", 5.0))
        # Cap accumulator at 1.0: at most one cell step per frame. Stops a
        # stalled player against a wall from banking 'fuel' and then
        # teleporting several cells when a path opens.
        self._move_progress = min(
            1.0, self._move_progress + max(0.0, speed * dt)
        )

        if self._move_progress >= 1.0 and (
            self.direction_x or self.direction_y
        ):
            if _is_blocked(
                grid,
                self.x,
                self.y,
                self.direction_x,
                self.direction_y,
            ):
                self.direction_x = 0
                self.direction_y = 0
                self._move_progress = 0.0
            else:
                self.x += self.direction_x
                self.y += self.direction_y
                self._move_progress -= 1.0

        # Halt visual interpolation when the next tile is a wall: prevents
        # Pac-Man from visually sliding into a wall before the next step.
        if (
            (self.direction_x or self.direction_y)
            and _is_blocked(
                grid,
                self.x,
                self.y,
                self.direction_x,
                self.direction_y,
            )
        ):
            self.direction_x = 0
            self.direction_y = 0
            self._move_progress = 0.0

    def lose_life(self) -> bool:
        """Lose one life and return True when no life remains."""

        self.lives = max(0, self.lives - 1)
        return self.lives == 0

    def respawn(self, spawn_pos: Tuple[int, int]) -> None:
        """Respawn at the given position."""

        self.x, self.y = spawn_pos
        self.spawn_x, self.spawn_y = spawn_pos
        self.direction_x = 0
        self.direction_y = 0
        self.buffered_x = 0
        self.buffered_y = 0
        self._move_progress = 0.0
