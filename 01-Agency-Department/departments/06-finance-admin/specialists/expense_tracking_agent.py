"""Expense Tracking Agent — expense DRAFT ledger entry + monthly report (Dept 06 Finance & Admin).

Role: make a DRAFT ledger entry + monthly report for each of Talvenor's expenses —
guard of the $0 cap — it does not approve spending, only
keeps the accounts. It makes an entry DRAFT; it is put in the ledger file only when Boss approves
— this worker itself writes no file.
Gate: none — the draft itself is safe. For spend, only Boss's "ok" — this worker
never approves spend.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

True state (2026-11-21): paying client 0, income $0, spending $0 cap —
Boss's money was not spent. The ledger is still empty — no spend happened.

This agent never: approves spend, changes the budget, writes a card
number, password, API key, invents a number, receipt, confirmation,
sends anything, publishes anything, spends anything, deletes anything, quotes a price,
gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Fixed categories — no making a category of your own.
CATEGORIES = {
    "API/Services": "API credit, SaaS subscription (Vapi, n8n)",
    "Tools": "Software license, utility",
    "Ads": "Paid ads (now $0 — if there is spending, Boss's separate funding is needed)",
    "Infrastructure": "Hosting, domain, CDN",
    "Subscriptions": "Recurring monthly/yearly service",
    "Other": "everything else (a reason must be written)",
}

# True state (2026-11-21) — no expense to track.
TOTAL_SPENT_USD = 0.0


class ExpenseTrackingAgent:
    """Expense DRAFT entry + report ONLY — no spend approval, writes no file."""

    task_kind = "expense_tracking"
    gate = None
    department = "06-finance-admin"
    role = "Expense Tracking Agent"

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
        amount = payload.get("amount") or "BOSS INPUT REQUIRED"
        vendor = payload.get("vendor") or "BOSS INPUT REQUIRED"
        category = payload.get("category") or "BOSS INPUT REQUIRED"
        return (
            "Expense tracking DRAFT for Talvenor. "
            f"Amount: {amount}. Vendor: {vendor}. Category: {category}. "
            "Fixed categories only; budget 80% warning, 100% STOP flag. "
            "Spend approved by Boss only — this worker never approves spend. "
            "Ledger is local JSON (store/expenses.json) — draft only, never "
            "write a file here. Never invent an amount, receipt, or "
            "confirmation; mark missing facts 'BOSS INPUT REQUIRED'. No card "
            "numbers, passwords, or API keys. No price, no guarantee, "
            "no dental/medical."
        )

    def _budget_flag(self, payload):
        """Budget 80%/100% alert — None if there is no budget."""
        try:
            spent = float(payload.get("spent_so_far"))
            budget = float(payload.get("monthly_budget"))
        except (TypeError, ValueError):
            return None
        if budget <= 0:
            return None
        pct = spent / budget * 100.0
        if pct >= 100:
            return f"🔴 STOP — budget 100% exceeded ({pct:.0f}%)."
        if pct >= 80:
            return f"🟡 Warning — budget 80% exceeded ({pct:.0f}%)."
        return f"OK — {pct:.0f}% of the budget used."

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making an expense DRAFT entry / monthly report. Writes no file, touches no network, spends nothing."""
        task = task or {}
        title = task.get("title") or "Expense tracking draft"
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
        amount = payload.get("amount") or "BOSS INPUT REQUIRED"
        currency = payload.get("currency") or "USD"
        vendor = payload.get("vendor") or "BOSS INPUT REQUIRED"
        description = payload.get("description") or "BOSS INPUT REQUIRED"
        category = payload.get("category") or "BOSS INPUT REQUIRED"
        date = payload.get("date") or "BOSS INPUT REQUIRED"
        confirmation = payload.get("confirmation_id") or "BOSS INPUT REQUIRED"
        context = payload.get("context") or "BOSS INPUT REQUIRED"
        budget_flag = self._budget_flag(payload)
        category_ok = category in CATEGORIES

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — entry built from payload only."

        lines = [
            "[MOCK DRAFT] Expense tracking — DRAFT ONLY",
            f"Department: {self.department} | Worker: {self.role}",
            "Spend approved by Boss only — this worker never approves spend.",
            f"Total spent (real, 2026-11-21): ${TOTAL_SPENT_USD:.2f} — ledger still empty.",
            "",
            "1. Ledger entry DRAFT (not yet put in the ledger file — only if Boss approves):",
            f"   Amount: {amount} {currency} | Vendor: {vendor}",
            f"   Description: {description}",
            f"   Category: {category}",
            f"   Date: {date} | Confirmation/receipt ID: {confirmation}",
            f"   Context (why it was needed): {context}",
        ]
        if not category_ok:
            lines += [
                "",
                "   ⚠️ Category is not right — nothing was written outside the fixed categories.",
                "   Valid categories: " + ", ".join(CATEGORIES.keys()) + ".",
            ]
        lines += [
            "",
            "2. Fixed categories:",
        ]
        for name, desc in CATEGORIES.items():
            lines.append(f"   - {name}: {desc}")
        lines += [
            "",
            "3. Budget status:",
        ]
        if budget_flag is not None:
            lines.append(f"   {budget_flag}")
        else:
            lines.append("   Boss has not set a monthly budget — BOSS INPUT REQUIRED.")
            lines.append("   At 80% a warning, at 100% a STOP flag — shown in red in the report.")
            lines.append("   The budget cannot be changed by the worker itself.")
        lines += [
            "",
            "4. Monthly report (DRAFT, one page):",
            "   Total spent: $0 (no spend happened) | Category split: none.",
            "   Biggest 3 expenses: none. Next month's forecast: cannot be invented.",
            "   Export: CSV/JSON can be given from store/expenses.json (if Boss wants).",
            "   Card number, password, API key must never be written in the ledger.",
            f"Booking link: {BOOKING_LINK} (New York Time) | Phone: {TALVENOR_PHONE}",
            f"Brain note: {brain_text}",
        ]
        notes = (
            "DRAFT ONLY — mock brain ($0). Expense entry + report DRAFT ONLY — "
            "No spend approval, no file written, no number/receipt "
            "invented. Gate: none (draft); spend needs only Boss's ok."
        )
        return {
            "status": "draft-ready",
            "output": "\n".join(lines),
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
