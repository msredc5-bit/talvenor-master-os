"""Calendar Integration Agent — booking-link integration draft (Dept 03, Phase 3).

ভূমিকা (role): Google Calendar Appointment Schedule booking link-এর সঙ্গে
সংযোগের DRAFT plan বানানো — কখনো live calendar ছোঁয় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই worker কখনো করে না: live calendar-এ ঢোকে না, event বানায়/বদলায়/মোছে
না, booking link বানায় না (আসল link-ই ব্যবহার করে), কিছু পাঠায় না,
খরচ করে না, দাম quote করে না, client-এর তথ্য/পরিসংখ্যান বানায় না,
কোনো guarantee দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class CalendarIntegrationAgent:
    """Booking-link integration DRAFT ONLY — কখনো live calendar ছোঁয় না।"""

    task_kind = "calendar_integration"
    gate = None
    department = "03-ai-engineering"
    role = "Calendar Integration Agent"

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
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"
        return (
            "Booking-link integration draft for a Talvenor client. "
            f"Client: {client}. Purpose: {purpose}. "
            "Booking link is the live Google Calendar Appointment Schedule "
            "link (15 min, New York Time). Describe where the link sits in "
            "the call flow. Do not invent client facts; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Booking-link integration DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Calendar integration draft"
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
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — calendar integration draft built from payload only."

        output = (
            "[MOCK DRAFT] Calendar Integration Agent — booking-link draft (DRAFT ONLY)\n"
            f"Client: {client} | Purpose: {purpose}\n"
            "Booking link (real, live):\n"
            f"- Link: {BOOKING_LINK}\n"
            "- Schedule: Talvenor Demo, 15 min, New York Time\n"
            "Where the link sits:\n"
            "- Call flow Action ধাপে: Sophia caller-কে booking link দেয়।\n"
            "- Call flow Confirm ধাপে: booking-এর বিবরণ আবার পড়ে শোনানো হয়।\n"
            "- Outreach draft-এ: 15-min demo call-এর CTA হিসেবে একই link।\n"
            "Status: DRAFT plan only — live calendar-এ কিছু বদলানো হয়নি, "
            "কোনো event বানানো/বদলানো/মোছা হয়নি।\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Booking-link integration DRAFT ONLY, "
            "কখনো live calendar ছোঁয়া নয়। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
