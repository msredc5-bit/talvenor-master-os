"""Deployment Agent — deployment plan draft ONLY (Dept 03, Phase 3).

ভূমিকা (role): deployment-এর plan DRAFT বানানো — কখনো কিছু deploy করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই; deploy-এর জন্য Boss-এর
"ok" + manual steps লাগে, সেটা এই worker-এর বাইরে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই worker কখনো করে না: কিছু deploy করে না, file লেখে না, server-এ ঢোকে
না, command চালায় না, কিছু পাঠায় না, খরচ করে না, মোছে না, দাম quote
করে না, client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না,
dental/medical নয়, deploy হয়েছে বলে দাবি করে না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class DeploymentAgent:
    """Deployment plan DRAFT ONLY — কখনো deploy করে না।"""

    task_kind = "deployment"
    gate = None
    department = "03-ai-engineering"
    role = "Deployment Agent"

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
        what = payload.get("what") or "BOSS INPUT REQUIRED"
        target = payload.get("target") or "BOSS INPUT REQUIRED"
        return (
            "Deployment plan draft for a Talvenor client. "
            f"Client: {client}. What: {what}. Target: {target}. "
            "Deployment needs Boss 'ok' plus manual steps; no worker "
            "deploys anything. List check, ok, manual deploy, verify steps "
            "as a DRAFT plan only. Do not invent client facts; mark missing "
            "facts 'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Deployment plan DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Deployment plan draft"
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
        what = payload.get("what") or "BOSS INPUT REQUIRED"
        target = payload.get("target") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — deployment plan built from payload only."

        output = (
            "[MOCK DRAFT] Deployment Agent — deployment plan (DRAFT ONLY)\n"
            f"Client: {client} | What: {what} | Target: {target}\n"
            "Rule: deployment-এ Boss-এর \"ok\" + manual steps লাগে; কোনো "
            "worker deploy করে না।\n"
            "Plan steps (DRAFT — কোনো ধাপ execute হয়নি):\n"
            "1. Check — কী deploy হবে, কোথায়, আগের draft-গুলো (solution, "
            "call flow, prompt, Vapi plan) Boss দেখেছেন কি না।\n"
            "2. Ok — Boss-এর exact word \"ok\" ছাড়া deploy নয়।\n"
            "3. Manual deploy — Boss/Elora হাতে deploy করবেন; এই worker "
            "file লেখে না, server-এ ঢোকে না, command চালায় না।\n"
            "4. Verify — Boss-এর signed-in session-এ real run দেখে তবেই "
            "live বলা যাবে; তার আগে DRAFT-ই শেষ কথা।\n"
            "Booking link (real): "
            f"{BOOKING_LINK} (15 min, New York Time)\n"
            "Status: DRAFT plan only — কিছু deploy করা হয়নি।\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Deployment plan DRAFT ONLY, "
            "কখনো deploy নয়। Gate: none (deploy-এর জন্য Boss-এর ok + "
            "manual steps, এই worker-এর বাইরে)।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
