"""Workflow Testing Agent — workflow test draft (Dept 07, Phase 3).

Role: writing a workflow test DRAFT — check script: what to check,
what to look at in each step.
Gate: None — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Honest status: n8n workflows READY, not LIVE (Boss's import + test
pending); CRM (n8n Cloud Data Tables) PLANNED, not live; brain mock ($0).
This agent never runs a live workflow, never claims one ran.

This agent never does this: it runs no workflow, claims no live run,
sends nothing, spends nothing, invents no client facts/prices/statistics,
gives no guarantee, takes no dental/medical, gives no legal advice.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

_CORE_STEPS = (
    "research",
    "draft",
    "approve",
    "send",
    "reply",
    "book",
    "build",
    "launch",
)


class WorkflowTestingAgent:
    """Workflow test check-script DRAFT ONLY — never a live run."""

    task_kind = "workflow_testing"
    gate = None
    department = "07-quality-security"
    role = "Workflow Testing Agent"

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
        workflow = payload.get("workflow") or "core agency workflow"
        return (
            "Workflow test check-script draft for Talvenor. "
            f"Workflow: {workflow}. "
            "List what to verify at each step, the expected result, and "
            "a pass/fail check. n8n workflows are READY, not LIVE; CRM "
            "is PLANNED, not live. Never claim a live run happened. "
            "Do not invent client facts or prices; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def _step_block(self, step):
        blocks = {
            "research": "Step research — check: prospect has real website/phone/service area; missing field = NOT_FOUND, never invented.",
            "draft": "Step draft — check: draft is plain US English, one CTA, booking link present, no price, no guarantee.",
            "approve": "Step approve — check: Boss gate word given (ok / send / post it) before any onward use; no gate = no use.",
            "send": "Step send — check: Email PAUSED since 2026-11-14; no send until DNS fix is verified and Boss restarts it.",
            "reply": "Step reply — check: decline = polite exit; interest = draft only, never price, booking link allowed.",
            "book": f"Step book — check: booking link is {BOOKING_LINK} (15 min, New York Time).",
            "build": "Step build — check: live stack is Vapi/Sophia; build plan is DRAFT only, never a live build claim.",
            "launch": "Step launch — check: QA checklist verdict (QAEngineer) + Boss ok before launch; no live claim without a real run.",
        }
        return blocks.get(step, f"Step {step} — check: BOSS INPUT REQUIRED (unknown step).")

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a workflow test check-script DRAFT. Writes no file, touches no network, runs no workflow."""
        task = task or {}
        title = task.get("title") or "Workflow test draft"
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
        workflow = payload.get("workflow") or "BOSS INPUT REQUIRED"
        workflow_line = (
            f"Workflow: {workflow}"
            if payload.get("workflow") else
            "Workflow: BOSS INPUT REQUIRED — core agency workflow drafted."
        )

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — check script built from payload only."

        steps = "\n".join(f"- {self._step_block(s)}" for s in _CORE_STEPS)
        output = (
            "[MOCK DRAFT] Workflow test — DRAFT ONLY\n"
            f"{workflow_line}\n"
            "Honest status: n8n workflows READY, not LIVE (Boss import + "
            "test pending); CRM (n8n Cloud Data Tables) PLANNED, not live; "
            "brain mock ($0).\n"
            "Check script (what to verify at each step):\n"
            f"{steps}\n"
            "Status: DRAFT check script only — no live workflow was run, "
            "no live run is claimed. Boss decides whether to run any test.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Check script ONLY, never live "
            "run. n8n READY-not-LIVE, CRM PLANNED-not-live. Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
