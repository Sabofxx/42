"""Maze loader and converter from MazeGenerator package."""

from __future__ import annotations

import sys
from typing import List, Tuple

try:
    from mazegenerator import MazeGenerator
except Exception:  # pragma: no cover - depends on environment
    MazeGenerator = None


TileGrid = List[List[str]]

WALL = "WALL"
WALL_42 = "WALL_42"
CORRIDOR = "CORRIDOR"
PACGUM = "PACGUM"
SUPER_PACGUM = "SUPER_PACGUM"
SPAWN_PACMAN = "SPAWN_PACMAN"
SPAWN_GHOST = "SPAWN_GHOST"

# Wall bit layout (per MazeGenerator):
#   bit 0 (1) = north wall, bit 1 (2) = east wall,
#   bit 2 (4) = south wall, bit 3 (8) = west wall.
_NORTH, _EAST, _SOUTH, _WEST = 1, 2, 4, 8


def _log(message: str) -> None:
    """Print a clear maze-loader warning."""

    print(f"[maze_loader] {message}", file=sys.stderr)


def _fallback_maze(width: int, height: int) -> List[List[int]]:
    """Build a deterministic empty fallback maze (no inner walls)."""

    maze: List[List[int]] = []
    for y in range(height):
        row: List[int] = []
        for x in range(width):
            mask = 0
            if y == 0:
                mask |= _NORTH
            if x == width - 1:
                mask |= _EAST
            if y == height - 1:
                mask |= _SOUTH
            if x == 0:
                mask |= _WEST
            row.append(mask)
        maze.append(row)
    return maze


def generate_maze(
    width: int,
    height: int,
    seed: int,
    perfect: bool = False,
) -> List[List[int]]:
    """Generate maze using the external MazeGenerator package."""

    if MazeGenerator is None:
        _log("mazegenerator package is unavailable, using fallback maze.")
        return _fallback_maze(width, height)

    try:
        generator = MazeGenerator(
            size=(width, height),
            perfect=bool(perfect),
            seed=seed,
        )
        maze = getattr(generator, "maze")
        if isinstance(maze, list) and maze and isinstance(maze[0], list):
            return maze
        raise TypeError("MazeGenerator.maze must be a list of lists.")
    except Exception as exc:
        _log(f"Maze generation failed: {exc}. Using fallback maze.")
        return _fallback_maze(width, height)


def convert_maze_to_tiles(
    maze: List[List[int]],
) -> Tuple[TileGrid, List[Tuple[int, int]]]:
    """Convert a bitmask maze into a 2x-scaled tile grid.

    Each maze cell (x, y) becomes the tile at (2x+1, 2y+1). Edges between
    cells become wall or corridor tiles. The outer ring is always WALL.

    Returns the tile grid and a list of spawn positions: index 0 is the
    Pac-Man spawn (center), and the next four are ghost spawns.
    """

    if not maze or not maze[0]:
        return [], []

    cells_h = len(maze)
    cells_w = len(maze[0])
    grid_w = 2 * cells_w + 1
    grid_h = 2 * cells_h + 1

    tiles: TileGrid = [[WALL for _ in range(grid_w)] for _ in range(grid_h)]

    for cy in range(cells_h):
        if len(maze[cy]) != cells_w:
            raise ValueError("Maze rows must have the same width.")
        for cx in range(cells_w):
            tx, ty = 2 * cx + 1, 2 * cy + 1
            mask = maze[cy][cx]
            if mask == 15:
                # Cell is part of the generator's '42' decoration. Tag it
                # distinctly so the renderer can colour it differently.
                tiles[ty][tx] = WALL_42
                continue
            tiles[ty][tx] = PACGUM
            # East opening
            if cx + 1 < cells_w and not (mask & _EAST):
                tiles[ty][tx + 1] = PACGUM
            # South opening
            if cy + 1 < cells_h and not (mask & _SOUTH):
                tiles[ty + 1][tx] = PACGUM

    # Super-pacgums at the four playable corner cells.
    corner_cells = [
        (0, 0),
        (cells_w - 1, 0),
        (0, cells_h - 1),
        (cells_w - 1, cells_h - 1),
    ]
    for cx, cy in corner_cells:
        tx, ty = 2 * cx + 1, 2 * cy + 1
        if tiles[ty][tx] != WALL:
            tiles[ty][tx] = SUPER_PACGUM

    # Pac-Man spawn at maze center.
    center_cx = cells_w // 2
    center_cy = cells_h // 2
    spawn_cell = _nearest_open_cell(maze, center_cx, center_cy)
    px, py = 2 * spawn_cell[0] + 1, 2 * spawn_cell[1] + 1
    tiles[py][px] = SPAWN_PACMAN

    # Ghost spawns: one per maze corner (per subject VI.1).
    ghost_cells = _ghost_corner_cells(maze)
    spawn_positions: List[Tuple[int, int]] = [(px, py)]
    for gcx, gcy in ghost_cells:
        gx, gy = 2 * gcx + 1, 2 * gcy + 1
        if tiles[gy][gx] not in (WALL, SPAWN_PACMAN, SUPER_PACGUM):
            tiles[gy][gx] = SPAWN_GHOST
        spawn_positions.append((gx, gy))

    return tiles, spawn_positions


def _nearest_open_cell(
    maze: List[List[int]],
    cx: int,
    cy: int,
) -> Tuple[int, int]:
    """Find an open (not fully walled) cell nearest to (cx, cy)."""

    cells_h = len(maze)
    cells_w = len(maze[0])
    best: Tuple[int, int] = (cx, cy)
    for radius in range(max(cells_w, cells_h)):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < cells_w and 0 <= ny < cells_h:
                    if maze[ny][nx] != 15:
                        return nx, ny
    return best


def _ghost_corner_cells(maze: List[List[int]]) -> List[Tuple[int, int]]:
    """Pick one open ghost spawn near each maze corner."""

    cells_h = len(maze)
    cells_w = len(maze[0])
    corners = [
        (0, 0),
        (cells_w - 1, 0),
        (0, cells_h - 1),
        (cells_w - 1, cells_h - 1),
    ]
    picks: List[Tuple[int, int]] = []
    for cx, cy in corners:
        picks.append(_nearest_open_cell(maze, cx, cy))
    return picks
