"""Sales Closer — sales call-এর প্রস্তুতি (sell section, Phase 7).

ভূমিকা (role): Boss-এর sales call-এর জন্য call-prep pack + close
checklist-এর DRAFT বানানো।
Gate: ok — pack ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), prep-ই শেষ কথা।
এই agent কখনো করে না: call করে না, close করে না, চুক্তি করে না,
দাম quote করে না, client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee
দেয় না। Call Boss নিজে নেন — এই agent শুধু তৈরি করে।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SalesCloserAgent:
    """Call-prep pack + close checklist DRAFT বানায়। কখনো call করে না।"""

    task_kind = "sales_close"
    gate = "ok"
    section = "sell"
    role = "Sales Closer"

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
        prospect = payload.get("prospect") or "BOSS INPUT REQUIRED"
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        goal = payload.get("goal") or "book the 15-min demo call"
        return (
            "Sales call-prep pack draft for a Talvenor demo call. "
            f"Prospect: {prospect}. Business: {business}. Goal: {goal}. "
            "Produce a short opening, likely questions with answers, "
            "and a close checklist. Boss takes the call himself — "
            "this is prep only, never a call or a close. "
            "Do not invent client facts or prices; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Call-prep pack DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Sales call prep"
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
        prospect = payload.get("prospect") or "BOSS INPUT REQUIRED"
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        goal = payload.get("goal") or "book the 15-min demo call"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — prep pack built from payload only."

        output = (
            "[MOCK DRAFT] Sales Call Prep — DRAFT ONLY\n"
            f"Prospect: {prospect} | Business: {business} | Goal: {goal}\n"
            "Call-prep pack (DRAFT):\n"
            "1. Opening (60 sec, plain US English): missed call = lost job; "
            "AI receptionist answers 24/7; book a 15-min demo call.\n"
            "2. Likely questions + answers (from real facts only): what it does "
            "(answers, qualifies, books), live stack Vapi/Sophia, "
            "booking link below. Price questions -> short call offer, "
            "never quote a price on the call prep.\n"
            "3. Close checklist (DRAFT): confirm demo time, send booking link, "
            "note next step, hand to OnboardingAgent after Boss says yes.\n"
            "4. Boss takes the call himself — this agent never calls, "
            "never closes, never signs anything.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Call-prep pack + close checklist, "
            "call নয়। Gate: ok — pack ব্যবহার করতে Boss-এর 'ok' লাগে। "
            "কোনো তথ্য না থাকলে 'BOSS INPUT REQUIRED' — বানানো তথ্য নেই।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
