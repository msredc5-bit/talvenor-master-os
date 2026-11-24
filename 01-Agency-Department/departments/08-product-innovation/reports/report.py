"""Department report compiler — 08-product-innovation (Phase 5).

Read-only. Stdlib only. Never writes any store file, never touches
the network, never raises on empty or missing data: a missing store
file means an empty list.

``compile_report(store_dir=None, tasks=None, runs=None)`` returns::

    {"department": "08-product-innovation",
     "generated_at": "<iso utc>",
     "task_counts": {"total": n, "by_status": {...}},
     "pending_approvals": n,
     "recent": [up to 5 recent task titles],
     "markdown": "<short markdown report text>"}

When ``tasks`` / ``runs`` lists are given they are used as-is; otherwise
``store/tasks.json`` and ``store/agent_runs.json`` are read from
``store_dir`` (default: the repo ``store/`` next to this department
tree, read-only). A store file may hold either a plain list or a dict
with a ``"records"`` list (the tasks-v1 shape). ``pending_approvals``
counts records whose status is ``"pending-approval"`` across both
lists. Importable standalone under ``python3 -I``.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

__all__ = ["compile_report", "DEPARTMENT"]

DEPARTMENT = "08-product-innovation"

_DEFAULT_STORE_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "store"))


def _as_list(data):
    """Accept a plain list or a {"records": [...]} dict; else []."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        records = data.get("records")
        if isinstance(records, list):
            return records
    return []


def _load_list(store_dir, filename):
    """Read one store file read-only; missing/unreadable -> []."""
    try:
        path = os.path.join(store_dir, filename)
        with open(path, "r", encoding="utf-8") as handle:
            return _as_list(json.load(handle))
    except Exception:
        return []


def _title(record):
    if not isinstance(record, dict):
        return str(record)
    title = record.get("title") or record.get("name") or record.get("id")
    return str(title) if title else "untitled"


def _status(record):
    if isinstance(record, dict):
        return str(record.get("status") or "unknown")
    return "unknown"


def compile_report(store_dir=None, tasks=None, runs=None):
    """Compile a read-only department report dict. Never raises on
    empty or missing data; never writes a file."""
    if tasks is None:
        base = store_dir or _DEFAULT_STORE_DIR
        tasks = _load_list(base, "tasks.json")
    else:
        tasks = _as_list(tasks)
    if runs is None:
        base = store_dir or _DEFAULT_STORE_DIR
        runs = _load_list(base, "agent_runs.json")
    else:
        runs = _as_list(runs)

    by_status = {}
    for record in tasks:
        status = _status(record)
        by_status[status] = by_status.get(status, 0) + 1
    pending = sum(
        1 for record in list(tasks) + list(runs)
        if _status(record) == "pending-approval"
    )
    recent = [_title(record) for record in tasks[-5:]][::-1]

    lines = [
        "# %s report" % DEPARTMENT,
        "",
        "- Tasks total: %d" % len(tasks),
        "- Pending approvals: %d" % pending,
    ]
    for status in sorted(by_status):
        lines.append("- %s: %d" % (status, by_status[status]))
    if recent:
        lines.append("")
        lines.append("Recent tasks:")
        for title in recent:
            lines.append("- %s" % title)
    else:
        lines.append("")
        lines.append("No tasks recorded.")

    return {
        "department": DEPARTMENT,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task_counts": {"total": len(tasks), "by_status": by_status},
        "pending_approvals": pending,
        "recent": recent,
        "markdown": "\n".join(lines) + "\n",
    }


if __name__ == "__main__":
    print(compile_report()["markdown"])
