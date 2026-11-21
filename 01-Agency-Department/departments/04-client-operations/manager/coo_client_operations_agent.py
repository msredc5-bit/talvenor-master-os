"""COO Client Operations Agent — manager of the Client Operations department (Phase 1).

Role: delegate to the Client Operations department's 9 existing specialists —
client intake, onboarding draft, delivery management, client
success, inbox triage, call monitoring, client reporting, retention,
renewal/upsell. For engine/section workers, it only makes a DRAFT of the delegation plan;
it loads the standalone specialists in the specialists/ dir (Phase 3)
and returns their DRAFT.
Gate: ok — Boss's "ok" is needed for the delegation plan; for intake/success-related
sending, a "send" gate is needed, which this manager does not do itself.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Paying clients 0 — there is still no live client; the intake/onboarding plan
It stays as a DRAFT.
Agency Chief wiring Phase 2 DONE — the Chief now calls this manager via DEPARTMENT_ROUTING.
This manager never: executes an engine/section worker, sends anything,
spends anything, deletes anything, invents client information/prices/statistics,
gives no guarantee, takes no dental/medical or patient-health business.
"""

import importlib.util
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
        "class": "CallMonitoringAgent",
        "file": "departments/04-client-operations/specialists/call_monitoring.py",
        "gate": None,
        "status": "EXISTING",
    },
    "client_reporting": {
        "specialist": "Client Reporting Agent",
        "class": "ClientReportingAgent",
        "file": "departments/04-client-operations/specialists/client_reporting.py",
        "gate": None,
        "status": "EXISTING",
    },
    "retention": {
        "specialist": "Retention Agent",
        "class": "RetentionAgent",
        "file": "departments/04-client-operations/specialists/retention.py",
        "gate": None,
        "status": "EXISTING",
    },
    "renewal_upsell": {
        "specialist": "Renewal & Upsell Agent",
        "class": "RenewalUpsellAgent",
        "file": "departments/04-client-operations/specialists/renewal_upsell.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class COOClientOperationsAgent:
    """Makes a DRAFT of the delegation plan for Client Operations specialists + loads and runs the Phase 3 specialists (DRAFT only)."""

    task_kind = "manage_client_operations"
    gate = "ok"
    department = "04-client-operations"
    role = "COO Client Operations Agent"

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
        """Build a delegation plan DRAFT + Phase 3 specialist load+run (DRAFT only). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Manage Client Operations"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # If there is a gated action, approval first — no draft without approval,
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
                "Specialists (9 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: Paying clients 0 — there is still no live client; intake and "
                "onboarding plan It stays as a DRAFT. Call monitoring, "
                "the reporting, retention, renewal/upsell specialists are now also "
                "EXISTING — their DRAFT comes through the manager."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, no "
                "not a worker execution. Agency Chief wiring Phase 2 DONE — the Chief now "
                "calls this manager via DEPARTMENT_ROUTING."
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
                f"Requested task_kind '{task_kind}' is not in this department.\n"
                "Known task kinds: " + ", ".join(known_kinds) + ".\n"
                "No worker executed; ask again with the correct task_kind."
            )
            notes = (
                "Unknown task — no delegation plan was made. This department's "
                "task kinds are listed above."
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # Phase 3: if a standalone .py exists in the specialists/ dir, load it with importlib
        # and run it — the result returned is the specialist's DRAFT itself.
        # For engine/section workers, the plan-draft behaviour below is unchanged.
        spec_file = entry.get("file") or ""
        if (entry.get("status") == "EXISTING"
                and spec_file.startswith(
                    "departments/04-client-operations/specialists/")
                and spec_file.endswith(".py")):
            here = os.path.dirname(os.path.abspath(__file__))
            spec_path = os.path.normpath(os.path.join(
                here, "..", "specialists", os.path.basename(spec_file)))
            spec = importlib.util.spec_from_file_location(
                f"dept04_specialist_{task_kind}", spec_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specialist_cls = getattr(mod, entry["class"])
            specialist = specialist_cls()
            return specialist.run(task, brain, gateway, approvals_path)

        payload = task.get("payload") or {}
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] Client Operations — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Client: {client}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']} will be given the task — the manager does not do the work itself.\n"
            "2. The specialist's output will be shown to Boss as a DRAFT.\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — nothing without Boss's exact word "
                "may not be sent/spent.\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — this role has no worker code; the skill doc "
                "says Boss/Elora will do the work by hand.\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan only; the worker "
            "was not executed, nothing was sent. Agency Chief wiring Phase 2 DONE — "
            "The Chief now calls this manager via DEPARTMENT_ROUTING."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
