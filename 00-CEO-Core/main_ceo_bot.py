"""Main CEO Bot — thin brain / router (Phase 0, REAL skeleton).

কাজ: Boss-এর (বা Jarvis-এর) দেওয়া task-টা পড়ে ঠিক Chief of Staff-এর
দিকে পাঠানো, আর gated কাজ হলে ApprovalGateway দিয়ে আটকে রাখা।

এই ফাইল ইঞ্জিন নয় — আসল worker engine ~/workspace/boss-ceo/ তে আছে
(15 worker, mock-tested + 1 live run)। এখানে engine-কে duplicate করা
হয়নি; Phase 1 থেকে Agency Chief (01-Agency-Department/
chief_of_staff_agency.py) engine-কে import করে ডাকে।

Jarvis (voice) আর Main CEO Bot (brain) আলাদা module — jarvis_voice.py
দেখুন। Gemini-র map-এ ওরা একসাথে মিশে গিয়েছিল, সেটা এখানে ঠিক করা
হয়েছে।
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_approval_gateway import ApprovalGateway, GATED_ACTIONS  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "00-CEO-Core", "config.json")

# REUSED engine — duplicate নয়, শুধু path reference (Phase 1-এ import হবে)
BOSS_CEO_ENGINE_PATH = os.path.expanduser("~/workspace/boss-ceo")

# business key -> Chief of Staff module (Phase 0: stub module-গুলো)
CHIEF_MODULES = {
    "agency": "01-Agency-Department.chief_of_staff_agency",
    "digital-product": "02-Digital-Product-Department.chief_of_staff_products",
    "content": "03-Content-Creation-Department.chief_of_staff_content",
}


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def route_task(task, tasks_path=None, approvals_path=None):
    """task = {"business": "agency"|"digital-product"|"content", "title": ..., "detail": ...}

    Agency হলে আসল Chief of Staff (Phase 1) কাজ করে — task type
    অনুযায়ী real boss-ceo worker-এর দিকে যায়, gated কাজ approval-এ
    আটকায়। Digital Product হলে আসল Products Chief (Phase 2) কাজ করে —
    kit শুধু blueprint, launch/sale Gate 0-তে আটকায়। Content হলে আসল
    Content Chief (Phase 3) কাজ করে — Creator OS-র ৬ worker ডাকে, draft
    বানায়, publish/upload gate-এ আটকায়, video file বানায় না।
    Gated action থাকলে task এগোয় না — approval request pending থাকে।
    """
    config = load_config()
    business = task.get("business")
    if business not in CHIEF_MODULES:
        raise ValueError(f"Unknown business: {business!r}. Known: {list(CHIEF_MODULES)}")

    if business == "agency":
        # Lazy import — Chief-এর engine import শুধু agency task-এ লাগে।
        chief_path = os.path.join(BASE_DIR, "01-Agency-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_agency  # noqa: PLC0415

        chief_result = chief_of_staff_agency.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path
        )
        return {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
        }

    if business == "digital-product":
        # Phase 2: Products Chief REAL — Gate 0 না পাস হওয়া পর্যন্ত
        # launch/sale আটকায়, kit শুধু blueprint হিসেবে আসে।
        chief_path = os.path.join(BASE_DIR, "02-Digital-Product-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_products  # noqa: PLC0415

        chief_result = chief_of_staff_products.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path
        )
        return {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
        }

    if business == "content":
        # Phase 3: Content Chief REAL — Creator OS-র ৬ worker ডাকে
        # (mock brain, $0), draft বানায়, publish/upload gate-এ আটকায়।
        # video file বানায় না, upload script চালায় না।
        chief_path = os.path.join(BASE_DIR, "03-Content-Creation-Department")
        if chief_path not in sys.path:
            sys.path.insert(0, chief_path)
        import chief_of_staff_content  # noqa: PLC0415

        chief_result = chief_of_staff_content.handle_task(
            task, tasks_path=tasks_path, approvals_path=approvals_path
        )
        return {
            "routed_to": CHIEF_MODULES[business],
            "business": business,
            "title": task.get("title"),
            "status": chief_result["status"],
            "chief_result": chief_result,
            "approval": chief_result.get("approval"),
            "spend_cap_usd": config["spend_cap_usd"],
        }

    approval = None
    action = task.get("gated_action")
    if action:
        if action not in GATED_ACTIONS:
            raise ValueError(f"Unknown gated action: {action!r}")
        gateway = ApprovalGateway()
        approval = gateway.request(action, task.get("detail", task.get("title", "")), task.get("requested_by", "Main CEO Bot"))
        # NOTE: এখানেই থেমে যায়। approve() শুধু Boss-এর gate word-এ চলে।

    return {
        "routed_to": CHIEF_MODULES[business],
        "business": business,
        "title": task.get("title"),
        "status": "routed-pending-approval" if approval else "routed-stub",
        "note": "Phase 3: Agency + Digital Product + Content Chiefs are REAL. Only Jarvis voice stays a STUB.",
        "approval": approval,
        "spend_cap_usd": config["spend_cap_usd"],
    }


if __name__ == "__main__":
    # হাতে চেক: শুধু non-gated routing। TEMP paths ব্যবহার করা হয়,
    # যাতে আসল store/tasks.json-এ test record না জমে।
    import tempfile  # noqa: PLC0415

    _tmp_tasks = os.path.join(tempfile.mkdtemp(), "tasks-test.json")
    _tmp_appr = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
    r1 = route_task({"business": "agency", "title": "test route"},
                    tasks_path=_tmp_tasks, approvals_path=_tmp_appr)
    assert r1["routed_to"].endswith("chief_of_staff_agency")
    assert r1["status"] == "route-only"  # Phase 1: type ছাড়া task = probe only
    assert r1["chief_result"]["department"] == "agency"
    print("main_ceo_bot: OK (routing works, Agency Chief is REAL)")
