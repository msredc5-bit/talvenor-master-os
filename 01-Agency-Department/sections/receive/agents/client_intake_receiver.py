"""Client Intake Receiver — receiving a new lead (receive section, Phase 7).

Role: taking a new lead's information when it arrives, logging it in the returned draft,
and building an intake checklist DRAFT.
Gate: send — no intake-related reply/message can be sent without Boss's send word
; this agent itself sends nothing.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
This agent never does this: it sends nothing, calls nobody, invents no client's
information/price/statistics, gives no guarantee, no dental/medical
or patient-health business.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ClientIntakeReceiverAgent:
    """Builds a new lead's intake log + checklist DRAFT. Never sends."""

    task_kind = "client_intake"
    gate = "send"
    section = "receive"
    role = "Client Intake Receiver"

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
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        owner = payload.get("owner") or "BOSS INPUT REQUIRED"
        trade = payload.get("trade") or "BOSS INPUT REQUIRED"
        city = payload.get("city") or "BOSS INPUT REQUIRED"
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        source = payload.get("source") or "BOSS INPUT REQUIRED"
        contact = payload.get("contact") or "BOSS INPUT REQUIRED"
        return (
            "Client intake draft for a new Talvenor lead. "
            f"Business: {business}. Owner: {owner}. Trade: {trade}. "
            f"City: {city}. State: {state}. Source: {source}. "
            f"Contact: {contact}. "
            "Produce an intake log line and a short intake checklist. "
            "Do not invent any client fact; mark missing facts "
            "'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building an intake DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Client intake"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # If there is a gated action, approval first — not even a draft without approval,
        # record PENDING and stop.
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
        business = payload.get("business") or "BOSS INPUT REQUIRED"
        owner = payload.get("owner") or "BOSS INPUT REQUIRED"
        trade = payload.get("trade") or "BOSS INPUT REQUIRED"
        city = payload.get("city") or "BOSS INPUT REQUIRED"
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        source = payload.get("source") or "BOSS INPUT REQUIRED"
        contact = payload.get("contact") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — checklist built from payload only."

        output = (
            "[MOCK DRAFT] Client Intake — DRAFT ONLY\n"
            f"Lead: {business} | Owner: {owner} | Trade: {trade} | "
            f"City: {city}, {state} | Source: {source} | Contact: {contact}\n"
            "Intake checklist (DRAFT):\n"
            "1. Confirm business + owner name from a real source (never guess).\n"
            "2. Confirm trade is a Talvenor niche (plumbing, HVAC, roofing, "
            "garage door, septic, tree, foundation, restoration, pest, vet) — "
            "not dental/medical/patient-health.\n"
            "3. Note missed-call pain signal, if seen on website/reviews.\n"
            "4. Hand to ProspectResearcher for research before any outreach.\n"
            "5. No reply sent from intake — any reply needs Boss 'send'.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Intake log + checklist, no sending. "
            "Without any information, 'BOSS INPUT REQUIRED' — no invented information. "
            "Gate: send — sending anything intake-related needs Boss's 'send'."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
