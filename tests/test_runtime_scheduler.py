"""§21 items 4–8 (Agent execution loop, subagent delegation, task
creation, task persistence, scheduler execution) — Talvenor Master OS,
Phase 8, Worker A.

Real code under test:
  00-CEO-Core/agent_runtime/{loop,context,limits,subagents,delegation,
  runner}.py, scripts/run_office.py (build_task), 00-CEO-Core/store_io.py,
  00-CEO-Core/workflow_engine/scheduler.py + quiet_schedules.py.

Every test uses a fresh tmp_path store dir; the real store/ is never
written (the autouse guard fixture refuses any store_io write aimed
at it, and the skill-execution log is redirected to tmp). No network,
no live LLM calls, mock/dev brain only, $0 everywhere. No time.sleep
dependence — timeouts are enforced with 0-second budgets or a short
future timeout against a waiting thread.
"""
import json
import os
import threading

import pytest

import skill_finder
import store_io
from agent_runtime import (
    AgentRuntime,
    BoundedLoop,
    RuntimeContext,
    RuntimeLimits,
)
from agent_runtime.delegation import DelegationEngine, decompose_task
from agent_runtime.subagents import (
    SubagentManager,
    SubagentSpec,
    run_parallel,
    validate_result,
)

REPO_ROOT = skill_finder._MASTER_OS_DIR


# --------------------------------------------------------------------------
# Isolation guards (local to this file — the shared conftest belongs to
# Worker C and is left untouched).
# --------------------------------------------------------------------------
def _is_real_store_path(path):
    real = os.path.realpath(os.path.join(REPO_ROOT, "store"))
    return os.path.realpath(str(path)).startswith(real + os.sep)


@pytest.fixture(autouse=True)
def _redirect_skill_log(tmp_path, monkeypatch):
    monkeypatch.setattr(
        skill_finder, "LOG_PATH", str(tmp_path / "skill_executions.jsonl"))


@pytest.fixture(autouse=True)
def _guard_real_store(monkeypatch):
    """Refuse any store_io / ScheduleStore write aimed at the real store/."""
    orig_write = store_io.write_json_atomic
    orig_update = store_io.update_json
    orig_append = store_io.append_json_line

    def _checked_write(path, payload):
        assert not _is_real_store_path(path), \
            f"test tried to write the REAL store: {path}"
        return orig_write(path, payload)

    def _checked_update(path, fn, default=None):
        assert not _is_real_store_path(path), \
            f"test tried to update the REAL store: {path}"
        return orig_update(path, fn, default=default)

    def _checked_append(path, record):
        assert not _is_real_store_path(path), \
            f"test tried to append to the REAL store: {path}"
        return orig_append(path, record)

    monkeypatch.setattr(store_io, "write_json_atomic", _checked_write)
    monkeypatch.setattr(store_io, "update_json", _checked_update)
    monkeypatch.setattr(store_io, "append_json_line", _checked_append)

    from quiet_schedules import ScheduleStore

    orig_save = ScheduleStore._save

    def _checked_save(self):
        assert not _is_real_store_path(self.schedules_path), \
            f"test tried to write the REAL store: {self.schedules_path}"
        return orig_save(self)

    monkeypatch.setattr(ScheduleStore, "_save", _checked_save)


@pytest.fixture
def temp_store(tmp_path):
    """A fresh, empty store dir for this test only."""
    store = tmp_path / "store"
    store.mkdir()
    return store


@pytest.fixture
def temp_schedule_store(temp_store):
    from quiet_schedules import ScheduleStore

    return ScheduleStore(str(temp_store / "schedules.json"))


@pytest.fixture
def run_office():
    import run_office as _run_office

    return _run_office


def _ctx(task=None, **limits):
    return RuntimeContext(task or {"id": "t1"}, RuntimeLimits(**limits))


