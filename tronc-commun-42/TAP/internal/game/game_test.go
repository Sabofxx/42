package game

import (
	"io"
	"strings"
	"testing"

	"tap/internal/logging"
	"tap/internal/protocol"
	"tap/internal/world"
)

// newTestGame builds a small but valid world entirely in memory.
func newTestGame(t *testing.T) *Game {
	t.Helper()
	w := &world.World{
		Start:   "loc.a",
		Respawn: "loc.a",
		Rooms: map[string]*world.Room{
			"loc.a": {Name: "Alpha", Exits: map[string]string{"north": "loc.b"}, Items: []string{"item.key"}, NPCs: []string{"npc.merchant"}},
			"loc.b": {Name: "Beta", Exits: map[string]string{"south": "loc.a"}, NPCs: []string{"npc.rat"}},
		},
		Items: map[string]*world.Item{
			"item.key":  {Name: "Brass Key", Obtainable: true},
			"item.coin": {Name: "Gold Coin", Obtainable: false},
		},
		NPCs: map[string]*world.NPC{
			"npc.merchant": {Name: "Merchant", Role: "quest-giver", Dialogue: []string{"hi"}, HP: 10},
			"npc.rat":      {Name: "Giant Rat", Role: "enemy", HP: 1, Attack: 1, Hostile: true},
		},
		Quests: map[string]*world.Quest{
			"get_key": {Giver: "npc.merchant", Type: "fetch", Target: "item.key", Count: 1, Reward: "item.coin"},
		},
	}
	return New(w, logging.New(io.Discard))
}

func handle(g *Game, p *Player, line string) string {
	reply, _ := g.Handle(p, protocol.ParseCommand(line))
	return reply
}

func TestConnectAndDuplicate(t *testing.T) {
	g := newTestGame(t)
	p, errLine := g.Connect("alice", "1.2.3.4")
	if p == nil {
		t.Fatalf("connect failed: %s", errLine)
	}
	if _, e := g.Connect("alice", "1.2.3.4"); e != protocol.Err(protocol.ErrNameInUse, "NAME_IN_USE") {
		t.Fatalf("duplicate name not rejected: %q", e)
	}
}

func TestTakeNonObtainableAndMissing(t *testing.T) {
	g := newTestGame(t)
	p, _ := g.Connect("alice", "ip")
	if r := handle(g, p, "TAKE Brass Key"); r != "OK taken=item.key" {
		t.Fatalf("TAKE by display name: %q", r)
	}
	if r := handle(g, p, "TAKE key"); !strings.HasPrefix(r, "ERR 404") {
		t.Fatalf("TAKE already-taken should 404: %q", r)
	}
	if !p.hasItem("item.key") {
		t.Fatal("item.key not in inventory")
	}
}

func TestMoveAndNoExit(t *testing.T) {
	g := newTestGame(t)
	p, _ := g.Connect("alice", "ip")
	if r := handle(g, p, "MOVE north"); r != "OK room=loc.b" {
		t.Fatalf("MOVE north: %q", r)
	}
	if r := handle(g, p, "MOVE north"); r != protocol.Err(protocol.ErrNoExit, "NO_EXIT") {
		t.Fatalf("MOVE into wall: %q", r)
	}
}

func TestFetchQuestLifecycle(t *testing.T) {
	g := newTestGame(t)
	p, _ := g.Connect("alice", "ip")
	handle(g, p, "TAKE key") // obtain the objective item first

	if r := handle(g, p, "QUEST merchant"); !strings.Contains(r, `"status":"active"`) {
		t.Fatalf("accept quest: %q", r)
	}
	if r := handle(g, p, "QUEST merchant"); !strings.Contains(r, `"status":"completed"`) {
		t.Fatalf("turn in quest: %q", r)
	}
	if !p.hasItem("item.coin") {
		t.Fatal("reward item.coin not granted")
	}
	if p.hasItem("item.key") {
		t.Fatal("fetch item.key should have been consumed on turn-in")
	}
}

func TestCombatHostileRules(t *testing.T) {
	g := newTestGame(t)
	p, _ := g.Connect("alice", "ip")
	handle(g, p, "MOVE north") // to loc.b with the rat (1 HP)
	r := handle(g, p, "ATTACK rat")
	if !strings.Contains(r, `"status":"victory"`) {
		t.Fatalf("rat should die in one hit: %q", r)
	}
	// NPC removed from the room afterwards.
	if r := handle(g, p, "ATTACK rat"); r != protocol.Err(protocol.ErrNPCNotFound, "NPC_NOT_FOUND") {
		t.Fatalf("rat should be gone: %q", r)
	}
	// Non-hostile NPC cannot be attacked.
	handle(g, p, "MOVE south")
	if r := handle(g, p, "ATTACK merchant"); r != protocol.Err(protocol.ErrNPCNotHostile, "NPC_NOT_HOSTILE") {
		t.Fatalf("merchant not hostile: %q", r)
	}
}
