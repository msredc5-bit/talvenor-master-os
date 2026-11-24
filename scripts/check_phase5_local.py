#!/usr/bin/env python3
"""check_phase5_local.py — Local-first Phase 5 self-check for the
shared department runtime wiring + Chief hook (Worker C).

What it checks (offline ONLY — no network, no live call, ever;
$0; real n8n is [NOT TESTED] — n8n lives on Boss's PC):

  1. All 8 departments have workflows/*.json + reports/report.py.
  2. Every department workflow JSON parses and has a "steps" list
     with >= 3 steps including exactly one gated step.
  3. Every department workflow executes in-memory via the Phase 4
     WorkflowEngine: mock steps ok, the gated step
     pending-approval, cost 0.0.
  4. Every reports/report.py compiles in-memory (fake tasks/runs)
     and on a missing store_dir without raising and without
     writing anything.
  5. Chief routes a dept task WITH "execute": True end-to-end
     (in-memory store stub — chief_of_staff_agency.update_json is
     patched BEFORE handle_task, same pattern as
     check_workflow_engine.py): result status executed /
     executed-partial, result has "execution" with steps evidence,
     the task log record carries "executions" with 1 record,
     cost 0.0.
  6. Chief routes the SAME dept task WITHOUT "execute": status
     draft-ready, NO "execution" key (default behaviour unchanged).
  7. A dept task with a gated_action still returns pending-approval
     and never executes (even with "execute": True). The gateway
     is stubbed in-memory (ApprovalGateway.request would write
     approvals.json on disk); the stub records nothing anywhere.
  8. department_runtime.compile_department_report works in-memory
     for at least one department.
  9. Real store files unchanged (sha256 of store/tasks.json and
     store/approvals.json before/after — if the run touched them,
     FAIL).

Stdlib only. No tempfile anywhere in this script (the VM-wide
exec-write block makes tempfile.mkdtemp() raise); every store
write is stubbed in-memory. A check that cannot run under the
block is marked BLOCKED in its output, never faked as a pass.

Run: python3 scripts/check_phase5_local.py
Exit 0 = no FAIL (BLOCKED checks are reported, not hidden).
"""

import copy
import hashlib
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
AGENCY_DIR = os.path.join(BASE, "01-Agency-Department")
DEPARTMENTS_DIR = os.path.join(AGENCY_DIR, "departments")
STORE_DIR = os.path.join(BASE, "store")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, DEPARTMENTS_DIR)
sys.path.insert(0, AGENCY_DIR)

DEPARTMENTS = [
    "01-sales-growth",
    "02-marketing",
    "03-ai-engineering",
    "04-client-operations",
    "05-research-strategy",
    "06-finance-admin",
    "07-quality-security",
    "08-product-innovation",
]

# Static gated-step test (mirrors the Phase 3 gate's decision order
# for the steps these workflows use): a gated tool, or a commit verb.
_GATED_TOOLS = {"gmail_send", "n8n_trigger"}
_GATED_ACTIONS = {"send", "publish", "spend", "delete", "upload",
                  "book", "pay", "order", "cancel"}

results = []  # (name, status, detail); status in PASS / FAIL / BLOCKED


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def blocked(name, reason):
    results.append((name, "BLOCKED", reason))
    print(f"[BLOCKED] {name} — {reason}")


def _sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _is_gated_step(step):
    if not isinstance(step, dict):
        return False
    tool = str(step.get("tool") or step.get("tool_name") or "").strip()
    action = str(step.get("action") or step.get("type") or "").strip()
    return tool in _GATED_TOOLS or action in _GATED_ACTIONS


def _dept_task(execute=None):
    """The acceptance-shaped dept task (TEST data only)."""
    task = {
        "business": "agency",
        "type": "dept_sales",
        "title": "TEST lead score — TEST Prospect LLC",
        "payload": {
            "task_kind": "lead_score",
            "prospect": "TEST Prospect LLC",
            "business_name": "TEST Prospect LLC",
            "strength": "STRONG",
            "score": 85,
        },
    }
    if execute is not None:
        task["execute"] = execute
    return task


