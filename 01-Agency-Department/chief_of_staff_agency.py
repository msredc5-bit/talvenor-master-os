"""Chief of Staff — Agency Department (REAL, Phase 1).

Talvenor AI Receptionist Agency — Boss-এর প্রথম ব্যবসা, MAIN।

কাজ: Main CEO Bot থেকে আসা task-টা পড়ে এই office-এর ভেতরে vendored
engine-এর আসল worker-এর দিকে পাঠানো, ফলাফল DRAFT হিসেবে ফেরত
দেওয়া, আর gated কাজ (send / publish / spend / delete) হলে
ApprovalGateway দিয়ে আটকে রাখা। Workers এখন office-এর ভেতরে
vendored (engine/workers/) — বাইরের কোনো checkout-এর ওপর
আর কোনো নির্ভরতা নেই (দেখুন engine/workers/SOURCE.md)।

নিয়ম (কোডে লেখা):
  - এই Chief কখনো মেইল/মেসেজ পাঠায় না, publish করে না, খরচ করে
    না, delete করে না। পাঠানো/পাবলিশ শুধু Boss-এর gate word-এ হয়,
    আর সেটাও Boss নিজে করেন (এই সিস্টেম শুধু DRAFT বানায়)।
  - Email পাঠানো PAUSED (Boss-এর নির্দেশ 2026-11-14) — draft-ই শেষ
    কথা, send-এর চেষ্টাও করা হয় না।
  - Worker-রা BrainFactory-র brain দিয়ে চলে — config.json-এর
    "brain" flag "mock" (DEFAULT, $0) হলে vendored MockLLMProvider,
    "live" হলে vendored MetaSparkProvider। ফলাফল DRAFT / MOCK হিসেবে
    লেবেল করা থাকে। Live brain শুধু Boss-এর আলাদা অনুমোদনে, এখানে নয়;
    Phase 6 কোনো live call করে না (দেখুন 00-CEO-Core/brain.py)।
  - RetellBuilder: engine-এর DEL worker-এর আসল নাম। কিন্তু
    Talvenor-এর live stack Vapi/Sophia (Boss Retell-এর জন্য টাকা
    দেবেন না) — তাই RetellBuilder-এর output শুধু DRAFT build plan,
    কখনো live build নয়।
  - Phase 2 wiring (2026-11-19): DEPARTMENT_ROUTING — ৮ department
    manager-কে Chief এখন call করে (dept_sales / dept_marketing /
    dept_engineering / dept_operations / dept_strategy / dept_finance /
    dept_quality / dept_innovation)। Manager-রা শুধু delegation plan-এর
    DRAFT বানায়; কোনো worker execute করে না। Manager-এর task_kind
    payload-এ থাকলে তা top-level-এ বসানো হয় (manager task.get
    ("task_kind") পড়ে); না থাকলে M1–M4 overview দেয়, M5–M8
    "unknown-task" ফেরত দেয় (known kind-গুলোর তালিকা সহ)।

Routing table: TASK_TYPE -> (worker class, division, gate word)
"""

import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# --- paths (VENDORED engine — এই office-এর ভেতরে, বাইরের checkout নয়) --
MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(MASTER_OS_DIR, "00-CEO-Core")
ENGINE_WORKERS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "engine", "workers")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, ENGINE_WORKERS_DIR)

from human_approval_gateway import ApprovalGateway  # noqa: E402
from brain import BrainFactory  # noqa: E402
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
ENGINE_PATH = ENGINE_WORKERS_DIR  # vendored engine, এই office-এর ভেতরে
AGENCY_OFFICE_PATH = "~/workspace/talvenor-office/"
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"
DEMO_VIDEO = "https://facebook.com/reel/2947321012290705/"

PIPELINE_STAGES = [
    "research",    # ProspectResearcher — US home-service SMB খোঁজা
    "draft",       # OutreachDrafter — cold email / IG DM draft (draft-only)
    "approve",     # Boss gate: send / ok
    "send",        # Boss পাঠান (এখন PAUSED — DNS fix বাকি)
    "reply",       # ReplyHandler — reply triage
    "book",        # 15-min call — BOOKING_LINK
    "build",       # Vapi Sophia — receptionist বানানো (RetellBuilder = DRAFT plan only)
    "launch",      # QA + onboarding, চালু
]

# task type -> (worker class, division, gate word for the OUTPUT's onward use)
# gate word = output পাঠাতে/ব্যবহার করতে Boss-এর যে শব্দ লাগবে।
# None = draft নিজেই নিরাপদ, কোনো gate নেই।
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

