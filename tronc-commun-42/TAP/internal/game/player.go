package game

// MaxHP is the health every player starts with (mandatory: 100 HP).
const MaxHP = 100

// QuestStatus is the lifecycle state of a quest for a given player.
type QuestStatus string

const (
	QuestActive    QuestStatus = "active"
	QuestCompleted QuestStatus = "completed"
)

// QuestState tracks one player's progress on one quest.
type QuestState struct {
	ID       string      `json:"quest_id"`
	Status   QuestStatus `json:"status"`
	Progress int         `json:"-"`
	Need     int         `json:"-"`
}

// Player is a connected, authenticated client.
type Player struct {
	Name string
	IP   string

	out chan string // buffered outbound lines (without trailing newline)

	Room      string   // current room id
	Inventory []string // item ids held
	HP        int
	MaxHP     int

	InCombat  string // npc id currently fighting in this room, "" if none
	defending bool   // DEFEND raised guard for the next incoming hit

	Group string // group id, "" if none

	Quests map[string]*QuestState
}

func newPlayer(name, ip, startRoom string, bufSize int) *Player {
	return &Player{
		Name:      name,
		IP:        ip,
		out:       make(chan string, bufSize),
		Room:      startRoom,
		Inventory: []string{},
		HP:        MaxHP,
		MaxHP:     MaxHP,
		Quests:    map[string]*QuestState{},
	}
}

// Out exposes the outbound channel so the server's writer goroutine can
// drain it. The channel is closed by the game when the player disconnects.
func (p *Player) Out() <-chan string { return p.out }

// Send queues a line for delivery to this player. It never blocks: if the
// client's buffer is full (slow or disconnecting client) the message is
// dropped so that a broadcast is never interrupted by one bad client.
func (p *Player) Send(line string) {
	select {
	case p.out <- line:
	default:
	}
}

func (p *Player) hasItem(id string) bool {
	for _, it := range p.Inventory {
		if it == id {
			return true
		}
	}
	return false
}

func (p *Player) removeItem(id string) bool {
	for i, it := range p.Inventory {
		if it == id {
			p.Inventory = append(p.Inventory[:i], p.Inventory[i+1:]...)
			return true
		}
	}
	return false
}
