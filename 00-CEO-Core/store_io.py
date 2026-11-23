"""Shared store I/O — atomic JSON writes + file locking (Phase 1, Unified OS).

Every writer of a shared store JSON file (tasks.json, usage_ledger.json,
approvals.json, memory.json, schedules.json, goals.json, agent_runs.json)
goes through here, so a concurrent writer (taskboard server, drain
subprocess, bridge cron) cannot tear a half-written file or silently
lose another writer's record.

Rules:
  - Writes are atomic: the payload is written to a temp file in the SAME
    directory, fsynced, then os.replace()d over the target. A reader never
    sees a half-written file.
  - Updates are locked: update_json() holds an exclusive flock on
    "<path>.lock" while it reads, applies the change, and writes. The lock
    file is a runtime artifact (add "*.lock" to .gitignore); it is never
    committed and never contains data.
  - Portability: flock needs fcntl (Linux/macOS). On Windows (the
    Founder's PC) fcntl is missing — the lock becomes a no-op and the
    atomic write still protects against torn files; concurrent writers on
    Windows can still race each other (documented limitation, same as
    before this module — the atomic write is strictly better than the
    plain open/write it replaces).
  - read_json() returns `default` when the file is missing, but RAISES
    on corrupt JSON — a corrupt store file must be noticed, not silently
    treated as empty.

Stdlib only. No network, no send, no publish, no spend.
"""

import json
import os
import tempfile
import threading

try:
    import fcntl
    _HAVE_FCNTL = True
except ImportError:  # Windows — no fcntl
    fcntl = None
    _HAVE_FCNTL = False

from contextlib import contextmanager

HAVE_FCNTL = _HAVE_FCNTL

# In-process locks, keyed by lock-file path — a second thread in this
# process waits here instead of blocking on flock (flock also works
# between threads, but the threading lock makes the wait explicit).
_thread_locks = {}
_thread_locks_guard = threading.Lock()


def _thread_lock_for(lock_path):
    with _thread_locks_guard:
        lock = _thread_locks.get(lock_path)
        if lock is None:
            lock = threading.Lock()
            _thread_locks[lock_path] = lock
        return lock


def lock_path_for(path):
    """The lock file for a store file — "<path>.lock", next to the file."""
    return str(path) + ".lock"


@contextmanager
def locked_file(path):
    """Hold an exclusive lock on "<path>.lock" for the block.

    No-op on platforms without fcntl (Windows) — the atomic write still
    applies. Never raises for a missing lock directory (it is created).
    """
    lock_path = lock_path_for(path)
    parent = os.path.dirname(os.path.abspath(lock_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    thread_lock = _thread_lock_for(lock_path)
    thread_lock.acquire()
    fd = None
    try:
        if _HAVE_FCNTL:
            fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o644)
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            if fd is not None:
                fcntl.flock(fd, fcntl.LOCK_UN)
                os.close(fd)
        finally:
            thread_lock.release()


def read_json(path, default=None):
    """Read a JSON file. Missing file -> default. Corrupt JSON -> raises."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        raise


def write_json_atomic(path, payload):
    """Write payload (a dict/list) as JSON, atomically (temp + os.replace).

    The temp file lives in the same directory as the target, so the
    replace is on one filesystem. The file is fsynced before the replace.
    """
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    fd, tmp_path = tempfile.mkstemp(prefix=".store-tmp-",
                                    dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    return path


def update_json(path, fn, default=None):
    """Locked read-modify-write: data = read (or default); new = fn(data);
    write new atomically. Returns the new payload.

    fn receives the loaded data (a dict/list, or `default` when the file
    is missing) and must return the payload to write. The whole
    read-apply-write happens under the file lock, so no concurrent
    writer's record is lost.
    """
    with locked_file(path):
        data = read_json(path, default=default)
        new_data = fn(data)
        write_json_atomic(path, new_data)
        return new_data


def append_json_line(path, record):
    """Append one JSON object as a line (for .log files, e.g. audit.log).

    The append happens under the file lock, so lines from concurrent
    writers cannot interleave. The file is created if missing.
    """
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with locked_file(path):
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
    return True


def read_json_lines(path):
    """Read a JSON-lines file. Blank lines are skipped; a corrupt line is
    skipped too (it is logged in the returned record as a skipped line
    count, never raised — a log reader must not crash on one bad line)."""
    records = []
    skipped = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    skipped += 1
    except FileNotFoundError:
        return [], 0
    return records, skipped


if __name__ == "__main__":
    # Self-test — TEMP files only, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_json = os.path.join(tmp_dir, "test.json")
    tmp_log = os.path.join(tmp_dir, "test.log")

    assert read_json(tmp_json, default={"x": 1}) == {"x": 1}
    write_json_atomic(tmp_json, {"schema": "t", "records": [1, 2]})
    assert read_json(tmp_json) == {"schema": "t", "records": [1, 2]}

    def _add(records):
        data = records if isinstance(records, dict) else {"records": []}
        data["records"].append(3)
        return data

    out = update_json(tmp_json, _add, default={"records": []})
    assert out["records"] == [1, 2, 3], out
    assert read_json(tmp_json)["records"] == [1, 2, 3]

    # Two sequential locked updates do not lose each other's record.
    update_json(tmp_json, lambda d: {**d, "records": d["records"] + [4]})
    update_json(tmp_json, lambda d: {**d, "records": d["records"] + [5]})
    assert read_json(tmp_json)["records"] == [1, 2, 3, 4, 5]

    # Corrupt JSON raises (never silently treated as empty).
    with open(tmp_json, "w", encoding="utf-8") as f:
        f.write("{not json")
    try:
        read_json(tmp_json)
        raise SystemExit("FAIL: corrupt JSON did not raise")
    except json.JSONDecodeError:
        pass

    append_json_line(tmp_log, {"event": "a", "n": 1})
    append_json_line(tmp_log, {"event": "b", "n": 2})
    recs, skipped = read_json_lines(tmp_log)
    assert len(recs) == 2 and skipped == 0, (recs, skipped)
    assert recs[0]["event"] == "a" and recs[1]["n"] == 2
    assert read_json_lines(os.path.join(tmp_dir, "missing.log")) == ([], 0)

    print("store_io: OK (atomic write, locked update, corrupt-JSON raises, "
          "JSON-lines append/read)")
