"""CEO reporting generator — daily / weekly / monthly Founder reports.

Reads only the real store files under ``store_dir`` (default: the repo
``store/``) plus the repo config and the Gate 0 status line. Every
number in the report cites its source file; a missing or unreadable
source is "unknown", never an invented number and never a silent 0
(unless the file exists and is genuinely empty).

Stdlib only. Read-only on the store: this module writes nothing.
Callers (scripts/generate_ceo_report.py) write the Markdown + JSON
twins to reports/ceo/.

Periods (rolling windows, see PERIODS):
  - "daily":   last 24 hours
  - "weekly":  last 7 days
  - "monthly": last 30 days — a 30-day window, NOT a calendar month.

Prospect PII is never read: no prospect list file is opened by this
module, and no client name appears in any report.
"""

import json
import os
from collections import Counter
from datetime import datetime, timedelta, timezone

GENERATOR_VERSION = "ceo-reporting-1.0.0"

# period -> (window days, window label)
PERIODS = {
    "daily": (1, "last 24 hours"),
    "weekly": (7, "last 7 days"),
    "monthly": (30, "last 30 days (30-day window, not a calendar month)"),
}

UNKNOWN = "unknown"

# Timestamp fields tried, in order, to place a record in the window.
_TS_FIELDS = ("queued_at", "completed_at", "at", "created_at",
              "requested_at", "decided_at", "updated_at", "learned_at")

_DEPARTMENT_DIRS = (
    "01-sales-growth", "02-marketing", "03-ai-engineering",
    "04-client-operations", "05-research-strategy", "06-finance-admin",
    "07-quality-security", "08-product-innovation",
)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value):
    """Parse an ISO-8601 timestamp to an aware datetime, else None."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _record_time(record):
    """First parseable timestamp found on a record, else None."""
    if not isinstance(record, dict):
        return None
    for field in _TS_FIELDS:
        parsed = _parse_iso(record.get(field))
        if parsed is not None:
            return parsed
    return None


def _read_json_file(path):
    """Read a JSON file.

    Returns (data, status) where status is "ok", "missing", "corrupt"
    or "wrong-shape". Missing is not an error — the caller reports
    "unknown" for that source.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f), "ok"
    except FileNotFoundError:
        return None, "missing"
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, "corrupt"
    except OSError:
        return None, "missing"


def _read_text_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), "ok"
    except OSError:
        return None, "missing"


def _records(data):
    """Record list from a store payload (dict with "records" or bare list)."""
    if isinstance(data, dict):
        recs = data.get("records")
        return recs if isinstance(recs, list) else []
    if isinstance(data, list):
        return data
    return []


def _fmt_age(delta):
    """Human age for a timedelta, e.g. '3d 4h' / '5h' / '20m'."""
    if delta is None:
        return UNKNOWN
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "0m"
    days, rem = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    if days:
        return "%dd %dh" % (days, hours)
    if hours:
        return "%dh %dm" % (hours, minutes)
    return "%dm" % minutes


def _fmt_usd(value):
    if isinstance(value, (int, float)):
        return "$%.2f" % float(value)
    return UNKNOWN


def _fmt_dt(dt):
    return dt.isoformat() if dt is not None else UNKNOWN


def _window_counts(records, start, end):
    """(in_window, undated) for records placed by their timestamp."""
    in_window = 0
    undated = 0
    for rec in records:
        ts = _record_time(rec)
        if ts is None:
            undated += 1
        elif start <= ts <= end:
            in_window += 1
    return in_window, undated


def _count_by(records, field):
    counts = Counter()
    for rec in records:
        if isinstance(rec, dict):
            counts[str(rec.get(field, UNKNOWN))] += 1
    return dict(sorted(counts.items()))


