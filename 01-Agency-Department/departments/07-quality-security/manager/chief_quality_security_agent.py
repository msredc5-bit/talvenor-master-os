"""Chief Quality Security Agent — quality & security department manager (Phase 1).

ভূমিকা (role): 07-quality-security department-এর manager — quality/
security task এলে কোন specialist-এর কাজ, তা ঠিক করে specialist-কে
load করে চালানো (importlib), আর ফলাফল DRAFT হিসেবে ফেরত দেওয়া।
নিজে কোনো QA/security check চালায় না।
Gate: ok — delegation plan ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

Mapped existing staff (7): QAEngineer (receptionist_qa, no gate —
12-check QA checklist; dept 03 Testing & Debugging-এর সঙ্গেও shared)
+ 6 নতুন specialist (Phase 3): Call Scenario Testing, Workflow
Testing, Data Validation, Security Monitoring, Access Control,
Compliance Review — সবাই DRAFT only, gate None। Voice Quality Testing
— QAEngineer দিয়ে আংশিক (partial), dedicated worker নেই। Backup &
Recovery GAP — repo-তে কোনো backup system নেই।
Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
এই manager কখনো করে না: কোনো QA/security check নিজে চালায় না, কিছু
পাঠায় না, খরচ করে না, client-এর তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো
guarantee দেয় না, dental/medical বা patient-health ব্যবসা নেয় না।
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds.
# EXISTING: worker আছে — file = 01-Agency-Department-এর ভেতরের relative path।
# ROLE-ONLY: role definition আছে, worker নেই — file = planned skill path।
# GAP: worker-ও নেই, skill-ও নেই।
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
        "file": "GAP — no worker, no skill yet (no backup system in the repo)",
        "gate": "ok",
        "status": "GAP",
    },
    "compliance_review": {
        "specialist": "Compliance Review Agent",
        "file": "departments/07-quality-security/specialists/compliance_review_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}

# task_kind -> (specialist module file, relative to 01-Agency-Department/,
# class name). শুধু standalone .py specialist-দের জন্য — QAEngineer
# (engine/workers/...) এখানে নেই, তার জন্য plan-draft behavior-ই থাকে।
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
    """Quality/security task-এর specialist-কে load করে চালায়; QAEngineer-এর জন্য delegation plan DRAFT বানায়। নিজে check চালায় না।"""

    task_kind = "manage_quality_security"
    gate = "ok"
    department = "07-quality-security"
    role = "Chief Quality Security Agent"

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
        """Standalone specialist .py importlib দিয়ে load করা (Chief-এর loader-এর মতো)।"""
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
        """Specialist চালানো বা delegation plan DRAFT বানানো। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Quality & security delegation"
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

        task_kind = task.get("task_kind")
        entry = DEPARTMENT_TASKS.get(task_kind)

        # Overview — task_kind না থাকলে বা manager-এর নিজের kind হলে
        # (M1–M4 pattern): সব specialist-এর তালিকা সহ overview draft।
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
                "Specialists (7 EXISTING — QAEngineer shared + 6 Phase 3 specialists):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                item = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {item['specialist']} | {item['file']} | "
                    f"gate: {item['gate'] or 'none'} | {item['status']}"
                )
            lines.append(
                "Note: Backup & Recovery GAP — repo-তে কোনো backup system "
                "নেই। QAEngineer dept 03-এর সঙ্গেও shared; voice quality "
                "শুধু আংশিক cover করে। 6 নতুন specialist DRAFT only, gate None।"
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, "
                "কোনো check নিজে চালানো নয়। Chief wiring Phase 2 DONE — "
                "Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।"
            )
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # Standalone specialist থাকলে তাকে load করে চালানো (importlib,
        # Chief-এর loader-এর মতো) — specialist-এর ফলাফলই ফেরত দেওয়া।
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
                "No worker was executed. সঠিক task_kind Boss-কে দিতে হবে।\n"
                f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}"
            )
            notes = (
                "DRAFT ONLY — mock brain ($0). Unknown task_kind — delegation "
                "হয়নি, কোনো worker চালানো হয়নি। Chief wiring Phase 2 DONE — "
                "এই manager-কে এখন DEPARTMENT_ROUTING দিয়ে Agency Chief ডাকে।"
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
            f"Gate: {gate} — Boss-এর \"{gate}\" লাগবে এই কাজের output ব্যবহার করতে।"
            if gate else
            "Gate: None — draft নিজেই নিরাপদ, কোনো gate নেই।"
        )
        status_note = (
            "worker exists; this plan routes only, never executes."
            if entry["status"] == "EXISTING" else
            "no worker yet — this plan routes only; it never executes a worker."
            if entry["status"] == "ROLE-ONLY" else
            "no worker, no skill yet — nothing to route to; Boss-কে সিদ্ধান্ত দিতে হবে।"
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
            "Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, execution নয়। "
            "QAEngineer dept 03-এর সঙ্গেও shared। Backup & Recovery GAP — "
            "repo-তে কোনো backup system নেই। Gate: ok।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
