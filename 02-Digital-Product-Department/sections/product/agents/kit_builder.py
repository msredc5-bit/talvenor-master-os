"""Kit Builder — Vet No-Show Recovery Kit-এর ৬ অংশের builder (section agent)।

Role (ভূমিকা): kit-outline.md-এর blueprint (নকশা) পড়ে kit-এর ৬ অংশের
সারাংশ + build order ফেরত দেওয়া।
Gate (গেট): build শুরু করতে / output ব্যবহার করতে Boss-এর `ok` লাগে।
Gate 0 status (গেট ০ অবস্থা): **NOT PASSED** — Lemon Squeezy signup test
Boss-এর step, এখনো বাকি। তাই এই agent kit-এর কোনো অংশ বানায় না; শুধু
blueprint-এর সারাংশ + build order দেয়, status `blocked-gate0`।
যা কখনো করে না: kit-এর কোনো অংশ (Sheets/Docs) বানায় না, কোনো file লেখে
না, sale/launch হিসেবে কিছু চিহ্নিত করে না, client/testimonial/statistic
বানায় না, $49-এর verified sale আছে বলে দাবি করে না, network ছোঁয় না।
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
KIT_LAUNCH_PRICE_USD_ONE_TIME = 39
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
PA_LIST_TARGET = 100
GATED_ACTIONS = ("send", "publish", "spend", "delete")

KIT_PARTS = [
    ("reminder-cadence-pack", "Reminder Cadence Pack — T-72h / T-24h / T-2h SMS + email + call script"),
    ("same-day-rebooking", "Same-Day Rebooking Scripts — phone + in-person script"),
    ("waitlist-fill-sop", "Waitlist-Fill SOP — এক পাতার SOP + call script"),
    ("no-show-log-tracker", "No-Show Log + $ Tracker — Sheets, formula সহ"),
    ("deposit-policy-template", "Deposit / No-Show Policy Template — attorney-review note সহ"),
    ("front-desk-quick-card", "Front-Desk Quick Card — ৫ লাইন, এক পাতা"),
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


class KitBuilderAgent:
    """Kit-এর blueprint সারাংশ + build order দেয় — kit নিজে বানায় না।"""

    task_kind = "kit_build"
    gate = "ok"
    section = "product"
    role = "Kit Builder"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        blueprint = _read_dept_file("kit-outline.md")
        parts_text = "\n".join(
            "  %d. %s — %s" % (i, slug, name)
            for i, (slug, name) in enumerate(KIT_PARTS, 1))
        build_order = (
            "Build order (kit-outline.md — Gate 0-র পরে, ৩–৪ সপ্তাহ, দিনে ১ ঘণ্টা, $0):\n"
            "  Week 0 — Gate 0: Lemon Squeezy signup test (Boss-এর step)\n"
            "  Week 1 — Validate + list: cadence AAHA/PetDesk যাচাই (Gate 1); PA list 100-এ পূর্ণ করা\n"
            "  Week 2 — Build: ৬ অংশ Sheets/Docs-এ বানানো; $ tracker formula sample-এ test; policy-তে attorney-review note\n"
            "  Week 3 — Store + sales page: Lemon Squeezy listing (primary) + Gumroad (backup); sales page (Boss review)\n"
            "  Week 4 — Launch: দিনে ২৫ মেইল, 100 clinic-কে (৪ দিন); reply + sale sheet-এ লেখা")
        summary = (
            "BLUEPRINT ONLY — Vet No-Show Recovery Kit ($49 one-time; প্রথম ৩০ buyer-এর জন্য launch price $39)।\n"
            "Format: Google Sheets + Google Docs + copy-paste script। কোড নেই, app নেই, install করতে হয় না।\n"
            "কার জন্য: independent companion-animal vet clinic, ১–৫ vet (corporate chain নয়, solo mobile vet নয়)।\n"
            "Kit-এর ৬ অংশ (কোনোটা বানানো হয়নি — 0/6):\n" + parts_text + "\n" + build_order + "\n"
            "Blueprint source: kit-outline.md (present: %s, chars: %d)।" % (
                blueprint is not None, len(blueprint) if blueprint else 0))
        if payload.get("mark_sold") or payload.get("mark_launched"):
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "Sale/launch দাবি Gate 0-তে আটকে আছে — কিছুই sold/launched হিসেবে লেখা হয়নি, sale এখনো 0।",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        if gate0["status"] != "PASSED":
            return {"status": "blocked-gate0", "task_kind": self.task_kind,
                    "section": self.section, "gate0": gate0, "output": summary,
                    "notes": "Gate 0 NOT PASSED — kit-এর কোনো অংশ বানানো যাবে না। এটা blueprint-এর সারাংশ + build order, kit নিজে নয়।",
                    "draft_only": True, "mock_brain": True, "gate": self.gate}
        output = _draft_with_brain(
            brain, "Vet No-Show Recovery Kit build order draft", summary)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0, "output": output,
                "notes": "Gate 0 পাস হয়েছে — build শুরু করতে Boss-এর 'ok' লাগবে। এই agent কোনো file বানায় না; build order plan দেয়।",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
