"""Environment and .env loading utilities."""

from __future__ import annotations

import os
from pathlib import Path


def _discover_default_env_file() -> Path | None:
    """Look for a .env in the current working directory and parents."""

    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        env_path = candidate / ".env"
        if env_path.is_file():
            return env_path
    return None


def load_env_file(path: str | None) -> None:
    """Load KEY=VALUE pairs from a .env file without overriding env vars.

    When ``path`` is None, walks up from the current working directory to find
    a ``.env`` file. Missing files are silently ignored in that auto-discovery
    mode so the agent stays usable when keys come from the environment only.
    """

    env_path: Path | None
    if path:
        env_path = Path(path)
        if not env_path.exists():
            raise FileNotFoundError(f".env file not found: {env_path}")
    else:
        env_path = _discover_default_env_file()
        if env_path is None:
            return
    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def split_env_tokens(value: str | None) -> list[str]:
    """Split API key env values that may be comma, colon, or newline separated."""

    if not value:
        return []
    tokens: list[str] = []
    for chunk in value.replace("\n", ",").replace(":", ",").split(","):
        token = chunk.strip()
        if token:
            tokens.append(token)
    return tokens


def api_keys_for_provider(provider_url: str, explicit_env: str | None = None) -> list[str]:
    """Return API tokens for a provider, supporting multi-token rotation."""

    env_names: list[str] = []
    if explicit_env:
        env_names.append(explicit_env)
    env_names.append("AGENT_SMITH_API_KEYS")

    lower_url = provider_url.lower()
    if "openrouter" in lower_url:
        env_names.append("OPENROUTER_API_KEY")
    if "together" in lower_url:
        env_names.append("TOGETHER_API_KEY")
    if "groq" in lower_url:
        env_names.append("GROQ_API_KEY")
    if "mistral" in lower_url:
        env_names.append("MISTRAL_API_KEY")
    if "fireworks" in lower_url:
        env_names.append("FIREWORKS_API_KEY")
    if "cohere" in lower_url:
        env_names.append("COHERE_API_KEY")
    if "google" in lower_url or "generativelanguage" in lower_url:
        env_names.append("GOOGLE_API_KEY")

    env_names.extend(["OPENAI_API_KEY", "OPENAI_COMPATIBLE_API_KEY"])
    seen: set[str] = set()
    keys: list[str] = []
    for env_name in env_names:
        for key in split_env_tokens(os.environ.get(env_name)):
            if key not in seen:
                seen.add(key)
                keys.append(key)
    return keys

