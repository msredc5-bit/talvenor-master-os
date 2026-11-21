"""Quiet schedules — change-only watches, one run at a time
(Improvement Phase 3, modelled on Nod's schedules.ts + proactivity.ts).

Nod's pattern (~/workspace/nod-reverse/reverse-engineering.md):
  - Schedules only report change: if nothing changed in a watch, the run
    is skipped (checked without a model call — an empty run costs nothing).
  - Only one run at a time; approvals apply to schedules too; a correction
    changes only the changed part and keeps the rest ("Every hour instead" only
    changes the timing).
  - Proactivity: the observer checks without a model call; it may build a private
    preparation draft — it cannot send / delete / submit / book /
    buy.

In this file (Python, stdlib only, no network / live call):
  - watch_marker(state) — the observable state's sha256 hash (last-seen
    state). If the state has not changed, the marker stays the same -> run skipped, quiet.
  - ScheduleStore — schedules.json: add / get / list / pause / resume /
    should_run / begin_run / end_run / skip / apply_correction /
    clear_stale_lock.
  - run_watch() — run one watch: state unchanged -> skip (no work,
    only skips are counted); changed -> run once, update the marker;
    if the work fails, the marker is not updated (it tries again next
    time — a watch is re-run safe, not a commit).
  - file_state() / tasks_queue_state() — the hash of store/tasks.json
    (for the bridge's empty-queue check — adoption is Boss's/parent's
    decision, not automatic).

Rules:
  - Only one run at a time (running lock; a lock older than 60 minutes is
    stale — it can be released with clear_stale_lock).
  - A correction changes only the named field; everything else stays as it was.
  - This module sends / publishes / spends / deletes nothing — it only decides
    when to run.

Usage:
  store = ScheduleStore()  # store/schedules.json
  s = store.add("taskboard-queue-watch", kind="watch",
                source="store/tasks.json", interval_minutes=10)
  out = run_watch(store, s["id"],
                  state_fn=tasks_queue_state,
                  work_fn=lambda: {"note": "queue drained (mock)"})
  # out = {"ran": False, "reason": "unchanged — quiet"} or {"ran": True, ...}

Status: REAL (Improvement Phase 3, 2026-11-21) — runs on the mock brain.
"""

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_SCHEDULES_PATH = os.path.join(_STORE_DIR, "schedules.json")
DEFAULT_TASKS_PATH = os.path.join(_STORE_DIR, "tasks.json")

