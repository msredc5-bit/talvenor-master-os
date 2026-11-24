#!/usr/bin/env python3
"""check_workflow_engine.py — Local-first Phase 4 self-check for the
workflow engine + n8n adapter + runtime wiring (Worker C).

What it checks (offline ONLY — no network beyond localhost, no live
call, ever; $0; real n8n is [NOT TESTED] — n8n lives on Boss's PC):

  Queue (Worker A — queue.py, present in this snapshot):
    1. DLQ transition after retries exhausted.
    2. DLQ never drains (dead_letter is terminal, never flagged
       stuck, never auto-retried).
    3. Requeue only with an explicit reason.
    4. Recovery scan handles stuck records (in-memory scan +
       stubbed-store recovery, same stub pattern as queue.py's own
       self-test — the real store is never touched).
    5. Old-schema record drains unchanged (normalize keeps fields,
       adds defaults only).
    All five run against queue.py's real API (Worker A's report
    was not in this worker's context — the cases are designed from
    queue.py itself, read in full before writing them).

  Scheduler (Worker B — scheduler.py, present in this snapshot):
    6. Definitions load + validate (4 jobs, draft/report/watch only).
    7. Creation into a temp store lands all records paused
       (attempts the real create_paused_jobs; under the VM-wide
       exec-write block this BLOCKs honestly instead of failing).
    8. Activate-without-approval refuses (bad approvals leave the
       record paused; run against an in-memory seeded store, no
       file writes needed).
    9. Paused job never due (due_jobs + should_run_job, seeded store).

  Adapter against the local test double (acceptance):
   10. create/activate/list/trigger/status end-to-end.
   11. Webhook without (or with a wrong) secret -> 401.
   12. Non-localhost base URL refused (ValueError).
   13. API key / webhook secret never appear in error output.
   14. Deactivate flips active; unknown execution -> 404.
   15. Test webhook (/webhook-test) triggers, status finished.

  Example workflow JSON:
   16. talvenor-lead-triage.json parses, has nodes + connections,
       active false, no credential keys, no send/publish node.

  Engine:
   17. Draft workflow completes (3 mock steps ok, cost 0.0).
   18. Non-dict step + non-dict workflow never raise (error results).
   19. Empty steps -> completed.
   20. Wall-clock budget (0s context) stops the workflow (partial).

  Gate preservation (Phase 3 gate, consulted for real):
   21. Step {tool: gmail_send} -> pending-approval, never executes.
   22. Step {action: "send"} -> pending-approval.
   23. Draft step allowed (draft_email tool / draft action).
   24. Unknown tool step fails closed -> pending-approval.

  Runtime wiring (Phase 4, additive):
   25. Task with a "workflow" key executes through the engine
       inside the runtime limits (completed, iterations == steps).
   26. Workflow bounded by the runtime iteration cap.
   27. Task without a "workflow" key is unchanged (mock loop).

  No live calls:
   28. Source scan: no requests/urllib anywhere in workflow_engine;
       socket/http.server only in test_double.py; http.client only
       in n8n_adapter.py; runner.py gains no network import.

  Store:
   29. Real store unchanged by this check run (read-only snapshot).

Stdlib only. Run: python3 scripts/check_workflow_engine.py
"""

import json
import os
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

results = []  # (name, status, detail); status in PASS / FAIL / SKIP / BLOCKED


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def skip(name, reason):
    results.append((name, "SKIP", reason))
    print(f"[SKIP] {name} — {reason}")


def blocked(name, reason):
    results.append((name, "BLOCKED", reason))
    print(f"[BLOCKED] {name} — {reason}")


