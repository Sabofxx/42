// Command cli is the command-line TAP client.
//
// Design choice (documented in README): this client uses the raw-protocol
// approach. Lines typed by the user are sent to the server verbatim as RFC
// 42TAP commands, and every line received from the server (responses and
// asynchronous events) is printed in real time. A dedicated reader goroutine
// keeps the client responsive to events while it waits for user input.
//
// Usage:
//   cli [-addr host:port] [-name username]
package main

import (
	"bufio"
	"flag"
	"fmt"
	"net"
	"os"
	"strings"
)

func main() {
	addr := flag.String("addr", "127.0.0.1:4242", "server address host:port")
	name := flag.String("name", "", "username to CONNECT with (optional; prompted if empty)")
	flag.Parse()

	conn, err := net.Dial("tcp", *addr)
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot connect to %s: %v\n", *addr, err)
		os.Exit(1)
	}
	defer conn.Close()
	fmt.Printf("Connected to %s\n", *addr)

	server := bufio.NewReader(conn)

	// Reader goroutine: print everything the server sends, asynchronously.
	go func() {
		for {
			line, err := server.ReadString('\n')
			if err != nil {
				fmt.Println("\n[disconnected from server]")
				os.Exit(0)
			}
			fmt.Print("S< " + line)
			fmt.Print("> ")
		}
	}()

	// If a name was supplied, auto-CONNECT after the greeting is shown.
	if *name != "" {
		fmt.Fprintf(conn, "CONNECT %s\n", *name)
	}

	// Main loop: forward user input to the server line by line.
	stdin := bufio.NewScanner(os.Stdin)
	stdin.Buffer(make([]byte, 0, 1024), 1024)
	fmt.Print("> ")
	for stdin.Scan() {
		line := strings.TrimRight(stdin.Text(), "\r\n")
		if line == "" {
			fmt.Print("> ")
			continue
		}
		if _, err := fmt.Fprintf(conn, "%s\n", line); err != nil {
			fmt.Fprintln(os.Stderr, "send failed:", err)
			return
		}
		if strings.EqualFold(line, "QUIT") {
			return
		}
	}
}