class _InMemoryStore:
    """Stand-in for chief_of_staff_agency.update_json: applies the
    caller's transform to an in-memory dict keyed by path. Nothing
    touches disk. Same stub pattern as check_workflow_engine.py."""

    def __init__(self):
        self.data = {}

    def update(self, path, fn, default=None):
        current = self.data.get(path)
        if current is None:
            current = copy.deepcopy(default) if default is not None \
                else {}
        self.data[path] = fn(current)
        return self.data[path]

    def records_for(self, path):
        data = self.data.get(path) or {}
        records = data.get("records") if isinstance(data, dict) else None
        return records if isinstance(records, list) else []


def main():
    store_before = {
        name: _sha256_file(os.path.join(STORE_DIR, name))
        for name in ("tasks.json", "approvals.json")
    }

    # -- imports ---------------------------------------------------------
    try:
        from workflow_engine.engine import WorkflowEngine  # noqa: PLC0415
        import department_runtime  # noqa: PLC0415
        import chief_of_staff_agency as chief  # noqa: PLC0415
    except ImportError as exc:  # noqa: BLE001
        check("phase5 imports (WorkflowEngine, department_runtime, "
              "chief_of_staff_agency)", False, str(exc))
        print("\n0/1 checks passed.")
        return 1

    # -- 1. All 8 departments have workflows/*.json + reports/report.py --
    try:
        missing = []
        for dept in DEPARTMENTS:
            wf_dir = os.path.join(DEPARTMENTS_DIR, dept, "workflows")
            try:
                wf_names = [n for n in os.listdir(wf_dir)
                            if n.endswith(".json")]
            except OSError:
                wf_names = []
            report = os.path.join(DEPARTMENTS_DIR, dept, "reports",
                                  "report.py")
            if not wf_names:
                missing.append(f"{dept}: no workflows/*.json")
            if not os.path.isfile(report):
                missing.append(f"{dept}: no reports/report.py")
        check("1. all 8 departments have workflows/*.json + "
              "reports/report.py", not missing,
              "missing: " + "; ".join(missing) if missing
              else "8/8 departments present")
    except Exception as exc:  # noqa: BLE001
        check("1. all 8 departments have workflows/*.json + "
              "reports/report.py", False,
              f"{type(exc).__name__}: {exc}"[:160])

    # -- 2. Every workflow JSON parses, >= 3 steps, exactly 1 gated ---
    try:
        problems = []
        checked = 0
        for dept in DEPARTMENTS:
            wf_dir = os.path.join(DEPARTMENTS_DIR, dept, "workflows")
            for name in sorted(os.listdir(wf_dir)):
                if not name.endswith(".json"):
                    continue
                checked += 1
                path = os.path.join(wf_dir, name)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except (OSError, json.JSONDecodeError) as exc:
                    problems.append(f"{dept}/{name}: unreadable "
                                    f"({type(exc).__name__})")
                    continue
                steps = wf.get("steps") if isinstance(wf, dict) else None
                if not isinstance(steps, list):
                    problems.append(f"{dept}/{name}: no 'steps' list")
                    continue
                gated = [s for s in steps if _is_gated_step(s)]
                if len(steps) < 3:
                    problems.append(
                        f"{dept}/{name}: only {len(steps)} steps")
                if len(gated) != 1:
                    problems.append(
                        f"{dept}/{name}: {len(gated)} gated steps "
                        "(want exactly 1)")
        check("2. every workflow JSON parses, >= 3 steps, exactly "
              "1 gated step", not problems,
              f"{checked} files checked"
              + ("; " + "; ".join(problems) if problems else
                 ", all >= 3 steps with exactly 1 gated step"))
    except Exception as exc:  # noqa: BLE001
        check("2. every workflow JSON parses, >= 3 steps, exactly "
              "1 gated step", False,
              f"{type(exc).__name__}: {exc}"[:160])

    # -- 3. Every workflow executes in-memory via WorkflowEngine -------
    try:
        engine = WorkflowEngine()
        problems = []
        for dept in DEPARTMENTS:
            wf = department_runtime.load_department_workflow(dept)
            out = engine.execute(wf)
            steps = out.get("steps") or []
            statuses = [s.get("status") for s in steps
                        if isinstance(s, dict)]
            pending = statuses.count("pending-approval")
            ok_steps = statuses.count("ok")
            if not (out.get("status") == "partial"
                    and pending == 1
                    and ok_steps == len(statuses) - 1
                    and out.get("cost_usd") == 0.0):
                problems.append(
                    f"{dept}: status={out.get('status')}, "
                    f"steps={statuses}, cost={out.get('cost_usd')}")
        check("3. every department workflow executes in-memory "
              "(mock steps ok, gated step pending-approval, $0.00)",
              not problems,
              "8/8 partial with exactly 1 pending-approval, cost 0.0"
              if not problems else "; ".join(problems))
    except Exception as exc:  # noqa: BLE001
        check("3. every department workflow executes in-memory "
              "(mock steps ok, gated step pending-approval, $0.00)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 4. Every report compiles in-memory + on a missing store_dir ---
    try:
        problems = []
        missing_dir = "/tmp/does-not-exist-phase5-check"
        for dept in DEPARTMENTS:
            fake_tasks = [{"id": "t1", "status": "draft-ready",
                           "title": "TEST task"},
                          {"id": "t2", "status": "pending-approval",
                           "title": "TEST gated task"}]
            fake_runs = [{"id": "t1", "status": "draft-ready"}]
            rep = department_runtime.compile_department_report(
                dept, tasks=fake_tasks, runs=fake_runs)
            if not isinstance(rep, dict) or "error" in rep:
                problems.append(f"{dept}: in-memory compile failed "
                                f"({rep.get('error') if isinstance(rep, dict) else rep})")
                continue
            if rep.get("department") != dept:
                problems.append(f"{dept}: report department "
                                f"is {rep.get('department')!r}")
            rep_missing = department_runtime.compile_department_report(
                dept, store_dir=missing_dir)
            if not isinstance(rep_missing, dict) \
                    or "error" in rep_missing:
                problems.append(f"{dept}: missing-store_dir compile "
                                "failed")
            if os.path.exists(missing_dir):
                problems.append(f"{dept}: missing store_dir was "
                                "created (a write happened)")
        check("4. every reports/report.py compiles in-memory and "
              "on a missing store_dir without raising or writing",
              not problems,
              "8/8 compile in-memory + missing-dir, nothing written"
              if not problems else "; ".join(problems))
    except Exception as exc:  # noqa: BLE001
        check("4. every reports/report.py compiles in-memory and "
              "on a missing store_dir without raising or writing",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 5. Chief routes a dept task WITH "execute": True --------------
    try:
        store = _InMemoryStore()
        real_update = chief.update_json
        chief.update_json = store.update
        try:
            result = chief.handle_task(
                _dept_task(execute=True),
                tasks_path="/in-memory/tasks.json",
                approvals_path="/in-memory/approvals.json")
        finally:
            chief.update_json = real_update
        logged = store.records_for("/in-memory/tasks.json")
        dept_logged = [r for r in logged
                       if r.get("type") == "dept_sales"]
        executions = (dept_logged[0].get("executions")
                      if dept_logged else None)
        execution = result.get("execution") or {}
        step_statuses = [s.get("status") for s in
                         (execution.get("steps") or [])
                         if isinstance(s, dict)]
        ok = (result.get("status") in ("executed", "executed-partial")
              and isinstance(execution, dict)
              and step_statuses == ["ok", "ok", "pending-approval"]
              and execution.get("cost_usd") == 0.0
              and isinstance(executions, list)
              and len(executions) == 1
              and executions[0].get("cost_usd") == 0.0
              and executions[0].get("status") in ("partial", "completed"))
        check("5. Chief routes dept task WITH execute=True "
              "end-to-end (in-memory store stub)",
              ok,
              f"chief={result.get('status')}, "
              f"steps={step_statuses}, "
              f"executions={[e.get('status') for e in executions] if isinstance(executions, list) else executions}, "
              f"cost={execution.get('cost_usd')}")
    except Exception as exc:  # noqa: BLE001
        check("5. Chief routes dept task WITH execute=True "
              "end-to-end (in-memory store stub)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 6. SAME task WITHOUT "execute": default behaviour unchanged ----
    try:
        store = _InMemoryStore()
        real_update = chief.update_json
        chief.update_json = store.update
        try:
            result = chief.handle_task(
                _dept_task(),
                tasks_path="/in-memory/tasks.json",
                approvals_path="/in-memory/approvals.json")
        finally:
            chief.update_json = real_update
        logged = store.records_for("/in-memory/tasks.json")
        dept_logged = [r for r in logged
                       if r.get("type") == "dept_sales"]
        ok = (result.get("status") == "draft-ready"
              and "execution" not in result
              and bool(dept_logged)
              and "executions" not in dept_logged[0])
        check("6. SAME dept task WITHOUT execute: draft-ready, "
              "NO execution key (default behaviour unchanged)",
              ok,
              f"chief={result.get('status')}, "
              f"has execution={'execution' in result}, "
              f"log has executions={'executions' in dept_logged[0] if dept_logged else 'no log record'}")
    except Exception as exc:  # noqa: BLE001
        check("6. SAME dept task WITHOUT execute: draft-ready, "
              "NO execution key (default behaviour unchanged)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 7. Gated dept task never executes, even with execute=True -----
    try:
        class _FakeGateway:
            """In-memory ApprovalGateway stand-in: request() records
            nothing anywhere (the real one writes approvals.json)."""
            def __init__(self, approvals_path=None):
                self.approvals_path = approvals_path
                self.requested = []

            def request(self, action, detail, requested_by):
                rec = {"id": "fake-appr-1", "action": action,
                       "detail": detail, "requested_by": requested_by,
                       "status": "pending"}
                self.requested.append(rec)
                return dict(rec)

            def is_approved(self, approval_id):
                return False

        store = _InMemoryStore()
        real_update = chief.update_json
        real_gateway = chief.ApprovalGateway
        chief.update_json = store.update
        chief.ApprovalGateway = _FakeGateway
        try:
            task = _dept_task(execute=True)
            task["gated_action"] = "send"
            result = chief.handle_task(
                task,
                tasks_path="/in-memory/tasks.json",
                approvals_path="/in-memory/approvals.json")
        finally:
            chief.update_json = real_update
            chief.ApprovalGateway = real_gateway
        ok = (result.get("status") == "pending-approval"
              and "execution" not in result
              and result.get("gated_action") == "send")
        check("7. gated dept task returns pending-approval and "
              "never executes (even with execute=True)",
              ok,
              f"chief={result.get('status')}, "
              f"has execution={'execution' in result}, "
              f"gated_action={result.get('gated_action')}")
    except Exception as exc:  # noqa: BLE001
        check("7. gated dept task returns pending-approval and "
              "never executes (even with execute=True)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 8. compile_department_report works in-memory -------------------
    try:
        rep = department_runtime.compile_department_report(
            "01-sales-growth",
            tasks=[{"id": "t1", "status": "draft-ready",
                    "title": "TEST task"},
                   {"id": "t2", "status": "pending-approval",
                    "title": "TEST gated task"}],
            runs=[{"id": "t1", "status": "draft-ready"}])
        ok = (isinstance(rep, dict) and "error" not in rep
              and rep.get("department") == "01-sales-growth"
              and rep.get("task_counts", {}).get("total") == 2)
        check("8. department_runtime.compile_department_report "
              "works in-memory (01-sales-growth)",
              ok,
              f"department={rep.get('department')}, "
              f"task_counts={rep.get('task_counts')}, "
              f"pending={rep.get('pending_approvals')}")
    except Exception as exc:  # noqa: BLE001
        check("8. department_runtime.compile_department_report "
              "works in-memory (01-sales-growth)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    # -- 9. Real store files unchanged ----------------------------------
    try:
        store_after = {
            name: _sha256_file(os.path.join(STORE_DIR, name))
            for name in ("tasks.json", "approvals.json")
        }
        changed = [n for n in store_before
                   if store_before[n] != store_after[n]]
        check("9. real store files unchanged (sha256 tasks.json + "
              "approvals.json before/after)",
              not changed,
              "hashes match" if not changed
              else "CHANGED: " + ", ".join(changed))
    except Exception as exc:  # noqa: BLE001
        check("9. real store files unchanged (sha256 tasks.json + "
              "approvals.json before/after)",
              False, f"{type(exc).__name__}: {exc}"[:160])

    decided = [r for r in results if r[1] in ("PASS", "FAIL")]
    passed = sum(1 for r in decided if r[1] == "PASS")
    blocked_n = sum(1 for r in results if r[1] == "BLOCKED")
    print(f"\nPASS {passed}/{len(decided)} decided checks"
          + (f" ({blocked_n} BLOCKED)" if blocked_n else "")
          + ".")
    return 0 if passed == len(decided) else 1


if __name__ == "__main__":
    sys.exit(main())
