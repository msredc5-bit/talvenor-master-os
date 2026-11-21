"""Backup & Recovery Agent — backup DRAFT plan + DR runbook (Dept 07 Quality & Security).

Role: building a DRAFT backup plan + disaster recovery
runbook for how to restore Talvenor Master OS data (repo + local store file)
if it is lost. It does not run backups, does not run restore tests — it gives a plan DRAFT.
A restore test needs Boss's "ok".
Gate: none — the draft itself is safe. Touching a restore test / the real store —
if a gated action arrives, a PENDING record is made in ApprovalGateway, nothing is executed.
Status: DRAFT ONLY — mock brain ($0), the draft is the final word.

True status (2026-11-21): no backup system yet — the repo is pushed to GitHub
(that is the backup for now), no dated backup of the store file, no restore test
done. So "protected" cannot be said.

This agent never does this: it never says "protected" without a restore test, never puts secret/
key/password in a backup, never deletes / changes the real store file,
never force-pushes / rewrites history, sends nothing, publishes nothing,
spends nothing, deletes nothing, quotes no price, gives no guarantee,
no dental/medical.
"""

import os
import sys

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
TALVENOR_PHONE = "+1 (947) 223-0244"

_GATE_ACTION_MAP = {"post it": "publish", "upload it": "publish"}
_GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Talvenor default (Boss can change it) — the numbers are Boss's, an engineer does not decide them alone.
DEFAULT_RPO = "1 day (store file)"
DEFAULT_RTO = "1 hour (fresh clone + store restore)"

# Asset inventory (the basis of the DRAFT plan).
ASSETS = (
    ("GitHub repo (msredc5-bit/talvenor-master-os)", "Code + skills + docs", "YES — this is the off-site copy"),
    ("store/memory.json", "Boss's words + agent note", "YES"),
    ("store/tasks.json", "Task queue", "YES"),
    ("store/approvals.json", "Approval record", "YES"),
    ("store/usage-ledger.json", "$0 ledger", "YES"),
    ("store/skill-proposals.json", "Skill proposals", "PARTIAL"),
    ("Voice model file (~361 MB)", "Piper/sherpa model", "NO — can be downloaded again"),
    ("API key", "Env var only", "CRITICAL — never goes into a backup"),
)


