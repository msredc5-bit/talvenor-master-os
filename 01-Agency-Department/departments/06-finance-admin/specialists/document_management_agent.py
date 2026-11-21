"""Document Management Agent — document organisation draft (Dept 06, Phase 3).

Role: only make a DRAFT of the organisation of where documents are
— it makes no document, writes/moves/deletes no file.
Gate: None — the draft itself is safe.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

The list has only verified places: Master OS repo
(`talvenor-master-os` — 00-CEO-Core, 01-Agency-Department,
02-Digital-Product-Department, 03-Content-Creation-Department,
CENTRAL-HQ, scripts, store), Talvenor office
(`~/workspace/talvenor-office/`), brand asset
(`~/workspace/talvenor-brand/`), JSON store
(`store/tasks.json`, `store/approvals.json`). CRM = n8n Cloud Data
Tables PLANNED, not live.

This agent never: makes a document, writes/moves/deletes a file,
claims an invented document's name/existence, sends anything, spends
anything, gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class DocumentManagementAgent:
    """Document organisation DRAFT ONLY — touches no file."""

    task_kind = "document_management"
    gate = None
    department = "06-finance-admin"
    role = "Document Management Agent"

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
        return (
            "Document organisation draft for Talvenor. "
            f"Topic: {topic}. "
            "List only verified locations: the Master OS repo folders, "
            "the Talvenor office, brand assets, and the JSON store. "
            "Do not invent any document; mark missing facts "
            "'BOSS INPUT REQUIRED'. No file is written, moved, or deleted. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making a document organisation DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Document organisation"
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

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — organisation built from task only."

        output = (
            "[MOCK DRAFT] Document organisation — DRAFT ONLY\n"
            f"Department: {self.department} | Worker: {self.role}\n"
            "Known locations (verified, 2026-11-19):\n"
            "- Master OS repo: talvenor-master-os/ — 00-CEO-Core, "
            "01-Agency-Department, 02-Digital-Product-Department, "
            "03-Content-Creation-Department, CENTRAL-HQ, scripts, store.\n"
            "- JSON store: store/tasks.json, store/approvals.json "
            "(DB = JSON store files).\n"
            "- Talvenor office: ~/workspace/talvenor-office/.\n"
            "- Brand asset: ~/workspace/talvenor-brand/ (logos, social kit).\n"
            "- CRM: n8n Cloud Data Tables PLANNED, not live — no document is here.\n"
            "Boss will decide the place for a new document — BOSS INPUT REQUIRED.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Document organisation ONLY — "
            "No file was written/moved/deleted, no document was made. "
            "Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
