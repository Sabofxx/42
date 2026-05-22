# Risks

| # | Risk | Likelihood | Impact | Owner | Mitigation |
|---|------|-----------|--------|-------|------------|
| 1 | mazegenerator wheel name not PEP-440 → pip refuses | medium | high | lel-ouaz | rename wheel to `mazegenerator-2.0.2-py3-none-any.whl` before install |
| 2 | Single-cell-per-tile maze leaves no wall between cells | high | high | omischle | scale grid to 2N+1; edges become wall/corridor tiles (fixed) |
| 3 | Ghost spawns on top of Pac-Man → instant game over | medium | high | omischle | spawn ghosts ≥2 cells away + 2s respawn grace |
| 4 | Config file with `#` comments crashes JSON parser | high | medium | omischle | `_strip_comments` removes `#` lines; unknown `#` keys silently dropped |
| 5 | Highscore file corrupted between sessions | low | low | lel-ouaz | catch JSON errors; start empty + log warning |
| 6 | Pygame not installed on evaluator machine | medium | high | lel-ouaz | clear error in `pac-man.py`, `make install` uses requirements.txt |
| 7 | Window resolution mismatch with maze size | medium | medium | lel-ouaz | renderer computes tile_size dynamically and centers playfield |
