"""COO Client Operations Agent — Client Operations department-এর manager (Phase 1).

ভূমিকা (role): Client Operations department-এর ৫ জন existing specialist-কে
delegate করা — client intake, onboarding draft, delivery manage, client
success, inbox triage। এই manager শুধু delegation plan-এর DRAFT বানায়;
কোনো worker execute করে না।
Gate: ok — delegation plan-এ Boss-এর "ok" লাগে; intake/success-সংক্রান্ত
কিছু পাঠাতে "send" gate লাগে, যা এই manager নিজে করে না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Paying clients 0 — এখনো কোনো live client নেই; intake/onboarding plan
DRAFT হিসেবেই থাকে।
Agency Chief wiring Phase 2 DONE — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।
এই manager কখনো করে না: কোনো worker execute করে না, কিছু পাঠায় না,
খরচ করে না, মুছে না, client-এর তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো
guarantee দেয় না, dental/medical বা patient-health ব্যবসা নেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

DEPARTMENT_TASKS = {
    "client_intake": {
        "specialist": "ClientIntakeReceiver",
        "file": "sections/receive/agents/client_intake_receiver.py",
        "gate": "send",
        "status": "EXISTING",
    },
    "onboarding_draft": {
        "specialist": "OnboardingAgent",
        "file": "engine/workers/src/workers/delivery.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "delivery_manage": {
        "specialist": "ServiceDeliveryManager",
        "file": "sections/delivery/agents/service_delivery_manager.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "client_success": {
        "specialist": "ClientSuccessAgent",
        "file": "sections/delivery/agents/client_success_agent.py",
        "gate": "send",
        "status": "EXISTING",
    },
    "inbox_triage": {
        "specialist": "InboxTriager",
        "file": "engine/workers/src/workers/admin.py",
        "gate": None,
        "status": "EXISTING",
    },
    "call_monitoring": {
        "specialist": "Call Monitoring Agent",
        "file": "ROLE-ONLY — skill: departments/04-client-operations/skills/coo-client-operations-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
    "client_reporting": {
        "specialist": "Client Reporting Agent",
        "file": "ROLE-ONLY — skill: departments/04-client-operations/skills/coo-client-operations-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
    "retention": {
        "specialist": "Retention Agent",
        "file": "ROLE-ONLY — skill: departments/04-client-operations/skills/coo-client-operations-agent.md",
        "gate": None,
        "status": "ROLE-ONLY",
    },
    "renewal_upsell": {
        "specialist": "Renewal & Upsell Agent",
        "file": "ROLE-ONLY — skill: departments/04-client-operations/skills/coo-client-operations-agent.md",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
}


class COOClientOperationsAgent:
    """Client Operations specialist-দের delegation plan DRAFT বানায়। কখনো execute করে না।"""

    task_kind = "manage_client_operations"
    gate = "ok"
    department = "04-client-operations"
    role = "COO Client Operations Agent"

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
        task_kind = task.get("task_kind") or self.task_kind
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        return (
            "Client Operations delegation plan draft for Talvenor. "
            f"Requested task kind: {task_kind}. Client: {client}. "
            "Name the specialist, their file, the gate needed, and the "
            "honest status. Paying clients are 0 — no live client yet, "
            "so intake/onboarding plans stay DRAFT. Do not invent any "
            "client fact; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No price, no guarantee, no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Delegation plan DRAFT বানানো। কোনো worker execute করে না, file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Manage Client Operations"
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

        task_kind = task.get("task_kind") or self.task_kind
        known_kinds = [self.task_kind] + sorted(DEPARTMENT_TASKS.keys())

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — delegation plan built from DEPARTMENT_TASKS only."

        if task_kind == self.task_kind:
            lines = [
                "[MOCK DRAFT] Client Operations — department overview delegation plan (DRAFT ONLY)",
                "Manager: COO Client Operations Agent | task_kind: manage_client_operations | gate: ok",
                "Specialists (5 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: Paying clients 0 — এখনো কোনো live client নেই; intake ও "
                "onboarding plan DRAFT হিসেবেই থাকে। Call monitoring, reporting, "
                "retention, renewal/upsell ROLE-ONLY।"
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, কোনো "
                "worker execute নয়। Agency Chief wiring Phase 2 DONE — Chief এখন "
                "এই manager-কে DEPARTMENT_ROUTING দিয়ে call করে।"
            )
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        entry = DEPARTMENT_TASKS.get(task_kind)
        if entry is None:
            output = (
                "[MOCK DRAFT] Client Operations — unknown task (DRAFT ONLY)\n"
                f"Requested task_kind '{task_kind}' এই department-এ নেই।\n"
                "Known task kinds: " + ", ".join(known_kinds) + ".\n"
                "কোনো worker execute হয়নি; সঠিক task_kind দিয়ে আবার চাইতে হবে।"
            )
            notes = (
                "Unknown task — delegation plan বানানো হয়নি। এই department-এর "
                "task kind-গুলো উপরে তালিকায় আছে।"
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        payload = task.get("payload") or {}
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] Client Operations — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Client: {client}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']}-কে task দেওয়া হবে — manager নিজে কাজটি করে না।\n"
            "2. Specialist-এর output DRAFT হিসেবে Boss-কে দেখানো হবে।\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — Boss-এর exact word ছাড়া কিছু "
                "পাঠানো/খরচ করা যাবে না।\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — এই role-এর কোনো worker code নেই; skill doc "
                "অনুযায়ী Boss/Elora হাতে কাজটি করবেন।\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan মাত্র; worker "
            "execute হয়নি, কিছু পাঠানো হয়নি। Agency Chief wiring Phase 2 DONE — "
            "Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
