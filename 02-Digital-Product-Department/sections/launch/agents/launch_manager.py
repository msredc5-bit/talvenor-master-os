"""Launch Manager — Vet Kit launch checklist DRAFT (section agent)।

Role (ভূমিকা): launch-এর checklist DRAFT বানানো — Gate 0, kit-এর ৬ অংশ,
Gate 1 যাচাই, store listing, sales page, 100 clinic-কে মেইল, reply + sale
sheet-এ লেখা।
Gate (গেট): launch এগোতে Boss-এর `go` লাগে।
Gate 0 status (গেট ০ অবস্থা): **NOT PASSED** — launch করা যাবে না। এই
agent শুধু DRAFT checklist দেয়, status `blocked-gate0`; launch হিসেবে
কিছু চিহ্নিত করে না, sale লেখে না।
যা কখনো করে না: launch করে না; mark_launched / mark_sold মানে না; কোনো
file লেখে না; মেইল পাঠায় না; client/testimonial/statistic বানায় না;
network ছোঁয় না।
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

LAUNCH_CHECKLIST = [
    "Gate 0 পাস (Lemon Squeezy store খোলে কি না) — এখনো NOT PASSED",
    "Kit-এর ৬ অংশ বানানো (Sheets + Docs + script) — এখনো হয়নি (0/6)",
    "Cadence AAHA/PetDesk guidance-এর সাথে যাচাই (Gate 1) — এখনো হয়নি",
    "Lemon Squeezy listing + Gumroad backup listing — এখনো হয়নি",
    "Sales page — Boss review করবেন launch-এর আগে",
    "100 clinic-কে ২৫টা করে মেইল (৪ দিন) — email channel এখন PAUSED (2026-11-14 থেকে)",
    "প্রতিটা reply + sale sheet-এ লেখা — sale এখনো 0",
]


def _dept_dir():
    """kit-outline.md খুঁজে department dir বের করা (read-only source)।"""
    here = os.path.dirname(os.path.abspath(__file__))
    node = here
    for _ in range(6):
        if os.path.isfile(os.path.join(node, "kit-outline.md")):
            return node
        node = os.path.dirname(node)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


def _read_dept_file(name):
    try:
        with open(os.path.join(_dept_dir(), name), "r", encoding="utf-8") as f:
            return f.read()
    except (FileNotFoundError, OSError):
        return None


def _gate0_status():
    """gate0-status.md-এর Status লাইন পড়া — PASSED না লেখা থাকলে NOT PASSED (fail-closed)।"""
    text = _read_dept_file("gate0-status.md")
    if text is None:
        return {"status": "NOT PASSED",
                "note": "gate0-status.md পড়া যায়নি — fail-closed: NOT PASSED ধরা হয়েছে।"}
    for line in text.splitlines():
        stripped = line.strip().lstrip("*").strip()
        if stripped.startswith("Status:"):
            value = stripped[len("Status:"):].strip().lstrip("*").strip()
            if value.startswith("PASSED"):
                return {"status": "PASSED",
                        "note": "gate0-status.md-এ Status: PASSED লেখা আছে।"}
            return {"status": "NOT PASSED",
                    "note": "Gate 0 পাস হয়নি — Lemon Squeezy signup test Boss-এর step, এখনো বাকি।"}
    return {"status": "NOT PASSED",
            "note": "gate0-status.md-এ Status লাইন পাওয়া যায়নি — fail-closed: NOT PASSED ধরা হয়েছে।"}


def _load_gateway(gateway, approvals_path):
    """ApprovalGateway lazy import — শুধু gated কাজে দরকার হলে।"""
    if gateway is not None:
        return gateway
    ceo_core = os.path.join(os.path.dirname(_dept_dir()), "00-CEO-Core")
    if ceo_core not in sys.path:
        sys.path.insert(0, ceo_core)
    from human_approval_gateway import ApprovalGateway  # noqa: PLC0415
    if approvals_path:
        return ApprovalGateway(approvals_path=approvals_path)
    return ApprovalGateway()


def _draft_with_brain(brain, prompt, static_text):
    """brain থাকলে brain.complete(prompt) ব্যবহার করে [MOCK DRAFT] লেখা;
    না থাকলে static DRAFT text। কখনো live call / network নয় — brain mock।"""
    if brain is not None:
        try:
            mock_text = brain.complete(prompt)
        except Exception:  # noqa: BLE001
            mock_text = ""
        if mock_text:
            return "[MOCK DRAFT]\n" + str(mock_text) + "\n\n---\n" + static_text
    return "DRAFT ONLY\n" + static_text


def _gated_check(agent, task, gateway, approvals_path):
    """gated_action থাকলে PENDING ফেরত দেয়; approved হলে None (শুধু DRAFT-এ
    এগোনো যাবে — agent কখনো gated action execute করে না)।"""
    gated_action = (task or {}).get("gated_action")
    if not gated_action:
        return None
    if gated_action not in GATED_ACTIONS:
        return {"status": "error",
                "error": "Unknown gated action %r." % (gated_action,),
                "draft_only": True, "mock_brain": True, "gate": agent.gate}
    gw = _load_gateway(gateway, approvals_path)
    approval_id = task.get("approval_id")
    if approval_id:
        try:
            if gw.is_approved(approval_id):
                return None
        except Exception:  # noqa: BLE001
            pass
    approval = gw.request(gated_action, task.get("title") or agent.task_kind,
                          "Digital-Product-Section-Agent")
    return {"status": "pending-approval", "approval": approval,
            "draft_only": True, "mock_brain": True, "gate": agent.gate}


class LaunchManagerAgent:
    """Launch checklist DRAFT দেয় — launch নিজে করে না।"""

    task_kind = "launch_prep"
    gate = "go"
    section = "launch"
    role = "Launch Manager"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        checklist_text = "\n".join(
            "  %d. %s" % (i, item)
            for i, item in enumerate(LAUNCH_CHECKLIST, 1))
        summary = (
            "Launch checklist DRAFT — Vet No-Show Recovery Kit ($49 one-time)।\n"
            + checklist_text + "\n"
            "Gate 0: %s। Kit বানানো: 0/6। PA list: 39/100। Sale: 0।" % gate0["status"])
        if payload.get("mark_sold") or payload.get("mark_launched"):
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "Launch/sale দাবি Gate 0-তে আটকে আছে — কিছুই launched/sold হিসেবে লেখা হয়নি, sale এখনো 0।",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        if gate0["status"] != "PASSED":
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "DRAFT checklist only — launch করা হয়নি, করা যাবে না। Gate 0 পাস না হওয়া পর্যন্ত launch আটকে আছে।",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit launch checklist draft", summary)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0, "output": output,
                "notes": "Gate 0 পাস হয়েছে — launch এগোতে Boss-এর 'go' লাগবে। Checklist DRAFT only; launch এই agent করে না।",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
