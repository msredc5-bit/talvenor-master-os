"""Layer 1 — OllamaProvider: a local Ollama model on Boss's PC.

Same LLMProvider interface as GeminiProvider — complete(prompt, *,
max_tokens) -> str — so switching is only a config matter
(00-CEO-Core/config.json's providers section).

Ollama is the LOCAL model server (http://localhost:11434): no API key,
no account, no billing, $0. Data never leaves Boss's PC. Any model
Ollama serves works — Gemma 4, Qwen, ... — just by naming it; there
is no separate "Gemma 4 adapter", Ollama IS the adapter and the model
is the name. The model must be pulled first:

    ollama pull qwen2.5-coder:1.5b

Honest limit (verified 2026-11-26): gemma4:12b does NOT run on an
8 GB PC — llama-server fails to initialize (out of memory) and
Claude Code reports the model "not changed". The small coder model
fits easily: ollama pull qwen2.5-coder:1.5b (~1 GB, ~2.5 GB memory). The provider never picks a model by itself — the name comes
from config (development_brain.model / fallback_chain entry
"ollama:<model>") or the BRAIN_MODEL env var.

Endpoint: http://localhost:11434/api/chat (Ollama native API, official).
Set OLLAMA_HOST to point at another Ollama server; the default is
localhost. If Ollama is not running, complete() raises a clear error
naming the fix instead of failing silently.
Stdlib only — no pip.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

from src.contracts.llm import LLMProvider  # noqa: E402

SYSTEM_PROMPT = (
    "You are a specialist worker inside CEO-OS, a personal CEO agent "
    "for a solo founder. Follow the brief exactly. Be concise and concrete. "
    "Never invent numbers, clients, prices, or results — if a number is "
    "needed and not given, say what input is missing."
)

ENV_VAR = "OLLAMA_HOST"
DEFAULT_HOST = "http://localhost:11434"
# F1: was gemma4:12b — cannot run on an 8 GB PC (OOM, verified twice).
DEFAULT_MODEL = "qwen2.5-coder:1.5b"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def _host():
    """Ollama server base URL — OLLAMA_HOST, or localhost by default."""
    return os.environ.get(ENV_VAR, "").strip() or DEFAULT_HOST


def list_local_models(host=None):
    """Model names installed on the local Ollama server (/api/tags).

    Raises on any failure (server down, bad response) — the caller
    decides what to do. No key is needed, ever.
    """
    base = (host or _host()).rstrip("/")
    req = urllib.request.Request(base + "/api/tags", method="GET")
    with urllib.request.build_opener(NoRedirect()).open(
            req, timeout=10) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    names = []
    for entry in (payload.get("models") or []):
        if isinstance(entry, dict) and entry.get("name"):
            names.append(str(entry["name"]))
    return names


class OllamaProvider(LLMProvider):
    name = "ollama-live"

    # timeout is 300s (5 min): a cold local model load on an 8 GB PC
    # can take minutes. It does NOT make gemma4:12b run — verified
    # 2026-11-26 it cannot start at all on 8 GB (llama-server init
    # crash, out of memory). It gives loadable models a fair chance.
    def __init__(self, model: str = DEFAULT_MODEL, timeout: int = 300):
        self.model = model
        self.timeout = timeout
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def complete(self, prompt: str, *, max_tokens: int = 500) -> str:
        host = _host().rstrip("/")
        body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.3},
        }
        req = urllib.request.Request(
            host + "/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = time.time()
        try:
            with urllib.request.build_opener(NoRedirect()).open(
                    req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"live brain call failed: HTTP {exc.code}: "
                f"{type(exc).__name__}: {exc}")
        except urllib.error.URLError as exc:
            # Connection refused / server down: the fix is starting
            # Ollama and pulling the model — say so plainly.
            raise RuntimeError(
                f"Ollama is not reachable at {host} — start Ollama on "
                f"this PC (it starts by itself after install, or run "
                f"'ollama serve') and pull the model ('ollama pull "
                f"{self.model}'). {type(exc).__name__}: {exc}")
        except Exception as exc:
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
            text = (payload["message"].get("content") or "").strip()
        except (KeyError, AttributeError, TypeError) as exc:
            raise RuntimeError(
                f"live brain API error: unexpected response shape: {exc}")
        self.calls += 1
        self.prompt_tokens += int(payload.get("prompt_eval_count") or 0)
        self.completion_tokens += int(payload.get("eval_count") or 0)
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
