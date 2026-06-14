package game

import (
	"encoding/json"

	"tap/internal/logging"
	"tap/internal/protocol"
)

// Combat model (design choice, documented in README):
//
//   - Combat is turn-based at the granularity of one ATTACK command: the
//     player strikes, and if the enemy survives it immediately counter-attacks.
//   - Player base damage is 12 (+5 with the Iron Sword reward) with a small
//     random variance. Enemy damage is the NPC's "attack" stat with variance.
//   - DEFEND halves the next incoming hit. FLEE ends combat without a strike.
//   - A defeated enemy is removed from the room. A player reduced to 0 HP
//     respawns at the world's safe respawn room with half max HP.
const (
	playerBaseAttack = 12
	swordBonus       = 5
)

func (g *Game) playerAttackPower(p *Player) int {
	power := playerBaseAttack
	if p.hasItem("item.iron_sword") {
		power += swordBonus
	}
	return power + g.rng.Intn(7) - 3 // +- 3 variance
}

type attackResult struct {
	AttackerHP int    `json:"attacker_hp"`
	TargetHP   int    `json:"target_hp"`
	Damage     int    `json:"damage"`
	Status     string `json:"status"`
}

// attackLocked resolves one round of combat between p and the NPC instance
// matching input in p's current room. Caller holds g.mu.
func (g *Game) attackLocked(p *Player, input string) string {
	inst, ok := g.resolveNPC(p.Room, input)
	if !ok {
		return protocol.Err(protocol.ErrNPCNotFound, "NPC_NOT_FOUND")
	}
	def := g.w.NPCs[inst.id]
	if !def.Hostile {
		return protocol.Err(protocol.ErrNPCNotHostile, "NPC_NOT_HOSTILE")
	}

	p.InCombat = inst.id

	// Player strikes.
	dmg := g.playerAttackPower(p)
	if dmg < 1 {
		dmg = 1
	}
	inst.hp -= dmg
	if inst.hp < 0 {
		inst.hp = 0
	}

	g.log.Info("combat", logging.Fields{
		"player": p.Name, "target": inst.id, "damage": dmg,
		"target_hp": inst.hp, "attacker_hp": p.HP, "room": p.Room,
	})

	if inst.hp == 0 {
		// Enemy defeated: remove from room, end combat, advance quests.
		delete(g.roomNPCs[p.Room], inst.id)
		p.InCombat = ""
		p.defending = false
		g.broadcastRoom(p.Room, p.Name, protocol.Event("ROOM COMBAT",
			p.Name+" defeated "+def.Name))
		g.log.Info("combat_victory", logging.Fields{"player": p.Name, "target": inst.id, "room": p.Room})
		g.onEnemyDefeated(p, inst.id)
		return protocol.OK(mustJSON(attackResult{
			AttackerHP: p.HP, TargetHP: 0, Damage: dmg, Status: "victory",
		}))
	}

	// Enemy counter-attacks.
	counter := def.Attack + g.rng.Intn(5) - 2 // +- 2 variance
	if counter < 1 {
		counter = 1
	}
	if p.defending {
		counter = (counter + 1) / 2
		p.defending = false
	}
	p.HP -= counter
	g.log.Info("combat_counter", logging.Fields{
		"player": p.Name, "attacker": inst.id, "damage": counter, "player_hp": p.HP,
	})

	if p.HP <= 0 {
		g.respawnLocked(p)
		g.broadcastRoom(p.Room, p.Name, protocol.Event("ROOM COMBAT",
			p.Name+" was defeated and fled to safety"))
		return protocol.OK(mustJSON(attackResult{
			AttackerHP: p.HP, TargetHP: inst.hp, Damage: dmg, Status: "defeated",
		}))
	}

	return protocol.OK(mustJSON(attackResult{
		AttackerHP: p.HP, TargetHP: inst.hp, Damage: dmg, Status: "combat",
	}))
}

func (g *Game) respawnLocked(p *Player) {
	old := p.Room
	p.HP = p.MaxHP / 2
	p.InCombat = ""
	p.defending = false
	p.Room = g.w.Respawn
	g.log.Warn("player_respawn", logging.Fields{"player": p.Name, "from": old, "to": p.Room, "hp": p.HP})
	if old != p.Room {
		g.broadcastRoom(old, p.Name, protocol.Event("ROOM PRESENCE LEAVE", p.Name))
		g.broadcastRoom(p.Room, p.Name, protocol.Event("ROOM PRESENCE ENTER", p.Name))
	}
}

func (g *Game) defendLocked(p *Player) string {
	if p.InCombat == "" {
		return protocol.Err(protocol.ErrNotInCombat, "NOT_IN_COMBAT")
	}
	p.defending = true
	return protocol.OK(`{"status": "defending"}`)
}

func (g *Game) fleeLocked(p *Player) string {
	if p.InCombat == "" {
		return protocol.Err(protocol.ErrNotInCombat, "NOT_IN_COMBAT")
	}
	p.InCombat = ""
	p.defending = false
	g.log.Info("combat_flee", logging.Fields{"player": p.Name, "room": p.Room})
	return protocol.OK(`{"status": "fled"}`)
}

type statusJSON struct {
	HP     int    `json:"hp"`
	MaxHP  int    `json:"max_hp"`
	Status string `json:"status"`
}

func (g *Game) statusLocked(p *Player) string {
	st := "healthy"
	switch {
	case p.InCombat != "":
		st = "combat"
	case p.HP < p.MaxHP/2:
		st = "wounded"
	}
	return protocol.OK(mustJSON(statusJSON{HP: p.HP, MaxHP: p.MaxHP, Status: st}))
}

func mustJSON(v interface{}) string {
	b, _ := json.Marshal(v)
	return string(b)
}
