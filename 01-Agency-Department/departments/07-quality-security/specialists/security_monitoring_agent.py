"""Security Monitoring Agent — security monitoring checklist draft (Dept 07, Phase 3).

Role: writing a security monitoring checklist DRAFT — secrets
scan, whether a key is in any repo/file, what to check.
Gate: None — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never does live monitoring, runs no scan, claims no live
monitoring. If a credential is needed, Boss himself will give it on a secure
page — the agent never asks for, looks at, or writes a password/key to a
file.

This agent never does this: it does no live monitoring, runs no scan,
looks at/asks for/writes no credential, changes/deletes no file, sends
nothing, spends nothing, invents no client facts/prices/statistics,
gives no guarantee, takes no dental/medical, gives no legal advice.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

_CHECKLIST = (
    "Secrets scan — no API key, password, token, or secret in any repo file or doc.",
    "No credential in memory or in any file — keys live only in the secure flow, never written down.",
    "No .env / credentials file committed to any repo.",
    "Booking link and phone are the only public contact details — no private contact shared.",
    "Any suspicious secret found is reported to Boss — never deleted or changed by the agent.",
)


class SecurityMonitoringAgent:
    """Security monitoring checklist DRAFT ONLY — never live monitoring."""

    task_kind = "security_monitoring"
    gate = None
    department = "07-quality-security"
    role = "Security Monitoring Agent"

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
        scope = payload.get("scope") or "whole talvenor-master-os repo"
        return (
            "Security monitoring checklist draft for Talvenor. "
            f"Scope: {scope}. "
            "Cover a secrets scan (no keys in repos/files), credential "
            "rules, and what to verify. Never claim live monitoring "
            "happened or a scan was run. Never ask for, look at, or "
            "write down any credential. Do not invent any finding. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a security monitoring checklist DRAFT. Writes no file, touches no network, runs no scan."""
        task = task or {}
        title = task.get("title") or "Security monitoring checklist draft"
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
        scope = payload.get("scope")
        scope_line = (
            f"Scope: {scope}"
            if scope else
            "Scope: BOSS INPUT REQUIRED — whole repo drafted."
        )

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — checklist built from payload only."

        items = "\n".join(f"- {item}" for item in _CHECKLIST)
        output = (
            "[MOCK DRAFT] Security monitoring checklist — DRAFT ONLY\n"
            f"{scope_line}\n"
            "Checklist (what to verify — no scan was run):\n"
            f"{items}\n"
            "Monitoring result: NOT VERIFIED — no live monitoring happened "
            "and no scan was run. Real checks are done by hand by "
            "Boss/Elora.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Checklist ONLY, never live "
            "monitoring, no scan run. Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