def _collect_tasks(store_dir, start, end):
    path = os.path.join(store_dir, "tasks.json")
    data, status = _read_json_file(path)
    source = "store/tasks.json"
    if status != "ok":
        return {
            "source": source, "status": status, "total": UNKNOWN,
            "in_window": UNKNOWN, "undated": UNKNOWN,
            "by_status": UNKNOWN, "by_type": UNKNOWN,
            "by_business": UNKNOWN, "executions": UNKNOWN,
            "executions_cost_usd": UNKNOWN,
        }
    records = _records(data)
    in_window, undated = _window_counts(records, start, end)
    executions = 0
    exec_cost = 0.0
    for rec in records:
        ex_list = rec.get("executions") if isinstance(rec, dict) else None
        if isinstance(ex_list, list):
            executions += len(ex_list)
            for ex in ex_list:
                if isinstance(ex, dict):
                    try:
                        exec_cost += float(ex.get("cost_usd") or 0.0)
                    except (TypeError, ValueError):
                        pass
    return {
        "source": source, "status": "ok", "total": len(records),
        "in_window": in_window, "undated": undated,
        "by_status": _count_by(records, "status"),
        "by_type": _count_by(records, "type"),
        "by_business": _count_by(records, "business"),
        "executions": executions,
        "executions_cost_usd": round(exec_cost, 6),
    }


def _collect_approvals(store_dir, start, end):
    path = os.path.join(store_dir, "approvals.json")
    data, status = _read_json_file(path)
    source = "store/approvals.json"
    if status != "ok":
        return {
            "source": source, "status": status, "total": UNKNOWN,
            "by_status": UNKNOWN, "pending": UNKNOWN,
            "pending_list": UNKNOWN, "oldest_pending_age": UNKNOWN,
            "decided_in_window": UNKNOWN,
        }
    records = _records(data)
    by_status = _count_by(records, "status")
    pending = [r for r in records
               if isinstance(r, dict) and r.get("status") == "pending"]
    pending_list = []
    oldest_age = None
    for rec in sorted(pending,
                      key=lambda r: _record_time(r) or datetime.min.replace(
                          tzinfo=timezone.utc)):
        ts = _record_time(rec)
        age = _fmt_age(end - ts) if ts is not None else UNKNOWN
        if ts is not None and (oldest_age is None or ts < oldest_age):
            oldest_age = ts
        pending_list.append({
            "id": rec.get("id", UNKNOWN),
            "action": rec.get("action", rec.get("scope", rec.get("type", UNKNOWN))),
            "detail": rec.get("detail", rec.get("note", rec.get("summary", ""))),
            "requested_at": _fmt_dt(ts),
            "age": age,
        })
    decided_in_window = sum(
        1 for r in records
        if isinstance(r, dict) and r.get("status") in ("approved", "rejected")
        and _record_time(r) is not None
        and start <= _record_time(r) <= end)
    return {
        "source": source, "status": "ok", "total": len(records),
        "by_status": by_status, "pending": len(pending),
        "pending_list": pending_list,
        "oldest_pending_age": (_fmt_age(end - oldest_age)
                               if oldest_age is not None else None),
        "decided_in_window": decided_in_window,
    }


def _collect_usage(store_dir, start, end):
    path = os.path.join(store_dir, "usage_ledger.json")
    data, status = _read_json_file(path)
    source = "store/usage_ledger.json"
    if status != "ok":
        return {
            "source": source, "status": status, "total_calls": UNKNOWN,
            "total_usd": UNKNOWN, "in_window_calls": UNKNOWN,
            "in_window_usd": UNKNOWN, "by_kind": UNKNOWN,
            "monthly_total_usd": UNKNOWN, "monthly_cap_usd": UNKNOWN,
            "over_monthly_cap": UNKNOWN,
        }
    records = _records(data)
    in_window, _undated = _window_counts(records, start, end)
    month = end.strftime("%Y-%m")
    total_usd = 0.0
    in_window_usd = 0.0
    monthly_usd = 0.0
    by_kind = Counter()
    for rec in records:
        if not isinstance(rec, dict):
            continue
        try:
            cost = float(rec.get("cost_usd") or 0.0)
        except (TypeError, ValueError):
            cost = 0.0
        total_usd += cost
        by_kind[str(rec.get("kind", UNKNOWN))] += 1
        ts = _record_time(rec)
        if ts is not None:
            if start <= ts <= end:
                in_window_usd += cost
            if ts.strftime("%Y-%m") == month:
                monthly_usd += cost
    cap = data.get("monthly_cap_usd") if isinstance(data, dict) else None
    if not isinstance(cap, (int, float)):
        cap = UNKNOWN
    over_cap = (isinstance(cap, (int, float))
                and round(monthly_usd, 6) > float(cap))
    return {
        "source": source, "status": "ok", "total_calls": len(records),
        "total_usd": round(total_usd, 6),
        "in_window_calls": in_window,
        "in_window_usd": round(in_window_usd, 6),
        "by_kind": dict(sorted(by_kind.items())),
        "monthly_total_usd": round(monthly_usd, 6),
        "monthly_cap_usd": cap,
        "over_monthly_cap": over_cap,
    }


