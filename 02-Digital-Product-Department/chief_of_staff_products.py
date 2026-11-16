"""Chief of Staff — Digital Product Department (REAL, Phase 2).

Product: Vet No-Show Recovery Kit — $49 one-time।
Independent US vet clinic-দের জন্য: reminder cadence, rebooking script,
waitlist SOP, no-show log + $ tracker, policy template।

কাজ: Main CEO Bot থেকে আসা task-টা পড়ে ঠিক কাজের দিকে পাঠানো,
ফলাফল DRAFT হিসেবে ফেরত দেওয়া, আর Gate 0 না পাস হওয়া পর্যন্ত
kit launch / sale-কে আটকে রাখা।

Gate 0 — কঠিন নিয়ম (কোডে লেখা, fail-closed):
  - Gate 0 = Lemon Squeezy signup test (BD individual হিসেবে) — Boss-এর
    step, এখনো NOT PASSED। ফলাফলের একমাত্র উৎস:
    02-Digital-Product-Department/gate0-status.md — "Status: PASSED"
    লেখা না থাকলে Gate 0 পাস ধরা হয় না।
  - Gate 0 পাস না হওয়া পর্যন্ত: kit বানানো/বেচা/launch করা যাবে না।
    kit_build শুধু BLUEPRINT (kit-outline.md) ফেরত দেয় — kit নিজে নয়।
    launch_prep শুধু DRAFT checklist দেয় — launch করে না।
    mark_launched / mark_sold চাইলে status "blocked-gate0" ফেরত আসে,
    কিছুই লেখা/বেচা হয় না।
  - Gated কাজ (send / publish / spend / delete) হলে worker একদম
    চালানো হয় না — ApprovalGateway-এ PENDING request লেখা হয়।
  - এই Chief কখনো মেইল পাঠায় না, publish করে না, খরচ করে না,
    delete করে না। Sale-এর সংখ্যা কখনো বানানো হয় না — sale 0।

Kit blueprint: 02-Digital-Product-Department/kit-outline.md
PA clinic list: 02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv
Payment rails: Lemon Squeezy (Gate 0-র পরে), backup Polar, Gumroad
(individual)। Etsy Bangladesh-এর জন্য বন্ধ — কখনো plan-এ নেই।

Wedge (UNTESTED): ২০ জন kit buyer-এর ১ জন receptionist নিলে
~$11K/mo — অনুমান, fact নয়, কখনো fact হিসেবে লেখা হয় না।
"""

import csv
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

DEPARTMENT = "digital-product"
BUSINESS = "Vet No-Show Recovery Kit"
PRICE_USD_ONE_TIME = 49
LAUNCH_PRICE_USD_ONE_TIME = 39  # প্রথম ৩০ buyer-এর জন্য (research §4.1)
KIT_BLUEPRINT_PATH = os.path.join(DEPT_DIR, "kit-outline.md")
GATE0_STATUS_PATH = os.path.join(DEPT_DIR, "gate0-status.md")
PA_LIST_PATH = os.path.join(DEPT_DIR, "pa-vet-list", "pa-vet-clinics.csv")

STORE_DIR = os.path.join(MASTER_OS_DIR, "store")
DEFAULT_TASKS_PATH = os.path.join(STORE_DIR, "tasks.json")
DEFAULT_APPROVALS_PATH = os.path.join(STORE_DIR, "approvals.json")

# Kit-এর ৬ অংশ (research report §4.1 থেকে — blueprint-এর কাঠামো)
KIT_PARTS = [
    "reminder-cadence-pack",   # T-72h / T-24h / T-2h SMS + email + call script
    "same-day-rebooking",      # no-show / late-cancel হলে on-the-spot rebook script
    "waitlist-fill-sop",       # খালি slot ভরার এক পাতার SOP + call script
    "no-show-log-tracker",     # Sheets: no-show log + $ tracker (formula)
    "deposit-policy-template", # deposit / no-show policy (attorney-review note সহ)
    "front-desk-quick-card",   # ৫ লাইনের এক পাতার desk card
]

# task type -> (handler, gate word for the OUTPUT's onward use)
# gate word = output পাঠাতে/ব্যবহার করতে Boss-এর যে শব্দ লাগবে।
# None = draft নিজেই নিরাপদ, কোনো gate নেই।
ROUTING = {
    "kit_build": ("blueprint", "ok"),
    "clinic_research": ("pa-list", None),
    "gate0_check": ("gate0-status", None),
    "launch_prep": ("launch-checklist-draft", "go"),
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def read_gate0_status():
    """Gate 0-র একমাত্র উৎস: gate0-status.md।

    ফাইলের "Status:" লাইনটা পড়ে — value "PASSED" দিয়ে শুরু হলেই
    পাস, নইলে NOT PASSED (fail-closed)। ব্যাখ্যার লাইনে "PASSED"
    শব্দ থাকলেও তা গোনা হয় না — শুধু Status লাইনটাই উৎস।
    ফাইল না থাকলে/পড়া না গেলেও NOT PASSED।
    """
    try:
        with open(GATE0_STATUS_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (FileNotFoundError, OSError):
        return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
                "note": "gate0-status.md পড়া যায়নি — fail-closed: NOT PASSED ধরা হয়েছে।"}
    for line in lines:
        stripped = line.strip().lstrip("*").strip()
        if stripped.startswith("Status:"):
            value = stripped[len("Status:"):].strip().lstrip("*").strip()
            if value.startswith("PASSED"):
                return {"status": "PASSED", "source": GATE0_STATUS_PATH,
                        "note": "gate0-status.md-এ Status: PASSED লেখা আছে।"}
            return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
                    "note": "Gate 0 পাস হয়নি — Lemon Squeezy signup test Boss-এর step, এখনো বাকি।"}
    return {"status": "NOT PASSED", "source": GATE0_STATUS_PATH,
            "note": "gate0-status.md-এ Status লাইন পাওয়া যায়নি — fail-closed: NOT PASSED ধরা হয়েছে।"}


