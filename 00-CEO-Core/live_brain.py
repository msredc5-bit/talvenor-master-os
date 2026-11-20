"""Live Brain adapter — Phase 10. Brain-কে mock থেকে real-এ নেওয়ার adapter।

কাজ: Main CEO Bot-এর brain যখন config-এ "live", তখন এই adapter
vendored MetaSparkProvider (Muse Spark, api.meta.ai) দিয়ে আসল
complete() call করে। কোনো call fail করলে (credential নেই, timeout,
403/401, non-200, API error) adapter চুপচাপ live সাজে না — LOUD
fallback: stderr-এ কারণ লিখে department-এর নিজের mock brain দিয়ে
draft ফেরত দেয়। এক call = এক attempt, কখনো retry loop নয়।

Credential: key কখনো এই file-এ নেই। MetaSparkProvider key নেয় শুধু
connector Secure Vault surrogate দিয়ে (custom.meta-model-api-2,
dynamic_credentials) — real key file/env/argument/log-এ কখনো আসে না।
Adapter construction-এ কোনো network I/O নেই (provider শুধু
model/timeout store করে) — network শুধু complete() call-এ।

Interface: provider-দের মতোই — complete(prompt, *, max_tokens) -> str,
health() -> dict। দুই department-এর mock-ই fallback হিসেবে চলে
(agency MockLLMProvider, content MockLLM) — Chief-দের call site
বদলাতে হয় না। Body (office, worker, tool, dashboard, gate) ছোঁয়া
হয় না — শুধু brain-এর ভাবনা live হয়।

Stdlib only (+ dynamic_credentials, connector helper) — কোনো pip নেই।
"""

import importlib
import os
import sys

CEO_CORE_DIR = os.path.dirname(os.path.abspath(__file__))
MASTER_OS_DIR = os.path.dirname(CEO_CORE_DIR)
AGENCY_WORKERS_DIR = os.path.join(
    MASTER_OS_DIR, "01-Agency-Department", "engine", "workers")

MODEL = "muse-spark-1.3"


def _load_module(workers_dir, dotted_name):
    """brain.py-র _load_module-এর copy (circular import এড়াতে এখানে)।

    Vendored tree-গুলো top-level `src` package share করে, তাই এক
    process-এ একসময় এক department-এর `src`-ই থাকতে পারে। চাওয়া
    dir-এর `src` না থাকলে stale `src` evict করে নতুনটা load করা হয়।
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


class LiveBrainAdapter:
    """Live brain + loud mock fallback — একটাই interface, দুই mode।

    mode: "live" (শেষ call live-এ সফল) বা "mock-fallback" (শেষ call
    live-এ fail করে mock draft ফেরত গেছে)। last_failure-এ fail-এর
    কারণ থাকে — কখনো খালি/চাপা নয়।
    """

    name = "live-brain-adapter"

    def __init__(self, mock_brain, live_provider=None, timeout=90):
        """mock_brain: department-এর নিজের mock (fallback-এর জন্য)।
        live_provider: test-এ inject করা যায়; না দিলে vendored
        MetaSparkProvider construct হয় (কোনো network I/O নেই)।"""
        self.mock_brain = mock_brain
        if live_provider is not None:
            self.live = live_provider
        else:
            mod = _load_module(AGENCY_WORKERS_DIR, "src.live.meta_provider")
            self.live = mod.MetaSparkProvider(model=MODEL, timeout=timeout)
        self.mode = "live"
        self.last_failure = None
        self.calls = 0
        self.live_calls = 0
        self.fallback_calls = 0

    def complete(self, prompt, *, max_tokens=500):
        """এক attempt: live call; fail করলে LOUD fallback to mock।"""
        self.calls += 1
        try:
            text = self.live.complete(prompt, max_tokens=max_tokens)
        except Exception as exc:  # noqa: BLE001 — যেকোনো live fail = fallback
            reason = f"{type(exc).__name__}: {exc}"
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
        self.mode = "live"
        self.last_failure = None
        self.live_calls += 1
        return text

    def health(self):
        """Adapter-এর সত্য অবস্থা — mode, call count, শেষ fail-এর কারণ।"""
        try:
            mock_health = self.mock_brain.health()
        except Exception:  # noqa: BLE001 — mock health কখনো adapter-কে ভাঙবে না
            mock_health = {"provider": "unknown"}
        return {
            "provider": self.name,
            "model": MODEL,
            "mode": self.mode,
            "ok": True,
            "calls": self.calls,
            "live_calls": self.live_calls,
            "fallback_calls": self.fallback_calls,
            "last_failure": self.last_failure,
            "mock_provider": mock_health.get("provider"),
        }


if __name__ == "__main__":
    # হাতে চেক: adapter construct হয়, কোনো network call হয় না।
    # (complete() ডাকা হয় না — সেটা live probe-এর কাজ।)
    _mod = _load_module(AGENCY_WORKERS_DIR, "src.mock.provider")
    _mock = _mod.MockLLMProvider(seed="master-os-phase1")
    adapter = LiveBrainAdapter(mock_brain=_mock)
    health = adapter.health()
    assert health["provider"] == "live-brain-adapter"
    assert health["mode"] == "live"
    assert health["calls"] == 0
    assert health["fallback_calls"] == 0
    assert health["last_failure"] is None
    print("live_brain: OK (adapter constructs, 0 calls, no network)")
