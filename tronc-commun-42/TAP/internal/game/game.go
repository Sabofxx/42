// Package game holds the authoritative, in-memory game state and all the
// rules of RFC 42TAP: rooms and presence, items, NPC dialogue, combat,
// quests, chat and groups.
//
// Concurrency model: a single mutex guards all mutable state. Every client
// connection is handled by its own goroutine in the server package; those
// goroutines call into Game, which serialises all mutations under g.mu.
// Outbound delivery is decoupled via each Player's buffered channel, so
// broadcasts performed while holding the lock never block on a slow client.
package game

import (
	"encoding/json"
	"math/rand"
	"sort"
	"strings"
	"sync"
	"time"

	"tap/internal/logging"
	"tap/internal/protocol"
	"tap/internal/world"
)

// outboundBuffer is the per-player outbound queue depth.
const outboundBuffer = 256

// npcInstance is the live combat state of an NPC placed in a room.
type npcInstance struct {
	id string // npc template id
	hp int
}

type group struct {
	id      string
	members map[string]bool
}

// Game is the authoritative world state.
type Game struct {
	mu  sync.Mutex
	w   *world.World
	log *logging.Logger
	rng *rand.Rand

	players   map[string]*Player                 // by username
	roomItems map[string][]string                // room id -> item ids on the floor
	roomNPCs  map[string]map[string]*npcInstance // room id -> npc id -> instance
	groups    map[string]*group
	nextGroup int
}

// New builds a Game from a validated world, seeding runtime state (room
// item placement and NPC instances) from the world definition.
func New(w *world.World, log *logging.Logger) *Game {
	g := &Game{
		w:         w,
		log:       log,
		rng:       rand.New(rand.NewSource(time.Now().UnixNano())),
		players:   map[string]*Player{},
		roomItems: map[string][]string{},
		roomNPCs:  map[string]map[string]*npcInstance{},
		groups:    map[string]*group{},
	}
	for id, r := range w.Rooms {
		items := make([]string, len(r.Items))
		copy(items, r.Items)
		g.roomItems[id] = items

		npcs := map[string]*npcInstance{}
		for _, nid := range r.NPCs {
			npcs[nid] = &npcInstance{id: nid, hp: w.NPCs[nid].HP}
		}
		g.roomNPCs[id] = npcs
	}
	return g
}

// ---- connection lifecycle ----

// Connect registers a new authenticated player. It returns the player and an
// empty error string on success, or a protocol error line on failure.
func (g *Game) Connect(name, ip string) (*Player, string) {
	g.mu.Lock()
	defer g.mu.Unlock()

	if _, exists := g.players[name]; exists {
		g.log.Warn("connect_rejected", logging.Fields{"player": name, "ip": ip, "reason": "NAME_IN_USE"})
		return nil, protocol.Err(protocol.ErrNameInUse, "NAME_IN_USE")
	}
	p := newPlayer(name, ip, g.w.Start, outboundBuffer)
	g.players[name] = p
	g.log.Info("player_connected", logging.Fields{"player": name, "ip": ip, "room": p.Room})

	// Announce presence to others already in the start room.
	g.broadcastRoom(p.Room, name, protocol.Event("ROOM PRESENCE ENTER", name))
	g.broadcastStatsLocked()
	return p, ""
}

// Disconnect removes a player and broadcasts their departure. It is safe to
// call for an abrupt drop; player state is removed before the LEAVE event is
// broadcast (global rule: clean up before broadcasting leave events).
func (g *Game) Disconnect(p *Player) {
	g.mu.Lock()
	defer g.mu.Unlock()
	if _, ok := g.players[p.Name]; !ok {
		return
	}

	room := p.Room
	// Drop held items back into the current room so they are not lost.
	for _, it := range p.Inventory {
		g.roomItems[room] = append(g.roomItems[room], it)
	}
	p.Inventory = nil
	g.leaveGroupLocked(p)
	delete(g.players, p.Name)
	close(p.out)

	g.log.Info("player_disconnected", logging.Fields{"player": p.Name, "ip": p.IP, "room": room})
	g.broadcastRoom(room, p.Name, protocol.Event("ROOM PRESENCE LEAVE", p.Name))
	g.broadcastStatsLocked()
}

