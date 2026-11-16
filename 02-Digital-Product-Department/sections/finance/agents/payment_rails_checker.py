"""Payment-Rails Checker — Gate 0 test steps + Boss-এর ফলাফল record (section agent)।

Role (ভূমিকা): Gate 0 test-এর ধাপগুলো লেখা আর Boss-এর ফলাফল record করা —
Lemon Squeezy signup (BD individual হিসেবে), ফেল হলে fallback order:
Polar → Gumroad (individual হিসেবে, LLC নয়)।
Gate (গেট): কোনো gate নেই — এটা শুধু যাচাই + record।
Gate 0 status (গেট ০ অবস্থা): **NOT PASSED** — এই role-ই Gate 0 দেখে,
কিন্তু নিজে কখনো "PASSED" লেখে না। Boss-এর ফলাফল শুধু Boss জানালে record
হয় (verbatim quote হিসেবে); gate0-status.md-এর Status লাইন এই agent
বদলায় না — কোনো file-ই লেখে না।
যা কখনো করে না: নিজে Lemon Squeezy / Polar / Gumroad-এ signup করে না;
নিজে থেকে Gate 0 PASSED বলে না; Etsy কখনো plan-এ আনে না (Bangladesh-এর
জন্য বন্ধ — hard no); কোনো file লেখে না; network ছোঁয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

GATE0_STEPS = [
    "1. lemonsqueezy.com-এ যান — Individual হিসেবে signup করুন (MAINUDDIN LLC নয় — LLC US-registered, US bank নেই বলে individual-ই সঠিক পথ)।",
    "2. Payout method দেখুন — BD bank payout দেখা যায় কি না।",
    "3. ফলাফল Boss-কে জানান: পাস / ফেল / কী বলল (screenshot দিলে ভালো হয়)। Boss-এর step, ~15 min, $0।",
    "4. Lemon Squeezy ফেল (triage/blocked) হলে backup rail test — Polar (BD seller/payout list-এ আছে, Stripe Connect Express)।",
    "5. Polar-ও না হলে Gumroad — BD bank payout আছে, individual হিসেবে register করতে হবে (LLC নয়)।",
    "6. সব rail বন্ধ হলে product track পুরো KILL — kit বানানো হবে না, Boss-কে জানানো হবে।",
]

RAIL_FEES = [
    "Lemon Squeezy: 5% + $0.50, $50 min payout (research report §2, 2026-11-12)।",
    "Polar: 5% + $0.50।",
    "Gumroad: ~12.9% + $0.80 effective, $100 min payout।",
    "Etsy: hard no — Bangladesh-এর জন্য বন্ধ, কখনো plan-এ নেই।",
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


class PaymentRailsCheckerAgent:
    """Gate 0 test steps লেখে + Boss-এর ফলাফল record করে — signup করে না।"""

    task_kind = "gate0_check"
    gate = None
    section = "finance"
    role = "Payment-Rails Checker"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        gate0 = _gate0_status()
        lines = [
            "Gate 0 — Lemon Squeezy Signup Test (test steps + record)।",
            "Current status (gate0-status.md থেকে পড়া): %s।" % gate0["status"],
            "",
            "Test steps (Boss-এর step, ~15 min, $0 — এই agent নিজে signup করে না):",
        ]
        lines.extend("  " + step for step in GATE0_STEPS)
        lines.append("")
        lines.append("Rail fees (research report §2, 2026-11-12):")
        lines.extend("  - " + fee for fee in RAIL_FEES)
        boss_result = (payload.get("boss_result") or "").strip()
        if boss_result:
            lines.append("")
            lines.append("Boss-এর জানানো ফলাফল (record only — verbatim quote, এই agent-এর verdict নয়):")
            lines.append("  \"%s\"" % boss_result)
            lines.append("এই agent নিজে Gate 0 PASSED লেখে না। gate0-status.md-এর Status লাইন বদলানো Boss-এর কথায় manual step — এই agent কোনো file লেখে না।")
        else:
            lines.append("")
            lines.append("Boss-এর ফলাফল এখনো আসেনি — Boss test করে জানালে তবেই record হবে। এই agent নিজে থেকে PASSED/FAILED লেখে না।")
        static_text = "\n".join(lines)
        output = _draft_with_brain(
            brain, "Gate 0 payment rails test steps draft", static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "gate0": gate0,
                "boss_result_recorded": bool(boss_result),
                "output": output,
                "notes": "Gate 0-র সত্য অবস্থা gate0-status.md থেকে পড়া। Boss-এর ফলাফল ছাড়া কোনো verdict নেই।",
                "draft_only": True, "mock_brain": True, "gate": self.gate}
