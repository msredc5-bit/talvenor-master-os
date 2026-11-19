"""Competitor Research Agent — competitor research draft (Phase 3).

ভূমিকা (role): শুধু প্রতিযোগী research-এর DRAFT লেখা — কখনো পাঠায় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

জানা প্রতিযোগী শুধু এরাই: Smith.ai, Abby, Ruby, CallRail Voice Assist — এই নামগুলোর বাইরে কোনো প্রতিযোগী বানানো যাবে না। কোনো প্রতিযোগীর দাম/পরিসংখ্যান/বৈশিষ্ট্য জানা না থাকলে "BOSS INPUT REQUIRED" — অনুমান করে লেখা যাবে না।

এই agent কখনো করে না: কিছু পাঠায় না, publish করে না, খরচ করে না,
delete করে না, client/প্রতিযোগী/দাম/পরিসংখ্যান বানায় না, কোনো
guarantee দেয় না, dental/medical বা patient-health ব্যবসা নেয় না।
Email PAUSED (2026-11-14 থেকে) — draft-ই শেষ কথা।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class CompetitorResearchAgent:
    """competitor research draft — DRAFT ONLY, কখনো পাঠায় না।"""

    task_kind = "competitor_research"
    gate = None
    department = "05-research-strategy"
    role = "Competitor Research Agent"

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
            "Competitor research draft for Talvenor. Known competitors only: Smith.ai, Abby, Ruby, CallRail Voice Assist. Never invent a competitor, price, or statistic. "
            f"Topic: {topic}. "
            "Do not invent any client fact, price, or statistic; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """competitor research draft। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Competitor research draft"
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

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — draft built from payload only."

        output = (
            "[MOCK DRAFT] Competitor research — DRAFT ONLY\n"
            f"Topic: {topic}\n"
            "Known competitors (verified names only): Smith.ai, Abby, Ruby, CallRail Voice Assist.\nPositioning note: Talvenor AI receptionist answers 24/7 so no missed call becomes a lost job.\nCompetitor prices/features: BOSS INPUT REQUIRED — verified source ছাড়া কোনো দাম/সংখ্যা লেখা হয়নি।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Competitor research draft ONLY। শুধু verified নাম ব্যবহার করা হয়েছে। "
            "কখনো পাঠানো নয়, কোনো খরচ নয়। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
