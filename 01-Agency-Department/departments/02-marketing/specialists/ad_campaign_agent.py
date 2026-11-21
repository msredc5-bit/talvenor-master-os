"""Ad Campaign Agent — paid ad campaign DRAFT plan + analysis (Dept 02 Marketing).

Role: a DRAFT plan + performance
analysis of Talvenor's paid ad campaign — brief → structure → launch plan → results analysis.
It runs no live ad, changes no budget, touches no account/API, spends no
money — it gives a plan DRAFT; something happens only when Boss approves + funds it.
Gate: none — the draft itself is safe. To act on the plan (fund/spend/publish),
Boss's exact gate word is needed — when a gated action comes, a PENDING record is made in ApprovalGateway,
it is not executed.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Honest status (2026-11-21): paid ads were never run, $0 spent. No ad
account is connected. Paying client 0.

This agent never: makes/runs a live campaign, changes a budget,
touches a Meta/Google account, token, or API key, invents numbers, CPA, or ROAS,
sends anything, publishes anything, spends anything, deletes anything, quotes prices,
Gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Brand (LOCKED) — no creative brief without the brand in the plan.
BRAND_NAVY = "#0B1D33"
BRAND_TEAL = "#14B8A6"
BRAND_HEADLINE = "Never miss a call. Never lose a job."


class AdCampaignAgent:
    """Paid ad campaign DRAFT plan + analysis ONLY — no live ad, $0 spent."""

    task_kind = "ad_campaign"
    gate = None
    department = "02-marketing"
    role = "Ad Campaign Agent"

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

    def _grade(self, payload):
        """Red/Yellow/Green grade from the numbers Boss gave — None if there are no numbers."""
        try:
            impressions = float(payload.get("impressions"))
            clicks = float(payload.get("clicks"))
            conversions = float(payload.get("conversions"))
            spend = float(payload.get("spend"))
            target_cpa = float(payload.get("target_cpa"))
        except (TypeError, ValueError):
            return None
        if target_cpa <= 0:
            return None
        cpa = spend / conversions if conversions > 0 else None
        ctr = (clicks / impressions * 100.0) if impressions > 0 else 0.0
        if conversions == 0 and spend >= 1.5 * target_cpa:
            return ("🔴 Red — STOP", "0 conversions, 1.5×+ target CPA spent — burning money.")
        if cpa is not None and cpa >= 2 * target_cpa:
            return ("🔴 Red — STOP", "CPA 2×+ target — burning money.")
        if impressions >= 1000 and ctr < 0.5:
            return ("🔴 Red — STOP", "CTR below 0.5% on 1,000+ impressions — creative must change.")
        if cpa is not None and cpa <= target_cpa and conversions >= 10:
            return ("🟢 Green — SCALE", "CPA at or below target, 10+ conversions — increase budget by 20% every 48 hours.")
        if cpa is not None and 0.5 * target_cpa <= cpa <= 1.5 * target_cpa:
            return ("🟡 Yellow — WAIT", "CPA near target but little data — do not touch.")
        if impressions < 1000 or clicks < 20:
            return ("🟡 Yellow — WAIT", "Little data (< 1,000 impressions / < 20 clicks) — not time to judge yet.")
        return ("🟡 Yellow — WAIT", "No clear signal — more data is needed.")

    def _prompt(self, task):
        payload = task.get("payload") or {}
        offer = payload.get("offer") or "BOSS INPUT REQUIRED"
        audience = payload.get("audience") or "BOSS INPUT REQUIRED"
        budget = payload.get("budget") or "BOSS INPUT REQUIRED"
        target_cpa = payload.get("target_cpa") or "BOSS INPUT REQUIRED"
        landing = payload.get("landing_page") or BOOKING_LINK
        return (
            "Paid ad campaign DRAFT plan for Talvenor (AI receptionist for "
            "US home-service owners). "
            f"Offer: {offer}. Audience: {audience}. Budget: {budget}. "
            f"Target CPA: {target_cpa}. Landing: {landing}. "
            "Brief → structure → launch plan → results analysis. Creative is "
            "the #1 lever; Sales objective; broad targeting; warmup $2–5/day, "
            "+10–20% per 48h; pixel setup step required. DRAFT ONLY — no live "
            "ads, $0 spent. Never invent numbers, CPA, or ROAS; mark missing "
            "facts 'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes an ad campaign DRAFT plan + analysis. Writes no file, touches no network, runs nothing."""
        task = task or {}
        title = task.get("title") or "Ad campaign draft plan"
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
        offer = payload.get("offer") or "BOSS INPUT REQUIRED"
        audience = payload.get("audience") or "BOSS INPUT REQUIRED"
        budget = payload.get("budget") or "BOSS INPUT REQUIRED"
        target_cpa = payload.get("target_cpa") or "BOSS INPUT REQUIRED"
        landing = payload.get("landing_page") or BOOKING_LINK
        grade = self._grade(payload)

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — plan built from payload only."

        lines = [
            "[MOCK DRAFT] Ad campaign plan — DRAFT ONLY",
            f"Department: {self.department} | Worker: {self.role}",
            "DRAFT — no live ads, $0 spent. No ad account is connected.",
            "",
            "1. Brief:",
            f"   Offer: {offer}",
            f"   Audience: {audience}",
            f"   Budget: {budget} (only if Boss gives it — otherwise BOSS INPUT REQUIRED)",
            f"   Target CPA: {target_cpa}",
            f"   Landing page / booking link: {landing}",
            "",
            "2. Structure (DRAFT):",
            "   - Objective: Sales (not the Traffic objective — cheap clicks + spam).",
            "   - Targeting: broad — the creative itself will do the targeting; no over-targeting.",
            "   - Creative is the #1 lever (Bid × Estimated Action Rate × Ad Quality).",
            "   - Brand: navy " + BRAND_NAVY + " + teal " + BRAND_TEAL
            + "; headline \"" + BRAND_HEADLINE + "\".",
            "   - If it looks like an ad it gets skipped — interruption marketing, it must blend into the feed.",
            "",
            "3. Launch plan (DRAFT):",
            "   - The pixel setup step must be there — without conversion data there is no optimization.",
            "   - Warmup: start with $2–5/day, increase by 10–20% every 48 hours.",
            "   - Scaling without warmup risks an account ban.",
            "",
            "4. Results analysis (grade — from the numbers Boss gave):",
        ]
        if grade is not None:
            lines.append(f"   Grade: {grade[0]} — {grade[1]}")
            lines.append("   CPA is the North Star, not CTR. If Green, increase budget by 20% every 48 hours.")
            lines.append("   Fatigue flag: if CTR is falling / CPA is rising / frequency is 3+, a new creative variation is needed.")
        else:
            lines.append("   Boss did not give numbers (impressions, clicks, conversions, spend, target CPA) —")
            lines.append("   No grade was given without numbers; no numbers were invented.")
        lines += [
            "",
            "5. Funnel debugging (from the surface inward): Creative → Landing page →",
            "   Messaging → Product/pricing → Market. Do not judge CTR on < 1,000 impressions",
            "   ; do not judge the LP on < 100 LP visitors; if a Green has < 10 conversions, scale carefully.",
            "Profit check: AOV must be > CPA; ROAS = AOV / CPA (must be > 1.0).",
            f"Booking link: {BOOKING_LINK} (New York Time) | Phone: {TALVENOR_PHONE}",
            f"Brain note: {brain_text}",
        ]
        notes = (
            "DRAFT ONLY — mock brain ($0). Ad campaign plan + analysis ONLY — "
            "No live ad, budget change, or account touched. $0 spent. No numbers, "
            "CPA, or ROAS was invented. Gate: none (draft); spending/publishing needs Boss's gate word."
        )
        return {
            "status": "draft-ready",
            "output": "\n".join(lines),
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
