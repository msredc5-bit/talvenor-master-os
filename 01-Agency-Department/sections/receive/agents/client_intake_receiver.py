"""Client Intake Receiver — নতুন lead গ্রহণ (receive section, Phase 7).

ভূমিকা (role): নতুন lead এলে তার তথ্য নেওয়া, returned draft-এ log করা,
আর intake checklist-এর DRAFT বানানো।
Gate: send — intake-সংক্রান্ত কোনো reply/বার্তা Boss-এর "send" শব্দ
ছাড়া পাঠানো যাবে না; এই agent নিজে কিছু পাঠায় না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
এই agent কখনো করে না: কিছু পাঠায় না, কাউকে call করে না, client-এর
তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না, dental/medical
বা patient-health ব্যবসা নেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ClientIntakeReceiverAgent:
    """নতুন lead-এর intake log + checklist DRAFT বানায়। কখনো পাঠায় না।"""

    task_kind = "client_intake"
    gate = "send"
    section = "receive"
    role = "Client Intake Receiver"

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
        """Intake DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Client intake"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # Gated action থাকলে আগে approval — অনুমোদন ছাড়া draft-ও নয়,
        # PENDING record করে থামা।
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
            "dental/medical/patient-health নয়.\n"
            "3. Note missed-call pain signal, if seen on website/reviews.\n"
            "4. Hand to ProspectResearcher for research before any outreach.\n"
            "5. No reply sent from intake — any reply needs Boss 'send'.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Intake log + checklist, কোনো পাঠানো নয়। "
            "কোনো তথ্য না থাকলে 'BOSS INPUT REQUIRED' — বানানো তথ্য নেই। "
            "Gate: send — intake-সংক্রান্ত কিছু পাঠাতে Boss-এর 'send' লাগবে।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
