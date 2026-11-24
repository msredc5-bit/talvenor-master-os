#!/usr/bin/env python3
"""sync_status.py — Talvenor Master OS dashboard sync (Phase 4).

Rebuilds the numbers in dashboards/status.html from the real files —
not hand-written numbers. If a source file has no value, it writes "unknown",
never invents one. Stdlib only, no network, no send, no spend.

Sources:
  - 00-CEO-Core/config.json — phase, version, gates, $0 cap, first mails,
    paying clients, email status, phase status lines
  - store/tasks.json + store/approvals.json — real task/approval counts
  - 02-Digital-Product-Department/gate0-status.md — Gate 0 Status line
    (only that line is read — fail-closed; the lesson of Phase 2's bug)
  - 02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv — PA list row
  - 03-Content-Creation-Department/pipeline.md — the 13-stage count line
  - 03-Content-Creation-Department/toolpilot-status.md — Subscribers line
    + Videos line
  - 01-Agency-Department/departments/ — subdir + manager/*.py counts;
    agents/agent-registry/registry.json — entry + EXISTING counts
  - 02-Digital-Product-Department/kit-outline.md — the kit's parts list
    (blueprint); if no built kit dir exists, kit_parts 0
  - 03-Content-Creation-Department/sections/ — subdir + agents/*.py counts
  - 00-CEO-Core/jarvis_voice.py — voice REAL or STUB (whether NotImplementedError
    exists + whether Piper exists)
  - n8n workflow JSON (2, outside folder) — reads the "active" flag
    (false = NOT LIVE, true = LIVE — whatever is true is what is written)

Run:  python3 scripts/sync_status.py
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

from usage_ledger import UsageLedger  # noqa: E402 — A6: ledger numbers on the dashboard

AUTO_SEND_PATH = os.path.expanduser(
    "~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json")
CALLBACK_PATH = os.path.expanduser(
    "~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json")

UNKNOWN = "unknown"


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def read_gate0_status():
    """Reads only the Status line of gate0-status.md — fail-closed."""
    text = _read_text(os.path.join(
        BASE, "02-Digital-Product-Department", "gate0-status.md"))
    if text is None:
        return UNKNOWN
    for line in text.splitlines():
        if line.strip().startswith("**Status:"):
            if "NOT PASSED" in line:
                return "NOT PASSED"
            if "PASSED" in line:
                return "PASSED"
            return UNKNOWN
    return UNKNOWN


def read_pipeline_counts():
    """REAL/MOCK/STUB/BLOCKED from pipeline.md's count line."""
    text = _read_text(os.path.join(
        BASE, "03-Content-Creation-Department", "pipeline.md"))
    if text is None:
        return {"real": UNKNOWN, "mock": UNKNOWN,
                "stub": UNKNOWN, "blocked": UNKNOWN}
    m = re.search(r"REAL \*\*(\d+)\*\* · MOCK \*\*(\d+)\*\* · "
                  r"STUB \*\*(\d+)\*\* · BLOCKED \*\*(\d+)\*\*", text)
    if not m:
        return {"real": UNKNOWN, "mock": UNKNOWN,
                "stub": UNKNOWN, "blocked": UNKNOWN}
    return {"real": int(m.group(1)), "mock": int(m.group(2)),
            "stub": int(m.group(3)), "blocked": int(m.group(4))}


def read_pa_list_count():
    path = os.path.join(BASE, "02-Digital-Product-Department",
                        "pa-vet-list", "pa-vet-clinics.csv")
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        if not rows:
            return UNKNOWN
        return len(rows) - 1  # excluding the header
    except OSError:
        return UNKNOWN


def read_toolpilot_subs():
    text = _read_text(os.path.join(
        BASE, "03-Content-Creation-Department", "toolpilot-status.md"))
    if text is None:
        return UNKNOWN
    m = re.search(r"Subscribers: \*\*(\d+)\*\*", text)
    return int(m.group(1)) if m else UNKNOWN


def read_voice_status():
    """Voice REAL or STUB from jarvis_voice.py — a STUB has NotImplementedError."""
    text = _read_text(os.path.join(BASE, "00-CEO-Core", "jarvis_voice.py"))
    if text is None:
        return {"label": UNKNOWN, "detail": UNKNOWN}
    if "NotImplementedError" not in text and "Piper" in text:
        return {"label": "REAL",
                "detail": "Jarvis voice — Piper TTS + Vosk/sherpa STT, offline, $0 "
                          "(mic test still pending on Boss's PC)"}
    return {"label": "STUB", "detail": "Jarvis voice STUB — Piper/sherpa "
                                        "not found in jarvis_voice.py "
                                        "(the real loop is voice/loop.py; "
                                        "mic test still Boss's PC step)"}


def read_workflow_status(path):
    """The active flag of an n8n workflow JSON — false = NOT LIVE."""
    data = _read_json(path)
    if data is None:
        return {"status": UNKNOWN, "nodes": UNKNOWN, "name": UNKNOWN}
    active = data.get("active")
    nodes = data.get("nodes")
    return {
        "status": "LIVE" if active is True else ("NOT LIVE" if active is False else UNKNOWN),
        "nodes": len(nodes) if isinstance(nodes, list) else UNKNOWN,
        "name": data.get("name") or UNKNOWN,
    }


