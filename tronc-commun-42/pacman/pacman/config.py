"""Configuration parser for Pac-Man game."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "highscore_filename": "highscores.json",
    "width": 21,
    "height": 21,
    "perfect_maze": False,
    "seed": 42,
    "lives": 3,
    "player_speed": 5.0,
    "level_max_time": 90,
    "num_levels": 10,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "ghost_speed": 4.0,
    "frightened_duration": 10.0,
    "respawn_delay": 5.0,
    "window_width": 672,
    "window_height": 756,
    "tile_size": 32,
    "fps": 60,
    "color_background": [0, 0, 0],
    "color_pacman": [255, 255, 0],
    "color_wall": [33, 33, 222],
    "color_wall_42": [66, 132, 255],
    "color_corridor": [0, 0, 0],
    "color_pacgum": [255, 184, 255],
    "color_super_pacgum": [255, 255, 255],
    "color_ghost_1": [255, 0, 0],
    "color_ghost_2": [255, 184, 255],
    "color_ghost_3": [0, 255, 255],
    "color_ghost_4": [255, 184, 82],
}

_INT_KEYS = {
    "width",
    "height",
    "seed",
    "lives",
    "level_max_time",
    "num_levels",
    "points_per_pacgum",
    "points_per_super_pacgum",
    "points_per_ghost",
    "window_width",
    "window_height",
    "tile_size",
    "fps",
}
_FLOAT_KEYS = {
    "player_speed",
    "ghost_speed",
    "frightened_duration",
    "respawn_delay",
}


def _log(message: str) -> None:
    """Print a clear configuration warning."""

    print(f"[config] {message}", file=sys.stderr)


def _strip_comments(raw_text: str) -> str:
    """Remove lines starting with # before JSON parsing."""

    lines = [
        line
        for line in raw_text.splitlines()
        if not line.lstrip().startswith("#")
    ]
    return "\n".join(lines)


def _clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    """Convert a value to a bounded integer."""

    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _clamp_float(
    value: Any,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    """Convert a value to a bounded float."""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _normalize_color(value: Any, default: list[int]) -> list[int]:
    """Validate an RGB color list."""

    if not isinstance(value, list) or len(value) != 3:
        return list(default)

    result: list[int] = []
    for item in value:
        try:
            channel = int(item)
        except (TypeError, ValueError):
            return list(default)
        result.append(max(0, min(255, channel)))
    return result


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and apply defaults to loaded config."""

    validated: Dict[str, Any] = dict(DEFAULT_CONFIG)

    for key, default_value in DEFAULT_CONFIG.items():
        if key not in config:
            _log(f"Missing '{key}', using default value {default_value!r}.")
            continue

        raw_value = config[key]
        if key in _INT_KEYS:
            validated[key] = _clamp_int(
                raw_value,
                int(default_value),
                1,
                10_000,
            )
        elif key in _FLOAT_KEYS:
            validated[key] = _clamp_float(
                raw_value,
                float(default_value),
                0.1,
                10_000.0,
            )
        elif key == "perfect_maze":
            validated[key] = bool(raw_value)
        elif key.startswith("color_"):
            validated[key] = _normalize_color(raw_value, list(default_value))
        elif key == "highscore_filename":
            try:
                candidate = str(raw_value).strip()
            except Exception:
                candidate = ""
            validated[key] = candidate or default_value
        else:
            validated[key] = raw_value

    for key in sorted(set(config).difference(DEFAULT_CONFIG)):
        if key.lstrip().startswith("#"):
            continue
        _log(f"Ignoring unknown config key '{key}'.")

    validated["width"] = max(5, validated["width"])
    validated["height"] = max(5, validated["height"])
    validated["lives"] = max(1, validated["lives"])
    validated["num_levels"] = max(1, validated["num_levels"])
    validated["level_max_time"] = max(1, validated["level_max_time"])
    validated["points_per_pacgum"] = max(0, validated["points_per_pacgum"])
    validated["points_per_super_pacgum"] = max(
        0,
        validated["points_per_super_pacgum"],
    )
    validated["points_per_ghost"] = max(0, validated["points_per_ghost"])

    return validated


def parse_config(filepath: str) -> Dict[str, Any]:
    """Parse config.json file with comment support."""

    path = Path(filepath)
    if not path.exists():
        _log(f"Config file not found: {filepath}")
        return dict(DEFAULT_CONFIG)

    try:
        raw_text = path.read_text(encoding="utf-8")
        config_data = json.loads(_strip_comments(raw_text) or "{}")
    except json.JSONDecodeError as exc:
        _log(f"Invalid JSON in config file: {exc}")
        return dict(DEFAULT_CONFIG)
    except OSError as exc:
        _log(f"Unable to read config file: {exc}")
        return dict(DEFAULT_CONFIG)

    if not isinstance(config_data, dict):
        _log("Config file must contain a JSON object at the top level.")
        return dict(DEFAULT_CONFIG)

    return validate_config(config_data)