# ---------------------------------------------------------------- item 4 — loop
class TestBoundedLoop:
    def test_step_done_completes(self):
        result = BoundedLoop().run(
            lambda c: {"status": "done", "output": "ok", "cost_usd": 0.0},
            _ctx())
        assert result.status == "completed"
        assert result.output == "ok"
        assert result.iterations == 1
        assert result.cost_usd == 0.0
        assert result.error is None

    def test_iteration_cap_enforced(self):
        result = BoundedLoop().run(
            lambda c: {"status": "continue", "cost_usd": 0.0},
            _ctx(max_iterations=3))
        assert result.status == "iteration_limit"
        assert result.iterations == 3
        assert "3" in (result.error or "")

    def test_zero_wall_clock_budget_times_out_immediately(self):
        calls = []

        def _step(c):
            calls.append(1)
            return {"status": "done", "output": "never"}

        result = BoundedLoop().run(_step, _ctx(wall_clock_seconds=0.0))
        assert result.status == "timeout"
        assert result.iterations == 0
        assert calls == [], "timed-out loop must not run any step"

    def test_cost_over_zero_cap_ends_cost_limit(self):
        # A "done" step that reports paid cost must end cost_limit,
        # never "completed" — the $0 cap is hard.
        result = BoundedLoop().run(
            lambda c: {"status": "done", "output": "x", "cost_usd": 1.0},
            _ctx(max_cost_usd=0.0))
        assert result.status == "cost_limit"
        assert result.cost_usd == 1.0

    def test_raising_step_ends_error_without_crashing_caller(self):
        def _boom(c):
            raise RuntimeError("boom")

        result = BoundedLoop().run(_boom, _ctx())
        assert result.status == "error"
        assert "RuntimeError: boom" in (result.error or "")
        assert result.iterations == 0

    def test_step_reporting_error_status(self):
        result = BoundedLoop().run(
            lambda c: {"status": "error", "error": "step failed"},
            _ctx())
        assert result.status == "error"
        assert result.error == "step failed"

    def test_non_dict_step_result_ends_error(self):
        result = BoundedLoop().run(lambda c: "not-a-dict", _ctx())
        assert result.status == "error"
        assert "must return a dict" in (result.error or "")

    def test_negative_cost_ends_error(self):
        result = BoundedLoop().run(
            lambda c: {"status": "done", "cost_usd": -1.0}, _ctx())
        assert result.status == "error"
        assert "must not be negative" in (result.error or "")

    def test_unknown_step_status_ends_error(self):
        result = BoundedLoop().run(
            lambda c: {"status": "teleport"}, _ctx())
        assert result.status == "error"
        assert "unknown step status" in (result.error or "")

    def test_trace_records_each_step(self):
        def _step(c):
            if c.iteration == 0:
                return {"status": "continue", "output": "first"}
            return {"status": "done", "output": "second"}

        result = BoundedLoop().run(_step, _ctx())
        assert result.status == "completed"
        assert result.iterations == 2
        assert len(result.trace) >= 2


