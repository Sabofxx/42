# Team

| Login | Role | Modules owned |
|-------|------|---------------|
| omischle | Engine / core logic | `config.py`, `maze_loader.py`, `entities/`, `game.py`, `scoring.py`, `cheat.py` |
| lel-ouaz | UI / packaging / docs | `highscore.py`, `ui/*`, `pac-man.py`, `tests/test_ui.py`, project docs |

## Decisions

- **Tile resolution = 2 × maze size + 1.** Required so walls between cells are first-class tiles, otherwise Pac-Man walks through walls.
- **Read-only `GameState` for UI.** Engine never imports pygame; UI never mutates game.
- **Cheats triggered by single keys (i / l / f / + / s).** Wired in `pac-man.py` event loop and routed to `CheatMode.toggle_cheat_by_key`.
- **Renderer computes tile size dynamically.** Window resolution can change without breaking layout.
- **Highscore file path is a config key.** Easy to switch between dev and eval runs.
