"""Chief Innovation Agent — product innovation department manager (Phase 1).

Role: manager of the 08-product-innovation department — when an Agency
service innovation task arrives, decide which specialist owns it, then
run the specialist worker and return its DRAFT. It does no
research/prototype itself.
Gate: ok — using the delegation/manager output needs Boss's "ok".
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.
Phase 3 DONE (2026-11-19): all 6 specialists are EXISTING — the manager now
loads and runs the specialist with importlib from task_kind.

This department has mapped existing staff — 6 specialists, all EXISTING.
The Vet No-Show Recovery Kit ($49) is not this department's — it is
02-Digital-Product-Department's; this department is only for Agency service
innovation.
This manager never does this: it does no research/prototype itself, builds no prototype,
sends nothing, spends nothing, invents no client facts/prices/statistics,
gives no guarantee, takes no dental/medical or patient-health
business.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds — all EXISTING (Phase 3, 2026-11-19): each
# role has a skill .md + specialist worker .py; the manager loads and runs the specialist from
# task_kind. The specialists have gate none.
# file field: repo-relative worker path from 01-Agency-Department.
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
    """Loads the specialist for a product innovation task and returns its DRAFT."""

    task_kind = "manage_product_innovation"
    gate = "ok"
    department = "08-product-innovation"
    role = "Chief Innovation Agent"

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
        """Loading a specialist worker file with importlib — like the Chief's
        SECTION_ROUTING loader (spec_from_file_location)."""
        here = os.path.dirname(os.path.abspath(__file__))
        agency_dir = os.path.normpath(os.path.join(here, "..", "..", ".."))
        spec_path = os.path.join(agency_dir, entry["file"])
        spec = importlib.util.spec_from_file_location(
            f"dept08_{entry['class']}", spec_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, entry["class"])()

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Running a specialist worker and returning its DRAFT. If it does not load,
        a DRAFT of the delegation plan (fallback). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Product innovation delegation"
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

        # Overview — if there is no task_kind (or the manager's own kind):
        # an overview DRAFT listing all the department's specialists.
        # (Phase 2: this branch was missing — the other 7 managers have it;
        # without it a bare call returned unknown-task instead of the roster.)
        if not task_kind or task_kind == self.task_kind:
            if brain is not None:
                try:
                    brain_text = brain.complete(
                        "Product Innovation department overview for Talvenor. "
                        "List the department specialists, their files, gates, "
                        "and honest status. Do not invent any fact.")
                except TypeError:
                    brain_text = brain.complete(
                        "Product Innovation department overview for Talvenor.",
                        max_tokens=500)
            else:
                brain_text = ("No brain passed — overview built from "
                              "DEPARTMENT_TASKS only.")
            lines = [
                "[MOCK DRAFT] Product Innovation — department overview delegation plan (DRAFT ONLY)",
                "Manager: Chief Innovation Agent | task_kind: manage_product_innovation | gate: ok",
                "Specialists (6 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                item = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {item['specialist']} | {item['file']} | "
                    f"gate: {item['gate'] or 'none'} | {item['status']}"
                )
            lines.append(
                "Note: Agency service innovation only — the Vet No-Show "
                "Recovery Kit belongs to the Digital Product Department, "
                "not here. All 6 specialists DRAFT only, gate None."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, "
                "no worker execution. Chief wiring Phase 2 DONE — "
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

        # Known kind — load and run the specialist worker, return its DRAFT.
        # If it does not load, a DRAFT of the delegation plan (fallback).
        if entry.get("status") == "EXISTING" and entry["file"].endswith(".py"):
            try:
                specialist = self._load_specialist(entry)
                return specialist.run(task, brain, gateway, approvals_path)
            except Exception as e:  # noqa: BLE001 — fallback plan, not a crash
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
            f"Gate: {gate} — Boss's \"{gate}\" is needed to use this task's output."
            if gate else
            "Gate: None — the draft itself is safe, no gate."
        )
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY (fallback)\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — specialist worker did not load "
            f"({load_error}); this plan is only routing, not execution.\n"
            "Agency service innovation only — Vet No-Show Recovery Kit "
            "02-Digital-Product-Department's, not this department's.\n"
            "Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan fallback — "
            "specialist did not load, so no execution. All 6 specialists are "
            "EXISTING; the load error must be checked and fixed. "
            "Vet Kit is 02-Digital-Product-Department's. Gate: ok."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