# --------------------------------------------------- item 5 — subagents + delegation
class TestSubagents:
    def test_spawn_ok_result_matches_contract(self):
        mgr = SubagentManager()
        parent = _ctx()

        def _work(child, data):
            return {"name": "w", "status": "ok", "output": data * 2,
                    "evidence": ["did it"], "cost_usd": 0.0}

        result = mgr.spawn(SubagentSpec("w", _work), 21, parent)
        assert validate_result(result) is True
        assert set(result) == {"name", "status", "output", "evidence",
                               "cost_usd"}
        assert result["status"] == "ok" and result["output"] == 42

    def test_spawn_plain_value_becomes_ok_output(self):
        mgr = SubagentManager()
        result = mgr.spawn(
            SubagentSpec("plain", lambda c, d: "hello"), None, _ctx())
        assert result["status"] == "ok"
        assert result["output"] == "hello"

    def test_spawn_raising_fn_returns_error_not_exception(self):
        mgr = SubagentManager()

        def _boom(child, data):
            raise ValueError("kaboom")

        result = mgr.spawn(SubagentSpec("boom", _boom), None, _ctx())
        assert result["status"] == "error"
        assert "ValueError: kaboom" in str(result["output"])

    def test_spawn_overrun_returns_timeout(self):
        mgr = SubagentManager()
        started = threading.Event()

        def _slow(child, data):
            started.set()
            threading.Event().wait(2.0)  # never finishes in time
            return {"status": "ok", "output": "late"}

        result = mgr.spawn(SubagentSpec("slow", _slow, timeout_seconds=0.2),
                           None, _ctx())
        assert result["status"] == "timeout"
        assert started.is_set()

    def test_spawn_invalid_result_becomes_error(self):
        mgr = SubagentManager()

        def _bad(child, data):
            return {"status": "bogus", "output": None}

        result = mgr.spawn(SubagentSpec("bad", _bad), None, _ctx())
        assert result["status"] == "error"
        assert "Invalid subagent result" in str(result["output"])

    def test_run_parallel_keeps_input_order_and_isolates_contexts(self):
        parent = _ctx({"id": "parent-task", "note": "keep"})
        parent.log_step("setup", "done", "parent trace")

        def _work(child, data):
            # Mutate ONLY the child: trace + cost must not leak.
            child.log_step("child", "done", data)
            child.cost_usd = 5.0
            return {"name": "x", "status": "ok",
                    "output": len(child.trace),
                    "evidence": [f"data={data}"], "cost_usd": 0.0}

        specs = [SubagentSpec(f"s{i}", _work) for i in range(3)]
        results = run_parallel(specs, ["a", "b", "c"], parent)
        assert [r["name"] for r in results] == ["s0", "s1", "s2"]
        assert all(r["status"] == "ok" for r in results)
        # Each child saw the parent's 1 trace entry + its own 1.
        assert [r["output"] for r in results] == [2, 2, 2]
        # Parent untouched by every child.
        assert len(parent.trace) == 1
        assert parent.cost_usd == 0.0
        assert parent.task == {"id": "parent-task", "note": "keep"}

    def test_run_parallel_one_failure_does_not_fail_batch(self):
        def _ok(child, data):
            return {"status": "ok", "output": data}

        def _fail(child, data):
            raise RuntimeError("one fails")

        results = run_parallel(
            [SubagentSpec("ok", _ok), SubagentSpec("fail", _fail),
             SubagentSpec("ok2", _ok)],
            [1, 2, 3], _ctx())
        assert [r["status"] for r in results] == ["ok", "error", "ok"]

    def test_run_parallel_empty_returns_empty(self):
        assert run_parallel([], [], _ctx()) == []

    def test_run_parallel_mismatched_lengths_raises(self):
        with pytest.raises(ValueError):
            run_parallel([SubagentSpec("a", lambda c, d: None)], [], _ctx())

    def test_validate_result_rejects_bad_results(self):
        good = {"name": "n", "status": "ok", "output": None,
                "evidence": [], "cost_usd": 0.0}
        assert validate_result(good) is True
        for bad in (
            {"status": "ok", "output": None, "evidence": [], "cost_usd": 0.0},
            {**good, "extra": 1},
            {**good, "status": "maybe"},
            {**good, "evidence": "not-a-list"},
            {**good, "cost_usd": "free"},
            {**good, "name": 7},
            "not-a-dict",
        ):
            with pytest.raises(ValueError):
                validate_result(bad)


class TestDelegation:
    def test_decompose_steps_list(self):
        steps = decompose_task({"id": "t",
                                "steps": [{"name": "a"}, {"kind": "b"}]})
        assert [s["name"] for s in steps] == ["a", "step-1"]
        assert steps[1]["kind"] == "b"

    def test_decompose_single_step_task(self):
        steps = decompose_task({"id": "solo"})
        assert steps == [{"name": "solo", "kind": "default",
                          "input": {"id": "solo"}}]

    def test_decompose_non_dict_task_raises(self):
        with pytest.raises(ValueError):
            decompose_task("not-a-dict")

    def test_execute_completed_all_steps_ok(self):
        engine = DelegationEngine()
        out = engine.execute(
            {"id": "t", "steps": [{"name": "research"}, {"name": "draft"}]},
            _ctx())
        assert out["status"] == "completed"
        assert len(out["steps"]) == 2
        assert all(s["status"] == "ok" for s in out["steps"])
        assert out["cost_usd"] == 0.0
        assert all("DRAFT" in str(s["output"]) for s in out["steps"])

    def test_execute_decompose_failure_returns_error_dict(self):
        engine = DelegationEngine()
        out = engine.execute({"id": "t", "steps": "not-a-list"}, _ctx())
        assert out["status"] == "error"
        assert out["steps"] == []
        assert out["cost_usd"] == 0.0

    def test_execute_partial_when_a_step_result_is_invalid(self):
        class _MixedManager:
            def run_parallel(self, specs, inputs, parent):
                return [
                    {"name": specs[0].name, "status": "ok",
                     "output": "fine", "evidence": [], "cost_usd": 0.0},
                    {"name": specs[1].name, "status": "error",
                     "output": "step broke", "evidence": [],
                     "cost_usd": 0.0},
                ]

        engine = DelegationEngine(manager=_MixedManager())
        out = engine.execute(
            {"id": "t", "steps": [{"name": "good"}, {"name": "bad"}]},
            _ctx())
        assert out["status"] == "partial"
        assert [s["status"] for s in out["steps"]] == ["ok", "error"]


