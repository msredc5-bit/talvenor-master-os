"""Chief Growth Agent — manager of the Sales & Growth department (Phase 1).

Role: delegate to the 13 existing specialists of the Sales & Growth department —
prospect research, outreach draft, reply triage, negotiation
prep, objection sim, sales close, follow-up draft, schedule help, maps
prospect find, business verify, lead score, CRM manage, sales intelligence. This manager
makes a DRAFT of the delegation plan + loads and runs the Phase 3 specialists with importlib (DRAFT only); does not execute the engine/section's old workers.
Gate: ok — the delegation plan needs Boss's "ok"; send/publish/spend/delete
This manager itself performs no gated action.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Agency Chief wiring Phase 2 DONE — the Chief now calls this manager via DEPARTMENT_ROUTING.
This manager never: executes the engine/section's old workers, sends anything,
publishes anything, spends anything, deletes anything, invents client facts/prices/statistics,
gives any guarantee, takes dental/medical or patient-health
businesses.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

DEPARTMENT_TASKS = {
    "prospect_research": {
        "specialist": "ProspectResearcher",
        "file": "engine/workers/src/workers/acquisition.py",
        "gate": None,
        "status": "EXISTING",
    },
    "outreach_draft": {
        "specialist": "OutreachDrafter",
        "file": "engine/workers/src/workers/acquisition.py",
        "gate": "send",
        "status": "EXISTING",
    },
    "reply_triage": {
        "specialist": "ReplyHandler",
        "file": "engine/workers/src/workers/acquisition.py",
        "gate": "send",
        "status": "EXISTING",
    },
    "negotiation_prep": {
        "specialist": "NegotiationCoach",
        "file": "engine/workers/src/workers/acquisition.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "objection_sim": {
        "specialist": "ObjectionSimulator",
        "file": "engine/workers/src/workers/marketing.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "sales_close": {
        "specialist": "SalesCloser",
        "file": "sections/sell/agents/sales_closer.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "followup_draft": {
        "specialist": "FollowUpAgent",
        "file": "sections/sell/agents/followup_agent.py",
        "gate": "send",
        "status": "EXISTING",
    },
    "schedule_help": {
        "specialist": "SchedulerAssistant",
        "file": "engine/workers/src/workers/admin.py",
        "gate": None,
        "status": "EXISTING",
    },
    "maps_prospect_find": {
        "specialist": "Google Maps Prospect Finder",
        "class": "GoogleMapsProspectFinder",
        "file": "departments/01-sales-growth/specialists/google_maps_prospect_finder.py",
        "gate": None,
        "status": "EXISTING",
    },
    "business_verify": {
        "specialist": "Business Verification Agent",
        "class": "BusinessVerificationAgent",
        "file": "departments/01-sales-growth/specialists/business_verification_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "lead_score": {
        "specialist": "Lead Scoring Agent",
        "class": "LeadScoringAgent",
        "file": "departments/01-sales-growth/specialists/lead_scoring_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "crm_manage": {
        "specialist": "CRM Manager Agent",
        "class": "CRMManagerAgent",
        "file": "departments/01-sales-growth/specialists/crm_manager_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "sales_intelligence": {
        "specialist": "Sales Intelligence Agent",
        "class": "SalesIntelligenceAgent",
        "file": "departments/01-sales-growth/specialists/sales_intelligence_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class ChiefGrowthAgent:
    """Makes a DRAFT of the delegation plan for Sales & Growth specialists + loads and runs the Phase 3 specialists (DRAFT only)."""

    task_kind = "manage_sales_growth"
    gate = "ok"
    department = "01-sales-growth"
    role = "Chief Growth Agent"

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
        prospect = payload.get("prospect") or "BOSS INPUT REQUIRED"
        return (
            "Sales & Growth delegation plan draft for Talvenor. "
            f"Requested task kind: {task_kind}. Prospect: {prospect}. "
            "Name the specialist, their file, the gate needed, and the "
            "honest status. Do not invent any client fact; mark missing "
            "facts 'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical. Email is PAUSED since 2026-11-14; "
            "follow-ups stay PARKED until a state reaches 100 first mails."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Build a delegation plan DRAFT + Phase 3 specialist load+run (DRAFT only). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Manage Sales & Growth"
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
                "[MOCK DRAFT] Sales & Growth — department overview delegation plan (DRAFT ONLY)",
                "Manager: Chief Growth Agent | task_kind: manage_sales_growth | gate: ok",
                "Specialists (13 EXISTING):",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {entry['specialist']} | {entry['file']} | "
                    f"gate: {entry['gate'] or 'none'} | {entry['status']}"
                )
            lines.append(
                "Note: FollowUpAgent follow-ups PARKED — Pennsylvania 39 first "
                "mails (2026-11-12 count, verified against "
                "leads-organized/*/emailed.csv); under the 100-mail rule, no "
                "follow-up in any state until 100 first mails have been sent. "
                "Email PAUSED since 2026-11-14."
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
                "[MOCK DRAFT] Sales & Growth — unknown task (DRAFT ONLY)\n"
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

        # Phase 3 — standalone specialist (departments/01-sales-growth/specialists/)
        # If present, load it with importlib and run it (like the Chief's loader);
        # not a plan-draft, the specialist's own draft is returned. The 8 engine/section
        # workers' plan-draft behaviour is unchanged.
        spec_file = entry.get("file") or ""
        spec_class = entry.get("class")
        if spec_class and spec_file.startswith("departments/01-sales-growth/specialists/"):
            here = os.path.dirname(os.path.abspath(__file__))
            spec_path = os.path.normpath(os.path.join(
                here, "..", "specialists", os.path.basename(spec_file)))
            spec = importlib.util.spec_from_file_location(
                f"sales_specialist_{task_kind}", spec_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            agent_cls = getattr(mod, spec_class)
            agent = agent_cls()
            return agent.run(task, brain, gateway, approvals_path)

        payload = task.get("payload") or {}
        prospect = payload.get("prospect") or "BOSS INPUT REQUIRED"
        output = (
            "[MOCK DRAFT] Sales & Growth — delegation plan (DRAFT ONLY)\n"
            f"Task: {task_kind} | Prospect: {prospect}\n"
            f"Specialist: {entry['specialist']} | File/skill: {entry['file']}\n"
            f"Gate needed: {entry['gate'] or 'none'} | Status: {entry['status']}\n"
            "Plan (DRAFT):\n"
            f"1. {entry['specialist']} will be given the task — the manager does not do the work itself.\n"
            "2. The specialist's output will be shown to Boss as a DRAFT.\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — nothing without Boss's exact word "
                "must not be sent/published/spent.\n"
            )
        if task_kind == "followup_draft":
            output += (
                "4. Follow-up PARKED — 100-mail rule: Pennsylvania 39 first "
                "mails (2026-11-12 count); no follow-up in any state until "
                "100 first mails.\n"
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
