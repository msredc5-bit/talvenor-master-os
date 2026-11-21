"""Sales Intelligence Agent — reply/lead signal insight draft (Sales & Growth, Phase 3).

Role: making a DRAFT insight from a prospect's reply or lead signal
— what the intent is, what the next step is. If the signal is not in the payload, it makes no
insight.
Gate: none — the insight DRAFT has no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never: invents a signal/reply/intent, sends any reply,
contacts anybody, quotes prices, gives any guarantee
gives none, no dental/medical.
Locked rule: decline = polite exit; interest/question/pricing/demo
request = draft only, never a price, a booking link may be given.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SalesIntelligenceAgent:
    """Signal insight DRAFT ONLY — from the given signal, nothing by guessing."""

    task_kind = "sales_intelligence"
    gate = None
    department = "01-sales-growth"
    role = "Sales Intelligence Agent"

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
        signal = payload.get("signal") or payload.get("reply_text") or "BOSS INPUT REQUIRED"
        return (
            "Sales intelligence insight draft for Talvenor. "
            f"Business: {business}. Signal/reply: {signal}. "
            "Classify intent ONLY from the given signal (interested / question / "
            "pricing / demo request / decline) and suggest the next step. If no "
            "signal is given, say NO SIGNAL — BOSS INPUT REQUIRED; never invent "
            "a signal. Pricing is LOCKED internal only — never quote a price; "
            "decline means polite exit."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes an insight DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Sales intelligence insight"
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
        signal = payload.get("signal") or ""
        reply_text = payload.get("reply_text") or ""
        platform = payload.get("platform") or "BOSS INPUT REQUIRED"
        raw = (signal or reply_text).strip()
        lowered = raw.lower()

        # Intent — only from the given signal/reply.
        if not raw:
            intent = "NO SIGNAL"
            next_step = "NO SIGNAL — BOSS INPUT REQUIRED; no insight can be given."
        elif any(w in lowered for w in ("not interested", "no thanks", "unsubscribe", "stop", "decline")):
            intent = "decline"
            next_step = "Polite exit — no more contact, no more pitch."
        elif any(w in lowered for w in ("price", "pricing", "cost", "how much", "quote")):
            intent = "pricing question"
            next_step = (
                "Show the reply DRAFT to Boss — never state a price (pricing LOCKED, "
                "internal only); say details will be given on a short call + booking link."
            )
        elif any(w in lowered for w in ("demo", "call", "book", "interested", "tell me more")):
            intent = "interested / demo request"
            next_step = (
                "Tell Boss; a DRAFT giving the 15-min call's booking link — "
                "Boss himself takes the call."
            )
        elif any(w in lowered for w in ("?", "how", "what", "when", "does it")):
            intent = "question"
            next_step = "Show the reply DRAFT to Boss — never send a reply directly."
        else:
            intent = "unclear — BOSS INPUT REQUIRED"
            next_step = "Signal is unclear — Boss/ReplyHandler will triage after seeing it."

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — insight built from payload only."

        output = (
            "[MOCK DRAFT] Sales Intelligence Agent — insight (DRAFT ONLY)\n"
            f"Business: {business} | Platform: {platform}\n"
            f"Signal/reply (given): {raw or 'BOSS INPUT REQUIRED'}\n"
            f"Intent: {intent}\n"
            f"Suggested next step: {next_step}\n"
            "Locked rule: decline = polite exit; interest/question/pricing/demo "
            "request = draft only, never a price, a booking link may be given.\n"
            "NOTE: This worker sends no reply — only an insight DRAFT; reply "
            "ReplyHandler (reply_triage, gate send) does the main triage work.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Insight DRAFT ONLY, from the given signal; "
            "No signal/reply was invented, no reply was sent. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
