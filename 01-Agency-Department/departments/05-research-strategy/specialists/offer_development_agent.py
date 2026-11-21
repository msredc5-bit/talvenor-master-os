"""Offer Development Agent — offer draft (Phase 3).

Role: write a DRAFT of the offer only — never send it.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Never any guarantee — not even a real business term may be written as a guarantee in public content.

This agent never: sends anything, publishes anything, spends anything,
does not delete, does not invent client/competitor/price/statistic facts,
gives no guarantee, takes no dental/medical or patient-health business.
Email PAUSED (since 2026-11-14) — the draft is the final word.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class OfferDevelopmentAgent:
    """offer draft — DRAFT ONLY, never sends it."""

    task_kind = "offer_development"
    gate = None
    department = "05-research-strategy"
    role = "Offer Development Agent"

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
            "Offer development draft for Talvenor AI receptionist. NO guarantees ever — not even real business terms as guarantees in public content. "
            f"Topic: {topic}. "
            "Do not invent any client fact, price, or statistic; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """offer draft. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Offer draft"
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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — draft built from payload only."

        output = (
            "[MOCK DRAFT] Offer development — DRAFT ONLY\n"
            f"Topic: {topic}\n"
            "Core offer (draft): AI receptionist answers 24/7 so no missed call becomes a lost job; booking link on a 15-min call.\nGuarantees: NONE — no guarantee is given.\nPrice in offer: LOCKED pricing internal only — a price is not written for a prospect unless Boss confirms it.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Offer draft ONLY. No guarantee, no invented client/testimonial. "
            "Never sending, never spending. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
