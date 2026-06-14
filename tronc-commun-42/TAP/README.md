*This project has been created as part of the 42 curriculum by omischle [, <login2>[, <login3>]].*

# TAP — The Answer Protocol

A shared-world, retro text adventure (a small MUD). A TCP server hosts one
persistent-feeling world; multiple players connect, explore rooms, chat,
trade items, talk to NPCs, fight enemies and complete quests in real time.
Two clients are provided: a command-line client and a graphical (web-based)
client. The server speaks the line-based **RFC 42TAP** protocol.

## Description

The goal is a multiplayer text adventure built around a simple, line-oriented
TCP protocol. The server is authoritative: it owns the world state and
enforces all rules (movement, presence, item ownership, combat, quests,
groups and chat). Clients are thin — they send protocol commands and react to
synchronous responses and asynchronous events.

- **Server** — implements every command and event of RFC 42TAP, loads the
  static world from JSON, validates it, and serves many concurrent players.
- **CLI client** — raw-protocol terminal client.
- **GUI client** — a self-contained Go program that bridges a browser UI to
  the server over TCP (web-based GUI).

Language: **Go** (standard library only — no third-party dependencies).
Python is not used anywhere in the deliverable.

## Instructions

Requirements: a Go toolchain (>= 1.18) and GNU Make.

```sh
make deps     # resolve modules (standard library only — effectively a no-op)
make build    # compile bin/tap-server, bin/tap-cli, bin/tap-gui
make lint     # go vet + gofmt compliance check
make test     # run the Go test suite
make clean    # remove ./bin
```

Run each component (see **Building and Running** for all options):

```sh
make run-server                 # listens on 127.0.0.1:4242 by default
make run-cli                    # connects to 127.0.0.1:4242
make run-gui                    # bridge UI on http://127.0.0.1:8080
```

## Building and Running

The build tool is **GNU Make** driving the Go toolchain. Binaries land in
`./bin`. All addresses are overridable via Make variables or binary flags.

### Server

```sh
make run-server ADDR=127.0.0.1:4242 WORLD=data/world.json
# or directly:
./bin/tap-server -addr :4242 -world data/world.json
```

Structured JSON logs are written to **stderr**; redirect them to a file with
`2> server.log`. Game state is in-memory and resets on restart (no
persistence is required).

### CLI client

```sh
make run-cli ADDR=127.0.0.1:4242
# or:
./bin/tap-cli -addr 127.0.0.1:4242 -name alice
```

After the greeting, type protocol commands directly (e.g. `CONNECT alice`,
`LOOK`, `MOVE north`, `CHAT GLOBAL hi`). Lines received from the server are
printed as `S< ...` in real time, even while you are typing. The optional
`-name` flag auto-sends `CONNECT <name>`.

### GUI client

```sh
make run-gui ADDR=127.0.0.1:4242 HTTP=127.0.0.1:8080
# or:
./bin/tap-gui -addr 127.0.0.1:4242 -http 127.0.0.1:8080
```

Then open <http://127.0.0.1:8080>. Enter a username and click **CONNECT**.
The page shows the room (with clickable exits), items (with TAKE buttons),
NPCs (TALK / ATTACK / QUEST buttons), the player inventory (DROP buttons),
separated chat views (Global / Room / Group), live player counters, an HP
bar, and a raw protocol log. The room view refreshes automatically after
TAKE/DROP/MOVE and on relevant world events.

## Architecture

**Server design — dispatcher + single-writer concurrency.**

- One goroutine per TCP connection reads and frames messages (handling TCP
  fragmentation and coalescing via a buffered reader, one LF-terminated line
  at a time, with a 1024-byte line cap).
- A **command dispatcher** (`internal/game.Handle`) maps each command name to
  a handler. Command names are case-insensitive.
- All mutable world state lives in `internal/game.Game` and is guarded by a
  **single mutex**. Every handler runs under that lock, so the world is always
  mutated serially and consistently — simple to reason about and free of data
  races (verified with `go test -race`).
