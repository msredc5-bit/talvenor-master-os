"""Phase 8 Worker B — brief §21 items 9-16 (Talvenor Master OS).

Real code under test (all stdlib, temp stores only, no network,
no live LLM calls, no send/publish/spend/delete/deploy, $0):

  item  9  Event trigger      — workflow_engine/n8n_adapter.py +
                               test_double.py (webhook trigger) and
                               workflow_engine/scheduler.py (due jobs).
                               There is NO event bus in the repo
                               (grep: no event_bus / EventBus /
                               subscribe anywhere) — the genuine
                               trigger paths are tested, the bus is
                               marked [NOT TESTED] with a skip.
  item 10  Retry handling     — workflow_engine/queue.py (DLQ,
                               retry budget, repeated-same-error).
  item 11  Restart recovery   — workflow_engine/queue.py
                               (scan + recover_stuck_records).
  items 12-13 Permission enforcement / Restricted-action blocking
                              — agent_runtime/gate.py,
                               trust_gate.py, human_approval_gateway.py,
                               permissions.py, tools.json (read-only).
  item 14  Approved policy-based execution — NO policy engine exists
                               in the repo (grep: no policy engine,
                               no evaluate_policy); only per-action
                               gates exist. The real per-action flow
                               is tested; the policy-engine part is
                               marked [NOT TESTED] with a skip.
  item 15  Provider failure   — live_brain.py (dev-mode adapter),
                               free_only_guard.py, and the real
                               GeminiProvider (key-missing + HTTP
                               code prefix paths; no network).
  item 16  Budget enforcement — agent_runtime/limits.py
                               (CostTracker / RuntimeLimits) and
                               queue.build_execution (negative cost).

Scheduler self-test regression (Phase 7 known issue 1, fixed in
Phase 8): scheduler.py __main__ step 9 scanned the whole file, so
its own token literals ("requests.", "urllib", ...) tripped it, and
the bare "sk-" token false-positived on the job id
"daily-task-queue-drain-watch" ("ta[sk-]queue"). Fixed by scanning
only the module body and checking "sk-" as a key-like pattern.
"""
import json
import os
import re
import subprocess
import sys
import urllib.error

import pytest

from agent_runtime.gate import enforce_gate, is_gated_action
from agent_runtime.limits import CostTracker, LimitExceeded, RuntimeLimits
from free_only_guard import (
    FreeOnlyViolation,
    check_call,
    is_free_model,
    is_rate_limit_error,
    log_call,
)
import free_only_guard
from human_approval_gateway import ApprovalGateway, GATE_WORD_FOR_ACTION
from live_brain import LiveBrainAdapter
from permissions import allowed_tools, check_permission, resolve_agent
from trust_gate import ConfirmationStore, trust_check
from workflow_engine import queue as queue_mod
from workflow_engine.engine import WorkflowEngine
from workflow_engine.n8n_adapter import N8nAdapter, N8nError
from workflow_engine.scheduler import (
    ActivationRefused,
    ScheduleStore,
    activate_job,
    create_paused_jobs,
    due_jobs,
    job_definitions,
    should_run_job,
    validate_job_definitions,
)
from workflow_engine.test_double import N8nTestDouble

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULER_PATH = os.path.join(
    REPO_ROOT, "00-CEO-Core", "workflow_engine", "scheduler.py")

_TS = "2026-11-25T01:00:00+00:00"
_BOSS_APPROVAL = {
    "approval_id": "APR-PH8-1", "approver": "Boss",
    "decision": "approved",
    "scope": "scheduler-activation:weekly-ceo-report",
}


def _record(**over):
    rec = {"id": "t1", "status": "queued", "business": "agency",
           "type": "caption_write", "title": "t", "payload": {},
           "retries": 0, "max_retries": 2, "last_error": None,
           "executions": []}
    rec.update(over)
    return rec


def _failed_executions(record, error, count):
    for i in range(1, count + 1):
        queue_mod.append_execution(record, queue_mod.build_execution(
            record["id"], i, "failed", started_at=_TS, finished_at=_TS,
            error=error, cost_usd=0.0))


