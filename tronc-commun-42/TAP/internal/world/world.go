// Package world loads and validates the static game world from a JSON file.
//
// The world describes rooms (with exits, initial items and NPC placements),
// item definitions, NPC definitions and quest definitions. Loading performs
// referential-integrity validation so the server fails fast on a broken
// world rather than misbehaving at runtime.
package world

import (
	"encoding/json"
	"fmt"
	"os"
)

// Room is a discrete location in the world.
type Room struct {
	Name        string            `json:"name"`
	Description string            `json:"description"`
	Exits       map[string]string `json:"exits"` // direction -> destination room id
	Items       []string          `json:"items"` // item ids present at startup
	NPCs        []string          `json:"npcs"`  // npc ids present at startup
}

// Item is an item definition.
type Item struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Obtainable  bool   `json:"obtainable"`
}

// NPC is a non-player-character definition.
type NPC struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Role        string   `json:"role"` // "dialogue", "quest-giver" or "enemy"
	Dialogue    []string `json:"dialogue"`
	HP          int      `json:"hp"`
	Attack      int      `json:"attack"`
	Hostile     bool     `json:"hostile"`
}

// Quest is a quest definition.
type Quest struct {
	Giver       string `json:"giver"` // npc id that issues the quest
	Description string `json:"description"`
	Type        string `json:"type"`   // "fetch" or "defeat"
	Target      string `json:"target"` // item id (fetch) or npc id (defeat)
	Count       int    `json:"count"`  // objective count
	Reward      string `json:"reward"` // item id granted on completion
}

// World is the fully-loaded, validated game world.
type World struct {
	Start   string            `json:"start"`
	Respawn string            `json:"respawn"`
	Rooms   map[string]*Room  `json:"rooms"`
	Items   map[string]*Item  `json:"items"`
	NPCs    map[string]*NPC   `json:"npcs"`
	Quests  map[string]*Quest `json:"quests"`
}

// Load reads and validates a world from the JSON file at path.
func Load(path string) (*World, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read world file: %w", err)
	}
	var w World
	if err := json.Unmarshal(data, &w); err != nil {
		return nil, fmt.Errorf("parse world JSON: %w", err)
	}
	if err := w.validate(); err != nil {
		return nil, fmt.Errorf("invalid world: %w", err)
	}
	return &w, nil
}

// validate checks referential integrity of the loaded world.
func (w *World) validate() error {
	if w.Start == "" {
		return fmt.Errorf("missing start room")
	}
	if w.Respawn == "" {
		w.Respawn = w.Start
	}
	if _, ok := w.Rooms[w.Start]; !ok {
		return fmt.Errorf("start room %q does not exist", w.Start)
	}
	if _, ok := w.Rooms[w.Respawn]; !ok {
		return fmt.Errorf("respawn room %q does not exist", w.Respawn)
	}

	for id, r := range w.Rooms {
		for dir, dest := range r.Exits {
			if _, ok := w.Rooms[dest]; !ok {
				return fmt.Errorf("room %q exit %q points to unknown room %q", id, dir, dest)
			}
		}
		for _, it := range r.Items {
			if _, ok := w.Items[it]; !ok {
				return fmt.Errorf("room %q references unknown item %q", id, it)
			}
		}
		for _, n := range r.NPCs {
			if _, ok := w.NPCs[n]; !ok {
				return fmt.Errorf("room %q references unknown npc %q", id, n)
			}
		}
	}

	for id, q := range w.Quests {
		if _, ok := w.NPCs[q.Giver]; !ok {
			return fmt.Errorf("quest %q has unknown giver %q", id, q.Giver)
		}
		switch q.Type {
		case "fetch":
			if _, ok := w.Items[q.Target]; !ok {
				return fmt.Errorf("fetch quest %q targets unknown item %q", id, q.Target)
			}
		case "defeat":
			if _, ok := w.NPCs[q.Target]; !ok {
				return fmt.Errorf("defeat quest %q targets unknown npc %q", id, q.Target)
			}
		default:
			return fmt.Errorf("quest %q has unknown type %q", id, q.Type)
		}
		if q.Reward != "" {
			if _, ok := w.Items[q.Reward]; !ok {
				return fmt.Errorf("quest %q grants unknown reward item %q", id, q.Reward)
			}
		}
		if q.Count < 1 {
			q.Count = 1
		}
	}
	return nil
}
