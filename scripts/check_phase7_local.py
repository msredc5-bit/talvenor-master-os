#!/usr/bin/env python3
"""check_phase7_local.py — Local-first Phase 7 self-check for the
control plane + approval centre + dashboard/CEO-report wiring
(Worker C).

What it checks (offline ONLY — no network, no live call, ever;
$0; no live send/deploy anywhere):

  1. control.py loads a missing file as running (never an exception).
  2. pause halts the drain consult AND the scheduler due checks
     (should_run_job False, due_jobs all not-due); resume restores due.
  3. resume restores running; an emergency_stop survives resume
     (resume refuses while it is set); clearing it restores running.
  4. clear_emergency_stop needs a non-empty reason (empty/blank
     raises; the stop stays set).
  5. Corrupt control.json halts fail-closed: consult raises
     ControlCorruptError, and the REAL run_office.py drain on a temp
     store exits 0 with the task intact + a control_halt audit note.
  6. Approval centre lists pending via the REAL gateway (age/expiry
     present, allowed gate words correct).
  7. Approve with the wrong gate word raises (gateway's own error);
     approve with the right word records approved (decided_by Boss).
  8. Reject records rejected; an expired record cannot be approved.
  9. Dashboard: sync_status.py on a temp copy shows the new Phase 7
     keys (departments / task_counts / approvals / control /
     ceo_report) AND the seeded numbers match (2 tasks: 1 done +
     1 queued; 1 pending approval; paused control state; 8
     departments) — SKIPPED (not failed) while Worker A's dashboard
     extension has not landed.
 10. CEO report generation (Worker B's generator) produces a report
     whose numbers match a seeded temp store (2 tasks, 1 done +
     1 queued, 1 pending approval; Markdown twin carries the same
     numbers; the temp store is untouched) — SKIPPED (not failed)
     while Worker B's ceo_reporting package has not landed.
 11. Real store files unchanged (sha256 of store/tasks.json,
     store/approvals.json, store/leads.json before/after).

Stdlib only. Every temp store is a per-run tempfile.mkdtemp() dir
(never a fixed /tmp path — the Phase 5 check-7 isolation lesson).
A check that cannot run because Worker A/B output has not landed
yet is marked SKIPPED in its output, never faked as a pass.
Exit 0 = no FAIL (SKIPPED checks are reported, not hidden).

Run: python3 scripts/check_phase7_local.py
"""

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
STORE_DIR = os.path.join(BASE, "store")
RUNNER = os.path.join(BASE, "scripts", "run_office.py")

sys.path.insert(0, CEO_CORE_DIR)

results = []


def check(name, ok, detail=""):
    results.append((name, "PASS" if ok else "FAIL", detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))


def skipped(name, reason):
    results.append((name, "SKIPPED", reason))
    print(f"[SKIPPED] {name} — {reason}")


def _sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _store_hashes():
    return {name: _sha256_file(os.path.join(STORE_DIR, name))
            for name in ("tasks.json", "approvals.json", "leads.json")}


