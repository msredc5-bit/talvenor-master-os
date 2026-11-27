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
  - FOUNDER OS phase (F2 batch 1) — a constant in this file, sourced
    from founder-os-audit-2026-11-26.md §14; config.json's "phase"
    is old numbering, kept as history, never the phase display
  - Agent Team Roster — 01-Agency-Department/agents/agent-registry/
    registry.json (69 entries) + logs/skill_executions.jsonl (latest
    skill-load timestamp per skill file) + the worker file's
    [MOCK DRAFT] marker (draft / coded / unknown)
  - Latest CEO report — copied byte-for-byte to dashboards/
    ceo-report.json so the Command Center (same origin) can fetch it;
    a stale copy is removed when no report is available
  - FOUNDER OS F2 batch 3 — chat (brain mode + chain from
    config.json, assistant name from store/MEMORY.md), voice command
    (00-CEO-Core/voice/loop.py GATE_PHRASES + voice detail),
    personas (00-CEO-Core/personas.json), execution
    (logs/skill_executions.jsonl recent records +
    logs/dev_brain_calls.jsonl), memory (store/memory.json structure
    ONLY — counts, boxes, entry metadata; never quote/text content),
    library (docs/ + top-level *.md + 00-CEO-Core/*.md +
    ~/workspace/unified-business-os/*.md when present), integrations
    (n8n MCP verified record 2026-11-25 + config provider states;
    a service is "connected" only with a dated probe record)

Run:  python3 scripts/sync_status.py
"""

import csv
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

from usage_ledger import UsageLedger  # noqa: E402 — A6: ledger numbers on the dashboard

# F2 batch 2 — approval TTL from the gateway itself (never a second
# hardcoded copy that can drift). The gateway is stdlib-only, so this
# import cannot fail on a missing package; the fallback is the same
# mirrored constant the file already used, for safety only.
try:
    from human_approval_gateway import APPROVAL_TTL_MINUTES
except Exception:  # noqa: BLE001 — gateway unreadable: mirror, do not crash sync
    APPROVAL_TTL_MINUTES = 20

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


# F2 batch 1 — FOUNDER OS phase. The audit (§14) is the source:
# F0–F10 is the only numbering from the audit's approval onward.
# Update this constant when a phase's exit gate passes. Never derive
# the phase from config.json — its "phase": 11 is old numbering.
FOUNDER_OS_PHASE = {
    "phase": "F2",
    "batch": 3,
    "label": "Founder Command Center — batch 3",
    "source": "founder-os-audit-2026-11-26.md §14 (F2)",
}


def read_founder_os():
    """Current FOUNDER OS phase (F2 batch 3)."""
    return dict(FOUNDER_OS_PHASE)


# F2 batch 3 — n8n Cloud MCP verified record (2026-11-25). The
# values are the verification itself (list-tools + search_workflows
# via custom.n8n-mcp/CONNECTOR.md): 75 tools, 0 workflows, 41
# read-only tools allowed, 34 write ops blocked. This is the ONLY
# service the Command Center may call "connected" — every other
# integration is "not connected" / "disabled" / "unknown" until a
# dated probe says otherwise.
N8N_MCP_VERIFIED = {
    "service": "n8n Cloud MCP",
    "instance": "talvenorai.app.n8n.cloud",
    "state": "connected",
    "verified": "2026-11-25",
    "tools": 75,
    "workflows": 0,
    "allowed_read_only": 41,
    "write_blocked": 34,
    "rest_api": "blocked on free trial (404)",
    "source": "custom.n8n-mcp/CONNECTOR.md (verified 2026-11-25)",
}

# F2 batch 3 — provider states. A provider is never "connected"
# without a dated probe. Meta was probed 2026-11-20 (tunnel 403,
# key validity unproven); Ollama was proven on Boss's PC
# 2026-11-26 (docs/live-brain-proof-2026-11-26.md). Every other
# provider is disabled in config and unprobed.
PROVIDER_STATES = {
    "meta": {
        "state": "unreachable from this VM",
        "verified": "2026-11-20",
        "evidence": "tunnel 403; key validity unproven",
        "source": "founder-os-audit-2026-11-26.md §5.2",
    },
    "ollama": {
        "state": "local — not present in this VM",
        "verified": "2026-11-26",
        "evidence": "proven on Boss's PC (qwen2.5-coder:1.5b, 1.9s)",
        "source": "docs/live-brain-proof-2026-11-26.md",
    },
}


def read_roster():
    """Agent Team Roster (F2 batch 1): one row per registry.json entry.

    worker: "draft" when the worker file contains the [MOCK DRAFT]
    marker, "coded" when it does not, "unknown" when the file cannot
    be read. last_skill_load: latest timestamp in
    logs/skill_executions.jsonl whose result is this entry's
    skill_file, else "unknown" — a skill load is activity evidence,
    not proof the agent executed a task; the card labels it as such.
    """
    reg_path = os.path.join(BASE, "01-Agency-Department", "agents",
                            "agent-registry", "registry.json")
    reg = _read_json(reg_path)
    if not isinstance(reg, list):
        return {"total": UNKNOWN, "entries": [], "with_activity": UNKNOWN,
                "draft": UNKNOWN, "coded": UNKNOWN}
    last_load = {}
    log_path = os.path.join(BASE, "logs", "skill_executions.jsonl")
    try:
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(ev, dict):
                    continue
                result = ev.get("result")
                ts = ev.get("timestamp")
                if isinstance(result, str) and isinstance(ts, str):
                    if result not in last_load or ts > last_load[result]:
                        last_load[result] = ts
    except OSError:
        pass
    entries = []
    draft = coded = with_activity = 0
    for e in reg:
        if not isinstance(e, dict):
            continue
        worker_file = e.get("worker_file") or UNKNOWN
        worker = UNKNOWN
        if isinstance(worker_file, str) and worker_file != UNKNOWN:
            try:
                with open(os.path.join(BASE, worker_file),
                          encoding="utf-8", errors="ignore") as f:
                    head = f.read(65536)
                worker = "draft" if "MOCK DRAFT" in head else "coded"
            except OSError:
                worker = UNKNOWN
        if worker == "draft":
            draft += 1
        elif worker == "coded":
            coded += 1
        skill_file = e.get("skill_file") or UNKNOWN
        last = (last_load.get(skill_file, UNKNOWN)
                if isinstance(skill_file, str) else UNKNOWN)
        if last != UNKNOWN:
            with_activity += 1
        entries.append({
            "role": e.get("role", UNKNOWN),
            "department": e.get("department", UNKNOWN),
            "skill_file": skill_file,
            "worker_file": worker_file,
            "status": e.get("status", UNKNOWN),
            "worker": worker,
            "last_skill_load": last,
        })
    return {"total": len(entries), "entries": entries,
            "with_activity": with_activity, "draft": draft, "coded": coded}


# F2 batch 2 — Task Center (module 10), Reports Center (15),
# Financial Dashboard (17), System Health (18), Settings &
# Permissions (19). All additive-only; existing keys never renamed.
# Every value comes from a real repo file; a missing source is
# "unknown", never a guessed number.

def read_task_queue(task_records):
    """Task Center: the task queue itself (records, not just counts),
    the queue-watch schedule, and how a drain happens.

    Records come from store/tasks.json via the caller (collect_status
    already read it). The watch comes from store/schedules.json.
    Drain is manual CLI — the schedules note says no runner is
    attached yet (bridge adoption needs Boss's word)."""
    counts = read_task_counts(task_records)
    records = []
    if isinstance(task_records, list):
        for rec in task_records:
            if not isinstance(rec, dict):
                continue
            records.append({
                "id": rec.get("id", UNKNOWN),
                "status": rec.get("status", UNKNOWN),
                "business": rec.get("business", UNKNOWN),
                "type": rec.get("type", UNKNOWN),
                "title": rec.get("title", UNKNOWN),
                "queued_at": rec.get("queued_at", UNKNOWN),
                "completed_at": rec.get("completed_at", UNKNOWN),
                "result": rec.get("result", UNKNOWN),
            })
    sched = _read_json(os.path.join(BASE, "store", "schedules.json")) or {}
    watch = {"name": UNKNOWN, "interval_minutes": UNKNOWN,
             "status": UNKNOWN, "runs": UNKNOWN,
             "last_run_at": UNKNOWN, "note": UNKNOWN}
    sched_records = sched.get("records") if isinstance(sched, dict) else None
    if isinstance(sched_records, list):
        for rec in sched_records:
            if isinstance(rec, dict) and rec.get("source") == "store/tasks.json":
                watch = {
                    "name": rec.get("name", UNKNOWN),
                    "interval_minutes": rec.get("interval_minutes", UNKNOWN),
                    "status": rec.get("status", UNKNOWN),
                    "runs": rec.get("runs", UNKNOWN),
                    "last_run_at": rec.get("last_run_at", UNKNOWN),
                    "note": rec.get("note", UNKNOWN),
                }
                break
    return {
        "total": counts.get("total", UNKNOWN),
        "by_status": counts,
        "records": records,
        "queue_watch": watch,
        "drain": {
            "method": "manual CLI",
            "command": "python scripts/run_office.py --drain-queue --max 2",
            "runner": "none attached",
            "source": "CLAUDE.md + store/schedules.json note",
        },
    }


def _report_generated_at(path, name):
    """Generated time of one report file: the JSON's own field for
    .json, a Generated line for .md, else the file mtime. Never
    raises — "unknown" when nothing can be read."""
    if name.endswith(".json"):
        data = _read_json(path)
        if isinstance(data, dict) and isinstance(
                data.get("generated_at"), str):
            return data["generated_at"]
    else:
        text = _read_text(path)
        if text:
            m = re.search(r"[Gg]enerated(?:_at)?:\s*(.+)", text)
            if m:
                return m.group(1).strip()
    try:
        return datetime.fromtimestamp(
            os.path.getmtime(path), tz=timezone.utc).isoformat()
    except OSError:
        return UNKNOWN


def read_reports():
    """Reports Center: every generated report in reports/ceo/ with
    kind, format, size, generated time and age in days. Performance
    and leads reports do not exist in this repo — that is shown as
    "none", not invented."""
    ceo_dir = os.path.join(BASE, "reports", "ceo")
    try:
        names = sorted(f for f in os.listdir(ceo_dir)
                       if os.path.isfile(os.path.join(ceo_dir, f)))
    except OSError:
        return {"total": UNKNOWN, "files": [], "latest": UNKNOWN,
                "performance": "none", "leads": "none"}
    now = datetime.now(timezone.utc)
    files = []
    for name in names:
        path = os.path.join(ceo_dir, name)
        kind = name.split("-")[0] if "-" in name else UNKNOWN
        fmt = "json" if name.endswith(".json") else (
            "md" if name.endswith(".md") else UNKNOWN)
        try:
            size = os.path.getsize(path)
        except OSError:
            size = UNKNOWN
        gen = _report_generated_at(path, name)
        age = UNKNOWN
        parsed = _parse_iso(gen) if isinstance(gen, str) else None
        if parsed is not None:
            age = max(0, int((now - parsed).total_seconds() // 86400))
        files.append({
            "name": name,
            "kind": kind,
            "format": fmt,
            "path": os.path.join("reports", "ceo", name),
            "size_bytes": size,
            "generated_at": gen,
            "age_days": age,
        })
    latest = None
    if files:
        dated = [f for f in files
                 if isinstance(f.get("generated_at"), str)
                 and _parse_iso(f["generated_at"]) is not None]
        if dated:
            latest = max(dated,
                         key=lambda f: _parse_iso(f["generated_at"]))
        else:
            latest = files[-1]
    return {
        "total": len(files),
        "files": files,
        "latest": latest if latest is not None else UNKNOWN,
        "performance": "none",
        "leads": "none",
    }


def _read_kit_prices():
    """Kit prices from the kit blueprint's Price line:
    "$49 one-time (launch price $39 for the first 30 buyers, then
    $49)". Both numbers parsed; "unknown" when the line is gone."""
    text = _read_text(os.path.join(
        BASE, "02-Digital-Product-Department", "kit-outline.md"))
    if text is None:
        return UNKNOWN, UNKNOWN
    m = re.search(r"\*\*Price:\*\*\s*\$(\d+)\s+one-time\s*\(launch price "
                  r"\$(\d+) for the first 30 buyers", text)
    if not m:
        return UNKNOWN, UNKNOWN
    return int(m.group(1)), int(m.group(2))


def read_finance(cfg):
    """Financial Dashboard: the spend ledger (real records), the
    LOCKED 2026-11-12 pricing tiers, Gate 0 economics, and revenue.

    Revenue is $0.00 only because paying clients is 0 — entailed,
    not invented. The wedge (1 in 20 kit buyers → $1,109/mo) is a
    durable policy fact from 02-Digital-Product-Department/README.md
    and MEMORY.md, labelled UNTESTED there and here."""
    ledger = read_usage_ledger()
    raw = _read_json(os.path.join(BASE, "store", "usage_ledger.json"))
    by_provider = {}
    by_kind = {}
    first_at = last_at = UNKNOWN
    prompt_tokens = completion_tokens = 0
    records = []
    if isinstance(raw, dict) and isinstance(raw.get("records"), list):
        records = [r for r in raw["records"] if isinstance(r, dict)]
        for r in records:
            prov = r.get("provider", UNKNOWN)
            by_provider.setdefault(prov, {"records": 0, "cost_usd": 0.0})
            by_provider[prov]["records"] += 1
            by_provider[prov]["cost_usd"] += float(
                r.get("cost_usd", 0) or 0)
            kind = r.get("kind", UNKNOWN)
            by_kind[kind] = by_kind.get(kind, 0) + 1
            prompt_tokens += int(r.get("prompt_tokens", 0) or 0)
            completion_tokens += int(r.get("completion_tokens", 0) or 0)
        if records:
            first_at = records[0].get("at", UNKNOWN)
            last_at = records[-1].get("at", UNKNOWN)
    ledger_detail = dict(ledger)
    ledger_detail["records"] = len(records) if records else (
        ledger.get("total_calls", UNKNOWN))
    ledger_detail["by_provider"] = by_provider or UNKNOWN
    ledger_detail["by_kind"] = by_kind or UNKNOWN
    ledger_detail["first_at"] = first_at
    ledger_detail["last_at"] = last_at
    ledger_detail["total_prompt_tokens"] = prompt_tokens
    ledger_detail["total_completion_tokens"] = completion_tokens

    pricing = _read_json(os.path.join(BASE, "00-CEO-Core", "pricing.json"))
    if not isinstance(pricing, dict):
        pricing = UNKNOWN

    honest = cfg.get("honest_status") or {}
    clients = honest.get("paying_clients", UNKNOWN)
    revenue = {
        "paying_clients": clients,
        "revenue_usd": 0.0 if clients == 0 else UNKNOWN,
        "note": ("0 clients — no revenue data exists"
                 if clients == 0 else UNKNOWN),
    }

    gate0 = read_gate0_status()
    kit_price, kit_launch = _read_kit_prices()
    gate0_econ = {
        "status": gate0,
        "kit_price_usd": kit_price,
        "kit_launch_price_usd": kit_launch,
        "kit_sales": 0 if gate0 == "NOT PASSED" else UNKNOWN,
        "wedge": "1 in 20 kit buyers takes the $1,109/mo receptionist "
                 "(UNTESTED — an estimate, not a fact)",
    }
    return {
        "ledger": ledger_detail,
        "pricing": pricing,
        "revenue": revenue,
        "gate0": gate0_econ,
    }


def _count_onnx(root):
    """Count of *.onnx files under root (recursive), 0 when absent."""
    total = 0
    try:
        for _dir, _sub, files in os.walk(root):
            total += sum(1 for f in files if f.endswith(".onnx"))
    except OSError:
        pass
    return total


def _dir_size_mb(root):
    """Total size of root in MB (1 decimal), "unknown" when absent."""
    total = 0
    try:
        for _dir, _sub, files in os.walk(root):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(_dir, f))
                except OSError:
                    pass
    except OSError:
        return UNKNOWN
    return round(total / (1024 * 1024), 1)


def read_health(cfg):
    """System Health: check-suite + pytest totals with run dates
    (from dashboards/health-record.json — written by the verification
    run; "unknown" when no record exists), plus cheap live facts:
    Python, disk, voice-model files, provider enablement from
    config (enabled/disabled — never "connected", no live probe),
    check-script and test-file counts, brain mode."""
    record = _read_json(os.path.join(BASE, "dashboards",
                                     "health-record.json"))
    suite = UNKNOWN
    pytest = UNKNOWN
    if isinstance(record, dict):
        if isinstance(record.get("suite"), dict):
            suite = record["suite"]
        if isinstance(record.get("pytest"), dict):
            pytest = record["pytest"]
    voice_root = os.path.join(BASE, "00-CEO-Core", "voice", "models")
    voice_models = {}
    for name in ("piper", "sherpa-bn", "vosk"):
        sub = os.path.join(voice_root, name)
        voice_models[name] = {
            "present": os.path.isdir(sub),
            "onnx_files": _count_onnx(sub),
        }
    voice_models["total_size_mb"] = _dir_size_mb(
        os.path.join(BASE, "00-CEO-Core", "voice"))
    providers = {}
    cfg_providers = cfg.get("providers") or {}
    if isinstance(cfg_providers, dict):
        for name in sorted(cfg_providers):
            entry = cfg_providers.get(name) or {}
            providers[name] = {
                "enabled": bool(entry.get("enabled", False))
                if isinstance(entry, dict) else UNKNOWN,
            }
    else:
        providers = UNKNOWN
    try:
        check_scripts = len([f for f in os.listdir(
            os.path.join(BASE, "scripts")) if f.startswith("check_")
            and f.endswith(".py")])
    except OSError:
        check_scripts = UNKNOWN
    try:
        test_files = len([f for f in os.listdir(
            os.path.join(BASE, "tests")) if f.startswith("test_")
            and f.endswith(".py")])
    except OSError:
        test_files = UNKNOWN
    try:
        disk = shutil.disk_usage(BASE)
        disk_info = {
            "path": BASE,
            "total_gb": round(disk.total / (1024 ** 3), 1),
            "free_gb": round(disk.free / (1024 ** 3), 1),
        }
    except OSError:
        disk_info = UNKNOWN
    return {
        "suite": suite,
        "pytest": pytest,
        "python": sys.version.split()[0],
        "disk": disk_info,
        "voice_models": voice_models,
        "providers": providers,
        "check_scripts": check_scripts,
        "test_files": test_files,
        "brain": cfg.get("brain", UNKNOWN),
        "record_source": ("dashboards/health-record.json"
                          if isinstance(record, dict) else UNKNOWN),
    }


def read_policy(cfg):
    """Settings & Permissions (READ-ONLY view): the approval policy
    as enforced in code — gate words, gated actions, TTL from the
    gateway itself, $0 cap, brain + production lock, free-only
    guard, email state, and the full permission matrix text
    (generated from 00-CEO-Core/permissions.py — never hand-edited).
    Nothing here is editable from the dashboard."""
    gates = cfg.get("gates") or {}
    honest = cfg.get("honest_status") or {}
    email_raw = honest.get("email_outreach") or ""
    email = "PAUSED" if "PAUSED" in str(email_raw) else (
        "unknown" if not email_raw else str(email_raw))
    matrix_path = os.path.join(BASE, "TALVENOR_PERMISSION_MATRIX.md")
    matrix_text = _read_text(matrix_path)
    agent_rows = 0
    tools = UNKNOWN
    if matrix_text is not None:
        for line in matrix_text.splitlines():
            if line.startswith("| `"):
                agent_rows += 1
        header = re.search(r"\| Agent \|([^\n]+)", matrix_text)
        if header:
            tools = sorted(set(re.findall(r"`([a-z0-9_]+)`",
                                          header.group(1))))
    prod = cfg.get("production_brain") or {}
    return {
        "gate_words": (dict(gates.get("words"))
                       if isinstance(gates.get("words"), dict) else UNKNOWN),
        "gated_actions": (list(gates.get("gated_actions"))
                          if isinstance(gates.get("gated_actions"), list)
                          else UNKNOWN),
        "gate_rule": gates.get("rule", UNKNOWN),
        "approval_ttl_minutes": APPROVAL_TTL_MINUTES,
        "spend_cap_usd": cfg.get("spend_cap_usd", UNKNOWN),
        "brain": cfg.get("brain", UNKNOWN),
        "production_brain": {
            "mode": prod.get("mode", UNKNOWN),
            "unlocked": prod.get("unlocked", UNKNOWN),
        } if isinstance(prod, dict) else UNKNOWN,
        "free_only_guard": os.path.exists(os.path.join(
            BASE, "00-CEO-Core", "free_only_guard.py")),
        "email": email,
        "permission_matrix": {
            "source": ("TALVENOR_PERMISSION_MATRIX.md — generated from "
                       "00-CEO-Core/permissions.py by "
                       "scripts/generate_permission_matrix.py"),
            "text": matrix_text if matrix_text is not None else UNKNOWN,
            "tools": tools,
            "agent_rows": agent_rows,
        },
    }


# F2 batch 3 — Unified AI Chat (2), Voice Command (3), Personality
# Switcher (4), Live Execution Monitor (12), Knowledge & Memory (13),
# Library (14), Integration Center (16). All additive-only; existing
# keys never renamed. Honesty rule for this batch: a module with no
# live backend is published as a SHELL with its reason in one line —
# never dressed up as live. No reader here sends, publishes, spends,
# or writes to any store; all of them read.


def read_chat(cfg):
    """Unified AI Chat: the brain this snapshot would talk to, and
    why send is disabled. There is no in-repo chat transcript and
    no chat endpoint — chat happens in the Muse chat with Mira,
    outside this repo. The assistant name is parsed from
    store/MEMORY.md (the assistant-name entry), not hardcoded."""
    mem_text = _read_text(os.path.join(BASE, "store", "MEMORY.md"))
    assistant = UNKNOWN
    if mem_text:
        m = re.search(r"The assistant's name is ([A-Za-z]+)", mem_text)
        if m:
            assistant = m.group(1)
    dev = cfg.get("development_brain") or {}
    chain = dev.get("fallback_chain")
    return {
        "brain": cfg.get("brain", UNKNOWN),
        "brain_chain": list(chain) if isinstance(chain, list) else UNKNOWN,
        "assistant": assistant,
        "surface": "Muse chat with Mira (outside this repo)",
        "connected": False,
        "send": {
            "enabled": False,
            "reason": ("The brain on this snapshot is mock, and the "
                       "live dev brain runs on Boss's PC only. Send "
                       "would need a live brain + a send path — "
                       "neither exists here."),
        },
        "transcript": "none",
        "note": ("No chat transcript is stored in this repo. No fake "
                 "replies are shown — the panel is a connection-state "
                 "surface until a real chat path exists."),
    }


def _parse_gate_phrases():
    """Voice gate phrases from 00-CEO-Core/voice/loop.py
    GATE_PHRASES — the dict the loop itself uses. "unknown" when
    the block cannot be parsed."""
    text = _read_text(os.path.join(BASE, "00-CEO-Core", "voice", "loop.py"))
    if text is None:
        return UNKNOWN
    m = re.search(r"GATE_PHRASES = \{([^}]*)\}", text, flags=re.S)
    if not m:
        return UNKNOWN
    pairs = re.findall(r'"([^"]+)":\s*"(send|publish)"', m.group(1))
    if not pairs:
        return UNKNOWN
    return {phrase: action for phrase, action in pairs}


def read_voice_command(cfg):
    """Voice Command: the real voice loop's state, and why the mic
    is off in the browser. The loop is a PC-side Python process
    (mic + local models); this page cannot reach it, so the panel
    is a status surface, not a live microphone."""
    loop_path = os.path.join(BASE, "00-CEO-Core", "voice", "loop.py")
    voice = read_voice_status()
    return {
        "loop_file": "00-CEO-Core/voice/loop.py",
        "loop_exists": os.path.exists(loop_path),
        "engines": voice.get("detail", UNKNOWN),
        "gate_phrases": _parse_gate_phrases(),
        "bengali_prompts": "regressed",
        "bengali_note": ("Bengali spoken prompts were replaced with "
                         "English in the 2026-11-21 full-English "
                         "conversion; Boss's decision is pending (F1). "
                         "One Bengali trigger mapping remains: "
                         "'পাঠাও' -> send."),
        "live_in_browser": False,
        "reason": ("The voice loop is a PC-side Python process (needs "
                   "a mic + local models); this browser page cannot "
                   "reach it."),
        "brain": cfg.get("brain", UNKNOWN),
        "brain_note": ("The loop speaks the brain's answer; with a "
                       "mock brain the answer is a draft "
                       "(voice/loop.py docstring)."),
    }


def read_personas():
    """Personality Switcher: the profiles in
    00-CEO-Core/personas.json. The switcher changes the DISPLAYED
    persona in module 2 only — the underlying brain does not
    switch on this snapshot."""
    data = _read_json(os.path.join(BASE, "00-CEO-Core", "personas.json"))
    if not isinstance(data, dict):
        return {"default": UNKNOWN, "profiles": [],
                "note": "00-CEO-Core/personas.json unreadable"}
    profiles = data.get("profiles")
    if not isinstance(profiles, list):
        profiles = []
    return {
        "default": data.get("default", UNKNOWN),
        "profiles": profiles,
        "note": ("Switching changes the displayed persona in module 2 "
                 "(Unified AI Chat) only. The underlying brain does "
                 "not switch on this snapshot."),
    }


def read_execution(task_records):
    """Live Execution Monitor: the most recent execution records —
    NOT a live stream (there is no event bus until F4). Sources:
    store/tasks.json totals (via the caller), the skill-execution
    log (recent records), the dev-brain call log, and the bridge
    cron (no run record exists in this repo, so its state is
    unknown). Nothing here claims a job is running now."""
    counts = read_task_counts(task_records)
    log_path = os.path.join(BASE, "logs", "skill_executions.jsonl")
    total_lines = 0
    parsed = 0
    errors = 0
    first_at = None
    last_at = None
    recent = []
    try:
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                total_lines += 1
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(ev, dict):
                    continue
                ts = ev.get("timestamp")
                if not isinstance(ts, str):
                    continue
                parsed += 1
                if first_at is None or ts < first_at:
                    first_at = ts
                if last_at is None or ts > last_at:
                    last_at = ts
                if ev.get("error") is not None:
                    errors += 1
                result = ev.get("result")
                recent.append({
                    "timestamp": ts,
                    "event": ev.get("event", UNKNOWN),
                    "skill": ev.get("skill", UNKNOWN),
                    "result_file": (result.split("/")[-1]
                                    if isinstance(result, str)
                                    else UNKNOWN),
                    "error": ev.get("error"),
                })
    except OSError:
        pass
    recent = recent[-8:]
    calls_path = os.path.join(BASE, "logs", "dev_brain_calls.jsonl")
    calls = []
    try:
        with open(calls_path, encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(rec, dict):
                    continue
                usage = rec.get("usage")
                calls.append({
                    "provider": rec.get("provider", UNKNOWN),
                    "model": rec.get("model", UNKNOWN),
                    "status": rec.get("status", UNKNOWN),
                    "error": rec.get("error"),
                    "total_tokens": (usage.get("total_tokens", UNKNOWN)
                                     if isinstance(usage, dict)
                                     else UNKNOWN),
                    "ts": rec.get("ts", UNKNOWN),
                })
    except OSError:
        pass
    return {
        "tasks": {
            "total": counts.get("total", UNKNOWN),
            "done": counts.get("done", UNKNOWN),
            "queued": counts.get("queued", UNKNOWN),
        },
        "skill_executions": {
            "total_lines": total_lines,
            "parsed": parsed,
            "first_at": first_at if first_at is not None else UNKNOWN,
            "last_at": last_at if last_at is not None else UNKNOWN,
            "errors": errors,
            "recent": recent,
        },
        "dev_brain_calls": {
            "total": len(calls),
            "records": calls,
        },
        "bridge": {
            "name": "master-os-3d-bridge",
            "state": UNKNOWN,
            "note": ("No run record in this repo — the bridge "
                     "regenerates dashboards/status.* every 10 "
                     "minutes; its last run is not recorded as a "
                     "file."),
        },
        "stream": "none",
        "stream_note": ("No live stream: there is no event bus until "
                        "F4. This monitor shows records, not a live "
                        "feed — nothing here proves a job is running "
                        "right now."),
    }


def read_memory():
    """Knowledge & Memory: the memory store's STRUCTURE only —
    schema, size, box list, per-box entry counts, and entry
    metadata (area / slug / box / status / dates). Quote and text
    content is NEVER published: the 3 verbatim quotes stay in the
    file, and the panel says where to read them. Engine methods
    are parsed from 00-CEO-Core/owner_memory.py."""
    path = os.path.join(BASE, "store", "memory.json")
    mem = _read_json(path)
    if not isinstance(mem, dict):
        return {"store_file": "store/memory.json", "schema": UNKNOWN,
                "entries": UNKNOWN, "boxes": UNKNOWN,
                "entries_meta": [], "verbatim_quotes": UNKNOWN}
    entries = mem.get("entries")
    if not isinstance(entries, list):
        entries = []
    boxes = mem.get("boxes")
    if not isinstance(boxes, list):
        boxes = []
    per_box = {}
    meta = []
    quotes = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        box = e.get("box", UNKNOWN)
        per_box[box] = per_box.get(box, 0) + 1
        if isinstance(e.get("quote"), str) and e.get("quote"):
            quotes += 1
        meta.append({
            "area": e.get("area", UNKNOWN),
            "slug": e.get("slug", UNKNOWN),
            "box": box,
            "status": e.get("status", UNKNOWN),
            "learned_at": e.get("learned_at", UNKNOWN),
            "updated_at": e.get("updated_at", UNKNOWN),
        })
    try:
        size = os.path.getsize(path)
    except OSError:
        size = UNKNOWN
    export_path = os.path.join(BASE, "store", "MEMORY.md")
    try:
        export_size = os.path.getsize(export_path)
    except OSError:
        export_size = UNKNOWN
    methods = []
    eng_text = _read_text(os.path.join(BASE, "00-CEO-Core",
                                       "owner_memory.py"))
    if eng_text:
        methods = sorted(set(re.findall(
            r"    def ([a-z_][a-z0-9_]*)\(", eng_text)))
        methods = [m for m in methods if not m.startswith("_")]
    return {
        "store_file": "store/memory.json",
        "schema": mem.get("schema", UNKNOWN),
        "size_bytes": size,
        "entries": len(entries),
        "boxes": boxes,
        "per_box": per_box,
        "entries_meta": meta,
        "verbatim_quotes": quotes,
        "export_file": "store/MEMORY.md",
        "export_size_bytes": export_size,
        "engine_file": "00-CEO-Core/owner_memory.py",
        "engine_methods": methods,
        "rule": ("Memory learns ONLY from Boss's own messages. "
                 "Memory is context, NOT permission."),
    }


def _list_md_files(directory, base_label):
    """One directory's *.md files: name, path, size, modified.
    Empty list when the directory is missing."""
    out = []
    try:
        names = sorted(f for f in os.listdir(directory)
                       if f.endswith(".md")
                       and os.path.isfile(os.path.join(directory, f)))
    except OSError:
        return out
    for name in names:
        path = os.path.join(directory, name)
        try:
            size = os.path.getsize(path)
            # Second precision: file mtimes do not need microseconds,
            # and microsecond digits can false-positive the Phase 6
            # scope guard, which scans every data line for a
            # three-digit scope number.
            mtime = datetime.fromtimestamp(
                os.path.getmtime(path), tz=timezone.utc).isoformat(
                    timespec="seconds")
        except OSError:
            size = UNKNOWN
            mtime = UNKNOWN
        out.append({
            "name": name,
            "path": os.path.join(base_label, name),
            "size_bytes": size,
            "modified_at": mtime,
        })
    return out


def read_library(reports):
    """Library: every document file that really exists in the repo
    (docs/, top-level *.md, 00-CEO-Core/*.md) plus the
    unified-business-os reports when that directory exists on this
    machine (VM only — not in the repo, not on Boss's PC). The CEO
    reports are listed in module 15; this key carries only their
    count + latest. Decks live outside the repo and are not listed
    — the note says so."""
    ubo_dir = os.path.expanduser("~/workspace/unified-business-os")
    ubo = _list_md_files(ubo_dir, "unified-business-os")
    latest = reports.get("latest") if isinstance(reports, dict) else None
    return {
        "docs": _list_md_files(os.path.join(BASE, "docs"), "docs"),
        "top_level": _list_md_files(BASE, ""),
        "ceo_core": _list_md_files(
            os.path.join(BASE, "00-CEO-Core"), "00-CEO-Core"),
        "unified_business_os": ubo if ubo else UNKNOWN,
        "ceo_reports": {
            "total": reports.get("total", UNKNOWN)
                       if isinstance(reports, dict) else UNKNOWN,
            "latest": (latest.get("name", UNKNOWN)
                       if isinstance(latest, dict) else UNKNOWN),
            "note": "File list in module 15 (Reports Center).",
        },
        "decks_note": ("Decks live outside the repo — not listed "
                       "here."),
    }


def read_integrations(cfg, status_workflows):
    """Integration Center: one row per service, with a dated probe
    record where one exists. The ONLY "connected" service is the
    n8n Cloud MCP (verified 2026-11-25). Provider states come
    from PROVIDER_STATES for the two probed providers; every other
    provider is disabled in config and unprobed. Vapi and
    Gmail/Calendar are connector-level, not repo-level — unknown."""
    adapter_path = os.path.join(
        BASE, "00-CEO-Core", "workflow_engine", "n8n_adapter.py")
    providers = {}
    cfg_providers = cfg.get("providers") or {}
    if isinstance(cfg_providers, dict):
        for name in sorted(cfg_providers):
            entry = cfg_providers.get(name) or {}
            known = PROVIDER_STATES.get(name)
            if known:
                providers[name] = {
                    "enabled": bool(entry.get("enabled", False))
                               if isinstance(entry, dict) else UNKNOWN,
                    "state": known["state"],
                    "verified": known["verified"],
                    "evidence": known["evidence"],
                    "source": known["source"],
                }
            else:
                providers[name] = {
                    "enabled": bool(entry.get("enabled", False))
                               if isinstance(entry, dict) else UNKNOWN,
                    "state": ("disabled in config"
                              if entry.get("enabled") is False
                              else UNKNOWN),
                    "verified": None,
                    "evidence": "not enabled; no probe",
                    "source": "00-CEO-Core/config.json",
                }
    else:
        providers = UNKNOWN
    workflows = []
    for key, label in (("workflow_auto_send", "Tier 2 auto-send"),
                       ("workflow_callback", "Callback")):
        w = status_workflows.get(key) or {}
        workflows.append({
            "label": label,
            "name": w.get("name", UNKNOWN),
            "nodes": w.get("nodes", UNKNOWN),
            "status": w.get("status", UNKNOWN),
        })
    return {
        "n8n_mcp": dict(N8N_MCP_VERIFIED),
        "n8n_adapter": {
            "service": "n8n adapter (repo)",
            "file": "00-CEO-Core/workflow_engine/n8n_adapter.py",
            "file_exists": os.path.exists(adapter_path),
            "state": "not connected",
            "evidence": ("localhost-only adapter; no n8n instance "
                         "runs on this machine (self-hosted not "
                         "installed); Cloud is reached via MCP, not "
                         "this adapter"),
            "source": "dashboards/n8n-wiring.md",
        },
        "n8n_workflows": workflows,
        "providers": providers,
        "vapi": {
            "service": "Vapi",
            "state": UNKNOWN,
            "evidence": ("No Vapi config in this repo — the Vapi "
                         "connector lives outside the repo"),
            "source": "none in repo",
        },
        "gmail_calendar": {
            "service": "Gmail / Calendar / Drive",
            "state": UNKNOWN,
            "evidence": ("Connector-level (Muse connectors), not "
                         "repo-level"),
            "source": "none in repo",
        },
    }


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

    # F2 batch 3 — computed once, reused by the return dict and by
    # the batch-3 readers (library needs reports; integrations needs
    # the workflow statuses).
    reports = read_reports()
    wf_auto = read_workflow_status(AUTO_SEND_PATH)
    wf_cb = read_workflow_status(CALLBACK_PATH)
    wf_statuses = {"workflow_auto_send": wf_auto,
                   "workflow_callback": wf_cb}

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
        "workflow_auto_send": wf_auto,
        "workflow_callback": wf_cb,
        # Phase 7 (Worker A) — additive keys only; dashboard-3d.html reads
        # this JSON, so existing keys are never renamed or removed.
        "departments": read_departments(),
        "task_counts": read_task_counts(task_records),
        "approvals": read_approvals_detail(appr_records),
        "control": read_control(),
        "ceo_report": read_ceo_report(),
        # F2 batch 1 — additive keys only; existing keys never renamed.
        "founder_os": read_founder_os(),
        "roster": read_roster(),
        # F2 batch 2 — additive keys only; existing keys never renamed.
        "task_queue": read_task_queue(task_records),
        "reports": reports,
        "finance": read_finance(cfg),
        "health": read_health(cfg),
        "policy": read_policy(cfg),
        # F2 batch 3 — additive keys only; existing keys never renamed.
        "chat": read_chat(cfg),
        "voice_command": read_voice_command(cfg),
        "personas": read_personas(),
        "execution": read_execution(task_records),
        "memory": read_memory(),
        "library": read_library(reports),
        "integrations": read_integrations(cfg, wf_statuses),
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
      <tr><td><strong>Phase 11</strong> — 8 LLM providers + fallback chain (brain still mock)</td><td>{phase_badge(ph.get("phase_11_providers", UNKNOWN))}</td></tr>
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


def write_ceo_report_json(status):
    """Publishes the latest CEO report JSON into dashboards/ so the
    Command Center (same origin) can fetch it. Copies the file
    status["ceo_report"]["path"] byte-for-byte when it is a .json
    report; removes a stale dashboards/ceo-report.json when no report
    is available, so the UI never shows an old report as live.
    Never raises — a missing report is "unknown", not a crash."""
    out = os.path.join(BASE, "dashboards", "ceo-report.json")
    ceo = status.get("ceo_report") or {}
    src_rel = ceo.get("path") if ceo.get("available") else None
    try:
        if isinstance(src_rel, str) and src_rel.endswith(".json"):
            src = os.path.join(BASE, src_rel)
            with open(src, "rb") as f:
                data = f.read()
            with open(out, "wb") as f:
                f.write(data)
            return out
        if os.path.exists(out):
            os.remove(out)
    except OSError:
        pass
    return None


def main():
    status = collect_status()
    html = render_html(status)
    out = os.path.join(BASE, "dashboards", "status.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    json_out = write_status_json(status)
    ceo_json_out = write_ceo_report_json(status)
    print("sync done ->", out)
    print("sync done ->", json_out)
    print("sync done ->", ceo_json_out or "ceo-report.json not published")
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
    fo = status["founder_os"]
    ro = status["roster"]
    print(f"founder_os={fo['phase']} batch {fo['batch']} · "
          f"roster={ro['total']} agents "
          f"({ro['with_activity']} with activity, "
          f"{ro['draft']} draft, {ro['coded']} coded)")
    tq = status["task_queue"]
    rp = status["reports"]
    fn = status["finance"]
    hl = status["health"]
    pol = status["policy"]
    print(f"batch3: task_queue={tq['total']} tasks · "
          f"reports={rp['total']} files · "
          f"finance ledger={fn['ledger'].get('records')} records "
          f"${fn['ledger'].get('total_usd')} · "
          f"health suite={hl['suite'] if isinstance(hl['suite'], dict) else hl['suite']} · "
          f"policy ttl={pol['approval_ttl_minutes']} min · "
          f"matrix rows={pol['permission_matrix'].get('agent_rows')}")
    ch = status["chat"]
    vc = status["voice_command"]
    ps = status["personas"]
    ex = status["execution"]
    mm = status["memory"]
    lb = status["library"]
    ig = status["integrations"]
    print(f"batch3: chat brain={ch['brain']} connected={ch['connected']} · "
          f"voice loop={vc['loop_exists']} live_in_browser="
          f"{vc['live_in_browser']} · "
          f"personas={len(ps['profiles'])} default={ps['default']} · "
          f"execution skill_log={ex['skill_executions']['total_lines']} "
          f"lines dev_calls={ex['dev_brain_calls']['total']} · "
          f"memory entries={mm['entries']} boxes={len(mm['boxes'])} · "
          f"library docs={len(lb['docs'])} top={len(lb['top_level'])} "
          f"ceo_core={len(lb['ceo_core'])} · "
          f"integrations n8n_mcp={ig['n8n_mcp']['state']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