// ---- broadcast helpers (caller must hold g.mu) ----

func (g *Game) broadcastRoom(roomID, except, line string) {
	for _, p := range g.players {
		if p.Room == roomID && p.Name != except {
			p.Send(line)
		}
	}
}

func (g *Game) broadcastGlobal(line string) {
	for _, p := range g.players {
		p.Send(line)
	}
}

func (g *Game) broadcastGroup(groupID, except, line string) {
	grp := g.groups[groupID]
	if grp == nil {
		return
	}
	for name := range grp.members {
		if name == except {
			continue
		}
		if p := g.players[name]; p != nil {
			p.Send(line)
		}
	}
}

func (g *Game) broadcastStatsLocked() {
	line := protocol.Event("STATS PLAYERS", "players="+itoa(len(g.players)))
	g.broadcastGlobal(line)
}

// ---- resolution helpers ----

// matchToken reports whether user input refers to a resource identified by
// id with display name name. Matching is case-insensitive and accepts the
// canonical id, the display name, or the id suffix after the dot (RFC 8.3).
func matchToken(input, id, name string) bool {
	in := strings.ToLower(strings.TrimSpace(input))
	if in == "" {
		return false
	}
	if in == strings.ToLower(id) || in == strings.ToLower(name) {
		return true
	}
	if dot := strings.IndexByte(id, '.'); dot >= 0 {
		if in == strings.ToLower(id[dot+1:]) {
			return true
		}
	}
	return false
}

// resolveRoomItem finds an item id currently on the floor of roomID matching
// input. Returns ("", false) if none.
func (g *Game) resolveRoomItem(roomID, input string) (string, bool) {
	for _, it := range g.roomItems[roomID] {
		if matchToken(input, it, g.w.Items[it].Name) {
			return it, true
		}
	}
	return "", false
}

func (g *Game) resolveInventoryItem(p *Player, input string) (string, bool) {
	for _, it := range p.Inventory {
		if matchToken(input, it, g.w.Items[it].Name) {
			return it, true
		}
	}
	return "", false
}

func (g *Game) resolveNPC(roomID, input string) (*npcInstance, bool) {
	for _, inst := range g.roomNPCs[roomID] {
		if matchToken(input, inst.id, g.w.NPCs[inst.id].Name) {
			return inst, true
		}
	}
	return nil, false
}

// ---- LOOK JSON ----

type roomJSON struct {
	ID          string            `json:"id"`
	Name        string            `json:"name"`
	Description string            `json:"description"`
	Exits       map[string]string `json:"exits"`
}

type lookJSON struct {
	Room    roomJSON `json:"room"`
	Players []string `json:"players"`
	Items   []string `json:"items"`
	NPCs    []string `json:"npcs"`
}

// lookLocked renders the current room state for p as the LOOK JSON payload.
func (g *Game) lookLocked(p *Player) string {
	r := g.w.Rooms[p.Room]

	players := []string{}
	for name, other := range g.players {
		if other.Room == p.Room {
			players = append(players, name)
		}
	}
	sort.Strings(players)

	items := []string{}
	items = append(items, g.roomItems[p.Room]...)
	sort.Strings(items)

	npcs := []string{}
	for nid := range g.roomNPCs[p.Room] {
		npcs = append(npcs, nid)
	}
	sort.Strings(npcs)

	payload := lookJSON{
		Room:    roomJSON{ID: p.Room, Name: r.Name, Description: r.Description, Exits: r.Exits},
		Players: players,
		Items:   items,
		NPCs:    npcs,
	}
	b, _ := json.Marshal(payload)
	return string(b)
}

func itoa(n int) string {
	if n == 0 {
		return "0"
	}
	neg := n < 0
	if neg {
		n = -n
	}
	var buf [20]byte
	i := len(buf)
	for n > 0 {
		i--
		buf[i] = byte('0' + n%10)
		n /= 10
	}
	if neg {
		i--
		buf[i] = '-'
	}
	return string(buf[i:])
}
