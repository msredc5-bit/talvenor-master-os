"""§21 items 22 (CEO consolidated reporting) + Scenario G —
Talvenor Master OS, Phase 8.

Real code under test: 00-CEO-Core/ceo_reporting/report.py.
Every figure is asserted against a seeded temp store; a missing
source must read "unknown", never an invented number.
"""
import json
from datetime import datetime, timezone

from ceo_reporting.report import UNKNOWN, generate_report, render_markdown

END = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)


def _seed_store(store_dir):
    """Seed a temp store with KNOWN records (2 tasks, 1 approval,
    1 usage line, memory, 1 schedule). Returns the seed dict."""
    store_dir.mkdir(parents=True, exist_ok=True)
    tasks = {"schema": "tasks-v1", "records": [
        {"id": "t1", "status": "queued", "type": "research",
         "business": "agency",
         "queued_at": "2026-11-25T00:00:00+00:00"},
        {"id": "t2", "status": "done", "type": "draft",
         "business": "agency",
         "queued_at": "2026-11-25T01:00:00+00:00",
         "completed_at": "2026-11-25T02:00:00+00:00",
         "executions": [{"attempt": 1, "task_id": "t2",
                         "status": "completed", "cost_usd": 0.0}]},
    ]}
    approvals = {"schema": "approvals-v1", "records": [
        {"id": "a1", "status": "pending", "action": "send_email",
         "detail": "test send",
         "requested_at": "2026-11-24T12:00:00+00:00"},
    ]}
    usage = {"schema": "usage-ledger-v1", "monthly_cap_usd": 0.0,
             "records": [
                 {"id": "000001", "at": "2026-11-25T03:00:00+00:00",
                  "kind": "mock", "cost_usd": 0.0}]}
    memory = {"schema": "owner-memory-v1", "entries": [{}],
              "boxes": ["shared"]}
    schedules = {"schema": "schedules-v1", "records": [
        {"id": "s1", "status": "paused", "name": "taskboard-queue-watch"},
    ]}
    for name, payload in (("tasks.json", tasks),
                          ("approvals.json", approvals),
                          ("usage_ledger.json", usage),
                          ("memory.json", memory),
                          ("schedules.json", schedules)):
        (store_dir / name).write_text(json.dumps(payload), encoding="utf-8")
    return {"tasks": tasks, "approvals": approvals, "usage": usage}


class TestCEOReporting:
    def test_every_figure_matches_the_seed(self, tmp_path):
        store = tmp_path / "store"
        _seed_store(store)
        rep = generate_report(str(store), "weekly", end=END)
        assert rep["tasks"]["total"] == 2
        assert rep["tasks"]["by_status"] == {"done": 1, "queued": 1}
        assert rep["tasks"]["in_window"] == 2
        assert rep["tasks"]["executions"] == 1
        assert rep["tasks"]["executions_cost_usd"] == 0.0
        assert rep["approvals"]["total"] == 1
        assert rep["approvals"]["pending"] == 1
        assert rep["approvals"]["pending_list"][0]["id"] == "a1"
        assert rep["approvals"]["oldest_pending_age"] == "1d 0h"
        assert rep["usage"]["total_calls"] == 1
        assert rep["usage"]["total_usd"] == 0.0
        assert rep["usage"]["over_monthly_cap"] is False
        assert rep["memory"]["entries"] == 1
        assert rep["memory"]["boxes"] == 1
        assert rep["schedules"]["total"] == 1
        assert len(rep["departments"]["departments"]) == 8
        md = render_markdown(rep)
        assert "## Tasks" in md and "a1" in md and "$0.00" in md

    def test_lead_chain_runs_counted_from_real_chain_records(self, tmp_path):
        """Seed the store by RUNNING the real lead chain into it,
        then assert the report counts the real chain record."""
        from lead_chain import run_lead_chain
        from lead_chain.fixtures import STRONG_TIER1_PROSPECT
        import copy
        store = tmp_path / "store"
        _seed_store(store)
        record = run_lead_chain(copy.deepcopy(STRONG_TIER1_PROSPECT),
                                store_dir=str(store))
        assert record["status"] == "blocked"
        rep = generate_report(str(store), "weekly", end=END)
        assert rep["lead_chain"]["total_runs"] == 1
        assert rep["lead_chain"]["by_status"] == {"blocked": 1}
        assert rep["lead_chain"]["log_lines"] == 1

    def test_empty_store_reads_unknown_never_invented(self, tmp_path):
        store = tmp_path / "empty-store"
        store.mkdir()
        rep = generate_report(str(store), "daily", end=END)
        assert rep["tasks"]["status"] == "missing"
        assert rep["tasks"]["total"] == UNKNOWN
        assert rep["approvals"]["total"] == UNKNOWN
        assert rep["usage"]["total_calls"] == UNKNOWN
        assert rep["lead_chain"]["total_runs"] == 0
        assert rep["lead_chain"]["status"] == "missing"
        md = render_markdown(rep)
        assert "unknown" in md
        # No invented totals anywhere in the summary.
        assert not any("2 task(s)" in line
                       for line in rep["executive_summary"])

    def test_unknown_period_rejected(self, tmp_path):
        store = tmp_path / "store"
        _seed_store(store)
        import pytest
        with pytest.raises(ValueError):
            generate_report(str(store), "yearly", end=END)

    def test_report_is_read_only_on_the_store(self, tmp_path):
        store = tmp_path / "store"
        _seed_store(store)
        before = {p.name: p.read_bytes() for p in store.iterdir()}
        generate_report(str(store), "weekly", end=END)
        after = {p.name: p.read_bytes() for p in store.iterdir()}
        assert before == after