# ---------------------------------------------------------------- item 9
class TestItem9EventTrigger:
    def test_webhook_trigger_round_trip_via_test_double(self):
        """The real trigger path that exists: an n8n webhook trigger
        against the local test double creates an execution that
        finishes, and its status reads back as finished."""
        with N8nTestDouble(secret="test-secret") as double:
            adapter = N8nAdapter(base_url=double.base_url,
                                 webhook_secret="test-secret")
            result = adapter.trigger_via_webhook(
                "prospect-reply",
                {"event": "prospect_reply", "from": "a@b.com"})
            assert result["status"] == "finished"
            assert result["executionId"].startswith("exec-")
            status = adapter.get_execution_status(result["executionId"])
            assert status["status"] == "finished"
            assert status["webhook_path"] == "prospect-reply"
            assert status["payload"]["event"] == "prospect_reply"

    def test_webhook_trigger_wrong_secret_is_401(self):
        """A trigger without the shared secret is refused (401) —
        the trigger path is authenticated, not open."""
        with N8nTestDouble(secret="test-secret") as double:
            adapter = N8nAdapter(base_url=double.base_url,
                                 webhook_secret="wrong-secret")
            with pytest.raises(N8nError) as excinfo:
                adapter.trigger_via_webhook("prospect-reply", {"x": 1})
            assert excinfo.value.status == 401

    def test_webhook_trigger_non_localhost_refused(self):
        """The adapter is localhost-only by design — a remote n8n
        URL is refused before any network happens."""
        with pytest.raises(ValueError, match="localhost-only"):
            N8nAdapter(base_url="https://n8n.example.com")

    def test_scheduler_due_job_detection(self, tmp_path):
        """The other real trigger path: a Boss-activated scheduler
        job is due on first run; a paused job is never due."""
        store = ScheduleStore(
            schedules_path=str(tmp_path / "schedules.json"))
        create_paused_jobs(store)
        assert all(not d["due"] for d in due_jobs(store))
        due, reason = should_run_job(store, "weekly-ceo-report",
                                     {"tasks": ["a"]})
        assert due is False and "paused" in reason
        activate_job(store, "weekly-ceo-report", _BOSS_APPROVAL)
        due, reason = should_run_job(store, "weekly-ceo-report",
                                     {"tasks": ["a"]})
        assert due is True and reason.startswith("first run")

    def test_scheduler_definitions_are_draft_only(self):
        """All 4 scheduler jobs validate and their actions are
        watch/report/draft only — a trigger can never smuggle a
        commit action in."""
        assert validate_job_definitions() is True
        assert len(job_definitions()) == 4
        assert all(j["action"] in ("watch", "report", "draft")
                   for j in job_definitions())

    @pytest.mark.skip(reason="[NOT TESTED] No event bus exists in the "
                      "repo (grep: no event_bus / EventBus / subscribe "
                      "in 00-CEO-Core, scripts, or the agency engine) "
                      "— Phase 0 audit gap. The real trigger paths "
                      "(n8n webhook, scheduler due) are tested above; "
                      "a bus-based 'Prospect Reply event triggers "
                      "classification' flow cannot be tested until "
                      "the bus is built.")
    def test_event_bus_prospect_reply(self):
        raise AssertionError("no event bus to test")


