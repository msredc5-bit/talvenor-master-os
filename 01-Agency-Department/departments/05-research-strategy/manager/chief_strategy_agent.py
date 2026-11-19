"""Chief Strategy Agent — research & strategy department manager (Phase 1).

ভূমিকা (role): 05-research-strategy department-এর manager — strategy-level
research task এলে কোন specialist-এর কাজ, তা ঠিক করে specialist-কে
load করে তার DRAFT ফেরত দেওয়া। নিজে কোনো research করে না।
Gate: ok — manager-এর output ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
Phase 3 DONE (2026-11-19) — ৭ specialist-ই EXISTING, manager এখন
importlib দিয়ে specialist load করে চালায়।

এই department-এ ৭ specialist EXISTING — competitor, industry, pricing,
niche, offer, market opportunity, business intelligence।
Prospect-level research করে ProspectResearcher (dept 01 Sales)।
এই manager কখনো করে না: কিছু পাঠায় না, খরচ করে না, client-এর
তথ্য/দাম/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না, dental/medical
বা patient-health ব্যবসা নেয় না।
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds — ৭টাই EXISTING (Phase 3, 2026-11-19):
# প্রতিটার worker + skill ফাইল disk-এ আছে; manager importlib দিয়ে
# specialist load করে চালায়। Gate: none — specialist draft নিজেই নিরাপদ।
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
    """Strategy research task specialist-এর কাছে delegate করে তার DRAFT ফেরত দেয়।"""

    task_kind = "manage_research_strategy"
    gate = "ok"
    department = "05-research-strategy"
    role = "Chief Strategy Agent"

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
        """Specialist worker importlib দিয়ে load করা — Chief-এর loader-এর মতো।"""
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
        """Specialist-কে delegate করে তার DRAFT ফেরত দেওয়া। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Research & strategy delegation"
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
        entry = DEPARTMENT_TASKS.get(task_kind)

        # Overview — task_kind না থাকলে (manager-এর নিজের kind) ৭ specialist-এর
        # তালিকা সহ overview draft (dept 01-এর pattern)।
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
                "Note: সব specialist DRAFT ONLY — mock brain ($0)। "
                "Pricing research INTERNAL ONLY; dental/medical সবসময় DQ; "
                "legal 4th client পর্যন্ত gated। Email PAUSED since 2026-11-14."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            return {
                "status": "draft-ready",
                "output": "\n".join(lines),
                "notes": (
                    "DRAFT ONLY — mock brain ($0). Overview, কোনো specialist "
                    "execute নয়। Chief wiring Phase 2 DONE — Agency Chief এখন "
                    "এই manager-কে DEPARTMENT_ROUTING দিয়ে ডাকে।"
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

        # EXISTING specialist — importlib দিয়ে load করে চালানো, তার result ফেরত।
        if entry["status"] == "EXISTING" and entry["file"].endswith(".py"):
            specialist = self._load_specialist(entry)
            return specialist.run(task, brain=brain, gateway=gateway,
                                  approvals_path=approvals_path)

        # Fallback — file না থাকলে পুরনো delegation plan draft (unchanged behavior)।
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
            f"Status: {entry['status']} — specialist file পাওয়া যায়নি, plan only।\n"
            "Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, execution নয় — "
            "specialist file পাওয়া যায়নি। "
            "Prospect-level research করে ProspectResearcher (dept 01 Sales)। "
            "Gate: ok।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
