"""Call Monitoring Agent — call-monitoring plan/checklist draft (Dept 04).

ভূমিকা (role): Sophia-র live call-এর জন্য কী check করতে হবে, তার
plan/checklist-এর DRAFT লেখা — কখনো live call দেখে না, live call-এর
data দাবি করে না।
Gate: none — checklist DRAFT নিজেই নিরাপদ, কিছু পাঠানো হয় না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

সত্য: live monitoring-এর কোনো automated access নেই — worker-এর কাছে
Sophia-র live call দেখার কোনো উপায় নেই। Checklist DRAFT Boss-কে যায়;
Boss নিজে Vapi dashboard-এ গিয়ে আসল call দেখে যাচাই করেন।
Live stack: Vapi/Sophia, +1 (947) 223-0244, GPT-4o-mini, Emma voice,
Deepgram nova-3। Paying clients 0 — কোনো real client-এর call-এ এই
checklist এখনো test হয়নি।

এই agent কখনো করে না: live call দেখে না, শোনে না, call-এর সংখ্যা/
transcript/ফলাফল বানায় না, কিছু পাঠায় না, দাম quote করে না, কোনো
guarantee দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class CallMonitoringAgent:
    """Call-monitoring checklist DRAFT ONLY — live call দেখে না।"""

    task_kind = "call_monitoring"
    gate = None
    department = "04-client-operations"
    role = "Call Monitoring Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — top level-এ কোনো repo import নয়।"""
        here = os.path.dirname(os.path.abspath(__file__))
        ceo_core = os.path.normpath(os.path.join(
            here, "..", "..", "..", "..", "00-CEO-Core"))
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        from human_approval_gateway import ApprovalGateway
        if approvals_path:
            return ApprovalGateway(approvals_path=approvals_path)
        return ApprovalGateway()

    def _request_approval(self, gateway, gated_action, title):
        """PENDING approval record করা — execute নয়, auto-approve নয়।"""
        action = _GATE_ACTION_MAP.get(gated_action, gated_action)
        if action in _GATED_ACTIONS:
            return gateway.request(action, title, type(self).__name__)
        return {
            "id": None,
            "action": gated_action,
            "detail": title,
            "requested_by": type(self).__name__,
            "status": "pending",
            "note": "Gate word approval needed; not a gateway action, so no record was written.",
        }

    def _prompt(self, task):
        payload = task.get("payload") or {}
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        return (
            "Call-monitoring checklist draft for a Talvenor client. "
            f"Client: {client}. Live receptionist is Vapi/Sophia. "
            "Cover: greeting, life-safety check, intent, qualify, "
            "action, confirm, log, close. The worker has no access to "
            "live calls — the checklist is for Boss to verify by hand "
            "in the Vapi dashboard. Do not invent call numbers, "
            "transcripts, or results; mark missing facts "
            "'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Call-monitoring checklist DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Call monitoring checklist draft"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        if gated_action:
            gw = gateway if gateway is not None else self._gateway(approvals_path)
            approved = False
            if approval_id:
                try:
                    approved = gw.is_approved(approval_id)
                except KeyError:
                    approved = False
            if not approved:
                approval = self._request_approval(gw, gated_action, title)
                return {
                    "status": "pending-approval",
                    "approval": approval,
                    "draft_only": True,
                    "mock_brain": True,
                    "gate": self.gate,
                }

        payload = task.get("payload") or {}
        client = payload.get("client") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — checklist built from payload only."

        output = (
            "[MOCK DRAFT] Call monitoring — checklist DRAFT ONLY\n"
            f"Client: {client}\n"
            "Live receptionist: Vapi/Sophia, +1 (947) 223-0244 "
            "(GPT-4o-mini, Emma voice, Deepgram nova-3).\n"
            "NO live call access — this worker never sees a live call. "
            "Boss verifies each check by hand in the Vapi dashboard.\n"
            "Checklist (what to check, where to check it):\n"
            "1. Greeting — Sophia greets by business name, plain US English "
            "(check: Vapi call log).\n"
            "2. Life-safety check — emergency call gets redirected, never "
            "booked (check: Vapi call log).\n"
            "3. Intent — caller intent caught correctly: new job, existing "
            "job, question, other (check: Vapi call log).\n"
            "4. Qualify — name, phone, service, area asked and logged "
            "(check: Vapi call log).\n"
            "5. Action — booking offered via booking link "
            f"{BOOKING_LINK} (15 min, New York Time) or message taken "
            "(check: Vapi call log + calendar).\n"
            "6. Confirm — caller hears the booking/message back, confirmed "
            "(check: Vapi call log).\n"
            "7. Log — call logged with outcome (check: Vapi call log).\n"
            "8. Close — polite close, no invented promise (check: Vapi call log).\n"
            "Paying clients: 0 — no real client call tested yet; this is a "
            "DRAFT checklist only.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Call-monitoring checklist DRAFT "
            "ONLY, live monitoring নয় — worker-এর live call-এর কোনো access "
            "নেই, কোনো live call data দাবি করা হয়নি। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