# ---------------------------------------------------------------- item 10
class TestItem10RetryHandling:
    @pytest.mark.parametrize("retries,max_retries,expected", [
        (0, 0, False),   # no failure yet: budget not spent
        (1, 0, True),    # max 0: the first failure exhausts
        (1, 2, False),
        (2, 2, False),   # 2 <= 2: one more retry left
        (3, 2, True),
        (5, 5, False),
        (6, 5, True),
    ])
    def test_retries_exhausted_boundaries(self, retries, max_retries,
                                          expected):
        assert queue_mod.retries_exhausted(retries, max_retries) \
            is expected

    @pytest.mark.parametrize("retries,max_retries", [
        (-1, 0), (0, -1), (1.5, 2), ("1", 2), (True, 2), (1, None),
    ])
    def test_retries_exhausted_rejects_bad_budgets(self, retries,
                                                   max_retries):
        with pytest.raises(ValueError):
            queue_mod.retries_exhausted(retries, max_retries)

    def test_dlq_on_exhaustion(self):
        rec = _record(retries=3, max_retries=2, last_error="boom")
        assert queue_mod.exhaustion_reason(rec) == "retries_exhausted"
        queue_mod.mark_dead_letter(rec, "retries_exhausted",
                                   last_error="boom", now=_TS)
        assert rec["status"] == "dead_letter"
        assert rec["dead_letter_reason"] == "retries_exhausted"
        assert rec["dead_letter_at"] == _TS
        assert rec["last_error"] == "boom"
        assert queue_mod.is_dead_letter(rec) is True
        assert queue_mod.is_terminal(rec) is True
        # A dead-letter record is never drained as queued and never
        # looks stuck to the recovery scan.
        assert queue_mod.scan_for_stuck_records([rec]) == []

    def test_dlq_reason_is_required(self):
        rec = _record()
        with pytest.raises(ValueError):
            queue_mod.mark_dead_letter(rec, "  ")
        with pytest.raises(ValueError):
            queue_mod.mark_dead_letter(rec, "")

    def test_repeated_same_error_early_dlq_at_3x(self):
        rec = _record(retries=1, max_retries=5)
        _failed_executions(rec, "boom", 2)
        assert queue_mod.consecutive_same_error_count(rec) == 2
        assert queue_mod.repeated_same_error(rec) is False
        assert queue_mod.exhaustion_reason(rec) is None
        _failed_executions(rec, "boom", 1)  # third identical failure
        assert queue_mod.consecutive_same_error_count(rec) == 3
        assert queue_mod.repeated_same_error(rec) is True
        assert queue_mod.exhaustion_reason(rec) == \
            "repeated_same_error: boom"

    def test_repeated_error_count_breaks_on_different_error(self):
        rec = _record()
        _failed_executions(rec, "boom", 2)
        queue_mod.append_execution(rec, queue_mod.build_execution(
            "t1", 3, "failed", started_at=_TS, finished_at=_TS,
            error="other", cost_usd=0.0))
        assert queue_mod.consecutive_same_error_count(rec) == 1
        assert queue_mod.repeated_same_error(rec) is False

    def test_repeated_error_count_breaks_on_success(self):
        rec = _record()
        _failed_executions(rec, "boom", 3)
        assert queue_mod.repeated_same_error(rec) is True
        queue_mod.append_execution(rec, queue_mod.build_execution(
            "t1", 4, "done", started_at=_TS, finished_at=_TS,
            error=None, cost_usd=0.0))
        assert queue_mod.consecutive_same_error_count(rec) == 0

    def test_repeated_same_error_threshold_validated(self):
        rec = _record()
        with pytest.raises(ValueError):
            queue_mod.repeated_same_error(rec, threshold=0)

    def test_execution_cap_counts_trims(self):
        rec = _record()
        for i in range(1, 105):
            queue_mod.append_execution(rec, queue_mod.build_execution(
                "t1", i, "failed", started_at=_TS, finished_at=_TS,
                error="x", cost_usd=0.0))
        assert len(rec["executions"]) == queue_mod.MAX_EXECUTIONS_PER_RECORD
        assert rec["executions"][0]["attempt"] == 5
        assert rec["executions_trimmed"] == 4

    def test_build_execution_rejects_negative_cost(self):
        with pytest.raises(ValueError):
            queue_mod.build_execution("t1", 1, "failed", cost_usd=-1.0)
        with pytest.raises(ValueError):
            queue_mod.build_execution("t1", 1, "weird")

    def test_requeue_is_manual_and_resets_budget(self):
        rec = _record(retries=3, max_retries=2, last_error="boom")
        queue_mod.mark_dead_letter(rec, "retries_exhausted", now=_TS)
        with pytest.raises(ValueError):
            queue_mod.requeue_from_dead_letter(rec, "")
        queue_mod.requeue_from_dead_letter(
            rec, "Boss: retry once, fixed prompt", now=_TS)
        assert rec["status"] == "queued" and rec["retries"] == 0
        assert rec["last_error"] is None
        assert rec["dead_letter_reason"] is None
        assert rec["requeue_count"] == 1
        # A queued record cannot be requeued again — no silent retry.
        with pytest.raises(ValueError):
            queue_mod.requeue_from_dead_letter(rec, "again")


# ---------------------------------------------------------------- item 11
class TestItem11RestartRecovery:
    def _write_tasks(self, tmp_path, records):
        path = tmp_path / "tasks.json"
        path.write_text(json.dumps({"schema": "tasks-v1",
                                    "records": records}),
                        encoding="utf-8")
        return str(tmp_path)

    def test_scan_finds_only_stuck_shapes(self):
        assert queue_mod.scan_for_stuck_records([
            {"id": "a", "status": "queued"},
            {"id": "b", "status": "done"},
            {"id": "c", "status": "dead_letter"},
            {"id": "d", "status": "failed"},
        ]) == []
        stuck = queue_mod.scan_for_stuck_records([
            {"id": "s1", "status": "running", "started_at": _TS},
            {"id": "s2", "status": "queued", "started_at": _TS},
            {"id": "s3", "status": "in_progress"},
        ])
        assert [f["record_id"] for f in stuck] == ["s1", "s2", "s3"]
        assert stuck[0]["reason"] == "transient_status:running"
        assert stuck[1]["reason"] == "started_but_not_terminal"

    def test_recovery_requeues_without_incrementing_retries(
            self, tmp_path):
        store_dir = self._write_tasks(tmp_path, [
            {"id": "s1", "status": "running", "started_at": _TS,
             "retries": 2, "max_retries": 2},
            {"id": "ok1", "status": "done"},
        ])
        report = queue_mod.recover_stuck_records(
            store_dir, policy="requeue",
            reason="test restart scan", now=_TS)
        assert len(report["found"]) == 1
        assert report["recovered"][0]["record_id"] == "s1"
        assert report["recovered"][0]["action"] == "requeued"
        data = json.loads((tmp_path / "tasks.json").read_text())
        by_id = {r["id"]: r for r in data["records"]}
        assert by_id["s1"]["status"] == "queued"
        assert by_id["s1"]["started_at"] is None
        assert by_id["s1"]["last_stuck_started_at"] == _TS
        # The attempt never completed: retries NOT incremented.
        assert by_id["s1"]["retries"] == 2
        assert by_id["s1"]["recovery_reason"] == "test restart scan"
        assert by_id["ok1"]["status"] == "done"  # untouched
        # The recovered record no longer looks stuck.
        assert queue_mod.scan_for_stuck_records(
            data["records"]) == []

    def test_recovery_mark_failed_exhausted_goes_to_dlq(self, tmp_path):
        store_dir = self._write_tasks(tmp_path, [
            {"id": "s9", "status": "running", "started_at": _TS,
             "retries": 4, "max_retries": 2, "last_error": "crash"},
        ])
        report = queue_mod.recover_stuck_records(
            store_dir, policy="mark_failed",
            reason="operator: never run again", now=_TS)
        assert report["recovered"][0]["action"] == "dead_letter"
        data = json.loads((tmp_path / "tasks.json").read_text())
        assert data["records"][0]["status"] == "dead_letter"
        assert "retries already exhausted" in \
            data["records"][0]["dead_letter_reason"]
        assert data["records"][0]["last_error"] == "crash"

    def test_recovery_rejects_unknown_policy(self, tmp_path):
        store_dir = self._write_tasks(tmp_path, [])
        with pytest.raises(ValueError):
            queue_mod.recover_stuck_records(store_dir, policy="delete")

    def test_recovery_missing_store_is_empty_report(self, tmp_path):
        report = queue_mod.recover_stuck_records(
            str(tmp_path / "empty-store"), policy="requeue",
            reason="test", now=_TS)
        assert report["found"] == [] and report["recovered"] == []

    def test_no_duplicate_execution_for_recovered_record(self, tmp_path):
        """A recovered record carries its old execution history
        unchanged — recovery appends no execution record, so the
        attempt is never counted twice."""
        rec = _record(id="s1", status="running", started_at=_TS,
                      retries=0, max_retries=2)
        _failed_executions(rec, "boom", 1)
        store_dir = self._write_tasks(tmp_path, [rec])
        queue_mod.recover_stuck_records(
            store_dir, policy="requeue", reason="test restart",
            now=_TS)
        data = json.loads((tmp_path / "tasks.json").read_text())
        recovered = data["records"][0]
        assert recovered["status"] == "queued"
        assert len(recovered["executions"]) == 1
        assert recovered["executions"][0]["attempt"] == 1
        assert recovered["executions"][0]["error"] == "boom"


