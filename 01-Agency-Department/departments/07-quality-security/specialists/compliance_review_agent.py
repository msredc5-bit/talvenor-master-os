"""Compliance Review Agent — compliance review draft (Dept 07, Phase 3).

Role: writing a compliance review DRAFT — no invented
client/stat/price, no dental/medical, no guarantee.
Gate: None — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never gives legal advice — attorney review is deferred until the first paying
client arrives. Pricing LOCKED, internal only —
never quoted to a prospect.

This agent never does this: it gives no legal advice, no legal verdict,
sends nothing, spends nothing, publishes/deletes nothing, invents no client facts/
prices/statistics, gives no guarantee, takes no dental/medical,
gives no invented testimonial/client/case study.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

_CHECKS = (
    "No invented client — no fake client name, story, or case study.",
    "No invented statistic — no number without a real, visible source.",
    "No price quoted — pricing is LOCKED and internal only; prospects are never quoted a price.",
    "No testimonial or review invented — only real words from a real person, with proof.",
    "No guarantee — no promise of results, income, or a refund timeline beyond the locked terms.",
    "No dental/medical or patient-health targeting — always DQ.",
    "Brand is Talvenor only — no older brand name anywhere.",
)


class ComplianceReviewAgent:
    """Compliance review DRAFT ONLY — never legal advice."""

    task_kind = "compliance_review"
    gate = None
    department = "07-quality-security"
    role = "Compliance Review Agent"

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
        """Recording a PENDING approval — not executing, not auto-approving."""
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
        topic = payload.get("topic") or "Talvenor public content"
        return (
            "Compliance review draft for Talvenor. "
            f"Material: {topic}. "
            "Check for invented clients, statistics, prices, "
            "testimonials, guarantees, dental/medical targeting, and "
            "wrong brand names. Pricing is LOCKED and internal only. "
            "Never give legal advice — attorney review is deferred "
            "until the first paying client. Do not invent any fact. "
            "No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a compliance review DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Compliance review draft"
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
        topic = payload.get("topic") or payload.get("material")
        topic_line = (
            f"Material reviewed: {topic}"
            if topic else
            "Material reviewed: BOSS INPUT REQUIRED — standard checklist drafted."
        )

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — review built from payload only."

        items = "\n".join(f"- {item}" for item in _CHECKS)
        output = (
            "[MOCK DRAFT] Compliance review — DRAFT ONLY\n"
            f"{topic_line}\n"
            "Checks (each must hold; a fail is reported to Boss, never "
            "fixed silently):\n"
            f"{items}\n"
            "Verdict: NOT A LEGAL VERDICT — this is a checklist draft only. "
            "Attorney review is deferred until the first paying client. "
            "Any legal question goes to Boss, not to this agent.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Review draft ONLY, never legal "
            "advice. Attorney review deferred — until the first paying client "
            "arrives. Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
