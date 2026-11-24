"""§21 item 23 (Dashboard pause and emergency stop) — Talvenor Master
OS, Phase 8.

Real code under test: 00-CEO-Core/control.py (ControlState /
consult), 00-CEO-Core/approval_centre.py (real ApprovalGateway),
scripts/run_office.py drain_queue() (control consult halts the
drain), scripts/sync_status.py read_control() (dashboard badge
source). All state in tmp_path; the real store is never touched.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from approval_centre import ApprovalCentre
from control import (
    ControlCorruptError,
    ControlRefused,
    ControlState,
    consult,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_run_office():
    spec = importlib.util.spec_from_file_location(
        "run_office_under_test", REPO_ROOT / "scripts" / "run_office.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestControlPlane:
    def test_missing_file_loads_as_running(self, tmp_path):
        cs = ControlState(control_path=str(tmp_path / "control.json"))
        assert cs.is_halted() is False
        assert cs.halt_reason() is None
        assert cs.load()["state"] == "running"
        assert consult(str(tmp_path / "control.json")) == (False, None)

    def test_pause_halts_and_resume_restores(self, tmp_path):
        path = str(tmp_path / "control.json")
        cs = ControlState(control_path=path)
        cs.pause("hold the queue", set_by="Boss")
        assert cs.is_halted() is True
        assert cs.load()["state"] == "paused"
        assert consult(path)[0] is True
        assert consult(path)[1].startswith("paused: hold the queue")
        cs.resume("back to work", set_by="Boss")
        assert cs.is_halted() is False
        assert cs.load()["state"] == "running"

    def test_emergency_stop_survives_resume(self, tmp_path):
        path = str(tmp_path / "control.json")
        cs = ControlState(control_path=path)
        cs.pause("hold", set_by="Boss")
        cs.emergency_stop("stop everything", set_by="Boss")
        assert cs.load()["state"] == "emergency_stop"
        with pytest.raises(ControlRefused):
            cs.resume("try to resume", set_by="Boss")
        assert cs.is_halted() is True
        assert cs.load()["emergency_stop"] is True
        assert cs.load()["paused"] is True  # stop did not clear pause

    def test_clear_emergency_stop_needs_a_reason(self, tmp_path):
        path = str(tmp_path / "control.json")
        cs = ControlState(control_path=path)
        cs.emergency_stop("stop", set_by="Boss")
        for bad in (None, "", "   "):
            with pytest.raises(ValueError):
                cs.clear_emergency_stop(bad, set_by="Boss")
        assert cs.load()["emergency_stop"] is True
        cs.clear_emergency_stop("all clear", set_by="Boss")
        assert cs.load()["emergency_stop"] is False
        cs.resume("back to work", set_by="Boss")
        assert cs.is_halted() is False

    def test_corrupt_file_fails_closed(self, tmp_path):
        path = tmp_path / "control.json"
        path.write_text("{not json", encoding="utf-8")
        cs = ControlState(control_path=str(path))
        with pytest.raises(ControlCorruptError):
            cs.load()
        with pytest.raises(ControlCorruptError):
            consult(str(path))
        # Wrong-schema payload is corrupt too, never "running".
        path.write_text(json.dumps({"schema": "other-v9"}), encoding="utf-8")
        with pytest.raises(ControlCorruptError):
            cs.load()

    def test_history_capped_at_100_with_drops_counted(self, tmp_path):
        cs = ControlState(control_path=str(tmp_path / "control.json"))
        for i in range(105):
            cs.pause("pause %d" % i, set_by="Boss")
        loaded = cs.load()
        assert len(loaded["history"]) == 100
        assert loaded["history_dropped"] >= 5
        assert loaded["history"][-1]["reason"] == "pause 104"


class TestApprovalCentreRoutesViaRealGateway:
    def test_request_approve_reject_round_trip(self, tmp_path):
        centre = ApprovalCentre(
            approvals_path=str(tmp_path / "approvals.json"))
        req = centre.request_approval("send", "test request", "check")
        assert req["status"] == "pending"
        pending = centre.list_pending()
        assert len(pending) == 1 and pending[0]["id"] == req["id"]
        assert pending[0]["allowed_gate_words"] == ["send", "পাঠাও"]
        assert pending[0]["expired"] is False
        with pytest.raises(ValueError):
            centre.decide(req["id"], "approve", gate_word="ok")
        out = centre.decide(req["id"], "approve", gate_word="send")
        assert out["status"] == "approved"
        assert out["decided_by"] == "Boss"
        assert centre.list_pending() == []
        req2 = centre.request_approval("publish", "test 2", "check")
        assert centre.decide(req2["id"], "reject")["status"] == "rejected"
        with pytest.raises(ValueError):
            centre.decide(req2["id"], "maybe")

    def test_centre_never_writes_approvals_json_directly(self, tmp_path):
        # The centre's only writer is the gateway: the file the
        # centre produces must be readable back through the gateway.
        centre = ApprovalCentre(
            approvals_path=str(tmp_path / "approvals.json"))
        req = centre.request_approval("send", "x", "check")
        centre.decide(req["id"], "approve", gate_word="send")
        from human_approval_gateway import ApprovalGateway
        gw = ApprovalGateway(
            approvals_path=str(tmp_path / "approvals.json"))
        assert gw.records[0]["status"] == "approved"


class TestControlCLI:
    """scripts/control.py — thin CLI over the real ControlState
    (Phase 8 candidate fix for the Phase 7 remaining task)."""

    def _run_cli(self, *argv):
        import subprocess
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "control.py"),
             *argv],
            capture_output=True, text=True, timeout=60)

    def test_cli_status_pause_resume_round_trip(self, tmp_path):
        path = str(tmp_path / "control.json")
        out = self._run_cli("--control-path", path, "status")
        assert out.returncode == 0
        assert "state: running" in out.stdout
        out = self._run_cli("--control-path", path, "pause",
                            "--reason", "hold the queue")
        assert out.returncode == 0
        assert "state: paused" in out.stdout
        out = self._run_cli("--control-path", path, "resume",
                            "--reason", "back to work")
        assert out.returncode == 0
        assert "state: running" in out.stdout
        # The CLI wrote the real control file, not a copy.
        assert ControlState(control_path=path).is_halted() is False

    def test_cli_emergency_stop_refuses_resume(self, tmp_path):
        path = str(tmp_path / "control.json")
        assert self._run_cli("--control-path", path, "emergency-stop",
                             "--reason", "stop everything").returncode == 0
        out = self._run_cli("--control-path", path, "resume",
                            "--reason", "try")
        assert out.returncode == 4
        assert "REFUSED" in out.stderr
        assert ControlState(control_path=path).is_halted() is True
        out = self._run_cli("--control-path", path, "clear",
                            "--reason", "all clear")
        assert out.returncode == 0
        assert ControlState(control_path=path).is_halted() is False

    def test_cli_corrupt_file_exits_fail_closed(self, tmp_path):
        path = tmp_path / "control.json"
        path.write_text("{not json", encoding="utf-8")
        out = self._run_cli("--control-path", str(path), "status")
        assert out.returncode == 3
        assert "CORRUPT" in out.stderr
        assert path.read_text(encoding="utf-8") == "{not json"

    def test_cli_clear_needs_a_reason(self, tmp_path):
        path = str(tmp_path / "control.json")
        self._run_cli("--control-path", path, "emergency-stop",
                      "--reason", "stop")
        out = self._run_cli("--control-path", path, "clear",
                            "--reason", "   ")
        assert out.returncode == 2


class TestDrainAndSchedulerHalt:
    def test_paused_control_halts_drain_nothing_runs(self, tmp_path):
        run_office = _load_run_office()
        store = tmp_path / "store"
        store.mkdir()
        (store / "tasks.json").write_text(json.dumps({
            "schema": "tasks-v1", "records": [{
                "id": "t1", "status": "queued", "type": "lead_chain",
                "business": "agency", "title": "TEST lead chain",
                "prospect": "strong_tier1",
                "queued_at": "2026-11-25T00:00:00+00:00"}]}),
            encoding="utf-8")
        ControlState(control_path=str(store / "control.json")).pause(
            "test pause", set_by="Boss")
        summary = run_office.drain_queue(str(store), max_tasks=5)
        assert summary["halted"] is True
        assert summary["processed"] == []
        tasks = json.loads((store / "tasks.json").read_text())
        assert tasks["records"][0]["status"] == "queued"  # untouched
        audit = (store / "audit.log").read_text(encoding="utf-8")
        assert "control_halt" in audit

    def test_running_control_drains_lead_chain_task(self, tmp_path):
        run_office = _load_run_office()
        store = tmp_path / "store"
        store.mkdir()
        (store / "tasks.json").write_text(json.dumps({
            "schema": "tasks-v1", "records": [{
                "id": "t1", "status": "queued", "type": "lead_chain",
                "business": "agency", "title": "TEST lead chain",
                "prospect": "strong_tier1",
                "queued_at": "2026-11-25T00:00:00+00:00"}]}),
            encoding="utf-8")
        summary = run_office.drain_queue(str(store), max_tasks=1)
        assert summary["halted"] is False
        tasks = json.loads((store / "tasks.json").read_text())
        # The lead chain ends "blocked" at deployment (sandbox) —
        # the drain records that terminal status, $0.
        assert tasks["records"][0]["status"] in ("blocked", "done")
        assert (store / "chains").is_dir()

    def test_scheduler_reports_no_job_due_while_paused(self, tmp_path):
        from quiet_schedules import ScheduleStore
        from workflow_engine import scheduler
        store = ScheduleStore(
            schedules_path=str(tmp_path / "schedules.json"))
        rec = store.add("lead research watch", kind="watch",
                        source="", interval_minutes=10, status="active")
        # Fixture activation marker, mirroring activate_job's note
        # ("activated-by: <id> (approver: ...)"); the activation
        # gate itself (refusal without a Boss approval) is item-14
        # territory, not this test.
        store.apply_correction(
            rec["id"], note="activated-by: TEST-fixture (approver: Boss)")
        # No source -> due once on first run (control running).
        due, _reason = scheduler.should_run_job(store, rec["id"])
        assert due is True
        # The scheduler consults control.json next to schedules.json.
        ControlState(control_path=str(tmp_path / "control.json")).pause(
            "test pause", set_by="Boss")
        due, reason = scheduler.should_run_job(store, rec["id"])
        assert due is False
        assert "control halted" in reason
        assert scheduler.due_jobs(store)[0]["due"] is False