# ------------------------------------------------------------ items 12-13
class TestItems12And13PermissionEnforcement:
    @pytest.mark.parametrize("action", [
        {"tool": "gmail_send", "action": "send"},
        {"tool": "n8n_trigger", "action": "send"},
        {"action": "send"},
        {"action": "publish"},
        {"action": "spend"},
        {"action": "delete"},
        {"action": "upload"},
        {"action": "book"},
        {"action": "pay"},
        {"action": "order"},
        {"action": "cancel"},
    ])
    def test_gated_actions_return_pending_approval(self, action):
        assert is_gated_action(action) is True
        verdict = enforce_gate(action)
        assert verdict["allowed"] is False
        assert verdict["status"] == "pending-approval"
        assert "gate word" in verdict["reason"]

    def test_commit_verb_on_ungated_tool_still_gated(self):
        # A "send" verb smuggled onto the draft tool must not slip
        # through the known-ungated-tool shortcut.
        assert is_gated_action(
            {"tool": "draft_email", "action": "send"}) is True

    def test_unknown_action_fails_closed(self):
        assert is_gated_action({"action": "teleport"}) is True
        assert is_gated_action({"action": "launch_missiles"}) is True
        verdict = enforce_gate({"action": "teleport"})
        assert verdict["allowed"] is False
        assert verdict["status"] == "pending-approval"

    @pytest.mark.parametrize("action", [
        {"tool": "draft_email", "action": "draft"},
        {"tool": "research_notes", "action": "draft"},
        {"tool": "draft_caption"},
        {"tool": "status_read"},
        {"action": "read"},
        {"action": "draft"},
        {"action": "search"},
        {"action": "list"},
        {"action": "status"},
    ])
    def test_ungated_draft_and_read_actions_allowed(self, action):
        assert is_gated_action(action) is False
        verdict = enforce_gate(action)
        assert verdict["allowed"] is True
        assert verdict["status"] == "allowed"

    def test_engine_never_executes_gated_step(self):
        result = WorkflowEngine().execute({"steps": [
            {"id": "draft-it", "kind": "draft", "input": {"x": 1}},
            {"id": "send-mail", "tool": "gmail_send", "action": "send",
             "input": {"to": "a@b.com"}},
            {"id": "spend-it", "action": "spend",
             "input": {"amount_usd": 5}},
        ]})
        assert result["status"] == "partial"
        by_id = {s["name"]: s for s in result["steps"]}
        assert by_id["draft-it"]["status"] == "ok"
        assert by_id["send-mail"]["status"] == "pending-approval"
        assert by_id["spend-it"]["status"] == "pending-approval"
        assert result["cost_usd"] == 0.0

    def test_permissions_table_denies_unassigned_tool(self):
        ok, reason = check_permission("OutreachDrafter", "gmail_send")
        assert ok is False and "not allowed" in reason
        ok, _ = check_permission("OutreachDrafter", "draft_email")
        assert ok is True
        # An unknown agent has no tools at all.
        assert allowed_tools("NoSuchAgent") == frozenset()
        assert allowed_tools(None) == frozenset()
        # The Chief may only REQUEST a gated tool — never execute it.
        ok, reason = check_permission("chief_of_staff_agency",
                                      "gmail_send")
        assert ok is True and "REQUEST" in reason

    def test_permissions_resolve_agent(self):
        assert resolve_agent({"agent": "OutreachDrafter"}) == \
            "OutreachDrafter"
        assert resolve_agent({"requested_by": "Main CEO Bot"}) == \
            "main_ceo_bot"
        assert resolve_agent({}) is None
        assert resolve_agent(None) is None

    def test_trust_gate_reads_free_commit_needs_words(self):
        cfg = {"spend_cap_usd": 0}
        assert trust_check("read", {}, config=cfg)["decision"] == "allow"
        assert trust_check("draft", {}, config=cfg)["decision"] == "allow"
        assert trust_check("send", {"to": "a@b.com"},
                           config=cfg)["decision"] == "ask"
        # Spend above the $0 cap is a hard deny.
        assert trust_check("spend", {"amount_usd": 5,
                                     "purpose": "ads"},
                           config=cfg)["decision"] == "deny"
        # Dental / medical is a hard DQ.
        assert trust_check("send", {"to": "x@dental.com"},
                           config=cfg)["decision"] == "deny"
        # An unverified quote is a deny, not an allow.
        d = trust_check("send", {"to": "a@b.com"},
                        owner_words=["Day 4 batch send"],
                        owner_source="Boss: today is off", config=cfg)
        assert d["decision"] == "deny"
        # A verified quote that covers the action allows.
        d = trust_check(
            "send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
            owner_words=["Day 4 batch send — email a@b.com"],
            owner_source="Boss (chat): Day 4 batch send — email a@b.com",
            config=cfg)
        assert d["decision"] == "allow"

    def test_gateway_rejects_wrong_gate_word_and_unknown_action(
            self, tmp_path):
        gw = ApprovalGateway(
            approvals_path=str(tmp_path / "approvals.json"))
        with pytest.raises(ValueError):
            gw.request("teleport", "not a gated action", "test")
        req = gw.request("send", "Day 4 batch - 25 emails",
                         "OutreachDrafter")
        assert req["status"] == "pending"
        assert gw.is_approved(req["id"]) is False
        with pytest.raises(ValueError):
            gw.approve(req["id"], gate_word="ok")
        assert gw.is_approved(req["id"]) is False
        approved = gw.approve(req["id"], gate_word="send",
                              decided_by="Boss")
        assert approved["status"] == "approved"
        assert approved["decided_by"] == "Boss"
        assert gw.is_approved(req["id"]) is True
        # An approved request cannot be decided twice.
        with pytest.raises(ValueError):
            gw.approve(req["id"], gate_word="send")

    def test_gateway_gate_words_match_trust_gate(self):
        # The two gate-word tables must stay identical (check_gate.py
        # verifies the same); a drift would let one gate allow what
        # the other blocks.
        from trust_gate import GATE_WORD_FOR_ACTION as TRUST_WORDS
        assert GATE_WORD_FOR_ACTION == TRUST_WORDS

    def test_confirmation_runs_once_and_never_reruns(self, tmp_path):
        store = ConfirmationStore(
            confirmations_path=str(tmp_path / "confirmations.json"),
            approvals_path=str(tmp_path / "approvals.json"))
        conf = store.create("send", {"to": "a@b.com", "subject": "Hi"},
                            "Send the Day 4 batch?", "Main CEO Bot")
        assert conf["status"] == "asked" and conf["approval_id"]
        # Not approved yet: execution is refused.
        with pytest.raises(ValueError):
            store.execute_once(conf["id"], lambda a: "sent")
        ran = []
        store.approve(conf["id"], gate_word="send")
        out = store.execute_once(conf["id"],
                                 lambda a: ran.append(a) or "sent-ok")
        assert out["status"] == "executed"
        assert ran == [{"subject": "Hi", "to": "a@b.com"}]
        with pytest.raises(ValueError):
            store.execute_once(conf["id"], lambda a: "again")


