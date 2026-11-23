"""Goal store + executive summary (Phase 1, Unified OS).

Goals are the Founder's stated goals — never invented. The seed below is
Boss's own words (2026-11-06: first client, then 2, then 3; 2026-11-12:
three tracks together — receptionist agency MAIN, digital product,
own YouTube channel). A goal's progress is always computed from real
store/config files at summary time — never stored as a stale number.

Store: store/goals.json — {"schema": "goals-v1", "goals": [...]}.
A goal: {"id", "title", "track", "target", "metric", "status",
"created_at", "notes"}. Status: active | done | paused.
Metric names and where they are read from (executive_summary):
  - "paying_clients"  -> 00-CEO-Core/config.json honest_status
  - "first_mails_sent" -> 00-CEO-Core/config.json honest_status
  - "email_outreach"  -> 00-CEO-Core/config.json honest_status (text)
  - "gate0"           -> 02-Digital-Product-Department/gate0-status.md
                         (the "Status:" line, fail-closed parse)
  - anything else     -> progress "unknown" (no store metric — honest,
                         never guessed).

executive_summary(store_dir) reads ONLY real files: tasks.json (counts
by status), usage_ledger.json (call count + total cost), approvals.json
(counts by status), config.json honest_status, gate0-status.md, and
goals.json. It contains no hardcoded business numbers — a missing file
reports "unknown", not 0 dressed up as a fact.

Stdlib only. No network, no send, no publish, no spend.
"""

import json
import os
import re
from datetime import datetime, timezone

try:
    from store_io import read_json, update_json, write_json_atomic
except ImportError:  # direct script run from another directory
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from store_io import read_json, update_json, write_json_atomic  # noqa: E402

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_GOALS_PATH = os.path.join(_STORE_DIR, "goals.json")
CONFIG_PATH = os.path.join(_MASTER_OS_DIR, "00-CEO-Core", "config.json")
GATE0_PATH = os.path.join(
    _MASTER_OS_DIR, "02-Digital-Product-Department", "gate0-status.md")

GOAL_STATUSES = ("active", "done", "paused")
SCHEMA = "goals-v1"

# Boss's stated goals (2026-11-06 + 2026-11-12). Seeded once, only into
# an empty goals file — never overwritten, never invented.
SEED_GOALS = [
    {
        "id": "first-paying-client",
        "title": "First paying client for the AI receptionist agency",
        "track": "agency",
        "target": "1 paying client, then 2, then 3",
        "metric": "paying_clients",
        "status": "active",
        "notes": "Boss 2026-11-06: receptionist stays MAIN, high-ticket; "
                 "target 1 -> 2 -> 3 clients, then slowly 20-30.",
    },
    {
        "id": "track-1-agency",
        "title": "Track 1: Talvenor AI receptionist agency (MAIN)",
        "track": "agency",
        "target": "Paying clients via email + Instagram outreach",
        "metric": "first_mails_sent",
        "status": "active",
        "notes": "Boss 2026-11-12: three tracks together; agency is MAIN. "
                 "Email PAUSED since 2026-11-14 (DNS fix pending).",
    },
    {
        "id": "track-2-digital-product",
        "title": "Track 2: Winning digital product under Talvenor",
        "track": "digital-product",
        "target": "Vet No-Show Recovery Kit, $49 one-time — Gate 0 first",
        "metric": "gate0",
        "status": "active",
        "notes": "Boss 2026-11-12: Vet No-Show Recovery Kit is the current "
                 "winner (84/100). Gate 0 = Lemon Squeezy signup test, "
                 "NOT PASSED yet.",
    },
    {
        "id": "track-3-content",
        "title": "Track 3: Own YouTube content channel",
        "track": "content",
        "target": "ToolPilot channel — first videos recorded",
        "metric": "toolpilot_videos",
        "status": "active",
        "notes": "Boss 2026-11-12: track 3 = own YouTube channel. ToolPilot "
                 "exists (@ToolPilotai69), 0 videos yet. Whether track 3 "
                 "is ToolPilot or a brand-new channel is still unanswered.",
    },
]


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def goals_path(store_dir=None):
    return os.path.join(store_dir or _STORE_DIR, "goals.json")


def load_goals(store_dir=None):
    """All goals (empty list when the file is missing)."""
    data = read_json(goals_path(store_dir), default=None)
    if not isinstance(data, dict):
        return []
    goals = data.get("goals", [])
    return [dict(g) for g in goals] if isinstance(goals, list) else []


def seed_goals(store_dir=None):
    """Write the seed goals into an EMPTY goals file only. Returns the
    goals. An existing non-empty file is never touched."""
    path = goals_path(store_dir)
    existing = load_goals(store_dir)
    if existing:
        return existing
    seeded = []
    for goal in SEED_GOALS:
        seeded.append({**goal, "created_at": _now_iso()})
    write_json_atomic(path, {"schema": SCHEMA, "goals": seeded})
    return seeded