SCHEDULE_KINDS = ("watch", "recurring")
SCHEDULE_STATUSES = ("active", "paused")
# A lock counts as stale after 60 minutes (modelled on Nod's one-run-at-a-time + stale
# lock release).
STALE_LOCK_MINUTES = 60
# Only these fields may change in a correction — everything else stays as it was.
CORRECTABLE_FIELDS = ("name", "kind", "source", "interval_minutes",
                      "status", "note")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value):
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def watch_marker(state):
    """Hash of the observable state — if the state has not changed, the marker is the same."""
    canonical = json.dumps(state, sort_keys=True, ensure_ascii=False,
                           default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def file_state(path):
    """A file's observable state (bytes hash + size) — if the file is missing,
    {"missing": True} (a different marker, so the first run happens)."""
    try:
        with open(path, "rb") as f:
            data = f.read()
        return {
            "path": os.path.basename(str(path)),
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
        }
    except OSError:
        return {"path": os.path.basename(str(path)), "missing": True}


def tasks_queue_state(tasks_path=None):
    """The state of store/tasks.json — for the bridge's queue watch."""
    return file_state(tasks_path or DEFAULT_TASKS_PATH)


class ScheduleStore:
    """Schedules + their last-seen markers — quiet by default."""

    def __init__(self, schedules_path=None):
        self.schedules_path = schedules_path or DEFAULT_SCHEDULES_PATH
        self._load()

    def _load(self):
        try:
            with open(self.schedules_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data.get("records", []) if isinstance(data, dict) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.records = []

    def _save(self):
        payload = {
            "schema": "schedules-v1",
            "note": ("Quiet schedules: a watch runs only when its observed "
                     "state changed. One run at a time. Corrections keep "
                     "the rest."),
            "records": self.records,
        }
        parent = os.path.dirname(self.schedules_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(self.schedules_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def add(self, name, kind="watch", source="", interval_minutes=10,
            status="active", note=""):
        if kind not in SCHEDULE_KINDS:
            raise ValueError(f"Unknown kind {kind!r}. Allowed: {list(SCHEDULE_KINDS)}")
        if status not in SCHEDULE_STATUSES:
            raise ValueError(f"Unknown status {status!r}.")
        if not name or not str(name).strip():
            raise ValueError("name must be a non-empty string.")
        if int(interval_minutes) <= 0:
            raise ValueError("interval_minutes must be positive.")
        record = {
            "id": uuid.uuid4().hex[:12],
            "name": name,
            "kind": kind,
            "source": source,
            "interval_minutes": int(interval_minutes),
            "status": status,
            "last_marker": None,
            "last_run_at": None,
            "last_result": None,
            "last_skip_reason": None,
            "running": False,
            "run_started_at": None,
            "runs": 0,
            "skips": 0,
            "created_at": _now_iso(),
            "note": note,
        }
        self.records.append(record)
        self._save()
        return dict(record)

    def get(self, schedule_id):
        for record in self.records:
            if record["id"] == schedule_id:
                return dict(record)
        raise KeyError(f"No schedule with id {schedule_id!r}")

    def list(self, active_only=False):
        if active_only:
            return [dict(r) for r in self.records if r["status"] == "active"]
        return [dict(r) for r in self.records]

    def pause(self, schedule_id):
        return self.apply_correction(schedule_id, status="paused")

    def resume(self, schedule_id):
        return self.apply_correction(schedule_id, status="active")

    def apply_correction(self, schedule_id, **changes):
        """A correction changes only the named field — everything else stays as it was.
        An unknown field raises ValueError (never silently ignored)."""
        record = self._find(schedule_id)
        for field in changes:
            if field not in CORRECTABLE_FIELDS:
                raise ValueError(
                    f"Cannot correct field {field!r}. Correctable: "
                    f"{list(CORRECTABLE_FIELDS)}")
        for field, value in changes.items():
            if field == "kind" and value not in SCHEDULE_KINDS:
                raise ValueError(f"Unknown kind {value!r}.")
            if field == "status" and value not in SCHEDULE_STATUSES:
                raise ValueError(f"Unknown status {value!r}.")
            if field == "interval_minutes" and int(value) <= 0:
                raise ValueError("interval_minutes must be positive.")
            record[field] = value
        self._save()
        return dict(record)

    def _is_stale_lock(self, record):
        started = _parse_iso(record.get("run_started_at"))
        if started is None:
            return True
        age = datetime.now(timezone.utc) - started
        return age.total_seconds() > STALE_LOCK_MINUTES * 60

    def should_run(self, schedule_id, current_state):
        """Whether a run should happen in this state (decided without doing work)."""
        record = self._find(schedule_id)
        if record["status"] != "active":
            return False, f"schedule is {record['status']} — skipped"
        if record.get("running"):
            if self._is_stale_lock(record):
                return True, "stale lock — previous run is older than 60 min"
            return False, "already running — one run at a time"
        marker = watch_marker(current_state)
        if record.get("last_marker") is None:
            return True, "first run — no marker yet"
        if marker == record["last_marker"]:
            return False, "unchanged — quiet"
        return True, "changed — state differs from last marker"

    def begin_run(self, schedule_id):
        record = self._find(schedule_id)
        if record.get("running") and not self._is_stale_lock(record):
            raise ValueError(
                f"Schedule {schedule_id} is already running — one run "
                "at a time.")
        record["running"] = True
        record["run_started_at"] = _now_iso()
        self._save()
        return dict(record)

    def end_run(self, schedule_id, result, current_state=None):
        """End of a run — release the lock. If current_state is given, the marker is updated
        (a successful run); if not, the marker stays as it was (a failed watch
        will try again next time)."""
        record = self._find(schedule_id)
        if not record.get("running"):
            raise ValueError(f"Schedule {schedule_id} is not running.")
        record["running"] = False
        record["run_started_at"] = None
        record["last_run_at"] = _now_iso()
        record["last_result"] = result
        record["runs"] += 1
        if current_state is not None:
            record["last_marker"] = watch_marker(current_state)
        self._save()
        return dict(record)

    def skip(self, schedule_id, reason):
        """Count a quiet skip — no work happened, only a record."""
        record = self._find(schedule_id)
        record["skips"] += 1
        record["last_skip_reason"] = reason
        self._save()
        return dict(record)

    def clear_stale_lock(self, schedule_id):
        record = self._find(schedule_id)
        if not record.get("running"):
            return dict(record)
        if not self._is_stale_lock(record):
            raise ValueError(
                f"Schedule {schedule_id} is running and the lock is not "
                "stale yet — wait for it to finish.")
        record["running"] = False
        record["run_started_at"] = None
        record["last_result"] = {"note": "stale lock cleared"}
        self._save()
        return dict(record)

    def _find(self, schedule_id):
        for record in self.records:
            if record["id"] == schedule_id:
                return record
        raise KeyError(f"No schedule with id {schedule_id!r}")


def run_watch(store, schedule_id, state_fn, work_fn):
    """Run one watch — change-only, one run at a time.

    state_fn() -> current observable state (without a model call).
    work_fn() -> result (runs only if the state changed).
    Returns {"ran": bool, "reason": str, "result": ...}.
    If the work fails, the lock is released and the marker is not updated.
    """
    state = state_fn()
    should, reason = store.should_run(schedule_id, state)
    if not should:
        store.skip(schedule_id, reason)
        return {"ran": False, "reason": reason, "result": None}
    store.begin_run(schedule_id)
    try:
        result = work_fn()
    except Exception as exc:  # noqa: BLE001 — release the lock, not the marker
        store.end_run(schedule_id, {"error": f"{type(exc).__name__}: {exc}"},
                      current_state=None)
        raise
    store.end_run(schedule_id, result, current_state=state)
    return {"ran": True, "reason": reason, "result": result}


if __name__ == "__main__":
    # Manual check: in a TEMP file, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_sched = os.path.join(tmp_dir, "schedules-test.json")

    store = ScheduleStore(schedules_path=tmp_sched)
    s = store.add("queue-watch", kind="watch", source="store/tasks.json",
                  interval_minutes=10)
    assert s["status"] == "active" and s["last_marker"] is None

    # 1. First run — no marker -> runs.
    out = run_watch(store, s["id"], lambda: {"ids": ["a"]},
                    lambda: {"worked": 1})
    assert out["ran"] is True and out["reason"].startswith("first run"), out
    assert store.get(s["id"])["runs"] == 1

    # 2. Same state -> quiet skip, no work.
    calls = []
    out = run_watch(store, s["id"], lambda: {"ids": ["a"]},
                    lambda: calls.append(1) or {"worked": 1})
    assert out["ran"] is False and "quiet" in out["reason"], out
    assert calls == [] and store.get(s["id"])["skips"] == 1

    # 3. State changed -> runs again.
    out = run_watch(store, s["id"], lambda: {"ids": ["a", "b"]},
                    lambda: {"worked": 2})
    assert out["ran"] is True and out["reason"].startswith("changed"), out

    # 4. Paused -> skip.
    store.pause(s["id"])
    out = run_watch(store, s["id"], lambda: {"ids": ["c"]},
                    lambda: {"worked": 3})
    assert out["ran"] is False and "paused" in out["reason"], out
    store.resume(s["id"])

    # 5. A correction changes only the named field; the rest stays as it was.
    before = store.get(s["id"])
    after = store.apply_correction(s["id"], interval_minutes=60)
    assert after["interval_minutes"] == 60
    assert after["last_marker"] == before["last_marker"]
    assert after["runs"] == before["runs"]
    try:
        store.apply_correction(s["id"], last_marker="forged")
        raise SystemExit("FAIL: correction changed a protected field")
    except ValueError:
        pass

    # 6. One run at a time — begin_run cannot happen twice.
    store.begin_run(s["id"])
    try:
        store.begin_run(s["id"])
        raise SystemExit("FAIL: overlapping run was allowed")
    except ValueError:
        pass
    store.end_run(s["id"], {"manual": True}, current_state={"ids": ["c"]})
    assert store.get(s["id"])["running"] is False

    # 7. Work fails -> the lock is released, the marker stays as it was.
    marker_before = store.get(s["id"])["last_marker"]
    def _boom():
        raise RuntimeError("work failed")
    try:
        run_watch(store, s["id"], lambda: {"ids": ["d"]}, _boom)
        raise SystemExit("FAIL: failed work did not raise")
    except RuntimeError:
        pass
    after_fail = store.get(s["id"])
    assert after_fail["running"] is False
    assert after_fail["last_marker"] == marker_before
    print("quiet_schedules: OK (first run, quiet skip, change re-runs, "
          "pause, correction keeps rest, one-run lock, failed work keeps marker)")
