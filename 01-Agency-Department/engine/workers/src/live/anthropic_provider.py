"""Layer 1 — AnthropicProvider: Claude model (Anthropic Messages API).

Same LLMProvider interface as MetaSparkProvider — complete(prompt, *,
max_tokens) -> str — so switching is only a config matter
(00-CEO-Core/config.json's providers section). The key comes only
from the ANTHROPIC_API_KEY environment variable — never from a file, log, or
argument. If there is no key / a network error / an API error, it raises;
LiveBrainAdapter catches it and gives a LOUD mock fallback. Construction has no
network I/O (the key is read only in complete()).

Anthropic's API is not like OpenAI's — Messages API: system is a separate field,
max_tokens is mandatory in the body, and the response has a list of content blocks.
Endpoint: https://api.anthropic.com/v1/messages (Anthropic, official).
Key available at: https://console.anthropic.com/settings/keys
Stdlib only — no pip.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

from src.contracts.llm import LLMProvider  # noqa: E402

SYSTEM_PROMPT = (
    "You are a specialist worker inside CEO-OS, a personal CEO agent "
    "for a solo founder. Follow the brief exactly. Be concise and concrete. "
    "Never invent numbers, clients, prices, or results — if a number is "
    "needed and not given, say what input is missing."
)

ENV_VAR = "ANTHROPIC_API_KEY"
ENDPOINT = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-4-5"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


class AnthropicProvider(LLMProvider):
    name = "anthropic-live"

    def __init__(self, model: str = DEFAULT_MODEL, timeout: int = 90):
        self.model = model
        self.timeout = timeout
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        api_key = os.environ.get(ENV_VAR)
        if not api_key:
            raise RuntimeError(
                "Anthropic API key missing: set " + ENV_VAR + " in the "
                "environment (never in a file). Get one at "
                "https://console.anthropic.com/settings/keys")
        body = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": ANTHROPIC_VERSION,
            },
            method="POST",
        )
        t0 = time.time()
        try:
            with urllib.request.build_opener(NoRedirect()).open(
                    req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(
                f"live brain call failed: {type(exc).__name__}: {exc}")
        if "error" in payload:
            raise RuntimeError(f"live brain API error: {payload['error']}")
        try:
            blocks = payload.get("content", []) or []
            text = "".join(
                block.get("text", "")
                for block in blocks if block.get("type") == "text"
            ).strip()
        except (AttributeError, TypeError) as exc:
            raise RuntimeError(
                f"live brain API error: unexpected response shape: {exc}")
        usage = payload.get("usage", {}) or {}
        self.calls += 1
        self.prompt_tokens += int(usage.get("input_tokens") or 0)
        self.completion_tokens += int(usage.get("output_tokens") or 0)
        return text

    def health(self) -> dict:
        return {
            "provider": self.name,
            "ok": True,
            "calls": self.calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.prompt_tokens + self.completion_tokens,
        }
