"""Brain — one switch for the office's LLM brain (Phase 6).

BrainFactory reads the "brain" flag from 00-CEO-Core/config.json:
  "mock" (DEFAULT, $0, drafts only) or "live" (LiveBrainAdapter).

The two departments' mocks have DIFFERENT shapes, and the factory
honours each one instead of forcing a single interface on them:
  - agency  -> vendored src.mock.provider.MockLLMProvider
               complete(prompt, *, max_tokens=500) -> str
  - content -> vendored src.workers.base.MockLLM
               complete(prompt) -> str
  - digital-product -> the agency mock tree, with its own Phase 2 seed
    ("master-os-phase2") — it used to raise ValueError, and the Products Chief
    quietly used the agency seed.
Both satisfy the only contract the workers actually call —
complete(prompt) -> str and health() -> dict — so each Chief keeps
its existing call sites untouched: it just asks the factory for its
own department's brain. Flipping the config flag swaps the brain for
both Chiefs at once; the default stays mock.

LIVE BRAIN — Phase 10 (wired via live_brain.py):
  - The live call is the VENDORED MetaSparkProvider
    (01-Agency-Department/engine/workers/src/live/meta_provider.py),
    wrapped by LiveBrainAdapter (00-CEO-Core/live_brain.py). Its key
    comes from the META_API_KEY environment variable (Boss's PC) or
    via the connector Secure Vault (custom.meta-model-api-2,
    dynamic_credentials surrogate) on the Muse VM — the key never
    appears in any file, argument, or log.
  - If a live call fails (no credential, timeout, 403/401, API
    error), the adapter falls back LOUDLY to the department's own
    mock brain (writing the reason to stderr) — never silently pretends
    live, never retries in a loop (one attempt per call).
  - Constructing the adapter performs NO network I/O (verified:
    import + construct, 0 calls). Only complete() touches the
    network, and only when config "brain" is "live".
  - Live probe result: see config.json honest_status.phases
    phase_10_live_brain — PROVEN LIVE only after a successful
    probe; otherwise the flag stays "mock" and the entry records
    the exact blocker.

LIVE BRAIN — Phase 11 (provider chain, same adapter):
  - The adapter now takes a CHAIN of providers from config.json
    "fallback_chain" (e.g. ["openrouter", "meta", "mock"]) and tries
    them one after another; only if all fail does it fall back to
    the department mock. Any vendor's any chat model works — same
    complete() interface, only the name changes.
  - Providers live in 01-Agency-Department/engine/workers/src/live/:
    meta (connector key), openai, anthropic, gemini, kimi, grok,
    openrouter (each its own env var, never in a file), ollama
    (local server, no key at all). The model
    name now comes from config ("brain_model" or the chain entry
    "provider:model") — MetaSparkProvider is no longer pinned to
    one model by the factory.
  - Default stays "mock". A temp config {"brain": "live"} with no
    providers section still builds the old default chain ["meta"].

DEV / PROD BRAIN SEPARATION — local-first Phase 1 (2026-11-24):
  - Three modes: "mock" (default, $0, drafts only), "development"
    (local free-tier testing only), "live" (production Live Brain).
  - "development" reads ONLY config.json "development_brain"
    (free_only, test_data_only, its own fallback_chain of free-tier
    models) and builds the adapter with mode="development".
    BRAIN_PROVIDER / BRAIN_MODEL env vars override the dev
    provider/model without editing config (still free-only gated).
  - "live" reads ONLY config.json "production_brain" and is LOCKED
    unless "production_brain.unlocked" is explicitly true — a Boss
    decision, never a dev change. With the lock in place, asking for
    "live" raises RuntimeError instead of building anything.
  - A dev brain can NEVER become the production brain: different
    config blocks, different mode string, and production requires
    the explicit unlocked flag. The top-level "brain" flag stays
    "mock" and "fallback_chain" stays the production chain (unused
    while locked).

Stdlib only. No network, no spend, no secrets in this file.
"""

import importlib
import json
import os
import sys

CEO_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_OS_DIR = os.path.dirname(CEO_CORE_DIR)
CONFIG_PATH = os.path.join(CEO_CORE_DIR, "config.json")

