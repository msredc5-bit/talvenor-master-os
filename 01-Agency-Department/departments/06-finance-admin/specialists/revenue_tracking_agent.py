"""Revenue Tracking Agent — revenue tracking template draft (Dept 06, Phase 3).

Role: only make a DRAFT of the TEMPLATE for revenue tracking —
never invent revenue, never put in a client's name/money.
Gate: None — the draft itself is safe.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Paying clients are read live from 00-CEO-Core/config.json honest_status
at run time (Phase 2) — no hardcoded copy lives in this file. Revenue
has no source field anywhere in the repo, so the output says UNKNOWN
for revenue instead of claiming $0. The template has only column headers
+ space for empty rows; no filled row. LOCKED pricing internal only — no
price numbers are put in the template; never quote a price to a prospect.

This agent never: invents revenue, puts in a client/money,
issues an invoice, takes a payment, sends anything, spends anything,
quotes a price, gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# (Phase 2: the old hardcoded PAYING_CLIENTS = 0 / REVENUE_TOTAL = 0 are
# gone — paying clients are read live from config.json honest_status,
# see _paying_clients; revenue has no source field, so it is UNKNOWN.)

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class RevenueTrackingAgent:
    """Revenue tracking template DRAFT ONLY — never invents revenue."""

    task_kind = "revenue_tracking"
    gate = None
    department = "06-finance-admin"
    role = "Revenue Tracking Agent"

    def _paying_clients(self):
        """Paying clients, read live from config.json honest_status.

        Phase 2: no hardcoded copy in this file. When the config has no
        value, returns "UNKNOWN" — never a guessed number."""
        here = os.path.dirname(os.path.abspath(__file__))
        ceo_core = os.path.normpath(os.path.join(
            here, "..", "..", "..", "..", "00-CEO-Core"))
        if ceo_core not in sys.path:
            sys.path.insert(0, ceo_core)
        import honest_status
        return honest_status.paying_clients()

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
        """Making a revenue tracking template DRAFT. Writes no file, touches no network."""
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

        paying_clients = self._paying_clients()
        if paying_clients == "UNKNOWN":
            clients_line = (
                "Paying clients: UNKNOWN — config.json honest_status has no "
                "paying_clients value; no client count is claimed."
            )
        else:
            clients_line = (
                "Paying clients (read from config.json honest_status): "
                f"{paying_clients}."
            )
        revenue_line = (
            "Revenue (real): UNKNOWN — no revenue source field exists in "
            "config.json honest_status; no revenue figure is claimed."
        )

        output = (
            "[MOCK DRAFT] Revenue tracking template — DRAFT ONLY\n"
            f"Department: {self.department} | Worker: {self.role}\n"
            f"{clients_line}\n"
            f"{revenue_line}\n"
            "Template (columns only — no filled row):\n"
            "Client | Tier | Monthly | Build fee | Status\n"
            "--- Boss will fill the row, when a paying client comes ---\n"
            "LOCKED pricing internal only — no price numbers are put in the template; never quote a price to a prospect.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Revenue tracking template ONLY — "
            "No revenue/client/money was invented. Paying clients read from "
            "config.json honest_status; revenue UNKNOWN (no source). Gate: None."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
