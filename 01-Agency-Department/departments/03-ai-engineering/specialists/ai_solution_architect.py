"""AI Solution Architect — solution design draft (Dept 03, Phase 3).

Role: hearing a client's need and making a DRAFT plan for which solution fits from Talvenor's live stack (Vapi/Sophia)
— it never builds.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This worker never: builds anything, changes anything in production,
sends nothing, spends nothing, deletes nothing, quotes no price, invents no client
facts/statistics, gives no guarantee, no dental/medical,
claims a live build happened.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class AISolutionArchitect:
    """Solution design DRAFT ONLY — never builds."""

    task_kind = "solution_architect"
    gate = None
    department = "03-ai-engineering"
    role = "AI Solution Architect"

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
        need = payload.get("need") or "BOSS INPUT REQUIRED"
        return (
            "Solution design draft for a Talvenor client. "
            f"Client: {client}. Business type: {business_type}. Need: {need}. "
            "Name which live-stack pieces fit (Vapi/Sophia receptionist, "
            "booking link, call flow, n8n workflow notes). Do not invent "
            "client facts or prices; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a solution design DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Solution design draft"
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
        need = payload.get("need") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — solution design built from payload only."

        dq_line = ""
        if business_type.strip().lower() in ("dental", "medical", "dentist", "clinic"):
            dq_line = "\nDQ: dental/medical or patient-health business — not a solution, not a target."

        output = (
            "[MOCK DRAFT] AI Solution Architect — solution design (DRAFT ONLY)\n"
            f"Client: {client} | Business type: {business_type} | Need: {need}"
            f"{dq_line}\n"
            "Solution pieces (live stack only):\n"
            "1. Vapi assistant Sophia — live receptionist, +1 (947) 223-0244, "
            "GPT-4o-mini, Emma voice, Deepgram nova-3.\n"
            "2. Call flow — Greet → Life-safety check → Intent → Qualify → "
            "Action → Confirm → Log → Close (with honest AI disclosure).\n"
            "3. Booking — Google Calendar Appointment Schedule link: "
            f"{BOOKING_LINK} (15 min, New York Time).\n"
            "4. Logging/follow-up — n8n workflow notes (READY, not LIVE; "
            "Boss's import + test is pending).\n"
            "Status: DRAFT plan only — no live build, nothing has been changed.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Solution design DRAFT ONLY, "
            "Never a build. Live stack Vapi/Sophia. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