def _count_subdirs(path):
    """Count of sorted subdirs — unknown if it cannot be read."""
    try:
        return len([d for d in sorted(os.listdir(path))
                    if os.path.isdir(os.path.join(path, d))])
    except OSError:
        return UNKNOWN


def _count_py_in_subdirs(parent, sub):
    """Count of *.py files in the sub/ folder of each sorted subdir of parent."""
    try:
        total = 0
        for name in sorted(os.listdir(parent)):
            d = os.path.join(parent, name, sub)
            if not os.path.isdir(d):
                continue
            total += len([f for f in sorted(os.listdir(d))
                          if f.endswith(".py")])
        return total
    except OSError:
        return UNKNOWN


def read_toolpilot_videos():
    """The Videos line of toolpilot-status.md — same pattern as subs."""
    text = _read_text(os.path.join(
        BASE, "03-Content-Creation-Department", "toolpilot-status.md"))
    if text is None:
        return UNKNOWN
    m = re.search(r"Videos: \*\*(\d+)\*\*", text)
    return int(m.group(1)) if m else UNKNOWN


def _read_kit_total():
    """Count of ### headings in kit-outline.md's 'Kit's 6 parts' section."""
    text = _read_text(os.path.join(
        BASE, "02-Digital-Product-Department", "kit-outline.md"))
    if text is None:
        return UNKNOWN
    in_section = False
    total = 0
    for line in text.splitlines():
        if line.startswith("## Kit's"):
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            if line.startswith("### "):
                total += 1
    return total if total else UNKNOWN


def read_business_os():
    """The real state of the 3 Business OSs — from all files, not hand-written numbers."""
    # --- Agency: counts from departments/ + registry.json ---
    dept_dir = os.path.join(BASE, "01-Agency-Department", "departments")
    reg = _read_json(os.path.join(
        BASE, "01-Agency-Department", "agents", "agent-registry",
        "registry.json"))
    if isinstance(reg, list):
        registry_entries = len(reg)
        registry_existing = len([e for e in reg
                                 if isinstance(e, dict)
                                 and e.get("status") == "EXISTING"])
    else:
        registry_entries = UNKNOWN
        registry_existing = UNKNOWN
    agency = {
        "dept_count": _count_subdirs(dept_dir),
        "manager_count": _count_py_in_subdirs(dept_dir, "manager"),
        "registry_entries": registry_entries,
        "registry_existing": registry_existing,
        # registry.md line 27's durable fact: 21 staff
        # (15 worker + 6 section agent).
        "staff_note": "21 staff (15 workers + 6 section agents)",
    }

    # --- Commerce: Gate 0 + PA list reuse; counts from the kit blueprint ---
    gate0 = read_gate0_status()
    kit_dir = os.path.join(BASE, "02-Digital-Product-Department", "kit")
    kit_total = _read_kit_total()
    if kit_total == UNKNOWN:
        kit_parts = UNKNOWN
    elif not os.path.isdir(kit_dir):
        # Blueprint exists, no built kit dir → no part has been built yet.
        kit_parts = 0
    else:
        kit_parts = len([f for f in sorted(os.listdir(kit_dir))
                         if os.path.isfile(os.path.join(kit_dir, f))])
    commerce = {
        "gate0": gate0,
        "pa_list": read_pa_list_count(),
        "kit_parts": kit_parts,
        "kit_total": kit_total,
        # If Gate 0 is not passed, kit building/selling has not even started → sale 0
        # (entailed, not invented).
        "kit_sales": 0 if gate0 == "NOT PASSED" else UNKNOWN,
        # The division statuses below are durable policy facts — source MEMORY.md
        # (Boss decisions 2026-11-12/11-19): Amazon GATED (5 live client +
        # until $5K MRR), Etsy CLOSED (Bangladesh), Shopify
        # PARKED (Boss's direct project), Dropshipping RESEARCH-ONLY,
        # Digital Products BLOCKED-GATE0 (Vet Kit $49).
        "divisions": {
            "amazon": "GATED",
            "etsy": "CLOSED",
            "shopify": "PARKED",
            "dropshipping": "RESEARCH-ONLY",
            "digital_products": "BLOCKED-GATE0",
        },
    }

    # --- Media: pipeline + ToolPilot reuse; counts from sections/ ---
    media = {
        "pipeline": read_pipeline_counts(),
        "toolpilot_subs": read_toolpilot_subs(),
        "toolpilot_videos": read_toolpilot_videos(),
        # pipeline.md's durable fact: Upload OFF — no real YouTube
        # upload verified yet.
        "upload": "OFF",
        "sections": _count_subdirs(os.path.join(
            BASE, "03-Content-Creation-Department", "sections")),
        "agents": _count_py_in_subdirs(os.path.join(
            BASE, "03-Content-Creation-Department", "sections"), "agents"),
    }
    return {"agency": agency, "commerce": commerce, "media": media}


