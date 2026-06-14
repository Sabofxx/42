// Package protocol implements the wire-level constructs of RFC 42TAP:
// command parsing, response/error formatting and event formatting.
//
// Framing is one UTF-8 message per line, terminated by LF (0x0A).
package protocol

import (
	"fmt"
	"strings"
)

// Greeting is the initial line the server sends on connection (RFC 3.2).
const Greeting = "OK hello proto=1"

// Standard RFC 42TAP error codes (RFC section 8.2). The codes marked
// "(extension)" are deviations documented in the project README.
const (
	ErrNameInUse        = 201 // NAME_IN_USE
	ErrNoExit           = 301 // NO_EXIT
	ErrNotInGroup       = 401 // NOT_IN_GROUP
	ErrAlreadyInGroup   = 402 // ALREADY_IN_GROUP
	ErrItemNotFound     = 404 // ITEM_NOT_FOUND
	ErrItemNotInInv     = 404 // ITEM_NOT_IN_INVENTORY
	ErrNPCNotFound      = 404 // NPC_NOT_FOUND
	ErrNPCNotHostile    = 405 // NPC_NOT_HOSTILE
	ErrNoQuestAvailable = 406 // NO_QUEST_AVAILABLE
	ErrConnectionFailed = 900 // CONNECTION_FAILED
	ErrSendFailed       = 901 // SEND_FAILED

	// Extensions (documented as deviations in README):
	ErrBadRequest    = 400 // BAD_REQUEST       - malformed/unknown command or bad arguments
	ErrNotConnected  = 202 // NOT_CONNECTED     - command issued before CONNECT
	ErrAlreadyConn   = 203 // ALREADY_CONNECTED - CONNECT issued twice
	ErrNotInCombat   = 407 // NOT_IN_COMBAT     - DEFEND/FLEE with no active combat
	ErrTargetMissing = 408 // TARGET_MISSING    - required argument missing
)

// Command is a parsed client command.
type Command struct {
	Raw  string   // full original line (without trailing newline)
	Name string   // upper-cased command name (e.g. "MOVE")
	Args []string // whitespace-split arguments
}

// Rest returns the arguments from index i onward, re-joined with single
// spaces. Useful for free-form trailing text such as chat messages.
func (c Command) Rest(i int) string {
	if i >= len(c.Args) {
		return ""
	}
	return strings.Join(c.Args[i:], " ")
}

// ParseCommand splits a raw line into a Command. Command names are
// case-insensitive (RFC 4.2) and are normalised to upper case.
func ParseCommand(line string) Command {
	line = strings.TrimRight(line, "\r\n")
	fields := strings.Fields(line)
	c := Command{Raw: line}
	if len(fields) == 0 {
		return c
	}
	c.Name = strings.ToUpper(fields[0])
	c.Args = fields[1:]
	return c
}

// OK formats a success response. With no data it is the bare "OK".
func OK(data string) string {
	if data == "" {
		return "OK"
	}
	return "OK " + data
}

// Err formats an error response: "ERR <code> <message>" (RFC 8.1).
func Err(code int, message string) string {
	return fmt.Sprintf("ERR %d %s", code, message)
}

// Event formats an asynchronous event line: "EVT <type> <data>" (RFC 7.1).
func Event(eventType, data string) string {
	if data == "" {
		return "EVT " + eventType
	}
	return "EVT " + eventType + " " + data
}