# ---------------------------------------------------------------- item 14
class TestItem14PolicyBasedExecution:
    def test_per_action_approval_flow_is_real(self, tmp_path):
        """What exists today: per-action approval through the
        gateway. A spend request stays pending until Boss's exact
        gate word ("go") approves it."""
        gw = ApprovalGateway(
            approvals_path=str(tmp_path / "approvals.json"))
        req = gw.request("spend", "test spend $5", "test")
        assert gw.pending()[0]["id"] == req["id"]
        with pytest.raises(ValueError):
            gw.approve(req["id"], gate_word="send")
        gw.approve(req["id"], gate_word="go", decided_by="Boss")
        assert gw.is_approved(req["id"]) is True

    def test_no_policy_engine_api_exists(self):
        """The bounded policy model was approved in principle, not
        built: the gateway exposes no policy evaluation, and no
        policy module exists to import."""
        import importlib.util
        assert importlib.util.find_spec("policy_engine") is None
        assert not hasattr(ApprovalGateway, "evaluate_policy")
        assert not hasattr(ApprovalGateway, "check_policy")
        assert not hasattr(ApprovalGateway, "policy")

    @pytest.mark.skip(reason="[NOT TESTED] Bounded policy-based "
                      "execution (pre-approved campaign policy: "
                      "audience, templates, volume, frequency, "
                      "restrictions) was approved in principle "
                      "2026-11-24 but NOT built — Phase 0 audit gap. "
                      "Only per-action gates exist (tested above). "
                      "Do not mistake the per-action approval flow "
                      "for the policy engine.")
    def test_policy_engine_execution(self):
        raise AssertionError("no policy engine to test")


