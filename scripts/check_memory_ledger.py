#!/usr/bin/env python3
"""check_memory_ledger.py — Improvement Phase 2 self-check
(quote-verified memory + usage ledger + task check-in).

Owner memory (modelled on Nod's memory.ts):
  1. owner_memory.py imports standalone, fast, no network
  2. seed_defaults: 3 entries, all verify True
  3. Cannot learn without a quote (ValueError)
  4. Learn -> verify True; duplicate slug -> ValueError
  5. Edit with a wrong quote forbidden; correct edit works
  6. archive hides, forget deletes
  7. Entry over 4,000 chars -> ValueError
  8. export_markdown has the seed quotes
  9. verify_all all True
 10. Unknown area/status -> ValueError

Usage ledger (modelled on Nod's ledger.ts, $0 cap):
 11. usage_ledger.py imports standalone, fast, no network
 12. Empty ledger: total $0, check-in False, over cap False
 13. Mock record $0; nonzero cost in mock -> ValueError
 14. Live cost check-in trips + monthly cap trips (cap $0)
 15. task_total differs per task; summary counts correct
 16. spend_report honest ($0.02, YES — STOP)
 17. Dispatcher ledger threading: mock call -> mock receipt $0;
     gated call -> gate receipt; no ledger_error
 18. No secrets in owner_memory.py / usage_ledger.py
 19. Real store unchanged by this check run

All checks run in TEMP files — the real store is only read, never written.
Stdlib only, no network, no spend, no send. Exit 0 = PASS.
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

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _snapshot_store():
    snap = {}
    store_dir = os.path.join(BASE, "store")
    for name in sorted(os.listdir(store_dir)):
        path = os.path.join(store_dir, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    snap[name] = f.read()
            except OSError:
                snap[name] = None
    return snap


def main():
    store_before = _snapshot_store()
    tmp_dir = tempfile.mkdtemp()

    # 1 + 11. Both modules import standalone, fast, no network.
    for mod in ("owner_memory", "usage_ledger"):
        try:
            t0 = time.time()
            proc = subprocess.run(
                [sys.executable, "-I", "-c",
                 "import sys; sys.path.insert(0, "
                 f"{CEO_CORE_DIR!r}); import {mod}; "
                 f"print('{mod} import OK')"],
                capture_output=True, text=True, timeout=30, cwd=BASE)
            elapsed = time.time() - t0
            check(f"{mod}.py imports standalone, fast, no network",
                  proc.returncode == 0 and elapsed < 10,
                  f"{elapsed:.2f}s, rc={proc.returncode}")
        except Exception as e:  # noqa: BLE001
            check(f"{mod}.py imports standalone, fast, no network", False, str(e))

    # 2-10. Owner memory.
    try:
        from owner_memory import OwnerMemory  # noqa: PLC0415

        tmp_mem = os.path.join(tmp_dir, "memory-test.json")
        tmp_md = os.path.join(tmp_dir, "MEMORY-test.md")
        mem = OwnerMemory(memory_path=tmp_mem)

        # 2. Seed: 3, all verify.
        seeded = mem.seed_defaults()
        check("seed_defaults: 3 entries, all quote-verified",
              len(seeded) == 3
              and all(mem.verify(e["area"], e["slug"]) for e in seeded),
              f"seeded={[e['slug'] for e in seeded]}")

        # 3. Cannot learn without a quote.
        try:
            mem.learn("preferences", "bad", "x", quote="Boss never said it",
                      source_message="Boss: Today is a holiday")
            ok_bad = False
        except ValueError:
            ok_bad = True
        check("learn without a verbatim quote -> ValueError", ok_bad)

        # 4. Learn -> verify; duplicate slug -> ValueError.
        e = mem.learn("routines", "test-rule", "Test rule.",
                      quote="do the test",
                      source_message="Boss: do the test, then tell me",
                      source_ref="test")
        ok_learn = mem.verify("routines", "test-rule") is True
        try:
            mem.learn("routines", "test-rule", "Again.", quote="do the test",
                      source_message="Boss: do the test")
            ok_dup = False
        except ValueError:
            ok_dup = True
        check("learn with quote -> verify True; duplicate slug rejected",
              ok_learn and ok_dup)

        # 5. Edit with a wrong quote forbidden; correct edit works.
        try:
            mem.edit("routines", "test-rule", quote="made-up words")
            ok_bad_edit = False
        except ValueError:
            ok_bad_edit = True
        mem.edit("routines", "test-rule", new_text="Test rule (edited).")
        ok_edit = mem.get("routines", "test-rule")["text"] == "Test rule (edited)."
        check("edit with a bad quote rejected; good edit applies",
              ok_bad_edit and ok_edit)

        # 6. Archive hides, forget deletes.
        mem.archive("routines", "test-rule")
        hidden = all(x["slug"] != "test-rule"
                     for x in mem.list_entries(area="routines"))
        shown_archived = any(x["slug"] == "test-rule" for x in
                             mem.list_entries(area="routines", include_archived=True))
        mem.forget("routines", "test-rule")
        try:
            mem.get("routines", "test-rule")
            ok_forget = False
        except KeyError:
            ok_forget = True
        check("archive hides, forget removes",
              hidden and shown_archived and ok_forget)

        # 7. 4,000 chars cap.
        try:
            mem.learn("lessons", "too-long", "x" * 4001, quote="x",
                      source_message="Boss: x")
            ok_cap = False
        except ValueError:
            ok_cap = True
        check("entry over 4000 chars -> ValueError", ok_cap)

        # 8. Seed quotes in the markdown export.
        out = mem.export_markdown(tmp_md)
        with open(out, encoding="utf-8") as f:
            md = f.read()
        check("markdown export contains the seed quotes",
              "Mira" in md and "Bengali" in md and "post it" in md
              and "NOT permission" in md)

        # 9. verify_all all True.
        check("verify_all: every active entry verifies",
              all(mem.verify_all().values()) and len(mem.verify_all()) == 3,
              str(mem.verify_all()))

        # 10. Unknown area/status -> ValueError.
        try:
            mem.learn("nowhere", "x", "y", quote="y", source_message="Boss: y")
            ok_area = False
        except ValueError:
            ok_area = True
        try:
            mem.learn("about", "x", "y", quote="y", source_message="Boss: y",
                      status="bogus")
            ok_status = False
        except ValueError:
            ok_status = True
        check("unknown area/status -> ValueError", ok_area and ok_status)
    except Exception as e:  # noqa: BLE001
        for name in ("seed_defaults: 3 entries, all quote-verified",
                     "learn without a verbatim quote -> ValueError",
                     "learn with quote -> verify True; duplicate slug rejected",
                     "edit with a bad quote rejected; good edit applies",
                     "archive hides, forget removes",
                     "entry over 4000 chars -> ValueError",
                     "markdown export contains the seed quotes",
                     "verify_all: every active entry verifies",
                     "unknown area/status -> ValueError"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 12-17. Usage ledger.
    try:
        from usage_ledger import UsageLedger  # noqa: PLC0415

        tmp_ledger = os.path.join(tmp_dir, "usage_ledger-test.json")
        ledger = UsageLedger(ledger_path=tmp_ledger)

        # 12. Empty ledger.
        check("empty ledger: $0 total, no check-in, not over cap",
              ledger.monthly_total() == 0.0
              and ledger.check_in_required("job-1") is False
              and ledger.over_monthly_cap() is False
              and ledger.monthly_cap_usd == 0.0)

        # 13. Mock $0; nonzero cost in mock -> ValueError.
        e = ledger.record("mock", "mock", "mock", cost_usd=0.0,
                          task_id="job-1", action="draft_email")
        ok_mock = e["cost_usd"] == 0.0 and ledger.monthly_total() == 0.0
        try:
            ledger.record("mock", "mock", "mock", cost_usd=0.01)
            ok_mock_cost = False
        except ValueError:
            ok_mock_cost = True
        check("mock record is $0; mock with a cost rejected",
              ok_mock and ok_mock_cost)

        # 14. Live cost trips check-in + monthly cap.
        ledger.record("live", "openrouter", "openrouter/free",
                      prompt_tokens=100, completion_tokens=50, cost_usd=0.02,
                      task_id="job-2", action="draft_email")
        check("live cost trips task check-in + monthly cap (cap $0)",
              ledger.check_in_required("job-2") is True
              and ledger.over_monthly_cap() is True
              and ledger.monthly_total() == 0.02)

        # 15. task_total + summary.
        s = ledger.summary()
        check("task totals separate; summary counts right",
              ledger.task_total("job-2") == 0.02
              and ledger.task_total("job-1") == 0.0
              and s["total_calls"] == 2 and s["total_usd"] == 0.02
              and s["by_kind"] == {"mock": 1, "live": 1}, str(s))

        # 16. spend_report honest.
        report = ledger.spend_report()
        check("spend_report is honest ($0.02, YES — STOP)",
              "$0.02" in report and "YES — STOP" in report, report.replace("\n", " | "))

        # 17. Dispatcher ledger threading.
        import tool_calling  # noqa: PLC0415

        tmp_appr = os.path.join(tmp_dir, "approvals-test.json")
        tmp_log = os.path.join(tmp_dir, "tool_calls-test.json")
        tmp_ledger2 = os.path.join(tmp_dir, "usage_ledger2-test.json")
        registry = tool_calling.ToolRegistry.load_from_json(
            os.path.join(CEO_CORE_DIR, "tools.json"))
        r1 = tool_calling.call_tool(
            "draft_email", {"business_name": "ABC Plumbing", "topic": "missed calls"},
            context={"task_id": "job-9"}, registry=registry,
            approvals_path=tmp_appr, calls_log_path=tmp_log,
            ledger_path=tmp_ledger2)
        r2 = tool_calling.call_tool(
            "gmail_send", {"to": "t@example.com", "subject": "Hi", "body": "Hello"},
            registry=registry, approvals_path=tmp_appr, calls_log_path=tmp_log,
            ledger_path=tmp_ledger2)
        led2 = UsageLedger(ledger_path=tmp_ledger2)
        kinds = [rec["kind"] for rec in led2.records]
        check("dispatcher ledger threading: mock + gate receipts, $0, no ledger_error",
              r1["status"] == "draft-ready" and r2["status"] == "pending-approval"
              and kinds == ["mock", "gate"]
              and led2.monthly_total() == 0.0
              and led2.records[0]["task_id"] == "job-9"
              and "ledger_error" not in r1 and "ledger_error" not in r2,
              f"kinds={kinds}")
    except Exception as e:  # noqa: BLE001
        for name in ("empty ledger: $0 total, no check-in, not over cap",
                     "mock record is $0; mock with a cost rejected",
                     "live cost trips task check-in + monthly cap (cap $0)",
                     "task totals separate; summary counts right",
                     "spend_report is honest ($0.02, YES — STOP)",
                     "dispatcher ledger threading: mock + gate receipts, $0, no ledger_error"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 18. No secrets.
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]|api_key\s*=|password\s*=|"
            r"Authorization.{0,20}Bearer [A-Za-z0-9]")
        bad = []
        for rel in ("00-CEO-Core/owner_memory.py", "00-CEO-Core/usage_ledger.py"):
            path = os.path.join(BASE, rel)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if secret_re.search(line):
                        bad.append(f"{rel}:{lineno}")
        check("no secrets in owner_memory.py / usage_ledger.py",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in owner_memory.py / usage_ledger.py", False, str(e))

    # 19. Real store unchanged.
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
    print("check_memory_ledger: ALL PASS (Improvement Phase 2 — memory + ledger).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
