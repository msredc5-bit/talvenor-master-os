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
   "last_error": null}         # set on a failed attempt that retries
Drain marks each processed record "done" (or "failed") with its
result attached; a record whose dependency failed is "blocked"; a
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
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
DEFAULT_STORE_DIR = os.path.join(ROOT, "store")

sys.path.insert(0, CEO_CORE_DIR)

from audit import audit_log  # noqa: E402
from store_io import update_json, write_json_atomic  # noqa: E402
import main_ceo_bot  # noqa: E402
import vault  # noqa: E402 — D3: drain writes done/failed task results to the vault

BUSINESS_ALIASES = {
    "agency": "agency",
    "products": "digital-product",
    "digital-product": "digital-product",
    "content": "content",
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


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
    for key in ("gated_action", "approval_id", "requested_by"):
        if input_data.get(key) is not None:
            task[key] = input_data[key]
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


def run_one(business, task_type, input_data, store_dir):
    """Route one task in-process and return its result dict."""
    os.makedirs(store_dir, exist_ok=True)
    tasks_path = os.path.join(store_dir, "tasks.json")
    approvals_path = os.path.join(store_dir, "approvals.json")
    task = build_task(business, task_type, input_data)
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
    for key in ("gated_action", "approval_id", "requested_by"):
        if record.get(key) is not None:
            input_data[key] = record[key]
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
                        retries=None, last_error=None):
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
    if status not in ("done", "failed"):
        return None  # only done/failed results go to the vault (D3)
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
    done_or_failed_keys = {
        rec.get("idempotency_key") for rec in records
        if rec.get("status") in ("done", "failed")
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
        if key and (key in done_or_failed_keys
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
    """The id of a failed/blocked/cancelled/duplicate dependency, or
    None when every dependency is done (or there is none)."""
    by_id = {rec.get("id"): rec for rec in records}
    terminal_bad = ("failed", "blocked", "cancelled", "duplicate")
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
    while retries < max_retries, else it is "failed". Records are
    re-read before every pick, so a dependency chain drains in one
    run. Every transition is appended to store/audit.log."""
    os.makedirs(store_dir, exist_ok=True)
    tasks_path = os.path.join(store_dir, "tasks.json")
    processed = []
    executions = 0
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
        try:
            ok, result = _run_one_subprocess(record, store_dir)
        except Exception as exc:  # noqa: BLE001 — a failed drain must not crash the run
            ok, result = False, {"error": f"{type(exc).__name__}: {exc}"}
        executions += 1
        if ok and result.get("status") != "error":
            vault_error = _mark_queued_record(
                tasks_path, record["id"], "done", result)
            _audit_task_transition(store_dir, record["id"], "queued", "done")
            entry = {"id": record["id"], "business": record.get("business"),
                     "type": record.get("type"), "status": "done"}
            if vault_error:
                entry["vault_error"] = vault_error
            processed.append(entry)
        else:
            retries = (record.get("retries") or 0) + 1
            chief_result = result.get("chief_result") or {}
            last_error = str(result.get("error")
                             or chief_result.get("error")
                             or result.get("status")
                             or "run failed")
            if retries <= (record.get("max_retries") or 0):
                _mark_queued_record(tasks_path, record["id"], "queued",
                                    result, retries=retries,
                                    last_error=last_error)
                _audit_task_transition(store_dir, record["id"], "queued",
                                       "queued",
                                       note=f"retry {retries}/{record.get('max_retries')}")
                processed.append({"id": record["id"],
                                  "business": record.get("business"),
                                  "type": record.get("type"),
                                  "status": "queued-retry",
                                  "retries": retries})
            else:
                vault_error = _mark_queued_record(
                    tasks_path, record["id"], "failed", result,
                    retries=retries, last_error=last_error)
                _audit_task_transition(store_dir, record["id"], "queued",
                                       "failed", note=last_error)
                entry = {"id": record["id"],
                         "business": record.get("business"),
                         "type": record.get("type"), "status": "failed"}
                if vault_error:
                    entry["vault_error"] = vault_error
                processed.append(entry)
    return {"mode": "drain-queue", "store_dir": store_dir,
            "max": max_tasks, "processed": processed}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run a Talvenor Master OS task via the Main CEO Bot.",
        epilog="Examples:\n"
               "  run one task: --business agency --task caption_write "
               "--input '{\"title\": \"...\"}'\n"
               "  find a skill: --business agency --task find_skill "
               "--input '{\"query\": \"backup\"}'\n"
               "  drain the queue: --drain-queue --max 2 "
               "(done/failed result also lands in store/vault/)",
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
