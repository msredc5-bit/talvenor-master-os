"""Lead Scoring Agent — STRONG/MEDIUM/WEAK to Tier 1/2/4 scoring draft (Sales & Growth, Phase 3).

Role: making a DRAFT scoring to put verified leads into tiers —
from the strength/score given in the payload; if there is no signal, it gives no score.
Gate: none — the scoring DRAFT has no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Scoring rules (LOCKED):
- STRONG 80–100 → Tier 1
- STRONG 60–79 → Tier 2
- MEDIUM → at most Tier 2 (never Tier 1, whatever the score)
- WEAK → Tier 4

This agent never: sets score/strength/tier by guessing, sends
anything, quotes prices, gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class LeadScoringAgent:
    """Scoring DRAFT ONLY — tier from the given signal, nothing by guessing."""

    task_kind = "lead_score"
    gate = None
    department = "01-sales-growth"
    role = "Lead Scoring Agent"

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
        """Record a PENDING approval — not execute, not auto-approve."""
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
        business = payload.get("business_name") or "BOSS INPUT REQUIRED"
        strength = payload.get("strength") or "BOSS INPUT REQUIRED"
        score = payload.get("score", "BOSS INPUT REQUIRED")
        return (
            "Lead scoring draft for Talvenor. "
            f"Business: {business}. Strength: {strength}. Score: {score}. "
            "Apply the locked rule: STRONG 80-100 Tier 1, STRONG 60-79 Tier 2, "
            "MEDIUM caps Tier 2, WEAK Tier 4. If strength or score is missing, "
            "say NOT SCORED — BOSS INPUT REQUIRED; never invent a score. "
            "No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a scoring DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Lead scoring draft"
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
        business = payload.get("business_name") or "BOSS INPUT REQUIRED"
        strength = (payload.get("strength") or "").strip().upper() or None
        raw_score = payload.get("score")
        score = None
        if raw_score is not None:
            try:
                score = int(raw_score)
            except (TypeError, ValueError):
                score = None

        # Deriving the tier — only from the given information.
        tier = None
        tier_note = ""
        if strength is None and score is None:
            tier_note = "NOT SCORED — both strength and score are BOSS INPUT REQUIRED."
        elif strength == "WEAK":
            tier = "Tier 4"
            tier_note = "WEAK → Tier 4 (whatever the score)."
        elif strength == "MEDIUM":
            tier = "Tier 2"
            tier_note = "MEDIUM → at most Tier 2 (not Tier 1)."
        elif strength == "STRONG":
            if score is None:
                tier_note = "STRONG, but score is BOSS INPUT REQUIRED — cannot say Tier 1 or Tier 2."
            elif score >= 80:
                tier = "Tier 1"
                tier_note = "STRONG 80–100 → Tier 1."
            elif score >= 60:
                tier = "Tier 2"
                tier_note = "STRONG 60–79 → Tier 2."
            else:
                tier_note = "STRONG but score is below 60 — strength/score do not match, BOSS INPUT REQUIRED."
        elif strength is not None:
            tier_note = f"Strength '{strength}' is not recognised — it must be STRONG/MEDIUM/WEAK; BOSS INPUT REQUIRED."
        else:
            # Only a score exists, no strength.
            if score is not None and score >= 80:
                tier_note = "Score 80+ but strength is BOSS INPUT REQUIRED — cannot say Tier 1."
            elif score is not None and score >= 60:
                tier_note = "Score 60–79 but strength is BOSS INPUT REQUIRED — cannot say the tier."
            else:
                tier_note = "Score below 60, strength is BOSS INPUT REQUIRED — cannot say the tier."

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — scoring built from payload only."

        output = (
            "[MOCK DRAFT] Lead Scoring Agent — scoring (DRAFT ONLY)\n"
            f"Business: {business}\n"
            f"Strength: {strength or 'BOSS INPUT REQUIRED'} | "
            f"Score: {score if score is not None else 'BOSS INPUT REQUIRED'}\n"
            f"Tier: {tier or 'NOT SCORED'}\n"
            f"{tier_note}\n"
            "Rules (LOCKED): STRONG 80–100 Tier 1; STRONG 60–79 Tier 2; "
            "MEDIUM at most Tier 2; WEAK Tier 4.\n"
            "Dental/medical or patient-health businesses never get a score — always DQ.\n"
            "Next step: Tier 1/2 lead → OutreachDrafter (outreach_draft, gate send) — "
            "DRAFT only; Email PAUSED (since 2026-11-14). For follow-up, the 100-mail rule: "
            "no follow-up in any state until 100 first mails (PA 37 → PARKED).\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Scoring DRAFT ONLY, from the given signal; "
            "No score/strength was invented. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
