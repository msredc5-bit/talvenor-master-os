"""Live Brain adapter — Phase 10. The adapter that takes the brain from mock to real.

Job: when the Main CEO Bot's brain is "live" in config, this adapter
makes the real complete() call via the vendored MetaSparkProvider
(Muse Spark, api.meta.ai). If any call fails (no credential, timeout,
403/401, non-200, API error) the adapter never silently pretends to be
live — LOUD fallback: it writes the reason to stderr and returns a
draft from the department's own mock brain. One call = one attempt, never
a retry loop.

Credential: the key is never in this file. MetaSparkProvider takes the key
from the META_API_KEY environment variable (Boss's PC) or via the
connector Secure Vault surrogate (custom.meta-model-api-2,
dynamic_credentials) on the Muse VM — the real key never appears in a
file, argument, or log.
Adapter construction performs no network I/O (a provider only stores
model/timeout) — network happens only in a complete() call.

Interface: the same as the providers — complete(prompt, *, max_tokens) -> str,
health() -> dict. Both departments' mocks work as fallback
(agency MockLLMProvider, content MockLLM) — the Chiefs' call sites
do not change. The body (office, worker, tool, dashboard, gate) is never
touched — only the brain's thinking goes live.

Phase 11 — provider chain: the adapter is now not one provider; it tries
providers one after another per config's fallback_chain
(openrouter -> meta -> ... -> mock). Every provider has the same interface
— complete(prompt, *, max_tokens) -> str — so any vendor's
any chat model can be fitted, just by changing the name. The provider registry
is below (PROVIDER_MODULES): module + class + default model. The key rule is
the same in every provider file — from an env var (Meta only via the connector
surrogate; Ollama needs no key at all). No provider in the chain does network at construction;
the key is read only in complete().

Stdlib only (+ dynamic_credentials, connector helper) — no pip.

Phase 1 — local-first development brain (2026-11-24): the adapter gains a
mode, "live" (default) or "development". In development mode the FREE-ONLY
GUARD (free_only_guard.py, same directory) is enforced IN THE CALL PATH —
adapter.complete() checks every provider against the allowlist BEFORE
calling it, never a paid model, never a silent paid fallback; a blocked
provider is logged ("blocked_free_only") and skipped. An HTTP 429 /
rate-limit error in development mode is a HARD STOP: no further provider
is tried, the call is logged ("rate_limited_stop"), the adapter records
rate_limited=True, and the loud mock fallback runs. Every call (success,
error, blocked, rate-limited) is logged with provider / model / status /
error / usage to logs/dev_brain_calls.jsonl. In mode "live" the Phase 10/11
behavior is unchanged (chain walk, loud fallback) except for the added
health keys ("brain_kind", "rate_limited", and "guard" in development
mode). The development brain is test-data-only and is never the
production brain (production stays locked behind its own Boss approval).
"""

import importlib
import os
import sys

CEO_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_OS_DIR = os.path.dirname(CEO_CORE_DIR)
AGENCY_WORKERS_DIR = os.path.join(
    MASTER_OS_DIR, "01-Agency-Department", "engine", "workers")

# Phase 1 — free-only guard (same directory). Imported with a fallback
# that puts 00-CEO-Core on sys.path, so this module still imports
# standalone (python3 -I) and when loaded by file path from brain.py.
try:
    from free_only_guard import (  # noqa: E402
        FreeOnlyViolation, check_call, is_rate_limit_error, log_call)
except ImportError:  # pragma: no cover — path fallback
    if CEO_CORE_DIR not in sys.path:
        sys.path.insert(0, CEO_CORE_DIR)
    from free_only_guard import (  # noqa: E402
        FreeOnlyViolation, check_call, is_rate_limit_error, log_call)

MODEL = "muse-spark-1.3"

# Phase 11 — provider registry: key -> (module, class).
# The modules live in 01-Agency-Department/engine/workers/src/live/,
# loaded as "src.live.<name>_provider" via _load_module.
# The key rule is written in each provider file (env var; Meta:
# META_API_KEY on a PC, or the connector surrogate on the Muse VM).
# The same information lives declaratively in config.json's providers
# section — check_providers.py matches the two.
PROVIDER_MODULES = {
    "meta": ("src.live.meta_provider", "MetaSparkProvider"),
    "openai": ("src.live.openai_provider", "OpenAIProvider"),
    "anthropic": ("src.live.anthropic_provider", "AnthropicProvider"),
    "gemini": ("src.live.gemini_provider", "GeminiProvider"),
    "kimi": ("src.live.kimi_provider", "KimiProvider"),
    "grok": ("src.live.grok_provider", "GrokProvider"),
    "openrouter": ("src.live.openrouter_provider", "OpenRouterProvider"),
    "ollama": ("src.live.ollama_provider", "OllamaProvider"),
}

