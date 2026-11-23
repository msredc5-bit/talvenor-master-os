"""Structured audit log — append-only JSON lines (Phase 1, Unified OS).

One record per line in store/audit.log:
  {"ts": "<iso utc>", "event": "<name>", ...details}

Events written today:
  - "gate_decision"    — a gated tool call's outcome (blocked-trust /
                         pending-approval) and a Chief's gated hold.
  - "permission_denied" — an agent asked for a tool it is not allowed.
  - "task_transition"  — a queued task moved to done / failed / cancelled /
                         duplicate / blocked in the drain.
  - "task_queued"      — the taskboard accepted a new queued task.
  - "task_cancelled"   — the taskboard cancelled a queued task.

Rules:
  - Append-only. Records are never edited or deleted (history stays).
  - A failed audit write never breaks the caller — audit_log() catches
    everything and returns False; the caller's work still stands.
  - The log is a record, not permission — nothing in here authorizes an
    action. Approval lives only in trust_gate + ApprovalGateway.

Stdlib only. No network, no send, no publish, no spend.
"""

import os
from datetime import datetime, timezone

try:
    from store_io import append_json_line, read_json_lines
except ImportError:  # direct script run from another directory
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from store_io import append_json_line, read_json_lines  # noqa: E402

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_AUDIT_PATH = os.path.join(_STORE_DIR, "audit.log")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def audit_log(event, details=None, store_dir=None, audit_path=None):
    """Append one audit record. Returns True on success, False on failure
    (a failure never raises — the caller's work must not break because
    the log could not be written)."""
    path = audit_path
    if path is None:
        base = store_dir or _STORE_DIR
        path = os.path.join(base, "audit.log")
    record = {"ts": _now_iso(), "event": event}
    if details:
        record.update(details)
    try:
        append_json_line(path, record)
        return True
    except Exception:  # noqa: BLE001 — the log must never crash the caller
        return False


def read_audit(audit_path=None, store_dir=None):
    """All audit records (oldest first) + count of skipped corrupt lines."""
    path = audit_path
    if path is None:
        base = store_dir or _STORE_DIR
        path = os.path.join(base, "audit.log")
    return read_json_lines(path)


if __name__ == "__main__":
    # Self-test — TEMP files only, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_log = os.path.join(tmp_dir, "audit.log")

    assert audit_log("gate_decision",
                     {"tool": "gmail_send", "status": "pending-approval"},
                     audit_path=tmp_log) is True
    assert audit_log("task_transition",
                     {"task_id": "abc", "to": "done"},
                     audit_path=tmp_log) is True
    recs, skipped = read_audit(audit_path=tmp_log)
    assert len(recs) == 2 and skipped == 0, (recs, skipped)
    assert recs[0]["event"] == "gate_decision"
    assert recs[1]["to"] == "done"
    assert all("ts" in r for r in recs)

    # A bad path fails soft (False, no raise) — parent is a file, not a dir.
    blocker = os.path.join(tmp_dir, "blocker")
    with open(blocker, "w", encoding="utf-8") as f:
        f.write("x")
    assert audit_log("x", {},
                     audit_path=os.path.join(blocker, "audit.log")) is False

    print("audit: OK (append-only JSON lines, soft failure)")
