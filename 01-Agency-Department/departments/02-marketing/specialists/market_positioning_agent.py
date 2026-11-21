"""Market Positioning Agent — positioning/messaging draft (Dept 02 Marketing).

Role: writing a DRAFT of Talvenor's positioning/messaging — AI
receptionist, for US home-service owners. It never publishes,
sends to nobody.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never: does any publish/publish-prep, quotes prices,
gives any guarantee, invents client facts/statistics,
no dental/medical. Live voice stack Vapi/Sophia — no other stack is
called live.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class MarketPositioningAgent:
    """Positioning/messaging draft ONLY — no invented claims."""

    task_kind = "market_position"
    gate = None
    department = "02-marketing"
    role = "Market Positioning Agent"

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
        niche = payload.get("niche") or "BOSS INPUT REQUIRED"
        return (
            "Positioning/messaging draft for Talvenor, an AI receptionist "
            "for US home-service owners. "
            f"Topic: {topic}. Niche: {niche}. "
            "Audience, problem (missed call = lost job), solution (AI "
            "receptionist answers 24/7), differentiator, headline + subline. "
            "No invented client facts, prices, statistics, testimonials, or "
            "guarantees; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a positioning DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Market positioning draft"
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
        niche = payload.get("niche") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — positioning built from payload only."

        output = (
            "[MOCK DRAFT] Market positioning — DRAFT ONLY\n"
            f"Topic: {topic} | Niche: {niche}\n"
            "Audience: US home-service owners (plumbing, HVAC, roofing, "
            "garage door, septic, tree, foundation, restoration, pest, vet) "
            "— dental/medical never.\n"
            "Problem: missed call = lost job — if the phone is not answered, the job is lost.\n"
            "Solution: Talvenor AI receptionist answers 24/7 (live stack: "
            "Vapi — Sophia, +1 (947) 223-0244) and books the call.\n"
            "Differentiator: you run the jobs, we run the phone — "
            "no call is missed, even after hours.\n"
            "Headline draft: \"Never miss a call. Never lose a job.\"\n"
            "Subline draft: \"AI receptionist for service businesses.\"\n"
            f"Book a 15-min call: {BOOKING_LINK} (New York Time)\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Positioning draft ONLY, never "
            "not publish/sending. No invented client, price, statistic, "
            "testimonial, or guarantee. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
