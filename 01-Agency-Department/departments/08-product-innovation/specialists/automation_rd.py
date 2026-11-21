"""Automation R&D Agent — automation R&D draft (Dept 08, Phase 3).

Role: writing an automation R&D DRAFT on a new automation idea —
it never runs a live automation, never claims one has launched.
Gate: none — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Honest status: n8n workflows READY, not LIVE — Boss's import + test
pending. CRM n8n Cloud Data Tables PLANNED, not live. Brain mock ($0).
This agent never does this: it runs no workflow, never claims a live automation,
invents no time/success numbers, sends nothing, spends nothing,
no dental/medical.
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class AutomationRDAgent:
    """Automation R&D DRAFT ONLY — only an idea, not a live automation."""

    task_kind = "automation_rd"
    gate = None
    department = "08-product-innovation"
    role = "Automation R&D Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "Automation R&D draft for Talvenor. "
            f"Automation idea: {topic}. "
            "What manual work it would save, which tool it could sit "
            "in (n8n READY not live, Vapi live, booking link live), "
            "and what still needs verification. Never claim a live "
            "automation — n8n workflows are READY, not live. Do not "
            "invent time saved or success numbers; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building an automation R&D DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Automation R&D draft"
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
        trigger = payload.get("trigger") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — R&D built from payload only."

        output = (
            "[MOCK DRAFT] Automation R&D — DRAFT ONLY\n"
            f"Automation idea: {topic}\n"
            f"Trigger: {trigger}\n"
            "Status: DRAFT ONLY — no live automation. n8n workflows "
            "READY, not LIVE — Boss's import + test pending.\n"
            "Where it could sit: n8n (READY, not live), Vapi/Sophia live "
            f"receptionist ({TALVENOR_PHONE}), booking link live; CRM n8n "
            "Cloud Data Tables PLANNED, not live.\n"
            "What is NOT known (no invented numbers): time saved, success "
            "rate — all BOSS INPUT REQUIRED / verification pending.\n"
            "Next verification step ($0): Boss decides whether to import "
            "and test; no live run before his word.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). R&D draft ONLY — n8n READY, LIVE "
            "not, no live automation. No invented time/success numbers "
            "none. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
