#!/usr/bin/env python3
"""check_live_brain.py — Phase 1 (local-first) self-check for the live brain adapter.

What it checks (mock mode — no network, no live call, ever):
  1. live_brain.py imports standalone (python3 -I), fast, no network.
  2. Adapter constructs with a stub live provider — health provider
     "live-brain-adapter", mode "live", 0 calls.
  3. Live success path: stub returns text -> complete() returns it,
     mode "live", live_calls 1.
  4. Fallback on timeout: stub raises URLError-style failure ->
     mock draft returned, mode "mock-fallback", reason recorded.
  5. Fallback on credential failure: stub raises
     DynamicCredentialError -> mock draft, reason recorded.
  6. Fallback on API error: stub raises API-error failure ->
     mock draft, reason recorded.
  7. BrainFactory temp configs: {"brain": "live"} raises RuntimeError
     (production LOCKED); {"brain": "development"} returns
     LiveBrainAdapter x2 (agency + content) in dev mode, 0 calls;
     bad mode raises ValueError.
  8. BrainFactory mock-mode temp config still returns each dept's
     own mock (unchanged behavior).
  9. No secrets in live_brain.py / brain.py / this file (no
     surrogate, no key literal, no password assignment).
 10. Real store unchanged by this check run (Phase 9: live queue).
 11. Real guard log untouched (the stub runs log to a temp file —
     LiveBrainAdapter.complete() logs every attempt, so without the
     redirect the offline stubs would pollute logs/dev_brain_calls.jsonl).

NOTE: the stub providers in sections 2-6 run in default (live) mode,
so the free-only guard does not apply there — guard enforcement is
covered by scripts/check_dev_brain.py.

LIVE PROBE (OFF by default — run only with --live, on Boss's PC):
  One tiny real call through the DEV brain path: the free tier
  (Ollama local Gemma 4 first, or Gemini gemini-3.5-flash-lite, or
  whichever free model scripts/setup_brain.py saved — max 30
  completion tokens) via BrainFactory.get_brain("agency") with a temp
  config mirroring the real config's development_brain block — the
  real config's brain flag is never flipped. Exactly one request,
  never retries. Prints reply, latency, tokens, mode, brain_kind, and
  the exact model tried. Exit 0 + PASS only if health mode is "live"
  AND brain_kind is "development"; otherwise FAILED with the exact
  reason and the brain stays mock.
  If the dev chain has an Ollama entry, the probe runs with NO key
  at all (local server). Otherwise it runs only when a key is set
  for a provider in the chain (GEMINI_API_KEY / OPENROUTER_API_KEY);
  with no key it prints the exact setup steps and exits non-zero
  WITHOUT attempting any call.

Boss PC steps (Windows):
  1. Local (no key): install Ollama (https://ollama.com), pull a model:
     ollama pull gemma4:12b
     (small fallback: ollama pull qwen2.5-coder:1.5b)
  2. Or a free key (no card, no billing): aistudio.google.com/apikey
  3. Set it (then open a NEW terminal):
     setx GEMINI_API_KEY "paste-key-here"
  4. Find a working free model (no JSON editing):
     python scripts\\setup_brain.py
  5. Direct curl test first (optional):
     curl.exe -s https://generativelanguage.googleapis.com/v1beta/openai/chat/completions -H "Authorization: Bearer $env:GEMINI_API_KEY" -H "Content-Type: application/json" -d '{"model":"gemini-3.5-flash-lite","messages":[{"role":"user","content":"Reply with the single word: ok"}]}'
  6. Then run: python scripts\\check_live_brain.py --live

Stdlib only. Run: python3 scripts/check_live_brain.py [--live]
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
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


class _StubLive:
    """Fake live provider — behavior: ok | timeout | credential | api-error."""

    def __init__(self, behavior):
        self.behavior = behavior
        self.calls = 0

    def complete(self, prompt, *, max_tokens=500):
        self.calls += 1
        if self.behavior == "ok":
            return "LIVE-REPLY: Talvenor Master OS runs the office."
        if self.behavior == "timeout":
            raise RuntimeError(
                "live brain call failed: URLError: timed out")
        if self.behavior == "credential":
            from dynamic_credentials import DynamicCredentialError  # noqa: PLC0415
            raise DynamicCredentialError(
                "authd surrogate unavailable (simulated)")
        if self.behavior == "api-error":
            raise RuntimeError(
                "live brain API error: {'code': 'invalid_api_key'}")
        raise RuntimeError(f"unknown stub behavior: {self.behavior}")


def _temp_config(mode, extra=None):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, f"config-{mode}.json")
    cfg = {"brain": mode}
    if extra:
        cfg.update(extra)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return path


def _dev_extra():
    """The development_brain block a dev temp config needs."""
    return {"development_brain": {
        "enabled": True,
        "fallback_chain": ["gemini:gemini-3.5-flash-lite",
                           "openrouter:openrouter/free"],
        "free_only": True,
        "test_data_only": True}}


def main():
    store_before = _snapshot_store()

    # Phase 1: LiveBrainAdapter.complete() logs EVERY attempt via the
    # free-only guard — redirect that log to a temp file so the
    # offline stub runs in sections 2-6 never pollute the real
    # logs/dev_brain_calls.jsonl.
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

    # 1. live_brain.py imports standalone, fast, no network.
    try:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, "
             f"{CEO_CORE_DIR!r}); import live_brain; "
             "print('live_brain import OK')"],
            capture_output=True, text=True, timeout=30, cwd=BASE)
        elapsed = time.time() - t0
        ok = proc.returncode == 0 and elapsed < 10
        check("live_brain.py imports standalone, fast, no network",
              ok, f"{elapsed:.2f}s, rc={proc.returncode}, "
              + (proc.stdout + proc.stderr).strip()[-200:])
    except Exception as e:  # noqa: BLE001
        check("live_brain.py imports standalone, fast, no network",
              False, str(e))

    # 2-6. Adapter behavior with stub live providers.
    try:
        from live_brain import LiveBrainAdapter  # noqa: PLC0415
        from brain import BrainFactory  # noqa: PLC0415

        mock_cfg = _temp_config("mock")
        agency_mock = BrainFactory.get_brain("agency", config_path=mock_cfg)

        # 2. Constructs, 0 calls, mode live.
        adapter = LiveBrainAdapter(mock_brain=agency_mock,
                                   live_provider=_StubLive("ok"))
        h = adapter.health()
        check("adapter constructs (stub live), 0 calls, mode live",
              h["provider"] == "live-brain-adapter"
              and h["mode"] == "live" and h["calls"] == 0
              and h["last_failure"] is None,
              f"provider={h['provider']}, mode={h['mode']}")

        # 3. Live success path.
        text = adapter.complete("smoke", max_tokens=30)
        h = adapter.health()
        check("live success: stub text returned, mode live",
              text.startswith("LIVE-REPLY") and h["mode"] == "live"
              and h["live_calls"] == 1 and h["fallback_calls"] == 0,
              f"text={text[:40]!r}")

        # 4. Fallback on timeout -> mock draft, reason recorded.
        adapter_t = LiveBrainAdapter(mock_brain=agency_mock,
                                     live_provider=_StubLive("timeout"))
        text = adapter_t.complete("smoke")
        h = adapter_t.health()
        check("fallback on timeout: mock draft, reason recorded",
              text.startswith("MOCK-PLAN") and h["mode"] == "mock-fallback"
              and h["fallback_calls"] == 1
              and h["last_failure"] is not None
              and "timed out" in h["last_failure"],
              f"mode={h['mode']}, reason={h['last_failure']!r}"[:160])

        # 5. Fallback on credential failure -> mock draft.
        adapter_c = LiveBrainAdapter(mock_brain=agency_mock,
                                     live_provider=_StubLive("credential"))
        text = adapter_c.complete("smoke")
        h = adapter_c.health()
        check("fallback on credential failure: mock draft, reason recorded",
              text.startswith("MOCK-PLAN") and h["mode"] == "mock-fallback"
              and h["fallback_calls"] == 1
              and "DynamicCredentialError" in (h["last_failure"] or ""),
              f"mode={h['mode']}")

        # 6. Fallback on API error -> mock draft.
        adapter_a = LiveBrainAdapter(mock_brain=agency_mock,
                                     live_provider=_StubLive("api-error"))
        text = adapter_a.complete("smoke")
        h = adapter_a.health()
        check("fallback on API error: mock draft, reason recorded",
              text.startswith("MOCK-PLAN") and h["mode"] == "mock-fallback"
              and h["fallback_calls"] == 1
              and "invalid_api_key" in (h["last_failure"] or ""),
              f"mode={h['mode']}")
    except Exception as e:  # noqa: BLE001
        for name in ("adapter constructs (stub live), 0 calls, mode live",
                     "live success: stub text returned, mode live",
                     "fallback on timeout: mock draft, reason recorded",
                     "fallback on credential failure: mock draft, reason recorded",
                     "fallback on API error: mock draft, reason recorded"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 7. BrainFactory temp configs: "live" is production-LOCKED,
    # "development" returns the dev adapter x2, bad mode raises.
    try:
        from brain import BrainFactory  # noqa: PLC0415

        # (a) {"brain": "live"} -> RuntimeError (production LOCKED).
        live_cfg = _temp_config("live")
        try:
            BrainFactory.get_brain("agency", config_path=live_cfg)
            locked_ok = False
            locked_detail = "no error raised — production live NOT locked"
        except RuntimeError as e:
            locked_ok = "LOCKED" in str(e)
            locked_detail = str(e)[:120]
        except Exception as e:  # noqa: BLE001
            locked_ok = False
            locked_detail = f"{type(e).__name__}: {e}"[:120]
        check('BrainFactory {"brain": "live"} -> RuntimeError '
              '(production LOCKED)',
              locked_ok, locked_detail)

        # (b) {"brain": "development"} -> LiveBrainAdapter x2, dev mode.
        dev_cfg = _temp_config("development", _dev_extra())
        try:
            agency_dev = BrainFactory.get_brain(
                "agency", config_path=dev_cfg)
            content_dev = BrainFactory.get_brain(
                "content", config_path=dev_cfg)
            h_a = agency_dev.health()
            h_c = content_dev.health()
            dev_ok = (type(agency_dev).__name__ == "LiveBrainAdapter"
                      and type(content_dev).__name__ == "LiveBrainAdapter"
                      and h_a.get("brain_kind") == "development"
                      and h_c.get("brain_kind") == "development"
                      and h_a["calls"] == 0 and h_c["calls"] == 0)
            dev_detail = (f"agency={type(agency_dev).__name__}, "
                          f"content={type(content_dev).__name__}, "
                          f"brain_kind={h_a.get('brain_kind')}")
        except Exception as e:  # noqa: BLE001
            dev_ok = False
            dev_detail = f"{type(e).__name__}: {e}"[:120]
        check("BrainFactory development temp config -> LiveBrainAdapter "
              "x2, brain_kind development, 0 calls",
              dev_ok, dev_detail)

        # (c) bad mode still raises ValueError.
        bad_cfg = _temp_config("bogus")
        try:
            BrainFactory.get_brain("agency", config_path=bad_cfg)
            bad_ok = False
        except ValueError:
            bad_ok = True
        check("BrainFactory bad mode raises ValueError",
              bad_ok, f"bad-raises={bad_ok}")
    except Exception as e:  # noqa: BLE001
        for name in ('BrainFactory {"brain": "live"} -> RuntimeError '
                     '(production LOCKED)',
                     "BrainFactory development temp config -> "
                     "LiveBrainAdapter x2, brain_kind development, 0 calls",
                     "BrainFactory bad mode raises ValueError"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 8. BrainFactory mock-mode temp config -> each dept's own mock.
    try:
        from brain import BrainFactory  # noqa: PLC0415

        mock_cfg = _temp_config("mock")
        agency_brain = BrainFactory.get_brain("agency", config_path=mock_cfg)
        content_brain = BrainFactory.get_brain("content", config_path=mock_cfg)
        ok = (type(agency_brain).__name__ == "MockLLMProvider"
              and agency_brain.complete("smoke").startswith("MOCK-PLAN")
              and type(content_brain).__name__ == "MockLLM"
              and content_brain.complete("smoke").startswith("[MOCK DRAFT"))
        check("BrainFactory mock-mode temp config -> each dept's own mock",
              ok, f"agency={type(agency_brain).__name__}, "
              f"content={type(content_brain).__name__}")
    except Exception as e:  # noqa: BLE001
        check("BrainFactory mock-mode temp config -> each dept's own mock",
              False, str(e))

    # 9. No secrets in the live-brain files.
    # (This check file itself is excluded: it holds the pattern
    # literal — the same self-reference the voice check notes.)
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]|api_key\s*=|password\s*=|"
            r"Authorization.{0,20}Bearer [A-Za-z0-9]")
        bad = []
        for rel in ("00-CEO-Core/live_brain.py", "00-CEO-Core/brain.py"):
            path = os.path.join(BASE, rel)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if secret_re.search(line):
                        bad.append(f"{rel}:{lineno}")
        check("no secrets in live_brain.py / brain.py",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in live_brain.py / brain.py", False, str(e))

    # 10. Real store unchanged by this check run.
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 11. Real guard log untouched (stub runs log to a temp file).
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
    print("check_live_brain: ALL PASS (mock mode — no live call made).")
    return 0


# Env var holding each free dev provider's key (names only — a key
# value is never read here except by the provider at call time).
_DEV_KEY_VARS = {"gemini": "GEMINI_API_KEY",
                 "openrouter": "OPENROUTER_API_KEY"}


def live_probe():
    """The ONE sanctioned live probe — only with --live, on Boss's PC.

    Dev-brain path: the free tier (Gemini gemini-3.5-flash-lite, or
    the model scripts/setup_brain.py saved) through
    BrainFactory.get_brain("agency") with a temp config mirroring the
    REAL config's development_brain block. The real config's brain
    flag is never flipped. One tiny call (max 30 tokens), never
    retries. PASS (exit 0) only if health mode is "live" AND
    brain_kind is "development". The key gate is derived from the dev
    chain itself: the probe runs when a key is set for any provider
    in the chain, so an OpenRouter-only setup is provable too.
    """
    from brain import BrainFactory  # noqa: PLC0415

    with open(os.path.join(CEO_CORE_DIR, "config.json"),
              encoding="utf-8") as f:
        real_cfg = json.load(f)
    dev_block = real_cfg.get("development_brain") or {}
    chain = [str(e) for e in dev_block.get("fallback_chain") or []]
    needed = {}
    for entry in chain:
        name = entry.partition(":")[0].strip().lower()
        var = _DEV_KEY_VARS.get(name)
        if var:
            needed[name] = var
    # Ollama needs no key: when the chain has an ollama entry, the
    # probe runs without any key (the adapter tries the local server
    # first; if it is down, the keyed providers fail loudly and the
    # probe reports FAILED with the exact reasons).
    has_ollama = any(
        e.partition(":")[0].strip().lower() == "ollama" for e in chain)
    if needed and not has_ollama and not any(
            os.environ.get(var) for var in needed.values()):
        print("[live-probe] No key is set for the dev chain "
              f"({', '.join(sorted(set(needed.values())))}) — "
              "no call attempted.")
        print("[live-probe] Setup steps (Boss's PC, Windows):")
        print("[live-probe] LOCAL (no key): install Ollama "
              "https://ollama.com, then: ollama pull gemma4:12b")
        print("[live-probe] 1. Get a free key (no card, no billing): "
              "https://aistudio.google.com/apikey")
        print('[live-probe] 2. Set it, then open a NEW terminal: '
              'setx GEMINI_API_KEY "paste-key-here"')
        print("[live-probe]    (or an OpenRouter key: "
              "https://openrouter.ai/keys -> "
              'setx OPENROUTER_API_KEY "paste-key-here")')
        print("[live-probe] 3. Find a working free model (no JSON editing): "
              "python scripts\\setup_brain.py")
        print("[live-probe] 4. Then run: "
              "python scripts\\check_live_brain.py --live")
        return 1

    print(f"[live-probe] dev chain: {chain}")
    temp_cfg = _temp_config("development",
                            {"development_brain": dev_block})
    adapter = BrainFactory.get_brain("agency", config_path=temp_cfg)
    prompt = "Reply in 5 words: what does Talvenor Master OS do?"
    t0 = time.time()
    text = adapter.complete(prompt, max_tokens=30)
    dt = time.time() - t0
    health = adapter.health()
    try:
        tokens = adapter.live.health()
    except Exception:  # noqa: BLE001
        tokens = {}
    print(f"[live-probe] reply: {text}")
    print(f"[live-probe] latency: {dt:.1f}s")
    print(f"[live-probe] usage: prompt={tokens.get('prompt_tokens')} "
          f"completion={tokens.get('completion_tokens')} "
          f"total={tokens.get('total_tokens')}")
    print(f"[live-probe] mode: {health['mode']}")
    print(f"[live-probe] brain_kind: {health.get('brain_kind')}")
    print(f"[live-probe] tried models: {health.get('models')}")
    if health["mode"] == "live" and health.get("brain_kind") == "development":
        print("[live-probe] PASS: free-tier dev brain works via "
              f"the adapter (live model: {health.get('model')}).")
        return 0
    print(f"[live-probe] FAILED: mode={health['mode']}, "
          f"brain_kind={health.get('brain_kind')}, "
          f"tried={health.get('models')}, "
          f"last_failure={health['last_failure']}")
    return 1


if __name__ == "__main__":
    if "--live" in sys.argv:
        sys.exit(live_probe())
    print("live probe skipped (run with --live for the one sanctioned probe).")
    sys.exit(main())
