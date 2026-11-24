#!/usr/bin/env python3
"""Runner — run the Talvenor Master OS offices from this machine (Phase 6).

One command to ROUTE a task through the Main CEO Bot -> Chief ->
worker chain, with gates enforced by the ApprovalGateway. A gated
action writes PENDING and never executes. Results are printed to
stdout as JSON and appended to store/tasks.json by the Chief.

Usage:
  # One task (mock brain, draft only):
  python3 scripts/run_office.py --business agency --task caption_write \\
      --input '{"title": "Caption for Monday reel", "payload": {}}'
  python3 scripts/run_office.py --business content --task script_write \\
      --input ./task.json
  python3 scripts/run_office.py --business products --task gate0_check \\
      --input '{}'

  # Skill search (business-agnostic — does not go to a Chief, local search +
  # DRAFT proposal; --business accepts any value, route_task decides by type
  # first):
  python3 scripts/run_office.py --business agency --task find_skill \\
      --input '{"query": "backup", "title": "find skill: backup"}'

  # Gated action -> PENDING, never executed:
  python3 scripts/run_office.py --business agency --task outreach_draft \\
      --input '{"title": "Send Day 4 batch", "gated_action": "send"}'

  # Drain the queue (up to N queued tasks per run):
  python3 scripts/run_office.py --drain-queue --max 2
  python3 scripts/run_office.py --drain-queue --max 2 --store-dir /tmp/store-test

--input is a JSON file path if the file exists, else a JSON string.
--store-dir defaults to the repo's real store/ — point it at a TEMP
dir for tests so the real store stays empty (0 records).
--business accepts: agency, products (= digital-product), content.

Queued-task record shape (in store/tasks.json, written by whatever
queues work — e.g. the bridge cron in dashboards/n8n-wiring.md).
Phase 1 (Unified OS) extends the tasks-v1 schema — old records
without the new fields still drain (defaults fill in):
  {"id": "...", "status": "queued", "business": "agency",
   "type": "outreach_draft", "title": "...", "payload": {...},
   "gated_action": "send", "queued_at": "...",
   "priority": 0,              # higher drains first
   "depends_on": [],           # ids that must be "done" first
   "retries": 0, "max_retries": 0,   # failure retry budget
   "cancelled": false,        # cancelled tasks are never run
   "idempotency_key": null,    # same key twice = one execution
   "last_error": null,         # set on a failed attempt that retries
   "executions": [...],        # Phase 4: per-attempt records
                               # {attempt, task_id, started_at,
                               #  finished_at, status, error, cost_usd}
   "dead_letter_reason": null, # Phase 4: why the record died
   "dead_letter_at": null}     # Phase 4: when it moved to DLQ
Drain marks each processed record "done" (or "dead_letter" when its
retry budget is exhausted — Phase 4 DLQ; the pre-Phase-4 "failed"
status is kept as a legacy terminal status and still honoured
everywhere) with its result attached; a record whose dependency
failed is "blocked"; a
second record with an already-used idempotency key is "duplicate";
a cancelled record is marked "cancelled". Every transition is
appended to store/audit.log. Each queued task runs in its OWN
subprocess: the two vendored worker trees both expose a top-level
`src` package, so an agency task and a content task cannot be
imported in one process (verified Phase 6) — subprocesses keep
drain correct for any mix.

Stdlib only. No network, no send, no publish, no spend, no delete.
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
DEFAULT_STORE_DIR = os.path.join(ROOT, "store")

sys.path.insert(0, CEO_CORE_DIR)

from audit import audit_log  # noqa: E402
from store_io import update_json, write_json_atomic  # noqa: E402
import control as control_plane  # noqa: E402 — Phase 7: drain consults the control plane first
import main_ceo_bot  # noqa: E402
import vault  # noqa: E402 — D3: drain writes done/dead_letter task results to the vault

BUSINESS_ALIASES = {
    "agency": "agency",
    "products": "digital-product",
    "digital-product": "digital-product",
    "content": "content",
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_queue_module():
    """Lazily load 00-CEO-Core/workflow_engine/queue.py by path
    (Phase 4 queue hardening: DLQ, recovery scan, execution
    records). Loaded under a distinct module name — never `queue`,
    which would shadow the stdlib. Returns the module, or None
    when it cannot be loaded; the drain works without it (the
    retries comparison below still dead-letters exhausted tasks,
    and the recovery scan is simply skipped that run)."""
    import importlib.util
    path = os.path.join(CEO_CORE_DIR, "workflow_engine", "queue.py")
    try:
        spec = importlib.util.spec_from_file_location(
            "talvenor_workflow_queue", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception:
        return None


def _load_json_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _read_store_tasks(tasks_path):
    try:
        data = _load_json_file(tasks_path)
        return data.get("records", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_store_tasks(tasks_path, records):
    # Phase 1 (Unified OS): atomic write — a concurrent writer can no
    # longer tear a half-written tasks file.
    payload = {"schema": "tasks-v1", "records": records}
    write_json_atomic(tasks_path, payload)


def normalize_task_record(record):
    """Fills the Phase 1 (Unified OS) tasks-v1 fields with defaults, so
    a record queued before Phase 1 still drains. Returns the record."""
    record.setdefault("priority", 0)
    record.setdefault("depends_on", [])
    record.setdefault("retries", 0)
    record.setdefault("max_retries", 0)
    record.setdefault("cancelled", False)
    record.setdefault("idempotency_key", None)
    record.setdefault("last_error", None)
    if not isinstance(record.get("depends_on"), list):
        record["depends_on"] = []
    return record


def parse_input(raw):
    """--input value: a JSON file path if it exists, else a JSON string."""
    if raw is None:
        return {}
    if os.path.isfile(raw):
        data = _load_json_file(raw)
    else:
        data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("--input JSON must be an object")
    return data


def build_task(business, task_type, input_data):
    """Input JSON -> the task dict Main CEO Bot expects."""
    task = {
        "business": business,
        "type": task_type,
        "title": input_data.get("title") or f"{business} {task_type}",
        "payload": dict(input_data.get("payload") or {}),
    }
    for key in ("gated_action", "approval_id", "requested_by", "execute"):
        if input_data.get(key) is not None:
            task[key] = input_data[key]
    if task_type == "lead_chain":
        # Phase 6 (local-first): the lead-chain input carries the
        # prospect at the top level (fixture id string or prospect
        # dict), not inside "payload". Forward it verbatim so
        # run_one() can hand it to ChainRunner; a prospect inside
        # "payload" is honoured too.
        if input_data.get("prospect") is not None:
            task["prospect"] = input_data["prospect"]
        elif "prospect" in task["payload"]:
            task["prospect"] = task["payload"]["prospect"]
    if task_type == "find_skill":
        # The skill-finder task's fields (from --input's top level,
        # else from the payload) — otherwise the query is lost and local
        # search runs on an empty query.
        for key in ("query", "propose", "candidate_repo", "candidate_skill",
                    "source_url", "license", "fit_note", "agent", "detail",
                    "proposals_path"):
            if input_data.get(key) is not None:
                task[key] = input_data[key]
            elif key in task["payload"]:
                task[key] = task["payload"][key]
    return task


def _load_chain_runner():
    """Import ChainRunner from the Phase 6 lead_chain package.

    Preferred: ``from lead_chain import ChainRunner`` (package
    export); fallback: ``lead_chain.chain.ChainRunner``. Raises
    ImportError when the package is not built yet — the caller
    reports it instead of routing the task nowhere.
    """
    try:
        from lead_chain import ChainRunner  # noqa: PLC0415
        return ChainRunner
    except ImportError:
        from lead_chain.chain import ChainRunner  # noqa: PLC0415
        return ChainRunner


def _resolve_lead_chain_prospect(prospect):
    """Resolve a fixture-id string via lead_chain.fixtures when the
    package provides it; prospect dicts pass through unchanged.
    Never raises — an unresolvable id is passed through for
    ChainRunner to report as its own error."""
    if not isinstance(prospect, str):
        return prospect
    try:
        import lead_chain.fixtures as fixtures  # noqa: PLC0415
        get_fixture = getattr(fixtures, "get_fixture", None)
        if callable(get_fixture):
            return get_fixture(prospect)
        table = getattr(fixtures, "FIXTURES", None)
        if isinstance(table, dict):
            if prospect in table:
                return table[prospect]
            # Match by the prospect's own "id" field, e.g.
            # "TEST-L-0001" -> the STRONG fixture dict.
            for value in table.values():
                if isinstance(value, dict) \
                        and value.get("id") == prospect:
                    return value
    except Exception:  # noqa: BLE001 — resolution is best-effort
        pass
    return prospect


def run_lead_chain(task, store_dir):
    """Route a lead_chain task to ChainRunner (Phase 6, sandbox).

    The chain runs against the --store-dir passed on the CLI (a
    temp dir in acceptance), NEVER the real store by default — the
    caller (run_one) passes store_dir straight through. Everything
    is draft-only, $0; the gated send is held and deployment stays
    blocked inside the chain. The result is also appended to
    store_dir/tasks.json (same tasks-v1 shape the Chief writes) so
    the execution is recorded; a failed log write never breaks the
    run. Returns the run_office result dict; the full ChainRunner
    result lives under "chain_result".
    """
    os.makedirs(store_dir, exist_ok=True)
    prospect = task.get("prospect")
    if prospect is None:
        prospect = (task.get("payload") or {}).get("prospect")
    prospect = _resolve_lead_chain_prospect(prospect)
    ChainRunner = _load_chain_runner()
    try:
        runner = ChainRunner()
    except TypeError:
        runner = ChainRunner(store_dir)
    try:
        chain_result = runner.run(prospect, store_dir)
    except TypeError:
        chain_result = runner.run(prospect)
    if not isinstance(chain_result, dict):
        chain_result = {"status": "error",
                        "error": "ChainRunner.run returned a non-dict "
                                 "result",
                        "result": chain_result}
    status = chain_result.get("status") or "error"
    result = {
        "routed_to": "00-CEO-Core.lead_chain.ChainRunner",
        "business": task.get("business"),
        "title": task.get("title"),
        "status": status,
        "chain_result": chain_result,
        "cost_usd": chain_result.get("cost_usd", 0.0),
    }
    try:
        tasks_path = os.path.join(store_dir, "tasks.json")

        def _apply(data):
            records = data.get("records", []) \
                if isinstance(data, dict) else []
            if not isinstance(records, list):
                records = []
            records.append({
                "id": uuid.uuid4().hex[:12],
                "department": "agency",
                "title": task.get("title"),
                "type": "lead_chain",
                "worker": "ChainRunner",
                "status": status,
                "logged_at": _now_iso(),
            })
            return {"schema": "tasks-v1", "records": records}

        update_json(tasks_path, _apply,
                    default={"schema": "tasks-v1", "records": []})
    except Exception:  # noqa: BLE001 — the log never breaks the run
        pass
    return result


def run_one(business, task_type, input_data, store_dir):
    """Route one task in-process and return its result dict."""
    os.makedirs(store_dir, exist_ok=True)
    tasks_path = os.path.join(store_dir, "tasks.json")
    approvals_path = os.path.join(store_dir, "approvals.json")
    task = build_task(business, task_type, input_data)
    if task_type == "lead_chain":
        # Phase 6 (local-first): the sandbox lead chain runs through
        # ChainRunner directly — not through the CEO -> Chief route
        # (the chain is its own router; it is draft-only and holds
        # every gated step itself). The execution is still logged
        # to store_dir/tasks.json by run_lead_chain().
        return run_lead_chain(task, store_dir)
    return main_ceo_bot.route_task(
        task, tasks_path=tasks_path, approvals_path=approvals_path)


def _run_one_subprocess(record, store_dir):
    """Run one queued task in a fresh process; return (ok, result dict).

    A fresh process per task avoids the vendored `src` package
    collision between the agency and content worker trees.
    """
    input_data = {
        "title": record.get("title") or f"{record.get('business')} {record.get('type')}",
        "payload": dict(record.get("payload") or {}),
    }
    for key in ("gated_action", "approval_id", "requested_by", "execute"):
        if record.get(key) is not None:
            input_data[key] = record[key]
    if record.get("type") == "lead_chain" \
            and record.get("prospect") is not None:
        # Phase 6 (local-first): a queued lead_chain record carries
        # its prospect at the top level — forward it so build_task()
        # can hand it to ChainRunner in the subprocess.
        input_data["prospect"] = record["prospect"]
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "run_office.py"),
         "--business", record["business"],
         "--task", record["type"],
         "--input", json.dumps(input_data, ensure_ascii=False),
         "--store-dir", store_dir],
        capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        return False, {"error": (proc.stderr or "").strip()[-500:]
                       or f"runner exited {proc.returncode}"}
    try:
        return True, json.loads(proc.stdout)
    except json.JSONDecodeError:
        return False, {"error": "runner printed non-JSON output",
                       "stdout": proc.stdout[-500:]}


def _audit_task_transition(store_dir, record_id, from_status, to_status,
                           note=None):
    """Appends one task transition to store/audit.log (Phase 1).
    Never raises — a failed audit write must not break the drain."""
    entry = {"task_id": record_id, "from": from_status, "to": to_status}
    if note:
        entry["note"] = note
    audit_log("task_transition", entry,
              audit_path=os.path.join(store_dir, "audit.log"))


def _mark_queued_record(tasks_path, record_id, status, result,
                        retries=None, last_error=None, executions=None,
                        extra=None):
    """Update one queued record IN PLACE, re-reading the file first
    under the store lock (Phase 1, Unified OS: store_io.update_json).

    Re-reading matters: the subprocess run already appended the
    Chief's own log entry to tasks.json — a blind write-back of the
    pre-drain records would delete it. After marking, the result is also written
    to the vault (store/vault/README.md's promise — D3); if the vault write fails,
    the drain result still stands, only vault_error is set.
    Returns the vault error (None when the vault write worked or the
    record was not found), or "store_corrupt_reset" when tasks.json
    was corrupt and had to be reset."""
    holder = {}

    def _apply(data):
        records = data.get("records", []) if isinstance(data, dict) else []
        if not isinstance(records, list):
            records = []
        for rec in records:
            if rec.get("id") == record_id:
                normalize_task_record(rec)  # old records gain the new fields
                rec["status"] = status
                rec["result"] = result
                rec["drained_at"] = _now_iso()
                if retries is not None:
                    rec["retries"] = retries
                if last_error is not None:
                    rec["last_error"] = last_error
                if executions is not None:
                    # Phase 4: structured per-attempt records.
                    rec["executions"] = executions
                if extra:
                    # Phase 4: extra fields, e.g. dead_letter_reason /
                    # dead_letter_at on a DLQ move.
                    rec.update(extra)
                holder["rec"] = rec
                break
        return {"schema": "tasks-v1", "records": records}

    try:
        update_json(tasks_path, _apply,
                    default={"schema": "tasks-v1", "records": []})
    except json.JSONDecodeError:
        # Corrupt store — keep the drain alive, audit it, write fresh.
        # The record being marked is lost with the corrupt file; the
        # drain reports it instead of silently pretending success.
        _audit_task_transition(
            os.path.dirname(tasks_path), record_id, "queued", status,
            note="tasks.json was corrupt — reset; this record was lost.")
        write_json_atomic(tasks_path, {"schema": "tasks-v1", "records": []})
        return "store_corrupt_reset"
    rec = holder.get("rec")
    if rec is None:
        return None  # record vanished meanwhile — nothing to mark
    if status not in ("done", "failed", "dead_letter"):
        return None  # only done/failed/dead_letter results go to the vault (D3)
    try:
        store_dir = os.path.dirname(tasks_path)
        vault.write_result(store_dir, rec)
    except Exception as exc:  # noqa: BLE001 — the vault never breaks the drain
        return f"{type(exc).__name__}: {exc}"
    return None


def _sweep_terminal_states(tasks_path, records):
    """Marks queued records that can never run: cancelled ones, and
    duplicates of an idempotency key that already ran (or is queued
    earlier). Returns the list of (id, new status) marked. The first
    record with a key runs; later ones are duplicates."""
    store_dir = os.path.dirname(tasks_path)
    marked = []
    # First record (by queued_at) with a key is the keeper; later ones
    # with the same key are duplicates.
    seen_keys = {}
    for rec in sorted(records, key=lambda r: r.get("queued_at") or ""):
        key = rec.get("idempotency_key")
        if key and key not in seen_keys:
            seen_keys[key] = rec.get("id")
    terminal_keys = {
        rec.get("idempotency_key") for rec in records
        if rec.get("status") in ("done", "failed", "dead_letter")
        and rec.get("idempotency_key")}
    for rec in records:
        if rec.get("status") != "queued":
            continue
        if rec.get("cancelled") or rec.get("status") == "cancelled":
            _mark_queued_record(tasks_path, rec["id"], "cancelled",
                                {"note": "Task was cancelled — never run."})
            _audit_task_transition(store_dir, rec["id"], "queued",
                                   "cancelled")
            marked.append((rec["id"], "cancelled"))
            continue
        key = rec.get("idempotency_key")
        if key and (key in terminal_keys
                    or seen_keys.get(key) != rec.get("id")):
            _mark_queued_record(
                tasks_path, rec["id"], "duplicate",
                {"note": f"Idempotency key {key!r} already used — not run again."})
            _audit_task_transition(store_dir, rec["id"], "queued",
                                   "duplicate",
                                   note=f"idempotency_key={key}")
            marked.append((rec["id"], "duplicate"))
    return marked


def _blocked_by_failed_dep(record, records):
    """The id of a failed/dead-letter/blocked/cancelled/duplicate
    dependency, or None when every dependency is done (or there is
    none)."""
    by_id = {rec.get("id"): rec for rec in records}
    terminal_bad = ("failed", "dead_letter", "blocked", "cancelled",
                    "duplicate")
    for dep_id in record.get("depends_on") or []:
        dep = by_id.get(dep_id)
        if dep is None:
            return dep_id  # dependency does not exist — can never be done
        if dep.get("status") in terminal_bad:
            return dep_id
    return None


def drain_queue(store_dir, max_tasks):
    """Process up to max_tasks queued records; return a summary dict.

    Order: priority desc, then queued_at asc. A record runs only when
    every depends_on id is "done". Cancelled records are marked
    "cancelled", duplicates "duplicate", records whose dependency
    failed "blocked" — none of those counts toward max_tasks, only
    executions do. A failed run retries (stays queued, retries += 1)
    while retries <= max_retries, else it moves to "dead_letter"
    (Phase 4 DLQ — never auto-retried, never drained as queued).
    Every attempt appends a structured execution record to the task
    (Phase 4). On startup the drain runs the restart-recovery scan
    (Phase 4) and requeues any record stuck in a transient
    in-progress state. Records are re-read before every pick, so a
    dependency chain drains in one run. Every transition is
    appended to store/audit.log.

    Phase 7 (Worker C): BEFORE anything above runs, the drain consults
    the control plane (store/control.json). When paused, emergency-
    stopped, or the control file is corrupt, the drain halts: no task
    executes, nothing is deleted, the halt is recorded in
    store/audit.log (event "control_halt"), and the summary reports
    halted=True with exit code 0."""
    os.makedirs(store_dir, exist_ok=True)
    tasks_path = os.path.join(store_dir, "tasks.json")
    processed = []
    executions = 0
    # Phase 7 (Worker C): control-plane consult — BEFORE any task
    # executes. A halted control plane (paused / emergency_stop /
    # corrupt control file) stops the drain here: nothing runs,
    # nothing is deleted, the halt is recorded, exit 0.
    control_path = os.path.join(store_dir, "control.json")
    try:
        halted, halt_reason = control_plane.consult(control_path)
    except control_plane.ControlCorruptError as exc:
        halted = True
        halt_reason = f"control file corrupt: {exc}"
    if halted:
        audit_log("control_halt",
                  {"reason": halt_reason, "control_path": control_path},
                  audit_path=os.path.join(store_dir, "audit.log"))
        return {"mode": "drain-queue", "store_dir": store_dir,
                "max": max_tasks, "processed": [], "recovered": [],
                "halted": True, "halt_reason": halt_reason}
    # Phase 4: restart-recovery scan — stuck records (transient
    # in-progress state, or started_at with no terminal status) are
    # recovered before any task is picked. A failed scan never
    # breaks the drain; the scan runs again on the next drain.
    _queue = _load_queue_module()
    recovered = []
    if _queue is not None:
        try:
            scan_report = _queue.recover_stuck_records(
                store_dir, policy="requeue",
                reason="restart-recovery scan at drain start")
            recovered = scan_report.get("recovered", [])
        except Exception:
            recovered = []
    # Safety bound: bookkeeping sweeps + executions cannot loop forever.
    for _ in range(max_tasks * 10 + 50):
        if executions >= max_tasks:
            break
        records = [normalize_task_record(r)
                   for r in _read_store_tasks(tasks_path)]
        _sweep_terminal_states(tasks_path, records)
        records = [normalize_task_record(r)
                   for r in _read_store_tasks(tasks_path)]
        queued = [r for r in records if r.get("status") == "queued"]
        if not queued:
            break
        # Block records whose dependency can never complete.
        blocked_any = False
        for rec in queued:
            bad_dep = _blocked_by_failed_dep(rec, records)
            if bad_dep is not None:
                _mark_queued_record(
                    tasks_path, rec["id"], "blocked",
                    {"note": f"Dependency {bad_dep!r} failed or is missing — never run."})
                _audit_task_transition(store_dir, rec["id"], "queued",
                                       "blocked", note=f"dep={bad_dep}")
                processed.append({"id": rec["id"],
                                  "business": rec.get("business"),
                                  "type": rec.get("type"),
                                  "status": "blocked"})
                blocked_any = True
        if blocked_any:
            continue
        # Next eligible: all deps done, highest priority first.
        by_id = {r.get("id"): r for r in records}
        eligible = [
            r for r in queued
            if all(by_id.get(d, {}).get("status") == "done"
                   for d in (r.get("depends_on") or []))]
        if not eligible:
            break  # waiting on queued deps that cannot run in this pass
        eligible.sort(key=lambda r: (-(r.get("priority") or 0),
                                     r.get("queued_at") or ""))
        record = eligible[0]
        started_at = _now_iso()
        try:
            ok, result = _run_one_subprocess(record, store_dir)
        except Exception as exc:  # noqa: BLE001 — a failed drain must not crash the run
            ok, result = False, {"error": f"{type(exc).__name__}: {exc}"}
        finished_at = _now_iso()
        executions += 1
        result_dict = result if isinstance(result, dict) else {}
        succeeded = ok and result_dict.get("status") != "error"
        # Phase 4: one structured execution record per attempt.
        # Recording never breaks the drain — a failure here only
        # means this attempt goes unrecorded.
        executions_list = None
        if _queue is not None:
            try:
                chief_result = result_dict.get("chief_result") or {}
                if not isinstance(chief_result, dict):
                    chief_result = {}
                exec_error = str(result_dict.get("error")
                                 or chief_result.get("error")
                                 or result_dict.get("status")
                                 or "run failed") \
                    if not succeeded else None
                exec_entry = _queue.build_execution(
                    record["id"],
                    len(record.get("executions") or []) + 1,
                    "done" if succeeded else "failed",
                    started_at=started_at, finished_at=finished_at,
                    error=exec_error, cost_usd=0.0)
                _queue.append_execution(record, exec_entry)
                executions_list = record.get("executions")
            except Exception:
                executions_list = None
        if succeeded:
            vault_error = _mark_queued_record(
                tasks_path, record["id"], "done", result,
                executions=executions_list)
            _audit_task_transition(store_dir, record["id"], "queued", "done")
            entry = {"id": record["id"], "business": record.get("business"),
                     "type": record.get("type"), "status": "done"}
            if vault_error:
                entry["vault_error"] = vault_error
            processed.append(entry)
        else:
            retries = (record.get("retries") or 0) + 1
            chief_result = result_dict.get("chief_result") or {}
            if not isinstance(chief_result, dict):
                chief_result = {}
            last_error = str(result_dict.get("error")
                             or chief_result.get("error")
                             or result_dict.get("status")
                             or "run failed")
            # Phase 4: terminal when the budget is spent OR the same
            # error repeated REPEAT_THRESHOLD times in a row.
            dl_reason = None
            if _queue is not None:
                try:
                    record["retries"] = retries
                    record["last_error"] = last_error
                    dl_reason = _queue.exhaustion_reason(record)
                except Exception:
                    dl_reason = None
            if dl_reason is None \
                    and retries > (record.get("max_retries") or 0):
                dl_reason = "retries_exhausted"
            if dl_reason is not None:
                vault_error = _mark_queued_record(
                    tasks_path, record["id"], "dead_letter", result,
                    retries=retries, last_error=last_error,
                    executions=executions_list,
                    extra={"dead_letter_reason": dl_reason,
                           "dead_letter_at": _now_iso()})
                _audit_task_transition(store_dir, record["id"], "queued",
                                       "dead_letter",
                                       note=f"{dl_reason}: {last_error}")
                entry = {"id": record["id"],
                         "business": record.get("business"),
                         "type": record.get("type"),
                         "status": "dead_letter",
                         "dead_letter_reason": dl_reason}
                if vault_error:
                    entry["vault_error"] = vault_error
                processed.append(entry)
            else:
                _mark_queued_record(tasks_path, record["id"], "queued",
                                    result, retries=retries,
                                    last_error=last_error,
                                    executions=executions_list)
                _audit_task_transition(store_dir, record["id"], "queued",
                                       "queued",
                                       note=f"retry {retries}/{record.get('max_retries')}")
                processed.append({"id": record["id"],
                                  "business": record.get("business"),
                                  "type": record.get("type"),
                                  "status": "queued-retry",
                                  "retries": retries})
    return {"mode": "drain-queue", "store_dir": store_dir,
            "max": max_tasks, "processed": processed,
            "recovered": recovered, "halted": False}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run a Talvenor Master OS task via the Main CEO Bot.",
        epilog="Examples:\n"
               "  run one task: --business agency --task caption_write "
               "--input '{\"title\": \"...\"}'\n"
               "  find a skill: --business agency --task find_skill "
               "--input '{\"query\": \"backup\"}'\n"
               "  drain the queue: --drain-queue --max 2 "
               "(done/dead_letter result also lands in store/vault/)",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--business", choices=sorted(BUSINESS_ALIASES),
                        help="agency | products | content")
    parser.add_argument("--task", help="task type, e.g. caption_write")
    parser.add_argument("--input",
                        help="JSON string or path to a JSON file")
    parser.add_argument("--drain-queue", action="store_true",
                        help="process queued tasks from store/tasks.json")
    parser.add_argument("--max", type=int, default=2,
                        help="max queued tasks per drain run (default 2)")
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR,
                        help="store dir (default: repo store/)")
    args = parser.parse_args(argv)

    if args.drain_queue:
        summary = drain_queue(args.store_dir, args.max)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    if not args.business or not args.task:
        parser.error("--business and --task are required (or use --drain-queue)")
    business = BUSINESS_ALIASES[args.business]
    try:
        input_data = parse_input(args.input)
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        print(f"run_office: bad --input: {exc}", file=sys.stderr)
        return 2
    try:
        result = run_one(business, args.task, input_data, args.store_dir)
    except Exception as exc:  # noqa: BLE001 — print the failure, don't crash silently
        print(f"run_office: FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