class TestRunner:
    def test_run_task_mock_step_is_draft_only(self):
        result = AgentRuntime().run_task({"id": "t1", "type": "draft"})
        assert result.status == "completed"
        assert result.output["mock_brain"] is True
        assert result.output["draft_only"] is True
        assert result.output["task_id"] == "t1"
        assert result.cost_usd == 0.0

    def test_run_task_with_skill_query_loads_skill_read_only(self):
        result = AgentRuntime().run_task(
            {"id": "t2", "skill_query": "backup"})
        assert result.status == "completed"
        assert result.output["skill_loaded"] is True
        assert result.output["skill"] == "backup-recovery-agent"

    def test_run_task_delegates_multi_step_task(self):
        result = AgentRuntime().run_task(
            {"id": "t3", "steps": [{"name": "a"}, {"name": "b"}]},
            delegate=True)
        assert result.status == "completed"
        assert result.output["status"] == "completed"
        assert result.iterations == 2
        assert result.cost_usd == 0.0

    def test_run_task_single_step_falls_back_to_loop(self):
        result = AgentRuntime().run_task({"id": "t4"}, delegate=True)
        assert result.status == "completed"
        assert result.output["mock_brain"] is True


# ------------------------------------------------------------ item 6 — task creation
class TestTaskCreation:
    def test_build_task_produces_valid_tasks_v1_record(self, run_office):
        task = run_office.build_task(
            "agency", "caption_write",
            {"title": "Caption for Monday reel", "payload": {"tone": "plain"}})
        assert task["business"] == "agency"
        assert task["type"] == "caption_write"
        assert task["title"] == "Caption for Monday reel"
        assert task["payload"] == {"tone": "plain"}
        # tasks-v1 queue fields are filled by normalize_task_record.
        record = run_office.normalize_task_record(dict(task))
        for field in ("priority", "depends_on", "retries", "max_retries",
                      "cancelled", "idempotency_key", "last_error"):
            assert field in record, field
        assert record["depends_on"] == []
        assert record["cancelled"] is False

    def test_build_task_defaults_title(self, run_office):
        task = run_office.build_task("content", "script_write", {})
        assert task["title"] == "content script_write"
        assert task["payload"] == {}

    def test_build_task_forwards_gated_fields(self, run_office):
        task = run_office.build_task(
            "agency", "outreach_draft",
            {"title": "Send Day 4 batch", "gated_action": "send",
             "requested_by": "Boss"})
        assert task["gated_action"] == "send"
        assert task["requested_by"] == "Boss"

    def test_build_task_lead_chain_forwards_prospect(self, run_office):
        prospect = {"name": "Test Plumbing", "email": "a@example.com"}
        task = run_office.build_task(
            "agency", "lead_chain", {"prospect": prospect})
        assert task["prospect"] == prospect

    def test_build_task_find_skill_forwards_query(self, run_office):
        task = run_office.build_task(
            "agency", "find_skill", {"query": "backup"})
        assert task["query"] == "backup"

    def test_parse_input_rejects_non_object_json(self, run_office):
        with pytest.raises(ValueError):
            run_office.parse_input('["not", "an", "object"]')


