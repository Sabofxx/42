# Gantt — Timeline

| Phase | Days | Owner | Status |
|-------|------|-------|--------|
| 0. Bootstrapping (repo, Makefile, structure) | 1 | omischle + lel-ouaz | done |
| 1. Engine (config, maze, entities, game, scoring, cheat) | 2-5 | omischle | done |
| 2. UI (window, renderer, menus, HUD, screens, highscore) | 6-7 | lel-ouaz | done |
| 3. Integration, tests, polish | 7 | omischle + lel-ouaz | done |
| 4. Packaging (PyInstaller) + deployment (itch.io) | 8 | lel-ouaz | pending |

## Daily log

- **D1** repo skeleton, Makefile, config schema.
- **D2-3** engine modules (config, maze_loader, scoring, cheat).
- **D3-4** entities (player, ghost) + tests.
- **D4-5** game loop + maze conversion fix (2x scaled tiles, real walls).
- **D6-7** full UI (window, renderer, menu, HUD, screens) + highscore persistence.
- **D7** wiring `pac-man.py` end-to-end, headless smoke test.
- **D8** packaging + itch.io upload (todo).
