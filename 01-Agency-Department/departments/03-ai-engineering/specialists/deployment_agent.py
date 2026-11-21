"""Deployment Agent — deployment plan draft ONLY (Dept 03, Phase 3).

Role: making a DRAFT of the deployment plan — it never deploys anything.
Gate: none — the draft itself is safe, there is no gate; deploying needs Boss's
"ok" + manual steps, which is outside this worker.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This worker never: deploys anything, writes a file, enters a server,
runs a command, sends anything, spends anything, deletes anything, quotes a price,
does not invent client facts/statistics, gives no guarantee,
no dental/medical, does not claim a deploy happened.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class DeploymentAgent:
    """Deployment plan DRAFT ONLY — never deploys."""

    task_kind = "deployment"
    gate = None
    department = "03-ai-engineering"
    role = "Deployment Agent"

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
        what = payload.get("what") or "BOSS INPUT REQUIRED"
        target = payload.get("target") or "BOSS INPUT REQUIRED"
        return (
            "Deployment plan draft for a Talvenor client. "
            f"Client: {client}. What: {what}. Target: {target}. "
            "Deployment needs Boss 'ok' plus manual steps; no worker "
            "deploys anything. List check, ok, manual deploy, verify steps "
            "as a DRAFT plan only. Do not invent client facts; mark missing "
            "facts 'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a deployment plan DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Deployment plan draft"
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
        what = payload.get("what") or "BOSS INPUT REQUIRED"
        target = payload.get("target") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — deployment plan built from payload only."

        output = (
            "[MOCK DRAFT] Deployment Agent — deployment plan (DRAFT ONLY)\n"
            f"Client: {client} | What: {what} | Target: {target}\n"
            "Rule: deploying needs Boss's \"ok\" + manual steps; no "
            "worker deploys.\n"
            "Plan steps (DRAFT — no step has been executed):\n"
            "1. Check — what will be deployed, where, and whether Boss has seen the previous drafts (solution, "
            "call flow, prompt, Vapi plan).\n"
            "2. Ok — Boss's exact word \"ok\" without it, no deploy.\n"
            "3. Manual deploy — Boss/Elora will deploy by hand; this worker "
            "writes no file, enters no server, runs no command.\n"
            "4. Verify — only after seeing a real run in Boss's signed-in session "
            "can it be called live; before that, the DRAFT is the final word.\n"
            "Booking link (real): "
            f"{BOOKING_LINK} (15 min, New York Time)\n"
            "Status: DRAFT plan only — nothing has been deployed.\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Deployment plan DRAFT ONLY, "
            "Never a deploy. Gate: none (deploying needs Boss's ok + "
            "manual steps, outside this worker)."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
