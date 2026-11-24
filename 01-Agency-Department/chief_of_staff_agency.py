"""Chief of Staff — Agency Department (REAL, Phase 1).

Talvenor AI Receptionist Agency — Boss's first business, MAIN.

Job: read the task coming from the Main CEO Bot and send it to the real worker of the vendored
engine inside this office, return the result as a DRAFT,
and if it is a gated job (send / publish / spend / delete),
hold it back with ApprovalGateway. Workers are now vendored inside the office
(engine/workers/) — no longer dependent on any outside checkout
(see engine/workers/SOURCE.md).

Rules (written in code):
  - This Chief never sends mail/messages, publishes, spends,
    or deletes. Sending/publishing happens only on Boss's gate word,
    and even that Boss does himself (this system only makes DRAFTs).
  - Email sending PAUSED (Boss's instruction 2026-11-14) — the draft is the final
    word, not even an attempt to send is made.
  - Workers run on BrainFactory's brain — if the "brain" flag in config.json is
    "mock" (DEFAULT, $0), the vendored MockLLMProvider,
    if "live", the vendored MetaSparkProvider. Results are labelled DRAFT / MOCK.
    A live brain only with Boss's separate approval, not here;
    Phase 6 makes no live call (see 00-CEO-Core/brain.py).
  - RetellBuilder: the real name of the engine's DEL worker. But
    Talvenor's live stack is Vapi/Sophia (Boss will not pay money for Retell)
    — so RetellBuilder's output is only a DRAFT build plan,
    never a live build.
  - Phase 2 wiring (2026-11-19): DEPARTMENT_ROUTING — the Chief now calls 8 department
    managers (dept_sales / dept_marketing /
    dept_engineering / dept_operations / dept_strategy / dept_finance /
    dept_quality / dept_innovation). Managers only make a DRAFT of the delegation plan;
    no worker is executed. The manager's task_kind,
    if it is in the payload, is placed at top level (the manager reads task.get
    ("task_kind")); if missing, M1–M4 give an overview, M5–M8
    return "unknown-task" (with a list of known kinds).
  - Skill hook WIRED (2026-11-25, Phase 2 local-first): _handle_task_inner
    loads the skill for a non-gated task AFTER the gated block via
    load_skill_for_task (00-CEO-Core/skill_finder.py — progressive
    disclosure, full text only for the top match) and attaches it as an
    additive result["skill"] key (name, repo path, loaded bool,
    ambiguous, candidates); department managers get the skill name/path
    as advisory context on their task copy. The hook is read-only and
    never executes a gated action; a lookup failure never breaks
    routing. CAVEAT: live-model skill execution still awaits Boss's PC
    live proof — the mock brain only drafts, the skill text is context,
    not a live run.
- Memory wiring (2026-11-21, MEMORY-STRUCTURE-DECISION-2026-11-21.md):
    handle_task() reads memory on every task — context_for(
    "chief_of_staff_agency") is attached to the result as "memory"
    (shared Boss-words + its own box). The Chief writes no note to memory —
    the routing log stays in tasks.json; memory is for Boss's words + lessons.
    Learning / forgetting Boss's words is not the Chief's job — that is the Main
    CEO Bot's job (record_owner_message /
    request_forget_owner_entry).

Routing table: TASK_TYPE -> (worker class, division, gate word)
"""

import importlib.util
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone

# --- paths (VENDORED engine — inside this office, not an outside checkout) --
MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(MASTER_OS_DIR, "00-CEO-Core")
ENGINE_WORKERS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "engine", "workers")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, ENGINE_WORKERS_DIR)

from audit import audit_log  # noqa: E402
from human_approval_gateway import ApprovalGateway  # noqa: E402
from owner_memory import OwnerMemory  # noqa: E402
from brain import BrainFactory  # noqa: E402
from store_io import update_json, write_json_atomic  # noqa: E402
from src.contracts.models import Task as EngineTask  # noqa: E402
from src.workers.acquisition import (  # noqa: E402
    NegotiationCoach,
    OutreachDrafter,
    ProspectResearcher,
    ReplyHandler,
)
from src.workers.admin import (  # noqa: E402
    InboxTriager,
    ReportCompiler,
    SchedulerAssistant,
)
from src.workers.delivery import (  # noqa: E402
    OnboardingAgent,
    QAEngineer,
    RetellBuilder,
)
from src.workers.marketing import (  # noqa: E402
    CaptionWriter,
    ContentPlanner,
    ObjectionSimulator,
    PublishPrep,
    VideoProducer,
)

