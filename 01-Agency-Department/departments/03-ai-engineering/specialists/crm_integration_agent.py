"""CRM Integration Agent — CRM integration DRAFT plan (Dept 03 AI Engineering).

Role: making a DRAFT integration plan for how a Lead/Deal record goes into the CRM — field, stage, sync
rules. CRM (n8n Cloud Data Tables)
PLANNED, not live — so it touches no live CRM, makes no record,
does no sync.
Gate: none — the draft itself is safe. Changing a deal stage / closing / deleting needs
Boss's approval — when a gated action comes, a PENDING record is made in ApprovalGateway,
it is not executed.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

Honest status (2026-11-21): CRM is not live. Lead pool 537 unique (CSV) —
this now works in place of the CRM. Paying client 0.

This agent never: claims a live CRM, makes a live record,
does no sync, does not auto-create a deal, does not change a stage, does not close,
deletes nothing, invents no record information, sends nothing, publishes
nothing, spends nothing, deletes nothing, quotes no prices, gives no guarantee,
no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

MODES = ("log", "standing", "follow-up", "hygiene")

# DRAFT field spec — when the CRM is live, records will be arranged in these fields.
CONTACT_FIELDS = ("name", "email", "phone", "business", "niche", "tier")
DEAL_FIELDS = ("stage", "owner", "next_action", "next_date", "source")


class CRMIntegrationAgent:
    """CRM integration DRAFT plan ONLY — CRM is not live, no record."""

    task_kind = "crm_integration"
    gate = None
    department = "03-ai-engineering"
    role = "CRM Integration Agent"

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
        mode = payload.get("mode") or "BOSS INPUT REQUIRED"
        contact = payload.get("contact") or payload.get("email") or "BOSS INPUT REQUIRED"
        return (
            "CRM integration DRAFT plan for Talvenor. "
            f"Mode: {mode} (log / standing / follow-up / hygiene). "
            f"Contact: {contact}. "
            "CRM is n8n Cloud Data Tables — PLANNED, not live — so draft only "
            "the field/stage/sync plan; never claim a live record. Contact "
            "first, deal second; never auto-create a deal. Every open deal "
            "needs owner + next action + date. Do not invent any record; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Makes a CRM integration DRAFT plan. Writes no file, touches no network, touches no CRM."""
        task = task or {}
        title = task.get("title") or "CRM integration draft plan"
        gated_action = task.get("gated_action")
        approval_id = task.get("approval_id")

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

        payload = task.get("payload") or {}
        mode = (payload.get("mode") or "").strip().lower().replace("_", "-")
        contact = payload.get("contact") or payload.get("email") or "BOSS INPUT REQUIRED"
        deal = payload.get("deal") or "BOSS INPUT REQUIRED"

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — plan built from payload only."

        lines = [
            "[MOCK DRAFT] CRM integration plan — DRAFT ONLY",
            f"Department: {self.department} | Worker: {self.role}",
            "CRM PLANNED, not live — there is no live record, no claim of a live sync.",
            "",
        ]
        if mode not in MODES:
            lines += [
                "Question — no mode was given, so no plan was made:",
                "Which mode is wanted? log / standing / follow-up / hygiene — say one.",
                "No plan can be made without a mode — the mode is not assumed by making one.",
                "",
                "What the modes mean:",
                "- log: a DRAFT record of a deal's activity from one email/meeting/call.",
                "- standing: a sweep plan for all new activities since the last run.",
                "- follow-up: a deal silent for 14+ days — a DRAFT of the next touch.",
                "- hygiene: an audit plan for duplicates, stale records, and missing fields.",
            ]
        else:
            lines += [
                f"Mode: {mode}",
                f"Contact: {contact} | Deal: {deal}",
                "",
                "1. Field spec (DRAFT — when the CRM is live, records will be arranged in these fields):",
                "   Contact: " + ", ".join(CONTACT_FIELDS) + ".",
                "   Deal: " + ", ".join(DEAL_FIELDS) + ".",
                "",
                "2. Contact first, deal later — never auto-create:",
                "   A contact must be found by email. If there is none, from the signature/calendar",
                "   invite, propose making one — it must be announced before writing.",
                "   If no deal matches, stop and ask.",
                "",
                "3. Next-step queue (DRAFT):",
                "   Every open deal must have: owner + next action + date.",
                "   One without them is a dying deal — it must be moved up the queue.",
                "",
                "4. Stage + sync rules (DRAFT):",
                "   Changing a stage / closing a deal — never without approval.",
                "   Sync: only when the CRM is live — now only a plan to match fields from the outreach pool (CSV, 537",
                "   unique).",
            ]
            if mode == "follow-up":
                lines += [
                    "",
            "   Follow-up: a silent deal is not just flagged — write a DRAFT of the next touch,"
                    "   in Boss's voice, based on the last exchange.",
                    "   A draft is not sent without approval.",
                ]
            if mode == "hygiene":
                lines += [
                    "",
                    "   Hygiene: duplicate contact/company, deals past their close date,",
                    "   missing required fields, deals without a next step — current vs",
                    "   proposed must be shown side by side. Only approved items are written.",
                ]
        lines += [
            "",
            f"Booking link: {BOOKING_LINK} (New York Time) | Phone: {TALVENOR_PHONE}",
            f"Brain note: {brain_text}",
        ]
        notes = (
            "DRAFT ONLY — mock brain ($0). CRM integration plan ONLY — no "
            "live CRM, live record, or live sync. No deal auto-creation, no stage "
            "change, no close, no delete. No information was invented. Gate: none (draft)."
        )
        return {
            "status": "draft-ready",
            "output": "\n".join(lines),
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