# Each provider's default model — used when config gives no model.
DEFAULT_MODELS = {
    "meta": "muse-spark-1.3",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-3.5-flash-lite",
    "kimi": "kimi-k2.5",
    "grok": "grok-4",
    "openrouter": "openrouter/free",
    "ollama": "qwen2.5-coder:1.5b",  # F1: gemma4:12b cannot run on an 8 GB PC (OOM, verified twice) — removed from the dev chain.
}


def load_provider(name, model=None, timeout=None):
    """Construct one provider — no network I/O.

    name: registry key ("meta" | "openai" | ... ). model: if None,
    DEFAULT_MODELS[name]. Unknown name -> ValueError.
    timeout: seconds for one live call. None means the per-provider
    default — 300s (5 min) for Ollama (a cold local model load on an
    8 GB PC can take minutes), 90s for every cloud provider.
    """
    key = str(name).strip().lower()
    if key not in PROVIDER_MODULES:
        raise ValueError(
            f"Unknown provider {name!r}. Known: {sorted(PROVIDER_MODULES)}")
    if timeout is None:
        timeout = 300 if key == "ollama" else 90
    module_name, class_name = PROVIDER_MODULES[key]
    mod = _load_module(AGENCY_WORKERS_DIR, module_name)
    cls = getattr(mod, class_name)
    return cls(model=model or DEFAULT_MODELS[key], timeout=timeout)


def build_provider_chain(cfg, timeout=None, mode="live"):
    """Build the live provider chain from config — no network I/O.

    timeout: seconds for one live call; None means the per-provider
    default (300s Ollama, 90s cloud) — see load_provider.

    cfg: config.json's dict (or {} — then the default ["meta"]).
    Each fallback_chain entry is "provider" or "provider:model"
    (the model may contain ":", e.g. openrouter:nvidia/...:free — so
    split on the first ":"). A "mock" entry is the end of the chain — it is not a
    provider, it is the adapter's implicit fallback, so it is skipped here.
    An empty chain raises RuntimeError (no live provider).
    If config's providers[name].enabled == false, that entry is skipped
    (2026-11-21 — the flag used to be decorative: openrouter was tried first
    in the chain even while disabled). If there is no providers section
    or the name is absent, the entry runs (the old behaviour) — only an
    explicit false skips it. Nothing changes for the mock brain.

    mode: "live" (default) or "development" (Phase 1). In development
    mode the `enabled` flag is IGNORED entirely — the
    development_brain.fallback_chain is an explicit, Boss-approved
    selection for dev testing only, and the `enabled` flags govern the
    PRODUCTION chain only. The dev-mode gate is the free-only allowlist:
    each entry (provider + resolved model, where the resolved model is
    the entry's model or DEFAULT_MODELS[provider]) is validated with
    check_call() and the FIRST non-allowlisted entry raises
    FreeOnlyViolation (fail-closed, before any provider is built).
    """
    if mode not in ("live", "development"):
        raise ValueError(
            f"Unknown brain mode {mode!r}. Allowed: ['live', 'development']")
    if not isinstance(cfg, dict):
        cfg = {}
    chain_spec = cfg.get("fallback_chain") or [cfg.get("brain_provider", "meta")]
    providers_cfg = cfg.get("providers") or {}
    providers = []
    for entry in chain_spec:
        if not isinstance(entry, str):
            raise ValueError(
                f"fallback_chain entry must be a string, got {entry!r}")
        name, _sep, model = entry.partition(":")
        name = name.strip().lower()
        if name == "mock":
            continue
        if mode == "live":
            entry_cfg = providers_cfg.get(name)
            if isinstance(entry_cfg, dict) and entry_cfg.get("enabled") is False:
                continue  # disabled provider — dropped from the chain
        if mode == "development":
            # Dev mode ignores `enabled`; the allowlist is the gate.
            resolved = model.strip() or DEFAULT_MODELS.get(name)
            check_call(name, resolved)
        providers.append(
            load_provider(name, model.strip() or None, timeout=timeout))
    if not providers:
        raise RuntimeError(
            "No live provider in fallback_chain — enable at least one "
            "provider (e.g. \"meta\" or \"openrouter\") or keep "
            "\"brain\": \"mock\" in 00-CEO-Core/config.json.")
    return providers