def _load_sync_status():
    """Load scripts/sync_status.py by path (no repo-wide side effects
    beyond its module import). Returns the module."""
    path = os.path.join(BASE, "scripts", "sync_status.py")
    spec = importlib.util.spec_from_file_location(
        "phase7_sync_status", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    hashes_before = _store_hashes()

    from control import (  # noqa: E402
        ControlCorruptError,
        ControlRefused,
        ControlState,
        consult,
    )
    from approval_centre import ApprovalCentre  # noqa: E402
    from human_approval_gateway import ApprovalGateway  # noqa: E402
    from workflow_engine import scheduler  # noqa: E402
    from quiet_schedules import ScheduleStore  # noqa: E402

    # 1. Missing control file loads as running, never an exception.
    try:
        tmp = tempfile.mkdtemp()
        cs = ControlState(control_path=os.path.join(tmp, "control.json"))
        loaded = cs.load()
        ok = (loaded["paused"] is False
              and loaded["emergency_stop"] is False
              and loaded["schema"] == "control-v1"
              and cs.is_halted() is False
              and cs.halt_reason() is None
              and consult(os.path.join(tmp, "control.json")) == (False, None))
        check("control loads a missing file as running",
              ok, "paused=False, emergency_stop=False, consult=(False, None)")
    except Exception as e:  # noqa: BLE001
        check("control loads a missing file as running", False, str(e))

    # 2. Pause halts the drain consult + scheduler due checks.
    try:
        tmp = tempfile.mkdtemp()
        store = ScheduleStore(
            schedules_path=os.path.join(tmp, "schedules.json"))
        scheduler.create_paused_jobs(store)
        approval = {"approval_id": "APR-P7-1", "approver": "Boss",
                    "decision": "approved",
                    "scope": "scheduler-activation:weekly-ceo-report"}
        scheduler.activate_job(store, "weekly-ceo-report", approval)
        due_before, _ = scheduler.should_run_job(
            store, "weekly-ceo-report", {"tasks": ["a"]})
        cs = ControlState(control_path=os.path.join(tmp, "control.json"))
        cs.pause("Phase 7 check 2 — hold the queue", set_by="Boss")
        halted, reason = consult(os.path.join(tmp, "control.json"))
        due_after, reason_after = scheduler.should_run_job(
            store, "weekly-ceo-report", {"tasks": ["a"]})
        due_list = scheduler.due_jobs(store)
        cs.resume("Phase 7 check 2 — back to work", set_by="Boss")
        due_restored, _ = scheduler.should_run_job(
            store, "weekly-ceo-report", {"tasks": ["a"]})
        ok = (due_before is True and halted is True
              and "paused" in (reason or "")
              and due_after is False and "control halted" in reason_after
              and all(not d["due"] for d in due_list)
              and due_restored is True)
        check("pause halts drain consult + scheduler due; resume restores",
              ok, f"due_before={due_before}, halted={halted}, "
              f"due_paused={due_after}, due_jobs_all_not_due="
              f"{all(not d['due'] for d in due_list)}, "
              f"due_restored={due_restored}")
    except Exception as e:  # noqa: BLE001
        check("pause halts drain consult + scheduler due; resume restores",
              False, str(e))

    # 3. Emergency stop survives resume; clearing restores running.
    try:
        tmp = tempfile.mkdtemp()
        cs = ControlState(control_path=os.path.join(tmp, "control.json"))
        cs.pause("hold", set_by="Boss")
        cs.emergency_stop("stop everything", set_by="Boss")
        refused = False
        try:
            cs.resume("try to resume", set_by="Boss")
        except ControlRefused:
            refused = True
        mid = cs.load()
        cs.clear_emergency_stop("all clear", set_by="Boss")
        after_clear = cs.load()
        cs.resume("back to work", set_by="Boss")
        final = cs.load()
        ok = (refused is True and mid["emergency_stop"] is True
              and after_clear["emergency_stop"] is False
              and after_clear["paused"] is True
              and final["paused"] is False
              and final["emergency_stop"] is False)
        check("emergency_stop survives resume; clear restores running",
              ok, f"resume_refused={refused}, stop_survived="
              f"{mid['emergency_stop']}, pause_kept_after_clear="
              f"{after_clear['paused']}, final_running="
              f"{not final['paused'] and not final['emergency_stop']}")
    except Exception as e:  # noqa: BLE001
        check("emergency_stop survives resume; clear restores running",
              False, str(e))

    # 4. clear_emergency_stop needs a non-empty reason.
    try:
        tmp = tempfile.mkdtemp()
        cs = ControlState(control_path=os.path.join(tmp, "control.json"))
        cs.emergency_stop("stop", set_by="Boss")
        refused = 0
        for bad_reason in (None, "", "   "):
            try:
                cs.clear_emergency_stop(bad_reason, set_by="Boss")
            except ValueError:
                refused += 1
        still_set = cs.load()["emergency_stop"] is True
        cs.clear_emergency_stop("real reason", set_by="Boss")
        cleared = cs.load()["emergency_stop"] is False
        check("clear_emergency_stop needs a non-empty reason",
              refused == 3 and still_set and cleared,
              f"empty-reasons refused={refused}/3, stop_stayed={still_set}, "
              f"cleared_with_reason={cleared}")
    except Exception as e:  # noqa: BLE001
        check("clear_emergency_stop needs a non-empty reason", False, str(e))

    # 5. Corrupt control.json halts fail-closed (consult + real drain).
    try:
        tmp = tempfile.mkdtemp()
        control_path = os.path.join(tmp, "control.json")
        with open(control_path, "w", encoding="utf-8") as f:
            f.write("{not json")
        corrupt_raises = False
        try:
            consult(control_path)
        except ControlCorruptError:
            corrupt_raises = True
        # Real drain on a temp store with 1 queued task + corrupt control.
        tasks_path = os.path.join(tmp, "tasks.json")
        with open(tasks_path, "w", encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": [{
                "id": "p7check5", "status": "queued",
                "business": "agency", "type": "caption_write",
                "title": "P7 check 5 — must not run",
                "payload": {}, "queued_at": "2026-11-25T00:00:00+00:00",
            }]}, f)
        proc = subprocess.run(
            [sys.executable, RUNNER, "--drain-queue", "--max", "1",
             "--store-dir", tmp],
            capture_output=True, text=True, timeout=300)
        summary = json.loads(proc.stdout) if proc.returncode == 0 else {}
        records = json.load(open(tasks_path, encoding="utf-8"))["records"]
        audit_path = os.path.join(tmp, "audit.log")
        audit_text = open(audit_path, encoding="utf-8").read() \
            if os.path.isfile(audit_path) else ""
        ok = (corrupt_raises and proc.returncode == 0
              and summary.get("halted") is True
              and "corrupt" in str(summary.get("halt_reason", ""))
              and len(records) == 1 and records[0]["status"] == "queued"
              and "control_halt" in audit_text)
        check("corrupt control.json halts fail-closed (consult + drain)",
              ok, f"consult_raised={corrupt_raises}, drain_rc="
              f"{proc.returncode}, halted={summary.get('halted')}, "
              f"task_still_queued={records[0]['status'] if records else '?'}, "
              f"audit_has_control_halt={'control_halt' in audit_text}")
    except Exception as e:  # noqa: BLE001
        check("corrupt control.json halts fail-closed (consult + drain)",
              False, str(e))

    # 6. Approval centre lists pending via the REAL gateway.
    try:
        tmp = tempfile.mkdtemp()
        approvals_path = os.path.join(tmp, "approvals.json")
        gw = ApprovalGateway(approvals_path=approvals_path)
        centre = ApprovalCentre(gateway=gw)
        centre.request_approval("send", "Day 4 batch", "OutreachDrafter")
        centre.request_approval("publish", "Monday reel", "ContentPlanner")
        pending = centre.list_pending()
        ok = (len(pending) == 2
              and {p["action"] for p in pending} == {"send", "publish"}
              and all(p["age_minutes"] is not None for p in pending)
              and all(p["expires_in_minutes"] is not None
                      for p in pending)
              and all(p["expired"] is False for p in pending)
              and {tuple(p["allowed_gate_words"]) for p in pending}
              == {("send", "পাঠাও"), ("post it", "post all")})
        check("approval centre lists pending via the real gateway",
              ok, f"pending={len(pending)}, actions="
              f"{sorted(p['action'] for p in pending)}, age/expiry present")
    except Exception as e:  # noqa: BLE001
        check("approval centre lists pending via the real gateway",
              False, str(e))

    # 7. Approve: wrong gate word raises; right word records approved.
    try:
        tmp = tempfile.mkdtemp()
        approvals_path = os.path.join(tmp, "approvals.json")
        centre = ApprovalCentre(approvals_path=approvals_path)
        req = centre.request_approval("send", "Day 4 batch",
                                      "OutreachDrafter")
        wrong_raised = False
        try:
            centre.decide(req["id"], "approve", gate_word="ok")
        except ValueError:
            wrong_raised = True
        out = centre.decide(req["id"], "approve", gate_word="send")
        on_disk = [r for r in json.load(
            open(approvals_path, encoding="utf-8"))["records"]
            if r["id"] == req["id"]][0]
        ok = (wrong_raised and out["status"] == "approved"
              and out["decided_by"] == "Boss" and out["gate_word"] == "send"
              and on_disk["status"] == "approved"
              and on_disk["decided_by"] == "Boss")
        check("approve: wrong gate word raises, right word records approved",
              ok, f"wrong_word_raised={wrong_raised}, status="
              f"{on_disk['status']}, decided_by={on_disk['decided_by']}")
    except Exception as e:  # noqa: BLE001
        check("approve: wrong gate word raises, right word records approved",
              False, str(e))

    # 8. Reject records rejected; expired record cannot be approved.
    try:
        tmp = tempfile.mkdtemp()
        approvals_path = os.path.join(tmp, "approvals.json")
        centre = ApprovalCentre(approvals_path=approvals_path)
        req = centre.request_approval("publish", "Monday reel",
                                      "ContentPlanner")
        out = centre.decide(req["id"], "reject")
        on_disk = [r for r in json.load(
            open(approvals_path, encoding="utf-8"))["records"]
            if r["id"] == req["id"]][0]
        reject_ok = (out["status"] == "rejected"
                     and on_disk["status"] == "rejected")
        # Expired: backdate requested_at 30 min (past the 20-min TTL)
        # in the TEST file, then approve must refuse. The gateway only
        # reads the file at construction, so the decision goes through
        # a FRESH centre (same as a fresh CLI run) — the in-memory
        # records of the old centre still hold the fresh timestamp.
        req2 = centre.request_approval("send", "old request",
                                       "OutreachDrafter")
        data = json.load(open(approvals_path, encoding="utf-8"))
        for rec in data["records"]:
            if rec["id"] == req2["id"]:
                rec["requested_at"] = "2026-11-24T19:00:00+00:00"
        with open(approvals_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        fresh = ApprovalCentre(approvals_path=approvals_path)
        expired_raised = False
        try:
            fresh.decide(req2["id"], "approve", gate_word="send")
        except ValueError as exc:
            expired_raised = "expired" in str(exc)
        on_disk2 = [r for r in json.load(
            open(approvals_path, encoding="utf-8"))["records"]
            if r["id"] == req2["id"]][0]
        ok = (reject_ok and expired_raised
              and on_disk2["status"] == "expired")
        check("reject records rejected; expired record cannot be approved",
              ok, f"rejected={reject_ok}, expired_refused={expired_raised}, "
              f"expired_status={on_disk2['status']}")
    except Exception as e:  # noqa: BLE001
        check("reject records rejected; expired record cannot be approved",
              False, str(e))

    # 9. Dashboard: sync_status.py on a temp copy shows the new keys
    # AND the seeded numbers (not just key presence).
    try:
        from datetime import datetime as _dt, timezone as _tz
        tmp = tempfile.mkdtemp()
        base = os.path.join(tmp, "repo")
        os.makedirs(os.path.join(base, "store"))
        os.makedirs(os.path.join(base, "00-CEO-Core"))
        shutil.copy(os.path.join(BASE, "00-CEO-Core", "config.json"),
                    os.path.join(base, "00-CEO-Core", "config.json"))
        with open(os.path.join(base, "store", "tasks.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": [
                {"id": "t1", "status": "done"},
                {"id": "t2", "status": "queued"}]}, f)
        with open(os.path.join(base, "store", "approvals.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "approvals-v1", "records": [
                {"id": "a1", "status": "pending",
                 "action": "send", "detail": "seeded pending",
                 "requested_by": "OutreachDrafter",
                 "requested_at": _dt.now(_tz.utc).isoformat()},
                {"id": "a2", "status": "approved"}]}, f)
        # Seed a PAUSED control file via the real control module, so
        # the dashboard's control reader is exercised end to end.
        ControlState(control_path=os.path.join(
            base, "store", "control.json")).pause(
            "Phase 7 check 9 — seeded pause", set_by="Boss")
        mod = _load_sync_status()
        mod.BASE = base
        status = mod.collect_status()
        wanted = ("departments", "task_counts", "approvals", "control",
                  "ceo_report")
        present = [k for k in wanted if k in status]
        if not present:
            skipped("dashboard shows new Phase 7 keys + seeded numbers",
                    "Worker A dashboard extension has not landed yet — "
                    "sync_status.py has none of the new keys; re-run once "
                    "it lands")
        elif len(present) != len(wanted):
            check("dashboard shows new Phase 7 keys + seeded numbers",
                  False, f"PARTIAL landing — present={sorted(present)}, "
                  f"missing={sorted(set(wanted) - set(present))}")
        else:
            tc = status["task_counts"]
            appr = status["approvals"]
            ctrl = status["control"]
            ok = (isinstance(tc, dict) and tc.get("queued") == 1
                  and tc.get("done") == 1 and tc.get("total") == 2
                  and isinstance(appr, dict)
                  and appr.get("pending_count") == 1
                  and len(appr.get("pending") or []) == 1
                  and appr["pending"][0]["id"] == "a1"
                  and isinstance(ctrl, dict)
                  and ctrl.get("paused") is True
                  and ctrl.get("state") == "paused"
                  and isinstance(status["departments"], dict)
                  and len(status["departments"]) == 8
                  and isinstance(status["ceo_report"], dict)
                  and status["ceo_report"].get("available") is False)
            check("dashboard shows new Phase 7 keys + seeded numbers",
                  ok, f"task_counts={tc}, approvals_pending="
                  f"{appr.get('pending_count')}, control={ctrl}, "
                  f"departments={len(status['departments'])}, "
                  f"ceo_report_available="
                  f"{status['ceo_report'].get('available')}")
    except Exception as e:  # noqa: BLE001
        check("dashboard shows new Phase 7 keys + seeded numbers",
              False, str(e))

    # 10. CEO report generation (Worker B) matches a seeded temp store.
    try:
        from datetime import datetime as _dt2, timezone as _tz2
        from ceo_reporting import generate_report, render_markdown  # noqa: E402
        tmp = tempfile.mkdtemp()
        now = _dt2.now(_tz2.utc).isoformat()
        store_files = {
            "tasks.json": {"schema": "tasks-v1", "records": [
                {"id": "t1", "status": "done", "queued_at": now},
                {"id": "t2", "status": "queued", "queued_at": now}]},
            "approvals.json": {"schema": "approvals-v1", "records": [
                {"id": "a1", "status": "pending", "action": "send",
                 "detail": "seeded pending", "requested_by": "X",
                 "requested_at": now},
                {"id": "a2", "status": "approved", "action": "publish",
                 "detail": "seeded approved", "requested_by": "X",
                 "requested_at": now, "decided_at": now}]},
        }
        for name, payload in store_files.items():
            with open(os.path.join(tmp, name), "w", encoding="utf-8") as f:
                json.dump(payload, f)
        before = {n: _sha256_file(os.path.join(tmp, n))
                  for n in store_files}
        report = generate_report(tmp, "weekly")
        after = {n: _sha256_file(os.path.join(tmp, n))
                 for n in store_files}
        md = render_markdown(report)
        tasks = report.get("tasks") or {}
        appr = report.get("approvals") or {}
        ok = (report.get("period") == "weekly"
              and report.get("window", {}).get("days") == 7
              and tasks.get("total") == 2
              and (tasks.get("by_status") or {}).get("done") == 1
              and (tasks.get("by_status") or {}).get("queued") == 1
              and appr.get("pending") == 1
              and "2 task(s) in the store" in md
              and before == after)
        check("CEO report generation matches a seeded temp store",
              ok, f"period={report.get('period')}, tasks_total="
              f"{tasks.get('total')}, by_status={tasks.get('by_status')}, "
              f"approvals_pending={appr.get('pending')}, markdown_matches="
              f"{'2 task(s) in the store' in md}, store_untouched="
              f"{before == after}")
    except ImportError:
        skipped("CEO report generation matches a seeded temp store",
                "Worker B ceo_reporting package has not landed yet "
                "(no 00-CEO-Core/ceo_reporting/); re-run once it lands")
    except Exception as e:  # noqa: BLE001
        check("CEO report generation matches a seeded temp store",
              False, str(e))

    # 11. Real store unchanged by this check run.
    try:
        after = _store_hashes()
        check("real store unchanged by this check run",
              after == hashes_before,
              "unchanged" if after == hashes_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if r[1] == "FAIL"]
    skipped_n = [r for r in results if r[1] == "SKIPPED"]
    passed = [r for r in results if r[1] == "PASS"]
    print(f"\n{len(passed)}/{len(results)} checks passed "
          f"({len(skipped_n)} skipped, {len(failed)} failed).")
    if skipped_n:
        print("SKIPPED:", [r[0] for r in skipped_n])
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 7 local check: ALL DECIDED CHECKS PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
