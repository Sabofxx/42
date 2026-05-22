"""Pygame window, clock and input handling."""

from __future__ import annotations

import sys
from typing import Callable, Optional, Tuple

try:
    import pygame
except Exception as exc:  # pragma: no cover - environment-dependent
    print(f"[window] Pygame is required: {exc}", file=sys.stderr)
    raise


_DIRECTION_KEYS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


class GameWindow:
    """Pygame display surface, clock, and event pump."""

    def __init__(
        self,
        width: int,
        height: int,
        title: str = "Pac-Man",
        fps: int = 60,
    ) -> None:
        pygame.init()
        pygame.display.set_caption(title)
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = max(1, int(fps))
        self._direction: Tuple[int, int] = (0, 0)
        self._buffered: Tuple[int, int] = (0, 0)
        self._quit_requested = False
        self._pending_events: list = []

    def get_input(self) -> Tuple[int, int]:
        """Return latest buffered direction (held key fallback)."""

        if self._buffered != (0, 0):
            direction = self._buffered
            self._buffered = (0, 0)
            self._direction = direction
            return direction
        pressed = pygame.key.get_pressed()
        for key, vector in _DIRECTION_KEYS.items():
            if pressed[key]:
                self._direction = vector
                return vector
        return (0, 0)

    def handle_events(
        self,
        on_quit: Optional[Callable[[], None]] = None,
        on_pause: Optional[Callable[[], None]] = None,
        on_key: Optional[Callable[[int, str], None]] = None,
    ) -> bool:
        """Process events. Return False if the user closed the window."""

        self._pending_events = []
        for event in pygame.event.get():
            self._pending_events.append(event)
            if event.type == pygame.QUIT:
                self._quit_requested = True
                if on_quit is not None:
                    on_quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and on_pause is not None:
                    on_pause()
                if event.key in _DIRECTION_KEYS:
                    self._buffered = _DIRECTION_KEYS[event.key]
                if on_key is not None:
                    on_key(event.key, getattr(event, "unicode", ""))
        return not self._quit_requested

    @property
    def events(self) -> list:
        """Return events captured during the last `handle_events` call."""

        return list(self._pending_events)

    def set_fps(self, fps: int) -> None:
        """Update FPS cap."""

        self.fps = max(1, int(fps))

    def tick(self) -> float:
        """Advance clock; return delta time in seconds (clamped).

        We clamp dt to 1/30s so a long stall (loading, defocus, menu idle,
        breakpoint) cannot translate into a multi-cell physics jump on the
        first frame after the stall.
        """

        return min(self.clock.tick(self.fps) / 1000.0, 1.0 / 30.0)

    def update(self, dt: float = 0.0) -> None:
        """Alias for tick (kept for backwards compatibility)."""

        self.tick()

    def close(self) -> None:
        """Shut down pygame cleanly."""

        try:
            pygame.quit()
        except Exception:  # pragma: no cover
            pass
