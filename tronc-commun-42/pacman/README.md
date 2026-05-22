*This project has been created as part of the 42 curriculum by lel-ouaz, omischle.*

# Pac-Man — Ghosts! More ghosts!

![status](https://img.shields.io/badge/build-passing-brightgreen)
![tests](https://img.shields.io/badge/tests-16%2F16-brightgreen)
![lint](https://img.shields.io/badge/flake8-clean-brightgreen)
![mypy](https://img.shields.io/badge/mypy-clean-brightgreen)

## Description

A modern Python recreation of the 1980 Namco arcade game **Pac-Man**, built
with `pygame` and an externally-supplied `A-Maze-ing` maze generator. Each
level is a procedurally-generated maze: collect every pacgum, avoid four
autonomous ghosts, grab a super-pacgum to flip the tables and eat them back.

Highlights:

- Strict separation between **engine** (no `pygame` imports) and **UI**
  (read-only access to a `GameState` snapshot).
- Maze tiles auto-scaled to `(2W+1)×(2H+1)` so that walls between cells are
  real, walkable-vs-blocked tiles (otherwise Pac-Man would clip).
- Ghosts with **distinct behaviours** — chase, ambush, random, scatter — and
  three state machines (`NORMAL`, `FRIGHTENED`, `EATEN`).
- Persistent **top-10 highscores** in JSON, corruption-safe, name-validated.
- A **cheat mode** for evaluators (single-key toggles) with a HUD overlay.
- Robust **error handling** at every boundary: no Python traceback ever
  reaches the user — only clear, prefixed messages.

## Instructions

### Install

```bash
make install        # installs pygame, mazegenerator wheel, dev tools
```

The assigned A-Maze-ing wheel is committed at the repository root as
`mazegenerator-2.0.2-py3-none-any.whl` (PEP-440-compliant name). `make
install` installs the wheel **and** the rest of `requirements.txt` in one
step.

### Run

```bash
make run                      # launches pac-man.py config.json
python3 pac-man.py config.json
```

The program takes **exactly one argument**: a `.json` configuration file.
Any error (missing file, bad JSON, invalid value) is logged with a clear
`[component] message` prefix; no Python traceback is ever shown.

### Test / Lint

```bash
make test          # 16 / 16 passing (pytest, headless SDL)
make lint          # flake8 + mypy (clean)
make lint-strict   # mypy --strict
make clean         # remove caches
make debug         # run under pdb
```

### Controls

| Key | Action |
|-----|--------|
| Arrow keys / WASD | move Pac-Man |
| ESC | pause / resume (in-game), back (menus) |
| ENTER / SPACE | confirm |
| `i` | toggle invincibility (cheat) |
| `l` | level skip (cheat) |
| `f` | freeze ghosts (cheat) |
| `+` | +1 life (cheat) |
| `s` | speed ×2 (cheat) |
| `p` | trigger power-up (cheat) — frightens all ghosts on demand so reviewers can test the 200/400/800/1600 chain without searching for a super-pacgum |

## Configuration

The config file uses JSON. Lines beginning with `#` are treated as comments
and stripped before parsing. JSON keys whose name starts with `#` are also
ignored silently (so the example `config.json` shipped in this repo, which
uses `"# comment": null` keys as section dividers, parses cleanly).

| Key | Default | Description |
|-----|---------|-------------|
| `highscore_filename` | `"highscores.json"` | path for persistent top-10 |
| `width`, `height` | `21`, `21` | maze dimensions (cells) |
| `perfect_maze` | `false` | A-Maze-ing `PERFECT` flag (subject requires `false`) |
| `seed` | `42` | fixed seed for level 1 |
| `lives` | `3` | starting lives |
| `player_speed` | `5.0` | cells per second |
| `ghost_speed` | `4.0` | cells per second |
| `level_max_time` | `90` | seconds per level |
| `num_levels` | `10` | levels to clear to win |
| `points_per_pacgum` | `10` | X in the subject |
| `points_per_super_pacgum` | `50` | Y |
| `points_per_ghost` | `200` | Z (multiplied 1→2→4→8 per chain) |
| `frightened_duration` | `10.0` | seconds a super-pacgum lasts |
| `respawn_delay` | `5.0` | seconds before an eaten ghost respawns |
| `window_width`, `window_height` | `672`, `756` | window size in pixels |
| `tile_size`, `fps` | `32`, `60` | render hint / frame cap |
| `color_*` | various `[r,g,b]` | UI colours (background, wall, pacgum, ghosts 1-4, …) |

**Faulty config handling**: any missing key falls back to its default; out-of-range
numbers are clamped; unknown keys are ignored. Bad JSON, unreadable file, or
non-object root all produce a logged warning and a fully-defaulted config —
the game still launches.

## Highscore system

Stored as a JSON array of `[name, score]` pairs at `highscore_filename`:

```json
[
  ["Sannaka", 1110],
  ["foliole", 20],
  ["Marmelade", 20],
  ["goldfish", 20]
]
```

**Why JSON + flat array**: human-readable, trivially diff-able, no schema
migration needed, and `json.loads` round-trips correctly with Python's
`list[tuple]`. The top 5 are also previewed on the main menu (matching the
subject screenshot).

Robustness rules enforced in `pacman/highscore.py`:

- File missing → empty list, no error.
- File corrupted (bad JSON, wrong shape, non-list entries) → empty list +
  a single `[highscore] ...` warning, never a traceback.
- Names are sanitised to **alphanumeric + space only**, **≤ 10 characters**,
  trimmed; empty → `"Player"`.
- Scores must be **non-negative integers**; anything else is dropped.
- Only **top 10** kept, sorted descending.
- The file is saved immediately after each `add_score()` call.

## Maze Generation

The external `mazegenerator.MazeGenerator` package is used **as-is**
(`pacman/maze_loader.py`):

```python
maze = MazeGenerator(
    size=(width, height),
    perfect=config["perfect_maze"],
    seed=seed,
).maze
```

It returns a `list[list[int]]` of `width × height` bitmasks. Each cell encodes
its walls — bit 0 = north, bit 1 = east, bit 2 = south, bit 3 = west.

A single cell ≠ a tile. To turn that abstract grid into a playable Pac-Man
board we **double-scale** it to `(2W+1) × (2H+1)`:

```
cell (cx,cy)    →    tile (2cx+1, 2cy+1)         corridor / pacgum
east edge       →    tile (2cx+2, 2cy+1)         WALL or PACGUM, per bitmask
south edge      →    tile (2cx+1, 2cy+2)         WALL or PACGUM, per bitmask
diagonal joints →    always WALL
outer ring      →    always WALL
```

Special tiles placed afterwards:

- **Pac-Man spawn** at the geometric centre (nearest open cell if blocked).
- **Super-pacgums** at the four maze corners.
- **Ghost spawns** at the four corners — one ghost per corner, as required
  by subject VI.1.

Level 1 uses `seed = 42` (subject requirement); subsequent levels draw a
random seed from a private RNG seeded by `config["seed"]`.

If the package fails to import or raises, a deterministic fallback maze
(open rectangle with outer walls) is generated so the game still runs.

## Implementation

| File | Owner | Purpose |
|------|-------|---------|
| `pac-man.py` | shared | entry point, arg/extension validation, top-level state machine |
| `pacman/config.py` | A | JSON+`#` parser, default merge, value clamping |
| `pacman/maze_loader.py` | A | `MazeGenerator` adapter + 2×-scaled tile conversion |
| `pacman/entities/player.py` | A | Pac-Man movement, life management, direction buffering |
| `pacman/entities/ghost.py` | A | four ghosts × `CHASE/AMBUSH/RANDOM/SCATTER` behaviours, `NORMAL/FRIGHTENED/EATEN` state machine, flee-when-frightened pathing |
| `pacman/game.py` | A | game loop, collision, pacgum/super pickup, level progression, `GameState` snapshot |
| `pacman/scoring.py` | A | point accumulation, 1→2→4→8 ghost chain multiplier |
| `pacman/cheat.py` | shared | cheat toggles + active state for HUD overlay |
| `pacman/highscore.py` | B | load / save / validate / top-10 |
| `pacman/ui/window.py` | B | pygame init, clock, input buffer, event pump |
| `pacman/ui/renderer.py` | B | maze, animated Pac-Man (mouth `sin`), ghosts (body + eyes + frightened blink), HUD bar, pause overlay, cheat overlay |
| `pacman/ui/menu.py` | B | main menu nav + embedded highscore preview |
| `pacman/ui/hud.py` | B | score / lives / level / time bar |
| `pacman/ui/screens.py` | B | pause, game-over, victory, name entry, instructions, highscores |
| `tests/` | B | 16 pytest cases (engine + UI + highscore) |
| `project_management/` | shared | Gantt, risks, team, acceptance, conflicts |

## General Software Architecture

```
                       pac-man.py (entry, state machine)
                                  │
              ┌───────────────────┴────────────────────┐
              ▼                                        ▼
       Engine (no pygame)                       UI (pygame)
       ──────────────────                       ───────────
       config.py                                ui/window.py
       maze_loader.py ◄── A-Maze-ing            ui/renderer.py
       entities/player.py                       ui/menu.py
       entities/ghost.py                        ui/hud.py
       game.py ──► GameState (read-only) ──►    ui/screens.py
       scoring.py                               highscore.py
       cheat.py ◄────────────────────────────►  (toggled by key in pac-man.py)
```

Communication is **one-way**: the engine exposes an immutable
`GameState` dataclass; the UI reads it and renders. The UI never mutates
engine state — only the entry point dispatches input back to `Game.update()`
and `CheatMode.toggle_cheat_by_key()`.

## Resources

### Documentation

- [Pygame docs](https://www.pygame.org/docs/) — Surface, Rect, Clock, KEYDOWN events
- [Pac-Man on Wikipedia](https://en.wikipedia.org/wiki/Pac-Man) — original
  ghost personalities (Blinky chases, Pinky ambushes, Inky random, Clyde scatters)
- [A-Maze-ing subject](https://42.fr) — bitmask wall encoding (N=1, E=2, S=4, W=8)
- [PEP 257](https://peps.python.org/pep-0257/) — docstring conventions
- PyInstaller [user guide](https://pyinstaller.org/) for the standalone build

### How AI was used

AI (Claude) was used as a paired-programming assistant. All AI output was
manually reviewed, edited, and tested. Concretely:

| Task | AI contribution | Human responsibility |
|------|-----------------|----------------------|
| Maze 2×-scale conversion design | proposed the `(2W+1) × (2H+1)` mapping when the original 1-tile-per-cell layout left no walls between cells | validated against the assigned package's bitmask semantics, wrote and fixed `convert_maze_to_tiles` |
| Ghost AI scaffolding | drafted the four behaviours and state transitions | tuned distances, fixed the frightened-mode flee (was random → now max-distance from player) |
| pygame boilerplate | window/clock/event pump pattern | input buffering policy, ESC routing to pause |
| Test cases | brainstormed edge cases (corrupted highscore file, ghost frightened timer expiry, wall blocking) | reviewed every assertion; rewrote the maze test after the corner-vs-ghost-spawn conflict |
| Documentation | first drafts of README sections | rewritten to match the actual code; AI-generated paragraphs that did not match implementation were deleted |

AI was **not** used for: the integration glue in `pac-man.py`, the decision
to embed the highscore preview in the main menu, the responsibility split
between A and B, nor the project-management documents.

Following the subject's AI guidelines: every block of generated code was
inspected, run, and tested before being kept. Anything we could not explain
line-by-line was rewritten by hand.

## Project Management

See [`project_management/`](project_management/):

- `GANTT.md` — daily timeline vs. actual progress.
- `RISKS.md` — identified risks and concrete mitigations.
- `TEAM.md` — role split and key design decisions.
- `ACCEPTANCE_TESTS.md` — full automated + manual test matrix (16 / 16 green).
- `CONFLICTS.md` — every blocking issue we hit and how we solved it.

## Deployment

A `pac-man.spec` is provided for PyInstaller:

```bash
pip install --user pyinstaller
pyinstaller pac-man.spec
# → dist/pac-man  (single-file executable)
```

The resulting binary is uploaded to **itch.io** (free / unlisted) for the
defense. The shipped archive contains `pac-man` + `config.json` and runs
out-of-the-box on Linux; a Windows build can be produced by running the same
spec on a Windows host.

## Known limitations

- Audio is intentionally not wired (subject allows skipping it).
- The main menu's highscore preview shows the top 5, not all 10 (subject
  screenshot shows 4); the full list is reachable via the **Highscores**
  menu entry.
