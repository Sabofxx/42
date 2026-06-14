package game

import (
	"strings"

	"tap/internal/logging"
	"tap/internal/protocol"
)

// Handle dispatches a single authenticated command for player p and returns
// the reply line to send back to that client. The boolean result is true when
// the connection should be closed afterwards (QUIT). All world mutations and
// broadcasts happen under g.mu.
func (g *Game) Handle(p *Player, cmd protocol.Command) (reply string, quit bool) {
	g.mu.Lock()
	defer g.mu.Unlock()

	g.log.Info("command", logging.Fields{
		"player": p.Name, "command": cmd.Name, "args": cmd.Args,
	})

	switch cmd.Name {
	case "LOOK":
		reply = protocol.OK(g.lookLocked(p))

	case "MOVE":
		reply = g.moveLocked(p, cmd.Rest(0))

	case "CHAT":
		reply = g.chatLocked(p, cmd)

	case "WHO":
		reply = g.whoLocked(p)

	case "TAKE":
		reply = g.takeLocked(p, cmd.Rest(0))

	case "DROP":
		reply = g.dropLocked(p, cmd.Rest(0))

	case "INVENTORY":
		reply = g.inventoryLocked(p)

	case "TALK":
		reply = g.talkLocked(p, cmd.Rest(0))

	case "ATTACK":
		reply = g.attackLocked(p, cmd.Rest(0))

	case "DEFEND":
		reply = g.defendLocked(p)

	case "FLEE":
		reply = g.fleeLocked(p)

	case "STATUS":
		reply = g.statusLocked(p)

	case "QUEST":
		reply = g.requestQuestLocked(p, cmd.Rest(0))

	case "QUESTS":
		reply = g.listQuestsLocked(p)

	case "GROUP":
		reply = g.groupLocked(p, cmd)

	case "QUIT":
		reply, quit = protocol.OK("bye"), true

	case "CONNECT":
		reply = protocol.Err(protocol.ErrAlreadyConn, "ALREADY_CONNECTED")

	case "":
		reply = protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")

	default:
		reply = protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")
	}

	if strings.HasPrefix(reply, "ERR") {
		g.log.Warn("response_error", logging.Fields{"player": p.Name, "command": cmd.Name, "reply": reply})
	}
	return reply, quit
}

func (g *Game) moveLocked(p *Player, dir string) string {
	dir = strings.ToLower(strings.TrimSpace(dir))
	r := g.w.Rooms[p.Room]
	dest, ok := r.Exits[dir]
	if !ok {
		return protocol.Err(protocol.ErrNoExit, "NO_EXIT")
	}
	old := p.Room
	p.Room = dest
	p.InCombat = "" // moving rooms breaks combat
	p.defending = false
	g.broadcastRoom(old, p.Name, protocol.Event("ROOM PRESENCE LEAVE", p.Name))
	g.broadcastRoom(dest, p.Name, protocol.Event("ROOM PRESENCE ENTER", p.Name))
	g.log.Info("move", logging.Fields{"player": p.Name, "from": old, "to": dest, "dir": dir})
	return protocol.OK("room=" + dest)
}

func (g *Game) chatLocked(p *Player, cmd protocol.Command) string {
	if len(cmd.Args) < 1 {
		return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
	}
	scope := strings.ToUpper(cmd.Args[0])
	msg := cmd.Rest(1)
	switch scope {
	case "GLOBAL":
		g.broadcastGlobal(protocol.Event("GLOBAL CHAT", p.Name+" "+msg))
	case "ROOM":
		// Sender sees room chat reflected too (broadcast to everyone in room).
		g.broadcastRoom(p.Room, "", protocol.Event("ROOM CHAT", p.Name+" "+msg))
	case "GROUP":
		if p.Group == "" {
			return protocol.Err(protocol.ErrNotInGroup, "NOT_IN_GROUP")
		}
		g.broadcastGroup(p.Group, "", protocol.Event("GROUP CHAT", p.Name+" "+msg))
	default:
		return protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")
	}
	g.log.Info("chat", logging.Fields{"player": p.Name, "scope": scope, "message": msg})
	return protocol.OK("")
}