def _snapshot_store():
    """Contents of the real store JSONs — this check's only job is to
    prove this run did not change them."""
    snap = {}
    store_dir = os.path.join(BASE, "store")
    for name in sorted(os.listdir(store_dir)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(store_dir, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    return snap


def main():
    store_before = _snapshot_store()

    # -- imports ---------------------------------------------------------
    try:
        from workflow_engine import (  # noqa: PLC0415
            N8nAdapter, N8nError, N8nTestDouble, WorkflowEngine,
        )
        from workflow_engine import engine as engine_mod  # noqa: PLC0415
        from workflow_engine import scheduler as sched  # noqa: PLC0415
        from quiet_schedules import ScheduleStore  # noqa: PLC0415
        from agent_runtime import (  # noqa: PLC0415
            AgentRuntime, RuntimeContext, RuntimeLimits,
        )
    except ImportError as e:  # noqa: BLE001
        check("workflow_engine imports", False, str(e))
        print("\n0/1 checks passed.")
        return 1

    # -- 1-5. Queue (Worker A — queue.py, real API) --------------------
    try:
        from workflow_engine import queue as q  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        q = None
        _queue_import_error = str(e)
    else:
        _queue_import_error = None

    if q is None:
        for qname in [
                "queue: DLQ transition after retries exhausted",
                "queue: DLQ never drains",
                "queue: requeue only with explicit reason",
                "queue: recovery scan handles stuck records",
                "queue: old-schema record drains unchanged"]:
            skip(qname, f"queue.py not importable: {_queue_import_error}")
    else:
        _TS = "2026-11-25T01:00:00+00:00"

        # 1. DLQ transition after retries exhausted.
        try:
            rec = {"id": "t1", "status": "queued",
                   "business": "agency", "type": "caption_write",
                   "title": "t", "payload": {}, "retries": 3,
                   "max_retries": 2, "last_error": "boom"}
            q.normalize_queue_record(rec)
            reason = q.exhaustion_reason(rec)
            try:
                q.mark_dead_letter(rec, "  ")
                reason_ok = False
            except ValueError:
                reason_ok = True
            q.mark_dead_letter(rec, "retries_exhausted",
                               last_error="boom", now=_TS)
            ok = (q.retries_exhausted(3, 2) is True
                  and q.retries_exhausted(2, 2) is False
                  and reason == "retries_exhausted" and reason_ok
                  and rec["status"] == "dead_letter"
                  and rec["dead_letter_reason"] == "retries_exhausted"
                  and rec["dead_letter_at"] == _TS
                  and rec["last_error"] == "boom"
                  and q.is_dead_letter(rec) is True
                  and q.is_terminal(rec) is True)
            check("queue: DLQ transition after retries exhausted",
                  ok, f"reason={reason}, status={rec['status']}, "
                  f"dead_letter_at={rec['dead_letter_at']}")
        except Exception as e:  # noqa: BLE001
            check("queue: DLQ transition after retries exhausted",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 2. DLQ never drains (terminal, never flagged stuck, no auto path).
        try:
            dead = {"id": "t1", "status": "dead_letter",
                    "retries": 3, "max_retries": 2,
                    "dead_letter_reason": "retries_exhausted",
                    "dead_letter_at": _TS, "last_error": "boom"}
            queued = {"id": "t2", "status": "queued"}
            try:
                q.requeue_from_dead_letter(queued, "auto?")
                auto_requeued = True
            except ValueError:
                auto_requeued = False
            ok = (q.is_terminal(dead) is True
                  and q.scan_for_stuck_records([dead]) == []
                  and q.count_by_status([dead])["dead_letter"] == 1
                  and not auto_requeued)
            check("queue: DLQ never drains (dead_letter terminal, "
                  "never flagged stuck, no auto-requeue)",
                  ok, f"terminal={q.is_terminal(dead)}, stuck="
                  f"{q.scan_for_stuck_records([dead])}, "
                  f"auto_requeued={auto_requeued}")
        except Exception as e:  # noqa: BLE001
            check("queue: DLQ never drains (dead_letter terminal, "
                  "never flagged stuck, no auto-requeue)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 3. Requeue only with an explicit reason.
        try:
            rec = {"id": "t1", "status": "dead_letter",
                   "retries": 3, "max_retries": 2, "last_error": "boom",
                   "dead_letter_reason": "retries_exhausted",
                   "dead_letter_at": _TS,
                   "executions": [{"error": "boom"}]}
            try:
                q.requeue_from_dead_letter(rec, "")
                empty_ok = False
            except ValueError:
                empty_ok = True
            q.requeue_from_dead_letter(
                rec, "Boss: retry once, fixed prompt", now=_TS)
            executions_kept = rec["executions"] == [{"error": "boom"}]
            try:
                q.requeue_from_dead_letter(rec, "again")
                wrong_status_ok = False
            except ValueError:
                wrong_status_ok = True
            legacy = {"id": "t2", "status": "failed", "retries": 1,
                      "max_retries": 0, "last_error": "old boom"}
            q.requeue_from_dead_letter(legacy, "Boss: retry legacy",
                                       now=_TS)
            ok = (empty_ok and rec["status"] == "queued"
                  and rec["retries"] == 0
                  and rec["last_error"] is None
                  and rec["dead_letter_reason"] is None
                  and rec["requeue_count"] == 1
                  and rec["requeue_reason"] == "Boss: retry once, "
                  "fixed prompt"
                  and executions_kept and wrong_status_ok
                  and legacy["status"] == "queued")
            check("queue: requeue only with explicit reason (manual, "
                  "history kept, legacy failed requeueable)",
                  ok, f"empty_refused={empty_ok}, status="
                  f"{rec['status']}, requeue_count="
                  f"{rec.get('requeue_count')}, history_kept="
                  f"{executions_kept}")
        except Exception as e:  # noqa: BLE001
            check("queue: requeue only with explicit reason (manual, "
                  "history kept, legacy failed requeueable)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 4. Recovery scan handles stuck records (stubbed store_io).
        try:
            clean = q.scan_for_stuck_records([
                {"id": "a", "status": "queued"},
                {"id": "b", "status": "done"},
                {"id": "c", "status": "dead_letter"},
                {"id": "d", "status": "failed"}])
            stuck = q.scan_for_stuck_records([
                {"id": "s1", "status": "running", "started_at": _TS},
                {"id": "s2", "status": "queued", "started_at": _TS},
                {"id": "s3", "status": "in_progress"}])
            scan_ok = (clean == []
                       and [f["record_id"] for f in stuck]
                       == ["s1", "s2", "s3"]
                       and stuck[0]["reason"] == "transient_status:running"
                       and stuck[1]["reason"]
                       == "started_but_not_terminal")
            # Stubbed store-level recovery (same pattern as
            # queue.py's own self-test — no disk, no real store).
            import copy as _copy  # noqa: PLC0415
            fake_store = {"schema": "tasks-v1", "records": [
                {"id": "s1", "status": "running", "started_at": _TS,
                 "retries": 0, "max_retries": 2},
                {"id": "ok1", "status": "done"},
                {"id": "s2", "status": "queued", "started_at": _TS,
                 "retries": 5, "max_retries": 2}]}
            audited = []

            def _fake_read(path, default=None):
                return _copy.deepcopy(fake_store)

            def _fake_update(path, fn, default=None):
                nonlocal fake_store
                fake_store = fn(fake_store)
                return fake_store

            def _fake_audit(event, details=None, store_dir=None,
                            audit_path=None):
                audited.append((event, details))
                return True

            real_read, real_update, real_audit = (
                q.read_json, q.update_json, q.audit_log)
            q.read_json, q.update_json, q.audit_log = (
                _fake_read, _fake_update, _fake_audit)
            try:
                report = q.recover_stuck_records(
                    "/tmp/fake-store", policy="requeue",
                    reason="test restart scan", now=_TS)
                by_id = {r["id"]: r
                         for r in fake_store["records"]}
                recover_ok = (
                    len(report["found"]) == 2
                    and {r["record_id"] for r in report["recovered"]}
                    == {"s1", "s2"}
                    and by_id["s1"]["status"] == "queued"
                    and by_id["s1"]["started_at"] is None
                    and by_id["s1"]["last_stuck_started_at"] == _TS
                    and by_id["s1"]["retries"] == 0
                    and by_id["ok1"]["status"] == "done"
                    and len(audited) == 2)
                fake_store["records"] = [
                    {"id": "s9", "status": "running",
                     "started_at": _TS, "retries": 4, "max_retries": 2,
                     "last_error": "crash"}]
                audited.clear()
                q.recover_stuck_records(
                    "/tmp/fake-store", policy="mark_failed",
                    reason="operator: never run again", now=_TS)
                recover_ok = (recover_ok
                              and fake_store["records"][0]["status"]
                              == "dead_letter"
                              and "retries already exhausted" in
                              fake_store["records"][0][
                                  "dead_letter_reason"])
                try:
                    q.recover_stuck_records("/tmp/fake-store",
                                            policy="delete")
                    policy_ok = False
                except ValueError:
                    policy_ok = True
                recover_ok = recover_ok and policy_ok
            finally:
                q.read_json, q.update_json, q.audit_log = (
                    real_read, real_update, real_audit)
            ok = scan_ok and recover_ok
            check("queue: recovery scan handles stuck records "
                  "(scan + stubbed requeue/mark_failed)",
                  ok, f"scan_ok={scan_ok}, recover_ok={recover_ok}, "
                  f"stuck={[f['record_id'] for f in stuck]}")
        except Exception as e:  # noqa: BLE001
            check("queue: recovery scan handles stuck records "
                  "(scan + stubbed requeue/mark_failed)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 5. Old-schema record drains unchanged.
        try:
            old = {"id": "old1", "status": "done",
                   "business": "agency", "type": "research",
                   "title": "old record", "payload": {}}
            q.normalize_queue_record(old)
            r2 = {"id": "t3", "status": "queued", "retries": 0,
                  "max_retries": 5}
            q.normalize_queue_record(r2)
            ok = (old["title"] == "old record"
                  and old["priority"] == 0 and old["retries"] == 0
                  and old["max_retries"] == 0
                  and old["depends_on"] == []
                  and old["executions"] == []
                  and old["dead_letter_reason"] is None
                  and q.consecutive_same_error_count(r2) == 0
                  and q.exhaustion_reason(r2) is None
                  and q.repeated_same_error(r2) is False)
            check("queue: old-schema record drains unchanged "
                  "(normalize adds defaults only, keeps fields)",
                  ok, f"title={old['title']!r}, executions="
                  f"{old['executions']}, exhaustion="
                  f"{q.exhaustion_reason(r2)}")
        except Exception as e:  # noqa: BLE001
            check("queue: old-schema record drains unchanged "
                  "(normalize adds defaults only, keeps fields)",
                  False, f"{type(e).__name__}: {e}"[:160])

    # -- 6. Scheduler definitions load + validate ----------------------
    try:
        jobs = sched.job_definitions()
        ok = (sched.validate_job_definitions() is True
              and len(jobs) == 4
              and [j["id"] for j in jobs] == [
                  "daily-task-queue-drain-watch",
                  "daily-approval-queue-watch",
                  "weekly-ceo-report",
                  "monthly-ledger-usage-summary"]
              and all(j["action"] in sched.ALLOWED_ACTION_KINDS
                      for j in jobs))
        try:
            sched.job_definition("no-such-job")
            ok = False
        except KeyError:
            pass
        bad = sched.job_definitions()
        bad[0]["action"] = "send"
        try:
            sched.validate_job_definitions(bad)
            ok = False
        except ValueError:
            pass
        check("scheduler: definitions load + validate (4 jobs, "
              "draft/report/watch only)",
              ok, f"jobs={[j['id'] for j in jobs]}")
    except Exception as e:  # noqa: BLE001
        check("scheduler: definitions load + validate (4 jobs, "
              "draft/report/watch only)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 7. Scheduler creation into a temp store lands all paused ------
    # Attempts the real path. Under the VM-wide exec-write block the
    # ScheduleStore save fails with OSError — that BLOCKs honestly.
    # Per-run fresh temp dir (coordinator fix 2026-11-25): the old
    # fixed /tmp path made this check fail on re-runs — jobs from a
    # previous run counted as "existing", so created=0. tempfile
    # works again now that the block has cleared (verified).
    try:
        tmp_dir = tempfile.mkdtemp(prefix="check-workflow-")
        tmp_sched = os.path.join(tmp_dir, "schedules.json")
        tmp_store = ScheduleStore(schedules_path=tmp_sched)
        out = sched.create_paused_jobs(tmp_store)
        ok = (len(out["created"]) == 4 and out["existing"] == []
              and all(r["status"] == "paused"
                      for r in tmp_store.list())
              and len(tmp_store.list()) == 4)
        out2 = sched.create_paused_jobs(tmp_store)
        ok = ok and out2["created"] == [] and len(out2["existing"]) == 4
        check("scheduler: creation into a temp store lands all "
              "records paused (+ idempotent)",
              ok, f"created={len(out['created'])}, "
              f"second_created={len(out2['created'])}")
    except OSError as e:  # noqa: BLE001 — the environment write block
        blocked("scheduler: creation into a temp store lands all "
                "records paused (+ idempotent)",
                f"environment write block — temp store unwritable: "
                f"{type(e).__name__}")
    except Exception as e:  # noqa: BLE001
        check("scheduler: creation into a temp store lands all "
              "records paused (+ idempotent)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- seeded in-memory store (no file writes) for checks 8-9 --------
    def _seeded_store():
        """A ScheduleStore whose records are seeded in memory from
        the real job definitions — the exact shape add() produces,
        minus the write. Read-only checks + refusal checks (which
        raise before any write) run against it."""
        store = ScheduleStore(schedules_path=os.path.join(
            BASE, ".check-workflow-seed-does-not-exist.json"))
        store.records = []
        for i, job in enumerate(sched.job_definitions()):
            store.records.append({
                "id": f"seed-{i + 1:03d}",
                "name": job["name"],
                "kind": job["kind"],
                "source": job["source"],
                "interval_minutes": job["interval_minutes"],
                "status": "paused",
                "last_marker": None,
                "last_run_at": None,
                "last_result": None,
                "last_skip_reason": None,
                "running": False,
                "run_started_at": None,
                "runs": 0,
                "skips": 0,
                "created_at": "2026-11-25T00:00:00+00:00",
                "note": sched._note_for(job),
            })
        return store

    # -- 8. Activate-without-approval refuses ---------------------------
    try:
        store = _seeded_store()
        bad_approvals = (None, {}, {"approval_id": "APR-1"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "approved"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "approved",
                          "scope": "scheduler-activation:other-job"},
                         {"approval_id": "APR-1", "approver": "Someone",
                          "decision": "approved",
                          "scope": "scheduler-activation:weekly-ceo-report"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "pending",
                          "scope": "scheduler-activation:weekly-ceo-report"})
        refused = 0
        for bad_approval in bad_approvals:
            try:
                sched.activate_job(store, "weekly-ceo-report", bad_approval)
            except sched.ActivationRefused:
                refused += 1
        rec = sched._find_record(store, "weekly-ceo-report")
        ok = (refused == len(bad_approvals)
              and rec["status"] == "paused"
              and not sched.is_activated(rec))
        try:
            sched.resume_job(store, "weekly-ceo-report")
            ok = False
        except sched.ActivationRefused:
            pass
        check("scheduler: activate-without-approval refuses, record "
              "stays paused (+ guarded resume refuses)",
              ok, f"refused={refused}/{len(bad_approvals)}, "
              f"status={rec['status']}")
    except Exception as e:  # noqa: BLE001
        check("scheduler: activate-without-approval refuses, record "
              "stays paused (+ guarded resume refuses)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 9. Paused job never due ----------------------------------------
    try:
        store = _seeded_store()
        due = sched.due_jobs(store)
        due_one, reason = sched.should_run_job(
            store, "weekly-ceo-report", {"tasks": ["a"]})
        ok = (len(due) == 4 and all(not d["due"] for d in due)
              and due_one is False and "paused" in reason)
        check("scheduler: paused job never due (due_jobs + "
              "should_run_job)",
              ok, f"due={[d['due'] for d in due]}, reason={reason}")
    except Exception as e:  # noqa: BLE001
        check("scheduler: paused job never due (due_jobs + "
              "should_run_job)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 10-15. Adapter against the local test double -------------------
    double = N8nTestDouble(secret="test-secret-4c")
    try:
        double.start()
        adapter = N8nAdapter(base_url=double.base_url,
                             api_key="test-key-4c",
                             webhook_secret="test-secret-4c")

        # 10. End-to-end: create/activate/list/trigger/status.
        try:
            with open(os.path.join(
                    CEO_CORE_DIR, "workflow_engine", "examples",
                    "talvenor-lead-triage.json"),
                    encoding="utf-8") as f:
                example = json.load(f)
            created = adapter.create_workflow(example)
            wid = created.get("id")
            listed = adapter.list_workflows()
            listed_ids = [w.get("id") for w in listed.get("data", [])]
            activated = adapter.activate_workflow(wid)
            triggered = adapter.trigger_via_webhook(
                "talvenor-lead-triage",
                {"business_name": "Example Plumbing Co.",
                 "need": "missed calls"})
            exec_id = triggered.get("executionId")
            status = adapter.get_execution_status(exec_id)
            ok = (wid and wid in listed_ids
                  and activated.get("active") is True
                  and triggered.get("status") == "finished"
                  and exec_id and status.get("status") == "finished")
            check("adapter: create/activate/list/trigger/status "
                  "end-to-end (test double)",
                  ok, f"workflow={wid}, active="
                  f"{activated.get('active')}, execution={exec_id}, "
                  f"status={status.get('status')}")
        except Exception as e:  # noqa: BLE001
            check("adapter: create/activate/list/trigger/status "
                  "end-to-end (test double)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 11. Webhook without (or with a wrong) secret -> 401.
        try:
            no_secret = N8nAdapter(base_url=double.base_url,
                                   api_key="test-key-4c")
            wrong_secret = N8nAdapter(base_url=double.base_url,
                                      api_key="test-key-4c",
                                      webhook_secret="wrong-secret")
            got = []
            for adapter_try in (no_secret, wrong_secret):
                try:
                    adapter_try.trigger_via_webhook(
                        "talvenor-lead-triage", {"x": 1})
                    got.append(None)
                except N8nError as exc:
                    got.append(exc.status)
            ok = got == [401, 401]
            check("adapter: webhook without/wrong secret -> 401",
                  ok, f"statuses={got}")
        except Exception as e:  # noqa: BLE001
            check("adapter: webhook without/wrong secret -> 401",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 12. Non-localhost base URL refused.
        try:
            refused = 0
            for bad_url in ("https://n8n.example.com",
                            "http://192.168.1.5:5678",
                            "http://n8n.internal:5678"):
                try:
                    N8nAdapter(base_url=bad_url)
                except ValueError:
                    refused += 1
            ok_local = True
            try:
                N8nAdapter(base_url="http://localhost:5678")
                N8nAdapter(base_url="http://127.0.0.1:5678")
            except ValueError:
                ok_local = False
            ok = refused == 3 and ok_local
            check("adapter: non-localhost base URL refused "
                  "(localhost/127.0.0.1 still allowed)",
                  ok, f"refused={refused}/3, localhost_ok={ok_local}")
        except Exception as e:  # noqa: BLE001
            check("adapter: non-localhost base URL refused "
                  "(localhost/127.0.0.1 still allowed)",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 13. API key / webhook secret never appear in error output.
        try:
            fake_key = "SECRETKEY-abc-123-xyz-4c"
            fake_secret = "SECRETWH-abc-123-xyz-4c"
            closed = N8nAdapter(base_url="http://127.0.0.1:1",
                                api_key=fake_key,
                                webhook_secret=fake_secret)
            leaked = []
            for call in (lambda: closed.list_workflows(),
                         lambda: closed.trigger_via_webhook("p", {})):
                try:
                    call()
                except N8nError as exc:
                    text = str(exc)
                    if fake_key in text or fake_secret in text:
                        leaked.append(text[:80])
                except Exception as exc:  # noqa: BLE001
                    text = str(exc)
                    if fake_key in text or fake_secret in text:
                        leaked.append(text[:80])
            with open(os.path.join(CEO_CORE_DIR, "workflow_engine",
                                   "n8n_adapter.py"),
                      encoding="utf-8") as f:
                adapter_src = f.read()
            # Source check, plainly: no print call in the adapter,
            # so a key/secret can never be printed from there.
            ok = not leaked and "print(" not in adapter_src
            check("adapter: API key / webhook secret never in error "
                  "output or logs",
                  ok, f"leaks={leaked}, has_print="
                  f"{'print(' in adapter_src}")
        except Exception as e:  # noqa: BLE001
            check("adapter: API key / webhook secret never in error "
                  "output or logs",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 14. Deactivate flips active; unknown execution -> 404.
        try:
            listed = adapter.list_workflows()
            wid = listed["data"][0]["id"]
            deactivated = adapter.deactivate_workflow(wid)
            got_404 = None
            try:
                adapter.get_execution_status("exec-999999")
            except N8nError as exc:
                got_404 = exc.status
            ok = (deactivated.get("active") is False
                  and got_404 == 404)
            check("adapter: deactivate flips active; unknown "
                  "execution -> 404",
                  ok, f"active_after_deactivate="
                  f"{deactivated.get('active')}, unknown_status={got_404}")
        except Exception as e:  # noqa: BLE001
            check("adapter: deactivate flips active; unknown "
                  "execution -> 404",
                  False, f"{type(e).__name__}: {e}"[:160])

        # 15. Test webhook (/webhook-test) triggers, status finished.
        try:
            triggered = adapter.trigger_via_webhook(
                "talvenor-lead-triage", {"probe": "test"}, test=True)
            exec_id = triggered.get("executionId")
            status = adapter.get_execution_status(exec_id)
            ok = (triggered.get("status") == "finished"
                  and status.get("status") == "finished"
                  and status.get("mode") == "test")
            check("adapter: test webhook (/webhook-test) triggers, "
                  "status finished",
                  ok, f"execution={exec_id}, status="
                  f"{status.get('status')}, mode={status.get('mode')}")
        except Exception as e:  # noqa: BLE001
            check("adapter: test webhook (/webhook-test) triggers, "
                  "status finished",
                  False, f"{type(e).__name__}: {e}"[:160])
    finally:
        double.stop()

    # -- 16. Example workflow JSON --------------------------------------
    try:
        with open(os.path.join(CEO_CORE_DIR, "workflow_engine",
                               "examples", "talvenor-lead-triage.json"),
                  encoding="utf-8") as f:
            example = json.load(f)
        nodes = example.get("nodes") or []
        connections = example.get("connections") or {}
        secret_keys = {"credentials", "credential", "apikey",
                       "api_key", "password", "token", "secret"}

        def _keys(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    yield key
                    yield from _keys(value)
            elif isinstance(obj, list):
                for item in obj:
                    yield from _keys(item)

        found_secret_keys = {k for k in _keys(example)
                             if str(k).lower() in secret_keys}
        node_types = " ".join(str(n.get("type", "")) for n in nodes).lower()
        bad_types = [t for t in ("send", "gmail", "smtp", "slack",
                                 "telegram", "publish")
                     if t in node_types]
        note = str(example.get("_talvenor_note", ""))
        ok = (isinstance(nodes, list) and len(nodes) >= 2
              and isinstance(connections, dict) and connections
              and example.get("active") is False
              and not found_secret_keys and not bad_types
              and "MANUAL IMPORT ONLY" in note
              and "NO credentials" in note)
        check("example: talvenor-lead-triage.json parses, nodes + "
              "connections, inactive, no credentials, no send node",
              ok, f"nodes={len(nodes)}, connections="
              f"{len(connections)}, active={example.get('active')}, "
              f"secret_keys={sorted(found_secret_keys)}, "
              f"bad_types={bad_types}")
    except Exception as e:  # noqa: BLE001
        check("example: talvenor-lead-triage.json parses, nodes + "
              "connections, inactive, no credentials, no send node",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 17-20. Engine ----------------------------------------------------
    try:
        out = WorkflowEngine().execute({
            "steps": [
                {"id": "research", "kind": "research",
                 "input": {"business_name": "Example Plumbing Co."}},
                {"id": "draft-caption", "kind": "draft",
                 "input": {"platform": "facebook"}},
                {"id": "qa", "kind": "qa"},
            ]})
        ok = (out["status"] == "completed"
              and len(out["steps"]) == 3
              and all(s["status"] == "ok" for s in out["steps"])
              and out["cost_usd"] == 0.0)
        check("engine: draft workflow completes (3 mock steps ok, "
              "cost 0.0)",
              ok, f"status={out['status']}, steps={len(out['steps'])}, "
              f"cost={out['cost_usd']}")
    except Exception as e:  # noqa: BLE001
        check("engine: draft workflow completes (3 mock steps ok, "
              "cost 0.0)",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        bad_step = WorkflowEngine().execute({"steps": ["not-a-dict"]})
        bad_wf = WorkflowEngine().execute("not-a-dict")
        bad_steps = WorkflowEngine().execute({"steps": "not-a-list"})
        ok = (bad_step["status"] == "error"
              and bad_step["steps"]
              and bad_step["steps"][0]["status"] == "error"
              and bad_wf["status"] == "error"
              and bad_steps["status"] == "error")
        check("engine: non-dict step / non-dict workflow / non-list "
              "steps never raise (error results)",
              ok, f"bad_step={bad_step['status']}, "
              f"bad_wf={bad_wf['status']}, bad_steps={bad_steps['status']}")
    except Exception as e:  # noqa: BLE001
        check("engine: non-dict step / non-dict workflow / non-list "
              "steps never raise (error results)",
              False, f"raised: {type(e).__name__}: {e}"[:160])

    try:
        out = WorkflowEngine().execute({"steps": []})
        ok = (out["status"] == "completed" and out["steps"] == []
              and out["cost_usd"] == 0.0)
        check("engine: empty steps -> completed",
              ok, f"status={out['status']}, steps={out['steps']}")
    except Exception as e:  # noqa: BLE001
        check("engine: empty steps -> completed",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        ctx = RuntimeContext({"id": "t"},
                             RuntimeLimits(wall_clock_seconds=0.0))
        out = WorkflowEngine().execute(
            {"steps": [{"id": "a", "kind": "draft"}]}, context=ctx)
        ok = (out["status"] == "partial" and out["steps"] == []
              and "wall-clock" in (out["error"] or ""))
        check("engine: wall-clock budget (0s) stops the workflow "
              "(partial, 0 steps run)",
              ok, f"status={out['status']}, steps={len(out['steps'])}, "
              f"error={out['error']}")
    except Exception as e:  # noqa: BLE001
        check("engine: wall-clock budget (0s) stops the workflow "
              "(partial, 0 steps run)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 21-24. Gate preservation ----------------------------------------
    try:
        out = WorkflowEngine().execute({
            "steps": [{"id": "mail", "tool": "gmail_send",
                       "action": "send",
                       "input": {"to": "a@b.com"}}]})
        step = out["steps"][0]
        ok = (step["status"] == "pending-approval"
              and out["status"] == "partial")
        check("gate: workflow step gmail_send -> pending-approval, "
              "never executes",
              ok, f"step={step['status']}, overall={out['status']}")
    except Exception as e:  # noqa: BLE001
        check("gate: workflow step gmail_send -> pending-approval, "
              "never executes",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        out = WorkflowEngine().execute({
            "steps": [{"id": "s", "action": "send"}]})
        ok = out["steps"][0]["status"] == "pending-approval"
        check("gate: workflow step action=send -> pending-approval",
              ok, f"step={out['steps'][0]['status']}")
    except Exception as e:  # noqa: BLE001
        check("gate: workflow step action=send -> pending-approval",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        out = WorkflowEngine().execute({
            "steps": [{"id": "d1", "tool": "draft_email"},
                      {"id": "d2", "action": "draft"}]})
        ok = (out["status"] == "completed"
              and all(s["status"] == "ok" for s in out["steps"]))
        check("gate: draft step allowed (draft_email tool / draft "
              "action)",
              ok, f"status={out['status']}, steps="
              f"{[s['status'] for s in out['steps']]}")
    except Exception as e:  # noqa: BLE001
        check("gate: draft step allowed (draft_email tool / draft "
              "action)",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        out = WorkflowEngine().execute({
            "steps": [{"id": "u", "tool": "unknown_tool_xyz"}]})
        ok = out["steps"][0]["status"] == "pending-approval"
        check("gate: unknown tool step fails closed "
              "(pending-approval)",
              ok, f"step={out['steps'][0]['status']}")
    except Exception as e:  # noqa: BLE001
        check("gate: unknown tool step fails closed "
              "(pending-approval)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 25-27. Runtime wiring -------------------------------------------
    try:
        r = AgentRuntime().run_task({
            "id": "wf-task",
            "workflow": {"steps": [
                {"id": "research", "kind": "research"},
                {"id": "draft-caption", "kind": "draft"},
                {"id": "qa", "kind": "qa"},
            ]}})
        out = r.output or {}
        ok = (r.status == "completed" and r.iterations == 3
              and r.cost_usd == 0.0
              and out.get("status") == "completed"
              and len(out.get("steps", [])) == 3
              and all(s["status"] == "ok" for s in out["steps"]))
        check("runtime: task with workflow key executes through the "
              "engine (completed, 3 steps)",
              ok, f"status={r.status}, iterations={r.iterations}, "
              f"cost={r.cost_usd}")
    except Exception as e:  # noqa: BLE001
        check("runtime: task with workflow key executes through the "
              "engine (completed, 3 steps)",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        r = AgentRuntime().run_task(
            {"id": "wf-cap",
             "workflow": {"steps": [
                 {"id": "s1", "kind": "draft"},
                 {"id": "s2", "kind": "draft"},
                 {"id": "s3", "kind": "draft"},
                 {"id": "s4", "kind": "draft"},
             ]}},
            limits=RuntimeLimits(max_iterations=2))
        out = r.output or {}
        ok = (r.status == "error" and r.iterations == 2
              and len(out.get("steps", [])) == 2)
        check("runtime: workflow bounded by the runtime iteration "
              "cap (2 of 4 steps)",
              ok, f"status={r.status}, iterations={r.iterations}, "
              f"steps_run={len(out.get('steps', []))}")
    except Exception as e:  # noqa: BLE001
        check("runtime: workflow bounded by the runtime iteration "
              "cap (2 of 4 steps)",
              False, f"{type(e).__name__}: {e}"[:160])

    try:
        r = AgentRuntime().run_task({"id": "plain"})
        out = r.output or {}
        ok = (r.status == "completed" and out.get("mock_brain") is True
              and out.get("draft_only") is True)
        check("runtime: task without workflow key unchanged (mock "
              "loop)",
              ok, f"status={r.status}, mock_brain={out.get('mock_brain')}")
    except Exception as e:  # noqa: BLE001
        check("runtime: task without workflow key unchanged (mock "
              "loop)",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 28. No live calls: source scan -----------------------------------
    # Token-based (not substring): string literals and docstrings do
    # not count — e.g. scheduler.py's self-test lists "requests." /
    # "urllib" as STRINGS, and n8n_adapter.py's docstring names
    # them as forbidden. Only real code tokens count.
    try:
        pkg = os.path.join(CEO_CORE_DIR, "workflow_engine")
        hits = []
        for name in sorted(os.listdir(pkg)):
            path = os.path.join(pkg, name)
            if os.path.isdir(path):
                if name == "examples":
                    continue
                for sub in sorted(os.listdir(path)):
                    if not sub.endswith(".py"):
                        continue
                    with open(os.path.join(path, sub),
                              encoding="utf-8") as f:
                        text = f.read()
                    hits.extend(_scan_file(f"{name}/{sub}", text))
                continue
            if not name.endswith(".py"):
                continue
            with open(path, encoding="utf-8") as f:
                text = f.read()
            hits.extend(_scan_file(name, text))
        runner_path = os.path.join(CEO_CORE_DIR, "agent_runtime",
                                   "runner.py")
        with open(runner_path, encoding="utf-8") as f:
            runner_src = f.read()
        hits.extend(_scan_file("runner.py", runner_src))
        ok = not hits
        check("no live calls: workflow_engine source scan clean "
              "(http.client only in adapter; socket/http.server only "
              "in double) + runner.py adds no network import",
              ok, f"hits={hits}")
    except Exception as e:  # noqa: BLE001
        check("no live calls: workflow_engine source scan clean "
              "(http.client only in adapter; socket/http.server only "
              "in double) + runner.py adds no network import",
              False, f"{type(e).__name__}: {e}"[:160])

    # -- 29. Real store unchanged -----------------------------------------
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else
              f"CHANGED: {[k for k in after if after.get(k) != store_before.get(k)]}")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if r[1] == "FAIL"]
    passed = [r for r in results if r[1] == "PASS"]
    skipped = [r for r in results if r[1] == "SKIP"]
    blocked_r = [r for r in results if r[1] == "BLOCKED"]
    decided = len(passed) + len(failed)
    print(f"\n{len(passed)}/{decided} checks passed "
          f"({len(skipped)} skipped, {len(blocked_r)} blocked).")
    if skipped:
        print("SKIPPED:", [r[0] for r in skipped])
    if blocked_r:
        print("BLOCKED:", [r[0] for r in blocked_r])
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_workflow_engine: ALL DECIDED CHECKS PASS "
          "(offline — no live call made; real n8n [NOT TESTED]).")
    return 0


def _scan_file(label, text):
    """Forbidden-token scan for one source file, on CODE tokens
    only (``tokenize`` — string literals and comments/docstrings
    are skipped, so a docstring saying "no requests" or a
    self-test listing "requests." as a string does not count).

    Allowed: http.client only in n8n_adapter.py; socket /
    http.server only in test_double.py. requests / urllib /
    subprocess are forbidden everywhere here.
    """
    import io  # noqa: PLC0415
    import tokenize  # noqa: PLC0415

    try:
        tokens = [(tok.type, tok.string)
                  for tok in tokenize.generate_tokens(io.StringIO(text).readline)
                  if tok.type in (tokenize.NAME, tokenize.OP)]
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return [f"{label}:unparseable"]
    names = [s for (t, s) in tokens if t == tokenize.NAME]
    hits = []
    for bad in ("requests", "urllib", "subprocess"):
        if bad in names:
            hits.append(f"{label}:{bad}")
    # Dotted uses: http.client / http.server as code (import or
    # attribute access) — token sequence NAME OP('.') NAME.
    pairs = set()
    for i in range(len(tokens) - 2):
        (t1, s1), (t2, s2), (t3, s3) = tokens[i:i + 3]
        if (t1 == tokenize.NAME and s2 == "."
                and t3 == tokenize.NAME):
            pairs.add((s1, s3))
    if ("http", "client") in pairs and label != "n8n_adapter.py":
        hits.append(f"{label}:http.client")
    if ("http", "server") in pairs and label != "test_double.py":
        hits.append(f"{label}:http.server")
    if "socket" in names and label != "test_double.py":
        hits.append(f"{label}:socket")
    return hits


if __name__ == "__main__":
    sys.exit(main())
