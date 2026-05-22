# Conflicts and resolutions

| # | Issue | Raised by | Resolved by | Resolution |
|---|-------|-----------|-------------|------------|
| 1 | mazegenerator wheel rejected by pip (`00001` not PEP-440) | lel-ouaz | lel-ouaz | rename to `mazegenerator-2.0.2-py3-none-any.whl` before `pip install`; `make install` works on the renamed copy |
| 2 | Maze cells stored as 1-tile-per-cell hid all walls | lel-ouaz | omischle | `convert_maze_to_tiles` now scales to (2W+1)×(2H+1); walls between cells are explicit tiles |
| 3 | Ghosts spawned adjacent to Pac-Man → instant death | lel-ouaz | omischle | larger spawn offsets + 2s `_respawn_grace` after level start and respawn |
| 4 | `config.json` uses `"# key"` comment keys | omischle | omischle | `_strip_comments` removes `#` lines; remaining `#` keys silently ignored (no warning spam) |
| 5 | Ghost spawn cells could overwrite super-pacgum tiles in the four corners | lel-ouaz | omischle | corner tiles keep their `SUPER_PACGUM` value; ghost spawn positions are tracked separately so the renderer can still draw the pellet under the ghost |
