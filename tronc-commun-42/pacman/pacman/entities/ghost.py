"""Ghost entities with distinct AI behaviors."""

from __future__ import annotations

import random
from collections import deque
from enum import Enum
from typing import List, Optional, Sequence, Tuple


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


def _bfs_next_step(
    grid: Sequence[Sequence[object]],
    start: Tuple[int, int],
    target: Tuple[int, int],
    forbid: Optional[Tuple[int, int]] = None,
) -> Optional[Tuple[int, int]]:
    """Return the first direction along the shortest path to ``target``.

    Walls block the search; ``forbid`` is an outgoing direction that may not
    be taken from ``start`` (used to enforce the no-reverse rule). Returns
    ``None`` when no path exists.
    """

    if start == target:
        return None
    sx, sy = start
    if not grid or sy < 0 or sy >= len(grid):
        return None
    if sx < 0 or sx >= len(grid[sy]):
        return None
    visited = {start}
    queue: "deque[Tuple[int, int, Tuple[int, int]]]" = deque()
    candidates = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for dx, dy in candidates:
        if forbid == (dx, dy):
            continue
        if _is_blocked(grid, sx, sy, dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        queue.append((nx, ny, (dx, dy)))
        visited.add((nx, ny))
    while queue:
        x, y, first_step = queue.popleft()
        if (x, y) == target:
            return first_step
        for dx, dy in candidates:
            if _is_blocked(grid, x, y, dx, dy):
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            queue.append((nx, ny, first_step))
    return None


class GhostBehavior(Enum):
    """Ghost behavior types."""

    CHASE = "chase"
    AMBUSH = "ambush"
    RANDOM = "random"
    SCATTER = "scatter"


class GhostState(Enum):
    """Ghost state types."""

    NORMAL = "normal"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


class Ghost:
    """Represents a single ghost."""

    def __init__(
        self,
        x: int,
        y: int,
        ghost_id: int,
        behavior: GhostBehavior,
    ) -> None:
        self.x = x
        self.y = y
        self.spawn_x = x
        self.spawn_y = y
        self.ghost_id = ghost_id
        self.behavior = behavior
        self.state = GhostState.NORMAL
        self.direction_x = 0
        self.direction_y = 0
        self._move_progress = 0.0
        self._state_timer = 0.0
        self._random = random.Random(ghost_id * 997 + x * 31 + y * 17)
        # Per-ghost scatter corner; populated lazily from the grid bounds.
        self.scatter_target: Tuple[int, int] = (x, y)

    @property
    def pos(self) -> Tuple[int, int]:
        """Return the current position."""

        return self.x, self.y

    @property
    def dir(self) -> Tuple[int, int]:
        """Return the current direction."""

        return self.direction_x, self.direction_y

    @property
    def visual_pos(self) -> Tuple[float, float]:
        """Continuous position interpolated between grid cells."""

        progress = max(0.0, min(0.999, self._move_progress))
        return (
            self.x + self.direction_x * progress,
            self.y + self.direction_y * progress,
        )

    @property
    def state_time_left(self) -> float:
        """Remaining seconds in the current timed state (0 if untimed)."""

        return max(0.0, self._state_timer)

    def set_state(self, state: GhostState, duration: float = 0.0) -> None:
        """Set ghost state (NORMAL, FRIGHTENED, EATEN)."""

        previous = self.state
        self.state = state
        self._state_timer = max(0.0, duration)
        if state == GhostState.NORMAL:
            self.direction_x = 0
            self.direction_y = 0
        if state == GhostState.EATEN and duration <= 0.0:
            self._state_timer = 0.1
        # Classic rule: reverse on transition into frightened.
        if state == GhostState.FRIGHTENED and previous != GhostState.FRIGHTENED:
            self.direction_x = -self.direction_x
            self.direction_y = -self.direction_y
            self._move_progress = 0.0

    def _neighbors(
        self,
        grid: Sequence[Sequence[object]],
        forbid_reverse: bool = True,
    ) -> List[Tuple[int, int]]:
        """Return walkable neighboring directions.

        When the ghost has a current heading, we drop the reverse direction
        (classic Pac-Man rule: ghosts only reverse at dead-ends or on
        explicit state changes). If forbidding the reverse would leave no
        choice, we fall back to the full neighbor list.
        """

        candidates = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        all_open = [
            (dx, dy)
            for dx, dy in candidates
            if not _is_blocked(grid, self.x, self.y, dx, dy)
        ]
        if not forbid_reverse or (self.direction_x, self.direction_y) == (0, 0):
            return all_open
        reverse = (-self.direction_x, -self.direction_y)
        filtered = [n for n in all_open if n != reverse]
        return filtered or all_open

    def _pick_direction(
        self,
        grid: Sequence[Sequence[object]],
        player_pos: Tuple[int, int],
        player_dir: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Pick a direction according to the current ghost behavior."""

        neighbors = self._neighbors(grid)
        if not neighbors:
            return 0, 0

        if self.state == GhostState.FRIGHTENED:
            def flee_score(direction: Tuple[int, int]) -> int:
                nx = self.x + direction[0]
                ny = self.y + direction[1]
                return abs(nx - player_pos[0]) + abs(ny - player_pos[1])
            if self._random.random() < 0.85:
                return max(neighbors, key=flee_score)
            return self._random.choice(neighbors)

        if self.state == GhostState.EATEN:
            target = (self.spawn_x, self.spawn_y)
        elif self.behavior == GhostBehavior.RANDOM:
            return self._random.choice(neighbors)
        elif self.behavior == GhostBehavior.SCATTER:
            target = self.scatter_target
        elif self.behavior == GhostBehavior.AMBUSH:
            # Pinky-style: aim 4 tiles ahead of Pac-Man.
            target = (
                player_pos[0] + player_dir[0] * 4,
                player_pos[1] + player_dir[1] * 4,
            )
        else:  # CHASE
            target = player_pos

        # Use BFS for a true shortest-path step. The forbidden direction is
        # the reverse of our current heading (preserves the no-reverse rule).
        forbid = None
        if (self.direction_x, self.direction_y) != (0, 0):
            forbid = (-self.direction_x, -self.direction_y)
        step = _bfs_next_step(grid, (self.x, self.y), target, forbid)
        if step is not None and step in neighbors:
            return step

        # Target unreachable (e.g. inside a wall) or path required reversing:
        # fall back to the closest open neighbour by squared distance.
        def squared_dist(direction: Tuple[int, int]) -> int:
            next_x = self.x + direction[0]
            next_y = self.y + direction[1]
            dx = next_x - target[0]
            dy = next_y - target[1]
            return dx * dx + dy * dy

        return min(neighbors, key=squared_dist)

    def update(
        self,
        dt: float,
        grid: Sequence[Sequence[object]],
        player_pos: Tuple[int, int],
        config: dict,
        player_dir: Tuple[int, int] = (0, 0),
    ) -> None:
        """Update ghost position based on behavior and state."""

        if self._state_timer > 0.0:
            self._state_timer = max(0.0, self._state_timer - dt)
            if self._state_timer == 0.0 and self.state == GhostState.EATEN:
                self.respawn((self.spawn_x, self.spawn_y))
                return
            if (
                self._state_timer == 0.0
                and self.state == GhostState.FRIGHTENED
            ):
                self.state = GhostState.NORMAL

        if self.state == GhostState.EATEN:
            return

        speed = float(config.get("ghost_speed", 4.0))
        if self.state == GhostState.FRIGHTENED:
            speed *= 0.6

        # On level start or after a hard reset the ghost has no direction;
        # pick one before accumulating progress so visual interp has a
        # heading to use.
        if (self.direction_x, self.direction_y) == (0, 0):
            new_dir = self._pick_direction(grid, player_pos, player_dir)
            self.direction_x, self.direction_y = new_dir

        # Cap to one cell per frame: prevents banked progress from teleporting
        # a ghost across multiple tiles when something unblocks suddenly.
        self._move_progress = min(
            1.0, self._move_progress + max(0.0, speed * dt)
        )

        if self._move_progress >= 1.0:
            # Crossing the current cell completes. Commit the step if the
            # heading still points to an open neighbour.
            if not _is_blocked(
                grid, self.x, self.y, self.direction_x, self.direction_y
            ):
                self.x += self.direction_x
                self.y += self.direction_y
                self._move_progress -= 1.0
            else:
                self._move_progress = 0.0

            # At the new cell centre, choose the next heading. This is the
            # ONLY place we change direction so the visual interpolation is
            # guaranteed to be linear across one full cell crossing.
            new_dir = self._pick_direction(grid, player_pos, player_dir)
            self.direction_x, self.direction_y = new_dir

    def respawn(self, spawn_pos: Tuple[int, int]) -> None:
        """Respawn ghost to corner."""

        self.x, self.y = spawn_pos
        self.spawn_x, self.spawn_y = spawn_pos
        self.state = GhostState.NORMAL
        self.direction_x = 0
        self.direction_y = 0
        self._move_progress = 0.0
        self._state_timer = 0.0

    @staticmethod
    def get_all_ghosts() -> List["Ghost"]:
        """Create four ghosts with different behaviors."""

        return [
            Ghost(1, 1, 0, GhostBehavior.CHASE),
            Ghost(3, 1, 1, GhostBehavior.AMBUSH),
            Ghost(1, 3, 2, GhostBehavior.RANDOM),
            Ghost(3, 3, 3, GhostBehavior.SCATTER),
        ]
