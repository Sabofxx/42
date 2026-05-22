"""Game renderer: draws maze, sprites, HUD and overlays."""

from __future__ import annotations

import math
from typing import List, Tuple

import pygame

from pacman.entities.ghost import Ghost, GhostState
from pacman.game import FloatingEffect, GameMode, GameState
from pacman.maze_loader import PACGUM, SUPER_PACGUM, WALL, WALL_42


def _color(config: dict, key: str, default: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Read a 3-tuple color from config."""

    value = config.get(key, default)
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(int(channel) for channel in value)  # type: ignore[return-value]
    return default


class Renderer:
    """Handles all drawing logic for the game scene."""

    HUD_HEIGHT = 56

    def __init__(self, screen: pygame.Surface, config: dict) -> None:
        self.screen = screen
        self.config = config
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 36, bold=True)
        self._anim_time = 0.0
        self._ghost_colors = [
            _color(config, f"color_ghost_{i + 1}", (255, 0, 0))
            for i in range(4)
        ]
        # Cached wall layer; invalidated when grid identity changes.
        self._wall_cache: pygame.Surface = pygame.Surface((1, 1))
        self._wall_cache_key: Tuple[int, int, int] = (0, 0, 0)
        # Cached ghost sprites keyed by (color, tile, mode).
        self._ghost_sprites: dict = {}
        self._ghost_sprite_tile: int = 0

    def _tile_size(self, grid: List[List[str]]) -> int:
        """Compute square tile pixel size that fits the playfield."""

        if not grid or not grid[0]:
            return 16
        playfield_w = self.screen.get_width()
        playfield_h = self.screen.get_height() - self.HUD_HEIGHT
        return max(4, min(playfield_w // len(grid[0]), playfield_h // len(grid)))

    def _offset(self, grid: List[List[str]], tile: int) -> Tuple[int, int]:
        """Center the playfield in the window below the HUD."""

        playfield_w = tile * len(grid[0])
        playfield_h = tile * len(grid)
        x = (self.screen.get_width() - playfield_w) // 2
        y = self.HUD_HEIGHT + (
            self.screen.get_height() - self.HUD_HEIGHT - playfield_h
        ) // 2
        return x, y

    def render_game(self, state: GameState, dt: float = 0.0) -> None:
        """Draw the full game frame."""

        self._anim_time += dt
        bg = _color(self.config, "color_background", (0, 0, 0))
        self.screen.fill(bg)
        if not state.grid:
            return

        tile = self._tile_size(state.grid)
        ox, oy = self._offset(state.grid, tile)
        self.render_grid(state.grid, tile, ox, oy)
        vx, vy = state.pacman.visual_pos
        self.render_pacman(vx, vy, state.pacman.dir, tile, ox, oy)
        self.render_ghosts(state.ghosts, tile, ox, oy)
        self.render_hud(state.score, state.lives, state.level, state.time_left)
        if state.frightened_time_left > 0.0:
            self._render_frightened_bar(
                state.frightened_time_left,
                float(self.config.get("frightened_duration", 10.0)),
            )
        self._render_effects(state.effects, tile, ox, oy)
        if state.ready_time_left > 0.0:
            self._render_ready_overlay(state.ready_time_left)
        if state.mode == GameMode.PAUSE:
            self.render_pause_overlay()

    def _rebuild_wall_cache(
        self,
        grid: List[List[str]],
        tile: int,
    ) -> None:
        """Pre-render the static wall layer once per level/resize."""

        width = tile * len(grid[0])
        height = tile * len(grid)
        wall_color = _color(self.config, "color_wall", (33, 33, 222))
        wall_42_color = _color(self.config, "color_wall_42", (66, 132, 255))
        corridor_color = _color(self.config, "color_corridor", (0, 0, 0))
        surface = pygame.Surface((width, height))
        surface.fill(corridor_color)
        for y, row in enumerate(grid):
            for x, tile_type in enumerate(row):
                if tile_type == WALL:
                    pygame.draw.rect(
                        surface,
                        wall_color,
                        pygame.Rect(x * tile, y * tile, tile, tile),
                    )
                elif tile_type == WALL_42:
                    pygame.draw.rect(
                        surface,
                        wall_42_color,
                        pygame.Rect(x * tile, y * tile, tile, tile),
                    )
        self._wall_cache = surface

    def render_grid(
        self,
        grid: List[List[str]],
        tile: int,
        ox: int,
        oy: int,
    ) -> None:
        """Draw the maze: walls (cached), pacgums and super-pacgums."""

        key = (id(grid), tile, len(grid))
        if key != self._wall_cache_key:
            self._rebuild_wall_cache(grid, tile)
            self._wall_cache_key = key
        self.screen.blit(self._wall_cache, (ox, oy))

        pacgum_color = _color(self.config, "color_pacgum", (255, 184, 255))
        super_color = _color(self.config, "color_super_pacgum", (255, 255, 255))
        pacgum_radius = max(2, tile // 6)
        super_radius = max(3, tile // 3)
        blink = (math.sin(self._anim_time * 6.0) + 1) * 0.5
        super_blink = (
            int(super_color[0] * (0.6 + 0.4 * blink)),
            int(super_color[1] * (0.6 + 0.4 * blink)),
            int(super_color[2] * (0.6 + 0.4 * blink)),
        )

        half = tile // 2
        for y, row in enumerate(grid):
            py = oy + y * tile + half
            for x, tile_type in enumerate(row):
                if tile_type == PACGUM:
                    pygame.draw.circle(
                        self.screen,
                        pacgum_color,
                        (ox + x * tile + half, py),
                        pacgum_radius,
                    )
                elif tile_type == SUPER_PACGUM:
                    pygame.draw.circle(
                        self.screen,
                        super_blink,
                        (ox + x * tile + half, py),
                        super_radius,
                    )

    def render_pacman(
        self,
        x: float,
        y: float,
        direction: Tuple[int, int],
        tile: int,
        ox: int,
        oy: int,
    ) -> None:
        """Draw an animated Pac-Man with waka mouth at a continuous pos."""

        color = _color(self.config, "color_pacman", (255, 255, 0))
        center = (
            int(ox + x * tile + tile / 2),
            int(oy + y * tile + tile / 2),
        )
        radius = tile // 2 - 1
        if radius <= 1:
            pygame.draw.circle(self.screen, color, center, max(1, radius))
            return

        mouth = abs(math.sin(self._anim_time * 8.0)) * (math.pi / 3)
        angle_map = {
            (1, 0): 0.0,
            (-1, 0): math.pi,
            (0, -1): -math.pi / 2,
            (0, 1): math.pi / 2,
            (0, 0): 0.0,
        }
        facing = angle_map.get(direction, 0.0)
        start = facing + mouth
        end = facing - mouth + 2 * math.pi
        points: List[Tuple[float, float]] = [
            (float(center[0]), float(center[1]))
        ]
        steps = 24
        for index in range(steps + 1):
            theta = start + (end - start) * index / steps
            points.append(
                (
                    center[0] + radius * math.cos(theta),
                    center[1] + radius * math.sin(theta),
                )
            )
        pygame.draw.polygon(self.screen, color, points)

    def _build_ghost_sprite(
        self,
        color: Tuple[int, int, int],
        tile: int,
    ) -> pygame.Surface:
        """Render a ghost sprite (body + skirt + eyes) once, reuse forever."""

        surface = pygame.Surface((tile, tile), pygame.SRCALPHA)
        radius = tile // 2 - 1
        if radius <= 1:
            pygame.draw.circle(
                surface, color, (tile // 2, tile // 2), max(1, radius)
            )
            return surface
        cx = cy = tile // 2
        body_rect = pygame.Rect(
            cx - radius, cy - radius, radius * 2, radius * 2
        )
        pygame.draw.rect(surface, color, body_rect, border_radius=radius)
        # Wavy skirt at the bottom — three little half-circles.
        skirt_y = cy + radius - radius // 4
        bump = max(2, radius // 3)
        for k in range(3):
            sx = cx - radius + bump + k * bump * 2
            pygame.draw.circle(surface, color, (sx, skirt_y), bump)
        # Eyes
        eye_white = (255, 255, 255)
        pupil = (10, 10, 80)
        eye_radius = max(2, radius // 3)
        offset = max(2, radius // 2)
        for sign in (-1, 1):
            ex = cx + sign * offset // 2
            ey = cy - offset // 3
            pygame.draw.circle(surface, eye_white, (ex, ey), eye_radius)
            pygame.draw.circle(surface, pupil, (ex, ey), eye_radius // 2)
        return surface

    def _get_ghost_sprite(
        self,
        color: Tuple[int, int, int],
        tile: int,
    ) -> pygame.Surface:
        """Return a cached ghost sprite, building it on first request."""

        if tile != self._ghost_sprite_tile:
            self._ghost_sprites.clear()
            self._ghost_sprite_tile = tile
        sprite = self._ghost_sprites.get(color)
        if sprite is None:
            sprite = self._build_ghost_sprite(color, tile)
            self._ghost_sprites[color] = sprite
        return sprite

    def render_ghosts(
        self,
        ghosts: List[Ghost],
        tile: int,
        ox: int,
        oy: int,
    ) -> None:
        """Draw each ghost from a pre-rendered sprite (much faster)."""

        frightened_color = (40, 80, 220)
        for index, ghost in enumerate(ghosts):
            if ghost.state == GhostState.EATEN:
                continue
            base = self._ghost_colors[index % len(self._ghost_colors)]
            if ghost.state == GhostState.FRIGHTENED:
                blink = math.sin(self._anim_time * 12.0) > 0
                color = (240, 240, 240) if blink else frightened_color
            else:
                color = base
            sprite = self._get_ghost_sprite(color, tile)
            vx, vy = ghost.visual_pos
            px = int(ox + vx * tile)
            py = int(oy + vy * tile)
            self.screen.blit(sprite, (px, py))

    def render_hud(
        self,
        score: int,
        lives: int,
        level: int,
        time_left: float,
    ) -> None:
        """Draw HUD bar (score, lives icons, level, time)."""

        hud_rect = pygame.Rect(0, 0, self.screen.get_width(), self.HUD_HEIGHT)
        pygame.draw.rect(self.screen, (20, 20, 40), hud_rect)
        pygame.draw.line(
            self.screen,
            (80, 80, 160),
            (0, self.HUD_HEIGHT - 2),
            (self.screen.get_width(), self.HUD_HEIGHT - 2),
            2,
        )
        cy = self.HUD_HEIGHT // 2

        score_surface = self.font.render(
            f"SCORE {score:06d}", True, (255, 255, 255)
        )
        self.screen.blit(
            score_surface, (16, cy - score_surface.get_height() // 2)
        )

        pac_color = _color(self.config, "color_pacman", (255, 255, 0))
        icon_radius = 9
        icon_gap = 22
        lives_x = 16 + score_surface.get_width() + 24
        for index in range(max(0, lives)):
            pygame.draw.circle(
                self.screen,
                pac_color,
                (lives_x + index * icon_gap, cy),
                icon_radius,
            )

        right_text = (
            f"LEVEL {level:2d}   TIME {max(0, int(time_left)):3d}s"
        )
        right_surface = self.font.render(right_text, True, (255, 255, 255))
        self.screen.blit(
            right_surface,
            (
                self.screen.get_width() - right_surface.get_width() - 16,
                cy - right_surface.get_height() // 2,
            ),
        )

    def _render_effects(
        self,
        effects: List[FloatingEffect],
        tile: int,
        ox: int,
        oy: int,
    ) -> None:
        """Draw floating score popups with fade-out."""

        if not effects:
            return
        for effect in effects:
            ratio = max(0.0, min(1.0, effect.time_left / max(0.001, effect.lifetime)))
            alpha = int(255 * ratio)
            text = self.font.render(effect.text, True, effect.color)
            text.set_alpha(alpha)
            px = int(ox + effect.x * tile + tile / 2 - text.get_width() / 2)
            py = int(oy + effect.y * tile + tile / 2 - text.get_height() / 2)
            self.screen.blit(text, (px, py))

    def _render_ready_overlay(self, time_left: float) -> None:
        """Show a centered READY! banner during the respawn grace."""

        text = self.big_font.render("READY!", True, (255, 220, 0))
        rect = text.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )
        pad = 16
        bg_rect = rect.inflate(pad * 2, pad * 2)
        bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        self.screen.blit(bg, bg_rect.topleft)
        self.screen.blit(text, rect)
        sub = self.font.render(
            f"{time_left:.1f}s", True, (255, 255, 255)
        )
        sub_rect = sub.get_rect(
            center=(rect.centerx, rect.bottom + 24)
        )
        self.screen.blit(sub, sub_rect)

    def _render_frightened_bar(self, time_left: float, total: float) -> None:
        """Draw a thin bar under the HUD showing super-pacgum time left."""

        if total <= 0.0:
            return
        ratio = max(0.0, min(1.0, time_left / total))
        width = int(self.screen.get_width() * 0.6)
        height = 6
        x = (self.screen.get_width() - width) // 2
        y = self.HUD_HEIGHT + 4
        pygame.draw.rect(self.screen, (60, 60, 80), (x, y, width, height))
        fill = int(width * ratio)
        color = (40, 80, 220) if ratio > 0.25 else (240, 240, 240)
        pygame.draw.rect(self.screen, color, (x, y, fill, height))

    def render_pause_overlay(self) -> None:
        """Draw a centered PAUSED overlay."""

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        text = self.big_font.render("PAUSED", True, (255, 255, 255))
        rect = text.get_rect(center=self.screen.get_rect().center)
        self.screen.blit(text, rect)

    def render_cheat_overlay(self, active_cheats: dict) -> None:
        """Draw a corner overlay listing active cheats."""

        labels: List[str] = []
        if active_cheats.get("invincible"):
            labels.append("INVINCIBLE")
        if active_cheats.get("ghosts_frozen"):
            labels.append("GHOSTS FROZEN")
        if active_cheats.get("double_speed"):
            labels.append("SPEED x2")
        if not labels:
            return
        y = self.HUD_HEIGHT + 4
        for label in labels:
            surface = self.font.render(label, True, (255, 200, 0))
            self.screen.blit(surface, (8, y))
            y += surface.get_height() + 2

    def flip(self) -> None:
        """Push the back buffer to the display."""

        pygame.display.flip()