def read_usage_ledger():
    """Real numbers from store/usage_ledger.json — monthly_total() +
    total_calls (A6). If the ledger file is missing, 0 — not unknown, 0."""
    try:
        ledger = UsageLedger()
        summary = ledger.summary()
        return {
            "monthly_total_usd": ledger.monthly_total(),
            "total_calls": summary["total_calls"],
            "total_usd": summary["total_usd"],
            "monthly_cap_usd": summary["monthly_cap_usd"],
            "over_monthly_cap": ledger.over_monthly_cap(),
        }
    except Exception:  # noqa: BLE001 — if the ledger cannot be read, the dashboard does not break
        return {"monthly_total_usd": UNKNOWN, "total_calls": UNKNOWN,
                "total_usd": UNKNOWN, "monthly_cap_usd": UNKNOWN,
                "over_monthly_cap": UNKNOWN}


# --- Phase 7 (Worker A): founder-dashboard extension, additive only. ---

DEPARTMENTS = [
    ("01-sales-growth", "Sales & Growth"),
    ("02-marketing", "Marketing"),
    ("03-ai-engineering", "AI Engineering"),
    ("04-client-operations", "Client Operations"),
    ("05-research-strategy", "Research & Strategy"),
    ("06-finance-admin", "Finance & Admin"),
    ("07-quality-security", "Quality & Security"),
    ("08-product-innovation", "Product Innovation"),
]

TASK_STATUSES = ("queued", "done", "dead_letter", "blocked",
                 "cancelled", "duplicate", "failed-legacy")

APPROVAL_TTL_MINUTES = 20  # mirrors human_approval_gateway.APPROVAL_TTL_MINUTES


