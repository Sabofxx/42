"""OpenAI-compatible LLM client with token accounting and key rotation."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from agent_smith.models import LLMResponse


def approximate_tokens(text: str) -> int:
    """Small deterministic token estimate used when provider usage is missing."""

    if not text:
        return 0
    return max(1, int(len(text) / 4))


@dataclass
class LLMConfig:
    provider_url: str
    model_name: str
    api_keys: list[str]
    temperature: float = 0.1
    max_tokens: int = 900
    timeout_seconds: float = 60.0
    max_retries: int = 0


class LLMClient:
    """Minimal OpenAI-compatible chat completions client."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._key_index = 0

    def _endpoint(self) -> str:
        base = self.config.provider_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    def _next_key(self) -> str | None:
        if not self.config.api_keys:
            return None
        key = self.config.api_keys[self._key_index % len(self.config.api_keys)]
        self._key_index += 1
        return key

    def complete(self, messages: list[dict[str, str]]) -> LLMResponse:
        """Generate a chat completion and normalize usage data."""

        if not self.config.provider_url or not self.config.model_name:
            raise RuntimeError("provider_url and model_name are required for LLM calls")
        if not self.config.api_keys:
            raise RuntimeError(
                "No API key found. Set OPENROUTER_API_KEY, OPENAI_API_KEY, "
                "AGENT_SMITH_API_KEYS, or pass --api-key-env."
            )

        payload: dict[str, Any] = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stop": ["<end_code>"],
        }
        body = json.dumps(payload).encode("utf-8")
        endpoint = self._endpoint()
        retries = 0
        last_error: Exception | None = None
        total_attempts = 1 + max(0, self.config.max_retries)

        for attempt in range(total_attempts):
            api_key = self._next_key()
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            request = urllib.request.Request(endpoint, data=body, headers=headers)
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(
                    request, timeout=self.config.timeout_seconds
                ) as response:
                    raw = response.read().decode("utf-8")
                latency_ms = (time.perf_counter() - started) * 1000
                parsed = json.loads(raw)
                text = parsed["choices"][0]["message"].get("content", "")
                usage = parsed.get("usage") or {}
                prompt_tokens = int(
                    usage.get(
                        "prompt_tokens",
                        approximate_tokens(json.dumps(messages, ensure_ascii=False)),
                    )
                )
                completion_tokens = int(
                    usage.get("completion_tokens", approximate_tokens(text))
                )
                return LLMResponse(
                    text=text,
                    input_tokens=prompt_tokens,
                    output_tokens=completion_tokens,
                    latency_ms=latency_ms,
                    retries=retries,
                )
            except urllib.error.HTTPError as exc:
                last_error = exc
                retryable = exc.code in {408, 409, 425, 429, 500, 502, 503, 504}
                if not retryable or attempt + 1 >= total_attempts:
                    break
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
                last_error = exc
                if attempt + 1 >= total_attempts:
                    break
            retries += 1
            time.sleep(min(2.0, 0.25 * (attempt + 1)))

        raise RuntimeError(f"LLM request failed after {retries + 1} attempt(s): {last_error}")

