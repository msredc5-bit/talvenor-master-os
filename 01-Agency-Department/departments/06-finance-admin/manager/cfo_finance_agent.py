"""CFO Finance Agent — finance & admin department manager (Phase 1).

Role: manager of the 06-finance-admin department — finance/admin
when a task comes in, decide which specialist's job it is and make a DRAFT of the DELEGATION PLAN
and run the Phase 3 dept-06 specialists (draft-only).
It writes no invoice/report itself. The section/engine's old workers
(BillingInvoiceAgent / ReportCompiler) it does not run — for them only
a DRAFT of the delegation plan. Gate: ok — Boss's "ok" is needed to use the delegation plan.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.
Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.
Specialist wiring Phase 3 DONE — the manager now loads and runs the dept-06 specialists
with importlib (draft-only).

Mapped existing staff (7): BillingInvoiceAgent (billing_invoice, ok —
LOCKED pricing, invoice only for a paying client on Boss's word,
never quote a price to a prospect), ReportCompiler (report_compile, no
gate — nothing but visible metrics, invents no numbers), +
Phase 3 specialists (5, no gate): RevenueTrackingAgent
(revenue_tracking — revenue $0, template only), SubscriptionTrackingAgent
(subscription_tracking — paid $0 so far), DocumentManagementAgent
(document_management — organisation draft only),
ComplianceCalendarAgent (compliance_calendar — attorney review
deferred, no deadline invented), ExpenseTrackingAgent
(expense_tracking — $0 cap, entry DRAFT only, no spend approval).
LOCKED pricing (2026-11-12, internal only): Starter $547/mo + $597;
Growth $1,109/mo + $1,297; Scale $1,672/mo + $1,997 — never quote to a prospect.
This manager never does: execute a section/engine old worker,
take payment, issue an invoice, send anything, spend anything,
invent prices, invent client information/statistics, give any guarantee,
dental/medical or patient-health businesses.
"""

