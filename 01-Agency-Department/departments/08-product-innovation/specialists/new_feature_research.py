"""New Feature Research Agent — নতুন feature research draft (Dept 08, Phase 3).

ভূমিকা (role): receptionist service-এ (Sophia, Vapi live) নতুন
feature-এর ভাবনা নিয়ে research-এর DRAFT লেখা — কখনো feature
বানায় না, বানানো হয়েছে বলে দাবি করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: feature বানায় না, live service বদলায় না,
client feedback/সংখ্যা/পরিসংখ্যান বানায় না, কিছু পাঠায় না,
খরচ করে না, dental/medical নয়।
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244।
Retell DROPPED 2026-10-26 — কখনো production নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class NewFeatureResearchAgent:
    """নতুন feature research DRAFT ONLY — ভাবনা মাত্র, build নয়।"""

    task_kind = "new_feature_research"
    gate = None
    department = "08-product-innovation"
    role = "New Feature Research Agent"

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
            "New feature research draft for the Talvenor receptionist "
            f"service (Sophia, Vapi live). Feature idea: {topic}. "
            "Which problem it solves (missed call = lost job), how it "
            "could fit the live receptionist, and what still needs "
            "verification. DRAFT idea only — never claim the feature "
            "is built. Do not invent client feedback or statistics; "
            "mark missing facts 'BOSS INPUT REQUIRED'. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """নতুন feature research DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "New feature research draft"
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
        problem = payload.get("problem") or "Missed calls mean lost jobs — receptionist must answer 24/7."

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — research built from payload only."

        output = (
            "[MOCK DRAFT] New feature research — DRAFT ONLY\n"
            f"Feature idea: {topic}\n"
            f"Problem it solves: {problem}\n"
            "Status: DRAFT IDEA ONLY — feature বানানো হয়নি, live service-এ "
            "কিছু বদলানো হয়নি।\n"
            "Fit with live service: Vapi/Sophia receptionist (live, "
            f"{TALVENOR_PHONE}) — feature-টা live কাজের সাথে মিলিয়ে ভাবা, "
            "চালু করা নয়।\n"
            "What is NOT known (no invented feedback): client feedback, "
            "usage numbers — all BOSS INPUT REQUIRED / verification pending.\n"
            "Next verification step ($0): Boss decides whether the idea is "
            "worth a deeper check; no build before his word.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Research draft ONLY, ভাবনা মাত্র — "
            "feature বানানো হয়নি, live service বদলানো হয়নি। কোনো বানানো "
            "client feedback/সংখ্যা নেই। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