def set_goal_status(goal_id, status, store_dir=None):
    """Change one goal's status (active/done/paused). KeyError when the
    goal does not exist; ValueError for an unknown status."""
    if status not in GOAL_STATUSES:
        raise ValueError(f"Unknown goal status {status!r}. "
                         f"Allowed: {list(GOAL_STATUSES)}")

    def _apply(data):
        goals = (data or {}).get("goals", []) if isinstance(data, dict) else []
        for goal in goals:
            if goal.get("id") == goal_id:
                goal["status"] = status
                goal["updated_at"] = _now_iso()
                return {"schema": SCHEMA, "goals": goals}
        raise KeyError(f"No goal {goal_id!r}.")

    update_json(goals_path(store_dir), _apply,
                default={"schema": SCHEMA, "goals": []})
    return [g for g in load_goals(store_dir) if g.get("id") == goal_id][0]


def _read_gate0():
    """Gate 0 status from the products Status line (fail-closed parse —
    the same rule as scripts/sync_engines.py). "unknown" when unreadable."""
    try:
        with open(GATE0_PATH, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return "unknown"
    for line in text.splitlines():
        m = re.match(r"^\**\s*Status:\s*(.+?)\**\s*$", line.strip())
        if m:
            return m.group(1).strip()
    return "unknown"


def _metric_value(metric, honest_status):
    """One goal metric, read from a real file. ("unknown", reason) when
    there is no store source for the metric — never guessed."""
    if metric in ("paying_clients", "first_mails_sent", "email_outreach"):
        value = (honest_status or {}).get(metric, "unknown")
        return value, "config.json honest_status"
    if metric == "gate0":
        return _read_gate0(), "gate0-status.md Status line"
    return "unknown", "no store metric for this goal"


def _count_by_status(records):
    counts = {}
    for record in records or []:
        status = record.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def executive_summary(store_dir=None):
    """The executive summary — every number read from real files.

    Returns a dict: generated_at, tasks (counts by status + total),
    ledger (total calls + total cost + cap), approvals (counts by
    status), honest_status (first_mails_sent, paying_clients,
    email_outreach — "unknown" when missing), goals (each with a
    progress value read from its metric source, or "unknown").
    """
    base = store_dir or _STORE_DIR
    tasks = read_json(os.path.join(base, "tasks.json"), default=None)
    task_records = (tasks or {}).get("records", []) \
        if isinstance(tasks, dict) else []
    ledger = read_json(os.path.join(base, "usage_ledger.json"),
                       default=None)
    ledger_records = (ledger or {}).get("records", []) \
        if isinstance(ledger, dict) else []
    approvals = read_json(os.path.join(base, "approvals.json"),
                          default=None)
    approval_records = (approvals or {}).get("records", []) \
        if isinstance(approvals, dict) else []
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, json.JSONDecodeError):
        config = {}
    honest = config.get("honest_status", {}) if isinstance(config, dict) else {}

    goals = []
    for goal in load_goals(base):
        value, source = _metric_value(goal.get("metric"), honest)
        goals.append({**goal, "progress": value, "progress_source": source})

    return {
        "generated_at": _now_iso(),
        "tasks": {
            "total": len(task_records),
            "by_status": _count_by_status(task_records),
        },
        "ledger": {
            "total_calls": len(ledger_records),
            "total_usd": round(sum(
                float(r.get("cost_usd", 0) or 0) for r in ledger_records), 6),
            "monthly_cap_usd": (ledger or {}).get("monthly_cap_usd", "unknown")
            if isinstance(ledger, dict) else "unknown",
        },
        "approvals": {
            "total": len(approval_records),
            "by_status": _count_by_status(approval_records),
        },
        "honest_status": {
            "first_mails_sent": honest.get("first_mails_sent", "unknown"),
            "paying_clients": honest.get("paying_clients", "unknown"),
            "email_outreach": honest.get("email_outreach", "unknown"),
        },
        "goals": goals,
    }


if __name__ == "__main__":
    # Manual check + CLI: seed if empty, print the summary as JSON.
    # Seeding writes store/goals.json (the goal store's own file).
    import argparse

    parser = argparse.ArgumentParser(
        description="Goal store + executive summary (reads real store state).")
    parser.add_argument("--store-dir", default=_STORE_DIR)
    parser.add_argument("--seed", action="store_true",
                        help="seed the goals file when it is empty")
    args = parser.parse_args()
    if args.seed:
        seeded = seed_goals(args.store_dir)
        print(f"goals: {len(seeded)} goal(s) in {goals_path(args.store_dir)}")
    print(json.dumps(executive_summary(args.store_dir), indent=2,
                     ensure_ascii=False))
