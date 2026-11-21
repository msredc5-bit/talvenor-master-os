"""Chief of Staff — Digital Product Department (REAL, Phase 2).

Product: Vet No-Show Recovery Kit — $49 one-time.
For independent US vet clinics: reminder cadence, rebooking script,
waitlist SOP, no-show log + $ tracker, policy template.

Job: read a task coming from the Main CEO Bot and route it to the right
work, return the result as a DRAFT, and hold kit launch / sale back
until Gate 0 has passed.

Gate 0 — hard rule (written in code, fail-closed):
  - Gate 0 = Lemon Squeezy signup test (as a BD individual) — Boss's
    step, still NOT PASSED. The only source for the result:
    02-Digital-Product-Department/gate0-status.md — unless it says
    "Status: PASSED", Gate 0 is not treated as passed.
  - Until Gate 0 passes: the kit cannot be built/sold/launched.
    kit_build returns only the BLUEPRINT (kit-outline.md) — not the kit
    itself. launch_prep gives only a DRAFT checklist — it does not launch.
    If mark_launched / mark_sold is requested, status "blocked-gate0" is
    returned and nothing is written/sold.
  - For gated work (send / publish / spend / delete) the worker is not
    run at all — a PENDING request is written to the ApprovalGateway.
  - This Chief never sends mail, publishes, spends, or deletes. The sale
    count is never invented — sales are 0.

Kit blueprint: 02-Digital-Product-Department/kit-outline.md
PA clinic list: 02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv
Payment rails: Lemon Squeezy (after Gate 0), backup Polar, Gumroad
(individual). Etsy is closed for Bangladesh — never in the plan.

Wedge (UNTESTED): if 1 of 20 kit buyers takes the receptionist,
~$11K/mo — an estimate, not a fact, never written as a fact.
"""

import csv
import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# --- paths -----------------------------------------------------------------
MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(MASTER_OS_DIR, "00-CEO-Core")
DEPT_DIR = os.path.join(MASTER_OS_DIR, "02-Digital-Product-Department")

sys.path.insert(0, CEO_CORE_DIR)

from human_approval_gateway import ApprovalGateway  # noqa: E402
from brain import BrainFactory  # noqa: E402

DEPARTMENT = "digital-product"
BUSINESS = "Vet No-Show Recovery Kit"
PRICE_USD_ONE_TIME = 49
LAUNCH_PRICE_USD_ONE_TIME = 39  # for the first 30 buyers (research §4.1)
KIT_BLUEPRINT_PATH = os.path.join(DEPT_DIR, "kit-outline.md")
GATE0_STATUS_PATH = os.path.join(DEPT_DIR, "gate0-status.md")
PA_LIST_PATH = os.path.join(DEPT_DIR, "pa-vet-list", "pa-vet-clinics.csv")

STORE_DIR = os.path.join(MASTER_OS_DIR, "store")
DEFAULT_TASKS_PATH = os.path.join(STORE_DIR, "tasks.json")
DEFAULT_APPROVALS_PATH = os.path.join(STORE_DIR, "approvals.json")

# The kit's 6 parts (from research report §4.1 — the blueprint's structure)
KIT_PARTS = [
    "reminder-cadence-pack",   # T-72h / T-24h / T-2h SMS + email + call script
    "same-day-rebooking",      # on-the-spot rebook script when a no-show / late-cancel happens
    "waitlist-fill-sop",       # one-page SOP for filling an empty slot + call script
    "no-show-log-tracker",     # Sheets: no-show log + $ tracker (formula)
    "deposit-policy-template", # deposit / no-show policy (with attorney-review note)
    "front-desk-quick-card",   # one-page desk card, 5 lines
]

# task type -> (handler, gate word for the OUTPUT's onward use)
# gate word = the Boss word needed to send/use the output.
# None = the draft itself is safe, no gate.
ROUTING = {
    "kit_build": ("blueprint", "ok"),
    "clinic_research": ("pa-list", None),
    "gate0_check": ("gate0-status", None),
    "launch_prep": ("launch-checklist-draft", "go"),
}

# Phase 7 — NEW task types only (section agents, sections/<section>/agents/).
# task type -> (agent file, agent class, gate word for the OUTPUT's onward use)
# Existing 4 ROUTING types unchanged — these 3 are checked alongside them.
SECTION_ROUTING = {
    "kit_sales": ("sections/sales/agents/kit_sales.py", "KitSalesAgent", "send"),
    "kit_qa": ("sections/product/agents/kit_qa.py", "KitQAAgent", "ok"),
    "support_draft": ("sections/support/agents/support_drafter.py", "SupportDrafterAgent", "send"),
}

