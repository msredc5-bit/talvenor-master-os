"""CTO AI Engineering Agent — AI Engineering department-এর manager (Phase 1).

ভূমিকা (role): AI Engineering department-এর specialist-দের delegate করা —
receptionist build (DRAFT plan only), QA checklist (shared, dept 07), আর
৭ specialist (solution, conversation, prompt, Vapi, calendar, n8n,
deployment) — এদের task এলে manager specialist-কে load করে চালায়, শুধু
plan দেয় না। এই manager delegation plan-এর DRAFT বানায়; engine/section-এর পুরনো worker execute করে না, কিছু deploy করে না।
Gate: ok — delegation plan-এ Boss-এর "ok" লাগে; deploy/send/spend/delete
কোনো gated action এই manager নিজে করে না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
LIVE production voice stack Vapi: Sophia, live receptionist, +1 (947)
223-0244 — Sophia কোনো demo agent নয়। Retell DROPPED 2026-10-26;
RetellBuilder শুধু DRAFT plan, production নয়।
Agency Chief wiring Phase 2 DONE — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।
এই manager কখনো করে না: engine/section-এর পুরনো worker execute করে না, কিছু deploy করে না,
production-এ কিছু বদলায় না, কিছু পাঠায় না, খরচ করে না, মুছে না,
client-এর তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না,
dental/medical বা patient-health ব্যবসা নেয় না।
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
        "file": "GAP — no worker file; CRM (n8n Data Tables) planned, not live",
        "gate": "ok",
        "status": "GAP",
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
# Chief-এর DEPARTMENT_ROUTING loader-এর মতো)।
SPECIALIST_CLASSES = {
    "solution_architect": "AISolutionArchitect",
    "conversation_design": "ConversationDesigner",
    "prompt_engineering": "PromptEngineeringAgent",
    "vapi_integration": "VapiIntegrationAgent",
    "calendar_integration": "CalendarIntegrationAgent",
    "n8n_automation": "N8nAutomationEngineer",
    "deployment": "DeploymentAgent",
}


class CTOAIEngineeringAgent:
    """AI Engineering specialist-দের delegation plan DRAFT বানায় + Phase 3 specialist-দের load করে চালায় (DRAFT only); deploy করে না।"""

    task_kind = "manage_ai_engineering"
    gate = "ok"
    department = "03-ai-engineering"
    role = "CTO AI Engineering Agent"

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
        """Delegation plan DRAFT বানানো + Phase 3 specialist load+run (DRAFT only)। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Manage AI Engineering"
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
                "CRM not live — CRM integration GAP. n8n workflows READY, not LIVE."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, কোনো "
                "worker execute নয়, কোনো deploy নয়। Agency Chief wiring Phase 2 DONE — "
                "Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।"
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

        # Specialist-এর standalone .py থাকলে (departments/03-ai-engineering/
        # specialists/) importlib দিয়ে load করে চালানো — Chief-এর loader-এর
        # মতো। Receptionist build/QA (engine/workers) আর GAP/ROLE-ONLY
        # kind-গুলো নিচের delegation plan branch-এ যায়।
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
            f"1. {entry['specialist']}-কে task দেওয়া হবে — manager নিজে কাজটি করে না।\n"
            "2. Specialist-এর output DRAFT হিসেবে Boss-কে দেখানো হবে।\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — Boss-এর exact word ছাড়া production-এ "
                "কিছু বদলানো/পাঠানো/খরচ করা যাবে না।\n"
            )
        if task_kind == "receptionist_build":
            output += (
                "4. RetellBuilder DRAFT plan ONLY — live stack Vapi/Sophia; "
                "Retell DROPPED 2026-10-26, production-এ Retell নয়।\n"
            )
        if task_kind == "receptionist_qa":
            output += (
                "4. QAEngineer shared with dept 07 — QA checklist, partial; "
                "verdict-এর জন্য Boss-এর ok লাগে।\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — এই role-এর কোনো worker code নেই; skill doc "
                "অনুযায়ী Boss/Elora হাতে কাজটি করবেন।\n"
            )
        if entry["status"] == "GAP":
            output += (
                "4. GAP — এই role-এর কোনো worker/skill নেই; CRM live না হওয়া "
                "পর্যন্ত integration সম্ভব নয়।\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan মাত্র; worker "
            "execute হয়নি, কিছু deploy হয়নি। Agency Chief wiring Phase 2 DONE — "
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