def gate0_passed():
    return read_gate0_status()["status"] == "PASSED"


def _read_kit_blueprint():
    """kit-outline.md পড়ে — না থাকলে অংশের তালিকা ফেরত দেয়।"""
    try:
        with open(KIT_BLUEPRINT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return None


def _read_pa_list():
    """PA vet list CSV পড়ে — row সংখ্যা + সারাংশ।"""
    if not os.path.isfile(PA_LIST_PATH):
        return {"rows": 0, "path": PA_LIST_PATH, "exists": False}
    with open(PA_LIST_PATH, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    return {"rows": len(rows), "path": PA_LIST_PATH, "exists": True,
            "cities": sorted({r.get("city", "") for r in rows if r.get("city")}),
            "target_rows": 100}


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
    """Main CEO Bot থেকে আসা একটা digital-product task চালানো।

    task = {
      "type": "kit_build" | "clinic_research" | "gate0_check" | "launch_prep",
      "title": "...",
      "payload": {...},           # input
      "gated_action": "send" | "publish" | "spend" | "delete" (optional),
      "approval_id": "..." (optional — আগে নেওয়া approval),
      "requested_by": "Main CEO Bot" (optional),
    }

    Returns: {"status": "draft-ready" | "blocked-gate0" | "pending-approval"
              | "route-only" | "error", ...}
    - mark_launched / mark_sold চাইলে Gate 0 যাচাই হয় — পাস না হলে
      status "blocked-gate0", কিছুই launch/sale হিসেবে লেখা হয় না।
    - gated_action থাকলে worker একদম চালানো হয় না — gateway-এ PENDING।
    - ফলাফল শুধু DRAFT / BLUEPRINT — kit বানানো/বেচা এই Chief করে না।
    """
    title = task.get("title", "")
    task_type = task.get("type")
    payload = task.get("payload") or {}
    requested_by = task.get("requested_by", "Main CEO Bot")
    gated_action = task.get("gated_action")

    # 1. Launch / sale দাবি — Gate 0 যাচাই, পাস না হলে আটকে যাবে।
    if payload.get("mark_launched") or payload.get("mark_sold"):
        gate0 = read_gate0_status()
        result = {
            "status": "blocked-gate0",
            "department": DEPARTMENT,
            "business": BUSINESS,
            "task": title,
            "gate0": gate0,
            "note": "Gate 0 পাস হয়নি — kit-কে launched/sold হিসেবে চিহ্নিত করা যাবে না। "
                    "কোনো sale লেখা হয়নি, sale এখনো 0।",
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

    # 2. Gated action — worker চালানো যাবে না, approval-এ আটকাতে হবে।
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

    # 3. Type ছাড়া task — শুধু routing probe, কাজ চলে না।
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

    # 4. অচেনা type — ভুল স্বীকার করে থামা, বানানো কাজ নয়।
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

    # 5. আসল routing — Gate 0-র অবস্থা সহ।
    handler, gate_word = ROUTING[task_type]
    gate0 = read_gate0_status()

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
        note = ("BLUEPRINT ONLY — এটা kit-এর নকশা, kit নিজে নয়। "
                "Gate 0 পাস না হওয়া পর্যন্ত kit বানানো/বেচা শুরু হবে না।")
    elif task_type == "clinic_research":
        pa_list = _read_pa_list()
        output = {
            "pa_list": pa_list,
            "note": "PA list ১০০ clinic-এর লক্ষ্যে — এখনো পুরো হয়নি, যাচাই করা row-ই শুধু আছে।",
        }
        note = "Clinic list — যাচাই করা public তথ্য শুধু, কিছু বানানো নয়। কোনো clinic-কে মেইল করা হয়নি।"
    elif task_type == "gate0_check":
        output = {"gate0": gate0}
        note = "Gate 0-র সত্য অবস্থা — gate0-status.md থেকে পড়া।"
    elif task_type == "launch_prep":
        output = {
            "launch_checklist_draft": [
                "Gate 0 পাস (Lemon Squeezy store খোলে কি না) — এখনো NOT PASSED",
                "Kit-এর ৬ অংশ বানানো (Sheets + Docs + script) — এখনো হয়নি",
                "Cadence AAHA/PetDesk guidance-এর সাথে যাচাই (Gate 1) — এখনো হয়নি",
                "Lemon Squeezy listing + Gumroad backup listing — এখনো হয়নি",
                "Sales page — Boss review করবেন launch-এর আগে",
                "100 clinic-কে ২৫টা করে মেইল (৪ দিন) — email channel এখন PAUSED",
            ],
            "launch_blocked": not gate0_passed(),
            "gate0": gate0,
        }
        note = ("DRAFT checklist only — launch করা হয়নি, করা যাবে না। "
                "Gate 0 পাস না হওয়া পর্যন্ত launch আটকে আছে।")
    else:  # pragma: no cover — ROUTING-এ নতুন key এলে এখানে আসে না
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
        "note": note + (f" Output ব্যবহার করতে Boss-এর gate word লাগবে: '{gate_word}'।" if gate_word else ""),
    }
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
    print("Kit parts:", len(KIT_PARTS), "| PA list target: 100 clinics")
    print("Launch/sale: BLOCKED until Gate 0 passes — this Chief never fakes a sale.")
