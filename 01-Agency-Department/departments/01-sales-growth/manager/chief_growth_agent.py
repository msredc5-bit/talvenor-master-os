"""Chief Growth Agent — Sales & Growth department-এর manager (Phase 1).

ভূমিকা (role): Sales & Growth department-এর ১৩ জন existing specialist-কে
delegate করা — prospect research, outreach draft, reply triage, negotiation
prep, objection sim, sales close, follow-up draft, schedule help, maps
prospect find, business verify, lead score, CRM manage, sales intelligence। এই manager
delegation plan-এর DRAFT বানায় + Phase 3 specialist-দের importlib দিয়ে load করে চালায় (DRAFT only); engine/section-এর পুরনো worker execute করে না।
Gate: ok — delegation plan-এ Boss-এর "ok" লাগে; send/publish/spend/delete
কোনো gated action এই manager নিজে করে না।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Agency Chief wiring Phase 2 DONE — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।
এই manager কখনো করে না: engine/section-এর পুরনো worker execute করে না, কিছু পাঠায় না,
প্রকাশ করে না, খরচ করে না, মুছে না, client-এর তথ্য/দাম/পরিসংখ্যান
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
    """Sales & Growth specialist-দের delegation plan DRAFT বানায় + Phase 3 specialist-দের load করে চালায় (DRAFT only)।"""

    task_kind = "manage_sales_growth"
    gate = "ok"
    department = "01-sales-growth"
    role = "Chief Growth Agent"

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
        """Delegation plan DRAFT বানানো + Phase 3 specialist load+run (DRAFT only)। কোনো file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Manage Sales & Growth"
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
                "Note: FollowUpAgent follow-ups PARKED — Pennsylvania 37 first "
                "mails; 100-mail rule অনুযায়ী কোনো state-এ 100 first mail না "
                "হলে follow-up নয়। Email PAUSED since 2026-11-14."
            )
            lines.append(f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, কোনো "
                "worker execute নয়। Agency Chief wiring Phase 2 DONE — Chief এখন "
                "এই manager-কে DEPARTMENT_ROUTING দিয়ে call করে।"
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

        # Phase 3 — standalone specialist (departments/01-sales-growth/specialists/)
        # থাকলে তাকে importlib দিয়ে load করে run করা (Chief-এর loader-এর মতো);
        # plan-draft নয়, specialist-এর নিজের draft-ই ফেরত। 8 engine/section
        # worker-এর plan-draft behavior অপরিবর্তিত।
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
            f"1. {entry['specialist']}-কে task দেওয়া হবে — manager নিজে কাজটি করে না।\n"
            "2. Specialist-এর output DRAFT হিসেবে Boss-কে দেখানো হবে।\n"
        )
        if entry["gate"]:
            output += (
                f"3. Gate '{entry['gate']}' — Boss-এর exact word ছাড়া কিছু "
                "পাঠানো/প্রকাশ/খরচ করা যাবে না।\n"
            )
        if task_kind == "followup_draft":
            output += (
                "4. Follow-up PARKED — 100-mail rule: Pennsylvania 37 first "
                "mails; কোনো state-এ 100 first mail না হলে follow-up নয়।\n"
            )
        if entry["status"] == "ROLE-ONLY":
            output += (
                "4. ROLE-ONLY — এই role-এর কোনো worker code নেই; skill doc "
                "অনুযায়ী Boss/Elora হাতে কাজটি করবেন।\n"
            )
        output += (
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan মাত্র; worker "
            "execute হয়নি, কিছু পাঠানো হয়নি। Agency Chief wiring Phase 2 DONE — "
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
