"""Conversation Designer — call-flow / conversation design draft (Dept 03, Phase 3).

Role: making a DRAFT of Sophia the receptionist's 8-step call flow —
it never makes any call, never changes a live assistant.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This worker never: changes a live assistant's flow, makes a call,
sends nothing, spends nothing, deletes nothing, quotes no price, invents no client
facts/statistics, gives no guarantee, no dental/medical,
writes a flow without AI disclosure.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ConversationDesigner:
    """Call-flow design DRAFT ONLY — never changes a live assistant."""

    task_kind = "conversation_design"
    gate = None
    department = "03-ai-engineering"
    role = "Conversation Designer"

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
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        services = payload.get("services") or "BOSS INPUT REQUIRED"
        return (
            "Call-flow design draft for a Talvenor client receptionist. "
            f"Client: {client}. Business type: {business_type}. "
            f"Services: {services}. "
            "Eight steps: Greet, Life-safety check, Intent, Qualify, Action, "
            "Confirm, Log, Close. Include honest AI disclosure and the "
            "booking link. Do not invent client facts; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a call-flow DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Conversation design draft"
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
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        services = payload.get("services") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — call flow built from payload only."

        dq_line = ""
        if business_type.strip().lower() in ("dental", "medical", "dentist", "clinic"):
            dq_line = "\nDQ: dental/medical or patient-health business — not a design, not a target."

        output = (
            "[MOCK DRAFT] Conversation Designer — call flow (DRAFT ONLY)\n"
            f"Client: {client} | Business type: {business_type} | Services: {services}"
            f"{dq_line}\n"
            "Call flow (8 steps):\n"
            "1. Greet — honest AI disclosure: the caller is told they are talking to Talvenor's "
            "AI receptionist Sophia.\n"
            "2. Life-safety check — if there is an emergency (fire, gas leak, flood, injury), "
            "the caller is told to go directly to the emergency number; Sophia herself "
            "does not handle emergencies.\n"
            "3. Intent — what the caller wants (booking, quote, emergency, or something else).\n"
            "4. Qualify — name, phone, service, area, time — whatever needs to be known.\n"
            "5. Action — giving the booking link: "
            f"{BOOKING_LINK} (15 min, New York Time).\n"
            "6. Confirm — reading the booking details back to the caller.\n"
            "7. Log — logging the call's information (n8n workflow, READY not LIVE).\n"
            "8. Close — thanks, and telling the next step.\n"
            "Status: DRAFT design only — nothing has been changed in the live assistant.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Call-flow design DRAFT ONLY, "
            "Never changing a live assistant. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