# Sweep 2026-11-21 — the 4 legacy ROUTING types now ALSO run through their
# section agent first (same files the skill files name). The agent's output
# is attached to the result (agent_status / agent_output); the Chief's
# outward contract — status / output / handler / gate — is UNCHANGED
# (check_phase2.py asserts it: kit_build -> draft-ready blueprint,
# clinic_research handler "pa-list", gate0_check -> draft-ready).
# task type -> (agent file, agent class)
LEGACY_SECTION_ROUTING = {
    "kit_build": ("sections/product/agents/kit_builder.py", "KitBuilderAgent"),
    "clinic_research": ("sections/research/agents/clinic_researcher.py", "ClinicResearcherAgent"),
    "gate0_check": ("sections/finance/agents/payment_rails_checker.py", "PaymentRailsCheckerAgent"),
    "launch_prep": ("sections/launch/agents/launch_manager.py", "LaunchManagerAgent"),
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_gate0_status():
    """The only source for Gate 0: gate0-status.md.

    Reads the file's "Status:" line — PASSED only if the value starts
    with "PASSED", otherwise NOT PASSED (fail-closed). The word "PASSED"
    in an explanation line does not count — only the Status line is the
    source. If the file is missing/unreadable, also NOT PASSED.
    """
    try:
        with open(GATE0_STATUS_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (FileNotFoundError, OSError):
        return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
                "note": "gate0-status.md could not be read — fail-closed: treated as NOT PASSED."}
    for line in lines:
        stripped = line.strip().lstrip("*").strip()
        if stripped.startswith("Status:"):
            value = stripped[len("Status:"):].strip().lstrip("*").strip()
            if value.startswith("PASSED"):
                return {"status": "PASSED", "source": GATE0_STATUS_PATH,
                        "note": "gate0-status.md says Status: PASSED."}
            return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
                    "note": "Gate 0 has not passed — the Lemon Squeezy signup test is Boss's step, still pending."}
    return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
            "note": "No Status line found in gate0-status.md — fail-closed: treated as NOT PASSED."}


def gate0_passed():
    return read_gate0_status()["status"] == "PASSED"


