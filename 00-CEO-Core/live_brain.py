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

Phase 11 — provider chain: adapter এখন একটা provider নয়, config-এর
fallback_chain অনুযায়ী একটার পর একটা provider চেষ্টা করে
(openrouter -> meta -> ... -> mock)। প্রতিটা provider একই interface
— complete(prompt, *, max_tokens) -> str — তাই যেকোনো vendor-এর
যেকোনো chat model বসানো যায়, শুধু নাম বদলে। Provider registry নিচে
(PROVIDER_MODULES): module + class + default model। Key-র নিয়ম
প্রতিটা provider file-এ একই — env var থেকে (Meta শুধু connector
surrogate দিয়ে)। Chain-এর কোনো provider-ই construction-এ network
করে না; key পড়া হয় শুধু complete()-এ।

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

# Phase 11 — provider registry: key -> (module, class)।
# Module-গুলো 01-Agency-Department/engine/workers/src/live/-এ থাকে,
# _load_module দিয়ে "src.live.<name>_provider" হিসেবে load হয়।
# Key-র নিয়ম প্রতিটা provider file-এ লেখা (env var; Meta শুধু
# connector surrogate)। config.json-এর providers section-এ একই
# তথ্য declarative ভাবে থাকে — check_providers.py দুটো মেলায়।
PROVIDER_MODULES = {
    "meta": ("src.live.meta_provider", "MetaSparkProvider"),
    "openai": ("src.live.openai_provider", "OpenAIProvider"),
    "anthropic": ("src.live.anthropic_provider", "AnthropicProvider"),
    "gemini": ("src.live.gemini_provider", "GeminiProvider"),
    "kimi": ("src.live.kimi_provider", "KimiProvider"),
    "grok": ("src.live.grok_provider", "GrokProvider"),
    "openrouter": ("src.live.openrouter_provider", "OpenRouterProvider"),
}

# প্রতিটা provider-এর default model — config-এ model না দিলে এটা চলে।
DEFAULT_MODELS = {
    "meta": "muse-spark-1.3",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-5",
    "gemini": "gemini-2.5-flash",
    "kimi": "kimi-k2.5",
    "grok": "grok-4",
    "openrouter": "openrouter/free",
}


def load_provider(name, model=None, timeout=90):
    """একটা provider construct করো — কোনো network I/O নেই।

    name: registry key ("meta" | "openai" | ... )। model: None হলে
    DEFAULT_MODELS[name]। Unknown name -> ValueError।
    """
    key = str(name).strip().lower()
    if key not in PROVIDER_MODULES:
        raise ValueError(
            f"Unknown provider {name!r}. Known: {sorted(PROVIDER_MODULES)}")
    module_name, class_name = PROVIDER_MODULES[key]
    mod = _load_module(AGENCY_WORKERS_DIR, module_name)
    cls = getattr(mod, class_name)
    return cls(model=model or DEFAULT_MODELS[key], timeout=timeout)


def build_provider_chain(cfg, timeout=90):
    """config থেকে live provider chain বানাও — কোনো network I/O নেই।

    cfg: config.json-এর dict (বা {} — তখন default ["meta"])।
    fallback_chain-এর প্রতিটা entry "provider" বা "provider:model"
    (model-এ ":" থাকতে পারে, যেমন openrouter:nvidia/...:free — তাই
    প্রথম ":"-এই split)। "mock" entry chain-এর শেষ — ওটা provider
    নয়, adapter-এর implicit fallback, তাই এখানে skip করা হয়।
    Chain খালি হলে RuntimeError (কোনো live provider নেই)।
    """
    if not isinstance(cfg, dict):
        cfg = {}
    chain_spec = cfg.get("fallback_chain") or [cfg.get("brain_provider", "meta")]
    providers = []
    for entry in chain_spec:
        if not isinstance(entry, str):
            raise ValueError(
                f"fallback_chain entry must be a string, got {entry!r}")
        name, _sep, model = entry.partition(":")
        name = name.strip().lower()
        if name == "mock":
            continue
        providers.append(
            load_provider(name, model.strip() or None, timeout=timeout))
    if not providers:
        raise RuntimeError(
            "No live provider in fallback_chain — enable at least one "
            "provider (e.g. \"meta\" or \"openrouter\") or keep "
            "\"brain\": \"mock\" in 00-CEO-Core/config.json.")
    return providers


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

    Phase 11: adapter এখন provider CHAIN নেয় — complete() chain-এর
    প্রতিটা provider একটার পর একটা চেষ্টা করে; সব fail করলে তবেই
    mock fallback। live_provider (একটা) দিলে chain=[সেটা] — পুরনো
    call site অপরিবর্তিত।
    """

    name = "live-brain-adapter"

    def __init__(self, mock_brain, live_provider=None, live_providers=None,
                 timeout=90):
        """mock_brain: department-এর নিজের mock (fallback-এর জন্য)।
        live_provider: একটা provider inject করা যায় (test-এ);
        live_providers: chain (list) দিলে সেটাই চলে; দুটোই না দিলে
        vendored MetaSparkProvider construct হয় (কোনো network I/O নেই)।"""
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
        self.calls = 0
        self.live_calls = 0
        self.fallback_calls = 0

    def complete(self, prompt, *, max_tokens=500):
        """এক attempt প্রতি provider: chain ঘুরে প্রথম সফল উত্তর নেয়;
        সব fail করলে LOUD fallback to mock।"""
        self.calls += 1
        errors = []
        for provider in self.live_chain:
            try:
                text = provider.complete(prompt, max_tokens=max_tokens)
            except Exception as exc:  # noqa: BLE001 — পরের provider চেষ্টা
                pname = getattr(provider, "name",
                                type(provider).__name__)
                errors.append(f"{pname}: {type(exc).__name__}: {exc}")
                continue
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
        """Adapter-এর সত্য অবস্থা — mode, call count, শেষ fail-এর কারণ।"""
        try:
            mock_health = self.mock_brain.health()
        except Exception:  # noqa: BLE001 — mock health কখনো adapter-কে ভাঙবে না
            mock_health = {"provider": "unknown"}
        return {
            "provider": self.name,
            "model": getattr(self.live, "model", None),
            "providers": [getattr(p, "name", type(p).__name__)
                          for p in self.live_chain],
            "models": [getattr(p, "model", None)
                       for p in self.live_chain],
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
