package protocol

import "testing"

func TestParseCommandCaseInsensitive(t *testing.T) {
	c := ParseCommand("move North\n")
	if c.Name != "MOVE" {
		t.Fatalf("name = %q, want MOVE", c.Name)
	}
	if len(c.Args) != 1 || c.Args[0] != "North" {
		t.Fatalf("args = %v, want [North]", c.Args)
	}
}

func TestRestJoinsTrailingText(t *testing.T) {
	c := ParseCommand("CHAT GLOBAL hello there world")
	if got := c.Rest(1); got != "hello there world" {
		t.Fatalf("Rest(1) = %q", got)
	}
	if got := c.Rest(0); got != "GLOBAL hello there world" {
		t.Fatalf("Rest(0) = %q", got)
	}
}

func TestFormatters(t *testing.T) {
	if OK("") != "OK" {
		t.Errorf("OK(\"\") = %q", OK(""))
	}
	if OK("room=loc.x") != "OK room=loc.x" {
		t.Errorf("OK data = %q", OK("room=loc.x"))
	}
	if Err(201, "NAME_IN_USE") != "ERR 201 NAME_IN_USE" {
		t.Errorf("Err = %q", Err(201, "NAME_IN_USE"))
	}
	if Event("ROOM PRESENCE ENTER", "alice") != "EVT ROOM PRESENCE ENTER alice" {
		t.Errorf("Event = %q", Event("ROOM PRESENCE ENTER", "alice"))
	}
}
