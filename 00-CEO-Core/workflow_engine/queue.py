"""Task-queue hardening — Talvenor Master OS, Phase 4 (local-first).

Worker A: DLQ status, restart-recovery scan, structured execution
records. Built on top of scripts/run_office.py's drain and the
tasks-v1 schema. Stdlib only. No network, no send, no publish, no
spend, no delete, no live calls, no keys.

DESIGN DECISIONS (see also the Phase 4 coordinator report)
----------------------------------------------------------
1. DLQ status name: "dead_letter".
   A queued task that exhausts its retry budget in the drain is
   marked "dead_letter" (not "failed"). The drain's retry rule is
   unchanged: a failed attempt stays "queued" with retries += 1
   while retries <= max_retries; the FIRST failure past the budget
   moves the record to "dead_letter" with last_error preserved and
   dead_letter_reason / dead_letter_at recorded. A dead-letter
   record is NEVER auto-retried and NEVER drained as queued.
   The old "failed" status is kept as a LEGACY terminal status:
   no new code writes it from the drain, but every reader honours
   it (dependency blocking, idempotency keys, vault, requeue) so
   records written before Phase 4 keep their meaning. TERMINAL
   statuses: done, failed (legacy), dead_letter, blocked,
   cancelled, duplicate.

2. Execution records live INLINE on the task record, as an
   optional "executions" list. Chosen over a separate executions
   store file because the task record is already the unit the
   drain re-reads and rewrites atomically under the store lock —
   a second file would need its own locking and could drift from
   tasks.json. Backward-compatible: records without "executions"
   still drain unchanged (missing list == no attempts recorded);
   normalize_queue_record() only adds the key when an attempt is
   actually recorded. Each entry: {"attempt", "task_id",
   "started_at", "finished_at", "status", "error", "cost_usd"}.
   The list is capped at MAX_EXECUTIONS_PER_RECORD (100); older
   entries are dropped and the drop is counted in
   "executions_trimmed", so history is never silently lost.

3. Restart-recovery scan — FINDING (verified by reading the
   drain): NO writer in the repo ever puts a task record into an
   in-progress state. scripts/run_office.py writes only queued /
   done / dead_letter / blocked / duplicate / cancelled (and the
   transient "queued-retry" drain summary, which is not a stored
   status), and never sets "started_at" on a task record. The
   "in_progress" in 00-CEO-Core/acceptance_flow.py is a step
   status inside acceptance records, not a queue status; the
   "running" lock in quiet_schedules.py belongs to schedule
   records, not tasks. So there is NO live stuck state to recover
   today — the scan is implemented DEFENSIVELY for the states a
   future drain (or a crash mid-run) could produce, and documents
   that finding instead of inventing a state. A record is STUCK
   when: (a) its status is in TRANSIENT_STATUSES ("running",
   "in_progress", "started"), or (b) it carries "started_at" but
   has no terminal status (crashed between start-of-run and
   marking). The scan runs at drain startup, before any task is
   picked, and only while no drain is running (that is the
   precondition that makes (b) safe — a record mid-run in another
   process looks identical). Recovery is safe by construction:
   requeue (default — status back to "queued", the stuck marker
   cleared, evidence kept in last_stuck_started_at /
   recovery_reason / recovered_at) or mark_failed (operator's
   explicit choice for a record that must never run again).
   Recovery NEVER deletes, NEVER executes, NEVER loses the
   record, and a failed scan never breaks the drain.

4. Requeue is MANUAL ONLY. requeue_from_dead_letter() takes an
   explicit reason string (empty reason raises ValueError) and is
   called from nowhere in the codebase — only a human (Boss's
   decision) or an explicit operator step may call it. It works
   from "dead_letter" and from legacy "failed" (the pre-DLQ
   equivalent), resets retries to 0, clears the dead-letter
   fields, and records requeue_reason / requeued_at /
   requeue_count for the audit trail.

5. Repeated same error: consecutive_same_error_count() counts
   the trailing executions with an identical non-null error.
   repeated_same_error() (default threshold 3) lets the drain
   dead-letter a task that fails the same way repeatedly even
   before its retry budget is spent. The threshold is a policy
   choice, recorded here, not silently tuned.

Import contract: Worker C owns 00-CEO-Core/workflow_engine/
__init__.py. Once it exists, import as
  sys.path.insert(0, "00-CEO-Core")
  from workflow_engine.queue import ...
Until then (and inside scripts/run_office.py's lazy hook) load
this file by path with importlib.util.spec_from_file_location.
This module never imports run_office (wrong direction) — its
normalize_queue_record() mirrors run_office.normalize_task_record
and is documented as such.
"""

