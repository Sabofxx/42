package game

import (
	"encoding/json"

	"tap/internal/logging"
	"tap/internal/protocol"
)

// Quest model (design choice, documented in README):
//
//   - QUEST <npc> requests a quest from a quest-giver NPC. If the player has
//     no record of that NPC's quest, it becomes "active". If the quest is
//     already active, the giver re-evaluates the objective and, when met,
//     completes it and grants the reward (turn-in by talking to the giver).
//   - "fetch" quests are satisfied by holding the required item(s).
//   - "defeat" quests progress automatically when the target enemy is slain
//     anywhere in the world (see onEnemyDefeated) and are turned in at the giver.
//   - QUESTS lists the player's active and completed quests with progress.

type questJSON struct {
	QuestID     string `json:"quest_id"`
	Description string `json:"description,omitempty"`
	Reward      string `json:"reward,omitempty"`
	Status      string `json:"status"`
	Progress    string `json:"progress,omitempty"`
}

// questByGiver returns the quest id whose giver is the given npc id.
func (g *Game) questByGiver(npcID string) (string, bool) {
	for qid, q := range g.w.Quests {
		if q.Giver == npcID {
			return qid, true
		}
	}
	return "", false
}

// requestQuestLocked handles QUEST <npc>. Caller holds g.mu.
func (g *Game) requestQuestLocked(p *Player, input string) string {
	inst, ok := g.resolveNPC(p.Room, input)
	if !ok {
		return protocol.Err(protocol.ErrNPCNotFound, "NPC_NOT_FOUND")
	}
	qid, ok := g.questByGiver(inst.id)
	if !ok {
		return protocol.Err(protocol.ErrNoQuestAvailable, "NO_QUEST_AVAILABLE")
	}
	q := g.w.Quests[qid]
	st := p.Quests[qid]

	// Already completed: nothing more to give.
	if st != nil && st.Status == QuestCompleted {
		return protocol.Err(protocol.ErrNoQuestAvailable, "NO_QUEST_AVAILABLE")
	}

	// First time: offer and activate the quest.
	if st == nil {
		st = &QuestState{ID: qid, Status: QuestActive, Need: q.Count}
		if q.Type == "fetch" {
			st.Progress = g.countItem(p, q.Target)
		}
		p.Quests[qid] = st
		g.log.Info("quest_accepted", logging.Fields{"player": p.Name, "quest": qid})
		return protocol.OK(mustJSON(questJSON{
			QuestID: qid, Description: q.Description, Reward: q.Reward,
			Status: "active", Progress: progressStr(st),
		}))
	}

	// Active: re-evaluate the objective for turn-in.
	if q.Type == "fetch" {
		st.Progress = g.countItem(p, q.Target)
	}
	if st.Progress >= st.Need {
		g.completeQuestLocked(p, qid)
		return protocol.OK(mustJSON(questJSON{
			QuestID: qid, Reward: q.Reward, Status: "completed",
		}))
	}
	return protocol.OK(mustJSON(questJSON{
		QuestID: qid, Description: q.Description, Status: "active", Progress: progressStr(st),
	}))
}

func (g *Game) completeQuestLocked(p *Player, qid string) {
	q := g.w.Quests[qid]
	st := p.Quests[qid]
	st.Status = QuestCompleted
	st.Progress = st.Need

	// Fetch quests consume the delivered items.
	if q.Type == "fetch" {
		for i := 0; i < q.Count; i++ {
			p.removeItem(q.Target)
		}
	}
	// Grant the reward into the player's inventory.
	if q.Reward != "" {
		p.Inventory = append(p.Inventory, q.Reward)
	}
	g.log.Info("quest_completed", logging.Fields{"player": p.Name, "quest": qid, "reward": q.Reward})
	p.Send(protocol.Event("QUEST COMPLETE", qid))
}

// onEnemyDefeated advances any active "defeat" quests targeting npcID.
func (g *Game) onEnemyDefeated(p *Player, npcID string) {
	for qid, q := range g.w.Quests {
		if q.Type != "defeat" || q.Target != npcID {
			continue
		}
		st := p.Quests[qid]
		if st == nil || st.Status == QuestCompleted {
			continue
		}
		st.Progress++
		g.log.Info("quest_progress", logging.Fields{
			"player": p.Name, "quest": qid, "progress": st.Progress, "need": st.Need,
		})
		if st.Progress >= st.Need {
			// Objective met; reward is collected by returning to the giver.
			p.Send(protocol.Event("QUEST OBJECTIVE", qid+" ready to turn in"))
		}
	}
}

func (g *Game) listQuestsLocked(p *Player) string {
	out := []questJSON{}
	for qid, st := range p.Quests {
		out = append(out, questJSON{
			QuestID: qid, Status: string(st.Status), Progress: progressStr(st),
		})
	}
	b, _ := json.Marshal(out)
	return protocol.OK(string(b))
}

func (g *Game) countItem(p *Player, id string) int {
	n := 0
	for _, it := range p.Inventory {
		if it == id {
			n++
		}
	}
	return n
}

func progressStr(st *QuestState) string {
	return itoa(st.Progress) + "/" + itoa(st.Need)
}
