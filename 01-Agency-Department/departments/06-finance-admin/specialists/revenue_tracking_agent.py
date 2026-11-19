"""Revenue Tracking Agent — revenue tracking template draft (Dept 06, Phase 3).

ভূমিকা (role): শুধু revenue tracking-এর TEMPLATE-এর DRAFT বানানো —
কখনো revenue বানায় না, client-এর নাম/টাকা বসায় না।
Gate: None — draft নিজেই নিরাপদ।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

সত্য অবস্থা (2026-11-19): paying client 0, revenue $0 — track করার
মতো revenue নেই। Template-এ শুধু column header + খালি row-র জায়গা;
কোনো ভরা row নেই। LOCKED pricing internal only — template-এ দামের
সংখ্যা বসানো হয় না, prospect-কে কখনো দাম quote নয়।

এই agent কখনো করে না: revenue বানায় না, client/টাকা বসায় না,
invoice issue করে না, payment নেয় না, কিছু পাঠায় না, খরচ করে না,
দাম quote করে না, কোনো guarantee দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# সত্য অবস্থা (2026-11-19) — track করার মতো revenue নেই।
PAYING_CLIENTS = 0
REVENUE_TOTAL = 0

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class RevenueTrackingAgent:
    """Revenue tracking template DRAFT ONLY — কখনো revenue বানায় না।"""

    task_kind = "revenue_tracking"
    gate = None
    department = "06-finance-admin"
    role = "Revenue Tracking Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "Revenue tracking template draft for Talvenor. "
            f"Topic: {topic}. "
            "Paying clients 0, revenue $0 — there is nothing to track yet, "
            "so draft only the empty template structure (columns, no rows). "
            "Do not invent any client, revenue, price, or statistic; "
            "mark missing facts 'BOSS INPUT REQUIRED'. "
            "LOCKED pricing is internal only — never quote a price. "
            "No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Revenue tracking template DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Revenue tracking template"
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

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — template built from task only."

        output = (
            "[MOCK DRAFT] Revenue tracking template — DRAFT ONLY\n"
            f"Department: {self.department} | Worker: {self.role}\n"
            f"Paying clients (real, 2026-11-19): {PAYING_CLIENTS} | "
            f"Revenue (real): ${REVENUE_TOTAL} — track করার মতো revenue নেই।\n"
            "Template (columns only — কোনো ভরা row নেই):\n"
            "Client | Tier | Monthly | Build fee | Status\n"
            "--- row ভরবে Boss, paying client এলে ---\n"
            "Total revenue: $0 (paying client 0)।\n"
            "LOCKED pricing internal only — template-এ দামের সংখ্যা বসানো "
            "হয় না; prospect-কে কখনো দাম quote নয়।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Revenue tracking template ONLY — "
            "কোনো revenue/client/টাকা বানানো হয়নি। Paying client 0, "
            "revenue $0। Gate: None।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
