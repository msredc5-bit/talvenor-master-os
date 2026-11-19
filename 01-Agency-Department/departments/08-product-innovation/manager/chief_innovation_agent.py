"""Chief Innovation Agent — product innovation department manager (Phase 1).

ভূমিকা (role): 08-product-innovation department-এর manager — Agency
service innovation task এলে কোন specialist-এর কাজ, তা ঠিক করে
DELEGATION PLAN-এর DRAFT বানানো। নিজে কোনো research/prototype করে না,
কোনো worker চালায় না।
Gate: ok — delegation plan ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

এই department-এ mapped existing staff নেই — GAP department।
Vet No-Show Recovery Kit ($49) এই department-এর নয় — সেটা
02-Digital-Product-Department-এর; এই department শুধু Agency service
innovation-এর জন্য।
এই manager কখনো করে না: worker execute করে না, prototype বানায় না,
কিছু পাঠায় না, খরচ করে না, client-এর তথ্য/দাম/পরিসংখ্যান বানায় না,
কোনো guarantee দেয় না, dental/medical বা patient-health ব্যবসা
নেয় না।
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds — সব ROLE-ONLY: role definition আছে, worker নেই।
# file field: "ROLE-ONLY — skill: <planned path>" (skill .md registry-তে
# এখনো বানানো হয়নি — এই file-এর scope-এর বাইরে)।
DEPARTMENT_TASKS = {
    "new_ai_product_research": {
        "specialist": "New AI Product Research Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/new-ai-product-research-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "new_feature_research": {
        "specialist": "New Feature Research Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/new-feature-research-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "automation_rd": {
        "specialist": "Automation R&D Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/automation-rd-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "technology_evaluation": {
        "specialist": "Technology Evaluation Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/technology-evaluation-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "product_improvement": {
        "specialist": "Product Improvement Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/product-improvement-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "prototype_builder": {
        "specialist": "Prototype Builder Agent",
        "file": "ROLE-ONLY — skill: departments/08-product-innovation/skills/prototype-builder-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
}


class ChiefInnovationAgent:
    """Product innovation task-এর delegation plan DRAFT বানায়। Worker চালায় না।"""

    task_kind = "manage_product_innovation"
    gate = "ok"
    department = "08-product-innovation"
    role = "Chief Innovation Agent"

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
                "Product innovation delegation request for Talvenor. "
                f"Topic: {topic}. "
                "The task_kind is unknown in this department. "
                "List the department's known task kinds and ask Boss "
                "for the correct one. Do not invent any fact. "
                "This department is Agency service innovation only — "
                "the Vet No-Show Recovery Kit belongs to the "
                "Digital Product Department, not here."
            )
        return (
            "Delegation plan draft for a Talvenor product innovation task. "
            f"Task kind: {task.get('task_kind')}. Topic: {topic}. "
            f"Specialist: {entry['specialist']}. "
            f"File/skill: {entry['file']}. "
            f"Gate: {entry['gate']}. Status: {entry['status']}. "
            "Produce a short delegation plan: specialist, their file/skill, "
            "gate needed, honest status. This department has no worker yet — "
            "the plan routes only, it never executes a worker and never "
            "builds a prototype. Agency service innovation only — the Vet "
            "No-Show Recovery Kit belongs to the Digital Product "
            "Department, not here. Do not invent any client fact, price, "
            "or statistic. No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Delegation plan DRAFT বানানো। কোনো worker চালায় না, file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Product innovation delegation"
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
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File/skill: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — role definition only, no worker yet. "
            "This plan routes only; it never executes a worker.\n"
            "Agency service innovation only — Vet No-Show Recovery Kit "
            "02-Digital-Product-Department-এর, এখানকার নয়।\n"
            "Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, execution নয়। "
            "এই department GAP — innovation-এর কোনো worker নেই। "
            "Vet Kit 02-Digital-Product-Department-এর। Gate: ok।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
