// Command server starts the TAP MUD server.
//
// Usage:
//   server [-addr host:port] [-world path/to/world.json]
package main

import (
	"flag"
	"os"

	"tap/internal/game"
	"tap/internal/logging"
	"tap/internal/server"
	"tap/internal/world"
)

func main() {
	addr := flag.String("addr", ":4242", "TCP address to listen on")
	worldPath := flag.String("world", "data/world.json", "path to the world JSON file")
	flag.Parse()

	// Structured JSON logs go to stderr so gameplay output streams stay clean.
	log := logging.New(os.Stderr)

	w, err := world.Load(*worldPath)
	if err != nil {
		log.Error("world_load_failed", logging.Fields{"path": *worldPath, "error": err.Error()})
		os.Exit(1)
	}
	log.Info("world_loaded", logging.Fields{
		"path": *worldPath, "rooms": len(w.Rooms), "items": len(w.Items),
		"npcs": len(w.NPCs), "quests": len(w.Quests),
	})

	g := game.New(w, log)
	srv := server.New(g, log)
	if err := srv.ListenAndServe(*addr); err != nil {
		log.Error("server_failed", logging.Fields{"error": err.Error()})
		os.Exit(1)
	}
}
