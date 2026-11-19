"""Conversation Designer — call-flow / conversation design draft (Dept 03, Phase 3).

ভূমিকা (role): Sophia receptionist-এর ৮ ধাপের call flow-এর DRAFT বানানো —
কখনো কোনো call করে না, live assistant বদলায় না।
Gate: none — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

এই worker কখনো করে না: live assistant-এর flow বদলায় না, call করে না,
কিছু পাঠায় না, খরচ করে না, মোছে না, দাম quote করে না, client-এর
তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না, dental/medical নয়,
AI disclosure ছাড়া flow লেখে না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ConversationDesigner:
    """Call-flow design DRAFT ONLY — কখনো live assistant বদলায় না।"""

    task_kind = "conversation_design"
    gate = None
    department = "03-ai-engineering"
    role = "Conversation Designer"

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
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        services = payload.get("services") or "BOSS INPUT REQUIRED"
        return (
            "Call-flow design draft for a Talvenor client receptionist. "
            f"Client: {client}. Business type: {business_type}. "
            f"Services: {services}. "
            "Eight steps: Greet, Life-safety check, Intent, Qualify, Action, "
            "Confirm, Log, Close. Include honest AI disclosure and the "
            "booking link. Do not invent client facts; mark missing facts "
            "'BOSS INPUT REQUIRED'. No guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Call-flow DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Conversation design draft"
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
        business_type = payload.get("business_type") or "BOSS INPUT REQUIRED"
        services = payload.get("services") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — call flow built from payload only."

        dq_line = ""
        if business_type.strip().lower() in ("dental", "medical", "dentist", "clinic"):
            dq_line = "\nDQ: dental/medical বা patient-health ব্যবসা — design নয়, target নয়।"

        output = (
            "[MOCK DRAFT] Conversation Designer — call flow (DRAFT ONLY)\n"
            f"Client: {client} | Business type: {business_type} | Services: {services}"
            f"{dq_line}\n"
            "Call flow (8 steps):\n"
            "1. Greet — honest AI disclosure: caller-কে জানানো হয় সে Talvenor-এর "
            "AI receptionist Sophia-র সঙ্গে কথা বলছে।\n"
            "2. Life-safety check — জরুরি (আগুন, গ্যাস লিক, বন্যা, আঘাত) হলে "
            "caller-কে সরাসরি emergency number-এ যেতে বলা হয়; Sophia নিজে "
            "emergency handle করে না।\n"
            "3. Intent — caller কী চায় (booking, quote, emergency, অন্য কিছু)।\n"
            "4. Qualify — নাম, phone, service, এলাকা, সময় — যা জানা দরকার।\n"
            "5. Action — booking link দেওয়া: "
            f"{BOOKING_LINK} (15 min, New York Time)।\n"
            "6. Confirm — booking-এর বিবরণ caller-কে আবার পড়ে শোনানো।\n"
            "7. Log — call-এর তথ্য লগ করা (n8n workflow, READY not LIVE)।\n"
            "8. Close — ধন্যবাদ, পরের ধাপ জানানো।\n"
            "Status: DRAFT design only — live assistant-এ কিছু বদলানো হয়নি।\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Call-flow design DRAFT ONLY, "
            "কখনো live assistant বদলানো নয়। Gate: none।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
