"""Google Maps Prospect Finder — discovery plan draft (Sales & Growth, Phase 3).

Role: making a DRAFT of the plan for finding plumber/HVAC/etc. prospects from Maps/Places data
— it never does a live search, searches for no business.
Gate: none — the plan DRAFT has no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

This agent never: does a live search/API call, invents a business name, phone,
email, address, or rating, sends nothing, quotes no prices,
Gives no guarantee, no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# To record — these fields are the prospect list's template.
RECORD_FIELDS = (
    "business name",
    "address",
    "phone",
    "website",
    "Google rating / reviews",
    "service area",
)


class GoogleMapsProspectFinder:
    """Maps/Places discovery plan DRAFT ONLY — no live search, nothing invented."""

    task_kind = "maps_prospect_find"
    gate = None
    department = "01-sales-growth"
    role = "Google Maps Prospect Finder"

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
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        city = payload.get("city") or "BOSS INPUT REQUIRED"
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        return (
            "Google Maps / Places prospect discovery plan draft for Talvenor. "
            f"Business type: {business_type}. City: {city}. State: {state}. "
            "List the search-query pattern, the fields to record, and the "
            "next step (verification). Do not invent any business, phone, "
            "email, address, or rating; mark missing facts "
            "'BOSS INPUT REQUIRED'. No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a discovery plan DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Maps prospect discovery plan"
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
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        city = payload.get("city") or "BOSS INPUT REQUIRED"
        state = payload.get("state") or "BOSS INPUT REQUIRED"
        area = payload.get("area") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — discovery plan built from payload only."

        fields_line = "; ".join(RECORD_FIELDS)
        output = (
            "[MOCK DRAFT] Google Maps Prospect Finder — discovery plan (DRAFT ONLY)\n"
            f"Business type: {business_type} | City: {city} | State: {state} | Area: {area}\n"
            "Search-query pattern (Maps/Places, must be searched by hand):\n"
            f"\"{business_type} in {city}, {state}\" — then the surrounding areas the same way.\n"
            f"Fields to record: {fields_line}.\n"
            "If any field is not found, NOT_FOUND must be written — it must never be invented.\n"
            "If a dental/medical or patient-health business is found, DQ — never a target.\n"
            "Next step: Business Verification Agent (business_verify) — the found business's\n"
            "website/phone/service area verification; then Lead Scoring Agent (lead_score).\n"
            "NOTE: This worker does no live search — only a plan DRAFT. The real search\n"
            "is done by Boss/Elora by hand (with ProspectResearcher + Apify/Places).\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Discovery plan ONLY, no live search, "
            "no business/phone/email was invented. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
