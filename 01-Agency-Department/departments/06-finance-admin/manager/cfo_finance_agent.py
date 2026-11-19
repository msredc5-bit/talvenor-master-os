"""CFO Finance Agent — finance & admin department manager (Phase 1).

ভূমিকা (role): 06-finance-admin department-এর manager — finance/admin
task এলে কোন specialist-এর কাজ, তা ঠিক করে DELEGATION PLAN-এর DRAFT
বানানো। নিজে কোনো invoice/report লেখে না, কোনো worker চালায় না।
Gate: ok — delegation plan ব্যবহার করতে Boss-এর "ok" লাগে।
অবস্থা (status): DRAFT ONLY — mock brain ($0), draft-ই শেষ কথা।
Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

Mapped existing staff (2): BillingInvoiceAgent (billing_invoice, ok —
LOCKED pricing, invoice শুধু paying client-এর জন্য Boss-এর কথায়,
prospect-কে কখনো দাম quote নয়), ReportCompiler (report_compile, no
gate — দেখা যায় এমন metric ছাড়া কিছু নয়, সংখ্যা বানায় না)।
LOCKED pricing (2026-11-12, internal only): Starter $547/mo + $597;
Growth $1,109/mo + $1,297; Scale $1,672/mo + $1,997 — prospect-কে
কখনো quote নয়।
এই manager কখনো করে না: worker execute করে না, payment নেয় না,
invoice issue করে না, কিছু পাঠায় না, খরচ করে না, দাম বানায় না,
client-এর তথ্য/পরিসংখ্যান বানায় না, কোনো guarantee দেয় না,
dental/medical বা patient-health ব্যবসা নেয় না।
"""

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
        "file": "ROLE-ONLY — skill: departments/06-finance-admin/skills/revenue-tracking-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "expense_tracking": {
        "specialist": "Expense Tracking Agent",
        "file": "GAP — no worker, no skill yet ($0 spend cap — no expenses to track)",
        "gate": "ok",
        "status": "GAP",
    },
    "subscription_tracking": {
        "specialist": "Subscription Tracking Agent",
        "file": "ROLE-ONLY — skill: departments/06-finance-admin/skills/subscription-tracking-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "document_management": {
        "specialist": "Document Management Agent",
        "file": "ROLE-ONLY — skill: departments/06-finance-admin/skills/document-management-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
    "compliance_calendar": {
        "specialist": "Compliance Calendar Agent",
        "file": "ROLE-ONLY — skill: departments/06-finance-admin/skills/compliance-calendar-agent.md (planned, not built)",
        "gate": "ok",
        "status": "ROLE-ONLY",
    },
}


class CFOFinanceAgent:
    """Finance/admin task-এর delegation plan DRAFT বানায়। Worker চালায় না।"""

    task_kind = "manage_finance_admin"
    gate = "ok"
    department = "06-finance-admin"
    role = "CFO Finance Agent"

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
        """Delegation plan DRAFT বানানো। কোনো worker চালায় না, file লেখে না, network ছোঁয় না।"""
        task = task or {}
        title = task.get("title") or "Finance & admin delegation"
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
        status_note = (
            "worker exists; this plan routes only, never executes."
            if entry["status"] == "EXISTING" else
            "no worker yet — this plan routes only; it never executes a worker."
            if entry["status"] == "ROLE-ONLY" else
            "no worker, no skill yet — nothing to route to; Boss-কে সিদ্ধান্ত দিতে হবে।"
        )
        output = (
            "[MOCK DRAFT] Delegation plan — DRAFT ONLY\n"
            f"Department: {self.department} | Manager: {self.role}\n"
            f"Task: {task_kind}\n"
            f"Specialist: {entry['specialist']}\n"
            f"File/skill: {entry['file']}\n"
            f"{gate_line}\n"
            f"Status: {entry['status']} — {status_note}\n"
            "Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।\n"
            f"Booking link (real): {BOOKING_LINK} | Phone (real): {TALVENOR_PHONE}\n"
            f"Brain note: {brain_text}"
        )
        notes = (
            "DRAFT ONLY — mock brain ($0). Delegation plan, execution নয়। "
            "Invoice শুধু paying client-এর জন্য Boss-এর কথায়; paying client 0। "
            "LOCKED pricing internal only — prospect-কে দাম quote নয়। Gate: ok।"
        )
        return {
            "status": "draft-ready",
            "output": output,
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
