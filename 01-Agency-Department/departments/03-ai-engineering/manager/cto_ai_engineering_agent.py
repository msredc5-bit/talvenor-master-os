"""CTO AI Engineering Agent — manager of the AI Engineering department (Phase 1).

Role: delegating to the AI Engineering department's specialists —
receptionist build (DRAFT plan only), QA checklist (shared, dept 07), and
7 specialist (solution, conversation, prompt, Vapi, CRM integration, calendar, n8n,
deployment) — when their task comes in, the manager loads and runs the specialist, not just
a plan. This manager makes a DRAFT of the delegation plan; it does not execute an engine/section old worker, deploys nothing.
Gate: ok — Boss's "ok" is needed for the delegation plan; deploy/send/spend/delete
This manager itself performs no gated action.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
LIVE production voice stack Vapi: Sophia, live receptionist, +1 (947)
223-0244 — Sophia is no demo agent. Retell DROPPED 2026-10-26;
RetellBuilder is DRAFT plan only, not production.
Agency Chief wiring Phase 2 DONE — the Chief now calls this manager via DEPARTMENT_ROUTING.
This manager never: executes an engine/section old worker, deploys anything,
changes anything in production, sends anything, spends anything, deletes anything,
invents client information/prices/statistics, gives any guarantee,
dental/medical or patient-health businesses.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

DEPARTMENT_TASKS = {
    "receptionist_build": {
        "specialist": "RetellBuilder",
        "file": "engine/workers/src/workers/delivery.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "receptionist_qa": {
        "specialist": "QAEngineer",
        "file": "engine/workers/src/workers/delivery.py",
        "gate": None,
        "status": "EXISTING",
    },
    "solution_architect": {
        "specialist": "AI Solution Architect",
        "file": "departments/03-ai-engineering/specialists/ai_solution_architect.py",
        "gate": None,
        "status": "EXISTING",
    },
    "conversation_design": {
        "specialist": "Conversation Designer",
        "file": "departments/03-ai-engineering/specialists/conversation_designer.py",
        "gate": None,
        "status": "EXISTING",
    },
    "prompt_engineering": {
        "specialist": "Prompt Engineering Agent",
        "file": "departments/03-ai-engineering/specialists/prompt_engineering_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "vapi_integration": {
        "specialist": "Vapi Integration Agent",
        "file": "departments/03-ai-engineering/specialists/vapi_integration_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "crm_integration": {
        "specialist": "CRM Integration Agent",
        "class": "CRMIntegrationAgent",
        "file": "departments/03-ai-engineering/specialists/crm_integration_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "calendar_integration": {
        "specialist": "Calendar Integration Agent",
        "file": "departments/03-ai-engineering/specialists/calendar_integration_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "n8n_automation": {
        "specialist": "n8n Automation Engineer",
        "file": "departments/03-ai-engineering/specialists/n8n_automation_engineer.py",
        "gate": None,
        "status": "EXISTING",
    },
    "deployment": {
        "specialist": "Deployment Agent",
        "file": "departments/03-ai-engineering/specialists/deployment_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}

# task_kind -> specialist class name (manager -> specialist importlib loading,
# like the Chief's DEPARTMENT_ROUTING loader).
SPECIALIST_CLASSES = {
    "solution_architect": "AISolutionArchitect",
    "conversation_design": "ConversationDesigner",
    "prompt_engineering": "PromptEngineeringAgent",
    "vapi_integration": "VapiIntegrationAgent",
    "crm_integration": "CRMIntegrationAgent",
    "calendar_integration": "CalendarIntegrationAgent",
    "n8n_automation": "N8nAutomationEngineer",
    "deployment": "DeploymentAgent",
}


class CTOAIEngineeringAgent:
    """Makes a DRAFT of the delegation plan for AI Engineering specialists + loads and runs the Phase 3 specialists (DRAFT only); does not deploy."""

    task_kind = "manage_ai_engineering"
    gate = "ok"
    department = "03-ai-engineering"
    role = "CTO AI Engineering Agent"

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
            "AI Engineering delegation plan draft for Talvenor. "
            f"Requested task kind: {task_kind}. Client: {client}. "
            "Name the specialist, their file, the gate needed, and the "
            "honest status. Live voice stack is Vapi/Sophia — Retell is "
            "DROPPED, RetellBuilder is a DRAFT plan only. Do not invent "
            "any client fact; mark missing facts 'BOSS INPUT REQUIRED'. "
            "No price, no guarantee, no dental/medical. Deployment needs "
            "Boss 'ok' plus manual steps; no worker deploys."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Build a delegation plan DRAFT + Phase 3 specialist load+run (DRAFT only). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Manage AI Engineering"
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
                "[MOCK DRAFT] AI Engineering — department overview delegation plan (DRAFT ONLY)",
                "Manager: CTO AI Engineering Agent | task_kind: manage_ai_engineering | gate: ok",
                "Specialists:",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: Live voice stack Vapi/Sophia (+1 (947) 223-0244) — "
                "Retell DROPPED 2026-10-26, RetellBuilder DRAFT plan only. "
                "QAEngineer shared with dept 07 (QA checklist, partial). "
                "CRM not live — CRM integration DRAFT plan only (worker EXISTS, CRM PLANNED). n8n workflows READY, not LIVE."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, no "
                "no worker execution, no deploy. Agency Chief wiring Phase 2 DONE — "
                "The Chief now calls this manager via DEPARTMENT_ROUTING."
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
                "[MOCK DRAFT] AI Engineering — unknown task (DRAFT ONLY)\n"
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

        # If the specialist has a standalone .py (departments/03-ai-engineering/
        # specialists/), load and run it with importlib — like the Chief's loader.
        # Receptionist build/QA (engine/workers) and GAP/ROLE-ONLY
        # kinds go to the delegation plan branch below.
        if (entry["status"] == "EXISTING"
                and entry["file"].startswith(
                    "departments/03-ai-engineering/specialists/")):
            here = os.path.dirname(os.path.abspath(__file__))
            specialist_path = os.path.normpath(os.path.join(
                here, "..", entry["file"].split(
                    "departments/03-ai-engineering/", 1)[1]))
            spec = importlib.util.spec_from_file_location(
                f"dept03_specialist_{task_kind}", specialist_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specialist_cls = getattr(mod, SPECIALIST_CLASSES[task_kind])
            specialist = specialist_cls()
            gw = gateway if gateway is not None else self._gateway(approvals_path)
            return specialist.run(task, brain, gw, approvals_path)

        payload = task.get("payload") or {}
        client = payload.get("client") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] AI Engineering — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Client: {client}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']} will be given the task — the manager does not do the work itself.\n"
            "2. The specialist's output will be shown to Boss as a DRAFT.\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — without Boss's exact word, nothing in production "
                "may be changed/sent/spent.\n"
            )
        if task_kind == "receptionist_build":
            output += (
                "4. RetellBuilder DRAFT plan ONLY — live stack Vapi/Sophia; "
                "Retell DROPPED 2026-10-26, Retell is not in production.\n"
            )
        if task_kind == "receptionist_qa":
            output += (
                "4. QAEngineer shared with dept 07 — QA checklist, partial; "
                "Boss's ok is needed for the verdict.\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — this role has no worker code; the skill doc "
                "says Boss/Elora will do the work by hand.\n"
            )
        if entry["status"] == "GAP":
            output += (
                "4. GAP — (worker + skill EXISTING on 2026-11-21) — CRM Integration "
                "Agent: departments/03-ai-engineering/specialists/crm_integration_agent.py; "
                "integration DRAFT plan only until the CRM (n8n Data Tables) goes live.\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan only; the worker "
            "nothing was executed, nothing was deployed. Agency Chief wiring Phase 2 DONE — "
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
