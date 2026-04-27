*This project has been created as part of the 42 curriculum by omischle.*

# A-Maze-ing

## Description

A maze generator written in Python that creates random mazes, outputs them in a hexadecimal wall-encoding format, and provides an interactive terminal visualization. The generator supports both perfect mazes (exactly one path between any two cells) and non-perfect mazes with multiple routes.

Key features:
- Recursive backtracker (DFS) maze generation algorithm
- Hexadecimal wall encoding output compatible with the moulinette validator
- Terminal ASCII rendering with ANSI colors
- Interactive menu: regenerate, show/hide shortest path, change wall colors
- Embedded "42" pattern drawn with fully closed cells
- Reusable `mazegen` Python package installable via pip

## Instructions

### Installation

```bash
# Install dependencies (flake8, mypy, build)
make install

# Or manually
pip install -r requirements.txt
```

### Running

```bash
# Run with default config
make run

# Run with a custom config
python3 a_maze_ing.py my_config.txt

# Debug mode
make debug
```

### Linting

```bash
make lint         # flake8 + mypy
make lint-strict  # flake8 + mypy --strict
```

### Building the package

```bash
make build
# Produces mazegen-1.0.0-py3-none-any.whl at the project root
```

## Configuration File Format

The config file uses `KEY=VALUE` pairs, one per line. Lines starting with `#` are comments.

| Key | Description | Example |
|-----|-------------|---------|
| `WIDTH` | Maze width in cells | `WIDTH=20` |
| `HEIGHT` | Maze height in cells | `HEIGHT=15` |
| `ENTRY` | Entry coordinates (x,y) | `ENTRY=0,0` |
| `EXIT` | Exit coordinates (x,y) | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Perfect maze (True/False) | `PERFECT=True` |
| `SEED` | (Optional) Random seed | `SEED=42` |

Example `config.txt`:
```
# My maze config
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## Maze Generation Algorithm

### Recursive Backtracker (DFS)

The algorithm uses an iterative depth-first search with backtracking:

1. Start from the entry cell, mark it as visited
2. While the stack is not empty:
   - Look at the current cell's unvisited neighbors
   - If there are unvisited neighbors, pick one at random, carve the wall between them, push the new cell onto the stack
   - If no unvisited neighbors, pop the stack (backtrack)
3. If any non-pattern cells remain unvisited (due to the 42 pattern splitting regions), connect them by carving a wall to a visited neighbor and continuing DFS

### Why this algorithm?

- Produces mazes with long, winding corridors that feel natural
- Guaranteed to produce a perfect maze (spanning tree) when no extra walls are removed
- Simple to implement iteratively, avoiding Python recursion limits
- Memory-efficient with an explicit stack

### Non-perfect mode

For non-perfect mazes, after generation ~20% of remaining internal walls are randomly removed. Each removal is validated to ensure no 3x3 open area exists (corridors stay at most 2 cells wide).

## Reusable Module: mazegen

The `mazegen` package contains the `MazeGenerator` class in a standalone module that can be imported in any Python project.

### Installation

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Usage

```python
from mazegen import MazeGenerator

# Create a 20x15 perfect maze with seed 42
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    perfect=True,
    seed=42,
)
gen.generate()

# Access the grid (2D list of wall integers)
for row in gen.grid:
    print(row)

# Get hex output
for line in gen.get_hex_grid():
    print(line)

# Get the shortest path as direction letters
path = gen.solution  # ['S', 'E', 'S', 'S', ...]

# Get path cell coordinates
cells = gen.get_path_cells()  # [(0,0), (1,0), ...]
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Number of columns (>= 2) |
| `height` | `int` | Number of rows (>= 2) |
| `entry` | `(int, int)` | Entry position (x, y) |
| `exit_pos` | `(int, int)` | Exit position (x, y) |
| `perfect` | `bool` | Perfect maze (default True) |
| `seed` | `int \| None` | Random seed (default None) |

### Wall encoding

Each cell is an integer where bits represent walls:
- Bit 0 (1) = North
- Bit 1 (2) = East
- Bit 2 (4) = South
- Bit 3 (8) = West

`0xF` (15) = all walls closed, `0x0` (0) = all walls open.

## Author

- **omischle**: Full project implementation

### Planning
1. Read and analyze the subject requirements
2. Design the MazeGenerator class and wall encoding
3. Implement core generation (recursive backtracker)
4. Add 42 pattern placement and BFS solver
5. Build the terminal display with interactive menu
6. Package as pip-installable module
7. Lint, test, and validate output

### What worked well
- Iterative DFS avoids stack overflow on large mazes
- Clean separation between generator (reusable) and display (project-specific)
- Wall coherency maintained by always updating both sides when carving

### What could be improved
- Add graphical MLX display as an alternative
- Support multiple generation algorithms (Prim's, Kruskal's)
- Animated generation display

### Tools used
- Python 3.10+
- flake8 / mypy for code quality
- setuptools for packaging

## Resources

- [Maze generation algorithms - Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive backtracker](https://en.wikipedia.org/wiki/Maze_generation_algorithm#Randomized_depth-first_search)
- [Python packaging guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- AI was used to assist with boilerplate code structure, flake8/mypy compliance, and documentation formatting. All logic was reviewed and validated manually.