AGENCY_WORKERS_DIR = os.path.join(
    MASTER_OS_DIR, "01-Agency-Department", "engine", "workers")
CONTENT_WORKERS_DIR = os.path.join(
    MASTER_OS_DIR, "03-Content-Creation-Department", "engine", "workers")

BRAIN_MODES = ("mock", "development", "live")
DEFAULT_BRAIN = "mock"

# Free default model per dev provider — used only when BRAIN_PROVIDER
# switches provider without BRAIN_MODEL. Only gemini/openrouter/ollama
# can ever pass the free-only guard, so this map is complete for dev mode.
_DEV_DEFAULT_MODELS = {"gemini": "gemini-3.5-flash-lite",
                       "openrouter": "openrouter/free",
                       "ollama": "gemma4:12b"}

# The seed each department's mock has always used — kept so flipping
# the flag back to mock reproduces exactly the old drafts.
_AGENCY_MOCK_SEED = "master-os-phase1"
_CONTENT_MOCK_SEED = "master-os-phase3"
# Digital Product's own seed (Phase 2) — get_brain(
# "digital-product") used to raise ValueError, and the Products Chief quietly
# used the agency seed (master-os-phase1). Now digital-product has its own
# branch: the agency mock still runs (the Products Chief's workers are vendored
# in the agency tree), but the seed is different — so the drafts no longer
# look like the agency's.
_DIGITAL_PRODUCT_MOCK_SEED = "master-os-phase2"


