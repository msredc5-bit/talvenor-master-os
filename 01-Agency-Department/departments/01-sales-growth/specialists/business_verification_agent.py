"""Business Verification Agent — verification checklist draft (Sales & Growth, Phase 3).

Role: making a DRAFT verification checklist for a prospect's website/phone/service area
— based on SOP 11-signal scoring. It opens no website itself,
does not call.
Gate: none — the checklist DRAFT has no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never: does a live check, invents verification results,
sends anything, quotes prices, gives any guarantee,
no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# SOP 11-signal — the verification template.
SIGNALS = (
    "website exists and opens",
    "phone number exists",
    "the phone is answered",
    "service area is clear",
    "service area is in the target state",
    "business name matches the address",
    "Google listing exists",
    "reviews exist",
    "services list exists",
    "contact/booking path exists",
    "not dental/medical",
)


class BusinessVerificationAgent:
    """Verification checklist DRAFT ONLY — no live check, no invented results."""

    task_kind = "business_verify"
    gate = None
    department = "01-sales-growth"
    role = "Business Verification Agent"

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
        website = payload.get("website") or "BOSS INPUT REQUIRED"
        phone = payload.get("phone") or "BOSS INPUT REQUIRED"
        return (
            "Business verification checklist draft for Talvenor (SOP 11-signal). "
            f"Business: {business}. Website: {website}. Phone: {phone}. "
            "List all 11 signals with PASS / FAIL / NOT_VERIFIED based ONLY on "
            "given facts; mark missing facts 'BOSS INPUT REQUIRED'. Never invent "
            "a verification result. Dental/medical means DQ."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a verification checklist DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Business verification checklist"
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
        website = payload.get("website") or "BOSS INPUT REQUIRED"
        phone = payload.get("phone") or "BOSS INPUT REQUIRED"
        service_area = payload.get("service_area") or "BOSS INPUT REQUIRED"
        # If the payload gives a signal result, use it; otherwise NOT_VERIFIED.
        given = payload.get("signals") or {}
        if not isinstance(given, dict):
            given = {}

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — verification checklist built from payload only."

        lines = [
            "[MOCK DRAFT] Business Verification Agent — verification checklist (DRAFT ONLY)",
            f"Business: {business} | Website: {website} | Phone: {phone} | Service area: {service_area}",
            "SOP 11-signal checklist (results only from the given information; otherwise NOT_VERIFIED):",
        ]
        for i, signal in enumerate(SIGNALS, start=1):
            result = given.get(signal) or given.get(str(i)) or "NOT_VERIFIED"
            if result not in ("PASS", "FAIL", "NOT_VERIFIED"):
                result = "NOT_VERIFIED"
            lines.append(f"{i}. {signal}: {result}")
        lines.append(
            "If it is a dental/medical or patient-health business, DQ — never a target."
        )
        lines.append(
            "Next step: verified lead → Lead Scoring Agent (lead_score); "
            "if fail/DQ, the lead is dropped."
        )
        lines.append(
            "NOTE: This worker does no live check — only a checklist DRAFT. "
            "The real verification is done by Boss/Elora by hand."
        )
        lines.append(
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}"
        )
        lines.append(f"Brain note: {brain_text}")
        notes = (
            "DRAFT ONLY — mock brain ($0). Verification checklist ONLY, live check "
            "not, no verification result was invented. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": "\n".join(lines),
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
