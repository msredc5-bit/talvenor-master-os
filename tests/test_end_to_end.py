"""Full end-to-end acceptance test (§21) — Talvenor Master OS, Phase 8.

One test runs the whole path in a temp store, $0, no live calls:
CEO route (run_office.run_one, lead_chain) -> departments
(department_runtime) -> workflows incl. n8n via the Phase 4 test
double (started on 127.0.0.1 in the test, never a real n8n) ->
dashboard sync (sync_status record-level readers over the temp
store's records) -> CEO report from the saved records.

The dashboard leg is honest about its boundary: sync_status
.collect_status() is repo-root bound (it reads the real store), so
the e2e asserts the record-level readers (read_task_counts /
read_approvals_detail) over temp-store records plus the temp
control state — the full-repo collect is covered by Phase 7's
check_phase7, not re-run here against the real store.
"""
import copy
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

from ceo_reporting.report import generate_report
from control import ControlState
from department_runtime import execute_department_task
from lead_chain.fixtures import STRONG_TIER1_PROSPECT
from workflow_engine.n8n_adapter import N8nAdapter
from workflow_engine.test_double import N8nTestDouble

REPO_ROOT = Path(__file__).resolve().parents[1]
END = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)


def _load_run_office():
    spec = importlib.util.spec_from_file_location(
        "run_office_under_test", REPO_ROOT / "scripts" / "run_office.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_sync_status():
    spec = importlib.util.spec_from_file_location(
        "sync_status_under_test", REPO_ROOT / "scripts" / "sync_status.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_full_end_to_end_acceptance(tmp_path):
    store = tmp_path / "store"
    store.mkdir()

    # 1. CEO route: a lead-chain task through run_office.run_one.
    run_office = _load_run_office()
    ceo_result = run_office.run_one(
        "agency", "lead_chain",
        {"title": "TEST e2e lead chain",
         "prospect": copy.deepcopy(STRONG_TIER1_PROSPECT)},
        str(store))
    assert ceo_result["status"] == "blocked"  # deployment always blocked
    assert ceo_result["cost_usd"] == 0.0
    assert ceo_result["routed_to"] == "00-CEO-Core.lead_chain.ChainRunner"

    # 2. Departments: research executes its real workflow, $0.
    dept = execute_department_task(
        "05-research-strategy",
        {"id": "TEST-E2E-1", "title": "TEST e2e research",
         "type": "research"})
    assert dept["status"] in ("executed", "executed-partial"), dept
    assert dept["cost_usd"] == 0.0

    # 3. Workflows via n8n — the Phase 4 test double on 127.0.0.1.
    with N8nTestDouble() as double:
        adapter = N8nAdapter(base_url=double.base_url)
        assert adapter.list_workflows() == {"data": []}
        created = adapter.create_workflow({
            "name": "TEST e2e workflow", "nodes": [], "connections": {}})
        assert created["id"]
        listed = adapter.list_workflows()
        assert len(listed["data"]) == 1
        assert listed["data"][0]["name"] == "TEST e2e workflow"
        assert listed["data"][0]["id"] == created["id"]

    # 4. Dashboard sync (record-level readers over temp-store records).
    sync_status = _load_sync_status()
    tasks = json.loads((store / "tasks.json").read_text())["records"]
    task_counts = sync_status.read_task_counts(tasks)
    assert task_counts["total"] == 1
    assert task_counts["blocked"] == 1
    assert sync_status.read_approvals_detail([])["pending"] == []
    # Control state for the temp store: running (nothing paused).
    assert ControlState(
        control_path=str(store / "control.json")).is_halted() is False

    # 5. CEO report from the actual saved execution records.
    rep = generate_report(str(store), "weekly", end=END)
    assert rep["tasks"]["total"] == 1
    assert rep["tasks"]["executions_cost_usd"] == 0.0
    assert rep["lead_chain"]["total_runs"] == 1
    assert rep["lead_chain"]["by_status"] == {"blocked": 1}
    assert len(rep["departments"]["departments"]) == 8
    assert rep["usage"]["total_calls"] == "unknown"  # no ledger seeded
