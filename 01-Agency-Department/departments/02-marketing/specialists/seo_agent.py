"""SEO Agent — SEO draft (Dept 02 Marketing).

Role: write a DRAFT of Talvenor's SEO — keyword suggestions, page
title/meta drafts, Google Business Profile suggestions. On no site/profile
does it change anything or publish anything.
Gate: none — the draft itself is safe, there is no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never: invents ranking/traffic/position numbers,
changes any site, quotes a price, gives any guarantee, invents client
information/statistics — no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SEOAgent:
    """SEO draft ONLY — a suggestion only, no invented ranking."""

    task_kind = "seo"
    gate = None
    department = "02-marketing"
    role = "SEO Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        page = payload.get("page") or "BOSS INPUT REQUIRED"
        niche = payload.get("niche") or "BOSS INPUT REQUIRED"
        return (
            "SEO draft for Talvenor (AI receptionist for US home-service owners). "
            f"Topic: {topic}. Page: {page}. Niche: {niche}. "
            "Keyword suggestions, page title draft, meta description draft, "
            "heading outline, Google Business Profile suggestion. Suggestions "
            "ONLY — never invent rankings, traffic, or positions. No invented "
            "client facts or prices; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making an SEO DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "SEO draft"
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
        page = payload.get("page") or "BOSS INPUT REQUIRED"
        niche = payload.get("niche") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — SEO draft built from payload only."

        output = (
            "[MOCK DRAFT] SEO — DRAFT ONLY\n"
            f"Topic: {topic} | Page: {page} | Niche: {niche}\n"
            "Keyword suggestions (suggestions ONLY — no ranking/traffic numbers):\n"
            "- Primary: AI receptionist for plumbers / AI receptionist for "
            "home service businesses\n"
            "- Supporting: AI phone answering service, virtual receptionist "
            "for HVAC, after-hours call answering for roofers\n"
            "Page title draft: \"Never Miss a Call — AI Receptionist for "
            "Home Service Businesses | Talvenor\"\n"
            "Meta description draft: \"Talvenor's AI receptionist answers "
            "every call 24/7 and books jobs for plumbers, HVAC, and roofers. "
            "Book a 15-min call.\"\n"
            "Heading outline: H1 missed call = lost job; H2 how the AI "
            "receptionist answers; H2 booking + the live receptionist.\n"
            "Google Business Profile suggestion: category 'Virtual "
            "receptionist service'; description uses the same headline; "
            "booking link in profile.\n"
            "Ranking/traffic: no numbers — none invented, none claimed.\n"
            f"Booking link: {BOOKING_LINK} (New York Time)\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). SEO draft ONLY, no site changed "
            "no publish. No ranking/traffic number was invented. "
            "No invented client, price, statistic, or guarantee. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
