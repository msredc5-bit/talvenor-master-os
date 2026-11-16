"""Kit QA — Vet No-Show Recovery Kit-এর ৬ অংশের QA checklist (section agent, NEW)।

Role (ভূমিকা): kit-outline.md-এর ৬ অংশের বিপরীতে QA checklist DRAFT
লেখা — কোনো অংশ বানানো হয়েছে কি না, হলে কী যাচাই করতে হবে।
Gate (গেট): QA ফলাফল ব্যবহার করতে Boss-এর `ok` লাগে।
Gate 0 status (গেট ০ অবস্থা): **NOT PASSED** — kit-এর ৬ অংশের কোনোটা
বানানো হয়নি (0/6), তাই QA করার মতো কিছু নেই। এই agent ফেরত দেয়:
"NOT BUILT — nothing to QA yet" + প্রতিটা অংশের QA checklist DRAFT।
যা কখনো করে না: কোনো অংশ pass বলে দাবি করে না (কিছু বানানোই হয়নি);
kit বানায় না; কোনো file লেখে না; client/testimonial/statistic বানায়
না; network ছোঁয় না।
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

# (slug, QA checklist — kit-outline.md থেকে, Gate 0-র পরে যাচাই করতে হবে)
KIT_QA_ITEMS = [
    ("reminder-cadence-pack",
     "T-72h / T-24h / T-2h তিনটে touch আছে কি না; [NAME] / [PET] / [TIME] field আছে কি না; "
     "Gate 1: cadence + script AAHA/PetDesk-এর published guidance-এর সাথে মেলে কি না।"),
    ("same-day-rebooking",
     "Phone script + in-person script দুটোই plain US English কি না; slot সেদিনই আবার ভরার কথা আছে কি না।"),
    ("waitlist-fill-sop",
     "এক পাতা কি না; কাকে আগে ফোন করবে + কোন order-এ + exact call script আছে কি না।"),
    ("no-show-log-tracker",
     "Formula auto-total করে কি না (sample সংখ্যা দিয়ে test); মাসের miss / আনুমানিক $ loss / recovery rate তিনটে দেখায় কি না।"),
    ("deposit-policy-template",
     "'have your own attorney review before using' লেখা আছে কি না; legal advice হিসেবে দেওয়া হয়নি তো।"),
    ("front-desk-quick-card",
     "৫ লাইন কি না; এক পাতা কি না; reception desk-এ রাখার মতো কি না।"),
]

GLOBAL_QA_CHECKS = [
    "'Talvenor' বানান সব জায়গায় ঠিক কি না।",
    "কোনো invented client / testimonial / statistic নেই তো।",
    "PIMS (practice-management software) replace করার দাবি নেই তো — kit PIMS-এর পাশে কাজ করে।",
    "$49 price-এর verified sale আছে বলে দাবি নেই তো (price inference, observed traction নয়)।",
    "কোনো clinic-কে দুইবার মেইল করার plan নেই তো।",
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


class KitQAAgent:
    """Kit-এর ৬ অংশের QA checklist DRAFT দেয় — কোনো অংশ pass বলে না।"""

    task_kind = "kit_qa"
    gate = "ok"
    section = "product"
    role = "Kit QA"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        blueprint = _read_dept_file("kit-outline.md")
        lines = [
            "NOT BUILT — nothing to QA yet",
            "Vet No-Show Recovery Kit ($49 one-time) — ৬ অংশের কোনোটা বানানো হয়নি (0/6)।",
            "QA করার মতো কিছু নেই। নিচের checklist DRAFT — Gate 0 পাস + build-এর পরে প্রতিটা অংশের বিপরীতে যাচাই করতে হবে।",
            "Blueprint source: kit-outline.md (present: %s, chars: %d)।" % (
                blueprint is not None, len(blueprint) if blueprint else 0),
            "",
            "Per-part QA checklist (DRAFT):",
        ]
        for i, (slug, checks) in enumerate(KIT_QA_ITEMS, 1):
            lines.append("  %d. %s — status: NOT BUILT" % (i, slug))
            lines.append("     Checks: %s" % checks)
        lines.append("")
        lines.append("Global checks (সব অংশে):")
        for item in GLOBAL_QA_CHECKS:
            lines.append("  - %s" % item)
        lines.append("")
        lines.append("Verdict: কোনো অংশ QA পাস করেনি — কিছু বানানোই হয়নি। Checklist DRAFT only।")
        static_text = "\n".join(lines)
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit QA checklist draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section,
                "parts_built": 0, "parts_total": len(KIT_QA_ITEMS),
                "output": output,
                "notes": "কোনো অংশ QA পাস করেনি — কিছু বানানোই হয়নি। Checklist DRAFT; build-এর পরে আবার QA করতে হবে।",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