# ---------------------------------------------------------- item 7 — persistence
class TestTaskPersistence:
    def test_atomic_write_rereads_identically(self, temp_store):
        path = temp_store / "tasks.json"
        payload = {"schema": "tasks-v1", "records": [
            {"id": "t1", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "T", "payload": {}}]}
        store_io.write_json_atomic(str(path), payload)
        assert store_io.read_json(str(path)) == payload

    def test_atomic_write_leaves_no_stray_temp_files(self, temp_store):
        path = temp_store / "tasks.json"
        store_io.write_json_atomic(str(path), {"schema": "tasks-v1",
                                              "records": []})
        assert list(temp_store.glob(".store-tmp-*")) == []
        assert path.is_file()

    def test_update_json_locked_roundtrip_keeps_records(self, temp_store):
        path = str(temp_store / "tasks.json")
        store_io.write_json_atomic(path, {"schema": "tasks-v1",
                                         "records": [{"id": "t1"}]})

        def _add(data):
            data["records"].append({"id": "t2"})
            return data

        out = store_io.update_json(path, _add)
        assert [r["id"] for r in out["records"]] == ["t1", "t2"]
        assert [r["id"] for r in
                store_io.read_json(path)["records"]] == ["t1", "t2"]

    def test_missing_file_returns_default(self, temp_store):
        assert store_io.read_json(str(temp_store / "nope.json"),
                                  default={"x": 1}) == {"x": 1}

    def test_corrupt_json_raises_instead_of_empty(self, temp_store):
        path = temp_store / "bad.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            store_io.read_json(str(path))

    def test_run_office_task_file_roundtrip(self, temp_store, run_office):
        """The tasks-v1 file run_office writes re-reads identically,
        through its own helpers."""
        path = str(temp_store / "tasks.json")
        record = run_office.normalize_task_record(
            run_office.build_task("agency", "caption_write",
                                  {"title": "T", "payload": {}}))
        record.update({"id": "task-1", "status": "queued"})
        run_office._write_store_tasks(path, [record])
        back = run_office._read_store_tasks(path)
        assert back == [record]

    def test_json_lines_append_and_read(self, temp_store):
        path = str(temp_store / "audit.log")
        store_io.append_json_line(path, {"event": "a", "n": 1})
        store_io.append_json_line(path, {"event": "b", "n": 2})
        records, skipped = store_io.read_json_lines(path)
        assert skipped == 0
        assert [r["event"] for r in records] == ["a", "b"]


