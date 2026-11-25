"""Free-only guard — Phase 1 (local-first development).

Rules enforced here (and ONLY here — this module is the single source of
truth for what "free-only" means in development mode):

* Allowlist: Gemini free-tier models only — gemini-3.5-flash-lite,
  gemini-2.0-flash — and OpenRouter models that are
  free: any model id ending in ":free", or exactly "openrouter/free"
  (the auto-router). Ollama local models: ANY model id is free-only
  (the server runs on Boss's PC — no key, no account, no billing,
  $0; data never leaves the PC). Nothing else is free-only.
* Meta / OpenAI / Anthropic / Kimi / Grok are NEVER free-only: any model
  of theirs is a violation in development mode. An unknown provider name
  is also a violation (fail-closed).
* No paid fallback: a blocked or failed free provider is never silently
  replaced by a paid model. The adapter walks only allowlisted providers.
* HTTP 429 / rate limit = HARD STOP: the adapter must not try the next
  provider after a rate-limit error; it logs "rate_limited_stop" and
  falls back loudly to mock. A 429 is a free-cap boundary, never a bill.
* Test data only: free-tier models may receive test data only — never
  private client data (Gemini free tier uses data to improve products;
  OpenRouter free models are served by third parties). Ollama local
  models keep data on the PC, so they are the most private dev-brain
  option — still test data only until Boss says otherwise.
* Dev brain only: this guard applies to the development brain
  (LiveBrainAdapter mode="development"). The production brain is a
  separate path and stays locked behind its own Boss approval.

Stdlib only. No network, no keys, no secrets: log records carry only
provider / model / status / error / usage — a key or token is never
written (log_call drops any field whose name contains "key" or "token").
"""

import json
import os
import urllib.error
from datetime import datetime, timezone

FREE_ONLY_GUARD_VERSION = "1.0"

# Allowlisted free models, by provider (registry key, lower-cased).
# Gemini: the exact free-tier ids. OpenRouter: the canonical free id is
# listed here; the full rule (any id ending in ":free") lives in
# is_free_model() because free OpenRouter ids cannot be enumerated.
FREE_ONLY_MODELS = {
    "gemini": frozenset({
        "gemini-3.5-flash-lite",
        "gemini-2.0-flash",
    }),
    "openrouter": frozenset({"openrouter/free"}),
}

# Providers that are never free-only, whatever the model id says.
_NEVER_FREE_PROVIDERS = frozenset(
    {"meta", "openai", "anthropic", "kimi", "grok"})

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default call-log path; tests may monkeypatch this module attribute.
LOG_PATH = os.path.join(_MASTER_OS_DIR, "logs", "dev_brain_calls.jsonl")

# In-memory call log (same records as the JSONL file, newest last).
_CALL_LOG = []


class FreeOnlyViolation(Exception):
    """A provider/model is not free-only — it must never be called
    in development mode."""


def _normalize_provider(provider):
    """Registry key for a provider name: stripped, lower-cased, with a
    trailing "-live" (as in provider.name, e.g. "gemini-live") removed."""
    name = str(provider or "").strip().lower()
    if name.endswith("-live"):
        name = name[: -len("-live")]
    return name


def is_free_model(provider, model):
    """True only if (provider, model) is on the free-only allowlist.

    Gemini: model must be one of FREE_ONLY_MODELS["gemini"] (exact,
    case-sensitive ids). OpenRouter: model must end in ":free" (exact,
    lower-case suffix) or be exactly "openrouter/free". Ollama: any
    non-empty model id (local server, $0, no key). Every other
    provider — including meta / openai / anthropic / kimi / grok and any
    unknown name — is never free-only, so this returns False for them.
    """
    name = _normalize_provider(provider)
    if name in _NEVER_FREE_PROVIDERS:
        return False
    if not isinstance(model, str):
        return False
    model_id = model.strip()
    if not model_id:
        return False
    if name == "ollama":
        return True
    if name == "gemini":
        return model_id in FREE_ONLY_MODELS["gemini"]
    if name == "openrouter":
        return model_id == "openrouter/free" or model_id.endswith(":free")
    return False


def check_call(provider, model):
    """Allow a development-mode call, or raise FreeOnlyViolation.

    Normalizes the provider name (strip, lower-case); the model id is
    compared as given — ids are case-sensitive, except the ":free"
    suffix check, which is an exact lower-case match. Unknown providers
    fail closed. Returns True when the call is allowed.
    """
    name = _normalize_provider(provider)
    if not is_free_model(name, model):
        raise FreeOnlyViolation(
            f"provider {provider!r} model {model!r} is not free-only: "
            "paid models are never allowed in development mode "
            "(free-only allowlist: Gemini gemini-3.5-flash-lite / "
            "gemini-2.0-flash, OpenRouter models ending in ':free' or "
            "'openrouter/free', any Ollama local model).")
    return True


def is_rate_limit_error(exc):
    """True when an exception is a rate-limit / HTTP 429 error.

    True for: an HTTPError (or any exception) with code 429, "429" or
    "RESOURCE_EXHAUSTED" in the message, or a "rate limit" /
    "rate_limit" / "rate-limited" / "rate limited" / "too many requests"
    message (case-insensitive). Never True for auth errors (401 / 403 /
    invalid credentials) or timeouts.
    """
    if exc is None:
        return False
    code = getattr(exc, "code", None)
    if isinstance(code, int):
        if code == 429:
            return True
        if code in (400, 401, 403, 404):
            return False
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429
    if isinstance(exc, TimeoutError):
        return False
    try:
        message = str(exc)
    except Exception:  # noqa: BLE001 — str() must never break detection
        return False
    lowered = message.lower()
    if "invalid_api_key" in lowered or "invalid api key" in lowered:
        return False
    if "timed out" in lowered or "timeout" in lowered:
        return False
    return (
        "429" in lowered
        or "resource_exhausted" in lowered
        or "rate limit" in lowered
        or "rate_limit" in lowered
        or "rate-limited" in lowered
        or "rate limited" in lowered
        or "too many requests" in lowered
    )


def log_call(record):
    """Append one call record to the JSONL log and the in-memory log.

    record: dict with keys provider, model, status ("ok" | "error" |
    "rate_limited_stop" | "blocked_free_only"), error (str or None),
    usage (dict or None). A "ts" (ISO-8601 UTC) field is added. The
    file write is wrapped so logging can never break a call, and the
    logs/ directory is created if needed. No secrets are ever written:
    only the five listed keys are kept, and any field whose name
    contains "key" or "token" is dropped.
    """
    if not isinstance(record, dict):
        return
    safe = {}
    for key, value in record.items():
        lowered_key = str(key).lower()
        if "key" in lowered_key or "token" in lowered_key:
            continue  # never write a key/token field, whatever it holds
        if key in ("provider", "model", "status", "error", "usage"):
            safe[key] = value
    for key in ("provider", "model", "status", "error", "usage"):
        safe.setdefault(key, None)
    safe["ts"] = datetime.now(timezone.utc).isoformat().replace(
        "+00:00", "Z")
    _CALL_LOG.append(dict(safe))
    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(safe) + "\n")
    except Exception:  # noqa: BLE001 — logging must never break a call
        pass


def get_call_log():
    """The in-memory list of call records logged so far (same records
    as the JSONL file, newest last)."""
    return _CALL_LOG