- Outbound delivery is **decoupled**: each player owns a buffered channel and
  a dedicated writer goroutine. Broadcasts (performed while holding the lock)
  do non-blocking sends, so a slow or disconnecting client can never stall a
  broadcast to everyone else. On disconnect, player state is removed *before*
  the LEAVE event is broadcast.

Package layout:

```
cmd/server   server entrypoint (flags, wiring)
cmd/cli      raw-protocol terminal client
cmd/gui      TCP↔browser bridge + embedded web UI
internal/protocol   message parsing, response/error/event formatting, error codes
internal/world      world model, JSON loader, referential-integrity validation
internal/game       authoritative state: rooms, items, NPCs, combat, quests, groups, chat
internal/server     TCP listener, framing, auth, dispatch wiring, abuse monitoring
internal/logging    structured JSON logger
data/world.json     the static world
```

GUI toolkit choice: a **web UI** served by a small Go HTTP bridge. The bridge
opens one TCP connection to the server, streams every server line to the
browser via **Server-Sent Events** (`/events`) and forwards browser commands
over TCP via **HTTP POST** (`/cmd`). This keeps the GUI dependency-free
(standard library only) and portable, while still speaking the real TCP
protocol to the server.

## Protocol Implementation

The implementation follows RFC 42TAP. Where the RFC prose and the subject's
worked examples differ, or where the RFC explicitly leaves things to the
implementer, we made the following documented choices/deviations:

- **WHO** returns JSON `{"room":[...],"server":N}` (as in the subject's
  example interactions) rather than the RFC prose form `OK players=<count>`.
  The richer payload is needed for the GUI's room/server counters.
- **TALK** returns JSON `{"npc":"<id>","dialogue":"<line>"}` (subject example
  form) rather than the RFC prose form `OK <dialogue>`, for structured display.
- **Additional error codes** (documented extensions):
  `400 BAD_REQUEST` (malformed/unknown command), `202 NOT_CONNECTED`
  (command before CONNECT), `203 ALREADY_CONNECTED`, `407 NOT_IN_COMBAT`
  (DEFEND/FLEE with no active combat), `408 TARGET_MISSING` (missing argument).
- **Additional combat commands** `DEFEND` and `FLEE` (the RFC invites these).
- **Event format.** Presence/chat events follow the examples exactly
  (`EVT ROOM PRESENCE ENTER <player>`, `EVT GLOBAL CHAT <player> <msg>`, …).
  The stats event is emitted as `EVT STATS PLAYERS players=<n>`. A few extra
  informational events are pushed: `EVT ROOM ITEM <player> took|dropped <id>`,
  `EVT ROOM COMBAT <text>`, `EVT QUEST COMPLETE <id>`, `EVT QUEST OBJECTIVE
  <id> ...`. Clients may ignore unknown events.
- **ROOM-scoped chat** is echoed to the sender too (everyone in the room).
- **Disconnect item handling.** Items held by a leaving player are dropped
  back into their current room, so unique item instances are never lost.
- **Resource resolution.** Items/NPCs match by canonical id, display name, or
  the id suffix after the dot — all case-insensitive (RFC 8.3). Multi-word
  display names are supported.

Implemented command set (every command/event from the protocol document):
`CONNECT, LOOK, MOVE, QUIT, CHAT, WHO, GROUP CREATE/INVITE/JOIN/LEAVE, TAKE,
DROP, INVENTORY, TALK, ATTACK, DEFEND, FLEE, STATUS, QUEST, QUESTS`.

## Combat System

Turn-based at the granularity of one `ATTACK` command:

1. The player strikes. Player damage = base **12** (+**5** if the *Iron Sword*
   reward is held) with a small random variance (±3); minimum 1.
2. If the enemy survives, it **immediately counter-attacks** for its `attack`
   stat (±2 variance, minimum 1).
