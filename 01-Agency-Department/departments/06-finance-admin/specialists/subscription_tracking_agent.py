"""Subscription Tracking Agent — subscription tracking draft (Dept 06, Phase 3).

ভূমিকা (role): শুধু subscription-এর হিসাবের DRAFT বানানো — কখনো
subscription বা খরচ বানায় না, কখনো subscription কেনে না।
Gate: None — draft নিজেই নিরাপদ।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

জানা সত্য (2026-11-19): Vapi — free credit $5 (verified 2026-11-11),
paid plan এখনো নেই, paid $0; Twilio — number এখনো import হয়নি;
n8n Cloud — plan/cost জানা নেই (BOSS INPUT REQUIRED)। $0 spend cap —
Boss-এর অনুমোদন ছাড়া কোনো paid subscription নয়।

এই agent কখনো করে না: subscription/plan/cost বানায় না, subscription
কেনে না, খরচ করে না, plan বদলায় না, কিছু পাঠায় না, কোনো guarantee
দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# জানা সত্য (2026-11-19) — paid subscription $0 so far।
PAID_SUBSCRIPTIONS_TOTAL = 0

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SubscriptionTrackingAgent:
    """Subscription tracking DRAFT ONLY — কখনো subscription/cost বানায় না।"""

    task_kind = "subscription_tracking"
    gate = None
    department = "06-finance-admin"
    role = "Subscription Tracking Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "Subscription tracking draft for Talvenor. "
            f"Topic: {topic}. "
            "Known only: Vapi free credit $5, no paid plan yet; Twilio "
            "number not imported yet; n8n Cloud plan/cost unknown. "
            "Do not invent any subscription, plan, or cost; mark missing "
            "facts 'BOSS INPUT REQUIRED'. $0 spend cap. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Subscription tracking DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Subscription tracking"
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

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — tracking built from task only."

        output = (
            "[MOCK DRAFT] Subscription tracking — DRAFT ONLY\n"
            f"Department: {self.department} | Worker: {self.role}\n"
            f"Paid subscriptions total (real): ${PAID_SUBSCRIPTIONS_TOTAL} — $0 spend cap।\n"
            "Known subscriptions (শুধু জানা সত্য):\n"
            "- Vapi (live voice stack, Sophia): free credit $5, paid plan এখনো নেই।\n"
            "- Twilio: number এখনো import হয়নি — cost BOSS INPUT REQUIRED।\n"
            "- n8n Cloud (Data Tables PLANNED, live নয়): plan/cost BOSS INPUT REQUIRED।\n"
            "Boss-এর অনুমোদন ছাড়া কোনো paid subscription নয়।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Subscription tracking ONLY — "
            "কোনো subscription/plan/cost বানানো হয়নি। Paid $0 so far। "
            "Gate: None।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
