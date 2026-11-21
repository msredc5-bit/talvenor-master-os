"""Access Control Agent — access-control draft (Dept 07, Phase 3).

Role: writing an access-control DRAFT — who can approve/send/
publish/spend (only Boss for gated actions).
Gate: None — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never changes any access, gives access to anyone, or takes
access from anyone, and never approves anything itself. Spend cap $0 — no spend
approval.

This agent never does this: it does not change access, do a gated action, send
anything, spend, publish/delete, or invent client facts/prices/
statistics, give any guarantee, or take dental/medical;
no legal advice.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

_GATED_TABLE = (
    ("send", "send", "Only Boss — email/DM sending."),
    ("publish", "post it", "Only Boss — posting on Facebook/Instagram/LinkedIn."),
    ("spend", "go / Boss allocation", "Only Boss — spend cap $0, no spend approved."),
    ("delete", "Boss exact word", "Only Boss — nothing is deleted without his exact word."),
)


class AccessControlAgent:
    """Access-control DRAFT ONLY — never changing access."""

    task_kind = "access_control"
    gate = None
    department = "07-quality-security"
    role = "Access Control Agent"

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
        action = payload.get("action") or "all four gated actions"
        return (
            "Access-control draft for Talvenor. "
            f"Action: {action}. "
            "Say who may do it (Boss only for gated actions), the gate "
            "word needed, and the agent's limit (draft only, never "
            "executes). Never change any access. Do not invent client "
            "facts or prices. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building an access-control DRAFT. Writes no file, touches no network, changes no access."""
        task = task or {}
        title = task.get("title") or "Access control draft"
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
        action = payload.get("action")
        action_line = (
            f"Action requested: {action}"
            if action else
            "Action requested: BOSS INPUT REQUIRED — all four gated actions drafted."
        )

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — access-control draft built from payload only."

        rows = "\n".join(
            f"- {name}: gate word '{word}' — {who}"
            for name, word, who in _GATED_TABLE
        )
        output = (
            "[MOCK DRAFT] Access control — DRAFT ONLY\n"
            f"{action_line}\n"
            "Who may approve/send/publish/spend:\n"
            f"{rows}\n"
            "Agent limit: Elora/agents only build DRAFTS — sending, "
            "publishing, spending, and deleting are done by Boss himself, "
            "only on his exact gate word. No access was changed by this "
            "draft; changing access is Boss's decision.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Access-control draft ONLY, "
            "Never changing access. Spend cap $0. Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
