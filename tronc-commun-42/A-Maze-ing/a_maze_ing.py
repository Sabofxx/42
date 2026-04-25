#!/usr/bin/env python3

import random
import sys
from typing import Optional

from mazegen import EAST
from mazegen import MazeGenerator
from mazegen import NORTH
from mazegen import SOUTH
from mazegen import WEST

RESET = "\033[0m"
BOLD = "\033[1m"
FG_RED = "\033[91m"
FG_GREEN = "\033[92m"
FG_YELLOW = "\033[93m"
FG_BLUE = "\033[94m"
FG_MAGENTA = "\033[95m"
FG_CYAN = "\033[96m"
FG_WHITE = "\033[97m"

WALL_SCHEMES: list[str] = [
    FG_WHITE, FG_GREEN, FG_YELLOW, FG_BLUE,
]


def parse_config(path: str) -> dict[str, str]:
    config: dict[str, str] = {}
    with open(path, "r") as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                raise ValueError(
                    f"Bad config line: {stripped}"
                )
            key, val = stripped.split("=", 1)
            config[key.strip()] = val.strip()
    required = [
        "WIDTH", "HEIGHT", "ENTRY",
        "EXIT", "OUTPUT_FILE", "PERFECT",
    ]
    for key in required:
        if key not in config:
            raise ValueError(
                f"Missing required key: {key}"
            )
    return config


def parse_coords(text: str) -> tuple[int, int]:
    parts = text.split(",")
    if len(parts) != 2:
        raise ValueError(
            f"Invalid coordinates: {text}"
        )
    return int(parts[0].strip()), int(parts[1].strip())


def build_maze(
    config: dict[str, str],
) -> MazeGenerator:
    width = int(config["WIDTH"])
    height = int(config["HEIGHT"])
    entry = parse_coords(config["ENTRY"])
    exit_pos = parse_coords(config["EXIT"])
    perfect = config["PERFECT"].lower() in (
        "true", "1", "yes",
    )
    seed: Optional[int] = None
    if "SEED" in config:
        seed = int(config["SEED"])
    else:
        seed = random.randint(0, 2**31 - 1)
        config["SEED"] = str(seed)
    maze = MazeGenerator(
        width=width,
        height=height,
        entry=entry,
        exit_pos=exit_pos,
        perfect=perfect,
        seed=seed,
    )
    maze.generate()
    return maze


def write_output(
    maze: MazeGenerator, path: str,
) -> None:
    with open(path, "w") as fh:
        for line in maze.get_hex_grid():
            fh.write(line + "\n")
        fh.write("\n")
        fh.write(
            f"{maze.entry[0]},{maze.entry[1]}\n"
        )
        fh.write(
            f"{maze.exit_pos[0]},"
            f"{maze.exit_pos[1]}\n"
        )
        fh.write("".join(maze.solution) + "\n")


def build_display(
    maze: MazeGenerator,
) -> list[list[bool]]:
    h, w = maze.height, maze.width
    dh, dw = 2 * h + 1, 2 * w + 1
    disp: list[list[bool]] = [
        [False] * dw for _ in range(dh)
    ]
    for dr in range(h + 1):
        for dc in range(w + 1):
            disp[2 * dr][2 * dc] = True
    for row in range(h):
        for col in range(w):
            cell = maze.grid[row][col]
            if cell & NORTH:
                disp[2 * row][2 * col + 1] = True
            if cell & SOUTH:
                disp[2 * (row + 1)][2 * col + 1] = True
            if cell & WEST:
                disp[2 * row + 1][2 * col] = True
            if cell & EAST:
                disp[2 * row + 1][2 * (col + 1)] = True
    return disp


