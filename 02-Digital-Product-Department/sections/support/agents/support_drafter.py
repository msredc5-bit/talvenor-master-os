"""Support Drafter — kit buyer-দের reply DRAFT (section agent)।

Role (ভূমিকা): kit buyer-দের প্রশ্নের reply-এর DRAFT লেখা — delivery,
file খোলা, tracker formula, script ব্যবহার, refund, policy template —
plain US English, DRAFT only।
Gate (গেট): পাঠাতে Boss-এর `send` লাগে। DRAFT নিজেই নিরাপদ।
Gate 0 status (গেট ০ অবস্থা): **BLOCKED (কাজ নেই এখন)** — sale 0, তাই
কোনো buyer নেই, কোনো support প্রশ্নও নেই। এই agent-এর output সবসময়
template — প্রথম sale-এর পরেই আসল buyer-reply কাজ শুরু হবে। প্রতিটা
output-এ সৎ note থাকে: sale 0, no live buyers yet।
যা কখনো করে না: legal advice দেয় না — policy template-এ সবসময় "have
your own attorney review before using" লেখে; refund policy বানায় না
(ঠিক হয়নি — BOSS INPUT REQUIRED); invented buyer-এর প্রশ্নের উত্তর
আসল message হিসেবে চালায় না; কোনো file লেখে না; network ছোঁয় না।
"""

import os
import sys

KIT_PRICE_USD_ONE_TIME = 49
BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
PHONE = "+1 (947) 223-0244"
GATED_ACTIONS = ("send", "publish", "spend", "delete")

HONEST_NOTE = ("Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale. "
               "DRAFT ONLY — not sent.")

TEMPLATES = {
    "delivery": (
        "Hi, thanks for getting the Vet No-Show Recovery Kit!\n\n"
        "Your files were delivered by download link (Lemon Squeezy; Gumroad backup). "
        "The kit is Google Sheets + Google Docs + copy-paste scripts — no code, no app, nothing to install. "
        "Open the Sheets tracker and the Docs files with a Google account. The 6 parts are: "
        "Reminder Cadence Pack, Same-Day Rebooking Scripts, Waitlist-Fill SOP, "
        "No-Show Log + $ Tracker, Deposit / No-Show Policy Template, and Front-Desk Quick Card.\n\n"
        "If a file won't open, reply to this email and tell us which one — we'll help.\n\n"
        "Best,\nMainuddin — Talvenor"),
    "tracker": (
        "Hi, thanks for asking about the $ tracker!\n\n"
        "In the No-Show Log + $ Tracker sheet, log each no-show on its own row. "
        "The formulas auto-total: how many appointments were missed this month, "
        "the estimated $ lost, and your recovery rate. Try it with a few sample numbers first — "
        "if the totals don't add up, reply here and tell us what you entered.\n\n"
        "Best,\nMainuddin — Talvenor"),
    "script": (
        "Hi, thanks for asking about the reminder scripts!\n\n"
        "Each script has [NAME] / [PET] / [TIME] fields — replace those with the client's details before you send or call. "
        "The cadence is T-72h, then T-24h, then T-2h (SMS + email + phone-call script at each step). "
        "Use the same-day rebooking script when a client no-shows or cancels late, so the slot can be filled the same day.\n\n"
        "Best,\nMainuddin — Talvenor"),
    "refund": (
        "Hi, thanks for writing about a refund.\n\n"
        "I'll confirm our refund terms and get back to you shortly — I don't want to give you the wrong answer here.\n\n"
        "Best,\nMainuddin — Talvenor"),
    "policy": (
        "Hi, thanks for asking about the policy template!\n\n"
        "The Deposit / No-Show Policy Template is a plain-words starting point your clinic can adopt. "
        "Please have your own attorney review before using — this template is not legal advice.\n\n"
        "Best,\nMainuddin — Talvenor"),
    "general": (
        "Hi, thanks for writing!\n\n"
        "The Vet No-Show Recovery Kit has 6 parts: Reminder Cadence Pack (T-72h / T-24h / T-2h), "
        "Same-Day Rebooking Scripts, Waitlist-Fill SOP, No-Show Log + $ Tracker, "
        "Deposit / No-Show Policy Template, and Front-Desk Quick Card. "
        "Tell us which part your question is about and we'll walk you through it.\n\n"
        "Best,\nMainuddin — Talvenor"),
}


def _dept_dir():
    """kit-outline.md খুঁজে department dir বের করা (read-only source)।"""
    here = os.path.dirname(os.path.abspath(__file__))
    node = here
    for _ in range(6):
        if os.path.isfile(os.path.join(node, "kit-outline.md")):
            return node
        node = os.path.dirname(node)
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(here))))


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


class SupportDrafterAgent:
    """Buyer-reply DRAFT (template) লেখে — পাঠায় না।"""

    task_kind = "support_draft"
    gate = "send"
    section = "support"
    role = "Support Drafter"

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        task = task or {}
        blocked = _gated_check(self, task, gateway, approvals_path)
        if blocked is not None:
            return blocked
        payload = task.get("payload") or {}
        topic = (payload.get("topic") or "general").strip().lower()
        if topic not in TEMPLATES:
            topic = "general"
        buyer_message = (payload.get("buyer_message") or "").strip()
        header = HONEST_NOTE + "\n"
        if buyer_message:
            header += "Replying to buyer message (Boss-forwarded): \"%s\"\n" % buyer_message
        else:
            header += "No real buyer message yet — template for topic '%s' (kit-outline.md থেকে)।\n" % topic
        if topic == "refund":
            header += "BOSS INPUT REQUIRED: refund policy এখনো ঠিক হয়নি — draft-এ কোনো refund promise নেই।\n"
        if topic == "policy":
            header += "Policy template legal advice নয় — draft-এ 'have your own attorney review before using' আছে।\n"
        static_text = header + "\n" + TEMPLATES[topic]
        output = _draft_with_brain(
            brain, "Vet Kit support reply draft (%s)" % topic, static_text)
        return {"status": "draft-ready", "task_kind": self.task_kind,
                "section": self.section, "topic": topic,
                "output": output,
                "notes": HONEST_NOTE + " Topic: %s। পাঠাতে Boss-এর 'send' লাগবে।" % topic,
                "draft_only": True, "mock_brain": True, "gate": self.gate}
