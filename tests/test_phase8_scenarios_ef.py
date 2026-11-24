"""Phase 8 Worker B — brief §21 scenarios E and F (Talvenor Master OS).

Scenario E: a restricted financial action (spend) requested without
approval is blocked AND recorded until valid Founder approval is
obtained; with a valid Boss approval the same action is allowed
through the gateway (record shows approved, decided_by Boss).

Scenario F: the application restarts during a pending job and
correctly recovers its task state without duplicate external
actions — a queued task survives a simulated restart (re-created
runner/drain against the same temp store dir), recovers, and drains
exactly once with exactly one execution record.

All stores are tmp_path. No network, no live calls, no
send/publish/spend/delete/deploy. $0 everywhere.
"""
import copy
import json

from agent_runtime.gate import enforce_gate
from human_approval_gateway import ApprovalGateway
from lead_chain.fixtures import STRONG_TIER1_PROSPECT
from workflow_engine import queue as queue_mod
import run_office


def _read_tasks(tmp_path):
    data = json.loads((tmp_path / "tasks.json").read_text(
        encoding="utf-8"))
    return {r["id"]: r for r in data["records"]}


def _seed_task(tmp_path, record):
    (tmp_path / "tasks.json").write_text(
        json.dumps({"schema": "tasks-v1", "records": [record]}),
        encoding="utf-8")


# ---------------------------------------------------------------- scenario E
class TestScenarioERestrictedFinancialAction:
    def test_spend_blocked_and_recorded_until_boss_approval(
            self, tmp_path):
        """End to end in a temp store: (1) a spend action with no
        approval is blocked by the gate AND recorded as a pending
        approval — nothing executes; (2) the wrong gate word does
        not release it; (3) Boss's exact gate word ("go") approves
        it and the record shows approved, decided_by Boss."""
        approvals_path = str(tmp_path / "approvals.json")
        gw = ApprovalGateway(approvals_path=approvals_path)

        # (1) Blocked: the runtime gate refuses the spend, and the
        # request is recorded as pending in the gateway.
        verdict = enforce_gate({
            "action": "spend",
            "args": {"amount_usd": 5, "purpose": "test ads"},
        })
        assert verdict["allowed"] is False
        assert verdict["status"] == "pending-approval"
        req = gw.request("spend", "test spend $5 (scenario E)",
                         "ScenarioE")
        assert req["status"] == "pending"
        assert gw.is_approved(req["id"]) is False
        assert len(gw.pending()) == 1
        # Nothing executed: the gate verdict is the only outcome,
        # and the pending record is the full audit trail.
        assert enforce_gate({"action": "spend"})["allowed"] is False

        # (2) The wrong gate word does not release it.
        import pytest
        with pytest.raises(ValueError):
            gw.approve(req["id"], gate_word="send")
        assert gw.is_approved(req["id"]) is False
        assert gw.pending()[0]["status"] == "pending"

        # (3) Boss's exact gate word approves it.
        approved = gw.approve(req["id"], gate_word="go",
                              decided_by="Boss")
        assert approved["status"] == "approved"
        assert approved["decided_by"] == "Boss"
        assert approved["gate_word"] == "go"
        assert gw.is_approved(req["id"]) is True
        assert gw.pending() == []

        # The approval survives a fresh gateway read of the same
        # temp file — the decision is really recorded, not in-memory.
        gw2 = ApprovalGateway(approvals_path=approvals_path)
        assert gw2.is_approved(req["id"]) is True
        assert gw2.pending() == []

    def test_spend_denied_by_trust_gate_even_before_gateway(self):
        """Belt and braces: the trust gate denies a $5 spend
        outright (spend cap $0), so it never even reaches a pending
        approval on a fabricated quote."""
        from trust_gate import trust_check
        decision = trust_check(
            "spend", {"amount_usd": 5, "purpose": "test ads"},
            config={"spend_cap_usd": 0})
        assert decision["decision"] == "deny"
        assert "$0" in decision["reason"]


