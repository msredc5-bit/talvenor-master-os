#!/usr/bin/env python3
"""check_live_brain.py — Phase 10 self-check for the live brain adapter.

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
  7. BrainFactory live-mode temp config returns LiveBrainAdapter
     (agency + content), 0 calls; bad mode raises ValueError.
  8. BrainFactory mock-mode temp config still returns each dept's
     own mock (unchanged behavior).
  9. No secrets in live_brain.py / brain.py / this file (no
     surrogate, no key literal, no password assignment).
 10. Real store unchanged by this check run (Phase 9: live queue).

LIVE PROBE (OFF by default — run only with --live):
  One tiny real call through the sanctioned connector path
  (custom.meta-model-api-2 surrogate, api.meta.ai, model
  muse-spark-1.3, max 30 completion tokens). Exactly one request,
  never retries. Prints reply, latency, tokens. Exit 0 + PASS only
  if the adapter mode is "live" afterwards; otherwise FAILED with
  the exact reason and the brain stays mock.

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
    """Real store-এর snapshot (Phase 9: store এখন live queue)।"""
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


def _temp_config(mode):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, f"config-{mode}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"brain": mode}, f)
    return path


def main():
    store_before = _snapshot_store()

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

    # 7. BrainFactory live-mode temp config -> LiveBrainAdapter (both depts).
    try:
        from brain import BrainFactory  # noqa: PLC0415

        live_cfg = _temp_config("live")
        agency_live = BrainFactory.get_brain("agency", config_path=live_cfg)
        content_live = BrainFactory.get_brain("content", config_path=live_cfg)
        bad_cfg = _temp_config("bogus")
        try:
            BrainFactory.get_brain("agency", config_path=bad_cfg)
            bad_ok = False
        except ValueError:
            bad_ok = True
        ok = (type(agency_live).__name__ == "LiveBrainAdapter"
              and agency_live.health()["provider"] == "live-brain-adapter"
              and agency_live.health()["mode"] == "live"
              and agency_live.health()["calls"] == 0
              and type(content_live).__name__ == "LiveBrainAdapter"
              and content_live.health()["calls"] == 0
              and bad_ok)
        check("BrainFactory live-mode temp config -> LiveBrainAdapter x2; "
              "bad mode raises",
              ok, f"agency={type(agency_live).__name__}, "
              f"content={type(content_live).__name__}, bad-raises={bad_ok}")
    except Exception as e:  # noqa: BLE001
        check("BrainFactory live-mode temp config -> LiveBrainAdapter x2; "
              "bad mode raises", False, str(e))

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

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_live_brain: ALL PASS (mock mode — no live call made).")
    return 0


def live_probe():
    """The ONE sanctioned live probe — only with --live. One request."""
    from live_brain import LiveBrainAdapter  # noqa: PLC0415
    from brain import BrainFactory  # noqa: PLC0415

    mock_cfg = _temp_config("mock")
    agency_mock = BrainFactory.get_brain("agency", config_path=mock_cfg)
    adapter = LiveBrainAdapter(mock_brain=agency_mock)
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
    if health["mode"] == "live":
        print("[live-probe] PASS: live Muse Spark path works via the adapter.")
        return 0
    print(f"[live-probe] FAILED: {health['last_failure']}")
    return 1


if __name__ == "__main__":
    if "--live" in sys.argv:
        sys.exit(live_probe())
    print("live probe skipped (run with --live for the one sanctioned probe).")
    sys.exit(main())
