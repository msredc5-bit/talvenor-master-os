"""Calendar Integration Agent — booking-link integration draft (Dept 03, Phase 3).

Role: making a DRAFT plan for connecting with the Google Calendar Appointment Schedule booking link
— it never touches a live calendar.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This worker never: enters a live calendar, makes/changes/deletes an event,
makes no booking link (it uses the real link itself), sends nothing,
spends nothing, quotes no prices, invents no client facts/statistics,
Gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class CalendarIntegrationAgent:
    """Booking-link integration DRAFT ONLY — never touches a live calendar."""

    task_kind = "calendar_integration"
    gate = None
    department = "03-ai-engineering"
    role = "Calendar Integration Agent"

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
        """Makes a booking-link integration DRAFT. Writes no file, touches no network."""
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
            "- In the call flow's Action step: Sophia gives the caller the booking link.\n"
            "- In the call flow's Confirm step: the booking details are read back to the caller.\n"
            "- In the outreach draft: the same link as the CTA for the 15-min demo call.\n"
            "Status: DRAFT plan only — nothing has been changed in the live calendar, "
            "no event was made/changed/deleted.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Booking-link integration DRAFT ONLY, "
            "Never touching a live calendar. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
