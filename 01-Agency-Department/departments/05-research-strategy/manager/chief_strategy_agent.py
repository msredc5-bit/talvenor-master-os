"""Chief Strategy Agent — research & strategy department manager (Phase 1).

Role: manager of the 05-research-strategy department — strategy-level
when a research task comes in, decide which specialist's job it is and
load the specialist and return their DRAFT. It does no research itself.
Gate: ok — Boss's "ok" is needed to use the manager's output.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.
Phase 3 DONE (2026-11-19) — all 7 specialists are EXISTING, the manager now
loads and runs the specialist with importlib.

This department has 7 EXISTING specialists — competitor, industry, pricing,
niche, offer, market opportunity, business intelligence.
ProspectResearcher (dept 01 Sales) does prospect-level research.
This manager never: sends anything, spends anything, invents client
information/prices/statistics, gives no guarantee, dental/medical
or patient-health businesses.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds — all 7 EXISTING (Phase 3, 2026-11-19):
# Each one's worker + skill file is on disk; the manager loads
# and runs the specialist with importlib. Gate: none — a specialist draft is safe on its own.
DEPARTMENT_TASKS = {
    "competitor_research": {
        "specialist": "Competitor Research Agent",
        "class": "CompetitorResearchAgent",
        "file": "departments/05-research-strategy/specialists/competitor_research_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "industry_research": {
        "specialist": "Industry Research Agent",
        "class": "IndustryResearchAgent",
        "file": "departments/05-research-strategy/specialists/industry_research_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "pricing_research": {
        "specialist": "Pricing Research Agent",
        "class": "PricingResearchAgent",
        "file": "departments/05-research-strategy/specialists/pricing_research_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "niche_selection": {
        "specialist": "Niche Selection Agent",
        "class": "NicheSelectionAgent",
        "file": "departments/05-research-strategy/specialists/niche_selection_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "offer_development": {
        "specialist": "Offer Development Agent",
        "class": "OfferDevelopmentAgent",
        "file": "departments/05-research-strategy/specialists/offer_development_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "market_opportunity": {
        "specialist": "Market Opportunity Agent",
        "class": "MarketOpportunityAgent",
        "file": "departments/05-research-strategy/specialists/market_opportunity_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "business_intelligence": {
        "specialist": "Business Intelligence Agent",
        "class": "BusinessIntelligenceAgent",
        "file": "departments/05-research-strategy/specialists/business_intelligence_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class ChiefStrategyAgent:
    """Delegates a strategy research task to a specialist and returns their DRAFT."""

    task_kind = "manage_research_strategy"
    gate = "ok"
    department = "05-research-strategy"
    role = "Chief Strategy Agent"

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

    def _prompt(self, task, entry=None):
        payload = task.get("payload") or {}
        topic = payload.get("topic") or "BOSS INPUT REQUIRED"
        if entry is None:
            return (
                "Research & strategy delegation request for Talvenor. "
                f"Topic: {topic}. "
                "The task_kind is unknown in this department. "
                "List the department's known task kinds and ask Boss "
                "for the correct one. Do not invent any fact."
            )
        return (
            "Delegation plan draft for a Talvenor research & strategy task. "
            f"Task kind: {task.get('task_kind')}. Topic: {topic}. "
            f"Specialist: {entry['specialist']}. "
            f"File: {entry['file']}. "
            f"Gate: {entry['gate']}. Status: {entry['status']}. "
            "The manager loads the specialist worker (importlib) and returns "
            "its draft. Do not invent any client fact, price, or statistic. "
            "No dental/medical."
        )

    def _load_specialist(self, entry):
        """Specialist worker loaded with importlib — like the Chief's loader."""
        here = os.path.dirname(os.path.abspath(__file__))
        dept_dir = os.path.normpath(os.path.join(here, ".."))
        rel = entry["file"].split("departments/05-research-strategy/", 1)[-1]
        path = os.path.join(dept_dir, rel)
        spec = importlib.util.spec_from_file_location(
            f"dept05_{entry['class']}", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return getattr(mod, entry["class"])()

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Delegates to a specialist and returns their DRAFT. Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Research & strategy delegation"
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
        entry = DEPARTMENT_TASKS.get(task_kind)

        # Overview — if there is no task_kind (the manager's own kind), an overview draft with the 7 specialists'
        # list (dept 01's pattern).
        if task_kind == self.task_kind:
            if brain is not None:
                try:
                    brain_text = brain.complete(self._prompt(task))
                except TypeError:
                    brain_text = brain.complete(self._prompt(task), max_tokens=500)
            else:
                brain_text = "No brain passed — overview built from DEPARTMENT_TASKS only."
            lines = [
                "[MOCK DRAFT] Research & Strategy — department overview (DRAFT ONLY)",
                "Manager: Chief Strategy Agent | task_kind: manage_research_strategy | gate: ok",
                "Specialists (7 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                e = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {e['specialist']} | {e['file']} | "
                    f"gate: {e['gate'] or 'none'} | {e['status']}"
                )
            lines.append(
                "Note: all specialists are DRAFT ONLY — mock brain ($0). "
                "Pricing research INTERNAL ONLY; dental/medical always DQ; "
                "legal gated until the 4th client. Email PAUSED since 2026-11-14."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": (
                    "DRAFT ONLY — mock brain ($0). Overview, no specialist "
                    "execution. Chief wiring Phase 2 DONE — the Agency Chief now "
                    "calls this manager with DEPARTMENT_ROUTING."
                ),
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

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
                "did not happen, no worker was run. Chief wiring Phase 2 DONE — "
                "the Agency Chief now calls this manager via DEPARTMENT_ROUTING."
            )
            return {
                "status": "unknown-task",
                "output": output,
                "notes": notes,
                "draft_only": True,
                "mock_brain": True,
                "gate": self.gate,
            }

        # EXISTING specialist — load and run with importlib, return its result.
        if entry["status"] == "EXISTING" and entry["file"].endswith(".py"):
            specialist = self._load_specialist(entry)
            return specialist.run(task, brain=brain, gateway=gateway,
                                  approvals_path=approvals_path)

        # Fallback — if the file is missing, the old delegation plan draft (unchanged behavior).
        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task, entry))
            except TypeError:
                brain_text = brain.complete(self._prompt(task, entry), max_tokens=500)
        else:
            brain_text = "No brain passed — delegation plan built from task only."

        gate = entry["gate"]
        gate_line = (
            f"Gate: {gate} — Boss's \"{gate}\" is needed to use this work's output."
            if gate else
            "Gate: None — the draft itself is safe, there is no gate."
        )
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File/skill: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — specialist file not found, plan only.\n"
            "Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, not execution — "
            "specialist file not found. "
            "Prospect-level research is done by ProspectResearcher (dept 01 Sales). "
            "Gate: ok."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