DEPARTMENT = "agency"
BUSINESS = "Talvenor AI Receptionist Agency"
ENGINE_PATH = ENGINE_WORKERS_DIR  # vendored engine, inside this office
AGENCY_OFFICE_PATH = "~/workspace/talvenor-office/"
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"
DEMO_VIDEO = "https://facebook.com/reel/2947321012290705/"

PIPELINE_STAGES = [
    "research",    # ProspectResearcher — finding US home-service SMBs
    "draft",       # OutreachDrafter — cold email / IG DM draft (draft-only)
    "approve",     # Boss gate: send / ok
    "send",        # Boss sends (now PAUSED — DNS fix pending)
    "reply",       # ReplyHandler — reply triage
    "book",        # 15-min call — BOOKING_LINK
    "build",       # Vapi Sophia — building the receptionist (RetellBuilder = DRAFT plan only)
    "launch",      # QA + onboarding, launch
]

# task type -> (worker class, division, gate word for the OUTPUT's onward use)
# gate word = the word from Boss needed to send/use the output.
# None = the draft itself is safe, no gate.
ROUTING = {
    "prospect_research": (ProspectResearcher, "ACQ", None),
    "outreach_draft": (OutreachDrafter, "ACQ", "send"),
    "reply_triage": (ReplyHandler, "ACQ", "send"),
    "negotiation_prep": (NegotiationCoach, "ACQ", "ok"),
    "receptionist_build": (RetellBuilder, "DEL", "ok"),
    "receptionist_qa": (QAEngineer, "DEL", None),
    "onboarding_draft": (OnboardingAgent, "DEL", "ok"),
    "content_plan": (ContentPlanner, "MKT", "ok"),
    "video_produce": (VideoProducer, "MKT", "ok"),
    "caption_write": (CaptionWriter, "MKT", None),
    "publish_prep": (PublishPrep, "MKT", "post it"),
    "objection_sim": (ObjectionSimulator, "MKT", "ok"),
    "inbox_triage": (InboxTriager, "OPS", None),
    "report_compile": (ReportCompiler, "OPS", None),
    "schedule_help": (SchedulerAssistant, "OPS", None),
}

STORE_DIR = os.path.join(MASTER_OS_DIR, "store")
DEFAULT_TASKS_PATH = os.path.join(STORE_DIR, "tasks.json")
DEFAULT_APPROVALS_PATH = os.path.join(STORE_DIR, "approvals.json")
DEFAULT_AGENT_RUNS_PATH = os.path.join(STORE_DIR, "agent_runs.json")

# --- Phase 1 (Unified OS): registry as runtime source of truth --------------
# registry.json is read at runtime, read-only, never written by the Chief.
# It is the single source of truth for who an agent is (role, department,
# task kind); registry.md is only its generated view.
REGISTRY_JSON_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "agents", "agent-registry", "registry.json")
_REGISTRY_CACHE = {"mtime": None, "entries": None}

_WORKER_RE = re.compile(r"Worker: (\w+) \((\w+)\)")
_COUNTERPART_RE = re.compile(r"no brief counterpart \((\w+)\)")


def load_registry(registry_path=None):
    """Loads registry.json (read-only). Cached per process; re-read when
    the file's mtime changes. A missing or corrupt file returns [] —
    routing never breaks because the registry is unreadable."""
    path = registry_path or REGISTRY_JSON_PATH
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return []
    if (_REGISTRY_CACHE["entries"] is not None
            and _REGISTRY_CACHE["mtime"] == mtime):
        return _REGISTRY_CACHE["entries"]
    try:
        with open(path, "r", encoding="utf-8") as f:
            entries = json.load(f)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(entries, list):
        return []
    _REGISTRY_CACHE["mtime"] = mtime
    _REGISTRY_CACHE["entries"] = entries
    return entries