# --- Phase 7 sections -------------------------------------------------------
SECTIONS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "sections")

# task type -> (agent module file, relative to sections/, class name, gate word)
# Phase 7 NEW staff — ROUTING-এর ১৫টা অপরিবর্তিত; এই ৬টা শুধু যোগ করা।
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
# Phase 2 wiring — ROUTING (১৫) ও SECTION_ROUTING (৬) অপরিবর্তিত; এই ৮টা শুধু যোগ করা।
# Manager-রা delegation plan-এর DRAFT বানায়; কোনো worker execute করে না।
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


def _log_task(record, tasks_path=None):
    """প্রতিটা routed task store/tasks.json-এ append করে। অন্য
    department-এর entry কখনো মুছে না — read-modify-write।"""
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
    """Main CEO Bot থেকে আসা একটা agency task চালানো।

    task = {
      "type": "outreach_draft" | "prospect_research" | ... (ROUTING keys)
             | "client_intake" | ... (SECTION_ROUTING keys)
             | "dept_sales" | ... (DEPARTMENT_ROUTING keys),
      "title": "...",
      "payload": {...},           # worker-কে দেওয়া input
      "gated_action": "send" | "publish" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — আগে নেওয়া approval),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "pending-approval" | "route-only" | "error", ...}
    - gated_action থাকলে worker একদম চালানো হয় না — gateway-এ PENDING
      approval request লেখা হয়, আর এখানেই থেমে যায়।
    - worker চালালেও ফলাফল শুধু DRAFT — পাঠানো/পাবলিশ এই Chief করে না।
    """
    title = task.get("title", "")
    task_type = task.get("type")
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")

    # 1. Gated action — worker চালানো যাবে না, approval-এ আটকাতে হবে।
    if gated_action:
        gateway = ApprovalGateway(approvals_path=approvals_path) if approvals_path else ApprovalGateway()
        approval_id = task.get("approval_id")
        if approval_id and gateway.is_approved(approval_id):
            # অনুমোদন থাকলেও এই Chief send/publish/spend/delete করে না —
            # শুধু জানায় যে Boss অনুমোদন দিয়েছেন, কাজটা Boss নিজে করবেন।
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

    # 1b. Phase 7 section agents — ROUTING-এর পাশাপাশি, gated block-এর পরে।
    # Gated action থাকলে উপরের block-ই ফিরেছে, তাই এখানে task-এ
    # gated_action নেই — agent শুধু DRAFT বানায়।
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
                note += f"Output পাঠাতে/ব্যবহার করতে Boss-এর gate word লাগবে: '{gate_word}'."
            else:
                note += "এই draft-এ কোনো gate নেই।"
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

    # 1c. Phase 2 department managers — SECTION_ROUTING-এর মতোই, gated block-এর পরে।
    # Gated action থাকলে উপরের block-ই ফিরেছে, তাই এখানে task-এ
    # gated_action নেই — manager শুধু delegation plan-এর DRAFT বানায়।
    # run_office.py input-এর payload-এ task_kind থাকলে তা manager-এর
    # top-level task_kind-এ বসানো হয় (manager task.get("task_kind") পড়ে)।
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
                note += f"Output পাঠাতে/ব্যবহার করতে Boss-এর gate word লাগবে: '{gate_word}'."
            else:
                note += "এই draft-এ কোনো gate নেই।"
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

    # 2. Type ছাড়া task — শুধু routing probe, worker চলে না।
    if not task_type:
        result = {
            "status": "route-only",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "note": "No task type given — routing probe only, no worker ran.",
            "routing_keys": sorted(ROUTING),
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

    # 3. অচেনা type — ভুল স্বীকার করে থামা, বানানো worker নয়।
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

    # 4. আসল routing — vendored worker, BrainFactory-র brain ($0 mock default)।
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
        note += f"Output পাঠাতে/ব্যবহার করতে Boss-এর gate word লাগবে: '{gate_word}'."
    else:
        note += "এই draft-এ কোনো gate নেই।"
    if worker_cls is RetellBuilder:
        note += " (RetellBuilder = DRAFT build plan only — live stack Vapi/Sophia, Boss Retell-এর জন্য টাকা দেবেন না।)"

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
        "mock_revenue_usd": worker_result.mock_revenue_usd,  # MOCK ledger only — real money নয়
        "mock_brain": True,
        "draft_only": True,
        "gate": gate_word,
        "note": note,
    }
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
