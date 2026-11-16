"""Client Success Agent — client check-in (delivery section, Phase 7).

ভূমিকা (role): paying client-এর check-in draft + renewal-reminder
draft বানানো।
Gate: send — check-in/renewal বার্তা পাঠাতে Boss-এর "send" লাগে;
এই agent নিজে কিছু পাঠায় না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
সত্য অবস্থা: paying client 0 (2026-11-16) — তাই client-সংক্রান্ত
কোনো তথ্য না থাকলে "BOSS INPUT REQUIRED" লিখতে হবে, কোনো client-এর
নাম/তথ্য/ফলাফল বানানো যাবে না।
এই agent কখনো করে না: কিছু পাঠায় না, client data বানায় না, দাম
quote করে না, কোনো guarantee/testimonial দেয় না, dental/medical নয়।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")


class ClientSuccessAgent:
    """Check-in + renewal-reminder DRAFT বানায়। কোনো client data বানায় না।"""

    task_kind = "client_success"
    gate = "send"
    section = "delivery"
    role = "Client Success Agent"

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
        kind = payload.get("kind") or "check-in"
        return (
            "Client success draft for a Talvenor paying client. "
            f"Client: {client}. Kind: {kind} (check-in or renewal reminder). "
            "Short, plain US English, one CTA (15-min call). "
            "Do not invent any client fact; mark missing facts "
            "'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no testimonial, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Check-in / renewal DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Client check-in"
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
        kind = payload.get("kind") or "check-in"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — draft built from payload only."

        output = (
            "[MOCK DRAFT] Client Success — DRAFT ONLY\n"
            f"Client: {client} | Kind: {kind}\n"
            "Honest note: paying clients = 0 (2026-11-16). If no real client "
            "is named in the payload, this draft is a TEMPLATE only — "
            "do not send it to anyone.\n"
            "Check-in draft (short, plain US English, 1 CTA):\n"
            "\"Hi — quick check-in. Is the receptionist catching every call "
            "the way you wanted? Any tweak you need, tell us — a 15-min call "
            f"works: {BOOKING_LINK}\"\n"
            "Renewal-reminder draft (short, plain US English, 1 CTA):\n"
            "\"Hi — your receptionist plan renews soon. Want to keep the same "
            "setup, or change anything first? A 15-min call sorts it: "
            f"{BOOKING_LINK}\"\n"
            f"Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Check-in + renewal-reminder drafts, "
            "কোনো পাঠানো নয়। Paying client 0 — client তথ্য না থাকলে "
            "'BOSS INPUT REQUIRED'। Gate: send।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
