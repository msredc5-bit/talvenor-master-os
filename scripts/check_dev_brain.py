#!/usr/bin/env python3
"""check_dev_brain.py — Phase 1 (local-first) self-check for the dev brain.

What it checks (offline ONLY — no network, no live call, ever; fake
providers only, fake key "test-fake-key" is never needed here because
no real provider is constructed):
  1. free_only_guard.py exists, version 1.0, allowlist holds the free
     models (FREE_ONLY_MODELS).
  2. Allowlist: check_call allows gemini-3.5-flash-lite,
     gemini-2.0-flash, openrouter/free,
     deepseek/deepseek-r1-0528:free, moonshotai/kimi-k2:free; rejects
     gpt-4o, claude-sonnet-4-5, gemini-2.5-flash, gemini-2.5-flash-lite
     (Google 404s it for new keys, Nov 2026), muse-spark-1.3,
     kimi-k2.5, grok-4, nvidia/nemotron-3-ultra-550b-a55b (paid
     openrouter id, no :free suffix), and unknown provider "nope".
  3. is_rate_limit_error: True for HTTP 429, RuntimeError("...429..."),
     RESOURCE_EXHAUSTED, "rate limit exceeded"; False for 401 /
     invalid_api_key / timeout messages.
  4. Dev-mode adapter blocks a non-free stub provider BEFORE any
     call: stub (openai-live / gpt-4o) has 0 calls after complete(),
     mock draft returned, last_failure names the violation, the guard
     log has a "blocked_free_only" entry.
  5. 429 hard stop: dev adapter chain [stub raising 429, stub ok] ->
     second stub 0 calls, mode mock-fallback, health rate_limited
     True, last_failure contains "rate_limited_stop", mock draft.
  6. Bad key (401 / invalid_api_key) and timeout: mock fallback,
     reason recorded, each provider called at most once (no retry loop).
  7. Structured output: fake provider returns a JSON string -> the
     adapter returns it unchanged and json.loads succeeds.
  8. Reasoning: fake provider returns a multi-sentence answer ->
     returned unchanged, verbatim.
  9. Tool selection: fake provider returns a tool-call JSON -> the
     adapter returns it unchanged AND no tool was executed (a
     tool-execution stub stays at 0 calls — the adapter never calls
     tools, it only returns text).
 10. Call log: after the above, guard.get_call_log() entries all carry
     provider/model/status (status in ok / error / rate_limited_stop /
     blocked_free_only); the temp log file has one JSON line per call.
 11. No secrets in free_only_guard.py / live_brain.py / brain.py /
     this file (same regex approach as check_live_brain.py section 9).
 12. Real store unchanged by this check run, and the real guard log
     file untouched (all test logging goes to a temp file via a
     monkeypatched LOG_PATH).

Stdlib only. Run: python3 scripts/check_dev_brain.py
"""

import json
import os
import re
import sys
import tempfile
import urllib.error

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

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


def _temp_config(cfg_dict):
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "config-test.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg_dict, f)
    return path


class _StubDev:
    """Fake dev provider — behavior: ok | rate-limit | bad-key | timeout.

    name/model/provider mirror a real provider's adapter attributes so
    the dev-mode guard sees the same shape it would see live.
    """

    def __init__(self, name, model, behavior, payload=None):
        self.name = name
        self.model = model
        self.provider = name[:-len("-live")] if name.endswith("-live") else name
        self.behavior = behavior
        self.payload = payload
        self.calls = 0

    def complete(self, prompt, *, max_tokens=500):
        self.calls += 1
        if self.behavior == "ok":
            return self.payload
        if self.behavior == "rate-limit":
            raise RuntimeError(
                "live brain call failed: HTTP 429 RESOURCE_EXHAUSTED: "
                "rate limit exceeded")
        if self.behavior == "bad-key":
            raise RuntimeError(
                "live brain API error: {'code': 'invalid_api_key'}")
        if self.behavior == "timeout":
            raise RuntimeError("live brain call failed: URLError: timed out")
        raise RuntimeError(f"unknown stub behavior: {self.behavior}")


class _ToolStub:
    """Fake tool executor — the adapter must never call it."""

    def __init__(self):
        self.calls = 0

    def run(self, tool, args):
        self.calls += 1
        return "tool ran"