import importlib.util
import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Department task kinds.
# EXISTING: a worker exists — file = relative path inside 01-Agency-Department.
# ROLE-ONLY: a role definition exists, no worker — file = planned skill path.
# GAP: neither a worker nor a skill.
DEPARTMENT_TASKS = {
    "billing_invoice": {
        "specialist": "BillingInvoiceAgent",
        "file": "sections/ops/agents/billing_invoice_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "invoice_management": {
        "specialist": "BillingInvoiceAgent",
        "file": "sections/ops/agents/billing_invoice_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "report_compile": {
        "specialist": "ReportCompiler",
        "file": "engine/workers/src/workers/admin.py",
        "gate": None,
        "status": "EXISTING",
    },
    "financial_reporting": {
        "specialist": "ReportCompiler",
        "file": "engine/workers/src/workers/admin.py",
        "gate": None,
        "status": "EXISTING",
    },
    "revenue_tracking": {
        "specialist": "Revenue Tracking Agent",
        "class": "RevenueTrackingAgent",
        "file": "departments/06-finance-admin/specialists/revenue_tracking_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "expense_tracking": {
        "specialist": "Expense Tracking Agent",
        "class": "ExpenseTrackingAgent",
        "file": "departments/06-finance-admin/specialists/expense_tracking_agent.py",
        "gate": "ok",
        "status": "EXISTING",
    },
    "subscription_tracking": {
        "specialist": "Subscription Tracking Agent",
        "class": "SubscriptionTrackingAgent",
        "file": "departments/06-finance-admin/specialists/subscription_tracking_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "document_management": {
        "specialist": "Document Management Agent",
        "class": "DocumentManagementAgent",
        "file": "departments/06-finance-admin/specialists/document_management_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
    "compliance_calendar": {
        "specialist": "Compliance Calendar Agent",
        "class": "ComplianceCalendarAgent",
        "file": "departments/06-finance-admin/specialists/compliance_calendar_agent.py",
        "gate": None,
        "status": "EXISTING",
    },
}


class CFOFinanceAgent:
    """Makes a DRAFT of the delegation plan for a finance/admin task; runs the dept-06 specialists (Phase 3) — DRAFT only."""

    task_kind = "manage_finance_admin"
    gate = "ok"
    department = "06-finance-admin"
    role = "CFO Finance Agent"

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
                "Finance & admin delegation request for Talvenor. "
                f"Topic: {topic}. "
                "The task_kind is unknown in this department. "
                "List the department's known task kinds and ask Boss "
                "for the correct one. Do not invent any fact, price, "
                "or statistic."
            )
        return (
            "Delegation plan draft for a Talvenor finance & admin task. "
            f"Task kind: {task.get('task_kind')}. Topic: {topic}. "
            f"Specialist: {entry['specialist']}. "
            f"File/skill: {entry['file']}. "
            f"Gate: {entry['gate']}. Status: {entry['status']}. "
            "Produce a short delegation plan: specialist, their file/skill, "
            "gate needed, honest status. This plan routes only, it never "
            "executes a worker, never issues an invoice, never collects "
            "payment. LOCKED pricing is internal only — never quote a price "
            "to a prospect. Do not invent any client fact, price, or "
            "statistic. No dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Making a DRAFT of the delegation plan; running the dept-06 specialists (Phase 3). Writes no file, touches no network."""
        task = task or {}
        title = task.get("title") or "Finance & admin delegation"
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

        task_kind = task.get("task_kind")

        # Overview — if there is no task_kind (or the manager's own kind):
        # an overview DRAFT with the list of all the department's specialists.
        if not task_kind or task_kind == self.task_kind:
            if brain is not None:
                try:
                    brain_text = brain.complete(
                        "Finance & admin department overview for Talvenor. "
                        "List the department specialists, their files, gates, "
                        "and honest status. Do not invent any fact, price, "
                        "or statistic. No dental/medical.")
                except TypeError:
                    brain_text = brain.complete(
                        "Finance & admin department overview for Talvenor.",
                        max_tokens=500)
            else:
                brain_text = ("No brain passed — overview built from "
                              "DEPARTMENT_TASKS only.")
            lines = [
                "[MOCK DRAFT] Finance & Admin — department overview delegation plan (DRAFT ONLY)",
                "Manager: CFO Finance Agent | task_kind: manage_finance_admin | gate: ok",
                "Specialists:",
            ]
            for kind in sorted(DEPARTMENT_TASKS.keys()):
                overview_entry = DEPARTMENT_TASKS[kind]
                lines.append(
                    f"- {kind}: {overview_entry['specialist']} | "
                    f"{overview_entry['file']} | "
                    f"gate: {overview_entry['gate'] or 'none'} | "
                    f"{overview_entry['status']}"
                )
            lines.append(
                "Note: Paying client 0, revenue $0; invoice only for a paying "
                "client, on Boss's word. Email PAUSED since 2026-11-14."
            )
            lines.append(
                f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}")
            lines.append(f"Brain note: {brain_text}")
            notes = (
                "DRAFT ONLY — mock brain ($0). Overview delegation plan, "
                "no execution of a section/engine old worker. Chief wiring "
                "Phase 2 DONE — the Chief now calls this manager with DEPARTMENT_ROUTING "
                "calls it."
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

        # Phase 3 specialist — for a kind with a standalone .py, load the specialist
        # and run it with importlib (like the Chief's loader); return its
        # result. For the section/engine's old workers, the plan-draft behavior below is
        # unchanged.
        if (entry["status"] == "EXISTING"
                and entry["file"].startswith(
                    "departments/06-finance-admin/specialists/")):
            here = os.path.dirname(os.path.abspath(__file__))
            specialist_path = os.path.normpath(os.path.join(
                here, "..", "..", "..", entry["file"]))
            spec = importlib.util.spec_from_file_location(
                f"dept06_specialist_{task_kind}", specialist_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            specialist_cls = getattr(mod, entry["class"])
            specialist = specialist_cls()
            gw = gateway if gateway is not None else self._gateway(approvals_path)
            return specialist.run(task, brain, gw, approvals_path)

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
        status_note = (
            "worker exists; this plan routes only, never executes."
            if entry["status"] == "EXISTING" else
            "no worker yet — this plan routes only; it never executes a worker."
            if entry["status"] == "ROLE-ONLY" else
            "worker + skill now exist (2026-11-21) — worker path in File/skill "
            "above; this plan routes only, never executes."
        )
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File/skill: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — {status_note}\n"
            "Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, not execution. "
            "Invoice only for a paying client, on Boss's word; paying client 0. "
            "LOCKED pricing internal only — never quote a price to a prospect. Gate: ok."
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
