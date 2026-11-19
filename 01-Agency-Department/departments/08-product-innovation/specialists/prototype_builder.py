"""Prototype Builder Agent — prototype plan draft ONLY (Dept 08, Phase 3).

ভূমিকা (role): prototype-এর PLAN-এর DRAFT লেখা — কখনো live prototype
বানায় না, কোনো code চালিয়ে service চালু করে না, কোনো খরচ করে না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: prototype বানায় না, code চালায় না, service
চালু করে না, সময়/খরচ/সাফল্যের সংখ্যা বানায় না, কিছু পাঠায় না,
খরচ করে না, Vet Kit-এর কাজ করে না (সেটা 02-Digital-Product-
Department-এর), dental/medical নয়।
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244।
Retell DROPPED 2026-10-26 — কখনো production নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class PrototypeBuilderAgent:
    """Prototype PLAN DRAFT ONLY — plan মাত্র, build নয়।"""

    task_kind = "prototype_builder"
    gate = None
    department = "08-product-innovation"
    role = "Prototype Builder Agent"

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
            "Prototype PLAN draft for Talvenor (plan only, never a build). "
            f"Prototype idea: {topic}. "
            "What it would show, steps 1-2-3, what it needs ($0 only), "
            "and what still needs verification. PLAN draft only — no "
            "prototype built, no code run, no service started. Do not "
            "invent time, cost, or success numbers; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Prototype PLAN DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না, code চালায় না।"""
        task = task or {}
        title = task.get("title") or "Prototype plan draft"
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
            brain_text = "No brain passed — plan built from payload only."

        output = (
            "[MOCK DRAFT] Prototype plan — DRAFT ONLY\n"
            f"Prototype idea: {topic}\n"
            "Status: PLAN DRAFT ONLY — কোনো prototype বানানো হয়নি, কোনো "
            "code চালানো হয়নি, কোনো service চালু হয়নি।\n"
            "Plan steps (idea only):\n"
            "  1. কী দেখাবে — ভাবনাটা এক লাইনে Boss-কে দেখানো।\n"
            "  2. কী লাগবে — শুধু $0, খরচ ছাড়া জিনিস; Boss-এর 'ok' ছাড়া কিছু নয়।\n"
            "  3. যাচাই — Boss plan দেখে বানাবেন কি না ঠিক করেন।\n"
            "What is NOT known (no invented numbers): time, cost, success "
            "rate — all BOSS INPUT REQUIRED / verification pending.\n"
            "Vet No-Show Recovery Kit is NOT this department's work — it "
            "belongs to the Digital Product Department.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Prototype PLAN draft ONLY — কোনো "
            "prototype বানানো হয়নি, কোনো code চালানো হয়নি। কোনো বানানো "
            "সময়/খরচ/সাফল্যের সংখ্যা নেই। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
