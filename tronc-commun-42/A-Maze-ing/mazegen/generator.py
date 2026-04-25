import random
from collections import deque
from typing import Optional


NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8
ALL_WALLS: int = NORTH | EAST | SOUTH | WEST

DIRECTIONS: list[tuple[int, int, int, int]] = [
    (-1, 0, NORTH, SOUTH),
    (0, 1, EAST, WEST),
    (1, 0, SOUTH, NORTH),
    (0, -1, WEST, EAST),
]

DIR_LETTERS: dict[tuple[int, int], str] = {
    (-1, 0): "N",
    (0, 1): "E",
    (1, 0): "S",
    (0, -1): "W",
}

DIGIT_4: list[list[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

DIGIT_2: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]


class MazeGenerator:

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_pos: tuple[int, int],
        perfect: bool = True,
        seed: Optional[int] = None,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError("Maze must be at least 2x2.")
        ex, ey = entry
        if not (0 <= ex < width and 0 <= ey < height):
            raise ValueError("Entry out of bounds.")
        ox, oy = exit_pos
        if not (0 <= ox < width and 0 <= oy < height):
            raise ValueError("Exit out of bounds.")
        if entry == exit_pos:
            raise ValueError(
                "Entry and exit must be different."
            )
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_pos = exit_pos
        self.perfect = perfect
        self.seed = seed
        self.grid: list[list[int]] = []
        self.pattern_cells: set[tuple[int, int]] = set()
        self._path: list[str] = []

    def generate(self) -> None:
        if self.seed is not None:
            random.seed(self.seed)
        else:
            random.seed()
        self.grid = [
            [ALL_WALLS] * self.width
            for _ in range(self.height)
        ]
        self.pattern_cells = set()
        self._place_42()
        self._validate_overlap()
        self._carve_dfs()
        if not self.perfect:
            self._remove_extra_walls()
        self._enforce_borders()
        self._path = self._solve()

    def _validate_overlap(self) -> None:
        e_yx = (self.entry[1], self.entry[0])
        x_yx = (self.exit_pos[1], self.exit_pos[0])
        if e_yx in self.pattern_cells:
            raise ValueError(
                "Entry overlaps with 42 pattern."
            )
        if x_yx in self.pattern_cells:
            raise ValueError(
                "Exit overlaps with 42 pattern."
            )

    def _place_42(self) -> None:
        pat_h, pat_w = 5, 7
        if (self.height < pat_h + 2
                or self.width < pat_w + 2):
            print(
                "Warning: maze too small for "
                "'42' pattern, skipping."
            )
            return
        sy = (self.height - pat_h) // 2
        sx = (self.width - pat_w) // 2
        for r in range(pat_h):
            for c in range(3):
                if DIGIT_4[r][c]:
                    self.pattern_cells.add(
                        (sy + r, sx + c)
                    )
                if DIGIT_2[r][c]:
                    self.pattern_cells.add(
                        (sy + r, sx + 4 + c)
                    )
        for row, col in self.pattern_cells:
            self.grid[row][col] = ALL_WALLS

    def _carve_dfs(self) -> None:
        visited: set[tuple[int, int]] = set(
            self.pattern_cells
        )
        start_y = self.entry[1]
        start_x = self.entry[0]

        def dfs(start: tuple[int, int]) -> None:
            stack = [start]
            visited.add(start)
            while stack:
                cy, cx = stack[-1]
                nbrs: list[
                    tuple[int, int, int, int]
                ] = []
                for dy, dx, wc, wn in DIRECTIONS:
                    ny, nx = cy + dy, cx + dx
                    if (
                        0 <= ny < self.height
                        and 0 <= nx < self.width
                        and (ny, nx) not in visited
                    ):
                        nbrs.append((ny, nx, wc, wn))
                if nbrs:
                    ny, nx, wc, wn = random.choice(
                        nbrs
                    )
                    self.grid[cy][cx] &= ~wc
                    self.grid[ny][nx] &= ~wn
                    visited.add((ny, nx))
                    stack.append((ny, nx))
                else:
                    stack.pop()

        dfs((start_y, start_x))
        non_pat: set[tuple[int, int]] = {
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
        } - self.pattern_cells
        unvis = non_pat - visited
        while unvis:
            found = False
            for uy, ux in list(unvis):
                if found:
                    break
                for dy, dx, wc, wn in DIRECTIONS:
                    ny, nx = uy + dy, ux + dx
                    if (
                        (ny, nx) in visited
                        and (ny, nx)
                        not in self.pattern_cells
                    ):
                        self.grid[uy][ux] &= ~wc
                        self.grid[ny][nx] &= ~wn
                        dfs((uy, ux))
                        unvis = non_pat - visited
                        found = True
                        break
            if not found:
                break

    def _remove_extra_walls(self) -> None:
        walls: list[
            tuple[int, int, int, int, int, int]
        ] = []
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) in self.pattern_cells:
                    continue
                if (
                    col + 1 < self.width
                    and self.grid[row][col] & EAST
                    and (row, col + 1)
                    not in self.pattern_cells
                ):
                    walls.append((
                        row, col, EAST,
                        row, col + 1, WEST,
                    ))
                if (
                    row + 1 < self.height
                    and self.grid[row][col] & SOUTH
                    and (row + 1, col)
                    not in self.pattern_cells
                ):
                    walls.append((
                        row, col, SOUTH,
                        row + 1, col, NORTH,
                    ))
        random.shuffle(walls)
        target = max(1, len(walls) // 5)
        removed = 0
        for r1, c1, w1, r2, c2, w2 in walls:
            if removed >= target:
                break
            self.grid[r1][c1] &= ~w1
            self.grid[r2][c2] &= ~w2
            if self._has_3x3_open():
                self.grid[r1][c1] |= w1
                self.grid[r2][c2] |= w2
            else:
                removed += 1

    def _has_3x3_open(self) -> bool:
        for row in range(self.height - 2):
            for col in range(self.width - 2):
                if self._is_open_3x3(row, col):
                    return True
        return False

    def _is_open_3x3(
        self, sy: int, sx: int,
    ) -> bool:
        for row in range(sy, sy + 3):
            for col in range(sx, sx + 2):
                if self.grid[row][col] & EAST:
                    return False
        for row in range(sy, sy + 2):
            for col in range(sx, sx + 3):
                if self.grid[row][col] & SOUTH:
                    return False
        return True

    def _enforce_borders(self) -> None:
        for col in range(self.width):
            self.grid[0][col] |= NORTH
            self.grid[self.height - 1][col] |= SOUTH
        for row in range(self.height):
            self.grid[row][0] |= WEST
            self.grid[row][self.width - 1] |= EAST

    def _solve(self) -> list[str]:
        ey, ex = self.entry[1], self.entry[0]
        ty, tx = self.exit_pos[1], self.exit_pos[0]
        queue: deque[tuple[int, int]] = deque()
        queue.append((ey, ex))
        seen: set[tuple[int, int]] = {(ey, ex)}
        parent: dict[
            tuple[int, int],
            tuple[int, int, str],
        ] = {}
        wall_map: dict[tuple[int, int], int] = {
            (-1, 0): NORTH,
            (0, 1): EAST,
            (1, 0): SOUTH,
            (0, -1): WEST,
        }
        while queue:
            cy, cx = queue.popleft()
            if (cy, cx) == (ty, tx):
                break
            for delta, wall in wall_map.items():
                if self.grid[cy][cx] & wall:
                    continue
                dy, dx = delta
                ny, nx = cy + dy, cx + dx
                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and (ny, nx) not in seen
                ):
                    seen.add((ny, nx))
                    ltr = DIR_LETTERS[delta]
                    parent[(ny, nx)] = (cy, cx, ltr)
                    queue.append((ny, nx))
        path: list[str] = []
        pos = (ty, tx)
        while pos in parent:
            py, px, ltr = parent[pos]
            path.append(ltr)
            pos = (py, px)
        path.reverse()
        return path

    @property
    def solution(self) -> list[str]:
        return list(self._path)

    def get_path_cells(self) -> list[tuple[int, int]]:
        cells: list[tuple[int, int]] = []
        row, col = self.entry[1], self.entry[0]
        cells.append((row, col))
        for direction in self._path:
            if direction == "N":
                row -= 1
            elif direction == "E":
                col += 1
            elif direction == "S":
                row += 1
            elif direction == "W":
                col -= 1
            cells.append((row, col))
        return cells

    def get_hex_grid(self) -> list[str]:
        return [
            "".join(f"{cell:X}" for cell in row)
            for row in self.grid
        ]
