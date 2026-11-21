"""Product Improvement Agent — product improvement draft (Dept 08, Phase 3).

Role: writing a DRAFT of ideas to make the live receptionist service (Sophia, Vapi) better —
it never invents client feedback, changes no
service.
Gate: none — the draft itself is safe, no gate.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Honest status: paying client 0 — no claim of client feedback.
This agent never does this: it invents no client feedback/words, changes no live service,
never claims it changed, invents no numbers/statistics,
sends nothing, spends nothing, no dental/medical.
Live stack Vapi/Sophia — Sophia live receptionist, +1 (947) 223-0244.
Retell DROPPED 2026-10-26 — never production.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ProductImprovementAgent:
    """Product improvement DRAFT ONLY — only an idea, no change."""

    task_kind = "product_improvement"
    gate = None
    department = "08-product-innovation"
    role = "Product Improvement Agent"

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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        return (
            "Product improvement draft for the Talvenor receptionist "
            f"service (Sophia, Vapi live). Improvement idea: {topic}. "
            "Which problem it fixes, what would change in the live "
            "service, and what still needs verification. DRAFT idea "
            "only — nothing changed in the live service. Paying "
            "clients are 0, so never invent client feedback; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No guarantee."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a product improvement DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Product improvement draft"
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
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        problem = payload.get("problem") or "Missed calls mean lost jobs — receptionist must answer 24/7."

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — improvement built from payload only."

        output = (
            "[MOCK DRAFT] Product improvement — DRAFT ONLY\n"
            f"Improvement idea: {topic}\n"
            f"Problem it fixes: {problem}\n"
            "Status: DRAFT IDEA ONLY — nothing in the service has been changed.\n"
            "What would change (idea only): live Vapi/Sophia receptionist "
            f"({TALVENOR_PHONE}) — change happens only on Boss's word, "
            "never by this draft.\n"
            "What is NOT known (no invented feedback): paying clients are 0, "
            "so no client feedback exists — BOSS INPUT REQUIRED.\n"
            "Next verification step ($0): Boss decides whether the idea is "
            "worth testing; no live change before his word.\n"
            f"Booking link (real): {BOOKING_LINK}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Improvement draft ONLY, only an idea — "
            "nothing in the service has been changed. No invented client feedback/numbers "
            "none. Gate: none."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