3. `DEFEND` raises a guard that **halves** the next incoming hit (consumed on
   the next enemy strike).
4. `FLEE` ends combat with no strike from either side.

- Players start at **100 HP** (`MaxHP`). `STATUS` reports
  `{"hp","max_hp","status"}` where status is `healthy`, `wounded` (< 50%) or
  `combat`.
- Enemy NPCs have per-type HP/attack (goblin 30/8, bandit 25/6, skeleton 20/5).
- A defeated enemy is removed from the room; combat ends; an `EVT ROOM COMBAT`
  is broadcast and any matching *defeat* quest advances.
- A player reduced to **0 HP respawns** at the world's safe `respawn` room
  with **half max HP**, combat cleared. The death is logged (WARN) and
  broadcast to the room.
- Moving rooms ends the player's combat state.
- `ATTACK` rejects non-hostile NPCs (`405 NPC_NOT_HOSTILE`) and absent NPCs
  (`404 NPC_NOT_FOUND`). `ATTACK` replies with
  `{"attacker_hp","target_hp","damage","status"}`, status ∈
  `combat`/`victory`/`defeated`.

Initiative order: attacker first, defender counters — deterministic and
simple, which keeps a shared multiplayer world predictable.

## Quest System

- `QUEST <npc>` requests a quest from a quest-giver. First request **activates**
  the quest (`status:"active"` with `progress` `x/n`). Re-issuing `QUEST` to the
  same giver is the **turn-in**: if the objective is met, the quest completes,
  the reward item is granted, and `fetch` objective items are consumed.
- **fetch** quests are satisfied by holding the required item(s); progress is
  recomputed from inventory at request/turn-in time.
- **defeat** quests progress automatically when the target enemy is slain
  (anywhere) while the quest is active; an `EVT QUEST OBJECTIVE ... ready to
  turn in` is pushed. The reward is collected by returning to the giver.
- `QUESTS` lists active and completed quests with progress.
- Completion grants the reward into the inventory and pushes
  `EVT QUEST COMPLETE <id>`. Completed quests cannot be re-taken
  (`406 NO_QUEST_AVAILABLE`).

