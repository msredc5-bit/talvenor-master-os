"""n8n Automation Engineer — n8n workflow draft notes (Dept 03, Phase 3).

Role: making DRAFT notes for n8n workflows — it never imports/runs a live workflow
— it never does.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

n8n workflows READY, not LIVE — Boss's import + test is pending. CRM (n8n Cloud
Data Tables) PLANNED, not live.
This worker never: imports/runs a live workflow, calls a webhook,
enters an n8n account, sends anything, spends anything, deletes anything, quotes a price,
does not invent client facts/statistics, gives no guarantee,
no dental/medical, does not claim a workflow is live.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class N8nAutomationEngineer:
    """n8n workflow DRAFT notes ONLY — never runs a live workflow."""

    task_kind = "n8n_automation"
    gate = None
    department = "03-ai-engineering"
    role = "n8n Automation Engineer"

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
        workflow = payload.get("workflow") or "BOSS INPUT REQUIRED"
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"
        return (
            "n8n workflow draft notes for a Talvenor client. "
            f"Client: {client}. Workflow: {workflow}. Purpose: {purpose}. "
            "Workflows are READY, not LIVE — Boss import + test still "
            "pending. CRM (n8n Cloud Data Tables) is PLANNED, not live. "
            "Describe trigger and steps as DRAFT notes only. Do not invent "
            "client facts; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes n8n workflow DRAFT notes. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "n8n workflow draft notes"
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
        workflow = payload.get("workflow") or "BOSS INPUT REQUIRED"
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — n8n workflow notes built from payload only."

        output = (
            "[MOCK DRAFT] n8n Automation Engineer — workflow notes (DRAFT ONLY)\n"
            f"Client: {client} | Workflow: {workflow} | Purpose: {purpose}\n"
            "Status: workflows READY, not LIVE — Boss's import + test is pending.\n"
            "CRM: n8n Cloud Data Tables — PLANNED, not live.\n"
            "Workflow notes (DRAFT):\n"
            "1. Trigger — when a Vapi/Sophia call ends, the call log arrives.\n"
            "2. Step — the call's information (name, phone, service, booking) is arranged.\n"
            "3. Step — if there is a booking, the booking link's details are added: "
            f"{BOOKING_LINK} (15 min, New York Time).\n"
            "4. Step — information is kept for follow-up (in Data Tables if the CRM is live; "
            "now PLANNED, so it is kept by hand).\n"
            "5. Next — Boss will import + test; before that, no claim that it is live.\n"
            "Status: DRAFT notes only — there is no live workflow, no "
            "import/run/webhook happened.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). n8n workflow DRAFT notes ONLY, "
            "Never a live workflow. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
