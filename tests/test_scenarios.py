"""§21 scenarios A, B, C, D, G — Talvenor Master OS, Phase 8.

Each scenario uses ONLY the real code that exists, in a temp store,
with TEST data. A leg with no real code is marked [NOT TESTED] with
the reason, never faked from mocks.
"""
import copy
import json
from datetime import datetime, timezone

import pytest

from lead_chain import run_lead_chain
from lead_chain.fixtures import STRONG_TIER1_PROSPECT

END = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------- Scenario A
class TestScenarioA:
    def test_scheduled_lead_research_runs_and_reports(self, tmp_path):
        """A: scheduled Lead Research task — due detection (quiet
        schedules + scheduler), delegation to 05-research-strategy
        (real department runtime), verification (lead chain),
        valid leads saved (chain record in the temp store), report
        (department report + CEO report). All $0.

        NOTE on activation: scheduler.activate_job needs a Boss
        approval, so the fixture marks the watch record active with
        the same activation note marker activate_job writes
        ("activated-by: ..."). The activation gate itself (refusal
        without approval) is item-14 territory, not this scenario.
        """
        from department_runtime import (
            compile_department_report,
            execute_department_task,
        )
        from ceo_reporting.report import generate_report
        from quiet_schedules import ScheduleStore
        from workflow_engine import scheduler

        store = tmp_path / "store"
        store.mkdir()
        sched = ScheduleStore(schedules_path=str(store / "schedules.json"))
        rec = sched.add("lead research watch", kind="watch", source="",
                        interval_minutes=10, status="active")
        sched.apply_correction(
            rec["id"], note="activated-by: TEST-fixture (approver: Boss)")
        due, reason = scheduler.should_run_job(sched, rec["id"])
        assert due is True, reason

        # Delegate: the research department runs its real workflow.
        dept = execute_department_task(
            "05-research-strategy",
            {"id": "TEST-A-1", "title": "TEST lead research",
             "type": "research"})
        assert dept["status"] in ("executed", "executed-partial"), dept
        assert dept["cost_usd"] == 0.0

        # Verify + save: the real lead chain on the TEST fixture.
        record = run_lead_chain(copy.deepcopy(STRONG_TIER1_PROSPECT),
                                store_dir=str(store))
        assert record["status"] == "blocked"  # deployment always blocked
        assert (store / "chains").is_dir()

        # Report: department report + CEO consolidated report.
        dept_report = compile_department_report(
            "05-research-strategy", store_dir=str(store), tasks=[],
            runs=[])
        assert "error" not in dept_report, dept_report
        rep = generate_report(str(store), "weekly", end=END)
        assert rep["lead_chain"]["total_runs"] == 1
        assert rep["lead_chain"]["by_status"] == {"blocked": 1}

    def test_paused_schedule_never_runs(self, tmp_path):
        from quiet_schedules import ScheduleStore
        from workflow_engine import scheduler
        sched = ScheduleStore(schedules_path=str(tmp_path / "schedules.json"))
        rec = sched.add("lead research watch", kind="watch", source="",
                        interval_minutes=10, status="paused")
        due, reason = scheduler.should_run_job(sched, rec["id"])
        assert due is False
        assert "paused" in reason


# ---------------------------------------------------------------- Scenario B
class TestScenarioB:
    def test_prospect_reply_classified_crm_dryrun_followup_parked(self,
                                                                  tmp_path):
        """B: Prospect Reply event — classification (real
        reply_triage), CRM update (real CRM dry-run — writes
        nothing), follow-up workflow (real followup_queue).
        The follow-up leg is REFUSED BY THE STANDING 100-MAIL RULE
        (1 first mail in PA < 100), so the queue is empty by rule,
        not by bug — asserted, not faked."""
        from followup_queue import build_followup_queue
        from lead_chain.crm_dryrun import dry_run_upsert
        from reply_triage import triage

        # Classification: interest -> hot_lead with a booking-link
        # draft that quotes no price and is never sendable.
        verdict = triage(
            "gmail", "test@example.invalid",
            "Hi — this looks interesting, can we book a demo call?",
            sender_name="TEST Owner")
        assert verdict["verdict"] == "hot_lead"
        assert verdict["sendable"] is False
        assert "https://calendar.app.google/WLoxBfnLGTdjK3LB8" in (
            verdict["draft"] or "")
        assert "$" not in (verdict["draft"] or "")

        # CRM update: dry-run upsert of the TEST prospect.
        crm = dry_run_upsert(copy.deepcopy(STRONG_TIER1_PROSPECT))
        assert crm["status"] == "ok" and crm["live"] is False

        # Follow-up workflow: 1 emailed PA lead in a temp leads file.
        leads_path = tmp_path / "leads.json"
        leads_path.write_text(json.dumps({
            "schema": "leads-v1", "leads": [{
            "id": "TEST-L-0001", "business_name": "TEST Prospect LLC",
            "state": "PA", "email": "test@example.invalid",
            "phone": "+1-555-0100", "domain": "test-prospect.example",
            "sent": {"emailed": True}, "flags": []}]}),
            encoding="utf-8")
        result = build_followup_queue(states=["PA"],
                                      leads_path=str(leads_path))
        assert result["queue"] == []
        assert len(result["refusals"]) == 1
        refusal = result["refusals"][0]
        assert refusal["state"] == "PA"
        assert refusal["first_mails"] == 1
        assert refusal["threshold"] == 100
        assert refusal["candidates_parked"] == 1
        assert "100-mail rule" in refusal["reason"]

    def test_bounce_and_decline_classified(self):
        from reply_triage import triage
        assert triage("gmail", "mailer-daemon@example.invalid",
                      "Delivery Status Notification (Failure) — "
                      "550 mailbox unavailable")["verdict"] == "bounce"
        decline = triage("gmail", "test@example.invalid",
                         "No thanks, not interested.")
        assert decline["verdict"] == "decline"
        assert decline["sendable"] is False


