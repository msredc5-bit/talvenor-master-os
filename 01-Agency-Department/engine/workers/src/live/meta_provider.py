"""Layer 1 — MetaSparkProvider: the REAL brain (Muse Spark via Meta Model API).

Same LLMProvider interface as MockLLMProvider, so swapping is a config
change (boss_run.py --live). Two key paths, in order:

1. META_API_KEY environment variable — the PC path. Boss sets his own
   Muse Spark key on his PC (Windows: setx META_API_KEY "paste-key-here");
   the key is never in a file, an argument, or a log. This is the path
   the Talvenor Master OS PC package uses (see 00-CEO-Core/PROVIDERS-SETUP.md
   and 00-CEO-Core/config.json providers.meta.env_var).
2. The registered connector credential (custom.meta-model-api-2) via the
   Secure Vault surrogate — the Muse VM path. Used only when no env var
   is set. The real key never appears in a file, env var, argument, or log.

Muse Spark is PAID / credit-based: it is a PRODUCTION-brain option only.
It is never in the free-only dev allowlist (00-CEO-Core/free_only_guard.py
rejects it in development mode) and never the dev brain.

One request per complete() call, no retries, no redirects. A failed call
raises; the worker base catches it and marks the worker failed — the day
never crashes.

Boss approved the real brain 2026-11-06 00:18 (from his $150 credit).
First live verification 2026-11-06 00:19 TIMED OUT after 60s ($0 spent,
key validity unproven) — the provider code below is ready, the key path
is NOT yet proven; retry only on Boss's word. Second probe 2026-11-20
01:44 failed (tunnel 403, api.meta.ai unreachable from this VM), $0
spent, key validity still unproven — no further live retry from this VM.
"""
from __future__ import annotations

import json
import os
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
            "run on the Muse VM, or set META_API_KEY in the environment "
            "(PC path, never in a file)"
        ) from exc
    return add_surrogate_to_request, read_json_response

SYSTEM_PROMPT = (
    "You are a specialist worker inside CEO-OS, a personal CEO agent "
    "for a solo founder. Follow the brief exactly. Be concise and concrete. "
    "Never invent numbers, clients, prices, or results — if a number is "
    "needed and not given, say what input is missing."
)

ENV_VAR = "META_API_KEY"
ENDPOINT = "https://api.meta.ai/v1/chat/completions"


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
        api_key = os.environ.get(ENV_VAR)
        if api_key:
            # PC path: key from the environment (never a file).
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json",
                         "Authorization": "Bearer " + api_key},
                method="POST",
            )
            try:
                with urllib.request.build_opener(NoRedirect()).open(
                        req, timeout=self.timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except Exception as exc:
                raise RuntimeError(
                    f"live brain call failed: {type(exc).__name__}: {exc}")
        else:
            # Muse VM path: key via the connector Secure Vault surrogate.
            req = urllib.request.Request(
                ENDPOINT,
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                add_surrogate_to_request, read_json_response = (
                    _load_surrogate())
            except Exception as exc:  # noqa: BLE001 — no surrogate, no key
                raise RuntimeError(
                    "Muse Spark API key missing: set " + ENV_VAR + " in the "
                    "environment (never in a file) — or run on the Muse VM "
                    "where the Meta connector supplies the key. "
                    f"Surrogate unavailable: {type(exc).__name__}: {exc}"
                ) from exc
            add_surrogate_to_request(
                req, "custom.meta-model-api-2", allowed_hosts=["api.meta.ai"])
            try:
                with urllib.request.build_opener(NoRedirect()).open(
                        req, timeout=self.timeout) as resp:
                    payload = read_json_response(resp)
            except Exception as exc:
                raise RuntimeError(
                    f"live brain call failed: {type(exc).__name__}: {exc}")
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