# ------------------------------------------------------------ item 8 — scheduler
class TestScheduler:
    def test_job_definitions_exist_and_validate(self):
        from workflow_engine.scheduler import (
            job_definitions,
            validate_job_definitions,
        )

        jobs = job_definitions()
        assert len(jobs) == 4, jobs
        assert {j["id"] for j in jobs} == {
            "daily-task-queue-drain-watch",
            "daily-approval-queue-watch",
            "weekly-ceo-report",
            "monthly-ledger-usage-summary",
        }
        assert validate_job_definitions() is True
        assert validate_job_definitions(jobs) is True
        # Deep copies: mutating the returned list must not corrupt the table.
        jobs[0]["id"] = "tampered"
        assert job_definitions()[0]["id"] != "tampered"

    def test_create_paused_jobs_all_paused_and_idempotent(
            self, temp_schedule_store):
        from workflow_engine.scheduler import create_paused_jobs

        out = create_paused_jobs(temp_schedule_store)
        assert len(out["created"]) == 4
        assert out["existing"] == []
        assert all(r["status"] == "paused"
                   for r in temp_schedule_store.list())
        out2 = create_paused_jobs(temp_schedule_store)
        assert out2["created"] == []
        assert len(out2["existing"]) == 4
        assert len(temp_schedule_store.list()) == 4

    def test_paused_job_is_never_due(self, temp_schedule_store):
        from workflow_engine.scheduler import (
            create_paused_jobs,
            due_jobs,
            should_run_job,
        )

        create_paused_jobs(temp_schedule_store)
        for row in due_jobs(temp_schedule_store):
            assert row["due"] is False, row
            assert "paused" in row["reason"], row
        due, reason = should_run_job(temp_schedule_store,
                                     "weekly-ceo-report")
        assert due is False
        assert "paused" in reason

    def test_activate_without_valid_approval_refused(
            self, temp_schedule_store):
        from workflow_engine.scheduler import (
            ActivationRefused,
            activate_job,
            create_paused_jobs,
            is_activated,
        )

        create_paused_jobs(temp_schedule_store)
        bad_approvals = [
            None,
            {"approval_id": "a1", "approver": "Someone",
             "decision": "approved",
             "scope": "scheduler-activation:weekly-ceo-report"},
            {"approval_id": "a1", "approver": "Boss",
             "decision": "rejected",
             "scope": "scheduler-activation:weekly-ceo-report"},
            {"approval_id": "a1", "approver": "Boss",
             "decision": "approved",
             "scope": "scheduler-activation:other-job"},
            {"approver": "Boss", "decision": "approved",
             "scope": "scheduler-activation:weekly-ceo-report"},
        ]
        for approval in bad_approvals:
            with pytest.raises(ActivationRefused):
                activate_job(temp_schedule_store, "weekly-ceo-report",
                             approval=approval)
        record = next(r for r in temp_schedule_store.list()
                      if r["name"].startswith("Weekly CEO"))
        assert record["status"] == "paused"
        assert is_activated(record) is False

    def test_activate_with_valid_boss_approval(self, temp_schedule_store):
        from workflow_engine.scheduler import (
            activate_job,
            create_paused_jobs,
            is_activated,
            should_run_job,
        )

        create_paused_jobs(temp_schedule_store)
        approval = {"approval_id": "boss-approval-1", "approver": "Boss",
                    "decision": "approved",
                    "scope": "scheduler-activation:weekly-ceo-report"}
        record = activate_job(temp_schedule_store, "weekly-ceo-report",
                              approval=approval)
        assert record["status"] == "active"
        assert is_activated(record) is True
        assert "boss-approval-1" in record["note"]
        # First run after activation: no marker yet, so it is due.
        due, reason = should_run_job(temp_schedule_store,
                                     "weekly-ceo-report")
        assert due is True, reason
        assert "first run" in reason

    def test_resume_never_activated_job_refused(self, temp_schedule_store):
        from workflow_engine.scheduler import (
            ActivationRefused,
            create_paused_jobs,
            resume_job,
        )

        create_paused_jobs(temp_schedule_store)
        with pytest.raises(ActivationRefused):
            resume_job(temp_schedule_store, "weekly-ceo-report")
        record = next(r for r in temp_schedule_store.list()
                      if r["name"].startswith("Weekly CEO"))
        assert record["status"] == "paused"

    def test_pause_then_resume_activated_job(self, temp_schedule_store):
        from workflow_engine.scheduler import (
            activate_job,
            create_paused_jobs,
            pause_job,
            resume_job,
        )

        create_paused_jobs(temp_schedule_store)
        approval = {"approval_id": "boss-approval-2", "approver": "Boss",
                    "decision": "approved",
                    "scope": "scheduler-activation:weekly-ceo-report"}
        activate_job(temp_schedule_store, "weekly-ceo-report",
                     approval=approval)
        assert pause_job(temp_schedule_store,
                         "weekly-ceo-report")["status"] == "paused"
        assert resume_job(temp_schedule_store,
                          "weekly-ceo-report")["status"] == "active"

    def test_activation_refused_while_control_paused(
            self, temp_store, temp_schedule_store):
        from control import ControlState
        from workflow_engine.scheduler import (
            ActivationRefused,
            activate_job,
            create_paused_jobs,
        )

        create_paused_jobs(temp_schedule_store)
        control = ControlState(str(temp_store / "control.json"))
        control.pause("phase8 test pause")
        approval = {"approval_id": "boss-approval-3", "approver": "Boss",
                    "decision": "approved",
                    "scope": "scheduler-activation:weekly-ceo-report"}
        with pytest.raises(ActivationRefused) as exc:
            activate_job(temp_schedule_store, "weekly-ceo-report",
                         approval=approval)
        assert "control" in str(exc.value).lower()
        control.resume("phase8 test resume")
        record = activate_job(temp_schedule_store, "weekly-ceo-report",
                              approval=approval)
        assert record["status"] == "active"

    def test_validate_approval_cases(self):
        from workflow_engine.scheduler import validate_approval

        scope = "scheduler-activation:weekly-ceo-report"
        good = {"approval_id": "a1", "approver": "Md Mainuddin",
                "decision": "approved", "scope": scope}
        assert validate_approval(good, scope)[0] is True
        assert validate_approval(None, scope)[0] is False
        assert validate_approval("not-a-dict", scope)[0] is False
        assert validate_approval({**good, "decision": "pending"},
                                 scope)[0] is False
        assert validate_approval({**good, "scope": scope + "-extra"},
                                 scope)[0] is False