import os
from datetime import datetime, timezone

try:
    from store_io import read_json, update_json
except ImportError:  # direct script run from another directory
    import sys
    # store_io lives in 00-CEO-Core, one level above this file —
    # NOT in this file's own directory (unlike audit.py's fallback).
    sys.path.insert(0, os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    from store_io import read_json, update_json  # noqa: E402

try:
    from audit import audit_log
except ImportError:  # direct script run from another directory
    import sys
    sys.path.insert(0, os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    from audit import audit_log  # noqa: E402

__all__ = [
    "DLQ_STATUS",
    "LEGACY_FAILED_STATUS",
    "TERMINAL_STATUSES",
    "TRANSIENT_STATUSES",
    "REPEAT_THRESHOLD",
    "MAX_EXECUTIONS_PER_RECORD",
    "EXECUTION_STATUSES",
    "normalize_queue_record",
    "is_terminal",
    "is_dead_letter",
    "retries_exhausted",
    "mark_dead_letter",
    "requeue_from_dead_letter",
    "build_execution",
    "append_execution",
    "consecutive_same_error_count",
    "repeated_same_error",
    "exhaustion_reason",
    "scan_for_stuck_records",
    "recover_stuck_records",
    "count_by_status",
]

# --- Statuses -------------------------------------------------------
DLQ_STATUS = "dead_letter"
LEGACY_FAILED_STATUS = "failed"
TERMINAL_STATUSES = frozenset({
    "done", "failed", "dead_letter", "blocked", "cancelled", "duplicate",
})
# Transient in-progress states. NO writer produces these today (see
# module docstring §3) — they are recognised defensively so a future
# drain that marks start-of-run, or a crash mid-run, cannot strand
# a record forever.
TRANSIENT_STATUSES = frozenset({"running", "in_progress", "started"})
# Same error this many times in a row => dead-letter early, even
# before the retry budget is spent (policy choice, see §5).
REPEAT_THRESHOLD = 3
# Per-record execution-history cap (see module docstring §2).
MAX_EXECUTIONS_PER_RECORD = 100
EXECUTION_STATUSES = frozenset({"done", "failed", "error", "timeout"})


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# --- Normalisation / status helpers ---------------------------------

def normalize_queue_record(record):
    """Fill the tasks-v1 defaults on a task record (in place).

    Mirrors scripts/run_office.py::normalize_task_record (same
    defaults, same depends_on repair) and additionally defaults
    the Phase 4 queue fields: "executions" ([]), "dead_letter_reason"
    (None), "dead_letter_at" (None), "executions_trimmed" (0).
    Old records without the new fields still drain unchanged —
    nothing here deletes or renames a field. Returns the record.
    """
    if not isinstance(record, dict):
        raise ValueError("task record must be an object, got "
                         + type(record).__name__)
    record.setdefault("priority", 0)
    record.setdefault("depends_on", [])
    record.setdefault("retries", 0)
    record.setdefault("max_retries", 0)
    record.setdefault("cancelled", False)
    record.setdefault("idempotency_key", None)
    record.setdefault("last_error", None)
    record.setdefault("executions", [])
    record.setdefault("dead_letter_reason", None)
    record.setdefault("dead_letter_at", None)
    record.setdefault("executions_trimmed", 0)
    if not isinstance(record.get("depends_on"), list):
        record["depends_on"] = []
    if not isinstance(record.get("executions"), list):
        record["executions"] = []
    return record


def is_terminal(record):
    """True when the record's status can never run again.

    Legacy "failed" counts as terminal (pre-Phase-4 equivalent of
    "dead_letter"). Unknown statuses are NOT terminal — fail closed
    toward "may still need handling", never toward dropping a task.
    """
    return record.get("status") in TERMINAL_STATUSES


def is_dead_letter(record):
    """True only for the DLQ status "dead_letter"."""
    return record.get("status") == DLQ_STATUS


def count_by_status(records):
    """{"total": n, <status>: count, ...} for a list of records."""
    counts = {"total": len(records)}
    for rec in records:
        status = rec.get("status") if isinstance(rec, dict) else None
        counts[status] = counts.get(status, 0) + 1
    return counts


# --- Dead-letter ------------------------------------------------------

def retries_exhausted(retries, max_retries):
    """True when the retry budget is spent, POST-increment.

    Matches the drain's rule exactly: after a failure the drain
    computes retries = old retries + 1 and retries again while
    retries <= max_retries. So the budget is spent when
    retries > max_retries. max_retries counts RETRIES after the
    first attempt (max_retries=0 => the first failure exhausts).
    Non-integer / negative inputs fail closed (ValueError) — a
    retry budget must be a real number, never a guess.
    """
    if (not isinstance(retries, int) or isinstance(retries, bool)
            or not isinstance(max_retries, int)
            or isinstance(max_retries, bool)):
        raise ValueError("retries and max_retries must be integers, got "
                         f"{retries!r} and {max_retries!r}")
    if retries < 0 or max_retries < 0:
        raise ValueError("retries and max_retries must be >= 0, got "
                         f"{retries!r} and {max_retries!r}")
    return retries > max_retries


def mark_dead_letter(record, reason, last_error=None, now=None):
    """Move a record to "dead_letter" (in place). Returns the record.

    reason is REQUIRED (non-empty string) — a DLQ move without a
    reason is a lost diagnosis. last_error is preserved when given
    (and kept when not given); the record's result and executions
    history are untouched. A record already in "dead_letter" keeps
    its original dead_letter_at and gains the new reason only if
    it had none — the first DLQ move is the audit fact, later
    calls must not rewrite it.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("mark_dead_letter needs a non-empty reason "
                         "string")
    if not isinstance(record, dict):
        raise ValueError("task record must be an object")
    if last_error is not None:
        record["last_error"] = str(last_error)
    if record.get("status") != DLQ_STATUS:
        record["status"] = DLQ_STATUS
        record["dead_letter_reason"] = reason.strip()
        record["dead_letter_at"] = now or _now_iso()
    elif not record.get("dead_letter_reason"):
        record["dead_letter_reason"] = reason.strip()
    return record


def requeue_from_dead_letter(record, reason, now=None):
    """Move a "dead_letter" (or legacy "failed") record back to
    "queued" (in place). MANUAL ONLY — nothing in the codebase
    calls this; it exists for an explicit human / Boss decision.

    reason is REQUIRED (non-empty string) — an anonymous requeue
    is a silent retry, which the DLQ exists to prevent. Resets
    retries to 0, clears last_error and the dead-letter fields,
    and records requeue_reason / requeued_at / requeue_count
    (incremented per requeue). The executions history is KEPT —
    the requeue must not erase why the task died. Raises
    ValueError for a wrong status or an empty reason. Returns the
    record.
    """
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("requeue_from_dead_letter needs a non-empty "
                         "reason string — a DLQ requeue is a manual "
                         "decision, never automatic")
    if not isinstance(record, dict):
        raise ValueError("task record must be an object")
    if record.get("status") not in (DLQ_STATUS, LEGACY_FAILED_STATUS):
        raise ValueError(
            "cannot requeue a record in status "
            f"{record.get('status')!r} — only 'dead_letter' or legacy "
            "'failed' can be requeued")
    record["status"] = "queued"
    record["retries"] = 0
    record["last_error"] = None
    record["dead_letter_reason"] = None
    record["dead_letter_at"] = None
    record["requeue_reason"] = reason.strip()
    record["requeued_at"] = now or _now_iso()
    record["requeue_count"] = (record.get("requeue_count") or 0) + 1
    return record


# --- Structured execution records -------------------------------------

def build_execution(task_id, attempt, status, started_at=None,
                    finished_at=None, error=None, cost_usd=0.0):
    """One per-attempt execution record (a plain dict, not stored).

    Fields: attempt (1-based), task_id, started_at, finished_at
    (ISO strings; default to now when omitted), status in
    {"done","failed","error","timeout"}, error (string or None),
    cost_usd (number >= 0 — the cost is RECORDED honestly; the $0
    cap is enforced by the runtime / free_only_guard, never by
    hiding a cost here). Raises ValueError on a bad status, a
    non-numeric or negative cost, or a non-string error.
    """
    if status not in EXECUTION_STATUSES:
        raise ValueError("execution status must be one of "
                         + ", ".join(sorted(EXECUTION_STATUSES))
                         + f", got {status!r}")
    if (not isinstance(cost_usd, (int, float))
            or isinstance(cost_usd, bool)):
        raise ValueError(f"cost_usd must be a number, got {cost_usd!r}")
    if cost_usd < 0:
        raise ValueError(f"cost_usd must be >= 0, got {cost_usd!r}")
    if error is not None and not isinstance(error, str):
        raise ValueError(f"error must be a string or None, got {error!r}")
    if not isinstance(attempt, int) or isinstance(attempt, bool) \
            or attempt < 1:
        raise ValueError(f"attempt must be a positive integer, got "
                         f"{attempt!r}")
    now = _now_iso()
    return {
        "attempt": attempt,
        "task_id": task_id,
        "started_at": started_at or now,
        "finished_at": finished_at or now,
        "status": status,
        "error": error,
        "cost_usd": cost_usd,
    }


def append_execution(record, execution):
    """Append an execution record to record["executions"] (in place).

    Creates the list when missing (old-schema records). Enforces
    the cap: past MAX_EXECUTIONS_PER_RECORD the oldest entries
    are dropped and "executions_trimmed" counts them, so the trim
    is visible, never silent. Validates the execution has the
    build_execution() fields. Returns the execution.
    """
    if not isinstance(record, dict):
        raise ValueError("task record must be an object")
    if not isinstance(execution, dict):
        raise ValueError("execution must be an object")
    for key in ("attempt", "task_id", "started_at", "finished_at",
                "status", "error", "cost_usd"):
        if key not in execution:
            raise ValueError(f"execution is missing field {key!r}")
    executions = record.get("executions")
    if not isinstance(executions, list):
        executions = []
        record["executions"] = executions
    executions.append(execution)
    while len(executions) > MAX_EXECUTIONS_PER_RECORD:
        executions.pop(0)
        record["executions_trimmed"] = \
            (record.get("executions_trimmed") or 0) + 1
    return execution


def consecutive_same_error_count(record):
    """Trailing executions with the identical non-null error.

    Counts backwards from the newest execution while the error
    string is equal and non-null. A null error breaks the run —
    a success (or an error-less failure) is not "the same error".
    Records without executions count 0.
    """
    executions = record.get("executions") or []
    if not isinstance(executions, list) or not executions:
        return 0
    last_error = executions[-1].get("error")
    if not last_error:
        return 0
    count = 0
    for entry in reversed(executions):
        if not isinstance(entry, dict):
            break
        if entry.get("error") == last_error:
            count += 1
        else:
            break
    return count


def repeated_same_error(record, threshold=REPEAT_THRESHOLD):
    """True when the same error failed >= threshold times in a row."""
    if (not isinstance(threshold, int) or isinstance(threshold, bool)
            or threshold < 1):
        raise ValueError(f"threshold must be a positive integer, got "
                         f"{threshold!r}")
    return consecutive_same_error_count(record) >= threshold


def exhaustion_reason(record):
    """Why this record should dead-letter now, or None.

    Checks in order: (1) retries exhausted — retries (already
    incremented for this attempt) > max_retries; (2) the same
    error repeated REPEAT_THRESHOLD times in a row. Returns
    "retries_exhausted", "repeated_same_error: <error>", or None.
    The record's executions list MUST already include the current
    attempt (the caller appends it first, then asks) — the count
    is judged on the record as it stands, never speculatively.
    """
    retries = record.get("retries") or 0
    max_retries = record.get("max_retries") or 0
    if retries_exhausted(retries, max_retries):
        return "retries_exhausted"
    if repeated_same_error(record):
        error = (record.get("executions") or [])[-1].get("error")
        return f"repeated_same_error: {error}"
    return None


# --- Restart-recovery scan ----------------------------------------------

def scan_for_stuck_records(records):
    """Find records stuck in a transient in-progress state.

    Input: a list of task-record dicts (read-only — nothing is
    modified). Returns a list of findings, one per stuck record:
    {"record_id", "status", "started_at", "reason"}.
    A record is STUCK when its status is in TRANSIENT_STATUSES
    ("running" / "in_progress" / "started") OR it carries a
    "started_at" timestamp but has no terminal status (crashed
    between start-of-run and marking). Terminal records, queued
    records with no started_at, and records without an id are
    never flagged. FINDING (see module docstring §3): no writer
    today produces either shape, so on a live store this scan is
    expected to return [] — it exists so a crash or a future
    drain change cannot strand a record silently.
    Precondition: run only at startup while no drain is running —
    a record mid-run in another process looks identical.
    """
    findings = []
    for rec in records or []:
        if not isinstance(rec, dict):
            continue
        status = rec.get("status")
        started_at = rec.get("started_at")
        if is_terminal(rec):
            continue
        if status in TRANSIENT_STATUSES:
            findings.append({
                "record_id": rec.get("id"),
                "status": status,
                "started_at": started_at,
                "reason": f"transient_status:{status}",
            })
        elif started_at:
            findings.append({
                "record_id": rec.get("id"),
                "status": status,
                "started_at": started_at,
                "reason": "started_but_not_terminal",
            })
    return findings


def recover_stuck_records(store_dir, policy="requeue",
                          reason="restart-recovery scan", now=None):
    """Scan a store dir and safely recover stuck records.

    policy "requeue" (default): stuck record -> "queued", the
    stuck marker cleared (started_at moved to
    last_stuck_started_at, so the evidence is kept), retries NOT
    incremented (the attempt never completed). policy
    "mark_failed": stuck record -> legacy "failed" with
    last_error set — the operator's explicit choice for a record
    that must never run again; if its retries are already
    exhausted it goes to "dead_letter" instead, with the recovery
    reason recorded. Any other policy raises ValueError.
    Writes through store_io.update_json (locked, atomic) and
    audits each recovery as event "task_recovered" (soft-fail —
    a failed audit write never breaks recovery). NEVER deletes,
    NEVER executes, NEVER loses the record. A missing tasks.json
    returns an empty report; a corrupt tasks.json raises (a
    corrupt store must be noticed, per store_io's rule).
    Returns {"store_dir", "policy", "reason", "found": [...],
    "recovered": [{"record_id", "action", "from_status", ...}],
    "skipped": [...]}. "found" lists every stuck record seen;
    "recovered" lists what was done; "skipped" lists stuck
    records that could not be recovered (no id).
    """
    if policy not in ("requeue", "mark_failed"):
        raise ValueError("policy must be 'requeue' or 'mark_failed', "
                         f"got {policy!r}")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("recover_stuck_records needs a non-empty "
                         "reason string")
    tasks_path = os.path.join(store_dir, "tasks.json")
    data = read_json(tasks_path, default={"schema": "tasks-v1",
                                          "records": []})
    records = data.get("records", []) if isinstance(data, dict) else []
    if not isinstance(records, list):
        return {"store_dir": store_dir, "policy": policy,
                "reason": reason, "found": [], "recovered": [],
                "skipped": [],
                "note": "tasks.json records is not a list — nothing "
                        "recovered"}
    findings = scan_for_stuck_records(records)
    by_id = {rec.get("id"): rec for rec in records
             if isinstance(rec, dict)}
    recovered = []
    skipped = []
    stamp = now or _now_iso()

    def _apply(payload):
        recs = payload.get("records", []) \
            if isinstance(payload, dict) else []
        if not isinstance(recs, list):
            recs = []
        for finding in findings:
            record_id = finding["record_id"]
            rec = next((r for r in recs if isinstance(r, dict)
                        and r.get("id") == record_id), None)
            if rec is None:
                skipped.append({"record_id": record_id,
                                "reason": "record vanished before "
                                          "recovery"})
                continue
            from_status = rec.get("status")
            if policy == "requeue":
                if rec.get("started_at"):
                    rec["last_stuck_started_at"] = rec.get("started_at")
                rec["started_at"] = None
                rec["status"] = "queued"
                rec["recovery_action"] = "requeued"
                rec["recovery_reason"] = reason.strip()
                rec["recovered_at"] = stamp
                action = "requeued"
            else:  # mark_failed
                if rec.get("started_at"):
                    rec["last_stuck_started_at"] = rec.get("started_at")
                rec["started_at"] = None
                retries = rec.get("retries") or 0
                max_retries = rec.get("max_retries") or 0
                if retries_exhausted(retries, max_retries):
                    mark_dead_letter(
                        rec,
                        f"recovery: {reason.strip()} — retries already "
                        "exhausted",
                        last_error=rec.get("last_error")
                        or "recovered from stuck state",
                        now=stamp)
                    action = "dead_letter"
                else:
                    rec["status"] = LEGACY_FAILED_STATUS
                    rec["last_error"] = (
                        rec.get("last_error")
                        or "recovered from stuck state: "
                        + finding["reason"])
                    rec["recovery_action"] = "marked_failed"
                    rec["recovery_reason"] = reason.strip()
                    rec["recovered_at"] = stamp
                    action = "marked_failed"
            recovered.append({"record_id": record_id,
                              "action": action,
                              "from_status": from_status,
                              "reason": finding["reason"]})
        return {"schema": data.get("schema", "tasks-v1")
                if isinstance(data, dict) else "tasks-v1",
                "records": recs}

    if findings:
        update_json(tasks_path, _apply,
                    default={"schema": "tasks-v1", "records": []})
        for item in recovered:
            audit_log("task_recovered",
                      {"task_id": item["record_id"],
                       "action": item["action"],
                       "from": item["from_status"],
                       "reason": reason.strip()},
                      store_dir=store_dir)
    return {"store_dir": store_dir, "policy": policy,
            "reason": reason.strip(), "found": findings,
            "recovered": recovered, "skipped": skipped}


if __name__ == "__main__":
    # Self-test — pure in-memory checks only (no disk, no tempfile,
    # no network). The store-level wrapper is exercised against
    # stubbed store_io/audit functions, never the real store.
    # Run: python3 00-CEO-Core/workflow_engine/queue.py
    # (or: python3 -c "import importlib.util; ..." from the repo root)
    _TS = "2026-11-25T01:00:00+00:00"

    # -- normalize: old-schema record gains defaults, keeps fields --
    old = {"id": "old1", "status": "done", "business": "agency",
           "type": "research", "title": "old record", "payload": {}}
    normalize_queue_record(old)
    assert old["priority"] == 0 and old["retries"] == 0
    assert old["max_retries"] == 0 and old["depends_on"] == []
    assert old["executions"] == [] and old["dead_letter_reason"] is None
    assert old["title"] == "old record"  # nothing renamed or lost

    # -- retries_exhausted matches the drain's post-increment rule --
    assert retries_exhausted(1, 0) is True   # max 0: first failure ends it
    assert retries_exhausted(1, 2) is False
    assert retries_exhausted(2, 2) is False  # 2 <= 2: one more retry
    assert retries_exhausted(3, 2) is True
    try:
        retries_exhausted(-1, 0)
        raise SystemExit("FAIL: negative retries did not raise")
    except ValueError:
        pass

    # -- DLQ transition: reason required, last_error kept, never drains --
    rec = {"id": "t1", "status": "queued", "business": "agency",
           "type": "caption_write", "title": "t", "payload": {},
           "retries": 3, "max_retries": 2, "last_error": "boom"}
    normalize_queue_record(rec)
    assert exhaustion_reason(rec) == "retries_exhausted"
    try:
        mark_dead_letter(rec, "  ")
        raise SystemExit("FAIL: empty DLQ reason did not raise")
    except ValueError:
        pass
    mark_dead_letter(rec, "retries_exhausted", last_error="boom",
                     now=_TS)
    assert rec["status"] == "dead_letter"
    assert rec["dead_letter_reason"] == "retries_exhausted"
    assert rec["dead_letter_at"] == _TS and rec["last_error"] == "boom"
    assert is_dead_letter(rec) is True and is_terminal(rec) is True
    assert scan_for_stuck_records([rec]) == []  # DLQ is terminal, not stuck
    assert count_by_status([rec])["dead_letter"] == 1

    # -- requeue: explicit reason only, manual only --
    try:
        requeue_from_dead_letter(rec, "")
        raise SystemExit("FAIL: empty requeue reason did not raise")
    except ValueError:
        pass
    requeue_from_dead_letter(rec, "Boss: retry once, fixed prompt",
                             now=_TS)
    assert rec["status"] == "queued" and rec["retries"] == 0
    assert rec["last_error"] is None
    assert rec["dead_letter_reason"] is None
    assert rec["requeue_count"] == 1
    assert rec["requeue_reason"] == "Boss: retry once, fixed prompt"
    try:
        requeue_from_dead_letter(rec, "again")
        raise SystemExit("FAIL: requeue of queued record did not raise")
    except ValueError:
        pass
    # legacy "failed" is requeueable too (pre-DLQ equivalent)
    legacy = {"id": "t2", "status": "failed", "retries": 1,
              "max_retries": 0, "last_error": "old boom"}
    requeue_from_dead_letter(legacy, "Boss: retry legacy failed",
                             now=_TS)
    assert legacy["status"] == "queued" and legacy["retries"] == 0

    # -- executions: build / append / cap / repeated error --
    r2 = {"id": "t3", "status": "queued", "retries": 0, "max_retries": 5}
    e1 = build_execution("t3", 1, "failed", started_at=_TS,
                         finished_at=_TS, error="boom", cost_usd=0.0)
    assert e1["attempt"] == 1 and e1["cost_usd"] == 0.0
    append_execution(r2, e1)
    append_execution(r2, build_execution(
        "t3", 2, "failed", started_at=_TS, finished_at=_TS,
        error="boom", cost_usd=0.0))
    assert consecutive_same_error_count(r2) == 2
    assert repeated_same_error(r2) is False
    append_execution(r2, build_execution(
        "t3", 3, "failed", started_at=_TS, finished_at=_TS,
        error="boom", cost_usd=0.0))
    assert consecutive_same_error_count(r2) == 3
    assert repeated_same_error(r2) is True
    assert exhaustion_reason(r2) == "repeated_same_error: boom"
    append_execution(r2, build_execution(
        "t3", 4, "done", started_at=_TS, finished_at=_TS,
        error=None, cost_usd=0.0))
    assert consecutive_same_error_count(r2) == 0  # success breaks the run
    try:
        build_execution("t3", 5, "failed", cost_usd=-1.0)
        raise SystemExit("FAIL: negative cost did not raise")
    except ValueError:
        pass
    try:
        build_execution("t3", 5, "weird")
        raise SystemExit("FAIL: bad execution status did not raise")
    except ValueError:
        pass
    # cap: 100 kept, trims counted, never silent
    r3 = {"id": "t4", "status": "queued"}
    for i in range(1, 105):
        append_execution(r3, build_execution(
            "t4", i, "failed", started_at=_TS, finished_at=_TS,
            error="x", cost_usd=0.0))
    assert len(r3["executions"]) == MAX_EXECUTIONS_PER_RECORD
    assert r3["executions"][0]["attempt"] == 5
    assert r3["executions_trimmed"] == 4

    # -- scan: nothing stuck in today's shapes; stuck shapes found --
    assert scan_for_stuck_records([
        {"id": "a", "status": "queued"},
        {"id": "b", "status": "done"},
        {"id": "c", "status": "dead_letter"},
        {"id": "d", "status": "failed"},   # legacy failed: terminal
    ]) == []
    stuck = scan_for_stuck_records([
        {"id": "s1", "status": "running", "started_at": _TS},
        {"id": "s2", "status": "queued", "started_at": _TS},
        {"id": "s3", "status": "in_progress"},
    ])
    assert [f["record_id"] for f in stuck] == ["s1", "s2", "s3"], stuck
    assert stuck[0]["reason"] == "transient_status:running"
    assert stuck[1]["reason"] == "started_but_not_terminal"

    # -- store-level recovery, against STUBBED store_io (no disk) --
    _fake_store = {"schema": "tasks-v1", "records": [
        {"id": "s1", "status": "running", "started_at": _TS,
         "retries": 0, "max_retries": 2},
        {"id": "ok1", "status": "done"},
        {"id": "s2", "status": "queued", "started_at": _TS,
         "retries": 5, "max_retries": 2},
    ]}
    _audited = []

    def _fake_read(path, default=None):
        import copy
        return copy.deepcopy(_fake_store)

    def _fake_update(path, fn, default=None):
        global _fake_store
        _fake_store = fn(_fake_store)
        return _fake_store

    def _fake_audit(event, details=None, store_dir=None,
                    audit_path=None):
        _audited.append((event, details))
        return True

    _real_read, _real_update, _real_audit = (
        read_json, update_json, audit_log)
    globals()["read_json"] = _fake_read
    globals()["update_json"] = _fake_update
    globals()["audit_log"] = _fake_audit
    try:
        report = recover_stuck_records(
            "/tmp/fake-store", policy="requeue",
            reason="test restart scan", now=_TS)
        assert len(report["found"]) == 2, report
        assert {r["record_id"] for r in report["recovered"]} == {
            "s1", "s2"}, report
        assert all(r["action"] == "requeued"
                   for r in report["recovered"])
        by_id = {r["id"]: r for r in _fake_store["records"]}
        assert by_id["s1"]["status"] == "queued"
        assert by_id["s1"]["started_at"] is None
        assert by_id["s1"]["last_stuck_started_at"] == _TS
        assert by_id["s1"]["retries"] == 0  # attempt never completed
        assert by_id["s1"]["recovery_reason"] == "test restart scan"
        assert by_id["ok1"]["status"] == "done"  # untouched
        assert len(_audited) == 2 and all(
            e == "task_recovered" for e, _ in _audited)
        # mark_failed policy: exhausted retries -> dead_letter
        _fake_store["records"] = [
            {"id": "s9", "status": "running", "started_at": _TS,
             "retries": 4, "max_retries": 2, "last_error": "crash"}]
        _audited.clear()
        report = recover_stuck_records(
            "/tmp/fake-store", policy="mark_failed",
            reason="operator: never run again", now=_TS)
        assert _fake_store["records"][0]["status"] == "dead_letter"
        assert "retries already exhausted" in \
            _fake_store["records"][0]["dead_letter_reason"]
        assert _fake_store["records"][0]["last_error"] == "crash"
        try:
            recover_stuck_records("/tmp/fake-store", policy="delete")
            raise SystemExit("FAIL: bad policy did not raise")
        except ValueError:
            pass
    finally:
        globals()["read_json"] = _real_read
        globals()["update_json"] = _real_update
        globals()["audit_log"] = _real_audit

    print("queue: OK (normalize old-schema; retries_exhausted matches "
          "drain; DLQ move + reason required; requeue manual + "
          "reason required; executions build/append/cap/repeat; "
          "scan finds stuck shapes only; stubbed-store recovery "
          "requeue + mark_failed)")