def _load_module(workers_dir, dotted_name):
    """A copy of brain.py's _load_module (here to avoid a circular import).

    The vendored trees share a top-level `src` package, so in one
    process only one department's `src` can exist at a time. If the wanted
    dir's `src` is not loaded, the stale `src` is evicted and the new one loaded.
    """
    src_pkg = sys.modules.get("src")
    if src_pkg is not None:
        loaded = [os.path.normpath(p)
                  for p in (getattr(src_pkg, "__path__", []) or [])]
        wanted = os.path.normpath(os.path.join(workers_dir, "src"))
        if wanted not in loaded:
            for name in [n for n in list(sys.modules)
                         if n == "src" or n.startswith("src.")]:
                del sys.modules[name]
    if workers_dir in sys.path:
        sys.path.remove(workers_dir)
    sys.path.insert(0, workers_dir)
    return importlib.import_module(dotted_name)


def _provider_key(provider):
    """Registry key ("gemini", "openrouter", ...) for a provider object.

    Reads provider.name (e.g. "gemini-live" -> "gemini"); falls back to
    the class name ("GeminiProvider" -> "gemini", "MetaSparkProvider"
    -> "meta"). Never raises — unknown shapes yield "unknown", which
    the free-only guard rejects fail-closed in development mode.
    """
    name = str(getattr(provider, "name", "") or "").strip().lower()
    if name.endswith("-live"):
        name = name[: -len("-live")]
    if name:
        return name
    cls = type(provider).__name__.lower()
    if cls.endswith("provider"):
        cls = cls[: -len("provider")]
    if cls == "metaspark":
        return "meta"
    return cls or "unknown"


def _provider_model(provider, key):
    """The model id a provider object would call with: its own .model,
    or DEFAULT_MODELS[key] when it has none."""
    model = getattr(provider, "model", None)
    if isinstance(model, str) and model.strip():
        return model
    return DEFAULT_MODELS.get(key)


