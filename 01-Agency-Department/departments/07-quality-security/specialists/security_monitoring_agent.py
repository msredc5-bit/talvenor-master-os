"""Security Monitoring Agent — security monitoring checklist draft (Dept 07, Phase 3).

ভূমিকা (role): security monitoring checklist-এর DRAFT লেখা — secrets
scan, repo/file-এ key নেই কি না, কী যাচাই করতে হবে।
Gate: None — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো live monitoring করে না, কোনো scan চালায় না, live
monitoring-এর দাবি করে না। Credential দরকার হলে Boss নিজে secure
page-এ দেবেন — agent কখনো password/key চায় না, দেখে না, file-এ
লেখে না।

এই agent কখনো করে না: live monitoring করে না, scan চালায় না,
কোনো credential দেখে/চায়/লেখে না, কোনো file বদলায়/মোছে না, কিছু
পাঠায় না, খরচ করে না, client-এর তথ্য/দাম/পরিসংখ্যান বানায় না,
কোনো guarantee দেয় না, dental/medical নয়, legal advice দেয় না।
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
    """Security monitoring checklist DRAFT ONLY — কখনো live monitoring নয়।"""

    task_kind = "security_monitoring"
    gate = None
    department = "07-quality-security"
    role = "Security Monitoring Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — top level-এ কোনো repo import নয়।"""
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
        """PENDING approval record করা — execute নয়, auto-approve নয়।"""
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
        """Security monitoring checklist DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না, scan চালায় না।"""
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
            "DRAFT ONLY — mock brain ($0). Checklist ONLY, কখনো live "
            "monitoring নয়, scan চালানো নয়। Gate: None।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