def _entry_kind(entry):
    """The task kind of a registry entry, from its notes."""
    notes = entry.get("notes", "") or ""
    m = _WORKER_RE.search(notes)
    if m:
        return m.group(2)
    m = _COUNTERPART_RE.search(notes)
    return m.group(1) if m else ""


def lookup_registry_entry(task_type=None, worker=None, registry_path=None):
    """Finds the registry entry for a run: first by task kind
    (the task type IS the worker's kind for engine/section workers),
    then by worker class name in the notes, then by role name.
    Returns the entry dict, or None when the agent is not in the
    registry (department managers are not — they live outside the 69)."""
    entries = load_registry(registry_path)
    if task_type:
        for entry in entries:
            if _entry_kind(entry) == task_type:
                return entry
    if worker:
        for entry in entries:
            if f"Worker: {worker} (" in (entry.get("notes", "") or ""):
                return entry
        for entry in entries:
            if (entry.get("role") == worker
                    or entry.get("role", "") + "Agent" == worker):
                return entry
    return None


def _log_agent_run(record, tasks_path=None, registry_path=None):
    """Records one agent run in store/agent_runs.json (append-only,
    atomic via store_io), next to tasks.json — so a check run that
    passes a TEMP tasks path also keeps its run log in TEMP, and the
    real store is only touched by a real run. The worker name, the
    registry role/department, and whether the agent is in the registry
    are recorded; managers are honestly marked in_registry=False.
    Never raises — a failed run log must not break routing."""
    worker = record.get("worker")
    if not worker:
        return False
    entry = lookup_registry_entry(
        task_type=record.get("type"), worker=worker,
        registry_path=registry_path)
    run = {
        "id": record.get("id"),
        "ran_at": record.get("logged_at") or _now_iso(),
        "worker": worker,
        "role": entry.get("role") if entry else None,
        "department": entry.get("department") if entry else None,
        "task_kind": _entry_kind(entry) if entry else None,
        "task_type": record.get("type"),
        "status": record.get("status"),
        "in_registry": entry is not None,
    }
    runs_path = (os.path.join(os.path.dirname(os.path.abspath(
        tasks_path)), "agent_runs.json") if tasks_path
        else DEFAULT_AGENT_RUNS_PATH)

    def _apply(data):
        records = data.get("records", []) if isinstance(data, dict) else []
        if not isinstance(records, list):
            records = []
        records.append(run)
        return {"schema": "agent-runs-v1", "records": records}

    try:
        update_json(runs_path, _apply,
                    default={"schema": "agent-runs-v1", "records": []})
    except Exception:  # noqa: BLE001 - run log must never break routing
        return False
    return True

# --- Phase 7 sections -------------------------------------------------------
SECTIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "sections")

# task type -> (agent module file, relative to sections/, class name, gate word)
# Phase 7 NEW staff — ROUTING's 15 unchanged; only these 6 added.
SECTION_ROUTING = {
    "client_intake": ("receive/agents/client_intake_receiver.py", "ClientIntakeReceiverAgent", "send"),
    "sales_close": ("sell/agents/sales_closer.py", "SalesCloserAgent", "ok"),
    "followup_draft": ("sell/agents/followup_agent.py", "FollowUpAgent", "send"),
    "delivery_manage": ("delivery/agents/service_delivery_manager.py", "ServiceDeliveryManagerAgent", "ok"),
    "client_success": ("delivery/agents/client_success_agent.py", "ClientSuccessAgent", "send"),
    "billing_invoice": ("ops/agents/billing_invoice_agent.py", "BillingInvoiceAgent", "ok"),
}

# --- Phase 2 departments ----------------------------------------------------
DEPARTMENTS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "departments")

