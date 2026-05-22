# Acceptance Tests

## Automated (`make test`)

- `test_parse_config_with_comments` — `#` lines stripped, unknown keys ignored
- `test_parse_config_missing_file_uses_defaults`
- `test_parse_config_invalid_json` — recovers with defaults, no traceback
- `test_scoring_multiplier_and_reset` — 200 / 400 / 800 / 1600 sequence
- `test_cheat_toggles` — invincibility, freeze, +life, speed, by-key dispatch
- `test_maze_conversion_doubles_grid` — 7×7 raw → 15×15 tiles + spawns + super pacgums
- `test_player_blocked_by_wall` — walls actually block movement
- `test_ghost_chases_player` — CHASE behavior makes ghost reach player
- `test_ghost_frightened_then_normal` — frightened timer expires
- `test_game_smoke_update` — game runs 50 ticks without crash
- `test_game_pacgum_collection` — pacgum count strictly decreases
- `test_validate_name_basic` — sanitization rules (alnum + space, ≤10 chars)
- `test_highscore_persistence` — JSON round-trip
- `test_highscore_corruption_recovery` — bad file → empty list, no crash
- `test_highscore_keeps_top_10`
- `test_ui_modules_import` — every UI class constructs without raising

Status: **16 / 16 passing**.

Engine tests owned by **omischle**, UI / highscore tests owned by **lel-ouaz**.

## Manual (run `make run`)

| # | Step | Expected | Validator |
|---|------|----------|-----------|
| M1 | Launch — main menu visible | Title + 4 options highlighted | lel-ouaz |
| M2 | Start game | Maze renders, Pac-Man at center, 4 ghosts spawn offset | omischle |
| M3 | Press arrow / WASD | Pac-Man moves and eats pacgums (score increments) | omischle |
| M4 | Eat super-pacgum | Ghosts turn blue, brief frightened state | omischle |
| M5 | Eat frightened ghost | +200 → +400 → +800 → +1600 | omischle |
| M6 | Press ESC | Pause overlay appears, options selectable | lel-ouaz |
| M7 | Lose all lives | Game-over screen, then name entry, then highscore stored | lel-ouaz |
| M8 | Press `i` during play | INVINCIBLE overlay appears, ghost hits ignored | omischle |
| M9 | Press `l` during play | Skip to next level | omischle |
| M10 | Quit and restart | Highscores screen shows previously stored name | lel-ouaz |
