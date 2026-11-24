"""Shared department runtime — Talvenor Master OS, local-first Phase 5.

The one place where a department manager's DRAFT becomes an
EXECUTED workflow run through the shared infrastructure:

  Chief of Staff (DEPARTMENT_ROUTING branch, "execute": True)
    -> execute_department_task(department_id, manager_task, manager_result)
    -> AgentRuntime (Phase 3, bounded loop, $0) runs the department's
       workflows/*.json through the Phase 4 workflow engine, behind
       the Phase 3 gate. A gated step comes back "pending-approval"
       and NEVER executes — that is the designed outcome, recorded
       as "executed-partial", not a failure.

Also in this module:

  * load_department_workflow(department_id) — first workflows/*.json
    (sorted), parsed + validated (dict with a "steps" list).
  * compile_department_report(department_id, store_dir, tasks, runs)
    — loads the department's reports/report.py with importlib and
    calls its compile_report(store_dir=..., tasks=..., runs=...).

Rules (hard):
  * Stdlib only. No network, no send, no publish, no spend, no
    delete, no live calls, no keys.
  * execute_department_task() and compile_department_report()
    NEVER raise — they return an "error" result instead, so a
    missing module, a bad workflow, or a broken report can never
    break Chief routing.
  * The 00-CEO-Core import is lazy (added to sys.path inside this
    module, same pattern the managers use). A missing AgentRuntime
    degrades to an "error" result.
  * Execution records reuse the Phase 4 queue shape:
    {"attempt", "task_id", "started_at", "finished_at", "status",
    "error", "cost_usd"} — status here is one of
    "completed" | "partial" | "error".
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import uuid
from datetime import datetime, timezone

__all__ = [
    "load_department_workflow",
    "execute_department_task",
    "compile_department_report",
]

DEPARTMENTS_DIR = os.path.dirname(os.path.abspath(__file__))
CEO_CORE_DIR = os.path.normpath(os.path.join(
    DEPARTMENTS_DIR, "..", "..", "00-CEO-Core"))

_RUNTIME_CLASS = None
_RUNTIME_ERROR = None


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _ensure_ceo_core_on_path():
    if CEO_CORE_DIR not in sys.path:
        sys.path.insert(0, CEO_CORE_DIR)


def _load_runtime_class():
    """Lazily import AgentRuntime (Phase 3). Cached; a missing
    import degrades gracefully — returns (None, error string)."""
    global _RUNTIME_CLASS, _RUNTIME_ERROR
    if _RUNTIME_CLASS is not None:
        return _RUNTIME_CLASS, None
    if _RUNTIME_ERROR is not None:
        return None, _RUNTIME_ERROR
    _ensure_ceo_core_on_path()
    try:
        from agent_runtime import AgentRuntime  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001 — degrade, never raise
        _RUNTIME_ERROR = f"{type(exc).__name__}: {exc}"
        return None, _RUNTIME_ERROR
    _RUNTIME_CLASS = AgentRuntime
    return _RUNTIME_CLASS, None


def load_department_workflow(department_id):
    """Load a department's workflow: the first workflows/*.json
    (sorted) under departments/<department_id>/.

    Returns the workflow dict. Raises ValueError with a clear
    message when the folder / file is missing, the JSON does not
    parse, or the content is not a dict with a "steps" list.
    department_id is the folder name, e.g. "01-sales-growth".
    """
    if not isinstance(department_id, str) or not department_id.strip():
        raise ValueError(
            "load_department_workflow needs a non-empty department_id "
            "string (the department folder name, e.g. "
            "'01-sales-growth')")
    department_id = department_id.strip()
    workflows_dir = os.path.join(DEPARTMENTS_DIR, department_id,
                                 "workflows")
    try:
        names = sorted(n for n in os.listdir(workflows_dir)
                       if n.endswith(".json"))
    except OSError as exc:
        raise ValueError(
            f"department {department_id!r} has no workflows/ folder "
            f"({type(exc).__name__}: {exc})") from exc
    if not names:
        raise ValueError(
            f"department {department_id!r} has no workflows/*.json")
    path = os.path.join(workflows_dir, names[0])
    try:
        with open(path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"department {department_id!r} workflow {names[0]!r} "
            f"could not be read/parsed "
            f"({type(exc).__name__}: {exc})") from exc
    if not isinstance(workflow, dict):
        raise ValueError(
            f"department {department_id!r} workflow {names[0]!r} "
            f"must be a JSON object, got {type(workflow).__name__}")
    steps = workflow.get("steps")
    if not isinstance(steps, list):
        raise ValueError(
            f"department {department_id!r} workflow {names[0]!r} "
            "must have a 'steps' list")
    return workflow


def _error_result(department_id, workflow_name, task_id, started_at,
                  error, execution=None):
    """Build the "error" return shape (never raises)."""
    finished_at = _now_iso()
    return {
        "status": "error",
        "department": department_id,
        "workflow": workflow_name,
        "execution": execution if isinstance(execution, dict) else {
            "status": "error", "steps": [], "cost_usd": 0.0,
            "error": error},
        "iterations": 0,
        "cost_usd": 0.0,
        "error": error,
        "execution_record": {
            "attempt": 1,
            "task_id": task_id,
            "started_at": started_at,
            "finished_at": finished_at,
            "status": "error",
            "error": error,
            "cost_usd": 0.0,
        },
    }


def execute_department_task(department_id, task, manager_result=None):
    """Run a department manager's draft task through the shared
    runtime + workflow engine. NEVER raises.

    task: the manager's task dict (title / type / payload).
    manager_result: the manager's result dict (advisory only today
    — the workflow, not the manager output, is what executes).

    Returns {"status", "department", "workflow", "execution",
    "iterations", "cost_usd", "error", "execution_record"} where
    status is "executed" (runtime completed), "executed-partial"
    (a gated step came back pending-approval — the designed
    outcome, the gated step NEVER executed), or "error".
    """
    started_at = _now_iso()
    dept = (department_id if isinstance(department_id, str)
            and department_id.strip() else "unknown-department")
    task = task if isinstance(task, dict) else {}
    task_id = task.get("id") or uuid.uuid4().hex[:12]
    title = task.get("title") or f"{dept} department task"
    try:
        workflow = load_department_workflow(dept)
    except ValueError as exc:
        return _error_result(dept, None, task_id, started_at, str(exc))
    except Exception as exc:  # noqa: BLE001 — never raise
        return _error_result(
            dept, None, task_id, started_at,
            f"{type(exc).__name__}: {exc}")
    workflow_name = workflow.get("name") or dept
    runtime_cls, runtime_error = _load_runtime_class()
    if runtime_cls is None:
        return _error_result(
            dept, workflow_name, task_id, started_at,
            "AgentRuntime unavailable: "
            + (runtime_error or "unknown import error"))
    runtime_task = {
        "title": title,
        "type": "dept_execute",
        "workflow": workflow,
    }
    try:
        run_result = runtime_cls().run_task(runtime_task)
    except Exception as exc:  # noqa: BLE001 — never raise
        return _error_result(
            dept, workflow_name, task_id, started_at,
            f"{type(exc).__name__}: {exc}")
    try:
        execution = run_result.output
        if not isinstance(execution, dict):
            execution = {"status": "error", "steps": [],
                         "cost_usd": 0.0,
                         "error": "runtime returned a non-dict output"}
        steps = execution.get("steps")
        if not isinstance(steps, list):
            steps = []
        pending = [str(s.get("name") or s.get("id") or "?")
                   for s in steps if isinstance(s, dict)
                   and s.get("status") == "pending-approval"]
        try:
            cost = float(getattr(run_result, "cost_usd", 0.0) or 0.0)
        except (TypeError, ValueError):
            cost = 0.0
        try:
            iterations = int(getattr(run_result, "iterations", 0) or 0)
        except (TypeError, ValueError):
            iterations = len(steps)
        raw_status = str(getattr(run_result, "status", "error"))
        error = getattr(run_result, "error", None)
        if raw_status == "completed":
            status, record_status = "executed", "completed"
            error = None
        elif pending:
            # Engine "partial" (runtime coerces it to "error") caused
            # by a gated step: the designed outcome — the gated step
            # NEVER executed. Recorded as executed-partial, not a
            # failure.
            status, record_status = "executed-partial", "partial"
            error = error or ("workflow partial: pending-approval: "
                              + ", ".join(pending))
        else:
            status, record_status = "error", "error"
            error = error or execution.get("error") or (
                "workflow error: failed steps: "
                + ", ".join(str(s.get("name") or s.get("id") or "?")
                            for s in steps
                            if isinstance(s, dict)
                            and s.get("status") == "error"))
        return {
            "status": status,
            "department": dept,
            "workflow": workflow_name,
            "execution": execution,
            "iterations": iterations,
            "cost_usd": cost,
            "error": error,
            "execution_record": {
                "attempt": 1,
                "task_id": task_id,
                "started_at": started_at,
                "finished_at": _now_iso(),
                "status": record_status,
                "error": error,
                "cost_usd": cost,
            },
        }
    except Exception as exc:  # noqa: BLE001 — never raise
        return _error_result(
            dept, workflow_name, task_id, started_at,
            f"{type(exc).__name__}: {exc}")


def compile_department_report(department_id, store_dir=None, tasks=None,
                              runs=None):
    """Compile a department's report via its reports/report.py.
    NEVER raises — any failure returns
    {"department": ..., "error": "<Type>: <msg>"}.

    The report module's compile_report(store_dir=..., tasks=...,
    runs=...) is called with keyword arguments; the returned dict
    is passed through unchanged (it already carries "department").
    """
    dept = (department_id if isinstance(department_id, str)
            and department_id.strip() else "unknown-department")
    try:
        report_path = os.path.join(DEPARTMENTS_DIR, dept, "reports",
                                   "report.py")
        if not os.path.isfile(report_path):
            return {"department": dept,
                    "error": "FileNotFoundError: no reports/report.py "
                             f"for department {dept!r}"}
        spec = importlib.util.spec_from_file_location(
            f"dept_report_{dept.replace('-', '_')}", report_path)
        if spec is None or spec.loader is None:
            return {"department": dept,
                    "error": "ImportError: could not load "
                             f"reports/report.py for {dept!r}"}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        compile_report = getattr(mod, "compile_report", None)
        if not callable(compile_report):
            return {"department": dept,
                    "error": "AttributeError: reports/report.py for "
                             f"{dept!r} has no compile_report()"}
        result = compile_report(store_dir=store_dir, tasks=tasks,
                                runs=runs)
        if not isinstance(result, dict):
            return {"department": dept,
                    "error": "TypeError: compile_report() for "
                             f"{dept!r} returned "
                             f"{type(result).__name__}, not a dict"}
        return result
    except Exception as exc:  # noqa: BLE001 — never raise
        return {"department": dept,
                "error": f"{type(exc).__name__}: {exc}"}


if __name__ == "__main__":
    # Self-test — in-memory only (reads the 01-sales-growth
    # workflow file; writes nothing, no live calls, $0).
    _wf = load_department_workflow("01-sales-growth")
    assert isinstance(_wf, dict) and isinstance(_wf.get("steps"), list)
    assert len(_wf["steps"]) >= 3
    _res = execute_department_task(
        "01-sales-growth",
        {"title": "self-test", "type": "dept_sales",
         "payload": {"task_kind": "lead_score",
                     "prospect": "TEST Prospect LLC"}})
    assert _res["status"] in ("executed", "executed-partial"), _res
    assert _res["cost_usd"] == 0.0
    assert _res["execution_record"]["status"] in (
        "completed", "partial", "error")
    _rep = compile_department_report(
        "01-sales-growth", tasks=[{"status": "draft-ready"}], runs=[])
    assert isinstance(_rep, dict) and "error" not in _rep, _rep
    _bad = compile_department_report("no-such-department")
    assert "error" in _bad
    print("department_runtime: OK (load workflow; execute "
          f"{_res['status']} via runtime, "
          f"{_res['iterations']} iterations, $0.00; report compiles; "
          "unknown department errors cleanly)")
