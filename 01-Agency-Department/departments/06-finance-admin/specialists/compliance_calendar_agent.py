"""Compliance Calendar Agent — compliance dates draft (Dept 06, Phase 3).

ভূমিকা (role): শুধু compliance তারিখের হিসাবের DRAFT বানানো — কখনো
deadline বানায় না, legal পরামর্শ দেয় না, আইনি দাবি করে না।
Gate: None — draft নিজেই নিরাপদ।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

জানা সত্য (2026-11-19): attorney review (service agreement) DEFERRED
— প্রথম paying client-এর আগে নয়, তারিখ নেই; dental/medical ব্যবসা
কখনো target নয় (সবসময় DQ); সাপ্তাহিক cadence রবিবার 6 PM Dhaka।
এর বাইরে কোনো compliance তারিখ জানা নেই — সব "BOSS INPUT REQUIRED"।

এই agent কখনো করে না: deadline/তারিখ বানায় না, legal পরামর্শ দেয়
না, আইনি দাবি করে না, কিছু পাঠায় না, খরচ করে না, কোনো guarantee
দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ComplianceCalendarAgent:
    """Compliance calendar DRAFT ONLY — কখনো deadline বানায় না।"""

    task_kind = "compliance_calendar"
    gate = None
    department = "06-finance-admin"
    role = "Compliance Calendar Agent"

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
            "Compliance calendar draft for Talvenor. "
            f"Topic: {topic}. "
            "Known only: attorney review is DEFERRED until the first "
            "paying client; dental/medical is never targeted; weekly "
            "cadence is Sunday 6 PM Dhaka. Do not invent any deadline, "
            "date, or legal claim; mark missing facts "
            "'BOSS INPUT REQUIRED'. No legal advice. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Compliance calendar DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Compliance calendar"
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
            brain_text = "No brain passed — calendar built from task only."

        output = (
            "[MOCK DRAFT] Compliance calendar — DRAFT ONLY\n"
            f"Department: {self.department} | Worker: {self.role}\n"
            "Known compliance items (শুধু জানা সত্য):\n"
            "- Attorney review (service agreement): DEFERRED — প্রথম paying "
            "client-এর আগে নয়; তারিখ নেই।\n"
            "- Dental/medical targeting: কখনো নয় — সবসময় DQ।\n"
            "- Weekly content plan + report: প্রতি রবিবার 6 PM Dhaka।\n"
            "- অন্য compliance তারিখ: BOSS INPUT REQUIRED — কোনো তারিখ বানানো নয়।\n"
            "Attorney review-এর তারিখ প্রথম paying client এলে Boss ঠিক করবেন।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Compliance calendar ONLY — "
            "কোনো deadline/তারিখ বানানো হয়নি, কোনো legal দাবি নয়। "
            "Attorney review deferred until first paying client। Gate: None।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
