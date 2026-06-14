// Package logging provides structured JSON logging for the TAP server.
//
// Every record carries a precise RFC3339Nano timestamp, a level
// (INFO/WARN/ERROR) and an event name, plus arbitrary structured fields.
// Records are emitted as one JSON object per line so they are trivial to
// parse with tools such as jq. Logging is serialised behind a mutex and
// kept to a single Encoder write per record to avoid measurable impact on
// server responsiveness.
package logging

import (
	"encoding/json"
	"io"
	"sync"
	"time"
)

// Level is a log severity.
type Level string

const (
	INFO  Level = "INFO"
	WARN  Level = "WARN"
	ERROR Level = "ERROR"
)

// Fields is a set of structured key/value pairs attached to a log record.
type Fields map[string]interface{}

// Logger writes structured JSON log records to an output stream.
type Logger struct {
	mu  sync.Mutex
	enc *json.Encoder
}

// New creates a Logger writing newline-delimited JSON to w.
func New(w io.Writer) *Logger {
	return &Logger{enc: json.NewEncoder(w)}
}

// Log writes a single record at the given level.
func (l *Logger) Log(level Level, event string, f Fields) {
	rec := make(map[string]interface{}, len(f)+3)
	for k, v := range f {
		rec[k] = v
	}
	rec["ts"] = time.Now().Format(time.RFC3339Nano)
	rec["level"] = string(level)
	rec["event"] = event

	l.mu.Lock()
	_ = l.enc.Encode(rec) // Encode appends a newline.
	l.mu.Unlock()
}

// Info logs at INFO level.
func (l *Logger) Info(event string, f Fields) { l.Log(INFO, event, f) }

// Warn logs at WARN level.
func (l *Logger) Warn(event string, f Fields) { l.Log(WARN, event, f) }

// Error logs at ERROR level.
func (l *Logger) Error(event string, f Fields) { l.Log(ERROR, event, f) }
