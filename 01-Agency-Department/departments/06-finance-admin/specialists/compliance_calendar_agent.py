"""Compliance Calendar Agent — compliance dates draft (Dept 06, Phase 3).

Role: only make a DRAFT of the compliance date account — never
invent a deadline, give legal advice, or make a legal claim.
Gate: None — the draft itself is safe.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Known facts (2026-11-19): attorney review (service agreement) DEFERRED
— not before the first paying client, no date; dental/medical business
is never a target (always DQ); weekly cadence Sunday 6 PM Dhaka.
No compliance date is known beyond this — all "BOSS INPUT REQUIRED".

This agent never: invents a deadline/date, gives legal advice,
makes a legal claim, sends anything, spends anything, gives any guarantee
gives none, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ComplianceCalendarAgent:
    """Compliance calendar DRAFT ONLY — never invents a deadline."""

    task_kind = "compliance_calendar"
    gate = None
    department = "06-finance-admin"
    role = "Compliance Calendar Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — no repo import at top level."""
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
        """Record a PENDING approval — not execute, not auto-approve."""
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
        """Making a compliance calendar DRAFT. Writes no file, touches no network."""
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
            "Known compliance items (only known facts):\n"
            "- Attorney review (service agreement): DEFERRED — not before the first paying client; no date.\n"
            "- Dental/medical targeting: never — always DQ.\n"
            "- Weekly content plan + report: every Sunday 6 PM Dhaka.\n"
            "- Other compliance dates: BOSS INPUT REQUIRED — no date invented.\n"
            "Boss will set the attorney review date when the first paying client comes.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Compliance calendar ONLY — "
            "No deadline/date was invented, no legal claim. "
            "Attorney review deferred until first paying client. Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
