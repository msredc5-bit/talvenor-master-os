"""Technology Evaluation Agent — technology evaluation draft (Dept 08, Phase 3).

ভূমিকা (role): নতুন tool/technology যাচাই করে evaluation-এর DRAFT
লেখা — শুধু যাচাই করা সত্য (verified fact) দিয়ে তুলনা, কোনো বানানো
benchmark, দাম, পরিসংখ্যান নয়।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

যাচাই করা সত্য: Vapi LIVE (Sophia, +1 (947) 223-0244, GPT-4o-mini,
Emma voice, Deepgram nova-3)। Retell DROPPED 2026-10-26 — কখনো
production নয়। DB = JSON store files। CRM n8n Cloud Data Tables
PLANNED, live নয়। $0 spend cap — কোনো tool কেনার প্রস্তাব নয়।
এই agent কখনো করে না: benchmark/দাম/পরিসংখ্যান বানায় না, tool
কেনে না, live stack বদলায় না, কিছু পাঠায় না, খরচ করে না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class TechnologyEvaluationAgent:
    """Technology evaluation DRAFT ONLY — verified fact only, বানানো নয়।"""

    task_kind = "technology_evaluation"
    gate = None
    department = "08-product-innovation"
    role = "Technology Evaluation Agent"

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
            "Technology evaluation draft for Talvenor. "
            f"Tool/technology: {topic}. "
            "Compare against the verified live stack only: Vapi LIVE "
            "(Sophia, GPT-4o-mini, Emma voice, Deepgram nova-3); "
            "Retell DROPPED 2026-10-26, never production. Pros/cons "
            "from verified facts only; what is unknown stays "
            "'BOSS INPUT REQUIRED'. No invented benchmarks, prices, "
            "or statistics. $0 spend cap — no purchase proposal."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Technology evaluation DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Technology evaluation draft"
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
        use_case = payload.get("use_case") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — evaluation built from payload only."

        output = (
            "[MOCK DRAFT] Technology evaluation — DRAFT ONLY\n"
            f"Tool/technology: {topic}\n"
            f"Use case: {use_case}\n"
            "Verified facts only:\n"
            "- Vapi LIVE — Sophia live receptionist, "
            f"{TALVENOR_PHONE}, GPT-4o-mini, Emma voice, Deepgram nova-3.\n"
            "- Retell DROPPED 2026-10-26 — never production, not an option.\n"
            "- DB = JSON store files; CRM n8n Cloud Data Tables PLANNED, live নয়.\n"
            "Pros/cons: only what is verified above — anything else is "
            "'BOSS INPUT REQUIRED' / verification pending.\n"
            "Cost: $0 spend cap — no purchase proposal; free / no-cost "
            "check only. No price quoted (pricing internal only).\n"
            "What is NOT known (no invented numbers): benchmarks, "
            "performance stats — all verification pending.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Evaluation draft ONLY, verified "
            "fact দিয়ে — কোনো বানানো benchmark, দাম, পরিসংখ্যান নেই। "
            "$0 spend cap মানা হয়েছে। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
