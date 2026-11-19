"""New AI Product Research Agent — নতুন AI product research draft (Dept 08, Phase 3).

ভূমিকা (role): নতুন AI product-এর ভাবনা নিয়ে research-এর DRAFT লেখা —
কখনো product বানায় না, দাম ঠিক করে না, কিছু বিক্রি করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: product বানায় না, দাম/বাজারের সংখ্যা/
পরিসংখ্যান বানায় না, কিছু পাঠায় না, খরচ করে না, Vet Kit-এর কাজ
করে না (সেটা 02-Digital-Product-Department-এর), dental/medical নয়।
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244।
Retell DROPPED 2026-10-26 — কখনো production নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class NewAIProductResearchAgent:
    """নতুন AI product research DRAFT ONLY — বানানো তথ্য নয়, build নয়।"""

    task_kind = "new_ai_product_research"
    gate = None
    department = "08-product-innovation"
    role = "New AI Product Research Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "New AI product research draft for Talvenor. "
            f"Product idea: {topic}. "
            "Who it helps (US home-service owners only, never "
            "dental/medical), how it fits the live Vapi/Sophia "
            "receptionist service, and what still needs verification. "
            "Do not invent any product, price, market number, or "
            "statistic; mark missing facts 'BOSS INPUT REQUIRED'. "
            "Research only — no build, no guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """নতুন AI product research DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "New AI product research draft"
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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        audience = payload.get("audience") or "US home-service owners (plumbing, HVAC, roofing, vet)"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — research built from payload only."

        output = (
            "[MOCK DRAFT] New AI product research — DRAFT ONLY\n"
            f"Product idea: {topic}\n"
            f"Who it helps: {audience} — dental/medical never a target.\n"
            "Fit with live service: Vapi/Sophia receptionist answers 24/7 "
            f"(live, {TALVENOR_PHONE}); this idea is a research draft only — "
            "nothing built, nothing priced.\n"
            "What is NOT known (no invented numbers): market size, price, "
            "demand — all BOSS INPUT REQUIRED / verification pending.\n"
            "Next verification step ($0): Boss decides whether the idea is "
            "worth a deeper check; no spend, no build before his word.\n"
            "Vet No-Show Recovery Kit is NOT this department's work — it "
            "belongs to the Digital Product Department.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Research draft ONLY, build নয়। "
            "কোনো বানানো product, দাম, বাজারের সংখ্যা, পরিসংখ্যান নেই। "
            "Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
