"""CRM Manager Agent — CRM organisation plan draft (Sales & Growth, Phase 3).

ভূমিকা (role): Lead-দের CRM-এ সাজানোর DRAFT organisation plan বানানো।
CRM = n8n Cloud Data Tables, PLANNED, live নয় — তাই কোনো live CRM ছোঁয়
না, কোনো record বানায় না, শুধু সাজানোর plan DRAFT দেয়।
Gate: none — plan DRAFT-এ কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: live CRM-এর দাবি করে না, live record বানায় না,
record-এর তথ্য বানায় না, কিছু পাঠায় না, দাম quote করে না,
কোনো guarantee দেয় না, dental/medical নয়।
DB = JSON store files — এটাই DB, CRM আলাদা জিনিস, live নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# CRM record-এর field-এর ছক (plan মাত্র, live record নয়)।
RECORD_FIELDS = (
    "business name",
    "state",
    "tier",
    "strength",
    "contact",
    "status",
    "next step",
)
STAGES = ("new", "contacted", "replied", "booked")


class CRMManagerAgent:
    """CRM organisation plan DRAFT ONLY — CRM live নয়, record বানায় না।"""

    task_kind = "crm_manage"
    gate = None
    department = "01-sales-growth"
    role = "CRM Manager Agent"

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
        business = payload.get("business_name") or "BOSS INPUT REQUIRED"
        tier = payload.get("tier") or "BOSS INPUT REQUIRED"
        stage = payload.get("stage") or "BOSS INPUT REQUIRED"
        return (
            "CRM organisation plan draft for Talvenor. CRM is n8n Cloud Data "
            "Tables, PLANNED, not live — draft a plan only, never claim a live "
            "CRM or live records. "
            f"Business: {business}. Tier: {tier}. Stage: {stage}. "
            "List the record fields, the stage meaning, and the next step by "
            "tier. Mark missing facts 'BOSS INPUT REQUIRED'. No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """CRM organisation plan DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "CRM organisation plan"
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
        business = payload.get("business_name") or "BOSS INPUT REQUIRED"
        tier = payload.get("tier") or "BOSS INPUT REQUIRED"
        stage = payload.get("stage") or "BOSS INPUT REQUIRED"
        next_step = payload.get("next_step") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — CRM plan built from payload only."

        fields_line = "; ".join(RECORD_FIELDS)
        stages_line = " → ".join(STAGES)
        output = (
            "[MOCK DRAFT] CRM Manager Agent — organisation plan (DRAFT ONLY)\n"
            "CRM: n8n Cloud Data Tables — PLANNED, NOT LIVE. কোনো live CRM, "
            "live record, live sync-এর দাবি নয়।\n"
            f"Business: {business} | Tier: {tier} | Stage: {stage} | Next step: {next_step}\n"
            f"Record field (ছক মাত্র): {fields_line}.\n"
            f"Stage flow: {stages_line}.\n"
            "Tier অনুযায়ী next step: Tier 1 আগে outreach, Tier 2 তারপর, Tier 4 পরে।\n"
            "Dental/medical বা patient-health ব্যবসা CRM-এও যায় না — সবসময় DQ।\n"
            "NOTE: CRM live না হওয়া পর্যন্ত এই plan DRAFT-ই থাকে; Boss CRM live "
            "করলে তবেই plan অনুযায়ী record সাজানো হবে। DB = JSON store files — "
            "এটাই DB, CRM আলাদা জিনিস।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). CRM organisation plan ONLY; CRM PLANNED, "
            "not live — কোনো live record বানানো হয়নি। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
