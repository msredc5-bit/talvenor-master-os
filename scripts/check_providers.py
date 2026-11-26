#!/usr/bin/env python3
"""check_providers.py — Phase 11 self-check for the 8 LLM providers.

What it checks (mock mode ONLY — no live call, ever):
  1. All 8 provider modules import standalone (python3 -I), fast, no network.
  2. Each provider constructs with its key unset — 0 calls, no network.
     (Ollama has no key: it constructs with OLLAMA_HOST unset, default
     localhost.)
  3. Missing key -> clean RuntimeError naming the env var, and NO
     network attempted (urlopen patched to fail the test if called).
     Meta has TWO key paths (META_API_KEY env var on a PC, connector
     surrogate on the Muse VM): with no env var set, complete() would
     take the surrogate path, so the generic missing-key test does not
     apply — instead its module must reference both paths, and a
     missing key with no surrogate must give a clean error naming
     META_API_KEY. Sections 4-6 DO run for Meta (a fake key
     in-process exercises the env-var path).
     Ollama has NO key at all: its section-3 test is "server down ->
     clean error naming Ollama + the fix, no network".
  4. Simulated success per env provider (fake key in-process only,
     fake opener returns a canned payload) -> text returned, tokens counted.
  5. Simulated API-error payload -> RuntimeError with "API error".
  6. Simulated timeout (URLError) -> RuntimeError.
  7. Adapter chain: stubs [fail, fail, ok] -> ok text; [fail, fail] ->
     mock fallback, reason recorded.
  8. BrainFactory selection by temp config: {"brain": "live"} ->
     RuntimeError (production LOCKED unless production_brain.unlocked
     is true); {"brain": "live", "production_brain": {"unlocked": true}}
     -> chain [meta] (unlocked compat); {"brain": "development"} ->
     LiveBrainAdapter in dev mode (free-only guard, 0 calls);
     dev chain with a paid model -> FreeOnlyViolation;
     fallback_chain ["openai", "meta", "mock"] -> chain [openai, meta];
     "provider:model" entries pick the model; unknown provider /
     empty chain -> RuntimeError; brain mock -> mocks.
  9. Real config.json validation: providers section == registry (8),
     each has https endpoint (Ollama: http://localhost only — local
     server, never remote) + env var + non-empty
     models list containing its default model; fallback_chain entries
     resolve (known provider or "mock"), no duplicates; brain_provider
     known; brain stays "mock"; phase 11 + v0.9.0. Phase 1 (local dev):
     development_brain present (free_only + test_data_only true,
     model gemini-3.5-flash-lite, fallback_chain all allowlisted —
     ollama entries accept any non-empty model);
     gemini models contain gemini-3.5-flash-lite and NOT the deprecated
     gemini-2.5-flash; openrouter models all :free / openrouter/free
     and free_only true; production_brain.unlocked is false.
 10. No secrets in the new/changed files (real key patterns only —
     env-var NAME references and os.environ.get() are not secrets).
 11. Real store unchanged by this check run (Phase 9: live queue).
 12. Real guard log untouched (section 7 stubs log to a temp file —
     LiveBrainAdapter.complete() logs every attempt, so without the
     redirect the offline stubs would pollute logs/dev_brain_calls.jsonl).

No live call is made anywhere in this file. The fake key used in the
simulated tests is the literal "test-fake-key" (not a real credential),
set only in this process's environment, never written to a file.

Stdlib only. Run: python3 scripts/check_providers.py
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from unittest import mock

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
WORKERS_DIR = os.path.join(
    BASE, "01-Agency-Department", "engine", "workers")
sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _snapshot_store():
    """Snapshot of the real store (Phase 9: store is now a live queue)."""
    snap = {}
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["tool_calls"] = os.path.exists(
        os.path.join(BASE, "store", "tool_calls.json"))
    return snap


# (module, class, env var, default model).
PROVIDERS = [
    ("src.live.meta_provider", "MetaSparkProvider", "META_API_KEY",
     "muse-spark-1.3"),
    ("src.live.openai_provider", "OpenAIProvider", "OPENAI_API_KEY", "gpt-4o"),
    ("src.live.anthropic_provider", "AnthropicProvider", "ANTHROPIC_API_KEY",
     "claude-sonnet-4-5"),
    ("src.live.gemini_provider", "GeminiProvider", "GEMINI_API_KEY",
     "gemini-3.5-flash-lite"),
    ("src.live.kimi_provider", "KimiProvider", "MOONSHOT_API_KEY", "kimi-k2.5"),
    ("src.live.grok_provider", "GrokProvider", "XAI_API_KEY", "grok-4"),
    ("src.live.openrouter_provider", "OpenRouterProvider",
     "OPENROUTER_API_KEY", "openrouter/free"),
    ("src.live.ollama_provider", "OllamaProvider", "OLLAMA_HOST",
     "qwen2.5-coder:1.5b"),  # F1: was gemma4:12b — cannot run on an 8 GB PC (OOM, verified twice).
]

OPENAI_OK = {
    "choices": [{"message": {"content": "LIVE-REPLY: provider works."}}],
    "usage": {"prompt_tokens": 10, "completion_tokens": 5},
}
# Ollama /api/chat shape: message.content + eval counts.
OLLAMA_OK = {
    "message": {"role": "assistant",
                "content": "LIVE-REPLY: provider works."},
    "done": True,
    "prompt_eval_count": 10,
    "eval_count": 5,
}
ANTHROPIC_OK = {
    "content": [{"type": "text", "text": "LIVE-REPLY: provider works."}],
    "usage": {"input_tokens": 10, "output_tokens": 5},
}
API_ERROR = {"error": {"message": "bad key", "code": "invalid_api_key"}}


class _FakeHTTPResponse:
    def __init__(self, payload):
        self._data = json.dumps(payload).encode()

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _FakeOpener:
    """Instead of urlopen — no network, returns a canned payload."""

    def __init__(self, payload=None, exc=None):
        self.payload = payload
        self.exc = exc
        self.calls = 0

    def open(self, req, timeout=None):
        self.calls += 1
        if self.exc is not None:
            raise self.exc
        return _FakeHTTPResponse(self.payload)


class _StubLive:
    """Fake live provider — behavior: ok | fail."""

    def __init__(self, behavior, name="stub-live"):
        self.behavior = behavior
        self.name = name
        self.model = "stub-model"
        self.calls = 0

    def complete(self, prompt, *, max_tokens=500):
        self.calls += 1
        if self.behavior == "ok":
            return "LIVE-REPLY: chain works."
        raise RuntimeError("live brain call failed: URLError: timed out")


def _temp_config(cfg_dict):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "config-test.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg_dict, f)
    return path


def _unset_env(env_var):
    """Context manager: sets an env var aside, restores it at the end."""
    saved = os.environ.pop(env_var, None)

    class _Ctx:
        def __enter__(self):
            os.environ.pop(env_var, None)
            return None

        def __exit__(self, *args):
            if saved is None:
                os.environ.pop(env_var, None)
            else:
                os.environ[env_var] = saved
            return False

    return _Ctx()


def main():
    store_before = _snapshot_store()

    # Phase 1: LiveBrainAdapter.complete() logs EVERY attempt via the
    # free-only guard — redirect that log to a temp file so the
    # offline stub runs in section 7 never pollute the real
    # logs/dev_brain_calls.jsonl (the real log is a record of real
    # dev-brain calls, not test stubs).
    guard_tmp_log = None
    guard_real_log = None
    guard_real_before = None
    try:
        import free_only_guard as _guard  # noqa: PLC0415
        guard_tmp_log = os.path.join(tempfile.mkdtemp(), "guard-test.log")
        guard_real_log = getattr(_guard, "LOG_PATH", None)
        if guard_real_log:
            try:
                with open(guard_real_log, encoding="utf-8") as f:
                    guard_real_before = f.read()
            except OSError:
                guard_real_before = None
        _guard.LOG_PATH = guard_tmp_log
    except ImportError:
        _guard = None

    # 1. All 7 provider modules import standalone, fast, no network.
    try:
        ok_all = True
        details = []
        for module, _cls, _env, _model in PROVIDERS:
            t0 = __import__("time").time()
            proc = subprocess.run(
                [sys.executable, "-I", "-c",
                 "import sys; sys.path.insert(0, "
                 f"{WORKERS_DIR!r}); import {module}; "
                 "print('import OK')"],
                capture_output=True, text=True, timeout=30, cwd=BASE)
            elapsed = __import__("time").time() - t0
            good = proc.returncode == 0 and elapsed < 10
            ok_all = ok_all and good
            details.append(f"{module.split('.')[-1]}:{elapsed:.1f}s"
                           f":rc={proc.returncode}")
        check("all 8 provider modules import standalone, fast, no network",
              ok_all, ", ".join(details))
    except Exception as e:  # noqa: BLE001
        check("all 8 provider modules import standalone, fast, no network",
              False, str(e))

    # 2-6. Per-provider behavior (in-process, simulated only).
    try:
        from live_brain import (  # noqa: PLC0415
            LiveBrainAdapter, _load_module)

        for module, cls_name, env_var, default_model in PROVIDERS:
            mod = _load_module(WORKERS_DIR, module)
            cls = getattr(mod, cls_name)

            # 2. Constructs with key unset, 0 calls, no network.
            if env_var is not None:
                with _unset_env(env_var):
                    provider = cls()
            else:
                provider = cls()
            h = provider.health()
            check(f"{cls_name} constructs (key unset), 0 calls",
                  h["provider"] == cls.name and h["calls"] == 0
                  and getattr(provider, "model", None) == default_model,
                  f"model={getattr(provider, 'model', None)}")

            def _no_network(*args, **kwargs):
                raise AssertionError("network attempted with no key")

            if cls_name == "MetaSparkProvider":
                # Meta has TWO key paths: the META_API_KEY env var (PC)
                # and the connector surrogate (Muse VM). With no env var
                # set, complete() would take the surrogate path, so the
                # generic missing-key test below does not apply — and
                # complete() is NEVER called unguarded here (it would
                # touch the connector + network). Instead verify the
                # module references both paths, and that a missing key
                # with no surrogate gives a clean error naming
                # META_API_KEY (surrogate loader patched out).
                with open(os.path.join(
                        WORKERS_DIR, "src", "live", "meta_provider.py"),
                        encoding="utf-8") as f:
                    src = f.read()
                check("MetaSparkProvider: META_API_KEY env var + "
                      "connector path",
                      "custom.meta-model-api-2" in src
                      and "META_API_KEY" in src
                      and "os.environ" in src,
                      "dual key path present")

                def _no_surrogate(*args, **kwargs):
                    raise ImportError("no surrogate on this machine")

                with _unset_env(env_var):
                    with mock.patch.object(
                            mod, "_load_surrogate",
                            side_effect=_no_surrogate):
                        with mock.patch.object(
                                urllib.request, "build_opener",
                                side_effect=_no_network):
                            try:
                                provider.complete("smoke")
                                raised = None
                            except RuntimeError as e:
                                raised = str(e)
                            except AssertionError:
                                raised = "NETWORK-ATTEMPTED"
                check("MetaSparkProvider missing key + no surrogate -> "
                      "error names META_API_KEY, no network",
                      raised is not None and "META_API_KEY" in raised
                      and "NETWORK-ATTEMPTED" not in raised,
                      (raised or "no error")[:120])
                # Fall through to sections 4-6: with a fake key set,
                # the env-var path is exercised with a fake opener.

            # 3. Missing key -> clean error naming the env var, NO network.
            # (Meta skipped: its missing-key case is covered above.
            # Ollama skipped here too: it has no key — its own
            # server-down test runs below.)
            if cls_name not in ("MetaSparkProvider", "OllamaProvider"):
                with _unset_env(env_var):
                    with mock.patch.object(urllib.request, "build_opener",
                                          side_effect=_no_network):
                        try:
                            provider.complete("smoke")
                            raised = None
                        except RuntimeError as e:
                            raised = str(e)
                        except AssertionError:
                            raised = "NETWORK-ATTEMPTED"
                check(f"{cls_name} missing key -> error names {env_var}, "
                      "no network",
                      raised is not None and env_var in raised
                      and "NETWORK-ATTEMPTED" not in raised,
                      (raised or "no error")[:120])

            if cls_name == "OllamaProvider":
                # No key exists for Ollama: with the server down,
                # complete() must name Ollama + the fix (start it,
                # pull the model) and attempt no real network.
                fake_down = _FakeOpener(
                    exc=urllib.error.URLError(
                        "[Errno 111] Connection refused"))
                with _unset_env(env_var):
                    with mock.patch.object(urllib.request, "build_opener",
                                          return_value=fake_down):
                        try:
                            provider.complete("smoke")
                            raised = None
                        except RuntimeError as e:
                            raised = str(e)
                check("OllamaProvider server down -> error names Ollama "
                      "+ the fix, no network",
                      raised is not None and "Ollama" in raised
                      and "ollama pull" in raised,
                      (raised or "no error")[:160])

            # 4-6. Simulated wire: success / API error / timeout.
            # Ollama speaks /api/chat (message.content), not the
            # OpenAI choices shape — and OLLAMA_HOST is a server
            # address, not a key, so the fake env value is a URL.
            ok_payload = (OLLAMA_OK if cls_name == "OllamaProvider"
                          else ANTHROPIC_OK
                          if cls_name == "AnthropicProvider"
                          else OPENAI_OK)
            env_value = ("http://localhost:11434"
                         if cls_name == "OllamaProvider"
                         else "test-fake-key")
            with mock.patch.dict(os.environ, {env_var: env_value}):
                # 4. Success -> text + tokens counted.
                fake = _FakeOpener(payload=ok_payload)
                with mock.patch.object(urllib.request, "build_opener",
                                      return_value=fake):
                    text = provider.complete("smoke", max_tokens=30)
                h = provider.health()
                check(f"{cls_name} simulated success: text + tokens",
                      text.startswith("LIVE-REPLY")
                      and h["calls"] >= 1
                      and h["total_tokens"] == 15,
                      f"text={text[:30]!r}, total={h['total_tokens']}")
                # 5. API error payload -> RuntimeError.
                fake_err = _FakeOpener(payload=API_ERROR)
                with mock.patch.object(urllib.request, "build_opener",
                                      return_value=fake_err):
                    try:
                        provider.complete("smoke")
                        err = None
                    except RuntimeError as e:
                        err = str(e)
                check(f"{cls_name} simulated API error -> RuntimeError",
                      err is not None and "API error" in err
                      and "invalid_api_key" in err,
                      (err or "no error")[:120])
                # 6. Timeout -> RuntimeError.
                fake_to = _FakeOpener(
                    exc=urllib.error.URLError("timed out"))
                with mock.patch.object(urllib.request, "build_opener",
                                      return_value=fake_to):
                    try:
                        provider.complete("smoke")
                        err = None
                    except RuntimeError as e:
                        err = str(e)
                check(f"{cls_name} simulated timeout -> RuntimeError",
                      err is not None and "timed out" in err,
                      (err or "no error")[:120])
    except Exception as e:  # noqa: BLE001
        check("per-provider behavior (construct/missing-key/simulated wire)",
              False, str(e))

    # 7. Adapter chain walks providers, then mock fallback.
    try:
        from live_brain import LiveBrainAdapter  # noqa: PLC0415
        from brain import BrainFactory  # noqa: PLC0415

        mock_cfg = _temp_config({"brain": "mock"})
        agency_mock = BrainFactory.get_brain("agency", config_path=mock_cfg)

        adapter = LiveBrainAdapter(
            mock_brain=agency_mock,
            live_providers=[_StubLive("fail", "stub-a"),
                            _StubLive("fail", "stub-b"),
                            _StubLive("ok", "stub-c")])
        text = adapter.complete("smoke")
        h = adapter.health()
        check("chain [fail, fail, ok] -> ok text from 3rd provider",
              text.startswith("LIVE-REPLY") and h["mode"] == "live"
              and h["live_calls"] == 1 and h["fallback_calls"] == 0
              and h["providers"] == ["stub-a", "stub-b", "stub-c"],
              f"mode={h['mode']}, live_calls={h['live_calls']}")

        adapter2 = LiveBrainAdapter(
            mock_brain=agency_mock,
            live_providers=[_StubLive("fail", "stub-a"),
                            _StubLive("fail", "stub-b")])
        text = adapter2.complete("smoke")
        h = adapter2.health()
        check("chain [fail, fail] -> mock fallback, reason recorded",
              text.startswith("MOCK-PLAN") and h["mode"] == "mock-fallback"
              and h["fallback_calls"] == 1
              and h["last_failure"] is not None
              and "stub-a" in h["last_failure"]
              and "stub-b" in h["last_failure"],
              f"mode={h['mode']}")
    except Exception as e:  # noqa: BLE001
        for name in ("chain [fail, fail, ok] -> ok text from 3rd provider",
                     "chain [fail, fail] -> mock fallback, reason recorded"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 8. BrainFactory selection by temp config.
    try:
        from brain import BrainFactory  # noqa: PLC0415

        # (a) {"brain": "live"} (no production_brain block) must now
        # raise RuntimeError mentioning LOCKED — production live is
        # locked behind production_brain.unlocked (Phase 1, worker A).
        cfg_a = _temp_config({"brain": "live"})
        try:
            BrainFactory.get_brain("agency", config_path=cfg_a)
            locked_ok = False
            detail_a = "no error raised — production live NOT locked"
        except RuntimeError as e:
            locked_ok = "LOCKED" in str(e)
            detail_a = str(e)[:120]
        except Exception as e:  # noqa: BLE001
            locked_ok = False
            detail_a = f"{type(e).__name__}: {e}"[:120]
        check('factory {"brain": "live"} -> RuntimeError (production LOCKED)',
              locked_ok, detail_a)

        # (f) {"brain": "live", "production_brain": {"unlocked": true}}
        # -> LiveBrainAdapter chain [meta] (unlocked compat).
        try:
            cfg_f = _temp_config({"brain": "live",
                                  "production_brain": {"unlocked": True}})
            brain_f = BrainFactory.get_brain("agency", config_path=cfg_f)
            h = brain_f.health()
            check('factory {"brain": "live", "production_brain": '
                  '{"unlocked": true}} -> chain [meta] (unlocked compat)',
                  type(brain_f).__name__ == "LiveBrainAdapter"
                  and h["providers"] == ["meta-spark-live"]
                  and h["models"] == ["muse-spark-1.3"]
                  and h["calls"] == 0,
                  f"providers={h['providers']}, models={h['models']}")
        except Exception as e:  # noqa: BLE001
            check('factory {"brain": "live", "production_brain": '
                  '{"unlocked": true}} -> chain [meta] (unlocked compat)',
                  False, f"{type(e).__name__}: {e}"[:120])

        # (g) {"brain": "development"} with a free-only chain ->
        # LiveBrainAdapter in dev mode, guard on, 0 calls, no key needed.
        try:
            cfg_g = _temp_config(
                {"brain": "development",
                 "development_brain": {
                     "enabled": True,
                     "fallback_chain": ["gemini:gemini-3.5-flash-lite",
                                        "openrouter:openrouter/free"],
                     "free_only": True,
                     "test_data_only": True}})
            brain_g = BrainFactory.get_brain("agency", config_path=cfg_g)
            h = brain_g.health()
            check('factory {"brain": "development"} -> dev adapter, '
                  'free-only guard, 0 calls',
                  type(brain_g).__name__ == "LiveBrainAdapter"
                  and h.get("brain_kind") == "development"
                  and h.get("guard") == "free-only"
                  and h["providers"] == ["gemini-live", "openrouter-live"]
                  and h["models"] == ["gemini-3.5-flash-lite",
                                      "openrouter/free"]
                  and h["calls"] == 0,
                  f"brain_kind={h.get('brain_kind')}, "
                  f"guard={h.get('guard')}, providers={h['providers']}, "
                  f"models={h['models']}")
        except Exception as e:  # noqa: BLE001
            check('factory {"brain": "development"} -> dev adapter, '
                  'free-only guard, 0 calls',
                  False, f"{type(e).__name__}: {e}"[:120])

        # (h) dev chain with a paid model -> FreeOnlyViolation at build.
        try:
            from free_only_guard import FreeOnlyViolation  # noqa: PLC0415
        except ImportError as e:
            check('factory dev chain ["openai:gpt-4o"] -> FreeOnlyViolation',
                  False, f"free_only_guard missing (worker B): {e}")
        else:
            cfg_h = _temp_config(
                {"brain": "development",
                 "development_brain": {
                     "enabled": True,
                     "fallback_chain": ["openai:gpt-4o"],
                     "free_only": True,
                     "test_data_only": True}})
            try:
                BrainFactory.get_brain("agency", config_path=cfg_h)
                paid_ok = False
                detail_h = "no error raised — paid model NOT rejected"
            except FreeOnlyViolation as e:
                paid_ok = True
                detail_h = str(e)[:120]
            except Exception as e:  # noqa: BLE001
                paid_ok = False
                detail_h = f"{type(e).__name__}: {e}"[:120]
            check('factory dev chain ["openai:gpt-4o"] -> FreeOnlyViolation',
                  paid_ok, detail_h)

        # (b) fallback_chain ["openai", "meta", "mock"] -> [openai, meta].
        # Phase 1: production live is LOCKED, so the temp config must
        # carry production_brain.unlocked to exercise the chain at all.
        cfg_b = _temp_config({"brain": "live",
                              "production_brain": {"unlocked": True},
                              "fallback_chain": ["openai", "meta", "mock"]})
        brain_b = BrainFactory.get_brain("agency", config_path=cfg_b)
        h = brain_b.health()
        check('factory chain ["openai", "meta", "mock"] -> [openai, meta]',
              h["providers"] == ["openai-live", "meta-spark-live"]
              and h["models"] == ["gpt-4o", "muse-spark-1.3"],
              f"providers={h['providers']}")

        # (c) "provider:model" entries pick the model.
        cfg_c = _temp_config(
            {"brain": "live",
             "production_brain": {"unlocked": True},
             "fallback_chain": ["openrouter:openrouter/free",
                                "grok:grok-4.6"]})
        brain_c = BrainFactory.get_brain("agency", config_path=cfg_c)
        h = brain_c.health()
        check('factory "provider:model" entries pick the model',
              h["providers"] == ["openrouter-live", "grok-live"]
              and h["models"] == ["openrouter/free", "grok-4.6"],
              f"models={h['models']}")

        # (d) unknown provider / empty chain -> RuntimeError.
        cfg_d = _temp_config({"brain": "live",
                              "production_brain": {"unlocked": True},
                              "fallback_chain": ["nope", "mock"]})
        try:
            BrainFactory.get_brain("agency", config_path=cfg_d)
            bad_ok = False
        except RuntimeError:
            bad_ok = True
        cfg_e = _temp_config({"brain": "live",
                              "production_brain": {"unlocked": True},
                              "fallback_chain": ["mock"]})
        try:
            BrainFactory.get_brain("agency", config_path=cfg_e)
            empty_ok = False
        except RuntimeError:
            empty_ok = True
        check("factory unknown provider / empty chain -> RuntimeError",
              bad_ok and empty_ok, f"unknown={bad_ok}, empty={empty_ok}")

        # (e) brain mock -> each dept's own mock (unchanged).
        mock_cfg = _temp_config({"brain": "mock"})
        agency_brain = BrainFactory.get_brain("agency", config_path=mock_cfg)
        content_brain = BrainFactory.get_brain("content",
                                               config_path=mock_cfg)
        check("factory brain mock -> each dept's own mock",
              type(agency_brain).__name__ == "MockLLMProvider"
              and type(content_brain).__name__ == "MockLLM",
              f"agency={type(agency_brain).__name__}, "
              f"content={type(content_brain).__name__}")
    except Exception as e:  # noqa: BLE001
        check("BrainFactory selection by temp config", False, str(e))

    # 9. Real config.json validation.
    try:
        from live_brain import (  # noqa: PLC0415
            PROVIDER_MODULES, DEFAULT_MODELS)

        with open(os.path.join(CEO_CORE_DIR, "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        providers = cfg.get("providers", {})
        problems = []
        if set(providers) != set(PROVIDER_MODULES):
            problems.append(
                f"providers keys {sorted(providers)} != registry "
                f"{sorted(PROVIDER_MODULES)}")
        for name, entry in providers.items():
            if name == "ollama":
                # Local server only — http://localhost, never remote.
                if entry.get("endpoint") != \
                        "http://localhost:11434/api/chat":
                    problems.append(
                        "ollama: endpoint must be "
                        "http://localhost:11434/api/chat")
            elif not str(entry.get("endpoint", "")).startswith("https://"):
                problems.append(f"{name}: endpoint not https")
            env_var = entry.get("env_var")
            if name == "meta":
                # Meta key slot (2026-11-25): META_API_KEY env var on
                # the PC, connector surrogate on the Muse VM.
                if env_var != "META_API_KEY":
                    problems.append(
                        "meta: env_var must be META_API_KEY")
            elif not isinstance(env_var, str) or not env_var:
                problems.append(f"{name}: env_var missing")
            models = entry.get("models", [])
            if not isinstance(models, list) or not models:
                problems.append(f"{name}: models empty")
            elif DEFAULT_MODELS.get(name) not in models:
                problems.append(
                    f"{name}: default {DEFAULT_MODELS.get(name)} "
                    "not in models")
        chain = cfg.get("fallback_chain", [])
        seen = set()
        for entry in chain:
            name = str(entry).partition(":")[0].strip().lower()
            if name != "mock" and name not in PROVIDER_MODULES:
                problems.append(f"fallback_chain: unknown {entry!r}")
            if entry in seen:
                problems.append(f"fallback_chain: duplicate {entry!r}")
            seen.add(entry)
        if cfg.get("brain_provider") not in PROVIDER_MODULES:
            problems.append("brain_provider unknown")
        if cfg.get("brain") != "mock":
            problems.append("brain is not mock")
        # D1 (2026-11-21): phase 9 -> 11 — the pin moves with the
        # config bump, it does not stay 9.
        if cfg.get("phase") != 11 or cfg.get("version") != "0.9.0":
            problems.append("phase/version moved (must stay 11 / 0.9.0)")
        # Phase 1 (local dev): development_brain / production_brain.
        dev = cfg.get("development_brain")
        if not isinstance(dev, dict):
            problems.append("development_brain block missing")
        else:
            if dev.get("free_only") is not True:
                problems.append("development_brain.free_only is not true")
            if dev.get("test_data_only") is not True:
                problems.append(
                    "development_brain.test_data_only is not true")
            if dev.get("model") != "gemini-3.5-flash-lite":
                problems.append(
                    "development_brain.model is not gemini-3.5-flash-lite")
            for entry in dev.get("fallback_chain", []):
                name, _sep, model = str(entry).partition(":")
                name = name.strip().lower()
                model = model.strip()
                if name == "ollama":
                    # Local server: any non-empty model id is free-only.
                    if not model:
                        problems.append(
                            "dev chain: ollama entry without a model")
                elif name == "gemini":
                    if model not in ("gemini-3.5-flash-lite",
                                     "gemini-2.0-flash"):
                        problems.append(
                            f"dev chain: non-allowlisted gemini {model!r}")
                elif name == "openrouter":
                    if not (model.endswith(":free")
                            or model == "openrouter/free"):
                        problems.append(
                            f"dev chain: non-free openrouter {model!r}")
                else:
                    problems.append(
                        f"dev chain: unknown provider {entry!r}")
        prod = cfg.get("production_brain")
        if not isinstance(prod, dict):
            problems.append("production_brain block missing")
        elif prod.get("unlocked") is not False:
            problems.append("production_brain.unlocked is not false")
        gemini_models = providers.get("gemini", {}).get("models", [])
        if "gemini-3.5-flash-lite" not in gemini_models:
            problems.append(
                "gemini models lack gemini-3.5-flash-lite")
        if "gemini-2.5-flash-lite" in gemini_models:
            problems.append(
                "gemini models still list removed gemini-2.5-flash-lite")
        if "gemini-2.5-flash" in gemini_models:
            problems.append(
                "gemini models still contain deprecated gemini-2.5-flash")
        or_models = providers.get("openrouter", {}).get("models", [])
        for model in or_models:
            if not (str(model).endswith(":free")
                    or str(model) == "openrouter/free"):
                problems.append(
                    f"openrouter model not :free: {model!r}")
        if providers.get("openrouter", {}).get("free_only") is not True:
            problems.append("openrouter.free_only is not true")
        check("real config.json: 8 providers + chain + mock default "
              "+ dev/prod blocks",
              not problems, "; ".join(problems[:5]) if problems else
              f"providers={len(providers)}, chain={chain}, "
              f"dev={dev.get('model') if isinstance(dev, dict) else None}")
    except Exception as e:  # noqa: BLE001
        check("real config.json: 8 providers + chain + mock default "
              "+ dev/prod blocks",
              False, str(e))

    # 10. No secrets in the new/changed files.
    # (This check file itself is excluded: it holds the pattern
    # literals and the "test-fake-key" dummy — the same self-reference
    # the live-brain check notes.)
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]{16,}|sk-ant-[A-Za-z0-9]{16,}|"
            r"AIza[A-Za-z0-9_\-]{20,}|xai-[A-Za-z0-9]{16,}|"
            r"api_key\s*=\s*[\"'][^\"']{8,}[\"']|"
            r"password\s*=\s*[\"'][^\"']+[\"']")
        bad = []
        rels = [
            "01-Agency-Department/engine/workers/src/live/meta_provider.py",
            "01-Agency-Department/engine/workers/src/live/openai_provider.py",
            "01-Agency-Department/engine/workers/src/live/anthropic_provider.py",
            "01-Agency-Department/engine/workers/src/live/gemini_provider.py",
            "01-Agency-Department/engine/workers/src/live/kimi_provider.py",
            "01-Agency-Department/engine/workers/src/live/grok_provider.py",
            "01-Agency-Department/engine/workers/src/live/openrouter_provider.py",
            "01-Agency-Department/engine/workers/src/live/ollama_provider.py",
            "00-CEO-Core/live_brain.py",
            "00-CEO-Core/brain.py",
            "00-CEO-Core/free_only_guard.py",
            "00-CEO-Core/config.json",
            "00-CEO-Core/PROVIDERS-SETUP.md",
        ]
        for rel in rels:
            path = os.path.join(BASE, rel)
            if not os.path.exists(path):
                bad.append(f"{rel}:MISSING")
                continue
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if secret_re.search(line):
                        bad.append(f"{rel}:{lineno}")
        check("no secrets in provider/config/guide files",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in provider/config/guide files", False, str(e))

    # 11. Real store unchanged by this check run.
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 12. Real guard log untouched (section 7 stubs log to a temp file).
    try:
        if guard_real_log is None:
            check("real guard log file untouched by this run",
                  _guard is None,
                  "no guard module — nothing to write"
                  if _guard is None else "no real log path")
        else:
            try:
                with open(guard_real_log, encoding="utf-8") as f:
                    guard_real_after = f.read()
            except OSError:
                guard_real_after = None
            check("real guard log file untouched by this run",
                  guard_real_after == guard_real_before,
                  "untouched" if guard_real_after == guard_real_before
                  else "CHANGED — stub entries leaked into the real log")
    except Exception as e:  # noqa: BLE001
        check("real guard log file untouched by this run", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_providers: ALL PASS (mock mode — no live call made).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
