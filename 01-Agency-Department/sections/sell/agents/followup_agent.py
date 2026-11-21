"""Follow-up Agent — follow-up draft (sell section, Phase 7).

Role: writing only the follow-up DRAFT — never sending it.
Gate: send — sending a follow-up needs Boss's send; Boss sends it himself.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Boss's standing 100-mail rule (2026-11-10, mandatory):
without 100 first mails complete in a state, no follow-up for that state.
Current truth (2026-11-16): total first mail 162, but
no state has reached 100 — so no state's follow-up is due
now. 20 ready PA follow-up drafts are PARKED. This rule cannot be broken:
if a state's first-mail count is below 100, the draft must say PARKED — follow-up
not due, and it cannot be written as if to send a follow-up.

This agent never does this: it never auto-sends, never sends a follow-up, never breaks the 100-mail
rule, never quotes a price, never invents client information/statistics,
never gives a guarantee, no dental/medical.
Email PAUSED (since 2026-11-14) — the draft is the final word.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# Boss's standing rule: without 100 first mails in a state, no follow-up.
FIRST_MAILS_TOTAL = 162
FOLLOWUP_THRESHOLD_PER_STATE = 100

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class FollowUpAgent:
    """Follow-up draft ONLY — following the 100-mail rule, never sending."""

    task_kind = "followup_draft"
    gate = "send"
    section = "sell"
    role = "Follow-up Agent"

    def _gateway(self, approvals_path=None):
        """ApprovalGateway lazy-load — no repo import at top level."""
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
        """Recording a PENDING approval — not executing, not auto-approving."""
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
        """Building a follow-up DRAFT. Writes no file, touches no network."""
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

        # 100-mail rule: if the state's count is known, verify it; if not,
        # BOSS INPUT REQUIRED — do not claim a follow-up is due by guessing.
        if state_first_mails is None:
            due_line = (
                "100-mail rule check: state first-mail count = "
                "BOSS INPUT REQUIRED — whether a follow-up is due cannot be said, "
                "so this draft is PARKED."
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
                    f"(threshold {FOLLOWUP_THRESHOLD_PER_STATE}) — follow-up due."
                )
                due = True
            else:
                due_line = (
                    f"100-mail rule check: {state} first mails = {count} "
                    f"(threshold {FOLLOWUP_THRESHOLD_PER_STATE}) — "
                    "PARKED, follow-up not due yet."
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
            f"{FIRST_MAILS_TOTAL} — no state at 100 yet.\n"
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
            "DRAFT ONLY — mock brain ($0). Follow-up draft ONLY, never sent. "
            "The 100-mail rule is honored — without 100 first mails in the state, PARKED. "
            "Email PAUSED (since 2026-11-14). Gate: send."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
