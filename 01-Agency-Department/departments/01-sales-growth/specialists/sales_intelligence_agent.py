"""Sales Intelligence Agent — reply/lead signal insight draft (Sales & Growth, Phase 3).

ভূমিকা (role): Prospect-এর reply বা lead signal থেকে insight-এর DRAFT
বানানো — intent কী, পরের ধাপ কী। Signal payload-এ না থাকলে insight
বানায় না।
Gate: none — insight DRAFT-এ কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: signal/reply/intent বানায় না, কোনো reply
পাঠায় না, কাউকে contact করে না, দাম quote করে না, কোনো guarantee
দেয় না, dental/medical নয়।
Locked rule: decline = polite exit; interest/question/pricing/demo
request = draft only, কখনো price নয়, booking link দেওয়া যায়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class SalesIntelligenceAgent:
    """Signal insight DRAFT ONLY — দেওয়া signal থেকে, আন্দাজে কিছু নয়।"""

    task_kind = "sales_intelligence"
    gate = None
    department = "01-sales-growth"
    role = "Sales Intelligence Agent"

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
        """Insight DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
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

        # Intent — শুধু দেওয়া signal/reply থেকে।
        if not raw:
            intent = "NO SIGNAL"
            next_step = "NO SIGNAL — BOSS INPUT REQUIRED; insight দেওয়া যাচ্ছে না।"
        elif any(w in lowered for w in ("not interested", "no thanks", "unsubscribe", "stop", "decline")):
            intent = "decline"
            next_step = "Polite exit — আর contact নয়, আর pitch নয়।"
        elif any(w in lowered for w in ("price", "pricing", "cost", "how much", "quote")):
            intent = "pricing question"
            next_step = (
                "Reply DRAFT Boss-কে দেখানো — দাম কখনো বলা নয় (pricing LOCKED, "
                "internal only); short call-এ details দেওয়ার কথা + booking link।"
            )
        elif any(w in lowered for w in ("demo", "call", "book", "interested", "tell me more")):
            intent = "interested / demo request"
            next_step = (
                "Boss-কে জানানো; 15-min call-এর booking link দেওয়ার DRAFT — "
                "Boss নিজে call নেন।"
            )
        elif any(w in lowered for w in ("?", "how", "what", "when", "does it")):
            intent = "question"
            next_step = "Reply DRAFT Boss-কে দেখানো — কখনো সরাসরি reply পাঠানো নয়।"
        else:
            intent = "unclear — BOSS INPUT REQUIRED"
            next_step = "Signal অস্পষ্ট — Boss/ReplyHandler দেখে triage করবেন।"

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
            "request = draft only, কখনো price নয়, booking link দেওয়া যায়।\n"
            "NOTE: এই worker কোনো reply পাঠায় না — insight DRAFT মাত্র; reply "
            "triage-এর মূল কাজ ReplyHandler (reply_triage, gate send) করে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Insight DRAFT ONLY, দেওয়া signal থেকে; "
            "কোনো signal/reply বানানো হয়নি, কোনো reply পাঠানো হয়নি। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