def _collect_memory(store_dir):
    path = os.path.join(store_dir, "memory.json")
    data, status = _read_json_file(path)
    source = "store/memory.json"
    if status != "ok":
        return {"source": source, "status": status,
                "entries": UNKNOWN, "boxes": UNKNOWN}
    entries = data.get("entries") if isinstance(data, dict) else None
    boxes = data.get("boxes") if isinstance(data, dict) else None
    return {
        "source": source, "status": "ok",
        "entries": len(entries) if isinstance(entries, list) else UNKNOWN,
        "boxes": len(boxes) if isinstance(boxes, list) else UNKNOWN,
    }


def _collect_lead_chain(store_dir):
    """Lead-chain runs from store/chains/ (Phase 6).

    A missing chains/ directory means no chain runs have been recorded
    — reported as 0 runs with the source noted, never an error.
    """
    chains_dir = os.path.join(store_dir, "chains")
    source = "store/chains/"
    if not os.path.isdir(chains_dir):
        return {"source": source, "status": "missing",
                "total_runs": 0, "by_status": {},
                "log_lines": UNKNOWN,
                "note": "store/chains/ absent — no lead-chain runs recorded."}
    by_status = Counter()
    total = 0
    corrupt = 0
    try:
        names = sorted(os.listdir(chains_dir))
    except OSError:
        return {"source": source, "status": "missing",
                "total_runs": 0, "by_status": {},
                "log_lines": UNKNOWN,
                "note": "store/chains/ unreadable."}
    for name in names:
        if not name.endswith(".json"):
            continue
        data, status = _read_json_file(os.path.join(chains_dir, name))
        if status != "ok" or not isinstance(data, dict):
            corrupt += 1
            continue
        total += 1
        by_status[str(data.get("status", UNKNOWN))] += 1
    log_lines = UNKNOWN
    log_path = os.path.join(chains_dir, "chain_log.jsonl")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            log_lines = sum(1 for line in f if line.strip())
    except OSError:
        log_lines = UNKNOWN
    result = {"source": source, "status": "ok", "total_runs": total,
              "by_status": dict(sorted(by_status.items())),
              "log_lines": log_lines,
              "note": "Deployment is always BLOCKED in the lead chain "
                      "(sandbox only)."}
    if corrupt:
        result["corrupt_files"] = corrupt
    return result


