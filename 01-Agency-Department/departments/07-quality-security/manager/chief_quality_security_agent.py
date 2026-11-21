"""Chief Quality Security Agent — quality & security department manager (Phase 1).

Role: manager of the 07-quality-security department — quality/
when a security task arrives, decide which specialist owns it, then
load and run the specialist (importlib), and return the result as a DRAFT.
It never runs any QA/security check itself.
Gate: ok — using the delegation plan needs Boss's "ok".
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.

Mapped existing staff (8): QAEngineer (receptionist_qa, no gate —
12-check QA checklist; also shared with dept 03 Testing & Debugging)
+ 7 specialist: Call Scenario Testing, Workflow Testing, Data
Validation, Security Monitoring, Access Control, Compliance Review
(Phase 3) + Backup & Recovery (2026-11-21) — all DRAFT only, gate
None. Voice Quality Testing — partly covered by QAEngineer (partial),
no dedicated worker. Backup & Recovery EXISTING — DRAFT plan only,
restore test not done.
Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.
This manager never does this: it never runs any QA/security check itself, sends
nothing, spends nothing, invents no client facts/prices/statistics, gives no
guarantee, takes no dental/medical or patient-health business.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds.
# EXISTING: worker exists — file = relative path inside 01-Agency-Department.
# ROLE-ONLY: role definition exists, no worker — file = planned skill path.
# GAP: neither worker nor skill.
DEPARTMENT_TASKS = {
    "receptionist_qa": {
        "specialist": "QAEngineer",
        "file": "engine/workers/src/workers/delivery.py",
        "gate": None,
        "status": "EXISTING",
        "note": "Shared with dept 03 Testing & Debugging.",
    },
    "voice_quality_testing": {
        "specialist": "QAEngineer (partial)",
        "file": "engine/workers/src/workers/delivery.py",
        "gate": None,
        "status": "EXISTING",
        "note": "Partial — QAEngineer 12-check checklist covers voice quality only in part; no dedicated voice-quality worker.",
    },
    "call_scenario_testing": {
        "specialist": "Call Scenario Testing Agent",
        "file": "departments/07-quality-security/specialists/call_scenario_testing_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "workflow_testing": {
        "specialist": "Workflow Testing Agent",
        "file": "departments/07-quality-security/specialists/workflow_testing_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "data_validation": {
        "specialist": "Data Validation Agent",
        "file": "departments/07-quality-security/specialists/data_validation_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "security_monitoring": {
        "specialist": "Security Monitoring Agent",
        "file": "departments/07-quality-security/specialists/security_monitoring_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "access_control": {
        "specialist": "Access Control Agent",
        "file": "departments/07-quality-security/specialists/access_control_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "backup_recovery": {
        "specialist": "Backup & Recovery Agent",
        "class": "BackupRecoveryAgent",
        "file": "departments/07-quality-security/specialists/backup_recovery_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "compliance_review": {
        "specialist": "Compliance Review Agent",
        "file": "departments/07-quality-security/specialists/compliance_review_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}

# task_kind -> (specialist module file, relative to 01-Agency-Department/,
# class name). Only for standalone .py specialists — QAEngineer
# (engine/workers/...) is not here; for it, the plan-draft behavior stays.
SPECIALIST_MODULES = {
    "call_scenario_testing": (
        "departments/07-quality-security/specialists/call_scenario_testing_agent.py",
        "CallScenarioTestingAgent",
    ),
    "workflow_testing": (
        "departments/07-quality-security/specialists/workflow_testing_agent.py",
        "WorkflowTestingAgent",
    ),
    "data_validation": (
        "departments/07-quality-security/specialists/data_validation_agent.py",
        "DataValidationAgent",
    ),
    "security_monitoring": (
        "departments/07-quality-security/specialists/security_monitoring_agent.py",
        "SecurityMonitoringAgent",
    ),
    "access_control": (
        "departments/07-quality-security/specialists/access_control_agent.py",
        "AccessControlAgent",
    ),
    "compliance_review": (
        "departments/07-quality-security/specialists/compliance_review_agent.py",
        "ComplianceReviewAgent",
    ),
}


class ChiefQualitySecurityAgent:
    """Loads and runs the specialist for a quality/security task; builds a delegation plan DRAFT for QAEngineer. Never runs a check itself."""

    task_kind = "manage_quality_security"
    gate = "ok"
    department = "07-quality-security"
    role = "Chief Quality Security Agent"

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

    def _prompt(self, task, entry=None):
        payload = task.get("payload") or {}
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        if entry is None:
            return (
                "Quality & security delegation request for Talvenor. "
                f"Topic: {topic}. "
                "The task_kind is unknown in this department. "
                "List the department's known task kinds and ask Boss "
                "for the correct one. Do not invent any fact."
            )
        return (
            "Delegation plan draft for a Talvenor quality & security task. "
            f"Task kind: {task.get('task_kind')}. Topic: {topic}. "
            f"Specialist: {entry['specialist']}. "
            f"File/skill: {entry['file']}. "
            f"Gate: {entry['gate']}. Status: {entry['status']}. "
            "Produce a short delegation plan: specialist, their file/skill, "
            "gate needed, honest status. This plan routes only, it never "
            "executes a worker and never runs a QA or security check itself. "
            "Do not invent any client fact, price, or statistic. "
            "No dental/medical."
        )

    def _load_specialist(self, task_kind):
        """Loading a standalone specialist .py with importlib (like the Chief's loader)."""
        module_file, class_name = SPECIALIST_MODULES[task_kind]
        here = os.path.dirname(os.path.abspath(__file__))
        agency_dir = os.path.normpath(os.path.join(here, "..", "..", ".."))
        specialist_path = os.path.join(agency_dir, module_file)
        spec = importlib.util.spec_from_file_location(
            f"dept07_specialist_{task_kind}", specialist_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, class_name)()

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Running a specialist or building a delegation plan DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Quality & security delegation"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

        # If a gated action is present, approval first — not even a draft without approval,
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

        task_kind = task.get("task_kind")
        entry = DEPARTMENT_TASKS.get(task_kind)

        # Overview — if task_kind is absent or is the manager's own kind
        # (M1–M4 pattern): overview draft with a list of all specialists.
        if not task_kind or task_kind == self.task_kind:
            if brain is not None:
                try:
                    brain_text = brain.complete(
                        "Quality & Security department overview for Talvenor. "
                        "List the department specialists, their files, gates, "
                        "and honest status. Do not invent any fact.")
                except TypeError:
                    brain_text = brain.complete(
                        "Quality & Security department overview for Talvenor.",
                        max_tokens=500)
            else:
                brain_text = "No brain passed — overview built from DEPARTMENT_TASKS only."
            lines = [
                "[MOCK DRAFT] Quality & Security — department overview delegation plan (DRAFT ONLY)",
                "Manager: Chief Quality Security Agent | task_kind: manage_quality_security | gate: ok",
                "Specialists (8 EXISTING — QAEngineer shared + 7 specialists):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                item = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {item['specialist']} | {item['file']} | "
                    f"gate: {item['gate'] or 'none'} | {item['status']}"
                )
            lines.append(
                "Note: Backup & Recovery EXISTING — DRAFT plan only, restore test not done. "
                "QAEngineer is also shared with dept 03; voice quality "
                "covers only part of it. 7 specialists DRAFT only, gate None."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, "
                "No check is run by itself. Chief wiring Phase 2 DONE — "
                "Agency Chief now calls this manager through DEPARTMENT_ROUTING."
            )
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # If a standalone specialist exists, load and run it (importlib,
        # like the Chief's loader) — return the specialist's result.
        if task_kind in SPECIALIST_MODULES:
            specialist = self._load_specialist(task_kind)
            return specialist.run(task, brain, gateway, approvals_path)

        if entry is None:
            kinds = ", ".join(sorted(DEPARTMENT_TASKS))
            output = (
                "[MOCK DRAFT] Unknown task — DRAFT ONLY\n"
                f"Department: {self.department} | Manager: {self.role}\n"
                f"Unknown task_kind: {task_kind or 'BOSS INPUT REQUIRED'}\n"
                f"Known task kinds in this department: {kinds}\n"
                "No worker was executed. The correct task_kind must be given to Boss.\n"
                f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}"
            )
            notes = (
                "DRAFT ONLY — mock brain ($0). Unknown task_kind — delegation "
                "not done, no worker was run. Chief wiring Phase 2 DONE — "
                "Agency Chief now calls this manager through DEPARTMENT_ROUTING."
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task, entry))
            except TypeError:
                brain_text = brain.complete(self._prompt(task, entry), max_tokens=500)
        else:
            brain_text = "No brain passed — delegation plan built from task only."

        gate = entry["gate"]
        gate_line = (
            f"Gate: {gate} — Boss's \"{gate}\" is needed to use this task's output."
            if gate else
            "Gate: None — the draft itself is safe, no gate."
        )
        status_note = (
            "worker exists; this plan routes only, never executes."
            if entry["status"] == "EXISTING" else
            "no worker yet — this plan routes only; it never executes a worker."
            if entry["status"] == "ROLE-ONLY" else
            "worker + skill now exist (2026-11-21) — worker path in File/skill "
            "above; this plan routes only, never executes."
        )
        note_line = f"Note: {entry['note']}\n" if entry.get("note") else ""
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File/skill: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — {status_note}\n"
            f"{note_line}"
            "Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, not execution. "
            "QAEngineer is also shared with dept 03. Backup & Recovery EXISTING — "
            "DRAFT plan only, restore test not done. Gate: ok."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
