// Command gui is the graphical TAP client.
//
// It is a self-contained Go program (standard library only) that acts as a
// bridge between the browser and the TAP server: it opens one TCP connection
// to the server, serves a web UI on a local HTTP port, streams every server
// line to the browser over Server-Sent Events, and forwards user commands
// back over TCP via HTTP POST. The web page is the graphical interface
// (web-based GUI is explicitly permitted by the subject).
//
// Usage:
//   gui [-addr server-host:port] [-http localhost:port]
package main

import (
	"bufio"
	"embed"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"sync"
)

//go:embed web/*
var webFS embed.FS

// bridge fans out server lines to all connected SSE subscribers and forwards
// browser commands to the single TCP connection.
type bridge struct {
	conn net.Conn

	mu   sync.Mutex
	subs map[chan string]bool
}

func newBridge(conn net.Conn) *bridge {
	return &bridge{conn: conn, subs: map[chan string]bool{}}
}

func (b *bridge) subscribe() chan string {
	ch := make(chan string, 256)
	b.mu.Lock()
	b.subs[ch] = true
	b.mu.Unlock()
	return ch
}

func (b *bridge) unsubscribe(ch chan string) {
	b.mu.Lock()
	delete(b.subs, ch)
	b.mu.Unlock()
}

func (b *bridge) publish(line string) {
	b.mu.Lock()
	defer b.mu.Unlock()
	for ch := range b.subs {
		select {
		case ch <- line:
		default:
		}
	}
}

// readServer pumps server lines into all subscribers until the TCP
// connection closes.
func (b *bridge) readServer() {
	r := bufio.NewReader(b.conn)
	for {
		line, err := r.ReadString('\n')
		if len(line) > 0 {
			b.publish(line)
		}
		if err != nil {
			b.publish("EVT CLIENT DISCONNECTED server connection closed\n")
			return
		}
	}
}

func (b *bridge) send(cmd string) error {
	_, err := io.WriteString(b.conn, cmd+"\n")
	return err
}

func main() {
	serverAddr := flag.String("addr", "127.0.0.1:4242", "TAP server address host:port")
	httpAddr := flag.String("http", "127.0.0.1:8080", "local HTTP address for the web UI")
	flag.Parse()

	conn, err := net.Dial("tcp", *serverAddr)
	if err != nil {
		fmt.Printf("cannot connect to TAP server %s: %v\n", *serverAddr, err)
		return
	}
	defer conn.Close()

	b := newBridge(conn)
	go b.readServer()

	mux := http.NewServeMux()

	// Static UI.
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		data, err := webFS.ReadFile("web/index.html")
		if err != nil {
			http.Error(w, "ui not found", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		_, _ = w.Write(data)
	})

	// Server-Sent Events: stream every server line to the browser.
	mux.HandleFunc("/events", func(w http.ResponseWriter, r *http.Request) {
		flusher, ok := w.(http.Flusher)
		if !ok {
			http.Error(w, "streaming unsupported", http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "text/event-stream")
		w.Header().Set("Cache-Control", "no-cache")
		w.Header().Set("Connection", "keep-alive")

		ch := b.subscribe()
		defer b.unsubscribe(ch)

		for {
			select {
			case <-r.Context().Done():
				return
			case line, ok := <-ch:
				if !ok {
					return
				}
				// SSE frame: strip trailing newline, send as one data event.
				for len(line) > 0 && (line[len(line)-1] == '\n' || line[len(line)-1] == '\r') {
					line = line[:len(line)-1]
				}
				fmt.Fprintf(w, "data: %s\n\n", line)
				flusher.Flush()
			}
		}
	})

	// Command forwarding: POST body is one raw protocol line.
	mux.HandleFunc("/cmd", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "POST only", http.StatusMethodNotAllowed)
			return
		}
		body, _ := io.ReadAll(io.LimitReader(r.Body, 1024))
		if err := b.send(string(body)); err != nil {
			http.Error(w, err.Error(), http.StatusBadGateway)
			return
		}
		w.WriteHeader(http.StatusNoContent)
	})

	fmt.Printf("TAP GUI client running.\n  Server : %s\n  Open   : http://%s\n", *serverAddr, *httpAddr)
	if err := http.ListenAndServe(*httpAddr, mux); err != nil {
		fmt.Println("http server error:", err)
	}
}
