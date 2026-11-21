"""Client Reporting Agent — client report draft (Dept 04).

Role: write a template + DRAFT of a report to give to a client —
Showing where each real number goes. If there are no real numbers, it does not invent any.
Gate: none — the report DRAFT itself is safe, it is not sent to the client.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Truth: paying clients 0 — there are still no real client numbers. The report has
only what can be seen (visible numbers only); if there is no number,
BOSS INPUT REQUIRED. The report DRAFT goes to Boss — Boss fills in the real numbers,
reviews it, and sends it to the client himself.

This agent never: invents a client's numbers/statistics, estimates,
sends the report to the client, quotes a price, gives any guarantee
gives none, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ClientReportingAgent:
    """Client report DRAFT ONLY — writes no number without a real number."""

    task_kind = "client_reporting"
    gate = None
    department = "04-client-operations"
    role = "Client Reporting Agent"

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
        period = payload.get("period") or "BOSS INPUT REQUIRED"
        return (
            "Client report draft for a Talvenor client. "
            f"Client: {client}. Period: {period}. "
            "Template: period, calls answered, bookings, missed-call "
            "recovery, next steps. Show where each real number comes "
            "from (Vapi dashboard / call log). If a real number is not "
            "in the payload, write 'BOSS INPUT REQUIRED' — never invent "
            "or estimate a number. Visible numbers only. No price, no "
            "guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making a client report DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Client report draft"
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
        period = payload.get("period") or "BOSS INPUT REQUIRED"
        calls = payload.get("calls_answered")
        bookings = payload.get("bookings")

        def _num(value):
            return str(value) if value is not None else "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — report built from payload only."

        output = (
            "[MOCK DRAFT] Client report — DRAFT ONLY (for Boss review, NOT sent to client)\n"
            f"Client: {client} | Period: {period}\n"
            "Report template (real numbers go here — source in brackets):\n"
            f"1. Calls answered: {_num(calls)} [Vapi dashboard — Boss fills in]\n"
            f"2. Bookings made: {_num(bookings)} [Vapi call log + calendar — Boss fills in]\n"
            "3. Missed-call recovery: BOSS INPUT REQUIRED "
            "[Vapi call log — Boss fills in]\n"
            "4. What went well: BOSS INPUT REQUIRED "
            "[from call-monitoring checklist — Boss fills in]\n"
            "5. What to fix: BOSS INPUT REQUIRED "
            "[from call-monitoring checklist — Boss fills in]\n"
            "6. Next steps: Boss reviews this draft, fills in real numbers, "
            "then sends it to the client himself.\n"
            "Paying clients: 0 — no real client numbers exist yet; every "
            "number above is BOSS INPUT REQUIRED until Boss fills it in.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Client report template + DRAFT "
            "ONLY — no number was invented, no estimate was made; missing "
            "numbers are BOSS INPUT REQUIRED. The report was not sent to the client. "
            "Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
