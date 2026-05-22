"""Persistent highscore system."""

from __future__ import annotations

import json
import string
import sys
from pathlib import Path
from typing import List, Optional, Tuple

HighscoreEntry = Tuple[str, int]
_MAX_ENTRIES = 10
_NAME_MAX = 10
_ALLOWED = set(string.ascii_letters + string.digits + " ")


def _log(message: str) -> None:
    """Print a clear highscore warning."""

    print(f"[highscore] {message}", file=sys.stderr)


class HighscoreManager:
    """Manages persistent top-10 highscores in JSON."""

    def __init__(self, filename: str = "highscores.json") -> None:
        self.filename = filename
        self._entries: List[HighscoreEntry] = self.load()

    def load(self) -> List[HighscoreEntry]:
        """Load highscores from disk, recovering on errors."""

        path = Path(self.filename)
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            _log(f"Could not read '{self.filename}': {exc}. Starting empty.")
            return []

        if not isinstance(data, list):
            _log("Highscore file has invalid format. Starting empty.")
            return []

        cleaned: List[HighscoreEntry] = []
        for raw in data:
            if (
                isinstance(raw, list)
                and len(raw) == 2
                and isinstance(raw[0], str)
            ):
                try:
                    score = int(raw[1])
                except (TypeError, ValueError):
                    continue
                if score < 0:
                    continue
                name = HighscoreManager.validate_name(raw[0])
                cleaned.append((name, score))

        cleaned.sort(key=lambda pair: pair[1], reverse=True)
        self._entries = cleaned[:_MAX_ENTRIES]
        return list(self._entries)

    def save(self, highscores: Optional[List[HighscoreEntry]] = None) -> bool:
        """Save highscores to disk. Never raises."""

        if highscores is not None:
            self._entries = list(highscores)[:_MAX_ENTRIES]
        try:
            Path(self.filename).write_text(
                json.dumps([list(pair) for pair in self._entries], indent=2),
                encoding="utf-8",
            )
            return True
        except OSError as exc:
            _log(f"Could not save highscores: {exc}.")
            return False

    def add_score(self, name: str, score: int) -> Optional[int]:
        """Insert score and return its rank (1-based) if it makes top 10."""

        sanitized = HighscoreManager.validate_name(name)
        try:
            score_value = int(score)
        except (TypeError, ValueError):
            return None
        if score_value < 0:
            return None
        entries = list(self._entries) + [(sanitized, score_value)]
        entries.sort(key=lambda pair: pair[1], reverse=True)
        entries = entries[:_MAX_ENTRIES]
        rank: Optional[int] = None
        for index, pair in enumerate(entries):
            if pair == (sanitized, score_value) and rank is None:
                rank = index + 1
        self._entries = entries
        self.save()
        return rank

    def get_top_10(self) -> List[HighscoreEntry]:
        """Return a copy of the current top 10 entries."""

        return list(self._entries)

    @staticmethod
    def validate_name(name: str) -> str:
        """Sanitize a player name to alphanumeric/space, max 10 chars."""

        if not isinstance(name, str):
            return "Player"
        cleaned = "".join(ch for ch in name if ch in _ALLOWED).strip()
        cleaned = cleaned[:_NAME_MAX]
        return cleaned or "Player"
