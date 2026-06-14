// Package server implements the TAP TCP server: connection acceptance,
// per-connection framing, authentication, command dispatch and abuse
// monitoring. Each connection is served by its own goroutine, with a second
// writer goroutine per player draining its outbound channel.
package server

import (
	"bufio"
	"io"
	"net"
	"strings"
	"sync"
	"time"

	"tap/internal/game"
	"tap/internal/logging"
	"tap/internal/protocol"
)

const (
	// maxLineBytes bounds a single message (RFC 9.4 recommends 1024 bytes).
	maxLineBytes = 1024
	// floodWindow / floodLimit define command-flooding detection.
	floodWindow = time.Second
	floodLimit  = 20
	// rapidConnWindow / rapidConnLimit define rapid-reconnection detection.
	rapidConnWindow = 10 * time.Second
	rapidConnLimit  = 10
)

// Server is a running TAP server.
type Server struct {
	game *game.Game
	log  *logging.Logger

	mu        sync.Mutex
	connTimes map[string][]time.Time // ip -> recent connection times (abuse monitor)
}

// New creates a server bound to the given game and logger.
func New(g *game.Game, log *logging.Logger) *Server {
	return &Server{game: g, log: log, connTimes: map[string][]time.Time{}}
}

// ListenAndServe binds to addr and serves connections until ln fails.
func (s *Server) ListenAndServe(addr string) error {
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		return err
	}
	s.log.Info("server_listening", logging.Fields{"addr": addr})
	for {
		conn, err := ln.Accept()
		if err != nil {
			s.log.Error("accept_failed", logging.Fields{"error": err.Error()})
			continue
		}
		go s.handleConn(conn)
	}
}

func ipOf(conn net.Conn) string {
	if host, _, err := net.SplitHostPort(conn.RemoteAddr().String()); err == nil {
		return host
	}
	return conn.RemoteAddr().String()
}

// monitorRapidConnections records a connection from ip and logs a WARN if the
// rate exceeds the configured threshold.
func (s *Server) monitorRapidConnections(ip string) {
	now := time.Now()
	s.mu.Lock()
	defer s.mu.Unlock()
	times := s.connTimes[ip]
	kept := times[:0]
	for _, t := range times {
		if now.Sub(t) < rapidConnWindow {
			kept = append(kept, t)
		}
	}
	kept = append(kept, now)
	s.connTimes[ip] = kept
	if len(kept) > rapidConnLimit {
		s.log.Warn("abuse_rapid_connections", logging.Fields{
			"ip": ip, "count": len(kept), "window_s": rapidConnWindow.Seconds(),
		})
	}
}

func (s *Server) handleConn(conn net.Conn) {
	ip := ipOf(conn)
	s.log.Info("connection_open", logging.Fields{"ip": ip})
	s.monitorRapidConnections(ip)

	defer func() {
		_ = conn.Close()
		s.log.Info("connection_close", logging.Fields{"ip": ip})
	}()

	reader := bufio.NewReader(conn)

	// RFC 3.2: server greets immediately.
	if _, err := io.WriteString(conn, protocol.Greeting+"\n"); err != nil {
		return
	}

	// Authentication phase: only CONNECT is accepted until identity is set.
	player := s.authenticate(conn, reader, ip)
	if player == nil {
		return
	}

	// Writer goroutine: serialises all outbound lines (replies + events).
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		w := bufio.NewWriter(conn)
		for line := range player.Out() {
			if _, err := w.WriteString(line + "\n"); err != nil {
				return
			}
			if err := w.Flush(); err != nil {
				return
			}
		}
	}()

	s.commandLoop(reader, player, ip)

	// Tear down: remove player state, then close its channel via Disconnect,
	// which lets the writer goroutine finish.
	s.game.Disconnect(player)
	wg.Wait()
}

// authenticate runs the pre-auth phase and returns the registered player, or
// nil if the connection ended or failed before authenticating.
func (s *Server) authenticate(conn net.Conn, reader *bufio.Reader, ip string) *game.Player {
	for {
		line, err := readLine(reader)
		if err != nil {
			return nil
		}
		cmd := protocol.ParseCommand(line)
		switch cmd.Name {
		case "CONNECT":
			if len(cmd.Args) < 1 {
				_, _ = io.WriteString(conn, protocol.Err(protocol.ErrTargetMissing, "TARGET_MISSING")+"\n")
				continue
			}
			player, errLine := s.game.Connect(cmd.Args[0], ip)
			if player == nil {
				_, _ = io.WriteString(conn, errLine+"\n")
				continue
			}
			_, _ = io.WriteString(conn, protocol.OK("connected")+"\n")
			return player
		case "QUIT":
			_, _ = io.WriteString(conn, protocol.OK("bye")+"\n")
			return nil
		case "":
			_, _ = io.WriteString(conn, protocol.Err(protocol.ErrBadRequest, "BAD_REQUEST")+"\n")
		default:
			_, _ = io.WriteString(conn, protocol.Err(protocol.ErrNotConnected, "NOT_CONNECTED")+"\n")
		}
	}
}

func (s *Server) commandLoop(reader *bufio.Reader, player *game.Player, ip string) {
	var windowStart time.Time
	var windowCount int

	for {
		line, err := readLine(reader)
		if err != nil {
			return // EOF or read error -> abrupt disconnect handled by caller
		}

		// Command-flood monitoring (logs only; the server stays responsive).
		now := time.Now()
		if now.Sub(windowStart) > floodWindow {
			windowStart, windowCount = now, 0
		}
		windowCount++
		if windowCount == floodLimit+1 {
			s.log.Warn("abuse_command_flood", logging.Fields{
				"player": player.Name, "ip": ip, "count": windowCount, "window_s": floodWindow.Seconds(),
			})
		}

		cmd := protocol.ParseCommand(line)
		reply, quit := s.game.Handle(player, cmd)
		player.Send(reply)
		if quit {
			return
		}
	}
}

// readLine reads one LF-terminated line, transparently handling TCP
// fragmentation and coalescing, and enforces the maximum line length. The
// returned string has no trailing CR/LF.
func readLine(reader *bufio.Reader) (string, error) {
	line, err := reader.ReadString('\n')
	if err != nil {
		if len(line) > 0 && err == io.EOF {
			return strings.TrimRight(line, "\r\n"), nil
		}
		return "", err
	}
	if len(line) > maxLineBytes {
		line = line[:maxLineBytes]
	}
	return strings.TrimRight(line, "\r\n"), nil
}
