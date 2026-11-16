"""Service Delivery Manager — delivery পরিচালনা (delivery section, Phase 7).

ভূমিকা (role): receptionist delivery-র checklist + go-live verification
ধাপের DRAFT বানানো।
Gate: ok — delivery plan/go-live-এ Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), plan-ই শেষ কথা।
Live stack Vapi/Sophia — এই agent কখনো live build করে না, শুধু DRAFT
plan; QA pass + Boss-এর ok ছাড়া কোনো receptionist "live" বলা যাবে না।
এই agent কখনো করে না: live build করে না, live দাবি করে না, দাম quote
করে না, client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ServiceDeliveryManagerAgent:
    """Delivery checklist + go-live verification DRAFT বানায়। Live দাবি করে না।"""

    task_kind = "delivery_manage"
    gate = "ok"
    section = "delivery"
    role = "Service Delivery Manager"

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
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        qa_pass = payload.get("qa_pass")
        return (
            "Delivery checklist draft for a Talvenor receptionist. "
            f"Client: {client}. Business: {business}. "
            f"QA passed: {qa_pass}. "
            "Produce a delivery checklist and go-live verification steps. "
            "Live stack is Vapi/Sophia — this is a DRAFT plan only, "
            "never a live build. Never claim live without a QA pass "
            "and Boss ok. Do not invent client facts or prices; mark "
            "missing facts 'BOSS INPUT REQUIRED'."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Delivery checklist DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Delivery checklist"
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
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        qa_pass = payload.get("qa_pass")
        qa_line = "QA pass: BOSS INPUT REQUIRED" if qa_pass is None else (
            "QA pass: YES" if qa_pass else "QA pass: NO — go-live BLOCKED")

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — checklist built from payload only."

        output = (
            "[MOCK DRAFT] Delivery Checklist — DRAFT ONLY\n"
            f"Client: {client} | Business: {business} | {qa_line}\n"
            "Delivery checklist (DRAFT):\n"
            "1. Onboarding pack complete (business info, hours, services, "
            "transfer number) — missing facts: BOSS INPUT REQUIRED.\n"
            "2. Receptionist DRAFT build plan reviewed (RetellBuilder plan; "
            "live stack Vapi/Sophia).\n"
            "3. QAEngineer checklist run — verdict READY or CHANGES.\n"
            "4. Go-live verification steps (DRAFT): test call, emergency flow, "
            "callback handling, honest AI disclosure, end_call behavior.\n"
            "5. Go-live ONLY after QA pass + Boss 'ok'. Without both, "
            "the receptionist is NOT live — never claim otherwise.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delivery checklist + go-live "
            "verification DRAFT, live build নয়। Gate: ok। QA pass + Boss "
            "'ok' ছাড়া live দাবি করা যাবে না।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