def _read_kit_blueprint():
    """Reads kit-outline.md — returns the list of parts if it is missing."""
    try:
        with open(KIT_BLUEPRINT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return None


def _read_pa_list():
    """Reads the PA vet list CSV — row count + summary."""
    if not os.path.isfile(PA_LIST_PATH):
        return {"rows": 0, "path": PA_LIST_PATH, "exists": False}
    with open(PA_LIST_PATH, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {"rows": len(rows), "path": PA_LIST_PATH, "exists": True,
            "cities": sorted({r.get("city", "") for r in rows if r.get("city")}),
            "target_rows": 100}


def _log_task(record, tasks_path=None):
    """Appends every routed task to store/tasks.json. Never deletes
    another department's entry — read-modify-write."""
    path = tasks_path or DEFAULT_TASKS_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    records.append(record)
    payload = {"schema": "tasks-v1", "records": records}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return record


def handle_task(task, tasks_path=None, approvals_path=None):
    """Runs one digital-product task coming from the Main CEO Bot.

    task = {
      "type": "kit_build" | "clinic_research" | "gate0_check" | "launch_prep",
      "title": "...",
      "payload": {...},           # input
      "gated_action": "send" | "publish" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — approval taken earlier),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "blocked-gate0" | "pending-approval"
              | "route-only" | "error", ...}
    - If mark_launched / mark_sold is requested, Gate 0 is checked — if it
      has not passed, status is "blocked-gate0" and nothing is recorded as
      launched/sold.
    - If a gated_action is present, the worker is not run at all — PENDING
      in the gateway.
    - The result is only DRAFT / BLUEPRINT — this Chief does not build or
      sell the kit.
    """
    title = task.get("title", "")
    task_type = task.get("type")
    payload = task.get("payload") or {}
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")

    # 1. Launch / sale claim — check Gate 0, block if it has not passed.
    if payload.get("mark_launched") or payload.get("mark_sold"):
        gate0 = read_gate0_status()
        result = {
            "status": "blocked-gate0",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "gate0": gate0,
            "note": "Gate 0 has not passed — the kit cannot be marked as launched/sold. "
                    "No sale was recorded, sales are still 0.",
            "draft_only": True,
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": "blocked-gate0",
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 2. Gated action — the worker cannot run, it must be held for approval.
    if gated_action:
        gateway = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        approval_id = task.get("approval_id")
        if approval_id and gateway.is_approved(approval_id):
            result = {
                "status": "approved-not-executed",
                "department": DEPARTMENT,
                "task": title,
                "gated_action": gated_action,
                "approval_id": approval_id,
                "note": "Boss approved, but this Chief never sends/publishes/spends/deletes. Boss executes it himself.",
                "draft_only": True,
            }
        else:
            approval = gateway.request(gated_action, title or task_type or "digital-product task", requested_by)
            result = {
                "status": "pending-approval",
                "department": DEPARTMENT,
                "task": title,
                "gated_action": gated_action,
                "approval": approval,
                "note": "Gated action refused — PENDING approval recorded. Nothing was sent/published/spent/deleted.",
                "draft_only": True,
            }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": result["status"],
            "gated_action": gated_action,
            "approval_id": result.get("approval", {}).get("id") or approval_id,
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 3. Task without a type — routing probe only, no work runs.
    if not task_type:
        result = {
            "status": "route-only",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "note": "No task type given — routing probe only, no work ran.",
            "routing_keys": sorted(ROUTING),
            "gate0": read_gate0_status(),
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": None,
            "worker": None,
            "status": "route-only",
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 3b. Phase 7 section agents — NEW task types only (kit_sales, kit_qa,
    #     support_draft). Existing 4 ROUTING types unchanged; gated_action /
    #     mark_launched / mark_sold blocks above already ran first.
    if task_type in SECTION_ROUTING:
        rel_path, agent_class_name, gate_word = SECTION_ROUTING[task_type]
        agent_path = os.path.join(DEPT_DIR, rel_path)
        gate0 = read_gate0_status()
        try:
            spec = importlib.util.spec_from_file_location(
                "products_section_%s" % task_type, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            agent = getattr(module, agent_class_name)()
            brain = BrainFactory.get_brain("agency")
            agent_result = agent.run(task, brain=brain, approvals_path=approvals_path)
        except Exception as exc:  # noqa: BLE001
            result = {
                "status": "error",
                "department": DEPARTMENT,
                "task": title,
                "type": task_type,
                "handler": agent_class_name,
                "error": "%s: %s" % (type(exc).__name__, exc),
                "draft_only": True,
            }
            _log_task({
                "id": uuid.uuid4().hex[:12],
                "department": DEPARTMENT,
                "title": title,
                "type": task_type,
                "worker": agent_class_name,
                "status": "error",
                "logged_at": _now_iso(),
            }, tasks_path=tasks_path)
            return result
        result = {
            "status": agent_result.get("status", "error"),
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "type": task_type,
            "handler": agent_class_name,
            "worker": agent_class_name,
            "output": agent_result.get("output", ""),
            "notes": agent_result.get("notes", ""),
            "mock_brain": agent_result.get("mock_brain", True),
            "gate0": gate0,
            "draft_only": True,
            "gate": gate_word,
            "note": agent_result.get("notes", ""),
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": agent_class_name,
            "status": result["status"],
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 4. Unknown type — admit the error and stop, no invented work.
    if task_type not in ROUTING:
        result = {
            "status": "error",
            "department": DEPARTMENT,
            "task": title,
            "type": task_type,
            "error": f"Unknown task type {task_type!r}. Known: {sorted(ROUTING)}",
        }
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": None,
            "status": "error",
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 5. Real routing — with the Gate 0 status. For a legacy type, the
    #    section agent runs first (LEGACY_SECTION_ROUTING) — the agent's
    #    output is attached to the result, but the legacy output /
    #    status / handler / gate below stay exactly as before.
    handler, gate_word = ROUTING[task_type]
    gate0 = read_gate0_status()

    agent_name = None
    agent_result = None
    if task_type in LEGACY_SECTION_ROUTING:
        agent_rel_path, agent_name = LEGACY_SECTION_ROUTING[task_type]
        agent_path = os.path.join(DEPT_DIR, agent_rel_path)
        try:
            spec = importlib.util.spec_from_file_location(
                "products_legacy_%s" % task_type, agent_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            agent = getattr(module, agent_name)()
            brain = BrainFactory.get_brain("agency")
            agent_result = agent.run(task, brain=brain, approvals_path=approvals_path)
        except Exception as exc:  # noqa: BLE001
            result = {
                "status": "error",
                "department": DEPARTMENT,
                "task": title,
                "type": task_type,
                "handler": handler,
                "agent": agent_name,
                "error": "%s: %s" % (type(exc).__name__, exc),
                "draft_only": True,
            }
            _log_task({
                "id": uuid.uuid4().hex[:12],
                "department": DEPARTMENT,
                "title": title,
                "type": task_type,
                "worker": agent_name,
                "status": "error",
                "logged_at": _now_iso(),
            }, tasks_path=tasks_path)
            return result

    if task_type == "kit_build":
        blueprint = _read_kit_blueprint()
        output = {
            "kit": BUSINESS,
            "price_usd_one_time": PRICE_USD_ONE_TIME,
            "launch_price_usd_one_time": LAUNCH_PRICE_USD_ONE_TIME,
            "parts": KIT_PARTS,
            "blueprint_file": KIT_BLUEPRINT_PATH,
            "blueprint_present": blueprint is not None,
            "blueprint_chars": len(blueprint) if blueprint else 0,
        }
        note = ("BLUEPRINT ONLY — this is the kit's design, not the kit itself. "
                "The kit will not start being built/sold until Gate 0 passes.")
    elif task_type == "clinic_research":
        pa_list = _read_pa_list()
        output = {
            "pa_list": pa_list,
            "note": "PA list aiming for 100 clinics — not complete yet, only verified rows are in it.",
        }
        note = "Clinic list — verified public information only, nothing invented. No clinic has been emailed."
    elif task_type == "gate0_check":
        output = {"gate0": gate0}
        note = "Gate 0's true status — read from gate0-status.md."
    elif task_type == "launch_prep":
        output = {
            "launch_checklist_draft": [
                "Gate 0 passed (does the Lemon Squeezy store open?) — still NOT PASSED",
                "The kit's 6 parts built (Sheets + Docs + script) — not done yet",
                "Cadence checked against AAHA/PetDesk guidance (Gate 1) — not done yet",
                "Lemon Squeezy listing + Gumroad backup listing — not done yet",
                "Sales page — Boss will review before launch",
                "Email 100 clinics, 25 a day (4 days) — email channel is now PAUSED",
            ],
            "launch_blocked": not gate0_passed(),
            "gate0": gate0,
        }
        note = ("DRAFT checklist only — no launch has happened, and it cannot happen. "
                "Launch is blocked until Gate 0 passes.")
    else:  # pragma: no cover — a new key in ROUTING never reaches here
        output = {}
        note = ""

    result = {
        "status": "draft-ready",
        "department": DEPARTMENT,
        "business": BUSINESS,
        "task": title,
        "type": task_type,
        "handler": handler,
        "output": output,
        "gate0": gate0,
        "draft_only": True,
        "gate": gate_word,
        "note": note + (f" Boss's gate word is needed to use the output: '{gate_word}'." if gate_word else ""),
    }
    if agent_result is not None:
        # The section agent really ran — its verdict + output are attached;
        # the legacy fields above did not change.
        result["agent"] = agent_name
        result["agent_status"] = agent_result.get("status")
        result["agent_output"] = agent_result.get("output", "")
        result["agent_notes"] = agent_result.get("notes", "")
    _log_task({
        "id": uuid.uuid4().hex[:12],
        "department": DEPARTMENT,
        "title": title,
        "type": task_type,
        "worker": handler,
        "status": "draft-ready",
        "logged_at": _now_iso(),
    }, tasks_path=tasks_path)
    return result


if __name__ == "__main__":
    print("Products Chief of Staff — REAL (Phase 2). Gate 0:", read_gate0_status()["status"])
    print("Product:", BUSINESS, "- $49 one-time (launch $39 first 30 buyers)")
    print("Routed task types:", ", ".join(sorted(ROUTING)))
    print("Section agents wired (Phase 7 + sweep 2026-11-21):",
          ", ".join(sorted(SECTION_ROUTING) + sorted(LEGACY_SECTION_ROUTING)))
    print("Kit parts:", len(KIT_PARTS), "| PA list target: 100 clinics")
    print("Launch/sale: BLOCKED until Gate 0 passes — this Chief never fakes a sale.")
