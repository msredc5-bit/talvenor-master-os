"""02-marketing department report compiler — Talvenor Master OS,
local-first Phase 5.

Read-only, stdlib only. Never writes any file and never changes any
store file. ``compile_report`` builds a small summary dict from task
and run records.

When ``tasks`` / ``runs`` arguments are given (lists of dicts), they
are used as-is. Otherwise the records are read from
``store/tasks.json`` and ``store/agent_runs.json`` under ``store_dir``
(default: the repo ``store/`` directory, resolved from this file).
A missing file, an unreadable file, or a bad shape means an empty
list — never an exception.

Return shape::

  {"department": "02-marketing",
   "generated_at": "<ISO-8601 UTC timestamp>",
   "task_counts": {"total": n, "by_status": {...}},
   "pending_approvals": n,
   "recent": [up to 5 recent task titles, most recent first],
   "markdown": "<short markdown report text>"}

``pending_approvals`` counts task and run records whose status is
exactly ``"pending-approval"``.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone

__all__ = ["compile_report", "DEPARTMENT"]

DEPARTMENT = "02-marketing"


def _default_store_dir():
    """Repo ``store/`` resolved from this file's location."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(
        os.path.join(here, "..", "..", "..", "..", "store"))


def _load_records(store_dir, filename):
    """Read one store file as a list of record dicts.

    Accepts a bare list or a ``{"records": [...]}`` mapping. A
    missing file, an unreadable file, or any other shape returns
    ``[]`` — never raises.
    """
    if not store_dir:
        return []
    path = os.path.join(str(store_dir), filename)
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return []
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        records = data.get("records")
        if isinstance(records, list):
            return [r for r in records if isinstance(r, dict)]
    return []


def _title(record):
    """Best display title for one record dict."""
    value = record.get("title") or record.get("name") or record.get("id")
    return str(value) if value else "untitled task"


def compile_report(store_dir=None, tasks=None, runs=None):
    """Compile the department report. Read-only; never raises on
    empty or missing data."""
    if tasks is None:
        tasks = _load_records(
            store_dir if store_dir is not None else _default_store_dir(),
            "tasks.json")
    if runs is None:
        runs = _load_records(
            store_dir if store_dir is not None else _default_store_dir(),
            "agent_runs.json")
    if not isinstance(tasks, list):
        tasks = []
    if not isinstance(runs, list):
        runs = []
    tasks = [t for t in tasks if isinstance(t, dict)]
    runs = [r for r in runs if isinstance(r, dict)]

    by_status = dict(Counter(
        str(t.get("status") or "unknown") for t in tasks))
    pending = sum(
        1 for r in tasks + runs
        if str(r.get("status") or "") == "pending-approval")
    recent = [_title(t) for t in tasks[-5:]][::-1]

    generated_at = datetime.now(timezone.utc).isoformat()
    lines = ["# %s report" % DEPARTMENT,
             "",
             "- Generated (UTC): %s" % generated_at,
             "- Tasks: %d total" % len(tasks),
             "- By status: %s" % (by_status or "none"),
             "- Pending approvals: %d" % pending,
             "- Recent tasks:"]
    if recent:
        lines.extend("  - %s" % title for title in recent)
    else:
        lines.append("  - none")
    markdown = "\n".join(lines) + "\n"

    return {
        "department": DEPARTMENT,
        "generated_at": generated_at,
        "task_counts": {"total": len(tasks), "by_status": by_status},
        "pending_approvals": pending,
        "recent": recent,
        "markdown": markdown,
    }