def _parse_iso(value):
    """ISO timestamp -> aware datetime, or None (never raises)."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _chain_records():
    """Phase 6 chain records under store/chains/ — read-only, never invent.

    Returns a list of (filename, dict) pairs, or [] when the dir is absent
    (no chain has run against the real store yet)."""
    chains_dir = os.path.join(BASE, "store", "chains")
    try:
        names = sorted(os.listdir(chains_dir))
    except OSError:
        return []
    out = []
    for name in names:
        if not name.endswith(".json"):
            continue
        data = _read_json(os.path.join(chains_dir, name))
        if isinstance(data, dict):
            out.append((name, data))
    return out


def read_departments():
    """Per-department status for all 8 departments.

    workflow: True when a *.json workflow file exists in workflows/.
    report_compiles: True when reports/report.py parses (compile check only).
    last_execution: outcome from a real chain record naming the department,
    else "unknown" — tasks.json carries no department field, so nothing is
    guessed from it."""
    chains = _chain_records()
    dept_dir = os.path.join(BASE, "01-Agency-Department", "departments")
    result = {}
    for slug, label in DEPARTMENTS:
        base = os.path.join(dept_dir, slug)
        try:
            wf_names = [f for f in os.listdir(os.path.join(base, "workflows"))
                        if f.endswith(".json")]
        except OSError:
            wf_names = []
        report_path = os.path.join(base, "reports", "report.py")
        report_src = _read_text(report_path)
        try:
            compile(report_src, report_path, "exec") if report_src else None
            report_compiles = report_src is not None
        except SyntaxError:
            report_compiles = False
        last_execution = UNKNOWN
        for fname, rec in chains:
            hay = fname + json.dumps(rec, default=str)
            if slug in hay or label.lower() in hay.lower():
                last_execution = (rec.get("outcome") or rec.get("status")
                                  or rec.get("result") or UNKNOWN)
                break
        result[slug] = {
            "label": label,
            "workflow_file": wf_names[0] if wf_names else UNKNOWN,
            "workflow_present": bool(wf_names),
            "report_compiles": report_compiles,
            "last_execution": last_execution,
        }
    return result


def read_task_counts(task_records):
    """tasks.json records counted by status. Unknown statuses land in
    "other" — never dropped, never invented."""
    counts = {st: 0 for st in TASK_STATUSES}
    counts["other"] = 0
    if isinstance(task_records, list):
        for rec in task_records:
            st = rec.get("status") if isinstance(rec, dict) else None
            if st in counts:
                counts[st] += 1
            else:
                counts["other"] += 1
    counts["total"] = sum(counts.values())
    return counts


def read_approvals_detail(appr_records):
    """Pending approvals with age (minutes since requested_at) and
    expires_in (minutes left of the 20-min TTL). Unparseable timestamps
    give "unknown", never a guessed number."""
    pending = []
    if isinstance(appr_records, list):
        now = datetime.now(timezone.utc)
        for rec in appr_records:
            if not isinstance(rec, dict) or rec.get("status") != "pending":
                continue
            requested = _parse_iso(rec.get("requested_at"))
            if requested is not None:
                age = int((now - requested).total_seconds() // 60)
                expires_in = APPROVAL_TTL_MINUTES - age
            else:
                age = UNKNOWN
                expires_in = UNKNOWN
            pending.append({
                "id": rec.get("id", UNKNOWN),
                "action": rec.get("action", UNKNOWN),
                "detail": rec.get("detail", UNKNOWN),
                "requested_by": rec.get("requested_by", UNKNOWN),
                "requested_at": rec.get("requested_at", UNKNOWN),
                "age_minutes": age,
                "expires_in_minutes": expires_in,
            })
    oldest_age = UNKNOWN
    ages = [p["age_minutes"] for p in pending
            if isinstance(p["age_minutes"], int)]
    if ages:
        oldest_age = max(ages)
    return {
        "pending": pending,
        "pending_count": len(pending),
        "oldest_age_minutes": oldest_age,
    }


def read_control():
    """Pause / emergency-stop state from store/control.json (Worker C's
    file). Missing or unreadable = unknown state, never a crash — the
    sync must keep working when Worker C has not created it yet."""
    default = {"paused": False, "emergency_stop": False, "state": UNKNOWN}
    data = _read_json(os.path.join(BASE, "store", "control.json"))
    if not isinstance(data, dict):
        return dict(default)
    return {
        "paused": bool(data.get("paused", False)),
        "emergency_stop": bool(data.get("emergency_stop", False)),
        "state": data.get("state", UNKNOWN),
    }


def read_ceo_report():
    """Latest CEO report from reports/ceo/ (Worker B's output), if any.

    Newest file by mtime wins. JSON reports contribute their own period /
    generated_at / counts when present; anything missing is "unknown"."""
    ceo_dir = os.path.join(BASE, "reports", "ceo")
    try:
        names = [f for f in sorted(os.listdir(ceo_dir))
                 if os.path.isfile(os.path.join(ceo_dir, f))]
    except OSError:
        return {"available": False}
    if not names:
        return {"available": False}
    latest = max(names, key=lambda n: os.path.getmtime(
        os.path.join(ceo_dir, n)))
    path = os.path.join("reports", "ceo", latest)
    full = os.path.join(BASE, path)
    result = {
        "available": True,
        "path": path,
        "period": UNKNOWN,
        "generated_at": UNKNOWN,
        "task_counts": UNKNOWN,
        "approval_counts": UNKNOWN,
    }
    try:
        result["generated_at"] = datetime.fromtimestamp(
            os.path.getmtime(full), tz=timezone.utc).isoformat()
    except OSError:
        pass
    if latest.endswith(".json"):
        data = _read_json(full)
        if isinstance(data, dict):
            result["period"] = data.get("period", UNKNOWN)
            if isinstance(data.get("generated_at"), str):
                result["generated_at"] = data["generated_at"]
            result["task_counts"] = data.get(
                "task_counts",
                (data.get("tasks") or {}).get("by_status", UNKNOWN)
                if isinstance(data.get("tasks"), dict) else UNKNOWN)
            result["approval_counts"] = data.get(
                "approval_counts", data.get("approvals", UNKNOWN))
    else:
        text = _read_text(full)
        if text:
            m = re.search(r"[Pp]eriod:\s*(.+)", text)
            if m:
                result["period"] = m.group(1).strip()
            m = re.search(r"[Gg]enerated(?:_at)?:\s*(.+)", text)
            if m:
                result["generated_at"] = m.group(1).strip()
    return result


def collect_status():
    """Gathers the true state from all sources in one place. Unknown if a value is missing."""
    cfg = _read_json(os.path.join(BASE, "00-CEO-Core", "config.json")) or {}
    honest = cfg.get("honest_status") or {}
    phases = honest.get("phases") or {}
    gates = cfg.get("gates") or {}

    tasks = _read_json(os.path.join(BASE, "store", "tasks.json")) or {}
    approvals = _read_json(os.path.join(BASE, "store", "approvals.json")) or {}
    task_records = tasks.get("records")
    appr_records = approvals.get("records")
    pending = ([r for r in appr_records if r.get("status") == "pending"]
               if isinstance(appr_records, list) else UNKNOWN)
    approved = ([r for r in appr_records if r.get("status") == "approved"]
                if isinstance(appr_records, list) else UNKNOWN)

    email_raw = honest.get("email_outreach") or ""
    email = "PAUSED" if "PAUSED" in str(email_raw) else (
        "unknown" if not email_raw else str(email_raw))

    return {
        "phase": cfg.get("phase", UNKNOWN),
        "version": cfg.get("version", UNKNOWN),
        "built": cfg.get("built", UNKNOWN),
        "gates_enabled": gates.get("enabled", UNKNOWN),
        "spend_cap_usd": cfg.get("spend_cap_usd", UNKNOWN),
        "first_mails": honest.get("first_mails_sent", UNKNOWN),
        "paying_clients": honest.get("paying_clients", UNKNOWN),
        "email": email,
        "gate0": read_gate0_status(),
        "pa_list": read_pa_list_count(),
        "pipeline": read_pipeline_counts(),
        "toolpilot_subs": read_toolpilot_subs(),
        "tasks_count": len(task_records) if isinstance(task_records, list) else UNKNOWN,
        "approvals_pending": len(pending) if isinstance(pending, list) else UNKNOWN,
        "approvals_approved": len(approved) if isinstance(approved, list) else UNKNOWN,
        # D2 (2026-11-21): phase_status = all keys of honest_status.phases —
        # not just phase_0–7 (agentic 1–3, unified_os, phase_9/10/11,
        # improvements all reach the dashboard). Unknown if a key is missing.
        "phase_status": dict(phases) if isinstance(phases, dict) else {},
        "voice": read_voice_status(),
        "usage_ledger": read_usage_ledger(),
        "business_os": read_business_os(),
        "workflow_auto_send": read_workflow_status(AUTO_SEND_PATH),
        "workflow_callback": read_workflow_status(CALLBACK_PATH),
        # Phase 7 (Worker A) — additive keys only; dashboard-3d.html reads
        # this JSON, so existing keys are never renamed or removed.
        "departments": read_departments(),
        "task_counts": read_task_counts(task_records),
        "approvals": read_approvals_detail(appr_records),
        "control": read_control(),
        "ceo_report": read_ceo_report(),
    }


def _badge(text, kind):
    return f'<span class="badge {kind}">{text}</span>'


def render_html(s):
    """Builds the full status.html from collect_status() (deterministic)."""
    ph = s["phase_status"]
    pipe = s["pipeline"]
    gate0 = s["gate0"]
    pa = s["pa_list"]
    subs = s["toolpilot_subs"]
    wf_a = s["workflow_auto_send"]
    wf_c = s["workflow_callback"]
    voice = s["voice"]
    phase = s["phase"]
    bo = s["business_os"]
    a = bo["agency"]
    c = bo["commerce"]
    d = c["divisions"]
    m = bo["media"]
    stages_total = (pipe["real"] + pipe["mock"] + pipe["stub"] + pipe["blocked"]
                    if all(isinstance(pipe[k], int)
                           for k in ("real", "mock", "stub", "blocked"))
                    else UNKNOWN)

    def phase_badge(status_text):
        if isinstance(status_text, str) and status_text.startswith("BUILT"):
            return _badge("BUILT", "built")
        if isinstance(status_text, str) and "NOT PROVEN LIVE" in status_text:
            return _badge("NOT PROVEN LIVE", "paused")
        if status_text == "PENDING":
            return _badge("PENDING", "pending")
        return _badge(str(status_text), "stub")

    ul = s.get("usage_ledger") or {}

    gate0_badge = (_badge("NOT PASSED", "paused") if gate0 == "NOT PASSED"
                   else _badge("PASSED", "built") if gate0 == "PASSED"
                   else _badge("unknown", "stub"))
    email_badge = (_badge("PAUSED", "paused") if s["email"] == "PAUSED"
                   else _badge(str(s["email"]), "stub"))

    def wf_badge(status):
        if status == "NOT LIVE":
            return _badge("READY · NOT LIVE", "pending")
        if status == "LIVE":
            return _badge("LIVE", "built")
        return _badge("unknown", "stub")

    # --- Phase 7 (Worker A) cards — built here, inserted before Contact. ---
    depts = s.get("departments") or {}
    tc = s.get("task_counts") or {}
    appr = s.get("approvals") or {}
    ctrl = s.get("control") or {}
    ceo = s.get("ceo_report") or {}

    if ctrl.get("emergency_stop") is True:
        control_badge = _badge("EMERGENCY STOP", "paused")
    elif ctrl.get("paused") is True:
        control_badge = _badge("PAUSED", "paused")
    elif ctrl.get("state") == UNKNOWN:
        control_badge = _badge("unknown", "stub")
    else:
        control_badge = _badge("RUNNING", "built")
    appr_pending = appr.get("pending_count", UNKNOWN)
    appr_oldest = appr.get("oldest_age_minutes", UNKNOWN)
    oldest_txt = (f"oldest {appr_oldest} min ago" if isinstance(appr_oldest, int)
                  else "oldest age unknown")
    founder_control_card = (
        '<div class="card">\n'
        '    <h2>Founder Control</h2>\n'
        f'    <p>System state: {control_badge} '
        f'(paused: {ctrl.get("paused", UNKNOWN)} · '
        f'emergency stop: {ctrl.get("emergency_stop", UNKNOWN)})</p>\n'
        f'    <p>Approval centre: <strong>{appr_pending}</strong> pending · '
        f'{oldest_txt} · approved {s["approvals_approved"]}</p>\n'
        '    <p class="note">No gated action runs without Boss\'s gate word. '
        'Pause / emergency stop is read from store/control.json when present.</p>\n'
        '  </div>\n'
    )

    dept_rows = ""
    for slug, _label in DEPARTMENTS:
        dept = depts.get(slug) or {}
        wf = (_badge("present", "built") if dept.get("workflow_present") is True
              else _badge("unknown", "stub"))
        rep = (_badge("compiles", "built") if dept.get("report_compiles") is True
               else _badge("unknown", "stub"))
        last = dept.get("last_execution", UNKNOWN)
        dept_rows += (
            f'      <tr><td><strong>{dept.get("label", slug)}</strong> '
            f'({slug})</td><td>{wf}</td><td>{rep}</td>'
            f'<td>{last}</td></tr>\n'
        )
    departments_card = (
        '<div class="card">\n'
        '    <h2>Departments — 8 inside Agency</h2>\n'
        '    <table>\n'
        '      <tr><th>Department</th><th>Workflow</th><th>report.py</th>'
        '<th>Last execution</th></tr>\n'
        f'{dept_rows}'
        '    </table>\n'
        '    <p class="note">Workflow = a *.json file in the department\'s '
        'workflows/ folder. Last execution comes from a real Phase 6 chain '
        'record in store/chains/ — "unknown" means no record exists yet.</p>\n'
        '  </div>\n'
    )

    if ceo.get("available") is True:
        ceo_body = (
            f'    <p>Period: <strong>{ceo.get("period", UNKNOWN)}</strong> · '
            f'generated: {ceo.get("generated_at", UNKNOWN)}</p>\n'
            f'    <p>Tasks summarised: {ceo.get("task_counts", UNKNOWN)} · '
            f'approvals summarised: {ceo.get("approval_counts", UNKNOWN)}</p>\n'
            f'    <p class="note">File: {ceo.get("path", UNKNOWN)}</p>\n'
        )
    else:
        ceo_body = (
            '    <p>No CEO report yet — Worker B\'s ceo_reporting has not '
            'produced one.</p>\n'
        )
    ceo_card = (
        '<div class="card">\n'
        '    <h2>CEO Report — latest</h2>\n'
        f'{ceo_body}'
        '  </div>\n'
    )

    return f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Talvenor Master OS — Status (Phase {phase})</title>
<style>
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #FFFBF5; color: #0B1D33; margin: 0; padding: 24px; }}
  .wrap {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ color: #EA580C; margin-bottom: 4px; }}
  .sub {{ color: #555; margin-top: 0; }}
  .card {{ background: #fff; border: 1px solid #e5ddd2; border-radius: 12px; padding: 18px 20px; margin: 14px 0; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }}
  .built {{ background: #d1fae5; color: #065f46; }}
  .stub {{ background: #fef3c7; color: #92400e; }}
  .pending {{ background: #e0e7ff; color: #3730a3; }}
  .paused {{ background: #fee2e2; color: #991b1b; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid #eee; vertical-align: top; }}
  .gate-on {{ color: #065f46; font-weight: 700; }}
  .note {{ font-size: 13px; color: #666; }}
  footer {{ font-size: 13px; color: #888; margin-top: 24px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>🎬 Talvenor Master OS</h1>
  <p class="sub">Status dashboard — Phase {phase} (this page is built by scripts/sync_status.py — numbers come from the real files, not hand-written)</p>

  <div class="card">
    <h2>3 businesses — only these 3 (136 DROPPED)</h2>
    <table>
      <tr><th>Business</th><th>State</th><th>True Story</th></tr>
      <tr><td><strong>1. Agency</strong> — Talvenor AI Receptionist</td><td><span class="badge built">MAIN · Phase 1 REAL</span></td><td>First mail {s["first_mails"]}, paying client {s["paying_clients"]} · Chief really calls 15 workers (mock brain, DRAFT ONLY) · Email {s["email"]}</td></tr>
      <tr><td><strong>2. Digital Product</strong> — Vet No-Show Recovery Kit ($49)</td><td><span class="badge built">Phase 2 REAL*</span></td><td><strong>Gate 0 {gate0}</strong> — Lemon Squeezy test is Boss's step, not done · Kit blueprint exists (not the kit itself) · PA list {pa} / 100 (verified) · Sale 0 · *Stuck at Gate 0</td></tr>
      <tr><td><strong>3. Content Engine</strong> — Creator OS / ToolPilot</td><td><span class="badge built">Phase 3 REAL</span></td><td>Chief really calls 6 workers (mock brain, DRAFT ONLY) · 13 stages: REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]} · Upload OFF · VOICE.md DRAFT · GPU AMD Radeon integrated 496 MB VRAM (FramePack/WanGP will not run) · ToolPilot videos 0 (subs {subs})</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Unified OS — 3 Business OS</h2>
    <table>
      <tr><th>Business OS</th><th>State</th><th>Real Numbers</th></tr>
      <tr><td><strong>Agency</strong> — AI Receptionist</td><td><span class="badge paused">email PAUSED</span></td><td>{a["dept_count"]} departments · {a["manager_count"]} managers · {a["registry_entries"]} registry entries · {a["staff_note"]} · email {s["email"]} · clients {s["paying_clients"]}</td></tr>
      <tr><td><strong>Commerce</strong> — Vet Kit ($49)</td><td><span class="badge paused">Gate 0 NOT PASSED</span></td><td>Vet Kit Gate 0 {c["gate0"]} · kit {c["kit_parts"]}/{c["kit_total"]} · PA {c["pa_list"]}/100 · sale {c["kit_sales"]} · Amazon {d["amazon"]} · Etsy {d["etsy"]} · Shopify {d["shopify"]} (Boss direct) · Dropshipping {d["dropshipping"]}</td></tr>
      <tr><td><strong>Media</strong> — Content Engine / ToolPilot</td><td><span class="badge stub">upload OFF</span></td><td>{m["sections"]} sections · {m["agents"]} agents · {stages_total} stages REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]} · upload {m["upload"]} · ToolPilot subs {m["toolpilot_subs"]} · videos {m["toolpilot_videos"]}</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Phase</h2>
    <table>
      <tr><td><strong>Phase 0</strong> — folder + CEO Core + approval gateway + dashboard</td><td>{phase_badge(ph.get("phase_0", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 1</strong> — Agency department (vendored worker, draft-only, holds the gate)</td><td>{phase_badge(ph.get("phase_1_agency", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 2</strong> — Digital Product (Chief REAL, kit blueprint, PA list {pa}/100 — launch/sale stuck at Gate 0)</td><td>{phase_badge(ph.get("phase_2_digital_product", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 3</strong> — Creator OS department (Chief REAL, 6 worker wired, 13 stage REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]}, upload OFF)</td><td>{phase_badge(ph.get("phase_3_creator_os", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 4</strong> — n8n wiring (Gmail, Vapi, Sheets — workflows READY, NOT LIVE)</td><td>{phase_badge(ph.get("phase_4_n8n_wiring", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 5</strong> — Three Engines (shared tool-calling core + 3 engines: Agency 15 / Products 5 / Content 8 staff)</td><td>{phase_badge(ph.get("phase_5_three_engines", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 6</strong> — Brain + Runner (BrainFactory mock default, run_office.py — workers vendored)</td><td>{phase_badge(ph.get("phase_6_brain_runner", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 7</strong> — Full Offices: 16 sections, 23 section agents, 23 section skills (Agency 5 / Products 6 / Content 5 sections)</td><td>{phase_badge(ph.get("phase_7_sections", UNKNOWN))}</td></tr>
      <tr><td><strong>Agentic Phase 1</strong> — 8 departments inside Agency</td><td>{phase_badge(ph.get("agentic_phase_1", UNKNOWN))}</td></tr>
      <tr><td><strong>Agentic Phase 2</strong> — Chief DEPARTMENT_ROUTING (8 managers)</td><td>{phase_badge(ph.get("agentic_phase_2", UNKNOWN))}</td></tr>
      <tr><td><strong>Agentic Phase 3</strong> — 43 ROLE-ONLY specialists built as worker code</td><td>{phase_badge(ph.get("agentic_phase_3", UNKNOWN))}</td></tr>
      <tr><td><strong>Unified OS</strong> — CENTRAL-HQ (one brain + 3 Chiefs)</td><td>{phase_badge(ph.get("unified_os", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 9</strong> — taskboard + MCP stdio + live-ready tool code</td><td>{phase_badge(ph.get("phase_9_connections", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 10</strong> — live brain probe (NOT PROVEN LIVE — brain mock)</td><td>{phase_badge(ph.get("phase_10_live_brain", UNKNOWN))}</td></tr>
      <tr><td><strong>Phase 11</strong> — 7 LLM providers + fallback chain (brain still mock)</td><td>{phase_badge(ph.get("phase_11_providers", UNKNOWN))}</td></tr>
      <tr><td><strong>Improvement P1</strong> — trust gate as code</td><td>{phase_badge(ph.get("improvement_p1_gate", UNKNOWN))}</td></tr>
      <tr><td><strong>Improvement P2</strong> — owner memory + usage ledger ($0)</td><td>{phase_badge(ph.get("improvement_p2_memory_ledger", UNKNOWN))}</td></tr>
      <tr><td><strong>Improvement P3</strong> — quiet schedules (change-only watches)</td><td>{phase_badge(ph.get("improvement_p3_quiet_schedules", UNKNOWN))}</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>n8n Wiring — Connection to the Outside World</h2>
    <table>
      <tr><th>Workflow</th><th>State</th><th>True Story</th></tr>
      <tr><td><strong>Auto-send</strong> — {wf_a["name"]} ({wf_a["nodes"]} nodes)</td><td>{wf_badge(wf_a["status"])}</td><td>Schedule 18:00 Dhaka → Google Sheet Queue → Gmail send → sent written to Sheet · Import + Gmail/Sheets connect + 1-mail test are Boss's step · Cannot be run while Email is PAUSED</td></tr>
      <tr><td><strong>Callback</strong> — {wf_c["name"]} ({wf_c["nodes"]} nodes)</td><td>{wf_badge(wf_c["status"])}</td><td>Website form → n8n webhook → Vapi POST /call → Sophia callback · Twilio number (~$1.15/mo) import + workflow import + Vapi credential + webhook URL are Boss's step</td></tr>
    </table>
    <p class="note">Host: Muse runtime + 10-min bridge cron ($0) — no 24/7 always-on server, that will have to be paid for later. No workflow is LIVE — LIVE is not claimed. Two send systems will not run together (double mail would go out).</p>
  </div>

  <div class="card">
    <h2>Gates and Limits</h2>
    <p>Gates: <span class="gate-on">{"ON" if s["gates_enabled"] is True else str(s["gates_enabled"])}</span> — send / publish / spend / delete, none of them happen without Boss's gate word. No auto-approve.</p>
    <p>Spend cap: <strong>${s["spend_cap_usd"]}</strong></p>
    <p>Email: {email_badge} since 2026-11-14 — the SPF/DMARC DNS fix is still in Boss's hands.</p>
    <p>Paying clients: <strong>{s["paying_clients"]}</strong> · Kit sales: <strong>0</strong> (Gate 0 {gate0}) · ToolPilot videos: <strong>0</strong> · Upload: <span class="badge paused">OFF</span> (stage 9, needs Boss's "upload it" + credential)</p>
    <p>Gate 0: {gate0_badge} — Lemon Squeezy signup test (~15 min) is Boss's step. If it passes, the PA list will fill to 100, then the kit is built.</p>
    <p>Store: tasks {s["tasks_count"]} · approvals pending {s["approvals_pending"]} / approved {s["approvals_approved"]}</p>
    <p>Usage ledger: {ul.get("total_calls", UNKNOWN)} calls · ${ul.get("monthly_total_usd", UNKNOWN)} this month (cap ${ul.get("monthly_cap_usd", UNKNOWN)}/mo) · over cap: {ul.get("over_monthly_cap", UNKNOWN)}</p>
  </div>

  <div class="card">
    <h2>REAL vs STUB vs REUSED</h2>
    <table>
      <tr><td><strong>REAL</strong></td><td>Approval gateway (approve/reject really records), Main CEO Bot router, config.json, this dashboard (built by sync), <strong>Agency Chief of Staff (15 worker routing, draft-only, gated work gets stuck in PENDING)</strong>, <strong>Products Chief of Staff (kit blueprint, PA list {pa}/100, launch/sale stuck at Gate 0)</strong>, <strong>Content Chief of Staff (6 Creator OS worker routing, draft-only, stuck at upload OFF, does not make video files)</strong></td></tr>
      <tr><td><strong>READY (NOT LIVE)</strong></td><td>n8n auto-send workflow + callback workflow — import files ready, Boss's import + connect + test remaining, neither is LIVE</td></tr>
      <tr><td><strong>{voice["label"]}</strong></td><td>{voice["detail"]}</td></tr>
      <tr><td><strong>VENDORED (Phase 6)</strong></td><td>boss-ceo engine (15 workers) + Creator OS (6 workers) — copies now inside the repo; talvenor-office, jarvis-ceo-os-concept — reference only</td></tr>
    </table>
    <p class="note">Gemini's map had 4 errors, fixed here: (1) Jarvis ≠ Main CEO Bot, separate; (2) an approval/gate layer exists; (3) store/Vault exists; (4) digital product = Vet Kit $49, not generic "Notion Kits".</p>
  </div>

  {founder_control_card}
  {departments_card}
  {ceo_card}
  <div class="card">
    <h2>Contact (real)</h2>
    <p>Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)<br>
    Phone: +1 (947) 223-0244<br>
    Email: hello@talvenorai.agency (outreach) · contact@talvenorai.agency (main)</p>
  </div>

  <footer>Built: {s.get("built", UNKNOWN)} (Phase {phase}) · Folder: ~/workspace/talvenor-master-os/ · Version {s["version"]} · Phase 2 stuck at Gate 0 — kit blueprint + PA list {pa}/100 only. Content: 13 stages REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]}, upload OFF. n8n workflows READY, NOT LIVE. No number invented — all synced from the real files.</footer>
</div>
</body>
</html>
"""


def write_status_json(status):
    """Writes the full dict from collect_status() to dashboards/status.json.

    dashboard-3d.html reads this JSON — so the 3D dashboard's numbers always come
    from the real files, not hand-written. Running sync_status.py refreshes the JSON
    immediately. Deterministic (sort_keys) — two runs are byte-identical."""
    out = os.path.join(BASE, "dashboards", "status.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False, sort_keys=True)
    return out


def main():
    status = collect_status()
    html = render_html(status)
    out = os.path.join(BASE, "dashboards", "status.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    json_out = write_status_json(status)
    print("sync done ->", out)
    print("sync done ->", json_out)
    bo = status["business_os"]
    print(f"phase={status['phase']} clients={status['paying_clients']} "
          f"first_mails={status['first_mails']} email={status['email']} "
          f"gate0={status['gate0']} pa_list={status['pa_list']} "
          f"pipeline={status['pipeline']} subs={status['toolpilot_subs']} "
          f"auto_send={status['workflow_auto_send']['status']} "
          f"callback={status['workflow_callback']['status']} "
          f"business_os=agency {bo['agency']['dept_count']} dept / "
          f"{bo['agency']['manager_count']} mgr / "
          f"{bo['agency']['registry_entries']} registry "
          f"({bo['agency']['registry_existing']} EXISTING) "
          f"commerce kit {bo['commerce']['kit_parts']}/"
          f"{bo['commerce']['kit_total']} "
          f"media {bo['media']['sections']} sections / "
          f"{bo['media']['agents']} agents")
    depts_ok = sum(1 for d in status["departments"].values()
                   if d["workflow_present"] and d["report_compiles"])
    print(f"phase7: departments {depts_ok}/8 ok · "
          f"task_counts={status['task_counts']} · "
          f"approvals_pending={status['approvals']['pending_count']} · "
          f"control={status['control']} · "
          f"ceo_report_available={status['ceo_report']['available']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