def _collect_departments(store_dir, repo_root, task_records):
    """One row per department via department_runtime.compile_department_report().

    Read-only; any failure leaves that department "unknown", never an
    exception. The department report modules read the store themselves
    when no tasks are passed; here the task records are passed through.
    """
    source = "01-Agency-Department/departments/department_runtime.py"
    rows = []
    runtime_path = os.path.join(
        repo_root, "01-Agency-Department", "departments",
        "department_runtime.py")
    compile_fn = None
    load_error = None
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ceo_reporting_department_runtime", runtime_path)
        if spec is None or spec.loader is None:
            raise ImportError("could not load department_runtime.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        compile_fn = getattr(mod, "compile_department_report", None)
        if not callable(compile_fn):
            raise AttributeError("no compile_department_report()")
    except Exception as exc:  # noqa: BLE001 — one bad import must not kill the report
        load_error = "%s: %s" % (type(exc).__name__, exc)
    for dept in _DEPARTMENT_DIRS:
        if load_error is not None:
            rows.append({"department": dept, "status": UNKNOWN,
                         "error": load_error})
            continue
        try:
            result = compile_fn(dept, store_dir=store_dir,
                                tasks=task_records, runs=[])
        except Exception as exc:  # noqa: BLE001 — per-department failure is "unknown"
            rows.append({"department": dept, "status": UNKNOWN,
                         "error": "%s: %s" % (type(exc).__name__, exc)})
            continue
        if not isinstance(result, dict):
            rows.append({"department": dept, "status": UNKNOWN,
                         "error": "TypeError: compile_department_report() "
                                  "returned %s" % type(result).__name__})
            continue
        if "error" in result:
            rows.append({"department": dept, "status": UNKNOWN,
                         "error": str(result["error"])[:200]})
            continue
        counts = result.get("task_counts") or {}
        by_status = counts.get("by_status") or {}
        rows.append({
            "department": dept, "status": "ok",
            "tasks_total": counts.get("total", UNKNOWN),
            "tasks_by_status": by_status if isinstance(by_status, dict) else UNKNOWN,
            "pending_approvals": result.get("pending_approvals", UNKNOWN),
        })
    return {"source": source, "departments": rows}


def _collect_schedules(store_dir):
    path = os.path.join(store_dir, "schedules.json")
    data, status = _read_json_file(path)
    source = "store/schedules.json"
    if status != "ok":
        return {"source": source, "status": status, "total": UNKNOWN,
                "by_status": UNKNOWN, "weekly_ceo_report": UNKNOWN}
    records = _records(data)
    weekly = None
    for rec in records:
        if not isinstance(rec, dict):
            continue
        if rec.get("id") in ("weekly-ceo-report",) or "ceo-report" in str(
                rec.get("id", "")) or "ceo-report" in str(rec.get("name", "")):
            weekly = {"id": rec.get("id", UNKNOWN),
                      "status": rec.get("status", UNKNOWN),
                      "last_run_at": rec.get("last_run_at", UNKNOWN)}
            break
    if weekly is None:
        weekly = {"id": "weekly-ceo-report", "status": "not present in store",
                  "note": "Defined (paused) in workflow_engine/scheduler.py; "
                          "never activated in the real store. This generator "
                          "does not activate any job."}
    return {"source": source, "status": "ok", "total": len(records),
            "by_status": _count_by(records, "status"),
            "weekly_ceo_report": weekly}


def _collect_config(repo_root):
    path = os.path.join(repo_root, "00-CEO-Core", "config.json")
    data, status = _read_json_file(path)
    source = "00-CEO-Core/config.json"
    if status != "ok" or not isinstance(data, dict):
        return {"source": source, "status": status,
                "phase": UNKNOWN, "version": UNKNOWN,
                "spend_cap_usd": UNKNOWN, "email": UNKNOWN,
                "first_mails_sent": UNKNOWN, "paying_clients": UNKNOWN,
                "gates_enabled": UNKNOWN,
                "production_brain_unlocked": UNKNOWN}
    honest = data.get("honest_status") or {}
    gates = data.get("gates") or {}
    prod = data.get("production_brain") or {}
    return {
        "source": source, "status": "ok",
        "phase": data.get("phase", UNKNOWN),
        "version": data.get("version", UNKNOWN),
        "spend_cap_usd": data.get("spend_cap_usd", UNKNOWN),
        "email": honest.get("email_outreach", UNKNOWN),
        "first_mails_sent": honest.get("first_mails_sent", UNKNOWN),
        "paying_clients": honest.get("paying_clients", UNKNOWN),
        "gates_enabled": gates.get("enabled", UNKNOWN),
        "production_brain_unlocked": prod.get("unlocked", UNKNOWN),
    }


def _collect_gate0(repo_root):
    path = os.path.join(repo_root, "02-Digital-Product-Department",
                        "gate0-status.md")
    text, status = _read_text_file(path)
    source = "02-Digital-Product-Department/gate0-status.md"
    if status != "ok":
        return {"source": source, "status": status, "gate0": UNKNOWN}
    for line in text.splitlines():
        if line.strip().startswith("**Status:"):
            if "NOT PASSED" in line:
                return {"source": source, "status": "ok",
                        "gate0": "NOT PASSED"}
            if "PASSED" in line:
                return {"source": source, "status": "ok",
                        "gate0": "PASSED"}
            return {"source": source, "status": "ok", "gate0": UNKNOWN}
    return {"source": source, "status": "ok", "gate0": UNKNOWN}


def _fmt_window(dt):
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _dhaka(dt):
    """UTC datetime rendered in Asia/Dhaka (UTC+6, no DST)."""
    from datetime import timezone as _tz
    dhaka = dt.astimezone(_tz(timedelta(hours=6)))
    return dhaka.strftime("%Y-%m-%d %H:%M Dhaka")


def generate_report(store_dir, period, end=None):
    """Build the CEO report dict for ``period`` over the window ending
    at ``end`` (aware datetime, default now UTC).

    Returns a JSON-serialisable dict; render_markdown() makes the
    Markdown twin with the same numbers.
    """
    if period not in PERIODS:
        raise ValueError("Unknown period %r. Allowed: %s"
                         % (period, sorted(PERIODS)))
    days, window_label = PERIODS[period]
    end_dt = end if end is not None else datetime.now(timezone.utc)
    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    start_dt = end_dt - timedelta(days=days)
    store_dir = os.path.abspath(str(store_dir))
    repo_root = os.path.dirname(store_dir)

    tasks = _collect_tasks(store_dir, start_dt, end_dt)
    approvals = _collect_approvals(store_dir, start_dt, end_dt)
    usage = _collect_usage(store_dir, start_dt, end_dt)
    memory = _collect_memory(store_dir)
    chain = _collect_lead_chain(store_dir)
    # Task records for the department compilers (all records, not just
    # the window — the department reports count by status themselves).
    _tdata, _tstatus = _read_json_file(os.path.join(store_dir, "tasks.json"))
    task_records = _records(_tdata) if _tstatus == "ok" else []
    departments = _collect_departments(store_dir, repo_root, task_records)
    schedules = _collect_schedules(store_dir)
    config = _collect_config(repo_root)
    gate0 = _collect_gate0(repo_root)

    # --- Executive summary: mechanical lines from the numbers only. ---
    summary = []
    if isinstance(tasks.get("total"), int):
        summary.append(
            "%d task(s) in the store (%s in this window); %s done, %s "
            "queued." % (
                tasks["total"], tasks["in_window"],
                tasks["by_status"].get("done", 0),
                tasks["by_status"].get("queued", 0)))
    else:
        summary.append("Task counts unknown — store/tasks.json is %s."
                       % tasks["status"])
    if isinstance(approvals.get("pending"), int):
        if approvals["pending"]:
            summary.append(
                "%d approval(s) pending Boss's gate word%s."
                % (approvals["pending"],
                   ("; oldest pending %s" % approvals["oldest_pending_age"])
                   if approvals.get("oldest_pending_age") else ""))
        else:
            summary.append("No approvals pending.")
    else:
        summary.append("Approval counts unknown — store/approvals.json is %s."
                       % approvals["status"])
    if isinstance(usage.get("total_usd"), (int, float)):
        summary.append(
            "Usage ledger: %d call(s) in total, %s spent (%s cap); %d "
            "call(s) in this window, %s." % (
                usage["total_calls"], _fmt_usd(usage["total_usd"]),
                _fmt_usd(usage.get("monthly_cap_usd")),
                usage["in_window_calls"], _fmt_usd(usage["in_window_usd"])))
    else:
        summary.append("Usage unknown — store/usage_ledger.json is %s."
                       % usage["status"])
    if isinstance(chain.get("total_runs"), int):
        summary.append(
            "Lead chain (sandbox): %d run(s) recorded; deployment always "
            "BLOCKED." % chain["total_runs"])
    if isinstance(config.get("email"), str) and "PAUSED" in config["email"]:
        summary.append("Email outreach is PAUSED — no email goes out.")
    if gate0.get("gate0") == "NOT PASSED":
        summary.append("Gate 0 (Vet Kit) is NOT PASSED — kit launch/sale "
                       "still blocked.")
    if config.get("paying_clients") == 0:
        summary.append("Paying clients: 0.")

    # --- Risks & blocked items: stated facts with sources. ---
    risks = [
        {"item": "Email outreach PAUSED",
         "status": config.get("email", UNKNOWN),
         "source": config["source"]},
        {"item": "Deployment BLOCKED (always — sandbox only)",
         "status": ("BLOCKED" if config.get("production_brain_unlocked")
                    is False else UNKNOWN),
         "source": config["source"]
                   + " (production_brain.unlocked=false)"},
        {"item": "Gate 0 (Vet Kit launch/sale)",
         "status": gate0.get("gate0", UNKNOWN),
         "source": gate0["source"]},
        {"item": "Live brain",
         "status": ("NOT PROVEN LIVE — brain is mock"
                    if config.get("production_brain_unlocked") is False
                    else UNKNOWN),
         "source": config["source"]},
    ]

    # --- Next actions: derived mechanically from the numbers. ---
    next_actions = []
    if isinstance(approvals.get("pending"), int) and approvals["pending"]:
        next_actions.append(
            "%d pending approval(s) await Boss's gate word." % approvals["pending"])
    if isinstance(config.get("email"), str) and "PAUSED" in config["email"]:
        next_actions.append(
            "Email stays PAUSED until Boss applies the SPF/DMARC fix and "
            "says to restart it — nothing to send meanwhile.")
    if gate0.get("gate0") == "NOT PASSED":
        next_actions.append(
            "Gate 0 is Boss's step (Lemon Squeezy signup test, ~15 min) — "
            "no kit work moves until it passes.")
    if isinstance(tasks.get("by_status"), dict) and tasks["by_status"].get("queued"):
        next_actions.append(
            "%d queued task(s) await a run." % tasks["by_status"]["queued"])
    if not next_actions:
        next_actions.append(
            "No action is forced by the numbers alone — the standing "
            "blocked items (email PAUSED, deployment BLOCKED, Gate 0 "
            "NOT PASSED) still stand.")

    report = {
        "generator": GENERATOR_VERSION,
        "generated_at": _now_iso(),
        "period": period,
        "window": {
            "label": window_label,
            "days": days,
            "start_utc": _fmt_window(start_dt),
            "end_utc": _fmt_window(end_dt),
            "start_dhaka": _dhaka(start_dt),
            "end_dhaka": _dhaka(end_dt),
        },
        "store_dir": store_dir,
        "executive_summary": summary,
        "config": config,
        "tasks": tasks,
        "approvals": approvals,
        "lead_chain": chain,
        "departments": departments,
        "usage": usage,
        "memory": memory,
        "schedules": schedules,
        "gate0": gate0,
        "risks_blocked": risks,
        "next_actions": next_actions,
        "notes": [
            "Monthly means the last 30 days (30-day window), not a "
            "calendar month.",
            "Every figure cites its source file; a missing or unreadable "
            "source is shown as 'unknown', never invented.",
            "This report is a draft for Boss to read. It is never sent "
            "or published by the generator.",
        ],
    }
    return report


def _table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def render_markdown(report):
    """Deterministic Markdown twin of generate_report()'s dict — the
    same numbers, same order. Only generated_at varies between runs.
    """
    w = report["window"]
    cfg = report["config"]
    tasks = report["tasks"]
    appr = report["approvals"]
    chain = report["lead_chain"]
    usage = report["usage"]
    sched = report["schedules"]
    lines = []
    lines.append("# CEO Report — %s" % report["period"].capitalize())
    lines.append("")
    lines.append("Generator: %s · Generated: %s"
                 % (report["generator"], report["generated_at"]))
    lines.append("Window: %s — %s to %s (%s to %s)"
                 % (w["label"], w["start_utc"], w["end_utc"],
                    w["start_dhaka"], w["end_dhaka"]))
    lines.append("Store: %s" % report["store_dir"])
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    for line in report["executive_summary"]:
        lines.append("- %s" % line)
    lines.append("")
    lines.append("## Context (source: %s)" % cfg["source"])
    lines.append("")
    lines.append("- Phase: %s · Version: %s" % (cfg["phase"], cfg["version"]))
    lines.append("- Spend cap: %s · Gates enabled: %s"
                 % (_fmt_usd(cfg["spend_cap_usd"]) if isinstance(
                     cfg["spend_cap_usd"], (int, float)) else cfg["spend_cap_usd"],
                     cfg["gates_enabled"]))
    lines.append("- First mails sent: %s · Paying clients: %s"
                 % (cfg["first_mails_sent"], cfg["paying_clients"]))
    lines.append("- Email: %s" % cfg["email"])
    lines.append("")
    lines.append("## Tasks (source: %s — status: %s)"
                 % (tasks["source"], tasks["status"]))
    lines.append("")
    if isinstance(tasks.get("total"), int):
        lines.append("- Total records: %d · In this window: %d · Undated: %d"
                     % (tasks["total"], tasks["in_window"], tasks["undated"]))
        lines.append("- Executions recorded: %d · Execution cost: %s"
                     % (tasks["executions"],
                        _fmt_usd(tasks["executions_cost_usd"])))
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in tasks["by_status"].items()],
            ["Status", "Count"]))
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in tasks["by_type"].items()],
            ["Type", "Count"]))
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in tasks["by_business"].items()],
            ["Business", "Count"]))
    else:
        lines.append("- Task counts: unknown (source %s)." % tasks["status"])
    lines.append("")
    lines.append("## Approvals (source: %s — status: %s)"
                 % (appr["source"], appr["status"]))
    lines.append("")
    if isinstance(appr.get("total"), int):
        lines.append("- Total: %d · Pending: %d · Decided in window: %d"
                     % (appr["total"], appr["pending"],
                        appr["decided_in_window"]))
        if appr["oldest_pending_age"]:
            lines.append("- Oldest pending age: %s" % appr["oldest_pending_age"])
        lines.append("")
        if appr["pending_list"]:
            lines.append(_table(
                [[p["id"], p["action"], p["detail"], p["requested_at"], p["age"]]
                 for p in appr["pending_list"]],
                ["ID", "Action", "Detail", "Requested", "Age"]))
        else:
            lines.append("- Pending list: (none)")
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in appr["by_status"].items()],
            ["Status", "Count"]))
    else:
        lines.append("- Approval counts: unknown (source %s)." % appr["status"])
    lines.append("")
    lines.append("## Lead chain — sandbox (source: %s — status: %s)"
                 % (chain["source"], chain["status"]))
    lines.append("")
    lines.append("- Total runs recorded: %s" % chain["total_runs"])
    lines.append("- Chain log lines: %s" % chain["log_lines"])
    if chain.get("note"):
        lines.append("- %s" % chain["note"])
    if chain.get("by_status"):
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in chain["by_status"].items()],
            ["Status", "Runs"]))
    lines.append("")
    lines.append("## Departments (source: %s)"
                 % report["departments"]["source"])
    lines.append("")
    dept_rows = []
    for d in report["departments"]["departments"]:
        if d["status"] == "ok":
            by_status = d.get("tasks_by_status")
            by_status_s = (", ".join("%s: %s" % (k, v)
                                     for k, v in by_status.items())
                           if isinstance(by_status, dict) and by_status
                           else "—")
            dept_rows.append([d["department"], d["tasks_total"],
                              by_status_s, d["pending_approvals"]])
        else:
            dept_rows.append([d["department"], UNKNOWN,
                              d.get("error", UNKNOWN), UNKNOWN])
    lines.append(_table(dept_rows,
                        ["Department", "Tasks", "By status", "Pending approvals"]))
    lines.append("")
    lines.append("## Usage & spend (source: %s — status: %s)"
                 % (usage["source"], usage["status"]))
    lines.append("")
    if isinstance(usage.get("total_calls"), int):
        lines.append("- Total calls: %d · Total spent: %s"
                     % (usage["total_calls"], _fmt_usd(usage["total_usd"])))
        lines.append("- In this window: %d call(s) · %s"
                     % (usage["in_window_calls"],
                        _fmt_usd(usage["in_window_usd"])))
        lines.append("- This month (%s): %s · Monthly cap: %s · Over cap: %s"
                     % (report["window"]["end_utc"][:7],
                        _fmt_usd(usage["monthly_total_usd"]),
                        _fmt_usd(usage["monthly_cap_usd"]),
                        usage["over_monthly_cap"]))
        lines.append("")
        lines.append(_table(
            [[k, v] for k, v in usage["by_kind"].items()],
            ["Kind", "Calls"]))
    else:
        lines.append("- Usage: unknown (source %s)." % usage["status"])
    lines.append("")
    lines.append("## Memory (source: %s — status: %s)"
                 % (report["memory"]["source"], report["memory"]["status"]))
    lines.append("")
    lines.append("- Entries: %s · Boxes: %s"
                 % (report["memory"]["entries"], report["memory"]["boxes"]))
    lines.append("")
    lines.append("## Schedules (source: %s — status: %s)"
                 % (sched["source"], sched["status"]))
    lines.append("")
    if isinstance(sched.get("total"), int):
        lines.append("- Total schedules: %d" % sched["total"])
        if isinstance(sched.get("by_status"), dict):
            lines.append(_table(
                [[k, v] for k, v in sched["by_status"].items()],
                ["Status", "Count"]))
        wk = sched["weekly_ceo_report"]
        lines.append("- Weekly CEO report job: %s (status: %s)"
                     % (wk.get("id", UNKNOWN), wk.get("status", UNKNOWN)))
        if wk.get("note"):
            lines.append("  - %s" % wk["note"])
    else:
        lines.append("- Schedules: unknown (source %s)." % sched["status"])
    lines.append("")
    lines.append("## Risks & blocked items")
    lines.append("")
    for r in report["risks_blocked"]:
        lines.append("- %s: **%s** (source: %s)"
                     % (r["item"], r["status"], r["source"]))
    lines.append("")
    lines.append("## Next actions (derived from the numbers above)")
    lines.append("")
    for action in report["next_actions"]:
        lines.append("- %s" % action)
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    for note in report["notes"]:
        lines.append("- %s" % note)
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    # Self-test — TEMP store only, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_store = os.path.join(tmp_dir, "store")
    os.makedirs(tmp_store)
    with open(os.path.join(tmp_store, "tasks.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "tasks-v1", "records": [
            {"id": "t1", "status": "queued", "type": "research",
             "business": "agency",
             "queued_at": "2026-11-25T00:00:00+00:00"},
            {"id": "t2", "status": "done", "type": "draft",
             "business": "agency",
             "queued_at": "2026-11-25T01:00:00+00:00",
             "completed_at": "2026-11-25T02:00:00+00:00",
             "executions": [{"attempt": 1, "task_id": "t2",
                             "status": "completed", "cost_usd": 0.0}]},
        ]}, f)
    with open(os.path.join(tmp_store, "approvals.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "approvals-v1", "records": [
            {"id": "a1", "status": "pending", "action": "send_email",
             "detail": "test send", "requested_at": "2026-11-24T12:00:00+00:00"},
        ]}, f)
    with open(os.path.join(tmp_store, "usage_ledger.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "usage-ledger-v1", "monthly_cap_usd": 0.0,
                   "records": [
                       {"id": "000001", "at": "2026-11-25T03:00:00+00:00",
                        "kind": "mock", "cost_usd": 0.0}]}, f)
    with open(os.path.join(tmp_store, "memory.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "owner-memory-v1", "entries": [{}],
                   "boxes": ["shared"]}, f)
    with open(os.path.join(tmp_store, "schedules.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "schedules-v1", "records": [
            {"id": "s1", "status": "paused", "name": "taskboard-queue-watch"},
        ]}, f)
    fixed_end = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)
    rep = generate_report(tmp_store, "weekly", end=fixed_end)
    assert rep["tasks"]["total"] == 2, rep["tasks"]
    assert rep["tasks"]["by_status"] == {"done": 1, "queued": 1}
    assert rep["tasks"]["in_window"] == 2
    assert rep["tasks"]["executions"] == 1
    assert rep["tasks"]["executions_cost_usd"] == 0.0
    assert rep["approvals"]["pending"] == 1
    assert rep["approvals"]["pending_list"][0]["id"] == "a1"
    assert rep["approvals"]["oldest_pending_age"] == "1d 0h", rep["approvals"]
    assert rep["usage"]["total_calls"] == 1
    assert rep["usage"]["total_usd"] == 0.0
    assert rep["lead_chain"]["total_runs"] == 0
    assert rep["lead_chain"]["status"] == "missing"
    assert len(rep["departments"]["departments"]) == 8
    md = render_markdown(rep)
    assert "## Tasks" in md and "a1" in md and "$0.00" in md
    # Empty temp store: everything "unknown", never an error.
    empty_store = os.path.join(tmp_dir, "empty-store")
    os.makedirs(empty_store)
    rep2 = generate_report(empty_store, "daily", end=fixed_end)
    assert rep2["tasks"]["status"] == "missing"
    assert rep2["tasks"]["total"] == UNKNOWN
    assert rep2["approvals"]["total"] == UNKNOWN
    assert rep2["usage"]["total_calls"] == UNKNOWN
    assert rep2["lead_chain"]["total_runs"] == 0
    md2 = render_markdown(rep2)
    assert "unknown" in md2
    print("ceo_reporting.report: OK (seeded temp store counts; empty "
          "store honest unknown; lead chain missing dir = 0 runs)")
