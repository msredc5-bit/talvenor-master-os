"""Billing Invoice Agent — invoice DRAFT (ops section, Phase 7).

Role: building an invoice DRAFT for a paying client —
only from LOCKED pricing (2026-11-12).
Gate: ok — using the invoice needs Boss's ok.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

LOCKED pricing (2026-11-12, lock Kore) — no price outside it:
  Starter: $547/mo + $597 build
  Growth:  $1,109/mo + $1,297 build
  Scale:   $1,672/mo + $1,997 build

Rules:
- An invoice is only for a paying client, on Boss's word. Paying client
  0 (2026-11-16) — without the client confirmed, BOSS INPUT REQUIRED,
  the invoice cannot be issued.
- A prospect can never be quoted any price — the invoice is not
  for a prospect.
- Payment can never be collected, no payment link/charge.
This agent never does this: it invents no price, tells no price to a prospect, takes no payment,
invents no client information, gives no guarantee.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

# LOCKED pricing (2026-11-12) — tier: (monthly, build fee)
LOCKED_PRICING = {
    "starter": (547, 597),
    "growth": (1109, 1297),
    "scale": (1672, 1997),
}

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class BillingInvoiceAgent:
    """Builds an invoice DRAFT from LOCKED pricing. Takes no payment."""

    task_kind = "billing_invoice"
    gate = "ok"
    section = "ops"
    role = "Billing Invoice Agent"

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
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        tier = payload.get("tier") or "BOSS INPUT REQUIRED"
        return (
            "Invoice draft for a Talvenor paying client. "
            f"Client: {client}. Tier: {tier}. "
            "Use LOCKED pricing only: Starter $547/mo + $597 build; "
            "Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build. "
            "Invoice only for a paying client on Boss's word. "
            "Never quote any price to a prospect. Never collect payment. "
            "Do not invent client facts; mark missing facts "
            "'BOSS INPUT REQUIRED'."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building an invoice DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Invoice draft"
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
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        tier_raw = str(payload.get("tier") or "").strip().lower()
        confirmed = payload.get("paying_client_confirmed") is True

        if tier_raw in LOCKED_PRICING:
            monthly, build = LOCKED_PRICING[tier_raw]
            tier_line = (f"Tier: {tier_raw.title()} — "
                         f"${monthly:,}/mo + ${build:,} build (LOCKED 2026-11-12)")
        elif tier_raw:
            tier_line = (f"Tier: {tier_raw} — NOT a locked tier. "
                         "Locked tiers only: Starter, Growth, Scale. "
                         "BOSS INPUT REQUIRED.")
            monthly, build = None, None
        else:
            tier_line = "Tier: BOSS INPUT REQUIRED (Starter / Growth / Scale)"
            monthly, build = None, None

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — invoice built from payload only."

        if not confirmed:
            status_line = (
                "Status: NOT ISSUED — no paying client confirmed on Boss's word. "
                "Paying clients = 0 (2026-11-16). This is a TEMPLATE draft only; "
                "Issuing the invoice needs Boss's confirm + 'ok'."
            )
        else:
            status_line = (
                "Status: DRAFT ready for Boss review — paying client confirmed "
                "on Boss's word. Issuing needs Boss's 'ok'."
            )

        output = (
            "[MOCK DRAFT] Invoice — DRAFT ONLY\n"
            f"Client: {client}\n"
            f"{tier_line}\n"
            f"{status_line}\n"
            "Invoice (DRAFT): Talvenor AI Receptionist — MAINUDDIN LLC, "
            "Pennsylvania, USA. Amounts from LOCKED pricing only; "
            "no other price exists in this draft. "
            "Never quote this to a prospect. Never collect payment from here.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Invoice DRAFT, not issued, not payment. "
            "No price except LOCKED pricing (2026-11-12). Gate: ok. "
            "Without the paying client confirmed, TEMPLATE only."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