Two quests ship in the world: **fetch_herbs** (merchant → Gold Coin) and
**slay_goblin** (guard → Iron Sword, which boosts attack — a small progression
loop: do the guard's quest to fight more effectively).

## World Design

The world (`data/world.json`) has **10 interconnected rooms** with **multiple
loops** and several branches; a full circuit is possible (no line-only map).
The server validates all exits and references on load and refuses to start on
a broken world.

```
        loc.bakery ── loc.north_gate ── loc.watchtower
            │              │                  │
        loc.square ──── loc.market ────── loc.forest_path
         /     \                                │
  loc.tavern  loc.well                      loc.clearing ──(down)── loc.crypt
  (branch)    (branch)                       (herbs)            (goblin, skeleton)
```

Loops include square→bakery→north_gate→market→square and
market→forest_path→watchtower→north_gate→market. Branches: tavern, well, and
the clearing/crypt descent.

- **NPC roles (≥3):** *dialogue* (baker, barkeep), *quest-giver* (merchant,
  guard), *enemy* (bandit, goblin, skeleton).
- **Items (≥4, ≥2 obtainable):** obtainable — Loaf of Bread, Frothy Ale,
  Healing Herbs, Old Torch; reward-only — Gold Coin, Iron Sword.
- **Items as unique instances:** TAKE removes an item from the room; DROP
  returns it; no duplication; reference by id or display name (multi-word OK).

The JSON layout is our own design (the subject's YAML example is illustrative
only). World data could equally be YAML; JSON was chosen to stay within the
standard library and guarantee a dependency-free build.

## Server Logging

Structured **JSON, one record per line**, written to **stderr** (redirect to a
file as needed). Every record carries an RFC3339Nano `ts`, a `level`
(`INFO`/`WARN`/`ERROR`) and an `event` name, plus structured fields. Logging is
serialised behind a mutex and limited to a single encoder write per record, so
it does not measurably affect responsiveness.

Logged events include:

- Connections/disconnections with IP and timestamp
  (`connection_open`, `player_connected`, `player_disconnected`,
  `connection_close`).
- Every command received, with player and parsed args (`command`).
- Errors sent to clients (`response_error`, WARN).
- World-state changes: `move`, `item_take`, `item_drop`, `combat`,
  `combat_counter`, `combat_victory`, `player_respawn`, group lifecycle.
- Quest progress and completion: `quest_accepted`, `quest_progress`,
  `quest_completed`.
- **Abuse patterns** (WARN): `abuse_command_flood` (> 20 commands/second on one
  connection) and `abuse_rapid_connections` (> 10 connects/10s from one IP).

Inspect logs with e.g. `./bin/tap-server 2>&1 | jq 'select(.level=="WARN")'`.

## Testing

Automated tests (`make test`, or `go test -race ./...`):

- `internal/protocol` — command parsing (case-insensitivity, trailing text)
  and response/error/event formatting.
- `internal/game` — connect + duplicate-name rejection, TAKE by display name
  and non-obtainable/missing handling, MOVE and NO_EXIT, the full fetch-quest
  lifecycle (accept → turn-in → reward → item consumption), and combat hostile
  rules (kill removes the NPC; non-hostile NPCs rejected).

Manual / multiplayer testing:

1. Start the server: `make run-server`.
2. Connect two CLI clients (`make run-cli`) as `alice` and `bob`; verify
   presence events, `CHAT GLOBAL/ROOM/GROUP`, `WHO`, and that one client's
   actions produce events on the other.
3. Open the GUI (`make run-gui`) and confirm the room/inventory/chat views and
   live counters update in real time alongside the CLI clients.
4. Combat: navigate to the crypt and `ATTACK goblin`; check HP changes,
   `DEFEND`/`FLEE`, victory removal, and respawn behaviour.
5. Quests: `QUEST guard` then defeat the goblin and return to turn in; `QUEST
   merchant` after taking the herbs.
6. Robustness: send malformed/unknown commands (expect `400 BAD_REQUEST`),
   commands before `CONNECT` (`202 NOT_CONNECTED`), and kill a client
   mid-session to confirm graceful cleanup and a broadcast LEAVE event.

## Group Contributions

This is a group project (2–3 learners). Suggested division of responsibilities
(fill in real logins/names):

- **omischle** — server core (`internal/game`, `internal/server`,
  `internal/protocol`, logging), CLI client, protocol compliance and tests.
- **<login2>** — GUI client (`cmd/gui` bridge + web UI), world design
  (`data/world.json`), combat/quest tuning.
- **<login3>** — (if applicable) world content, testing, documentation.

> Each member must be able to explain any part of the code during evaluation.

## Resources

Classic references on the topic:

- RFC 2119 — *Key words for use in RFCs to Indicate Requirement Levels*.
- RFC 5234 — *Augmented BNF for Syntax Specifications: ABNF*.
- RFC 793 — *Transmission Control Protocol*; RFC 3629 — *UTF-8*.
- The history of **MUDs** (Multi-User Dungeons) and line-based text protocols.
- Go standard library: `net`, `bufio`, `encoding/json`, `net/http`
  (Server-Sent Events), `embed`.

**How AI was used.** AI assistance was used to help scaffold the project
structure, draft boilerplate (logging, the JSON world loader, the SSE bridge)
and this documentation, and to cross-check the implementation against the RFC
and subject examples. Every generated piece was reviewed, tested (unit tests +
manual multiplayer sessions) and adjusted by the team; we only kept code we
fully understand and can justify during peer evaluation. AI was **not** used to
make design decisions blindly — combat/quest mechanics and the world layout
were decided by the team and then implemented with AI as a drafting aid.
