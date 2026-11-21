"""Retention Agent — retention plan draft (Dept 04).

Role: write a DRAFT of the retention plan for keeping a client —
never tell the client anything, send anything.
Gate: none — the plan DRAFT itself is safe.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Truth: paying clients 0 — retention work has not started yet, no
retained client. This plan is only a DRAFT; it has not been run on any real client
yet.

This agent never: claims any client is retained,
tells/sends the client anything, tells about a discount/guarantee/price, invents any
result — no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class RetentionAgent:
    """Retention plan DRAFT ONLY — no claim of a retained client."""

    task_kind = "retention"
    gate = None
    department = "04-client-operations"
    role = "Retention Agent"

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
        return (
            "Retention plan draft for a Talvenor client. "
            f"Client: {client}. Paying clients are 0 — no client is "
            "retained yet, so this is a DRAFT plan only, never a claim "
            "about a retained client. Cover: regular check-in, hearing "
            "and fixing issues, showing value with reports, and flagging "
            "risk signals to Boss early. No discount, no guarantee, no "
            "price, no invented result, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making a retention plan DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Retention plan draft"
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
            brain_text = "No brain passed — plan built from payload only."

        output = (
            "[MOCK DRAFT] Retention plan — DRAFT ONLY\n"
            f"Client: {client}\n"
            "Paying clients: 0 — no client retained yet; this plan has "
            "not run on any real client.\n"
            "Retention plan (DRAFT):\n"
            "1. Regular check-in — Boss checks in with the client on a "
            "fixed rhythm; what the client says goes to Boss first.\n"
            "2. Hear and fix issues — any issue from call monitoring or "
            "the client report goes to Boss, then gets fixed, then the "
            "fix is confirmed with the client.\n"
            "3. Show value — the client report (calls answered, bookings, "
            "missed-call recovery) shows the client what Sophia did.\n"
            "4. Risk signal — if the client goes quiet or complains, "
            "Boss is told at once; the worker never contacts the client.\n"
            "No discount, no guarantee, no price in this plan — pricing "
            "is LOCKED, internal only.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Retention plan DRAFT ONLY — "
            "paying client 0, no retained client, no result invented "
            "yet. Nothing was told/sent to the client. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