class BackupRecoveryAgent:
    """Backup DRAFT plan + DR runbook ONLY — does not run backups, does not test."""

    task_kind = "backup_recovery"
    gate = None
    department = "07-quality-security"
    role = "Backup & Recovery Agent"

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

    def _prompt(self, task):
        payload = task.get("payload") or {}
        scenario = payload.get("scenario") or "BOSS INPUT REQUIRED"
        rpo = payload.get("rpo") or DEFAULT_RPO
        rto = payload.get("rto") or DEFAULT_RTO
        return (
            "Backup + disaster recovery DRAFT plan for Talvenor Master OS. "
            f"Scenario: {scenario}. RPO: {rpo}. RTO: {rto}. "
            "Inventory → RPO/RTO → 3-2-1 strategy → verification → runbook. "
            "A backup counts only after a restore test — never claim "
            "'protected' without one. Secrets never go in a backup; no "
            "force-push, no history rewrite; restore tests run on TEMP copies "
            "only, never the real store. Do not invent test results; mark "
            "missing facts 'BOSS INPUT REQUIRED'. No price, no guarantee, "
            "no dental/medical."
        )

    def run(self, task, brain=None, gateway=None, approvals_path=None):
        """Building a Backup DRAFT plan + DR runbook. Writes no file, touches no network, runs no backup, restores nothing."""
        task = task or {}
        title = task.get("title") or "Backup and recovery draft plan"
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
        scenario = (payload.get("scenario") or "").strip().lower()
        rpo = payload.get("rpo") or DEFAULT_RPO
        rto = payload.get("rto") or DEFAULT_RTO

        if brain is not None:
            try:
                brain_text = brain.complete(self._prompt(task))
            except TypeError:
                brain_text = brain.complete(self._prompt(task), max_tokens=500)
        else:
            brain_text = "No brain passed — plan built from payload only."

        lines = [
            "[MOCK DRAFT] Backup + disaster recovery plan — DRAFT ONLY",
            f"Department: {self.department} | Worker: {self.role}",
            "No protected without a restore test — no restore test was done, so in this plan",
            "\"protected\" was not said. Backup health: NOT VERIFIED.",
            "",
            "1. Asset inventory (what hurts if lost):",
        ]
        for asset, kind, critical in ASSETS:
            lines.append(f"   - {asset} | {kind} | Critical: {critical}")
        lines += [
            "",
            "2. RPO / RTO (the numbers are Boss's — an engineer does not decide them alone):",
            f"   RPO (how much data loss is acceptable): {rpo}",
            f"   RTO (how fast it can be restored): {rto}",
            "",
            "3. Strategy — 3-2-1, at our scale:",
            "   - 3 copy: local repo + GitHub push + dated backups/ copy.",
            "   - 2 medium: disk + GitHub.",
            "   - 1 off-site: GitHub itself is the off-site — a backup is never on just one PC.",
            "   - Secrets never in a backup: no .env; the API key lives in an env var,",
            "     never written to any file.",
            "",
            "4. Verification — without a test it is not a backup:",
            "   - For every backup: is the file there, is the size right, does the checksum match.",
            "   - Restore test (sample), weekly: clone into a TEMP folder + store file",
            "     placed and checks run (the real store must not be touched).",
            "   - Full restore test, monthly: fresh-clone the whole repo and check.",
            "   - If a restore test fails, the verdict is AT RISK — \"protected\" cannot be said.",
            "   - A replica is not a backup — a push to GitHub alone does not prove restore; a test is needed.",
            "",
            "5. Recovery — steps per scenario (DRAFT):",
        ]
        if scenario in ("store corrupt", "store_corrupt", "corrupt"):
            lines += [
                "   Scenario: store file corrupt —",
            "   1) restore from the backup copy → 2) match the checksum → 3) tell Boss.",
            ]
        elif scenario in ("repo lost", "repo_lost", "pc lost", "pc_lost"):
            lines += [
            "   Scenario: repo lost / PC broken —",
            "   1) fresh clone from GitHub → 2) place the store backup →",
            "   3) run checks → 4) tell Boss.",
            ]
        elif scenario in ("wrong delete", "wrong_delete", "delete"):
            lines += [
            "   Scenario: accidental delete —",
            "   1) restore from Git history (never force-push).",
            ]
        else:
            lines += [
            "   No scenario given — steps for the three scenarios:",
            "   - Store file corrupt: restore from the backup copy → checksum → tell Boss.",
            "   - Repo lost / PC broken: fresh clone → store backup → check → tell Boss.",
            "   - Accidental delete: restore from Git history (never force-push).",
            "   After every recovery: what happened, how much was lost, how to stop it happening again — a one-page note.",
            ]
        lines += [
            "",
            "6. Runbook (DRAFT — anyone can run it):",
            "   Last tested date: never tested (BOSS INPUT REQUIRED).",
            "   Next test date: Boss will decide. Owner: Boss.",
            f"   RPO: {rpo} | RTO: {rto}.",
            "   Backup health: NOT VERIFIED (no restore test done).",
            "   A restore test cannot be run without Boss's \"ok\" (even on a TEMP copy).",
            f"Booking link: {BOOKING_LINK} (New York Time) | Phone: {TALVENOR_PHONE}",
            f"Brain note: {brain_text}",
        ]
        notes = (
            "DRAFT ONLY — mock brain ($0). Backup plan + DR runbook ONLY — "
            "No backup was run, no restore test was done, the real store "
            "was not touched. No protected without a restore test. Gate: none (draft); "
            "a restore test needs Boss's ok."
        )
        return {
            "status": "draft-ready",
            "output": "\n".join(lines),
            "notes": notes,
            "draft_only": True,
            "mock_brain": True,
            "gate": self.gate,
        }