def render_maze(
    maze: MazeGenerator,
    show_path: bool = False,
    color_idx: int = 0,
) -> str:
    disp = build_display(maze)
    dh = len(disp)
    dw = len(disp[0]) if disp else 0
    wall_c = WALL_SCHEMES[color_idx % len(WALL_SCHEMES)]
    pat_c = FG_YELLOW
    path_set: set[tuple[int, int]] = set()
    if show_path:
        path_set = set(maze.get_path_cells())
    ey, ex = maze.entry[1], maze.entry[0]
    ty, tx = maze.exit_pos[1], maze.exit_pos[0]
    pat = maze.pattern_cells
    lines: list[str] = []
    for dr in range(dh):
        row = ""
        for dc in range(dw):
            is_cell = dr % 2 == 1 and dc % 2 == 1
            if is_cell:
                cr, cc = dr // 2, dc // 2
                if (cr, cc) in pat:
                    row += pat_c + "\u2588\u2588" + RESET
                elif (cr, cc) == (ey, ex):
                    row += (
                        FG_MAGENTA
                        + "\u2588\u2588"
                        + RESET
                    )
                elif (cr, cc) == (ty, tx):
                    row += (
                        FG_RED + "\u2588\u2588" + RESET
                    )
                elif (cr, cc) in path_set:
                    row += (
                        FG_CYAN + "\u2588\u2588" + RESET
                    )
                else:
                    row += "  "
            elif disp[dr][dc]:
                is_pat_wall = _is_pattern_wall(
                    dr, dc, maze,
                )
                if is_pat_wall:
                    row += pat_c + "\u2588\u2588" + RESET
                else:
                    row += (
                        wall_c + "\u2588\u2588" + RESET
                    )
            else:
                row += "  "
        lines.append(row)
    return "\n".join(lines)


def _is_pattern_wall(
    dr: int, dc: int, maze: MazeGenerator,
) -> bool:
    pat = maze.pattern_cells
    h, w = maze.height, maze.width
    if dr % 2 == 0 and dc % 2 == 1:
        above = dr // 2 - 1
        below = dr // 2
        cc = dc // 2
        a_ok = 0 <= above < h and (above, cc) in pat
        b_ok = 0 <= below < h and (below, cc) in pat
        return a_ok and b_ok
    if dr % 2 == 1 and dc % 2 == 0:
        left = dc // 2 - 1
        right = dc // 2
        cr = dr // 2
        l_ok = 0 <= left < w and (cr, left) in pat
        r_ok = 0 <= right < w and (cr, right) in pat
        return l_ok and r_ok
    if dr % 2 == 0 and dc % 2 == 0:
        adj = [
            (dr // 2 - 1, dc // 2 - 1),
            (dr // 2 - 1, dc // 2),
            (dr // 2, dc // 2 - 1),
            (dr // 2, dc // 2),
        ]
        count = sum(
            1 for ar, ac in adj
            if 0 <= ar < h and 0 <= ac < w
            and (ar, ac) in pat
        )
        return count >= 3
    return False


def interactive_loop(
    maze: MazeGenerator,
    config: dict[str, str],
) -> None:
    show_path = False
    color_idx = 0
    while True:
        print("\033[2J\033[H", end="", flush=True)
        print(render_maze(maze, show_path, color_idx))
        print(f"\n{BOLD}=== A-Maze-ing ==={RESET}")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "1":
            config["SEED"] = str(
                random.randint(0, 2**31 - 1)
            )
            maze = build_maze(config)
            write_output(maze, config["OUTPUT_FILE"])
            show_path = False
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_idx = (color_idx + 1) % len(
                WALL_SCHEMES
            )
        elif choice == "4":
            break


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py <config>",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        config = parse_config(sys.argv[1])
        maze = build_maze(config)
        write_output(maze, config["OUTPUT_FILE"])
        interactive_loop(maze, config)
    except FileNotFoundError:
        print(
            f"Error: '{sys.argv[1]}' not found.",
            file=sys.stderr,
        )
        sys.exit(1)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        sys.exit(0)


if __name__ == "__main__":
    main()
