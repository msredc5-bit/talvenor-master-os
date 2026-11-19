"""Vapi Integration Agent — Vapi integration draft (Dept 03, Phase 3).

ভূমিকা (role): Vapi assistant Sophia-র সঙ্গে সংযোগের DRAFT plan বানানো —
কখনো live account বদলায় না, API call করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

Live stack শুধু Vapi — অন্য কোনো voice provider production নয়।
এই worker কখনো করে না: live Vapi account-এ কিছু বদলায় না, API call
করে না, key ছোঁয় না, কিছু পাঠায় না, খরচ করে না, মোছে না, দাম quote
করে না, client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না,
dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class VapiIntegrationAgent:
    """Vapi integration DRAFT ONLY — কখনো live account বদলায় না।"""

    task_kind = "vapi_integration"
    gate = None
    department = "03-ai-engineering"
    role = "Vapi Integration Agent"

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
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"
        return (
            "Vapi integration draft for a Talvenor client. "
            f"Client: {client}. Purpose: {purpose}. "
            "Live stack is Vapi — assistant Sophia, org 1861a735, phone "
            "+1 (947) 223-0244, GPT-4o-mini, Emma voice, Deepgram nova-3. "
            "List the integration steps as a DRAFT plan only. Do not invent "
            "client facts; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Vapi integration DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Vapi integration draft"
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
        purpose = payload.get("purpose") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — Vapi integration draft built from payload only."

        output = (
            "[MOCK DRAFT] Vapi Integration Agent — integration draft (DRAFT ONLY)\n"
            f"Client: {client} | Purpose: {purpose}\n"
            "Live stack (Vapi only):\n"
            "- Provider: Vapi | Assistant: Sophia (live receptionist)\n"
            "- Org: 1861a735 | Phone: +1 (947) 223-0244\n"
            "- Model: GPT-4o-mini | Voice: Emma | Transcription: Deepgram nova-3\n"
            "Integration steps (DRAFT plan — কোনো ধাপ execute হয়নি):\n"
            "1. Client-এর need অনুযায়ী Sophia-র call flow + prompt draft নেওয়া।\n"
            "2. Booking link যুক্ত করা: "
            f"{BOOKING_LINK} (15 min, New York Time)।\n"
            "3. Call log / follow-up-এর জন্য n8n workflow notes নেওয়া "
            "(READY, not LIVE)।\n"
            "4. Boss-এর ok-এর পর হাতে প্রয়োগ + test call।\n"
            "Status: DRAFT plan only — live Vapi account-এ কিছু বদলানো হয়নি, "
            "কোনো API call হয়নি।\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Vapi integration DRAFT ONLY, "
            "কখনো live account বদলানো নয়। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
