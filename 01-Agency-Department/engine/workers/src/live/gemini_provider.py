"""Layer 1 — GeminiProvider: Google Gemini model (OpenAI-compatible endpoint).

MetaSparkProvider-এর মতোই LLMProvider interface — complete(prompt, *,
max_tokens) -> str — তাই বদলানো শুধু config-এর ব্যাপার
(00-CEO-Core/config.json-এর providers section)। Key আসে শুধু
GEMINI_API_KEY environment variable থেকে — কখনো file, log বা argument
থেকে নয়। Key নেই / network error / API error হলে raise করে;
LiveBrainAdapter ধরে LOUD mock fallback দেয়। Construction-এ কোনো
network I/O নেই (key পড়া হয় শুধু complete()-এ)।

Google-এর official OpenAI compatibility endpoint — OpenAI-র মতোই
chat completions shape, শুধু base URL আলাদা (Google AI Studio docs)।
Endpoint: https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
Key পাওয়া যায়: https://aistudio.google.com/apikey
Stdlib only — কোনো pip নেই।
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

ENV_VAR = "GEMINI_API_KEY"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
DEFAULT_MODEL = "gemini-2.5-flash"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


class GeminiProvider(LLMProvider):
    name = "gemini-live"

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
                "Gemini API key missing: set " + ENV_VAR + " in the "
                "environment (never in a file). Get one at "
                "https://aistudio.google.com/apikey")
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
