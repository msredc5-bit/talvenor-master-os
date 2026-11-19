"""n8n Automation Engineer — n8n workflow draft notes (Dept 03, Phase 3).

ভূমিকা (role): n8n workflow-এর DRAFT notes বানানো — কখনো live workflow
import/run করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

n8n workflows READY, not LIVE — Boss-এর import + test বাকি। CRM (n8n Cloud
Data Tables) PLANNED, not live।
এই worker কখনো করে না: live workflow import/run করে না, webhook call করে
না, n8n account-এ ঢোকে না, কিছু পাঠায় না, খরচ করে না, মোছে না, দাম quote
করে না, client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না,
dental/medical নয়, workflow live বলে দাবি করে না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class N8nAutomationEngineer:
    """n8n workflow DRAFT notes ONLY — কখনো live workflow চালায় না।"""

    task_kind = "n8n_automation"
    gate = None
    department = "03-ai-engineering"
    role = "n8n Automation Engineer"

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
        """n8n workflow DRAFT notes বানানো। কোনো file লেখে না, network ছোঁয় না।"""
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
            "Status: workflows READY, not LIVE — Boss-এর import + test বাকি।\n"
            "CRM: n8n Cloud Data Tables — PLANNED, not live।\n"
            "Workflow notes (DRAFT):\n"
            "1. Trigger — Vapi/Sophia call শেষ হলে call log আসে।\n"
            "2. Step — call-এর তথ্য (নাম, phone, service, booking) সাজানো হয়।\n"
            "3. Step — booking থাকলে booking link-এর বিবরণ যুক্ত করা হয়: "
            f"{BOOKING_LINK} (15 min, New York Time)।\n"
            "4. Step — follow-up-এর জন্য তথ্য রাখা হয় (CRM live হলে Data "
            "Tables-এ; এখন PLANNED, তাই হাতে রাখা হয়)।\n"
            "5. Next — Boss import + test করবেন; তার আগে live বলে দাবি নয়।\n"
            "Status: DRAFT notes only — কোনো live workflow নেই, কোনো "
            "import/run/webhook হয়নি।\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). n8n workflow DRAFT notes ONLY, "
            "কখনো live workflow নয়। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
