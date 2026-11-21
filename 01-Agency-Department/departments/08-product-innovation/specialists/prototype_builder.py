"""Prototype Builder Agent — prototype plan draft ONLY (Dept 08, Phase 3).

Role: writing a DRAFT of a prototype PLAN — it never builds a live prototype,
runs no code to launch a service, spends nothing.
Gate: none — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never does this: it builds no prototype, runs no code, launches no service,
invents no time/spend/success numbers, sends nothing,
spends nothing, does no Vet Kit work (that is 02-Digital-Product-
Department's), no dental/medical.
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244.
Retell DROPPED 2026-10-26 — never production.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class PrototypeBuilderAgent:
    """Prototype PLAN DRAFT ONLY — only a plan, no build."""

    task_kind = "prototype_builder"
    gate = None
    department = "08-product-innovation"
    role = "Prototype Builder Agent"

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
            "Prototype PLAN draft for Talvenor (plan only, never a build). "
            f"Prototype idea: {topic}. "
            "What it would show, steps 1-2-3, what it needs ($0 only), "
            "and what still needs verification. PLAN draft only — no "
            "prototype built, no code run, no service started. Do not "
            "invent time, cost, or success numbers; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a prototype PLAN DRAFT. Writes no file, touches no network, runs no code."""
        task = task or {}
        title = task.get("title") or "Prototype plan draft"
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
            brain_text = "No brain passed — plan built from payload only."

        output = (
            "[MOCK DRAFT] Prototype plan — DRAFT ONLY\n"
            f"Prototype idea: {topic}\n"
            "Status: PLAN DRAFT ONLY — no prototype has been built, no "
            "code has been run, no service has launched.\n"
            "Plan steps (idea only):\n"
            "  1. What it will show — show the idea to Boss in one line.\n"
            "  2. What is needed — only $0, no-spend things; nothing without Boss's 'ok'.\n"
            "  3. Check — Boss decides from the plan whether to build it.\n"
            "What is NOT known (no invented numbers): time, cost, success "
            "rate — all BOSS INPUT REQUIRED / verification pending.\n"
            "Vet No-Show Recovery Kit is NOT this department's work — it "
            "belongs to the Digital Product Department.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Prototype PLAN draft ONLY — no "
            "prototype has been built, no code has been run. No invented "
            "time/spend/success numbers. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
