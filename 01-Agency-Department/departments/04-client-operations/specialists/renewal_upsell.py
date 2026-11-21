"""Renewal & Upsell Agent — renewal/upsell plan draft (Dept 04).

Role: write a DRAFT of the plan for a paying client's renewal or upsell —
never tell the client anything, never quote a price.
Gate: none — the plan DRAFT itself is safe.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Truth: paying clients 0 — no renewal due, no upsell happened.
This plan is only a DRAFT. An upsell is not told to the client until Boss says "ok"
. Pricing LOCKED, internal only — a price is told only by Boss's decision.

This agent never: tells the client about renewal/upsell, quotes a price/discount/
tier, claims any renewal/upsell happened, sends
anything, gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class RenewalUpsellAgent:
    """Renewal/upsell plan DRAFT ONLY — quotes no price."""

    task_kind = "renewal_upsell"
    gate = None
    department = "04-client-operations"
    role = "Renewal & Upsell Agent"

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
            "Renewal/upsell plan draft for a Talvenor client. "
            f"Client: {client}. Paying clients are 0 — no renewal is "
            "due, no upsell has happened, so this is a DRAFT plan only. "
            "Cover: when renewal comes up, showing the client their "
            "value, and upsell only when the client truly needs more. "
            "Never quote a price, discount, or tier — pricing is LOCKED, "
            "internal only. Upsell is never told to the client until "
            "Boss says 'ok'. No invented renewal/upsell, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making a renewal/upsell plan DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Renewal/upsell plan draft"
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
            "[MOCK DRAFT] Renewal & upsell plan — DRAFT ONLY\n"
            f"Client: {client}\n"
            "Paying clients: 0 — no renewal due, no upsell done; this "
            "plan has not run on any real client.\n"
            "Renewal/upsell plan (DRAFT):\n"
            "1. Renewal timing — Boss checks the renewal date first; "
            "nothing is said to the client before that.\n"
            "2. Show value — the client report (calls answered, bookings, "
            "missed-call recovery) is shown before any renewal talk.\n"
            "3. Upsell only on real need — upsell is considered only if "
            "the client truly needs more; never pushed.\n"
            "4. Boss decides — no upsell is told to the client until Boss "
            "says 'ok'; price is never quoted by this worker (pricing "
            "LOCKED, internal only — price only on Boss's decision).\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Renewal/upsell plan DRAFT ONLY — "
            "paying client 0, no renewal due, no upsell happened. "
            "Nothing was told to the client, no price was quoted. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