# ---------------------------------------------------------------- item 15
class _FakeMockBrain:
    def complete(self, prompt):
        return "[MOCK] draft — live brain not working"

    def health(self):
        return {"provider": "mock"}


class _FakeProvider:
    def __init__(self, name, model, behaviour):
        self.name = name
        self.model = model
        self.behaviour = behaviour
        self.calls = 0

    def complete(self, prompt, *, max_tokens=500):
        self.calls += 1
        return self.behaviour(prompt)

    def health(self):
        return {"total_tokens": 5}


class TestItem15ProviderFailure:
    @pytest.fixture(autouse=True)
    def _isolate_call_log(self, tmp_path, monkeypatch):
        monkeypatch.setattr(free_only_guard, "LOG_PATH",
                            str(tmp_path / "dev_brain_calls.jsonl"))
        free_only_guard._CALL_LOG.clear()
        yield
        free_only_guard._CALL_LOG.clear()

    def test_free_only_allowlist(self):
        assert is_free_model("gemini", "gemini-2.5-flash-lite") is True
        assert is_free_model("gemini", "gemini-3.5-flash-lite") is True
        assert is_free_model("gemini-live", "gemini-2.0-flash") is True
        assert is_free_model("openrouter", "openrouter/free") is True
        assert is_free_model("openrouter", "x-ai/grok:free") is True
        assert is_free_model("openai", "gpt-4o") is False
        assert is_free_model("meta", "muse-spark-1.3") is False
        assert is_free_model("anthropic", "claude-sonnet-4-5") is False
        assert is_free_model("gemini", "gemini-1.5-pro") is False
        assert is_free_model("unknown-provider", "free-model") is False
        # Model ids are case-sensitive.
        assert is_free_model("gemini", "GEMINI-2.5-FLASH-LITE") is False
        assert check_call("gemini", "gemini-2.5-flash-lite") is True
        with pytest.raises(FreeOnlyViolation):
            check_call("openai", "gpt-4o")

    @pytest.mark.parametrize("exc,expected", [
        (urllib.error.HTTPError("http://x", 429, "Too Many Requests",
                                {}, None), True),
        (urllib.error.HTTPError("http://x", 401, "Unauthorized",
                                {}, None), False),
        (urllib.error.HTTPError("http://x", 403, "Forbidden",
                                {}, None), False),
        (TimeoutError("timed out"), False),
        (RuntimeError("live brain call failed: HTTP 429: boom"), True),
        (RuntimeError("live brain call failed: HTTP 401: bad key"), False),
        (RuntimeError("invalid_api_key"), False),
        (RuntimeError("rate limit exceeded"), True),
        (None, False),
    ])
    def test_rate_limit_detection(self, exc, expected):
        assert is_rate_limit_error(exc) is expected

    def test_dev_brain_free_provider_succeeds_live(self):
        good = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                             lambda p: "live answer")
        adapter = LiveBrainAdapter(_FakeMockBrain(),
                                   live_provider=good, mode="development")
        assert adapter.complete("hello") == "live answer"
        assert adapter.mode == "live"
        assert adapter.live_calls == 1
        assert adapter.last_failure is None
        assert good.calls == 1

    def test_dev_brain_paid_provider_never_called(self):
        paid = _FakeProvider("openai-live", "gpt-4o",
                             lambda p: "paid answer")
        adapter = LiveBrainAdapter(_FakeMockBrain(),
                                   live_provider=paid, mode="development")
        out = adapter.complete("hello")
        assert out.startswith("[MOCK]")
        assert paid.calls == 0  # blocked BEFORE any call
        assert adapter.mode == "mock-fallback"
        assert adapter.fallback_calls == 1
        assert "FreeOnlyViolation" in (adapter.last_failure or "")
        statuses = [r["status"] for r in free_only_guard.get_call_log()]
        assert statuses == ["blocked_free_only"]

    def test_dev_brain_429_is_a_hard_stop(self):
        def _boom_429(prompt):
            raise urllib.error.HTTPError("http://x", 429,
                                         "Too Many Requests", {}, None)
        first = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                              _boom_429)
        second = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                               lambda p: "second answer")
        adapter = LiveBrainAdapter(
            _FakeMockBrain(), live_providers=[first, second],
            mode="development")
        out = adapter.complete("hello")
        assert out.startswith("[MOCK]")
        assert first.calls == 1
        assert second.calls == 0  # hard stop: never tried
        assert adapter.rate_limited is True
        assert adapter.mode == "mock-fallback"
        statuses = [r["status"] for r in free_only_guard.get_call_log()]
        assert statuses == ["rate_limited_stop"]

    def test_dev_brain_timeout_falls_through_to_next_provider(self):
        def _boom_timeout(prompt):
            raise TimeoutError("timed out")
        first = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                              _boom_timeout)
        second = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                               lambda p: "second answer")
        adapter = LiveBrainAdapter(
            _FakeMockBrain(), live_providers=[first, second],
            mode="development")
        assert adapter.complete("hello") == "second answer"
        assert first.calls == 1 and second.calls == 1
        assert adapter.rate_limited is False
        assert adapter.mode == "live"

    def test_dev_brain_bad_key_error_prefixed_with_http_code(self):
        def _boom_401(prompt):
            raise RuntimeError(
                "live brain call failed: HTTP 401: bad API key")
        bad = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                            _boom_401)
        good = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                             lambda p: "good answer")
        adapter = LiveBrainAdapter(
            _FakeMockBrain(), live_providers=[bad, good],
            mode="development")
        assert adapter.complete("hello") == "good answer"
        # The 401 failure was logged as an error, not a rate stop.
        statuses = [r["status"] for r in free_only_guard.get_call_log()]
        assert statuses == ["error", "ok"]
        assert "HTTP 401" in free_only_guard.get_call_log()[0]["error"]

    def test_dev_brain_all_providers_fail_is_loud_fallback(self):
        def _boom(prompt):
            raise RuntimeError("connection refused")
        only = _FakeProvider("gemini-live", "gemini-2.5-flash-lite",
                             _boom)
        adapter = LiveBrainAdapter(_FakeMockBrain(),
                                   live_provider=only, mode="development")
        out = adapter.complete("hello")
        assert out.startswith("[MOCK]")
        assert adapter.last_failure is not None
        assert "RuntimeError" in adapter.last_failure
        assert adapter.health()["brain_kind"] == "development"
        assert adapter.health()["guard"] == "free-only"

    def test_log_call_never_writes_keys_or_tokens(self, tmp_path):
        log_path = tmp_path / "dev_brain_calls.jsonl"
        log_call({"provider": "gemini",
                  "model": "gemini-2.5-flash-lite", "status": "error",
                  "error": "boom", "usage": None,
                  "api_key": "sk-secret-value",
                  "token": "tok-secret-value"})
        line = log_path.read_text(encoding="utf-8")
        assert "sk-secret-value" not in line
        assert "tok-secret-value" not in line
        record = json.loads(line)
        assert record["provider"] == "gemini"
        assert record["status"] == "error"

    def test_real_gemini_provider_missing_key_raises_without_network(
            self, monkeypatch):
        """The real GeminiProvider: no key in the environment means
        complete() raises before any network I/O."""
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        provider = self._load_gemini_provider()
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
            provider.complete("hello")

    def test_real_gemini_provider_http_error_prefixed_with_code(
            self, monkeypatch):
        """The real GeminiProvider's except-block prefixes HTTP
        failures with 'HTTP <code>:' so the guard's 429 detection
        can see them. The HTTP layer is stubbed — no network."""
        monkeypatch.setenv("GEMINI_API_KEY", "test-key-never-sent")
        provider = self._load_gemini_provider()
        err = urllib.error.HTTPError("http://x", 429,
                                     "Too Many Requests", {}, None)

        class _FakeOpener:
            def open(self, req, timeout=None):
                raise err

        monkeypatch.setattr("urllib.request.build_opener",
                            lambda *a, **k: _FakeOpener())
        with pytest.raises(RuntimeError) as excinfo:
            provider.complete("hello")
        assert str(excinfo.value).startswith(
            "live brain call failed: HTTP 429:")
        assert is_rate_limit_error(excinfo.value) is True

    @staticmethod
    def _load_gemini_provider():
        """Load the real GeminiProvider by file path with a stubbed
        src.contracts.llm (avoids the vendored `src` package
        collision in-process). No network, no key read at import."""
        import importlib.util
        import types
        workers = os.path.join(REPO_ROOT, "01-Agency-Department",
                               "engine", "workers")
        stub_src = types.ModuleType("src")
        stub_src.__path__ = []
        stub_contracts = types.ModuleType("src.contracts")
        stub_contracts.__path__ = []
        stub_llm = types.ModuleType("src.contracts.llm")

        class LLMProvider:
            name = "llm"

            def complete(self, prompt, *, max_tokens=500):
                raise NotImplementedError

            def health(self):
                return {"provider": self.name}

        stub_llm.LLMProvider = LLMProvider
        # The stub lives in sys.modules ONLY while the module is
        # executed — leaving it there would poison any later test
        # that imports the real vendored `src` package (it broke
        # TestScenarioC). Restore the prior entries afterwards; the
        # loaded module keeps its own reference to the stub class.
        _keys = ("src", "src.contracts", "src.contracts.llm")
        _prior = {k: sys.modules.get(k) for k in _keys}
        sys.modules.setdefault("src", stub_src)
        sys.modules.setdefault("src.contracts", stub_contracts)
        sys.modules.setdefault("src.contracts.llm", stub_llm)
        path = os.path.join(workers, "src", "live",
                            "gemini_provider.py")
        spec = importlib.util.spec_from_file_location(
            "gemini_provider_real", path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        finally:
            for key in _keys:
                if _prior[key] is None:
                    sys.modules.pop(key, None)
                else:
                    sys.modules[key] = _prior[key]
        return module.GeminiProvider()


# ---------------------------------------------------------------- item 16
class TestItem16BudgetEnforcement:
    def test_zero_cap_any_paid_cost_exceeds(self):
        tracker = CostTracker(max_cost_usd=0.0)
        assert tracker.exceeded() is False
        assert tracker.record(0.0) == 0.0
        assert tracker.exceeded() is False
        tracker.record(0.01)
        assert tracker.exceeded() is True
        assert tracker.remaining() == pytest.approx(-0.01)

    def test_positive_cap_boundary(self):
        tracker = CostTracker(max_cost_usd=1.0)
        tracker.record(1.0)
        assert tracker.exceeded() is False  # strictly greater to exceed
        tracker.record(0.001)
        assert tracker.exceeded() is True

    def test_negative_cap_rejected(self):
        with pytest.raises(ValueError):
            CostTracker(max_cost_usd=-1.0)

    def test_runtime_limits_reject_negative_values(self):
        with pytest.raises(ValueError):
            RuntimeLimits(max_iterations=-1)
        with pytest.raises(ValueError):
            RuntimeLimits(wall_clock_seconds=-1.0)
        with pytest.raises(ValueError):
            RuntimeLimits(max_cost_usd=-0.01)
        # Zero limits are valid (a run that may do nothing).
        assert RuntimeLimits(max_iterations=0).max_iterations == 0

    def test_limit_exceeded_kinds(self):
        assert LimitExceeded("cost").kind == "cost"
        assert LimitExceeded("iterations").kind == "iterations"
        assert LimitExceeded("timeout").kind == "timeout"
        with pytest.raises(ValueError):
            LimitExceeded("unknown-kind")

    def test_engine_honours_iteration_cap(self):
        from agent_runtime.context import RuntimeContext
        from agent_runtime.limits import RuntimeLimits as Limits
        ctx = RuntimeContext({"title": "t"}, limits=Limits(
            max_iterations=1, wall_clock_seconds=60.0,
            max_cost_usd=0.0))
        result = WorkflowEngine().execute({"steps": [
            {"id": "one", "kind": "draft"},
            {"id": "two", "kind": "draft"},
            {"id": "three", "kind": "draft"},
        ]}, context=ctx)
        assert result["status"] == "partial"
        assert len(result["steps"]) == 1
        assert "iteration cap" in (result["error"] or "")


# ------------------------------------------- scheduler self-test regression
class TestSchedulerSelfTestRegression:
    def test_scheduler_self_test_passes(self):
        """Phase 7 known issue 1, fixed in Phase 8: the __main__
        self-test used to fail on its own forbidden-token literal.
        It now passes end to end (temp store only; real store read
        for a hash check, never written)."""
        proc = subprocess.run(
            [sys.executable, SCHEDULER_PATH],
            capture_output=True, text=True, timeout=120,
            cwd=REPO_ROOT)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert proc.stdout.startswith("scheduler: OK")

    def test_scan_still_detects_a_real_token(self):
        """Negative control for the fix: the same scan rules applied
        to a body that DOES contain a forbidden token must fail —
        the fix did not neuter the scan."""
        # The exact scan from the fixed self-test, on a planted body:
        planted = "def f():\n    import requests\n    return requests.get()\n"
        with pytest.raises(AssertionError):
            for token in ("requests.", "urllib", "http.client",
                          "socket.", "api_key"):
                assert token not in planted, \
                    f"forbidden token in source: {token}"

    def test_scan_key_pattern_ignores_job_id(self):
        """The 'sk-' false positive: the bare substring occurs in
        the legitimate job id 'daily-task-queue-drain-watch', so the
        fixed scan only flags a key-like pattern (sk- + 20 or more
        alphanumerics)."""
        body = '"id": "daily-task-queue-drain-watch",\n'
        assert "sk-" in body  # the old bare-substring check tripped here
        assert re.search(r"sk-[A-Za-z0-9]{20,}", body) is None
        assert re.search(r"sk-[A-Za-z0-9]{20,}",
                         "key = 'sk-abcdefghij1234567890'") is not None
