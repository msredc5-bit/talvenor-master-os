"""Follow-up Agent — follow-up draft (sell section, Phase 7).

ভূমিকা (role): শুধু follow-up-এর DRAFT লেখা — কখনো পাঠায় না।
Gate: send — follow-up পাঠাতে Boss-এর "send" লাগে; পাঠানো Boss নিজে করেন।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

Boss-এর standing 100-mail নিয়ম (2026-11-10, বাধ্যতামূলক):
কোনো state-এ 100টা first mail complete না হলে ওই state-এর কোনো
follow-up নয়। বর্তমান সত্য (2026-11-16): মোট first mail 162, কিন্তু
কোনো state-ই 100-তে পৌঁছায়নি — তাই এখন কোনো state-এর follow-up due
নয়। 20টা ready PA follow-up draft PARKED আছে। এই নিয়ম ভাঙা যাবে না:
state-এর first-mail সংখ্যা 100-এর নিচে হলে draft-এ "PARKED — follow-up
not due" লিখতে হবে, follow-up পাঠানোর মতো করে লেখা যাবে না।

এই agent কখনো করে না: auto-send করে না, follow-up পাঠায় না, 100-mail
নিয়ম ভাঙে না, দাম quote করে না, client-এর তথ্য/পরিসংখ্যান বানায় না,
কোনো guarantee দেয় না, dental/medical নয়।
Email PAUSED (2026-11-14 থেকে) — draft-ই শেষ কথা।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# Boss-এর standing নিয়ম: কোনো state-এ 100 first mail না হলে follow-up নয়।
FIRST_MAILS_TOTAL = 162
FOLLOWUP_THRESHOLD_PER_STATE = 100

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class FollowUpAgent:
    """Follow-up draft ONLY — 100-mail নিয়ম মেনে, কখনো পাঠায় না।"""

    task_kind = "followup_draft"
    gate = "send"
    section = "sell"
    role = "Follow-up Agent"

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
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        return (
            "Follow-up email draft for a Talvenor prospect. "
            f"Prospect: {prospect}. State: {state}. "
            "Short, plain US English, one CTA (15-min demo call). "
            "Respect the 100-mail rule: no follow-up for a state until "
            "that state's first mails reach 100. Do not invent client "
            "facts or prices; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Follow-up DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Follow-up draft"
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
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        state_first_mails = payload.get("state_first_mails")

        # 100-mail নিয়ম: state-এর সংখ্যা জানা থাকলে যাচাই করা, না থাকলে
        # BOSS INPUT REQUIRED — অনুমান করে follow-up due বলা যাবে না।
        if state_first_mails is None:
            due_line = (
                "100-mail rule check: state first-mail count = "
                "BOSS INPUT REQUIRED — follow-up due কি না বলা যাচ্ছে না, "
                "তাই এই draft PARKED।"
            )
            due = False
        else:
            try:
                count = int(state_first_mails)
            except (TypeError, ValueError):
                count = -1
            if count >= FOLLOWUP_THRESHOLD_PER_STATE:
                due_line = (
                    f"100-mail rule check: {state} first mails = {count} "
                    f"(threshold {FOLLOWUP_THRESHOLD_PER_STATE}) — follow-up due।"
                )
                due = True
            else:
                due_line = (
                    f"100-mail rule check: {state} first mails = {count} "
                    f"(threshold {FOLLOWUP_THRESHOLD_PER_STATE}) — "
                    "PARKED, follow-up not due yet।"
                )
                due = False

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — follow-up built from payload only."

        output = (
            "[MOCK DRAFT] Follow-up — DRAFT ONLY\n"
            f"Prospect: {prospect} | State: {state}\n"
            f"{due_line}\n"
            "Overall first mails (real, 2026-11-16): "
            f"{FIRST_MAILS_TOTAL} — no state at 100 yet।\n"
            "Follow-up draft (short, plain US English, 1 CTA):\n"
            "\"Hi — quick follow-up. Missed calls still mean lost jobs, "
            "and our AI receptionist answers 24/7 so none slip through. "
            "Worth a 15-min call? Book here: "
            f"{BOOKING_LINK}\""
            + ("\nStatus: DUE — draft ready for Boss review (send needs 'send')."
               if due else
               "\nStatus: PARKED — do NOT send; 100-mail rule not met for this state.")
            + f"\nPhone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Follow-up draft ONLY, কখনো পাঠানো নয়। "
            "100-mail নিয়ম মানা হয়েছে — state 100 first mail না হলে PARKED। "
            "Email PAUSED (2026-11-14 থেকে)। Gate: send।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
