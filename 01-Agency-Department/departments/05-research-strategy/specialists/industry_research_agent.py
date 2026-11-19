"""Industry Research Agent — industry research draft (Phase 3).

ভূমিকা (role): শুধু home-service industry research-এর DRAFT লেখা — কখনো পাঠায় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

প্রতিটা পরিসংখ্যানের source লাগবে — source না থাকলে "UNVERIFIED" লেবেল দিতে হবে, কখনো source ছাড়া সংখ্যা সত্য বলে লেখা যাবে না।

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


class IndustryResearchAgent:
    """industry research draft — DRAFT ONLY, কখনো পাঠায় না।"""

    task_kind = "industry_research"
    gate = None
    department = "05-research-strategy"
    role = "Industry Research Agent"

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
            "Industry research draft for Talvenor home-service market (plumbing, HVAC, roofing, etc.). Every statistic needs a source or is labelled UNVERIFIED. "
            f"Topic: {topic}. "
            "Do not invent any client fact, price, or statistic; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """industry research draft। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Industry research draft"
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
            "[MOCK DRAFT] Industry research — DRAFT ONLY\n"
            f"Topic: {topic}\n"
            "Focus: US home-service SMBs (plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet).\nKey theme: missed calls mean lost jobs; AI receptionist answers 24/7.\nStatistics: BOSS INPUT REQUIRED — source ছাড়া কোনো সংখ্যা লেখা হয়নি; source না থাকলে UNVERIFIED লেবেল লাগবে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Industry research draft ONLY। Source ছাড়া কোনো সংখ্যা সত্য বলে লেখা হয়নি। "
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