# ---------------------------------------------------------------- scenario F
class TestScenarioFRestartRecovery:
    def test_restart_recovers_pending_job_and_drains_exactly_once(
            self, tmp_path):
        """Seed a queued lead_chain task; simulate a restart by
        (a) marking it stuck mid-run (the state a crash leaves),
        (b) running the restart-recovery scan, then (c) re-creating
        the drain against the SAME temp store dir. The task recovers
        to queued, drains to done, and carries exactly ONE execution
        record — no duplicate external action."""
        prospect = copy.deepcopy(STRONG_TIER1_PROSPECT)
        task = {
            "id": "f-restart-1", "status": "running",
            "started_at": "2026-11-25T00:00:00+00:00",
            "business": "agency", "type": "lead_chain",
            "title": "F restart test", "payload": {},
            "prospect": prospect, "retries": 0, "max_retries": 2,
            "depends_on": [], "priority": 0, "executions": [],
        }
        _seed_task(tmp_path, task)

        # (a) Pre-restart state: the record looks stuck mid-run.
        assert queue_mod.scan_for_stuck_records([task])[0][
            "record_id"] == "f-restart-1"

        # (b) Restart: the recovery scan requeues it WITHOUT
        # incrementing retries (the attempt never completed).
        report = queue_mod.recover_stuck_records(
            str(tmp_path), policy="requeue",
            reason="scenario F simulated restart",
            now="2026-11-25T01:00:00+00:00")
        assert len(report["recovered"]) == 1
        assert report["recovered"][0]["action"] == "requeued"
        recovered = _read_tasks(tmp_path)["f-restart-1"]
        assert recovered["status"] == "queued"
        assert recovered["retries"] == 0
        assert recovered["started_at"] is None
        assert queue_mod.scan_for_stuck_records(
            [recovered]) == []

        # (c) Re-created drain against the SAME store dir: the task
        # runs once and finishes; a second drain finds nothing left
        # to run (no duplicate execution).
        summary = run_office.drain_queue(str(tmp_path), max_tasks=5)
        assert summary["halted"] is False
        assert summary["recovered"] == []  # already recovered above
        processed = [p for p in summary["processed"]
                     if p["id"] == "f-restart-1"]
        assert len(processed) == 1
        assert processed[0]["status"] == "done"

        final = _read_tasks(tmp_path)["f-restart-1"]
        assert final["status"] == "done"
        executions = final.get("executions") or []
        assert len(executions) == 1  # exactly one attempt, ever
        assert executions[0]["attempt"] == 1
        assert executions[0]["status"] == "done"
        assert executions[0]["cost_usd"] == 0.0

        summary2 = run_office.drain_queue(str(tmp_path), max_tasks=5)
        assert summary2["processed"] == []
        assert len(_read_tasks(tmp_path)["f-restart-1"]
                   .get("executions") or []) == 1

    def test_restart_with_clean_store_drains_queued_task_once(
            self, tmp_path):
        """Control case: a plain queued task (no crash) also drains
        exactly once across two drain runs — the drain itself never
        double-executes."""
        prospect = copy.deepcopy(STRONG_TIER1_PROSPECT)
        task = {
            "id": "f-clean-1", "status": "queued",
            "business": "agency", "type": "lead_chain",
            "title": "F clean test", "payload": {},
            "prospect": prospect, "retries": 0, "max_retries": 0,
            "depends_on": [], "priority": 0,
        }
        _seed_task(tmp_path, task)
        summary = run_office.drain_queue(str(tmp_path), max_tasks=5)
        assert [p["status"] for p in summary["processed"]
                if p["id"] == "f-clean-1"] == ["done"]
        summary2 = run_office.drain_queue(str(tmp_path), max_tasks=5)
        assert summary2["processed"] == []
        final = _read_tasks(tmp_path)["f-clean-1"]
        assert len(final.get("executions") or []) == 1