type whoJSON = struct {
	Room   []string `json:"room"`
	Server int      `json:"server"`
}

func (g *Game) whoLocked(p *Player) string {
	room := []string{}
	for name, other := range g.players {
		if other.Room == p.Room {
			room = append(room, name)
		}
	}
	return protocol.OK(mustJSON(whoJSON{Room: room, Server: len(g.players)}))
}

func (g *Game) takeLocked(p *Player, input string) string {
	if input == "" {
		return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
	}
	id, ok := g.resolveRoomItem(p.Room, input)
	if !ok {
		return protocol.Err(protocol.ErrItemNotFound, "ITEM_NOT_FOUND")
	}
	if !g.w.Items[id].Obtainable {
		return protocol.Err(protocol.ErrItemNotFound, "ITEM_NOT_FOUND")
	}
	// Remove one instance from the room floor.
	floor := g.roomItems[p.Room]
	for i, it := range floor {
		if it == id {
			g.roomItems[p.Room] = append(floor[:i], floor[i+1:]...)
			break
		}
	}
	p.Inventory = append(p.Inventory, id)
	g.broadcastRoom(p.Room, p.Name, protocol.Event("ROOM ITEM", p.Name+" took "+id))
	g.log.Info("item_take", logging.Fields{"player": p.Name, "item": id, "room": p.Room})
	return protocol.OK("taken=" + id)
}

func (g *Game) dropLocked(p *Player, input string) string {
	if input == "" {
		return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
	}
	id, ok := g.resolveInventoryItem(p, input)
	if !ok {
		return protocol.Err(protocol.ErrItemNotInInv, "ITEM_NOT_IN_INVENTORY")
	}
	p.removeItem(id)
	g.roomItems[p.Room] = append(g.roomItems[p.Room], id)
	g.broadcastRoom(p.Room, p.Name, protocol.Event("ROOM ITEM", p.Name+" dropped "+id))
	g.log.Info("item_drop", logging.Fields{"player": p.Name, "item": id, "room": p.Room})
	return protocol.OK("dropped=" + id)
}

func (g *Game) inventoryLocked(p *Player) string {
	return protocol.OK(mustJSON(p.Inventory))
}

type talkJSON struct {
	NPC      string `json:"npc"`
	Dialogue string `json:"dialogue"`
}

func (g *Game) talkLocked(p *Player, input string) string {
	if input == "" {
		return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
	}
	inst, ok := g.resolveNPC(p.Room, input)
	if !ok {
		return protocol.Err(protocol.ErrNPCNotFound, "NPC_NOT_FOUND")
	}
	def := g.w.NPCs[inst.id]
	line := ""
	if len(def.Dialogue) > 0 {
		line = def.Dialogue[g.rng.Intn(len(def.Dialogue))]
	}
	g.log.Info("talk", logging.Fields{"player": p.Name, "npc": inst.id})
	return protocol.OK(mustJSON(talkJSON{NPC: inst.id, Dialogue: line}))
}

func (g *Game) groupLocked(p *Player, cmd protocol.Command) string {
	if len(cmd.Args) < 1 {
		return protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")
	}
	switch strings.ToUpper(cmd.Args[0]) {
	case "CREATE":
		return g.groupCreateLocked(p)
	case "INVITE":
		if len(cmd.Args) < 2 {
			return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
		}
		return g.groupInviteLocked(p, cmd.Args[1])
	case "JOIN":
		if len(cmd.Args) < 2 {
			return protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")
		}
		return g.groupJoinLocked(p, cmd.Args[1])
	case "LEAVE":
		return g.groupLeaveLocked(p)
	default:
		return protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")
	}
}