def _load_module(workers_dir, dotted_name):
    """Import a module from a vendored workers tree.

    Both vendored trees expose a top-level `src` package, so in one
    process only one department's `src` can live in sys.modules at a
    time (verified: importing both Chiefs in one process fails with
    "No module named 'src.creator_workers'"). If a stale `src` from
    the other department is loaded, evict it first — safe here,
    because Chiefs bind their worker classes at import time and never
    re-import `src.*` inside handle_task.
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
    # Always FIRST: the other department's workers dir may already be
    # on sys.path ahead of this one, and `src` would resolve to it.
    sys.path.insert(0, workers_dir)
    return importlib.import_module(dotted_name)


class BrainFactory:
    """Return the office brain for a department, per config.json."""

    @staticmethod
    def get_brain_mode(config_path=CONFIG_PATH):
        """"mock", "development" or "live" from config.json — "mock" if
        missing/unreadable."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return DEFAULT_BRAIN
        mode = str(cfg.get("brain", DEFAULT_BRAIN)).lower()
        if mode not in BRAIN_MODES:
            raise ValueError(
                f"Unknown brain mode {mode!r} in {config_path}. "
                f"Allowed: {list(BRAIN_MODES)}")
        return mode

    @staticmethod
    def get_brain(department, seed=None, config_path=CONFIG_PATH):
        """The brain object for `department` ("agency" | "digital-product"
        | "content").

        Mock (default): that department's own vendored mock, seeded as
        before — each Chief can use the result exactly as it used its
        mock before. Digital-product uses the agency mock tree (its
        workers are vendored there) with its own Phase 2 seed.
        Development: LiveBrainAdapter in mode="development", built
        from config.json "development_brain" (free-tier models only,
        test data only) — never the production brain.
        Live: LOCKED unless config.json "production_brain.unlocked"
        is true (a Boss decision); otherwise raises RuntimeError.
        When unlocked, LiveBrainAdapter wrapping the provider chain
        from config.json "fallback_chain" (same adapter serves all
        departments — its complete(prompt, *, max_tokens) accepts the
        positional call both worker bases make; on live failure of
        every provider it falls back LOUDLY to that department's own
        mock).
        """
        mode = BrainFactory.get_brain_mode(config_path)
        if mode == "live":
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cfg = {}
            if not cfg.get("production_brain", {}).get("unlocked") is True:
                raise RuntimeError(
                    "Production Live Brain is LOCKED: "
                    "\"production_brain.unlocked\" is not true in "
                    f"{config_path}. Use \"development\" mode for local "
                    "free-tier testing. Unlocking the production Live "
                    "Brain is a Boss decision — it is never unlocked "
                    "by a dev change."
                )
            return BrainFactory._live_brain(department, config_path=config_path)
        if mode == "development":
            return BrainFactory._development_brain(
                department, config_path=config_path)
        if department == "agency":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            return mod.MockLLMProvider(seed=seed or _AGENCY_MOCK_SEED)
        if department == "digital-product":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            return mod.MockLLMProvider(
                seed=seed or _DIGITAL_PRODUCT_MOCK_SEED)
        if department == "content":
            mod = _load_module(CONTENT_WORKERS_DIR, "src.workers.base")
            return mod.MockLLM(seed=seed or _CONTENT_MOCK_SEED)
        raise ValueError(
            f"Unknown department: {department!r}. Known: ['agency', "
            "'digital-product', 'content']")

    @staticmethod
    def _development_brain(department, config_path=CONFIG_PATH):
        """Construct the local-first Phase 1 development adapter — NO
        network call here.

        Reads ONLY config.json "development_brain" (free-tier models,
        test data only) and builds the provider chain from its own
        fallback_chain — never the production "fallback_chain" and
        never the production brain. Returns LiveBrainAdapter with
        mode="development". Construction only stores model/timeout;
        each provider's key is fetched only when complete() is called
        (env var only — never a file). A dev brain can never become
        the production brain: different config block, different mode
        string, and production requires the explicit unlocked flag.

        Env override (no JSON edit needed): BRAIN_PROVIDER and
        BRAIN_MODEL win over config's provider/model — the override
        becomes the first chain entry, the config chain stays as
        fallback. The free-only guard still applies
        (build_provider_chain validates every entry), so a paid
        provider or a non-free model here raises FreeOnlyViolation
        instead of being called.
        """
        if department == "agency":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            mock = mod.MockLLMProvider(seed=_AGENCY_MOCK_SEED)
        elif department == "digital-product":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            mock = mod.MockLLMProvider(seed=_DIGITAL_PRODUCT_MOCK_SEED)
        elif department == "content":
            mod = _load_module(CONTENT_WORKERS_DIR, "src.workers.base")
            mock = mod.MockLLM(seed=_CONTENT_MOCK_SEED)
        else:
            raise ValueError(
                f"Unknown department: {department!r}. "
                "Known: ['agency', 'digital-product', 'content']")
        try:
            if CEO_CORE_DIR not in sys.path:
                sys.path.insert(0, CEO_CORE_DIR)
            from live_brain import (  # noqa: E402
                LiveBrainAdapter, build_provider_chain)
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cfg = {}
            dev = cfg.get("development_brain")
            if not isinstance(dev, dict):
                raise RuntimeError(
                    "Development brain is not configured: "
                    "\"development_brain\" is missing from "
                    f"{config_path}.")
            # Env override: BRAIN_PROVIDER / BRAIN_MODEL win over
            # config — no JSON edit needed to switch the dev brain.
            # The free-only guard still gates every entry (a paid
            # provider or non-free model raises FreeOnlyViolation).
            env_provider = os.environ.get(
                "BRAIN_PROVIDER", "").strip().lower()
            env_model = os.environ.get("BRAIN_MODEL", "").strip()
            config_provider = str(
                dev.get("provider", "gemini")).strip().lower()
            config_model = str(dev.get("model", "")).strip()
            if env_provider and env_provider != config_provider:
                # The config model belongs to the config provider —
                # it must not be carried across to another provider
                # (openrouter:gemini-3.5-flash-lite would be rejected
                # by the free-only guard). Use the provider's free
                # default instead.
                provider = env_provider
                model = env_model or _DEV_DEFAULT_MODELS.get(provider, "")
            else:
                provider = env_provider or config_provider
                model = env_model or config_model
            chain_entries = [str(e) for e in
                             (dev.get("fallback_chain") or [])]
            if env_provider or env_model:
                primary = f"{provider}:{model}" if model else provider
                chain_entries = [primary] + [
                    e for e in chain_entries if e != primary]
            chain = build_provider_chain(
                {"fallback_chain": chain_entries,
                 "providers": cfg.get("providers", {})},
                mode="development")
            return LiveBrainAdapter(
                mock_brain=mock, live_providers=chain, mode="development")
        except Exception as exc:  # noqa: BLE001 — re-raised as a clear error
            # A free-only violation is a fail-closed guard decision, not
            # a configuration error — propagate it unwrapped so callers
            # see FreeOnlyViolation itself (check_providers §8(h)).
            # CEO_CORE_DIR is on sys.path by now (inserted above before
            # the live_brain import), so this import resolves.
            try:
                from free_only_guard import (  # noqa: PLC0415
                    FreeOnlyViolation)
            except Exception:  # noqa: BLE001 — guard module missing
                FreeOnlyViolation = None
            if (FreeOnlyViolation is not None
                    and isinstance(exc, FreeOnlyViolation)):
                raise
            raise RuntimeError(
                "Development brain is not configured: the development "
                "adapter could not be constructed in this "
                f"environment ({type(exc).__name__}: {exc}). Keys come "
                "ONLY from environment variables — a key is never "
                "stored in a file. Set \"brain\": \"mock\" in "
                "00-CEO-Core/config.json to keep drafting at $0."
            ) from exc

    @staticmethod
    def _live_brain(department, config_path=CONFIG_PATH):
        """Construct the Phase 10/11 live adapter — NO network call here.

        The adapter wraps the provider CHAIN from config.json
        "fallback_chain" (default ["meta"] — the Phase 10 behavior)
        and falls back LOUDLY to the department's own mock if every
        provider fails. Construction only stores model/timeout; each
        provider's key is fetched only when complete() is called
        (env var, or Meta's Secure Vault surrogate — never a file).
        Any failure to import/construct (e.g. an unknown provider in
        the chain) raises a clear error instead of attempting a call.
        """
        if department == "agency":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            mock = mod.MockLLMProvider(seed=_AGENCY_MOCK_SEED)
        elif department == "digital-product":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            mock = mod.MockLLMProvider(seed=_DIGITAL_PRODUCT_MOCK_SEED)
        elif department == "content":
            mod = _load_module(CONTENT_WORKERS_DIR, "src.workers.base")
            mock = mod.MockLLM(seed=_CONTENT_MOCK_SEED)
        else:
            raise ValueError(
                f"Unknown department: {department!r}. "
                "Known: ['agency', 'digital-product', 'content']")
        try:
            if CEO_CORE_DIR not in sys.path:
                sys.path.insert(0, CEO_CORE_DIR)
            from live_brain import (  # noqa: E402
                LiveBrainAdapter, build_provider_chain)
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cfg = {}
            chain = build_provider_chain(cfg)
            return LiveBrainAdapter(mock_brain=mock, live_providers=chain)
        except Exception as exc:  # noqa: BLE001 — re-raised as a clear error
            raise RuntimeError(
                "Live brain is not configured: the live adapter "
                "could not be constructed in this "
                f"environment ({type(exc).__name__}: {exc}). Keys come "
                "ONLY from environment variables (Meta: META_API_KEY, "
                "or the connector Secure Vault custom.meta-model-api-2 "
                "on the Muse VM) — a key is never "
                "stored in a file. Set \"brain\": \"mock\" in "
                "00-CEO-Core/config.json to keep drafting at $0."
            ) from exc


def get_brain(department, seed=None, config_path=CONFIG_PATH):
    """Module-level shortcut for BrainFactory.get_brain."""
    return BrainFactory.get_brain(department, seed=seed, config_path=config_path)


if __name__ == "__main__":
    mode = BrainFactory.get_brain_mode()
    print(f"brain mode (config): {mode}")
    agency_brain = BrainFactory.get_brain("agency")
    digital_brain = BrainFactory.get_brain("digital-product")
    content_brain = BrainFactory.get_brain("content")
    print("agency brain:", type(agency_brain).__name__,
          "| health:", agency_brain.health())
    print("digital-product brain:", type(digital_brain).__name__,
          "| health:", digital_brain.health())
    print("content brain:", type(content_brain).__name__,
          "| health:", content_brain.health())
    assert agency_brain.health()["calls"] == 0
    assert digital_brain.health()["calls"] == 0
    assert content_brain.health()["calls"] == 0
    print("brain.py: OK (all three mocks, 0 calls, $0)")
