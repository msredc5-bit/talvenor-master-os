"""§21 item 24 (Audit logging) — Talvenor Master OS, Phase 8.

Real code under test: 00-CEO-Core/audit.py (audit_log / read_audit)
and scripts/run_office.py (drain writes task_transition +
control_halt lines to store/audit.log).

Note on the Phase 0 audit's "store/audit.log does NOT exist": the
log file is created lazily by the first audit_log() call — it does
not exist until something is audited. That is the real behaviour
and is asserted here (missing file reads as empty, not an error).
"""
import json

from audit import audit_log, read_audit


class TestAuditLogging:
    def test_missing_log_reads_empty_not_error(self, tmp_path):
        records, skipped = read_audit(
            audit_path=str(tmp_path / "audit.log"))
        assert records == [] and skipped == 0

    def test_append_only_json_lines_with_timestamp(self, tmp_path):
        path = str(tmp_path / "audit.log")
        assert audit_log("gate_decision",
                         {"tool": "gmail_send",
                          "status": "pending-approval"},
                         audit_path=path) is True
        assert audit_log("task_transition",
                         {"task_id": "abc", "to": "done"},
                         audit_path=path) is True
        records, skipped = read_audit(audit_path=path)
        assert len(records) == 2 and skipped == 0
        assert records[0]["event"] == "gate_decision"
        assert records[1]["to"] == "done"
        assert all("ts" in r for r in records)
        lines = (tmp_path / "audit.log").read_text(
            encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        assert all(json.loads(line) for line in lines)

    def test_corrupt_line_is_skipped_and_counted(self, tmp_path):
        path = tmp_path / "audit.log"
        audit_log("gate_decision", {"tool": "x"}, audit_path=str(path))
        with open(path, "a", encoding="utf-8") as f:
            f.write("{not json\n")
        audit_log("task_transition", {"to": "done"}, audit_path=str(path))
        records, skipped = read_audit(audit_path=str(path))
        assert len(records) == 2
        assert skipped == 1

    def test_failed_write_returns_false_never_raises(self, tmp_path):
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        assert audit_log("x", {},
                         audit_path=str(blocker / "audit.log")) is False

    def test_drain_writes_task_transition_lines(self, tmp_path):
        """The drain (run_office.drain_queue) appends one
        task_transition per processed task to the temp store's
        audit.log — the audit trail is real, not a fixture."""
        import importlib.util
        from pathlib import Path
        spec = importlib.util.spec_from_file_location(
            "run_office_under_test",
            Path(__file__).resolve().parents[1] / "scripts" / "run_office.py")
        run_office = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_office)
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
        records, _skipped = read_audit(
            audit_path=str(store / "audit.log"))
        events = [r["event"] for r in records]
        assert "task_transition" in events
