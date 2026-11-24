"""Layer 1 — OpenRouterProvider: OpenRouter auto-router + named models.

Same LLMProvider interface as MetaSparkProvider — complete(prompt, *,
max_tokens) -> str — so switching is only a config matter
(00-CEO-Core/config.json's providers section). The key comes only
from the OPENROUTER_API_KEY environment variable — never from a file, log, or
argument. If there is no key / a network error / an API error, it raises;
LiveBrainAdapter catches it and gives a LOUD mock fallback. Construction has no
network I/O (the key is read only in complete()).

The model can be chosen two ways:
  - "openrouter/free" — auto-router: on every request OpenRouter itself
    picks a fitting free model (Boss does not need to remember
    the model's name).
  - By name, e.g. "nvidia/nemotron-3-ultra-550b-a55b:free" — models ending in :free
    are free. Free models change (come/go),
    so it is good to keep several models in the fallback chain.
Free limit (OpenRouter docs): 20 requests/min, 50 requests/day;
Buying $10 lifetime credit gives 1,000/day. The limit is counted in requests,
not tokens.

Endpoint: https://openrouter.ai/api/v1/chat/completions
(OpenAI-compatible, official). Key available at: https://openrouter.ai/keys
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

ENV_VAR = "OPENROUTER_API_KEY"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/free"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


class OpenRouterProvider(LLMProvider):
    name = "openrouter-live"

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
                "OpenRouter API key missing: set " + ENV_VAR + " in the "
                "environment (never in a file). Get one at "
                "https://openrouter.ai/keys")
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            ENDPOINT,
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key,
                "HTTP-Referer": "https://talvenorai.agency",
                "X-Title": "Talvenor Master OS",
            },
            method="POST",
        )
        t0 = time.time()
        try:
            with urllib.request.build_opener(NoRedirect()).open(
                    req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            # Phase 1: surface the HTTP status explicitly so the
            # free-only guard's rate-limit detection (is_rate_limit_error)
            # can see a 429 even if the wrapped message is reworded.
            code = getattr(exc, "code", None)
            if isinstance(code, int):
                raise RuntimeError(
                    f"live brain call failed: HTTP {code}: "
                    f"{type(exc).__name__}: {exc}")
            raise RuntimeError(
                f"live brain call failed: {type(exc).__name__}: {exc}")
        if "error" in payload:
            raise RuntimeError(f"live brain API error: {payload['error']}")
        try:
            choice = payload["choices"][0]
            text = (choice["message"].get("content") or "").strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"live brain API error: unexpected response shape: {exc}")
        usage = payload.get("usage", {}) or {}
        self.calls += 1
        self.prompt_tokens += int(usage.get("prompt_tokens") or 0)
        self.completion_tokens += int(usage.get("completion_tokens") or 0)
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
