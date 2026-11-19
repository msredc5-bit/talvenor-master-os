"""Business Intelligence Agent — business intelligence draft (Phase 3).

ভূমিকা (role): শুধু আসল সংখ্যা দিয়ে BI সারাংশের DRAFT লেখা — কখনো পাঠায় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

শুধু আসল সংখ্যা: paying client 0, প্রথম মেইল 162, Email PAUSED (2026-11-14 থেকে), revenue $0। কোনো metric বানানো যাবে না।

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


class BusinessIntelligenceAgent:
    """business intelligence draft — DRAFT ONLY, কখনো পাঠায় না।"""

    task_kind = "business_intelligence"
    gate = None
    department = "05-research-strategy"
    role = "Business Intelligence Agent"

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
            "Business intelligence draft for Talvenor from REAL numbers only: paying clients 0, first mails 162, email PAUSED since 2026-11-14, revenue $0. Never invent a metric. "
            f"Topic: {topic}. "
            "Do not invent any client fact, price, or statistic; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """business intelligence draft। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Business intelligence draft"
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
            "[MOCK DRAFT] Business intelligence — DRAFT ONLY\n"
            f"Topic: {topic}\n"
            "Real numbers only (2026-11-19): paying clients 0; first mails 162; email PAUSED since 2026-11-14; revenue $0; spend cap $0.\nLive stack: Vapi/Sophia, +1 (947) 223-0244; booking link 15-min, New York Time.\nAny other metric: BOSS INPUT REQUIRED — আসল সংখ্যা ছাড়া কিছু লেখা হয়নি।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). BI draft ONLY, আসল সংখ্যা দিয়ে। কোনো metric বানানো হয়নি। "
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
