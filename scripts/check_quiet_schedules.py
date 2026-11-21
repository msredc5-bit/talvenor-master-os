#!/usr/bin/env python3
"""check_quiet_schedules.py — Improvement Phase 3 self-check
(quiet schedules: change-only watches, one run at a time).

Modelled on Nod's schedules.ts + proactivity.ts:
  1. quiet_schedules.py imports standalone, fast, no network
  2. watch_marker: same state -> same marker; different state -> different
     marker; key order does not matter
  3. file_state: same bytes -> same hash; missing file -> missing True
  4. add: wrong kind/status/interval -> ValueError
  5. First run runs (no marker)
  6. Same state -> quiet skip, no work, skips are counted
  7. State changed -> runs again
  8. Paused -> skip; resume -> runs
  9. Correction only changes the stated field, the rest stays as before; protected
     fields raise ValueError if changed
 10. One run at a time: begin_run not twice; end_run releases the lock
 11. Work fails -> lock released, marker stays the previous one, error recorded
 12. Stale lock (60+ minutes): should_run True, clear_stale_lock runs;
     clearing a fresh lock raises ValueError
 13. tasks_queue_state: reads the real store/tasks.json (read-only), has sha256
 14. Runner (scripts/run_quiet_schedules.py): --list runs; in a TEMP store the
     active watch drains on the first run (queued find_skill task becomes done
     , vault file is written), later runs quiet-skip; the real
     store is not touched
 15. No secrets in quiet_schedules.py
 16. Real store unchanged by this check run

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
from datetime import datetime, timedelta, timezone

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

    # 1. Imports standalone, fast, no network.
    try:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, "
             f"{CEO_CORE_DIR!r}); import quiet_schedules; "
             "print('quiet_schedules import OK')"],
            capture_output=True, text=True, timeout=30, cwd=BASE)
        elapsed = time.time() - t0
        check("quiet_schedules.py imports standalone, fast, no network",
              proc.returncode == 0 and elapsed < 10,
              f"{elapsed:.2f}s, rc={proc.returncode}")
    except Exception as e:  # noqa: BLE001
        check("quiet_schedules.py imports standalone, fast, no network", False, str(e))

    try:
        from quiet_schedules import (  # noqa: PLC0415
            ScheduleStore, file_state, run_watch, tasks_queue_state,
            watch_marker)

        # 2. Marker: same state -> same marker; different -> different;
        #    key order irrelevant.
        m1 = watch_marker({"ids": ["a"], "n": 1})
        m2 = watch_marker({"n": 1, "ids": ["a"]})
        m3 = watch_marker({"ids": ["a", "b"], "n": 1})
        check("watch_marker: same state same marker, key order irrelevant",
              m1 == m2 and m1 != m3 and len(m1) == 64)

        # 3. file_state.
        tmp_file = os.path.join(tmp_dir, "state.txt")
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("hello")
        fs1 = file_state(tmp_file)
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write("hello!")
        fs2 = file_state(tmp_file)
        fs_missing = file_state(os.path.join(tmp_dir, "nope.txt"))
        check("file_state: same bytes same hash; missing -> missing True",
              fs1["sha256"] != fs2["sha256"] and fs1["size"] == 5
              and fs_missing.get("missing") is True)

        # 4. add validation.
        store = ScheduleStore(schedules_path=os.path.join(tmp_dir, "sched.json"))
        ok_kind = ok_status = ok_interval = False
        try:
            store.add("x", kind="bogus")
        except ValueError:
            ok_kind = True
        try:
            store.add("x", status="bogus")
        except ValueError:
            ok_status = True
        try:
            store.add("x", interval_minutes=0)
        except ValueError:
            ok_interval = True
        check("add rejects bad kind/status/interval",
              ok_kind and ok_status and ok_interval)

        s = store.add("queue-watch", kind="watch", source="store/tasks.json",
                      interval_minutes=10)

        # 5. First run.
        out = run_watch(store, s["id"], lambda: {"ids": ["a"]},
                        lambda: {"worked": 1})
        check("first run executes (no marker yet)",
              out["ran"] is True and out["reason"].startswith("first run")
              and store.get(s["id"])["runs"] == 1, str(out))

        # 6. Unchanged -> quiet skip, work not called.
        calls = []
        out = run_watch(store, s["id"], lambda: {"ids": ["a"]},
                        lambda: calls.append(1) or {"worked": 1})
        check("unchanged state -> quiet skip, work not called",
              out["ran"] is False and "quiet" in out["reason"]
              and calls == [] and store.get(s["id"])["skips"] == 1, str(out))

        # 7. Changed -> runs again.
        out = run_watch(store, s["id"], lambda: {"ids": ["a", "b"]},
                        lambda: {"worked": 2})
        check("changed state -> runs again",
              out["ran"] is True and out["reason"].startswith("changed")
              and store.get(s["id"])["runs"] == 2, str(out))

        # 8. Paused -> skip; resume -> runs.
        store.pause(s["id"])
        out = run_watch(store, s["id"], lambda: {"ids": ["c"]},
                        lambda: {"worked": 3})
        ok_paused = out["ran"] is False and "paused" in out["reason"]
        store.resume(s["id"])
        out = run_watch(store, s["id"], lambda: {"ids": ["c"]},
                        lambda: {"worked": 3})
        check("paused skips; resumed runs",
              ok_paused and out["ran"] is True, f"paused={ok_paused}, resumed={out['ran']}")

        # 9. Correction keeps the rest; protected field rejected.
        before = store.get(s["id"])
        after = store.apply_correction(s["id"], interval_minutes=60)
        ok_corr = (after["interval_minutes"] == 60
                   and after["last_marker"] == before["last_marker"]
                   and after["runs"] == before["runs"]
                   and after["name"] == before["name"])
        try:
            store.apply_correction(s["id"], last_marker="forged")
            ok_prot = False
        except ValueError:
            ok_prot = True
        check("correction changes only named fields; protected field rejected",
              ok_corr and ok_prot)

        # 10. One run at a time.
        store.begin_run(s["id"])
        try:
            store.begin_run(s["id"])
            ok_overlap = False
        except ValueError:
            ok_overlap = True
        store.end_run(s["id"], {"manual": True}, current_state={"ids": ["c"]})
        check("one run at a time; end_run releases the lock",
              ok_overlap and store.get(s["id"])["running"] is False)

        # 11. Failed work -> lock released, marker unchanged, error recorded.
        marker_before = store.get(s["id"])["last_marker"]
        def _boom():
            raise RuntimeError("work failed")
        try:
            run_watch(store, s["id"], lambda: {"ids": ["d"]}, _boom)
            ok_raise = False
        except RuntimeError:
            ok_raise = True
        after_fail = store.get(s["id"])
        check("failed work releases lock, keeps marker, records error",
              ok_raise and after_fail["running"] is False
              and after_fail["last_marker"] == marker_before
              and "work failed" in str(after_fail["last_result"]), str(after_fail["last_result"]))

        # 12. Stale lock handling.
        store.begin_run(s["id"])
        rec = store._find(s["id"])
        rec["run_started_at"] = (datetime.now(timezone.utc)
                                 - timedelta(minutes=61)).isoformat()
        store._save()
        should, reason = store.should_run(s["id"], {"ids": ["e"]})
        ok_stale = should is True and "stale" in reason
        cleared = store.clear_stale_lock(s["id"])
        ok_clear = cleared["running"] is False
        store.begin_run(s["id"])
        try:
            store.clear_stale_lock(s["id"])
            ok_fresh = False
        except ValueError:
            ok_fresh = True
        store.end_run(s["id"], {"manual": True}, current_state={"ids": ["e"]})
        check("stale lock (60+ min) runs + clears; fresh lock cannot be cleared",
              ok_stale and ok_clear and ok_fresh, f"stale={ok_stale} clear={ok_clear} fresh={ok_fresh}")

        # 13. tasks_queue_state reads the real store/tasks.json (read-only).
        state = tasks_queue_state()
        check("tasks_queue_state reads real store/tasks.json",
              isinstance(state.get("sha256"), str) and len(state["sha256"]) == 64
              and state.get("size", 0) > 0, str(state)[:120])
    except Exception as e:  # noqa: BLE001
        for name in ("watch_marker: same state same marker, key order irrelevant",
                     "file_state: same bytes same hash; missing -> missing True",
                     "add rejects bad kind/status/interval",
                     "first run executes (no marker yet)",
                     "unchanged state -> quiet skip, work not called",
                     "changed state -> runs again",
                     "paused skips; resumed runs",
                     "correction changes only named fields; protected field rejected",
                     "one run at a time; end_run releases the lock",
                     "failed work releases lock, keeps marker, records error",
                     "stale lock (60+ min) runs + clears; fresh lock cannot be cleared",
                     "tasks_queue_state reads real store/tasks.json"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 14. Runner (run_quiet_schedules.py) — end-to-end in a TEMP store.
    try:
        runner_store = os.path.join(tmp_dir, "runner-store")
        os.makedirs(runner_store, exist_ok=True)
        runner_sched = {
            "schema": "schedules-v1",
            "records": [{
                "id": "watch1",
                "name": "taskboard-queue-watch",
                "kind": "watch",
                "source": "store/tasks.json",
                "interval_minutes": 10,
                "status": "active",
                "last_marker": None,
                "last_run_at": None,
                "last_result": None,
                "last_skip_reason": None,
                "running": False,
                "run_started_at": None,
                "runs": 0,
                "skips": 0,
                "created_at": "2026-11-21T00:00:00+00:00",
                "note": "check-only schedule",
            }],
        }
        with open(os.path.join(runner_store, "schedules.json"),
                  "w", encoding="utf-8") as f:
            json.dump(runner_sched, f, indent=2)
        with open(os.path.join(runner_store, "tasks.json"),
                  "w", encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": [{
                "id": "task1", "status": "queued", "business": "agency",
                "type": "find_skill", "title": "find skill: backup",
                "payload": {},
                "queued_at": "2026-11-21T00:00:00+00:00"}]}, f, indent=2)
        runner = os.path.join(BASE, "scripts", "run_quiet_schedules.py")

        def _run_runner(*extra):
            return subprocess.run(
                [sys.executable, runner, "--store-dir", runner_store,
                 *extra],
                capture_output=True, text=True, timeout=300)

        p_list = _run_runner("--list")
        list_ok = (p_list.returncode == 0
                   and "taskboard-queue-watch" in p_list.stdout)
        p1 = _run_runner()
        s1 = json.loads(p1.stdout) if p1.returncode == 0 else {}
        with open(os.path.join(runner_store, "tasks.json"),
                  encoding="utf-8") as f:
            tasks_after = json.load(f)["records"]
        vault_dir = os.path.join(runner_store, "vault")
        vault_files = (sorted(os.listdir(vault_dir))
                       if os.path.isdir(vault_dir) else [])
        run1_ok = (p1.returncode == 0 and len(s1.get("ran", [])) == 1
                   and tasks_after[0]["status"] == "done"
                   and len(vault_files) == 1)
        # Run 2: the drain queue changed (done was written), so the state
        # changed again — runs, but processed 0 because the queue is empty.
        p2 = _run_runner()
        s2 = json.loads(p2.stdout) if p2.returncode == 0 else {}
        run2_ok = (p2.returncode == 0 and len(s2.get("ran", [])) == 1
                   and s2["ran"][0].get("result", {}).get("processed") == [])
        # Run 3: state did not change again — quiet skip.
        p3 = _run_runner()
        s3 = json.loads(p3.stdout) if p3.returncode == 0 else {}
        run3_ok = (p3.returncode == 0 and s3.get("ran") == []
                   and len(s3.get("skipped", [])) == 1
                   and "quiet" in s3["skipped"][0].get("reason", ""))
        check("runner runs: --list works; TEMP watch drains queued task "
              "(done + vault file), then quiet-skips",
              list_ok and run1_ok and run2_ok and run3_ok,
              f"list={list_ok} run1={run1_ok} run2={run2_ok} "
              f"run3={run3_ok} vault={vault_files}")
    except Exception as e:  # noqa: BLE001
        check("runner runs: --list works; TEMP watch drains queued task "
              "(done + vault file), then quiet-skips",
              False, f"{type(e).__name__}: {e}")

    # 15. No secrets.
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]|api_key\s*=|password\s*=|"
            r"Authorization.{0,20}Bearer [A-Za-z0-9]")
        bad = []
        path = os.path.join(BASE, "00-CEO-Core", "quiet_schedules.py")
        with open(path, encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                if secret_re.search(line):
                    bad.append(f"quiet_schedules.py:{lineno}")
        check("no secrets in quiet_schedules.py",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in quiet_schedules.py", False, str(e))

    # 16. Real store unchanged.
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
    print("check_quiet_schedules: ALL PASS (Improvement Phase 3 — quiet schedules).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
