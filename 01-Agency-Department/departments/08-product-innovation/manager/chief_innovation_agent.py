"""Chief Innovation Agent — product innovation department manager (Phase 1).

ভূমিকা (role): 08-product-innovation department-এর manager — Agency
service innovation task এলে কোন specialist-এর কাজ, তা ঠিক করে
specialist worker-কে চালিয়ে তার DRAFT ফেরত দেওয়া। নিজে কোনো
research/prototype করে না।
Gate: ok — delegation/manager output ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
Phase 3 DONE (2026-11-19): ৬ specialist-ই EXISTING — manager এখন
task_kind দেখে specialist-কে importlib দিয়ে load করে চালায়।

এই department-এ mapped existing staff আছে — ৬ specialist, সব EXISTING।
Vet No-Show Recovery Kit ($49) এই department-এর নয় — সেটা
02-Digital-Product-Department-এর; এই department শুধু Agency service
innovation-এর জন্য।
এই manager কখনো করে না: নিজে research/prototype করে না, prototype
বানায় না, কিছু পাঠায় না, খরচ করে না, client-এর তথ্য/দাম/পরিসংখ্যান
বানায় না, কোনো guarantee দেয় না, dental/medical বা patient-health
ব্যবসা নেয় না।
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds — সব EXISTING (Phase 3, 2026-11-19): প্রতিটা
# role-এর skill .md + specialist worker .py আছে; manager task_kind
# দেখে specialist-কে load করে চালায়। Specialist-দের gate none।
# file field: 01-Agency-Department থেকে repo-relative worker path।
DEPARTMENT_TASKS = {
    "new_ai_product_research": {
        "specialist": "New AI Product Research Agent",
        "class": "NewAIProductResearchAgent",
        "file": "departments/08-product-innovation/specialists/new_ai_product_research.py",
        "gate": None,
        "status": "EXISTING",
    },
    "new_feature_research": {
        "specialist": "New Feature Research Agent",
        "class": "NewFeatureResearchAgent",
        "file": "departments/08-product-innovation/specialists/new_feature_research.py",
        "gate": None,
        "status": "EXISTING",
    },
    "automation_rd": {
        "specialist": "Automation R&D Agent",
        "class": "AutomationRDAgent",
        "file": "departments/08-product-innovation/specialists/automation_rd.py",
        "gate": None,
        "status": "EXISTING",
    },
    "technology_evaluation": {
        "specialist": "Technology Evaluation Agent",
        "class": "TechnologyEvaluationAgent",
        "file": "departments/08-product-innovation/specialists/technology_evaluation.py",
        "gate": None,
        "status": "EXISTING",
    },
    "product_improvement": {
        "specialist": "Product Improvement Agent",
        "class": "ProductImprovementAgent",
        "file": "departments/08-product-innovation/specialists/product_improvement.py",
        "gate": None,
        "status": "EXISTING",
    },
    "prototype_builder": {
        "specialist": "Prototype Builder Agent",
        "class": "PrototypeBuilderAgent",
        "file": "departments/08-product-innovation/specialists/prototype_builder.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class ChiefInnovationAgent:
    """Product innovation task-এর specialist-কে load করে তার DRAFT ফেরত দেয়।"""

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
            f"File: {entry['file']}. "
            f"Gate: {entry['gate']}. Status: {entry['status']}. "
            "The specialist worker could not be loaded in this run, so "
            "this is a routing-only fallback plan — it never executes a "
            "worker and never builds a prototype. Agency service "
            "innovation only — the Vet No-Show Recovery Kit belongs to "
            "the Digital Product Department, not here. Do not invent "
            "any client fact, price, or statistic. No dental/medical."
        )

    def _load_specialist(self, entry):
        """Specialist worker file importlib দিয়ে load করা — Chief-এর
        SECTION_ROUTING loader-এর মতো (spec_from_file_location)।"""
        here = os.path.dirname(os.path.abspath(__file__))
        agency_dir = os.path.normpath(os.path.join(here, "..", "..", ".."))
        spec_path = os.path.join(agency_dir, entry["file"])
        spec = importlib.util.spec_from_file_location(
            f"dept08_{entry['class']}", spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, entry["class"])()

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Specialist worker চালিয়ে তার DRAFT ফেরত দেওয়া। Load না হলে
        delegation plan-এর DRAFT (fallback)। কোনো file লেখে না, network ছোঁয় না।"""
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
            roster = "\n".join(
                f"- {kind}: {DEPARTMENT_TASKS[kind]['specialist']} "
                f"(EXISTING, {DEPARTMENT_TASKS[kind]['file']})"
                for kind in sorted(DEPARTMENT_TASKS)
            )
            output = (
                "[MOCK DRAFT] Unknown task — DRAFT ONLY\n"
                f"Department: {self.department} | Manager: {self.role}\n"
                f"Unknown task_kind: {task_kind or 'BOSS INPUT REQUIRED'}\n"
                f"Known task kinds in this department: {kinds}\n"
                "Department specialists (all EXISTING):\n"
                f"{roster}\n"
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

        # Known kind — specialist worker load করে চালানো, তার DRAFT ফেরত।
        # Load না হলে delegation plan-এর DRAFT (fallback)।
        if entry.get("status") == "EXISTING" and entry["file"].endswith(".py"):
            try:
                specialist = self._load_specialist(entry)
                return specialist.run(task, brain, gateway, approvals_path)
            except Exception as e:  # noqa: BLE001 — fallback plan, crash নয়
                load_error = f"{type(e).__name__}: {e}"
            else:
                load_error = None
        else:
            load_error = "specialist file is not an EXISTING .py worker"
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
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY (fallback)\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — specialist worker load হয়নি "
            f"({load_error}); এই plan শুধু routing, execution নয়।\n"
            "Agency service innovation only — Vet No-Show Recovery Kit "
            "02-Digital-Product-Department-এর, এখানকার নয়।\n"
            "Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan fallback — "
            "specialist load হয়নি, তাই execution নয়। ৬ specialist-ই "
            "EXISTING; load error দেখে ঠিক করতে হবে। "
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