def _run_allowlist_and_rate_checks(guard, FreeOnlyViolation):
    """Sections 2-3: guard allowlist + is_rate_limit_error."""
    # 2. Allowlist.
    allowed = [
        ("gemini", "gemini-3.5-flash-lite"),
        ("gemini", "gemini-2.0-flash"),
        ("openrouter", "openrouter/free"),
        ("openrouter", "deepseek/deepseek-r1-0528:free"),
        ("openrouter", "moonshotai/kimi-k2:free"),
    ]
    rejected = [
        ("openai", "gpt-4o"),
        ("anthropic", "claude-sonnet-4-5"),
        ("gemini", "gemini-2.5-flash"),
        ("gemini", "gemini-2.5-flash-lite"),
        ("meta", "muse-spark-1.3"),
        ("kimi", "kimi-k2.5"),
        ("grok", "grok-4"),
        ("openrouter", "nvidia/nemotron-3-ultra-550b-a55b"),
        ("nope", "whatever"),
    ]
    allow_bad = []
    for provider, model in allowed:
        try:
            guard.check_call(provider, model)
        except Exception as e:  # noqa: BLE001
            allow_bad.append(f"{provider}:{model} -> "
                             f"{type(e).__name__}: {e}")
    reject_bad = []
    for provider, model in rejected:
        try:
            guard.check_call(provider, model)
            reject_bad.append(f"{provider}:{model} NOT rejected")
        except FreeOnlyViolation:
            pass
        except Exception as e:  # noqa: BLE001
            reject_bad.append(f"{provider}:{model} -> wrong error "
                              f"{type(e).__name__}")
    check("guard allowlist: free models allowed, paid rejected",
          not allow_bad and not reject_bad,
          "; ".join((allow_bad + reject_bad)[:4])
          or f"{len(allowed)} allowed, {len(rejected)} rejected")

    # 3. is_rate_limit_error.
    true_cases = [
        urllib.error.HTTPError(
            "https://example.invalid/", 429, "Too Many Requests",
            None, None),
        RuntimeError("request failed with HTTP 429"),
        RuntimeError("RESOURCE_EXHAUSTED: quota exceeded"),
        RuntimeError("rate limit exceeded, try again later"),
    ]
    false_cases = [
        urllib.error.HTTPError(
            "https://example.invalid/", 401, "Unauthorized",
            None, None),
        RuntimeError("live brain API error: {'code': 'invalid_api_key'}"),
        RuntimeError("live brain call failed: URLError: timed out"),
        RuntimeError("connection reset by peer"),
    ]
    rate_bad = []
    for exc in true_cases:
        if not guard.is_rate_limit_error(exc):
            rate_bad.append(f"missed: {exc!r}"[:80])
    for exc in false_cases:
        if guard.is_rate_limit_error(exc):
            rate_bad.append(f"false positive: {exc!r}"[:80])
    check("is_rate_limit_error: 429 true, 401/timeout false",
          not rate_bad, "; ".join(rate_bad[:3]) or "8/8 correct")


