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
queues work — e.g. the bridge cron in dashboards/n8n-wiring.md):
  {"id": "...", "status": "queued", "business": "agency",
   "type": "outreach_draft", "title": "...", "payload": {...},
   "gated_action": "send", "queued_at": "..."}
Drain marks each processed record "done" (or "failed") with its
result attached. Each queued task runs in its OWN subprocess: the
two vendored worker trees both expose a top-level `src` package, so
an agency task and a content task cannot be imported in one process
(verified Phase 6) — subprocesses keep drain correct for any mix.

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
    payload = {"schema": "tasks-v1", "records": records}
    with open(tasks_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


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


def _mark_queued_record(tasks_path, record_id, status, result):
    """Update one queued record IN PLACE, re-reading the file first.

    Re-reading matters: the subprocess run already appended the
    Chief's own log entry to tasks.json — a blind write-back of the
    pre-drain records would delete it. After marking, the result is also written
    to the vault (store/vault/README.md's promise — D3); if the vault write fails,
    the drain result still stands, only vault_error is set.
    """
    records = _read_store_tasks(tasks_path)
    vault_error = None
    for rec in records:
        if rec.get("id") == record_id:
            rec["status"] = status
            rec["result"] = result
            rec["drained_at"] = _now_iso()
            break
    else:
        _write_store_tasks(tasks_path, records)
        return None
    _write_store_tasks(tasks_path, records)
    try:
        store_dir = os.path.dirname(tasks_path)
        vault.write_result(store_dir, rec)
    except Exception as exc:  # noqa: BLE001 — the vault never breaks the drain
        vault_error = f"{type(exc).__name__}: {exc}"
    return vault_error


def drain_queue(store_dir, max_tasks):
    """Process up to max_tasks queued records; return a summary dict."""
    os.makedirs(store_dir, exist_ok=True)
    tasks_path = os.path.join(store_dir, "tasks.json")
    queued = [r for r in _read_store_tasks(tasks_path)
              if r.get("status") == "queued"][:max_tasks]
    processed = []
    for record in queued:
        try:
            ok, result = _run_one_subprocess(record, store_dir)
        except Exception as exc:  # noqa: BLE001 — a failed drain must not crash the run
            ok, result = False, {"error": f"{type(exc).__name__}: {exc}"}
        status = "done" if ok and result.get("status") != "error" else "failed"
        vault_error = _mark_queued_record(tasks_path, record["id"], status, result)
        entry = {"id": record["id"], "business": record.get("business"),
                 "type": record.get("type"), "status": status}
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
