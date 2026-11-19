"""Data Validation Agent — data validation draft (Dept 07, Phase 3).

ভূমিকা (role): lead list/file-এর data validation-এর DRAFT লেখা —
কোন field যাচাই করতে হবে, কী missing/invented হতে পারে।
Gate: None — draft নিজেই নিরাপদ, কোনো gate নেই।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।

কঠোর নিয়ম: field না পেলে NOT_FOUND — কখনো email, ফোন, ঠিকানা
অনুমান করে বানানো যাবে না। এই agent কোনো file পড়ে না, কোনো
validation ফলাফল বানায় না। DB = JSON store files; CRM PLANNED,
live নয়।

এই agent কখনো করে না: validation ফলাফল বানায় না, field অনুমান করে
পূরণ করে না, কোনো file পড়ে/লেখে/বদলায় না, কিছু পাঠায় না, খরচ
করে না, client-এর তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো guarantee
দেয় না, dental/medical নয়, legal advice দেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

_STANDARD_FIELDS = (
    ("business_name", "required"),
    ("website", "required"),
    ("phone", "required"),
    ("email", "required — never guessed; missing = NOT_FOUND"),
    ("state", "required"),
    ("service_area", "required"),
    ("need_signal", "optional — only if seen on website/call"),
)


class DataValidationAgent:
    """Data validation checklist DRAFT ONLY — কখনো ফলাফল বানানো নয়।"""

    task_kind = "data_validation"
    gate = None
    department = "07-quality-security"
    role = "Data Validation Agent"

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
        list_name = payload.get("list_name") or "standard prospect fields"
        return (
            "Data validation draft for a Talvenor lead list/file. "
            f"List: {list_name}. "
            "List the fields to check, which are required, and what to "
            "do when a field is missing (NOT_FOUND) or looks invented "
            "(tell Boss, never fix it silently). Never invent a field "
            "value or a validation result. Dental/medical is always DQ. "
            "Do not invent client facts or prices. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Data validation DRAFT বানানো। কোনো file পড়ে না, লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Data validation draft"
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
        list_name = payload.get("list_name")
        list_line = (
            f"List/file: {list_name}"
            if list_name else
            "List/file: BOSS INPUT REQUIRED — standard prospect fields drafted."
        )
        given_fields = payload.get("fields")
        if isinstance(given_fields, list) and given_fields:
            field_lines = "\n".join(
                f"- {str(f)}: check present + real; missing = NOT_FOUND"
                for f in given_fields
            )
        else:
            field_lines = "\n".join(
                f"- {name}: {rule}; missing = NOT_FOUND"
                for name, rule in _STANDARD_FIELDS
            )

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — validation draft built from payload only."

        output = (
            "[MOCK DRAFT] Data validation — DRAFT ONLY\n"
            f"{list_line}\n"
            "Rules: field না পেলে NOT_FOUND — কখনো email/ফোন/ঠিকানা "
            "অনুমান করে বানানো নয়। Invented মনে হলে Boss-কে জানানো, "
            "নিজে ঠিক করা নয়। Dental/medical থাকলে DQ।\n"
            "Fields to check:\n"
            f"{field_lines}\n"
            "Validation result: NOT VERIFIED — this draft checked no file "
            "and no result is claimed. Real validation is done by hand "
            "by Boss/Elora.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Checklist ONLY, কখনো validation "
            "ফলাফল বানানো নয়, কোনো file পড়া নয়। Gate: None।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