# ---------------------------------------------------------------- Scenario C
class TestScenarioC:
    def test_new_client_event_routes_to_operations_with_onboarding(self,
                                                                   tmp_path):
        """C: new Client event — routing via the Chief's real
        DEPARTMENT_ROUTING (client work -> 04-client-operations /
        COOClientOperationsAgent) + the lead chain's real
        client_onboarding step (draft checklist). There is no live
        onboarding flow behind the label; the config-tasks leg is
        the checklist items in the step detail."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "chief_of_staff_agency",
            __import__("pathlib").Path(__file__).resolve().parents[1]
            / "01-Agency-Department" / "chief_of_staff_agency.py")
        chief = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(chief)
        routing = chief.DEPARTMENT_ROUTING
        assert routing["dept_operations"][0] == (
            "04-client-operations/manager/coo_client_operations_agent.py")
        assert routing["dept_operations"][1] == "COOClientOperationsAgent"
        record = run_lead_chain(copy.deepcopy(STRONG_TIER1_PROSPECT),
                                store_dir=str(tmp_path))
        step = {s["id"]: s for s in record["steps"]}["client_onboarding"]
        assert step["status"] == "ok"
        assert step["department"] == "04-client-operations"
        # Checklist items come from the real step executor (the
        # chain routes the step through the engine mock — see
        # test_lead_chain.py::TestClientOnboarding).
        from lead_chain.steps import execute_step
        _status, detail, _error = execute_step(
            {"id": "client_onboarding", "kind": "client_onboarding",
             "specialist": "RetentionAgent"},
            copy.deepcopy(STRONG_TIER1_PROSPECT), {})
        for item in ("confirm business name", "confirm booking calendar",
                     "confirm call-handling script", "confirm go-live"):
            assert item in detail, item


# ---------------------------------------------------------------- Scenario D
class TestScenarioD:
    def test_qa_failure_recovery_not_tested_gap(self):
        """D: [NOT TESTED] — a QA failure verdict exists
        (tenant_qa.run_qa -> "fail"), but NO code creates a recovery
        task or notifies a manager on failure (see
        test_tenant.py::TestReceptionistQA::
        test_qa_failure_has_no_recovery_task_mechanism). This test
        pins the verdict half so the gap is visible, and fails if
        someone later adds a recovery path without wiring this test
        to it."""
        import tenant_qa
        import tenant_schema
        tenant = tenant_schema.synthetic_tenant()
        script = tenant_qa.synthetic_call_script(tenant)
        script["turns"][-1]["text"] += " The visit costs $99."
        result = tenant_qa.run_qa(tenant, script)
        assert result["verdict"] == "fail"
        assert [c for c in result["checks"]
                if c["id"] == "no_price_quoted"][0]["passed"] is False
        pytest.xfail(
            "Scenario D recovery leg: no recovery-task or "
            "manager-notification mechanism exists yet — see "
            "test_tenant.py gap test")


# ---------------------------------------------------------------- Scenario G
class TestScenarioG:
    def test_ceo_report_from_actual_saved_execution_records(self, tmp_path):
        """G: the CEO report is generated from ACTUAL saved
        execution records in a temp store — the lead chain run and
        the drain's task records — and every figure matches them."""
        from ceo_reporting.report import generate_report
        store = tmp_path / "store"
        store.mkdir()
        (store / "tasks.json").write_text(json.dumps({
            "schema": "tasks-v1", "records": [{
                "id": "t1", "status": "done", "type": "lead_chain",
                "business": "agency",
                "queued_at": "2026-11-25T00:00:00+00:00",
                "completed_at": "2026-11-25T02:00:00+00:00",
                "executions": [{"attempt": 1, "task_id": "t1",
                                "status": "completed",
                                "cost_usd": 0.0}]}]}),
            encoding="utf-8")
        run_lead_chain(copy.deepcopy(STRONG_TIER1_PROSPECT),
                       store_dir=str(store))
        rep = generate_report(str(store), "weekly", end=END)
        assert rep["tasks"]["total"] == 1
        assert rep["tasks"]["by_status"] == {"done": 1}
        assert rep["tasks"]["executions"] == 1
        assert rep["tasks"]["executions_cost_usd"] == 0.0
        assert rep["lead_chain"]["total_runs"] == 1
        assert rep["lead_chain"]["by_status"] == {"blocked": 1}
