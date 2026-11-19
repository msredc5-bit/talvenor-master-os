"""Lead Scoring Agent — STRONG/MEDIUM/WEAK to Tier 1/2/4 scoring draft (Sales & Growth, Phase 3).

ভূমিকা (role): যাচাই হওয়া lead-কে tier-এ ফেলার DRAFT scoring বানানো —
payload-এ দেওয়া strength/score থেকেই; signal না থাকলে score দেয় না।
Gate: none — scoring DRAFT-এ কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

Scoring নিয়ম (LOCKED):
- STRONG 80–100 → Tier 1
- STRONG 60–79 → Tier 2
- MEDIUM → সর্বোচ্চ Tier 2 (score যতই হোক Tier 1 নয়)
- WEAK → Tier 4

এই agent কখনো করে না: score/strength/tier আন্দাজে বসায় না, কিছু
পাঠায় না, দাম quote করে না, কোনো guarantee দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class LeadScoringAgent:
    """Scoring DRAFT ONLY — দেওয়া signal থেকে tier, আন্দাজে কিছু নয়।"""

    task_kind = "lead_score"
    gate = None
    department = "01-sales-growth"
    role = "Lead Scoring Agent"

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
        """Scoring DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
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

        # Tier বের করা — শুধু দেওয়া তথ্য থেকে।
        tier = None
        tier_note = ""
        if strength is None and score is None:
            tier_note = "NOT SCORED — strength ও score দুটোই BOSS INPUT REQUIRED।"
        elif strength == "WEAK":
            tier = "Tier 4"
            tier_note = "WEAK → Tier 4 (score যাই হোক)।"
        elif strength == "MEDIUM":
            tier = "Tier 2"
            tier_note = "MEDIUM → সর্বোচ্চ Tier 2 (Tier 1 নয়)।"
        elif strength == "STRONG":
            if score is None:
                tier_note = "STRONG, কিন্তু score BOSS INPUT REQUIRED — Tier 1 না Tier 2 বলা যাচ্ছে না।"
            elif score >= 80:
                tier = "Tier 1"
                tier_note = "STRONG 80–100 → Tier 1।"
            elif score >= 60:
                tier = "Tier 2"
                tier_note = "STRONG 60–79 → Tier 2।"
            else:
                tier_note = "STRONG কিন্তু score 60-এর নিচে — strength/score মিলছে না, BOSS INPUT REQUIRED।"
        elif strength is not None:
            tier_note = f"Strength '{strength}' চেনা যাচ্ছে না — STRONG/MEDIUM/WEAK হতে হবে; BOSS INPUT REQUIRED।"
        else:
            # শুধু score আছে, strength নেই।
            if score is not None and score >= 80:
                tier_note = "Score 80+ কিন্তু strength BOSS INPUT REQUIRED — Tier 1 বলা যাচ্ছে না।"
            elif score is not None and score >= 60:
                tier_note = "Score 60–79 কিন্তু strength BOSS INPUT REQUIRED — tier বলা যাচ্ছে না।"
            else:
                tier_note = "Score 60-এর নিচে, strength BOSS INPUT REQUIRED — tier বলা যাচ্ছে না।"

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
            "নিয়ম (LOCKED): STRONG 80–100 Tier 1; STRONG 60–79 Tier 2; "
            "MEDIUM সর্বোচ্চ Tier 2; WEAK Tier 4।\n"
            "Dental/medical বা patient-health ব্যবসা কখনো score পায় না — সবসময় DQ।\n"
            "পরের ধাপ: Tier 1/2 lead → OutreachDrafter (outreach_draft, gate send) — "
            "DRAFT only; Email PAUSED (2026-11-14 থেকে)। Follow-up-এ 100-mail rule: "
            "কোনো state-এ 100 first mail না হলে follow-up নয় (PA 37 → PARKED)।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Scoring DRAFT ONLY, দেওয়া signal থেকে; "
            "কোনো score/strength বানানো হয়নি। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
