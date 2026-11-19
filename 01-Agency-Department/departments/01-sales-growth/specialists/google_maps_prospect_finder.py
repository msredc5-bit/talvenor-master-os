"""Google Maps Prospect Finder — discovery plan draft (Sales & Growth, Phase 3).

ভূমিকা (role): Maps/Places data থেকে plumber/HVAC/etc. prospect খোঁজার
plan-এর DRAFT বানানো — কখনো live search করে না, কোনো ব্যবসা খোঁজে না।
Gate: none — plan DRAFT-এ কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই agent কখনো করে না: live search/API call করে না, ব্যবসার নাম, ফোন,
ইমেইল, ঠিকানা, রেটিং বানায় না, কিছু পাঠায় না, দাম quote করে না,
কোনো guarantee দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Record করতে হবে — এই field-গুলোই prospect তালিকার ছক।
RECORD_FIELDS = (
    "business name",
    "address",
    "phone",
    "website",
    "Google rating / reviews",
    "service area",
)


class GoogleMapsProspectFinder:
    """Maps/Places discovery plan DRAFT ONLY — live search নয়, কিছু বানায় না।"""

    task_kind = "maps_prospect_find"
    gate = None
    department = "01-sales-growth"
    role = "Google Maps Prospect Finder"

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
        """Discovery plan DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
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
            "Search-query pattern (Maps/Places, হাতে খুঁজতে হবে):\n"
            f"\"{business_type} in {city}, {state}\" — তারপর আশেপাশের এলাকা একইভাবে।\n"
            f"Record করার field: {fields_line}.\n"
            "কোনো field না পাওয়া গেলে NOT_FOUND লিখতে হবে — কখনো বানানো যাবে না।\n"
            "Dental/medical বা patient-health ব্যবসা পেলে DQ — কখনো target নয়।\n"
            "পরের ধাপ: Business Verification Agent (business_verify) — পাওয়া ব্যবসার\n"
            "website/phone/service area যাচাই; তারপর Lead Scoring Agent (lead_score)।\n"
            "NOTE: এই worker কোনো live search করে না — plan DRAFT মাত্র। আসল খোঁজা\n"
            "Boss/Elora হাতে করেন (ProspectResearcher + Apify/Places দিয়ে)।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Discovery plan ONLY, live search নয়, "
            "কোনো ব্যবসা/ফোন/ইমেইল বানানো হয়নি। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
