"""Pricing Research Agent — pricing research draft (Phase 3).

Role: write a DRAFT of pricing research only — INTERNAL ONLY, never send it.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Talvenor pricing LOCKED (2026-11-12): $547/$1,109/$1,672/mo + build $597/$1,297/$1,997 — this price must never be changed, and must never be quoted to a prospect. This draft is INTERNAL ONLY.

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


class PricingResearchAgent:
    """pricing research draft — DRAFT ONLY, never sends it."""

    task_kind = "pricing_research"
    gate = None
    department = "05-research-strategy"
    role = "Pricing Research Agent"

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
            "Pricing research draft for Talvenor — INTERNAL ONLY, never quoted to a prospect. Talvenor pricing is LOCKED ($547/$1,109/$1,672 per month + builds $597/$1,297/$1,997). "
            f"Topic: {topic}. "
            "Do not invent any client fact, price, or statistic; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """pricing research draft. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Pricing research draft"
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
            "[MOCK DRAFT] Pricing research (INTERNAL ONLY) — DRAFT ONLY\n"
            f"Topic: {topic}\n"
            "Talvenor pricing LOCKED (2026-11-12, internal only): Starter $547/mo + build $597; Growth $1,109/mo + build $1,297; Scale $1,672/mo + build $1,997.\nWARNING: this price must never be quoted to a prospect — unless Boss confirms it, there is no talk about price.\nMarket price comparison: BOSS INPUT REQUIRED — no market price was written without a verified source.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Pricing research draft ONLY, INTERNAL ONLY. LOCKED pricing was not changed, no quote to a prospect. "
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