class LiveBrainAdapter:
    """Live brain + loud mock fallback — one interface, two modes.

    mode: "live" (the last call succeeded live) or "mock-fallback" (the last call
    failed live and a mock draft was returned). last_failure holds the failure's
    reason — never empty/suppressed. brain_mode ("live" | "development",
    health()["brain_kind"]) is the separate Phase 1 construction mode:
    "development" enforces the free-only guard in complete().

    Phase 11: the adapter now takes a provider CHAIN — complete() tries each
    provider in the chain one after another; only if all fail does it
    fall back to mock. Giving one live_provider makes chain=[that one] — old
    call sites unchanged.
    """

    name = "live-brain-adapter"

    def __init__(self, mock_brain, live_provider=None, live_providers=None,
                 timeout=90, mode="live"):
        """mock_brain: the department's own mock (for fallback).
        live_provider: one provider can be injected (in tests);
        live_providers: if a chain (list) is given, that runs; if neither is given,
        the vendored MetaSparkProvider is constructed (no network I/O).
        mode: "live" (default — Phase 10/11 behavior) or "development"
        (Phase 1 — the free-only guard is enforced in complete(), and a
        429 / rate-limit error is a hard stop). self.mode stays the
        runtime state ("live" / "mock-fallback"); the brain kind lives
        in self.brain_mode / health()["brain_kind"]."""
        if mode not in ("live", "development"):
            raise ValueError(
                f"Unknown brain mode {mode!r}. "
                "Allowed: ['live', 'development']")
        self.brain_mode = mode
        self.brain_kind = mode
        self.mock_brain = mock_brain
        if live_providers is not None:
            if not live_providers:
                raise ValueError("live_providers chain is empty")
            self.live_chain = list(live_providers)
        elif live_provider is not None:
            self.live_chain = [live_provider]
        else:
            mod = _load_module(AGENCY_WORKERS_DIR, "src.live.meta_provider")
            self.live_chain = [mod.MetaSparkProvider(model=MODEL,
                                                     timeout=timeout)]
        self.live = self.live_chain[0]
        self.mode = "live"
        self.last_failure = None
        self.rate_limited = False
        self.calls = 0
        self.live_calls = 0
        self.fallback_calls = 0

    def complete(self, prompt, *, max_tokens=500):
        """One attempt per provider: walks the chain and takes the first successful
        answer; if all fail, LOUD fallback to mock.

        Development mode: BEFORE each provider call the free-only guard
        (check_call) runs on that provider's registry key + model — a
        blocked provider is never called (0 calls on it), is logged as
        "blocked_free_only", and counts as a provider failure. A
        rate-limit error (is_rate_limit_error) is a HARD STOP: no
        remaining provider is tried, the call is logged as
        "rate_limited_stop", rate_limited is set, and the loud mock
        fallback runs with last_failure naming the stop. In live mode
        the chain walk is unchanged (a 429 is logged as "error" and the
        next provider is tried, as before). Every attempt is logged
        (provider / model / status / error / usage)."""
        self.calls += 1
        errors = []
        dev = (self.brain_mode == "development")
        for provider in self.live_chain:
            pname = getattr(provider, "name", type(provider).__name__)
            pkey = _provider_key(provider)
            pmodel = _provider_model(provider, pkey)
            if dev:
                try:
                    check_call(pkey, pmodel)
                except FreeOnlyViolation as exc:
                    errors.append(f"{pname}: FreeOnlyViolation: {exc}")
                    log_call({"provider": pkey, "model": pmodel,
                              "status": "blocked_free_only",
                              "error": str(exc), "usage": None})
                    continue
            try:
                text = provider.complete(prompt, max_tokens=max_tokens)
            except Exception as exc:  # noqa: BLE001 — try the next provider
                if dev and is_rate_limit_error(exc):
                    errors.append(
                        f"{pname}: rate_limited_stop: "
                        f"{type(exc).__name__}: {exc}")
                    log_call({"provider": pkey, "model": pmodel,
                              "status": "rate_limited_stop",
                              "error": str(exc), "usage": None})
                    self.rate_limited = True
                    break  # HARD STOP — never try the next provider
                errors.append(f"{pname}: {type(exc).__name__}: {exc}")
                log_call({"provider": pkey, "model": pmodel,
                          "status": "error",
                          "error": str(exc), "usage": None})
                continue
            usage = None
            try:
                phealth = provider.health()
                if (isinstance(phealth, dict)
                        and phealth.get("total_tokens") is not None):
                    usage = {"total_tokens": phealth["total_tokens"]}
            except Exception:  # noqa: BLE001 — usage is best-effort only
                usage = None
            log_call({"provider": pkey, "model": pmodel,
                      "status": "ok", "error": None, "usage": usage})
            self.mode = "live"
            self.last_failure = None
            self.live_calls += 1
            self.live = provider
            return text
        reason = "; ".join(errors) if errors else "no live provider"
        self.last_failure = reason
        self.mode = "mock-fallback"
        self.fallback_calls += 1
        print(
            "[LIVE-BRAIN] LIVE FAILED ("
            f"{reason}) — falling back to MOCK draft. "
            "Live brain is NOT working; this output is a mock draft.",
            file=sys.stderr,
        )
        return self.mock_brain.complete(prompt)

    def health(self):
        """The adapter's true state — mode, call count, the last failure's reason."""
        try:
            mock_health = self.mock_brain.health()
        except Exception:  # noqa: BLE001 — mock health must never break the adapter
            mock_health = {"provider": "unknown"}
        result = {
            "provider": self.name,
            "model": getattr(self.live, "model", None),
            "providers": [getattr(p, "name", type(p).__name__)
                          for p in self.live_chain],
            "models": [getattr(p, "model", None)
                       for p in self.live_chain],
            "mode": self.mode,
            "brain_kind": self.brain_mode,
            "rate_limited": self.rate_limited,
            "ok": True,
            "calls": self.calls,
            "live_calls": self.live_calls,
            "fallback_calls": self.fallback_calls,
            "last_failure": self.last_failure,
            "mock_provider": mock_health.get("provider"),
        }
        if self.brain_mode == "development":
            result["guard"] = "free-only"
        return result


if __name__ == "__main__":
    # Manual check: the adapter constructs, no network call happens.
    # (complete() is not called — that is the live probe's job.)
    _mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
    _mock = _mod.MockLLMProvider(seed="master-os-phase1")
    adapter = LiveBrainAdapter(mock_brain=_mock)
    health = adapter.health()
    assert health["provider"] == "live-brain-adapter"
    assert health["mode"] == "live"
    assert health["brain_kind"] == "live"
    assert health["rate_limited"] is False
    assert health["calls"] == 0
    assert health["fallback_calls"] == 0
    assert health["last_failure"] is None
    assert "guard" not in health
    assert DEFAULT_MODELS["gemini"] == "gemini-3.5-flash-lite"
    print("live_brain: OK (adapter constructs, 0 calls, no network)")