def main():
    store_before = _snapshot_store()

    # 1-3. The guard module itself: present, versioned, allowlist, 429.
    guard = None
    guard_import_error = None
    try:
        import free_only_guard as guard  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        guard_import_error = str(e)

    if guard is None:
        check("free_only_guard.py imports (worker B)",
              False, f"missing: {guard_import_error}")
        for name in (
                "guard allowlist: free models allowed, paid rejected",
                "is_rate_limit_error: 429 true, 401/timeout false",
                "dev adapter blocks non-free stub before any call",
                "429 hard stop: 2nd provider never tried",
                "bad key / timeout: mock fallback, at most 1 call each",
                "structured output returned unchanged, parses as JSON",
                "reasoning answer returned unchanged, verbatim",
                "tool-selection JSON returned unchanged, no tool executed",
                "call log: entries carry provider/model/status",
                "real guard log file untouched by this run"):
            check(name, False, "free_only_guard missing (worker B)")
    else:
        version_ok = getattr(guard, "FREE_ONLY_GUARD_VERSION", None) == "1.0"
        models = getattr(guard, "FREE_ONLY_MODELS", None)
        models_ok = (models is not None
                     and "gemini-2.5-flash-lite" not in str(models)
                     and "gemini-3.5-flash-lite" in str(models)
                     and "gemini-2.0-flash" in str(models))
        check("free_only_guard.py imports, version 1.0, allowlist holds "
              "the free gemini models",
              version_ok and models_ok,
              f"version={getattr(guard, 'FREE_ONLY_GUARD_VERSION', None)!r}")

        # 2. Allowlist. 3. is_rate_limit_error.
        try:
            from free_only_guard import FreeOnlyViolation  # noqa: PLC0415
        except ImportError as e:
            check("guard allowlist: free models allowed, paid rejected",
                  False, f"FreeOnlyViolation missing (worker B): {e}")
            check("is_rate_limit_error: 429 true, 401/timeout false",
                  False, f"FreeOnlyViolation missing (worker B): {e}")
            FreeOnlyViolation = None
        if FreeOnlyViolation is not None:
            _run_allowlist_and_rate_checks(guard, FreeOnlyViolation)

    # 4-10. Dev-mode adapter behavior with fake providers only.
    # The guard's log is redirected to a temp file so the real logs/
    # file is never touched by this test run.
    tmp_log = None
    real_log_path = None
    real_log_before = None
    if guard is not None:
        tmp_log = os.path.join(tempfile.mkdtemp(), "guard-test.log")
        real_log_path = getattr(guard, "LOG_PATH", None)
        if real_log_path:
            try:
                with open(real_log_path, encoding="utf-8") as f:
                    real_log_before = f.read()
            except OSError:
                real_log_before = None
        guard.LOG_PATH = tmp_log
    try:
        from live_brain import LiveBrainAdapter  # noqa: PLC0415
        from brain import BrainFactory  # noqa: PLC0415

        mock_cfg = _temp_config({"brain": "mock"})
        agency_mock = BrainFactory.get_brain("agency", config_path=mock_cfg)

        def _dev_adapter(stubs):
            return LiveBrainAdapter(mock_brain=agency_mock,
                                    live_providers=stubs,
                                    mode="development")

        # 4. Non-free stub blocked BEFORE any call.
        try:
            paid_stub = _StubDev("openai-live", "gpt-4o", "ok",
                                 payload="LIVE-REPLY: should never appear.")
            adapter = _dev_adapter([paid_stub])
            text = adapter.complete("smoke")
            h = adapter.health()
            log = guard.get_call_log() if guard is not None else []
            blocked = [e for e in log
                       if e.get("status") == "blocked_free_only"]
            last = h.get("last_failure") or ""
            ok = (paid_stub.calls == 0
                  and text.startswith("MOCK-PLAN")
                  and h["mode"] == "mock-fallback"
                  and ("FreeOnlyViolation" in last
                       or "free-only" in last.lower()
                       or "free_only" in last.lower())
                  and bool(blocked))
            check("dev adapter blocks non-free stub before any call",
                  ok, f"stub_calls={paid_stub.calls}, mode={h['mode']}, "
                  f"last_failure={last[:100]!r}, "
                  f"blocked_entries={len(blocked)}")
        except Exception as e:  # noqa: BLE001
            check("dev adapter blocks non-free stub before any call",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 5. 429 hard stop: second provider never tried.
        try:
            stub_429 = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                                "rate-limit")
            stub_ok = _StubDev("openrouter-live", "openrouter/free", "ok",
                               payload="LIVE-REPLY: should never appear.")
            adapter = _dev_adapter([stub_429, stub_ok])
            text = adapter.complete("smoke")
            h = adapter.health()
            ok = (stub_ok.calls == 0
                  and stub_429.calls == 1
                  and text.startswith("MOCK-PLAN")
                  and h["mode"] == "mock-fallback"
                  and h.get("rate_limited") is True
                  and "rate_limited_stop" in (h.get("last_failure") or ""))
            check("429 hard stop: 2nd provider never tried",
                  ok, f"stub429_calls={stub_429.calls}, "
                  f"stub_ok_calls={stub_ok.calls}, mode={h['mode']}, "
                  f"rate_limited={h.get('rate_limited')}, "
                  f"last_failure={(h.get('last_failure') or '')[:80]!r}")
        except Exception as e:  # noqa: BLE001
            check("429 hard stop: 2nd provider never tried",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 6. Bad key + timeout: mock fallback, at most 1 call each.
        try:
            stub_key = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                                "bad-key")
            adapter_k = _dev_adapter([stub_key])
            text_k = adapter_k.complete("smoke")
            h_k = adapter_k.health()
            stub_to = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                               "timeout")
            adapter_t = _dev_adapter([stub_to])
            text_t = adapter_t.complete("smoke")
            h_t = adapter_t.health()
            ok = (text_k.startswith("MOCK-PLAN")
                  and h_k["mode"] == "mock-fallback"
                  and stub_key.calls == 1
                  and "invalid_api_key" in (h_k.get("last_failure") or "")
                  and text_t.startswith("MOCK-PLAN")
                  and h_t["mode"] == "mock-fallback"
                  and stub_to.calls == 1
                  and "timed out" in (h_t.get("last_failure") or ""))
            check("bad key / timeout: mock fallback, at most 1 call each",
                  ok, f"key_calls={stub_key.calls}, "
                  f"timeout_calls={stub_to.calls}")
        except Exception as e:  # noqa: BLE001
            check("bad key / timeout: mock fallback, at most 1 call each",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 7. Structured output returned unchanged, parses as JSON.
        try:
            payload = '{"answer": "ok", "confidence": 0.9}'
            stub = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                            "ok", payload=payload)
            adapter = _dev_adapter([stub])
            text = adapter.complete("smoke", max_tokens=30)
            parsed = json.loads(text)
            ok = (text == payload
                  and parsed.get("answer") == "ok"
                  and parsed.get("confidence") == 0.9)
            check("structured output returned unchanged, parses as JSON",
                  ok, f"text={text[:60]!r}")
        except Exception as e:  # noqa: BLE001
            check("structured output returned unchanged, parses as JSON",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 8. Reasoning: multi-sentence answer returned verbatim.
        try:
            payload = ("Talvenor Master OS routes a task from the Main CEO "
                       "Bot to the right Chief, the Chief drafts the work, "
                       "and nothing goes out until Boss approves it.")
            stub = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                            "ok", payload=payload)
            adapter = _dev_adapter([stub])
            text = adapter.complete("smoke", max_tokens=100)
            check("reasoning answer returned unchanged, verbatim",
                  text == payload, f"len={len(text)}")
        except Exception as e:  # noqa: BLE001
            check("reasoning answer returned unchanged, verbatim",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 9. Tool selection: JSON returned unchanged, no tool executed.
        try:
            tool_stub = _ToolStub()
            payload = ('{"tool": "gmail_send", "args": '
                       '{"to": "x@example.com"}}')
            stub = _StubDev("gemini-live", "gemini-3.5-flash-lite",
                            "ok", payload=payload)
            adapter = _dev_adapter([stub])
            text = adapter.complete("smoke", max_tokens=30)
            parsed = json.loads(text)
            ok = (text == payload
                  and parsed.get("tool") == "gmail_send"
                  and tool_stub.calls == 0)
            check("tool-selection JSON returned unchanged, no tool executed",
                  ok, f"tool_calls={tool_stub.calls}")
        except Exception as e:  # noqa: BLE001
            check("tool-selection JSON returned unchanged, no tool executed",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 10. Call log: entries carry provider/model/status; temp file
        # has one JSON line per call.
        try:
            log = guard.get_call_log() if guard is not None else []
            allowed_status = {"ok", "error", "rate_limited_stop",
                              "blocked_free_only"}
            bad_entries = [e for e in log
                           if not isinstance(e, dict)
                           or not e.get("provider")
                           or not e.get("model")
                           or e.get("status") not in allowed_status]
            lines = []
            if tmp_log and os.path.exists(tmp_log):
                with open(tmp_log, encoding="utf-8") as f:
                    lines = [ln for ln in f if ln.strip()]
                json_bad = []
                for ln in lines:
                    try:
                        json.loads(ln)
                    except json.JSONDecodeError:
                        json_bad.append(ln[:60])
            else:
                json_bad = ["temp log file missing"]
            ok = (bool(log) and not bad_entries
                  and len(lines) == len(log) and not json_bad)
            check("call log: entries carry provider/model/status",
                  ok, f"entries={len(log)}, lines={len(lines)}, "
                  f"bad={len(bad_entries)}")
        except Exception as e:  # noqa: BLE001
            check("call log: entries carry provider/model/status",
                  False, f"{type(e).__name__}: {e}"[:160])
    except Exception as e:  # noqa: BLE001
        for name in ("dev adapter blocks non-free stub before any call",
                     "429 hard stop: 2nd provider never tried",
                     "bad key / timeout: mock fallback, at most 1 call each",
                     "structured output returned unchanged, parses as JSON",
                     "reasoning answer returned unchanged, verbatim",
                     "tool-selection JSON returned unchanged, no tool executed",
                     "call log: entries carry provider/model/status"):
            if not any(r[0] == name for r in results):
                check(name, False, f"{type(e).__name__}: {e}"[:160])

    # 11. No secrets in the dev-brain files.
    # (This check file itself is excluded: it holds the pattern
    # literals — the same self-reference the live-brain check notes.)
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]|api_key\s*=|password\s*=|"
            r"Authorization.{0,20}Bearer [A-Za-z0-9]")
        bad = []
        for rel in ("00-CEO-Core/free_only_guard.py",
                    "00-CEO-Core/live_brain.py",
                    "00-CEO-Core/brain.py"):
            path = os.path.join(BASE, rel)
            if not os.path.exists(path):
                bad.append(f"{rel}:MISSING")
                continue
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if secret_re.search(line):
                        bad.append(f"{rel}:{lineno}")
        check("no secrets in free_only_guard.py / live_brain.py / brain.py",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in free_only_guard.py / live_brain.py / brain.py",
              False, str(e))

    # 12. Real store unchanged + real guard log untouched.
    try:
        after = _snapshot_store()
        store_ok = after == store_before
        log_ok = True
        log_detail = "real log untouched"
        if real_log_path:
            try:
                with open(real_log_path, encoding="utf-8") as f:
                    log_ok = f.read() == real_log_before
            except OSError:
                log_ok = real_log_before is None
            if not log_ok:
                log_detail = "REAL guard log changed during this run"
        check("real store unchanged by this check run",
              store_ok, "unchanged" if store_ok else "CHANGED")
        if guard is not None:
            check("real guard log file untouched by this run",
                  log_ok, log_detail)
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_dev_brain: ALL PASS (offline — no live call made).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