# task type -> (manager module file, relative to departments/, class name, gate word)
# Phase 2 wiring — ROUTING (15) and SECTION_ROUTING (6) unchanged; only these 8 added.
# Managers make a DRAFT of the delegation plan; no worker is executed.
DEPARTMENT_ROUTING = {
    "dept_sales": ("01-sales-growth/manager/chief_growth_agent.py", "ChiefGrowthAgent", "ok"),
    "dept_marketing": ("02-marketing/manager/marketing_director_agent.py", "MarketingDirectorAgent", "ok"),
    "dept_engineering": ("03-ai-engineering/manager/cto_ai_engineering_agent.py", "CTOAIEngineeringAgent", "ok"),
    "dept_operations": ("04-client-operations/manager/coo_client_operations_agent.py", "COOClientOperationsAgent", "ok"),
    "dept_strategy": ("05-research-strategy/manager/chief_strategy_agent.py", "ChiefStrategyAgent", "ok"),
    "dept_finance": ("06-finance-admin/manager/cfo_finance_agent.py", "CFOFinanceAgent", "ok"),
    "dept_quality": ("07-quality-security/manager/chief_quality_security_agent.py", "ChiefQualitySecurityAgent", "ok"),
    "dept_innovation": ("08-product-innovation/manager/chief_innovation_agent.py", "ChiefInnovationAgent", "ok"),
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _skill_query_for_task(task):
    """Derive a skill-finder query from a task (Phase 2, 2026-11-25).

    Query = task title + task type (underscores -> spaces) + payload
    task_kind (when present and not already in the query). The type
    alone is usually enough ("caption_write" -> caption-writer); the
    title adds the task's own words; task_kind adds the manager's
    kind. Read-only string work — no file or network access.
    """
    parts = []
    title = (task.get("title") or "").strip()
    if title:
        parts.append(title)
    task_type = (task.get("type") or "").strip()
    if task_type:
        parts.append(task_type.replace("_", " "))
    payload = task.get("payload") or {}
    kind = payload.get("task_kind") or task.get("task_kind") or ""
    if isinstance(kind, str) and kind.strip():
        kind = kind.strip().replace("_", " ")
        if kind not in " ".join(parts):
            parts.append(kind)
    return " ".join(parts).strip()


def _load_skill_for_task(task):
    """Load the skill for a task (Phase 2 skill hook, 2026-11-25).

    Calls the hardened finder (skill_finder.load_skill_for_task —
    progressive disclosure, full text only for the top match) and
    returns an additive info dict: {"query", "name", "path", "loaded",
    "ambiguous", "candidates"}. Read-only: loading never executes a
    gated action and never writes a skill file. NEVER raises — a
    missing finder, an empty query, or a lookup failure returns
    loaded=False (with "error" when the finder itself raised) so
    routing continues exactly as before.
    """
    query = _skill_query_for_task(task)
    info = {"query": query, "name": None, "path": None,
            "loaded": False, "ambiguous": False, "candidates": []}
    if not query:
        return info
    try:
        import skill_finder  # noqa: PLC0415 (CEO_CORE_DIR is on sys.path)
        found = skill_finder.load_skill_for_task(query)
    except Exception as e:  # noqa: BLE001 - skill lookup never breaks routing
        info["error"] = f"{type(e).__name__}: {e}"
        return info
    loaded = found.get("loaded") or {}
    info["name"] = loaded.get("name")
    info["path"] = loaded.get("path")
    info["loaded"] = bool(loaded)
    info["ambiguous"] = bool(found.get("ambiguous"))
    info["candidates"] = list(found.get("candidates") or [])
    return info


def _log_task(record, tasks_path=None):
    """Appends every routed task to store/tasks.json. Never deletes another
    department's entry — locked read-modify-write + atomic write
    (Phase 1, Unified OS: store_io). A corrupt tasks file is reset to
    just this record and the reset is written to the audit log — the
    old silent reset is gone."""
    path = tasks_path or DEFAULT_TASKS_PATH

    def _apply(data):
        records = data.get("records", []) if isinstance(data, dict) else []
        if not isinstance(records, list):
            records = []
        records.append(record)
        return {"schema": "tasks-v1", "records": records}

    try:
        update_json(path, _apply, default={"schema": "tasks-v1", "records": []})
    except json.JSONDecodeError:
        audit_log("store_corrupt_reset", {
            "file": path, "kept_record": record.get("id"),
            "note": "tasks.json was corrupt — reset to this record only.",
        }, audit_path=os.path.join(os.path.dirname(os.path.abspath(path)),
                                   "audit.log"))
        write_json_atomic(path, {"schema": "tasks-v1", "records": [record]})
    _log_agent_run(record, tasks_path=tasks_path)
    return record


def handle_task(task, tasks_path=None, approvals_path=None, memory_path=None):
    """Run one agency task coming from the Main CEO Bot + memory wiring.

    Memory: on every task the Chief reads its own box's context
    (context_for("chief_of_staff_agency") — shared Boss-words + its own
    note) and attaches it to the result as "memory". Nothing is written to memory —
    the routing log stays in tasks.json.
    The real work is in _handle_task_inner() — this wrapper only adds the memory read.
    """
    mem = (OwnerMemory(memory_path=memory_path)
           if memory_path else OwnerMemory())
    memory_ctx = mem.context_for("chief_of_staff_agency")
    result = _handle_task_inner(task, tasks_path=tasks_path,
                                approvals_path=approvals_path)
    result["memory"] = memory_ctx
    return result


def _handle_task_inner(task, tasks_path=None, approvals_path=None):
    """Run one agency task coming from the Main CEO Bot.

    task = {
      "type": "outreach_draft" | "prospect_research" | ... (ROUTING keys)
             | "client_intake" | ... (SECTION_ROUTING keys)
             | "dept_sales" | ... (DEPARTMENT_ROUTING keys),
      "title": "...",
      "payload": {...},           # input given to the worker
      "gated_action": "send" | "publish" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — approval taken earlier),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "pending-approval" | "route-only" | "error", ...}
    - If there is a gated_action, the worker is not run at all — a PENDING
      approval request is written to the gateway, and it stops right here.
    - Even when a worker runs, the result is only a DRAFT — this Chief does not send/publish.
    """
    title = task.get("title", "")
    task_type = task.get("type")
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")

    # 1. Gated action — the worker must not run, it must be held at approval.
    if gated_action:
        gateway = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        approval_id = task.get("approval_id")
        if approval_id and gateway.is_approved(approval_id):
            # Even with approval, this Chief does not send/publish/spend/delete —
            # it only reports that Boss has approved, and Boss himself will do the work.
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
            approval = gateway.request(gated_action, title or task_type or "agency task", requested_by)
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

    # 1a. Phase 2 skill hook (2026-11-25) — AFTER the gated block, so a
    # gated task never reaches skill loading (it returned above).
    # Read-only: load_skill_for_task loads the top match's full text
    # only; nothing is executed and no gated action can fire from a
    # skill. Additive only: result["skill"] is a new key; no existing
    # key or status changes. A lookup failure never breaks routing.
    skill_info = _load_skill_for_task(task)

    # 1b. Phase 7 section agents — alongside ROUTING, after the gated block.
    # If a gated action was present the block above already returned, so here the task
    # No gated_action — the agent only makes a DRAFT.
    if task_type in SECTION_ROUTING:
        module_file, class_name, gate_word = SECTION_ROUTING[task_type]
        agent_path = os.path.join(SECTIONS_DIR, module_file)
        spec = importlib.util.spec_from_file_location(
            f"section_agent_{task_type}", agent_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        agent_cls = getattr(mod, class_name)
        agent = agent_cls()
        gw = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        agent_result = agent.run(
            task, BrainFactory.get_brain("agency"), gw, approvals_path)
        if agent_result.get("status") == "pending-approval":
            result = {
                "status": "pending-approval",
                "department": DEPARTMENT,
                "task": title,
                "type": task_type,
                "worker": class_name,
                "section": agent.section,
                "gated_action": gated_action,
                "approval": agent_result.get("approval"),
                "note": "Gated action refused — PENDING approval recorded. Nothing was sent/published/spent/deleted.",
                "draft_only": True,
                "mock_brain": True,
                "gate": gate_word,
            }
        else:
            note = "DRAFT ONLY — mock brain ($0). "
            if gate_word:
                note += f"Boss's gate word is needed to send/use the output: '{gate_word}'."
            else:
                note += "This draft has no gate."
            result = {
                "status": "draft-ready",
                "department": DEPARTMENT,
                "business": BUSINESS,
                "task": title,
                "type": task_type,
                "worker": class_name,
                "section": agent.section,
                "output": agent_result.get("output"),
                "notes": agent_result.get("notes"),
                "mock_brain": True,
                "draft_only": True,
                "gate": gate_word,
                "note": note,
            }
        result["skill"] = skill_info
        _log_task({
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": class_name,
            "status": result["status"],
            "logged_at": _now_iso(),
        }, tasks_path=tasks_path)
        return result

    # 1c. Phase 2 department managers — like SECTION_ROUTING, after the gated block.
    # If a gated action was present the block above already returned, so here the task
    # No gated_action — the manager only makes a DRAFT of the delegation plan.
    # If the run_office.py input's payload has a task_kind, it is put into the manager's
    # top-level task_kind (the manager reads task.get("task_kind")).
    if task_type in DEPARTMENT_ROUTING:
        module_file, class_name, gate_word = DEPARTMENT_ROUTING[task_type]
        manager_path = os.path.join(DEPARTMENTS_DIR, module_file)
        spec = importlib.util.spec_from_file_location(
            f"department_manager_{task_type}", manager_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        manager_cls = getattr(mod, class_name)
        manager = manager_cls()
        gw = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        manager_task = dict(task)
        payload_kind = (task.get("payload") or {}).get("task_kind")
        if payload_kind and not manager_task.get("task_kind"):
            manager_task["task_kind"] = payload_kind
        # Phase 2 skill hook (advisory only): the skill name/path ride
        # on the manager's task copy; managers ignore unknown keys.
        # Nothing is injected into any engine EngineTask payload.
        manager_task["skill"] = {"name": skill_info.get("name"),
                                 "path": skill_info.get("path")}
        manager_result = manager.run(
            manager_task, BrainFactory.get_brain("agency"), gw, approvals_path)
        department_folder = module_file.split("/")[0]
        if manager_result.get("status") == "pending-approval":
            result = {
                "status": "pending-approval",
                "department": DEPARTMENT,
                "task": title,
                "type": task_type,
                "worker": class_name,
                "manager_department": department_folder,
                "gated_action": gated_action,
                "approval": manager_result.get("approval"),
                "note": "Gated action refused — PENDING approval recorded. Nothing was sent/published/spent/deleted.",
                "draft_only": True,
                "mock_brain": True,
                "gate": gate_word,
            }
        elif manager_result.get("status") == "unknown-task":
            result = {
                "status": "unknown-task",
                "department": DEPARTMENT,
                "task": title,
                "type": task_type,
                "worker": class_name,
                "manager_department": department_folder,
                "output": manager_result.get("output"),
                "notes": manager_result.get("notes"),
                "mock_brain": True,
                "draft_only": True,
                "gate": gate_word,
                "note": "Unknown department task kind — no delegation plan made. Known kinds are listed in the manager output.",
            }
        else:
            note = "DRAFT ONLY — mock brain ($0). "
            if gate_word:
                note += f"Boss's gate word is needed to send/use the output: '{gate_word}'."
            else:
                note += "This draft has no gate."
            result = {
                "status": "draft-ready",
                "department": DEPARTMENT,
                "business": BUSINESS,
                "task": title,
                "type": task_type,
                "worker": class_name,
                "manager_department": department_folder,
                "output": manager_result.get("output"),
                "notes": manager_result.get("notes"),
                "mock_brain": True,
                "draft_only": True,
                "gate": gate_word,
                "note": note,
            }
        # Phase 5 shared-runtime hook (2026-11-25): when the incoming
        # task carries "execute": True AND the manager returned a
        # draft, run the department workflow through the shared
        # runtime (AgentRuntime + workflow engine, behind the gate).
        # A gated step comes back pending-approval and NEVER
        # executes — recorded as "executed-partial", not a failure.
        # Without "execute": True, or for pending-approval /
        # unknown-task manager results, behaviour is EXACTLY as
        # before: no new keys, no status change, no "executions"
        # in the log record. The department_runtime import is lazy
        # (inside this branch) and failure-proof: a missing/broken
        # module only attaches an error "execution" dict and never
        # changes result["status"].
        _exec_record = None
        if (task.get("execute") is True
                and manager_result.get("status") == "draft-ready"):
            try:
                if DEPARTMENTS_DIR not in sys.path:
                    sys.path.insert(0, DEPARTMENTS_DIR)
                import department_runtime  # noqa: PLC0415 (lazy)
                _exec = department_runtime.execute_department_task(
                    department_folder, manager_task, manager_result)
                result["execution"] = _exec.get("execution")
                if _exec.get("status") in ("executed",
                                           "executed-partial"):
                    result["status"] = _exec["status"]
                elif _exec.get("status") == "error":
                    result["status"] = "error"
                _exec_record = _exec.get("execution_record")
            except Exception as _exc:  # noqa: BLE001 — never break routing
                result["execution"] = {
                    "status": "error",
                    "error": f"{type(_exc).__name__}: {_exc}"}
        result["skill"] = skill_info
        _log_record = {
            "id": uuid.uuid4().hex[:12],
            "department": DEPARTMENT,
            "title": title,
            "type": task_type,
            "worker": class_name,
            "status": result["status"],
            "logged_at": _now_iso(),
        }
        if _exec_record is not None:
            _log_record["executions"] = [_exec_record]
        _log_task(_log_record, tasks_path=tasks_path)
        return result

    # 2. Task without a type — only a routing probe, no worker runs.
    if not task_type:
        result = {
            "status": "route-only",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "note": "No task type given — routing probe only, no worker ran.",
            "routing_keys": sorted(ROUTING),
        }
        result["skill"] = skill_info
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

    # 3. Unknown type — admit the mistake and stop, no invented worker.
    if task_type not in ROUTING:
        result = {
            "status": "error",
            "department": DEPARTMENT,
            "task": title,
            "type": task_type,
            "error": f"Unknown task type {task_type!r}. Known: {sorted(ROUTING)}",
        }
        result["skill"] = skill_info
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

    # 4. Real routing — vendored worker, BrainFactory's brain ($0 mock default).
    worker_cls, division, gate_word = ROUTING[task_type]
    llm = BrainFactory.get_brain("agency")
    worker = worker_cls(
        f"agency-{worker_cls.__name__}",
        "talvenor-agency",
        division,
        worker_cls.__name__,
        llm,
    )
    engine_task = EngineTask(
        task_id=f"agency-{uuid.uuid4().hex[:12]}",
        business_id="talvenor-agency",
        division_id=division,
        kind=worker_cls.task_kind,
        payload=dict(getattr(worker_cls, "default_payload", {}) or {},
                     **(task.get("payload") or {})),
    )
    worker_result = worker.execute(engine_task)

    note = "DRAFT ONLY — mock brain ($0). "
    if gate_word:
        note += f"Boss's gate word is needed to send/use the output: '{gate_word}'."
    else:
        note += "This draft has no gate."
    if worker_cls is RetellBuilder:
        note += " (RetellBuilder = DRAFT build plan only — live stack Vapi/Sophia, Boss will not pay money for Retell.)"

    result = {
        "status": "draft-ready",
        "department": DEPARTMENT,
        "business": BUSINESS,
        "task": title,
        "type": task_type,
        "worker": worker_cls.__name__,
        "division": division,
        "worker_status": worker_result.status,
        "output": worker_result.output,
        "notes": worker_result.notes,
        "mock_revenue_usd": worker_result.mock_revenue_usd,  # MOCK ledger only — not real money
        "mock_brain": True,
        "draft_only": True,
        "gate": gate_word,
        "note": note,
    }
    result["skill"] = skill_info
    _log_task({
        "id": uuid.uuid4().hex[:12],
        "department": DEPARTMENT,
        "title": title,
        "type": task_type,
        "worker": worker_cls.__name__,
        "status": "draft-ready",
        "logged_at": _now_iso(),
    }, tasks_path=tasks_path)
    return result


if __name__ == "__main__":
    print("Agency Chief of Staff — REAL (Phase 1). Pipeline:", " -> ".join(PIPELINE_STAGES))
    print("Routed task types:", ", ".join(sorted(ROUTING)))
    print("Department task types:", ", ".join(sorted(DEPARTMENT_ROUTING)))
    print("Engine:", ENGINE_PATH, "| Office:", AGENCY_OFFICE_PATH)
    print("Email: PAUSED — this Chief only drafts, never sends.")
