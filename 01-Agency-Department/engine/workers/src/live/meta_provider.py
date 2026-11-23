"""Layer 1 — MetaSparkProvider: the REAL brain (Muse Spark via Meta Model API).

Same LLMProvider interface as MockLLMProvider, so swapping is a config
change (boss_run.py --live). Auth uses the registered connector credential
(custom.meta-model-api-2) via the Secure Vault surrogate — the real key
never appears in a file, env var, argument, or log. One request per
complete() call, no retries, no redirects. A failed call raises; the worker
base catches it and marks the worker failed — the day never crashes.

Boss approved the real brain 2026-11-06 00:18 (from his $150 credit).
First live verification 2026-11-06 00:19 TIMED OUT after 60s ($0 spent,
key validity unproven) — the provider code below is ready, the key path
is NOT yet proven; retry only on Boss's word.
"""
from __future__ import annotations

import json
import time
import urllib.request

from src.contracts.llm import LLMProvider


def _load_surrogate():
    """Secure Vault surrogate — imported LAZILY (Phase 2).

    The old top-level ``sys.path.insert(0, "/opt/muse/skills/..."
    + "custom-connector-setup/bin")`` + ``from dynamic_credentials import
    ...`` made this module un-importable on a plain checkout (Boss's
    PC), where that VM-only directory does not exist. Now the import
    happens only when complete() actually runs a live call, and a
    missing surrogate fails that call with a clear error instead of
    breaking the import.
    """
    import sys

    sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
    try:
        from dynamic_credentials import (  # noqa: E402
            add_surrogate_to_request, read_json_response)
    except ImportError as exc:
        raise RuntimeError(
            "live brain unavailable: the Meta connector surrogate "
            "(dynamic_credentials) is not installed on this machine — "
            "run on the Muse VM, or install the connector first"
        ) from exc
    return add_surrogate_to_request, read_json_response

SYSTEM_PROMPT = (
    "You are a specialist worker inside CEO-OS, a personal CEO agent "
    "for a solo founder. Follow the brief exactly. Be concise and concrete. "
    "Never invent numbers, clients, prices, or results — if a number is "
    "needed and not given, say what input is missing."
)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


class MetaSparkProvider(LLMProvider):
    name = "meta-spark-live"

    def __init__(self, model: str = "muse-spark-1.3", timeout: int = 90):
        self.model = model
        self.timeout = timeout
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": max_tokens,
            "reasoning_effort": "minimal",
            "temperature": 0.3,
        }
        req = urllib.request.Request(
            "https://api.meta.ai/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        add_surrogate_to_request, read_json_response = _load_surrogate()
        add_surrogate_to_request(
            req, "custom.meta-model-api-2", allowed_hosts=["api.meta.ai"])
        t0 = time.time()
        try:
            with urllib.request.build_opener(NoRedirect()).open(
                    req, timeout=self.timeout) as resp:
                payload = read_json_response(resp)
        except Exception as exc:
            raise RuntimeError(f"live brain call failed: {type(exc).__name__}: {exc}")
        if "error" in payload:
            raise RuntimeError(f"live brain API error: {payload['error']}")
        choice = payload["choices"][0]
        text = (choice["message"].get("content") or "").strip()
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
