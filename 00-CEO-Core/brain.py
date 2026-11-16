"""Brain — one switch for the office's LLM brain (Phase 6).

BrainFactory reads the "brain" flag from 00-CEO-Core/config.json:
  "mock" (DEFAULT, $0, drafts only) or "live" (MetaSparkProvider).

The two departments' mocks have DIFFERENT shapes, and the factory
honours each one instead of forcing a single interface on them:
  - agency  -> vendored src.mock.provider.MockLLMProvider
               complete(prompt, *, max_tokens=500) -> str
  - content -> vendored src.workers.base.MockLLM
               complete(prompt) -> str
Both satisfy the only contract the workers actually call —
complete(prompt) -> str and health() -> dict — so each Chief keeps
its existing call sites untouched: it just asks the factory for its
own department's brain. Flipping the config flag swaps the brain for
both Chiefs at once; the default stays mock.

LIVE BRAIN — honest status (read before flipping the flag):
  - The live provider is the VENDORED MetaSparkProvider
    (01-Agency-Department/engine/workers/src/live/meta_provider.py).
    Its key comes ONLY via the connector Secure Vault
    (custom.meta-model-api-2, dynamic_credentials surrogate) — the
    key never appears in any file, env var, argument, or log.
  - Its first live verification TIMED OUT on 2026-11-06 ($0 spent,
    key validity UNPROVEN) — the key path is UNPROVEN.
  - Phase 6 makes NO live calls: constructing the provider performs
    no network I/O (verified: import + construct, 0 calls). Only a
    worker calling complete() would touch the network, and no Chief
    does that while "brain" is "mock".
  - "live" is therefore UNWIRED-UNTIL-FLIPPED: flip the flag only on
    Boss's explicit word, and only after a live verification proves
    the key path. If construction fails in this environment, the
    factory raises a clear error instead of attempting any call.

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

BRAIN_MODES = ("mock", "live")
DEFAULT_BRAIN = "mock"

# The seed each department's mock has always used — kept so flipping
# the flag back to mock reproduces exactly the old drafts.
_AGENCY_MOCK_SEED = "master-os-phase1"
_CONTENT_MOCK_SEED = "master-os-phase3"


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
        """"mock" or "live" from config.json — "mock" if missing/unreadable."""
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
        """The brain object for `department` ("agency" | "content").

        Mock (default): that department's own vendored mock, seeded as
        before — each Chief can use the result exactly as it used its
        mock before. Live: the vendored MetaSparkProvider (same object
        serves both departments — its complete(prompt, *, max_tokens)
        accepts the positional call both worker bases make).
        """
        if BrainFactory.get_brain_mode(config_path) == "live":
            return BrainFactory._live_brain()
        if department == "agency":
            mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
            return mod.MockLLMProvider(seed=seed or _AGENCY_MOCK_SEED)
        if department == "content":
            mod = _load_module(CONTENT_WORKERS_DIR, "src.workers.base")
            return mod.MockLLM(seed=seed or _CONTENT_MOCK_SEED)
        raise ValueError(
            f"Unknown department: {department!r}. Known: ['agency', 'content']")

    @staticmethod
    def _live_brain():
        """Construct the vendored live provider — NO network call here.

        Construction only stores model/timeout; the key is fetched by
        the Secure Vault surrogate only when complete() is called, and
        Phase 6 never calls it. Any failure to import/construct (e.g.
        the connector surrogate is absent) raises a clear error
        instead of attempting a call.
        """
        try:
            mod = _load_module(AGENCY_WORKERS_DIR, "src.live.meta_provider")
            provider = mod.MetaSparkProvider()
        except Exception as exc:  # noqa: BLE001 — re-raised as a clear error
            raise RuntimeError(
                "Live brain is not configured: the vendored "
                "MetaSparkProvider could not be constructed in this "
                f"environment ({type(exc).__name__}: {exc}). The live key "
                "comes ONLY via the connector Secure Vault "
                "(custom.meta-model-api-2) — it is never stored in a file. "
                "Phase 6 makes no live calls; set \"brain\": \"mock\" in "
                "00-CEO-Core/config.json to keep drafting at $0."
            ) from exc
        return provider


def get_brain(department, seed=None, config_path=CONFIG_PATH):
    """Module-level shortcut for BrainFactory.get_brain."""
    return BrainFactory.get_brain(department, seed=seed, config_path=config_path)


if __name__ == "__main__":
    mode = BrainFactory.get_brain_mode()
    print(f"brain mode (config): {mode}")
    agency_brain = BrainFactory.get_brain("agency")
    content_brain = BrainFactory.get_brain("content")
    print("agency brain:", type(agency_brain).__name__,
          "| health:", agency_brain.health())
    print("content brain:", type(content_brain).__name__,
          "| health:", content_brain.health())
    assert agency_brain.health()["calls"] == 0
    assert content_brain.health()["calls"] == 0
    print("brain.py: OK (both mocks, 0 calls, $0)")
