#!/usr/bin/env python3
"""Quiet-schedule runner — run the watches in store/schedules.json (A1).

Runner for 00-CEO-Core/quiet_schedules.py's ScheduleStore + run_watch():
if the state has not changed, the watch quiet-skips (no work); if changed,
it runs once. Seeded watch `taskboard-queue-watch` (source
store/tasks.json, paused) — when the queue changes, the drain work_fn runs: the queue
is drained (run_office.drain_queue — draft/result only, gated
work gets stuck in PENDING; done/failed results are also written to the vault).

This runner schedules nothing itself — one run checks once.
Whether the bridge cron (every 10 minutes, outside the repo) runs it is
Boss/parent's decision; if the schedule is `paused`, the runner does
nothing (run_watch itself skips).

Usage:
  python3 scripts/run_quiet_schedules.py --list
  python3 scripts/run_quiet_schedules.py
  python3 scripts/run_quiet_schedules.py --schedule-id <id> --max 2
  python3 scripts/run_quiet_schedules.py --store-dir /tmp/store-test

--store-dir defaults to the repo's real store/ — tests must pass a TEMP dir
so the real store is not touched. Stdlib only. No network,
no send, no publish, no spend, no delete.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
DEFAULT_STORE_DIR = os.path.join(ROOT, "store")

sys.path.insert(0, CEO_CORE_DIR)

from quiet_schedules import (  # noqa: E402
    ScheduleStore, file_state, run_watch, tasks_queue_state)


def _resolve_source(source, store_dir):
    """A schedule's source (repo-relative, e.g. store/tasks.json) ->
    the real path. If it starts with "store/..." it is taken inside store_dir
    (also correct in a TEMP store); other relative paths are relative to
    the repo root. Absolute paths stay as they are."""
    if not source:
        return os.path.join(store_dir, "tasks.json")
    if os.path.isabs(source):
        return source
    if source == "store" or source.startswith("store/"):
        return os.path.join(store_dir, source[len("store/"):])
    return os.path.join(ROOT, source)


def _state_fn_for(schedule, store_dir):
    source = schedule.get("source") or ""
    if "tasks.json" in source:
        tasks_path = _resolve_source(source, store_dir)
        return lambda: tasks_queue_state(tasks_path)
    path = _resolve_source(source, store_dir)
    return lambda: file_state(path)


def _drain_work_fn(store_dir, max_tasks):
    """Queue drain — run_office.drain_queue (lazy import: --list does not load
    the Main CEO Bot)."""
    if SCRIPTS_DIR not in sys.path:
        sys.path.insert(0, SCRIPTS_DIR)
    import run_office  # noqa: PLC0415
    return lambda: run_office.drain_queue(store_dir, max_tasks)


def _work_fn_for(schedule, store_dir, max_tasks):
    source = schedule.get("source") or ""
    if "tasks.json" in source:
        return _drain_work_fn(store_dir, max_tasks)
    return lambda: {"note": "no drain work for this source",
                    "source": source}


def run_all(store_dir, schedule_id=None, max_tasks=2):
    """Run all (or one) watch schedules; returns: a summary dict."""
    schedules_path = os.path.join(store_dir, "schedules.json")
    store = ScheduleStore(schedules_path=schedules_path)
    schedules = store.list()
    if schedule_id:
        schedules = [s for s in schedules if s["id"] == schedule_id]
        if not schedules:
            raise ValueError(f"No schedule with id {schedule_id!r}.")
    ran, skipped, errors = [], [], []
    for schedule in schedules:
        if schedule.get("kind") != "watch":
            skipped.append({"id": schedule["id"], "name": schedule.get("name"),
                            "reason": f"kind {schedule.get('kind')!r} — "
                                      "runner only runs watches"})
            continue
        try:
            out = run_watch(
                store, schedule["id"],
                state_fn=_state_fn_for(schedule, store_dir),
                work_fn=_work_fn_for(schedule, store_dir, max_tasks))
        except Exception as exc:  # noqa: BLE001 — if one watch fails, the others still run
            errors.append({"id": schedule["id"], "name": schedule.get("name"),
                           "error": f"{type(exc).__name__}: {exc}"})
            continue
        entry = {"id": schedule["id"], "name": schedule.get("name"),
                 "ran": out["ran"], "reason": out["reason"]}
        if out["ran"]:
            entry["result"] = out.get("result")
            ran.append(entry)
        else:
            skipped.append(entry)
    return {"mode": "run-quiet-schedules", "store_dir": store_dir,
            "ran": ran, "skipped": skipped, "errors": errors}


def list_schedules(store_dir):
    """Summary of all schedules (read-only)."""
    store = ScheduleStore(
        schedules_path=os.path.join(store_dir, "schedules.json"))
    return [{"id": s["id"], "name": s["name"], "kind": s["kind"],
             "source": s.get("source"), "status": s["status"],
             "interval_minutes": s.get("interval_minutes"),
             "runs": s.get("runs"), "skips": s.get("skips"),
             "last_run_at": s.get("last_run_at"),
             "last_skip_reason": s.get("last_skip_reason")}
            for s in store.list()]


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Run quiet schedules (change-only watches) once.")
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR,
                        help="store dir (default: repo store/)")
    parser.add_argument("--schedule-id", default=None,
                        help="run only this schedule id")
    parser.add_argument("--max", type=int, default=2,
                        help="max queued tasks drained per watch run (default 2)")
    parser.add_argument("--list", action="store_true",
                        help="list schedules and exit (read-only)")
    args = parser.parse_args(argv)

    os.makedirs(args.store_dir, exist_ok=True)
    if args.list:
        print(json.dumps(list_schedules(args.store_dir), indent=2,
                         ensure_ascii=False))
        return 0
    try:
        summary = run_all(args.store_dir, schedule_id=args.schedule_id,
                          max_tasks=args.max)
    except ValueError as exc:
        print(f"run_quiet_schedules: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
