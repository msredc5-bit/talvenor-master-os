#!/usr/bin/env python3
"""Phase 2 self-check — Agency Chief -> 8 department managers wiring.

যাচাই করে:
  1. ৮টা department-এর SECTION.md আছে
  2. ৮টা manager file আছে + python3 -I-তে standalone import হয়
     (stdlib only) + class attrs ঠিক (task_kind / gate / department / role)
  3. ৮টা manager skill file আছে (প্রতি manager-এর একটা করে)
  4. Chief-এর DEPARTMENT_ROUTING-এ ৮টা entry — file/class/gate
     registry manager table + manager class-এর সাথে মেলে
  5. Chief ৮টা dept type-ই route করে (run_office.py, TEMP store):
     প্রতিটা valid task_kind-এ draft-ready, [MOCK DRAFT];
     dept_sales kind ছাড়া overview দেয়
  6. Gated action -> PENDING, execute হয় না (TEMP store):
     dept_sales + send, dept_strategy + send — প্রতিটায় ঠিক ১
     pending approval
  7. Unknown task kind -> status "unknown-task", known kind-গুলোর
     তালিকা সহ (draft-ready বলে ভুল লেবেল নয়)
  8. departments/ + registry.md-এ কোনো stale wiring দাবি নেই
     ("Chief এখনো call করে না" / "এখনো Agency Chief ডাকে না")
  9. ROUTING (১৫) ও SECTION_ROUTING (৬) অপরিবর্তিত
 10. departments/ + chief file-এ forbidden term নেই
     (Retell Integration / PostgreSQL / Sophia Demo / Paperclip /
     UroNex / NexaFlow / 90-second demo)
 11. Real store untouched (tasks 0, approvals 0, tool_calls.json নেই)
 12. পুরনো check (phase0/1/2/3/4 + engines + phase6 + phase7) এখনো PASS

Chief-level test run_office.py subprocess-এ চলে। Manager run() test
in-process নয় — Chief-এর DEPARTMENT_ROUTING branch-ই আসল path।
সব store-touching step TEMP file-এ। Stdlib only, no network,
no send, no publish, no spend, no delete। Exit 0 = PASS.
"""

import ast
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

AGENCY_DIR = os.path.join(BASE, "01-Agency-Department")
DEPARTMENTS_DIR = os.path.join(AGENCY_DIR, "departments")
CHIEF_PATH = os.path.join(AGENCY_DIR, "chief_of_staff_agency.py")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# (department folder, manager file, class, task_kind, gate,
#  chief task type, valid department task_kind for smoke test)
MANAGERS = [
    ("01-sales-growth", "chief_growth_agent.py", "ChiefGrowthAgent",
     "manage_sales_growth", "ok", "dept_sales", "prospect_research"),
    ("02-marketing", "marketing_director_agent.py", "MarketingDirectorAgent",
     "manage_marketing", "ok", "dept_marketing", "content_plan"),
    ("03-ai-engineering", "cto_ai_engineering_agent.py",
     "CTOAIEngineeringAgent", "manage_ai_engineering", "ok",
     "dept_engineering", "receptionist_build"),
    ("04-client-operations", "coo_client_operations_agent.py",
     "COOClientOperationsAgent", "manage_client_operations", "ok",
     "dept_operations", "client_intake"),
    ("05-research-strategy", "chief_strategy_agent.py", "ChiefStrategyAgent",
     "manage_research_strategy", "ok", "dept_strategy",
     "competitor_research"),
    ("06-finance-admin", "cfo_finance_agent.py", "CFOFinanceAgent",
     "manage_finance_admin", "ok", "dept_finance", "billing_invoice"),
    ("07-quality-security", "chief_quality_security_agent.py",
     "ChiefQualitySecurityAgent", "manage_quality_security", "ok",
     "dept_quality", "voice_quality_testing"),
    ("08-product-innovation", "chief_innovation_agent.py",
     "ChiefInnovationAgent", "manage_product_innovation", "ok",
     "dept_innovation", "new_ai_product_research"),
]


def _load_manager_file(path):
    spec = importlib.util.spec_from_file_location(
        "p2_mgr_" + os.path.splitext(os.path.basename(path))[0], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _count_dict_keys(path, name):
    """একটা module-level dict-এর key সংখ্যা (value literal না হলেও চলে)।"""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    if isinstance(node.value, ast.Dict):
                        return len(node.value.keys)
                    raise ValueError(f"{name} is not a dict literal")
    raise ValueError(f"{name} not found in {path}")


def _parse_dict_from_file(path, name):
    """একটা module-level dict literal ast দিয়ে পড়া (import ছাড়া)।"""
    with open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"{name} not found in {path}")


def main():
    # 1. All 8 department SECTION.md files exist
    try:
        missing = []
        for dept, _fn, _cls, _kind, _gate, _tt, _vk in MANAGERS:
            path = os.path.join(DEPARTMENTS_DIR, dept, "SECTION.md")
            if not os.path.isfile(path):
                missing.append(os.path.relpath(path, BASE))
        check("8 department SECTION.md files exist", not missing,
              f"missing={missing}" if missing else "8/8")
    except Exception as e:  # noqa: BLE001
        check("8 department SECTION.md files exist", False, str(e))

    # 2. All 8 manager files import standalone (python3 -I) + class attrs
    try:
        code_lines = ["import importlib.util, json, sys"]
        payload = []
        for dept, fname, cls, kind, gate, _tt, _vk in MANAGERS:
            path = os.path.join(DEPARTMENTS_DIR, dept, "manager", fname)
            payload.append((path, cls, kind, gate, dept))
        code_lines.append(f"MANAGERS = {payload!r}")
        code_lines.append("out = []")
        code_lines.append("for path, cls, kind, gate, dept in MANAGERS:")
        code_lines.append("    spec = importlib.util.spec_from_file_location('m_' + cls, path)")
        code_lines.append("    mod = importlib.util.module_from_spec(spec)")
        code_lines.append("    spec.loader.exec_module(mod)")
        code_lines.append("    c = getattr(mod, cls)")
        code_lines.append("    assert c.task_kind == kind, (cls, c.task_kind, kind)")
        code_lines.append("    assert c.gate == gate, (cls, c.gate, gate)")
        code_lines.append("    assert c.department == dept, (cls, c.department, dept)")
        code_lines.append("    assert isinstance(c.role, str) and c.role")
        code_lines.append("    out.append(cls)")
        code_lines.append("print('MANAGERS_OK ' + ','.join(out))")
        proc = subprocess.run(
            [sys.executable, "-I", "-c", "\n".join(code_lines)],
            capture_output=True, text=True, timeout=120, cwd=BASE)
        ok = proc.returncode == 0 and "MANAGERS_OK" in proc.stdout
        detail = (proc.stdout + proc.stderr).strip()[-300:]
        check("8 managers import standalone + class attrs correct",
              ok, f"{len(MANAGERS)} managers; " + detail)
    except Exception as e:  # noqa: BLE001
        check("8 managers import standalone + class attrs correct",
              False, str(e))

    # 3. All 8 manager skill files exist
    try:
        missing = []
        for dept, fname, _cls, _kind, _gate, _tt, _vk in MANAGERS:
            skill = fname[:-3].replace("_", "-") + ".md"
            path = os.path.join(DEPARTMENTS_DIR, dept, "skills", skill)
            if not os.path.isfile(path):
                missing.append(os.path.relpath(path, BASE))
        check("8 manager skill files exist (one per manager)", not missing,
              f"missing={missing}" if missing else "8/8")
    except Exception as e:  # noqa: BLE001
        check("8 manager skill files exist (one per manager)", False, str(e))

    # 4. DEPARTMENT_ROUTING: 8 entries, file/class/gate match managers
    try:
        routing = _parse_dict_from_file(CHIEF_PATH, "DEPARTMENT_ROUTING")
        bad = []
        if set(routing.keys()) != {m[5] for m in MANAGERS}:
            bad.append(f"keys={sorted(routing.keys())}")
        for dept, fname, cls, _kind, gate, task_type, _vk in MANAGERS:
            entry = routing.get(task_type)
            if entry is None:
                bad.append(f"missing {task_type}")
                continue
            exp_file = f"{dept}/manager/{fname}"
            if tuple(entry) != (exp_file, cls, gate):
                bad.append(f"{task_type}: {entry} != {(exp_file, cls, gate)}")
            if not os.path.isfile(os.path.join(DEPARTMENTS_DIR, exp_file)):
                bad.append(f"file missing: {exp_file}")
        check("DEPARTMENT_ROUTING: 8 entries, file/class/gate match",
              not bad, "; ".join(bad) if bad else "8/8 match registry table")
    except Exception as e:  # noqa: BLE001
        check("DEPARTMENT_ROUTING: 8 entries, file/class/gate match",
              False, str(e))

    # 5+6+7. Chief routing via run_office.py (TEMP stores)
    runner = os.path.join(BASE, "scripts", "run_office.py")

    def run_runner(business, task_type, input_data, store_dir):
        return subprocess.run(
            [sys.executable, runner, "--business", business,
             "--task", task_type, "--input", json.dumps(input_data),
             "--store-dir", store_dir],
            capture_output=True, text=True, timeout=300)

    # 5. All 8 dept types route -> draft-ready, [MOCK DRAFT]
    for dept, _fn, cls, _kind, _gate, task_type, valid_kind in MANAGERS:
        try:
            store = tempfile.mkdtemp()
            proc = run_runner("agency", task_type,
                              {"title": f"Phase 2 smoke {task_type}",
                               "payload": {"task_kind": valid_kind}},
                              store)
            result = json.loads(proc.stdout)
            chief = result.get("chief_result", result)
            ok = (proc.returncode == 0
                  and result.get("status") == "draft-ready"
                  and chief.get("mock_brain") is True
                  and chief.get("draft_only") is True
                  and chief.get("worker") == cls
                  and chief.get("manager_department") == dept
                  and chief.get("gate") == "ok"
                  and "[MOCK DRAFT]" in (chief.get("output") or "")
                  + (chief.get("notes") or ""))
            check(f"Chief routes {task_type} ({valid_kind}) -> draft-ready [MOCK DRAFT]",
                  ok, f"status={result.get('status')}, "
                  f"worker={chief.get('worker')}")
        except Exception as e:  # noqa: BLE001
            check(f"Chief routes {task_type} ({valid_kind}) -> draft-ready [MOCK DRAFT]",
                  False, str(e))

    # 5b. Overview without task_kind (M1-M4 pattern) -> draft-ready
    try:
        store = tempfile.mkdtemp()
        proc = run_runner("agency", "dept_sales",
                          {"title": "Phase 2 smoke sales overview"}, store)
        result = json.loads(proc.stdout)
        chief = result.get("chief_result", result)
        ok = (proc.returncode == 0
              and result.get("status") == "draft-ready"
              and "overview" in (chief.get("output") or "").lower()
              and "[MOCK DRAFT]" in (chief.get("output") or ""))
        check("dept_sales without task_kind -> overview draft-ready",
              ok, f"status={result.get('status')}")
    except Exception as e:  # noqa: BLE001
        check("dept_sales without task_kind -> overview draft-ready",
              False, str(e))

    # 6. Gated actions -> PENDING, exactly 1 pending approval each
    for task_type, label in (
            ("dept_sales", "dept_sales + send"),
            ("dept_strategy", "dept_strategy + send")):
        try:
            store = tempfile.mkdtemp()
            proc = run_runner("agency", task_type,
                              {"title": f"Phase 2 smoke gated {label}",
                               "gated_action": "send"},
                              store)
            result = json.loads(proc.stdout)
            approvals = json.load(
                open(os.path.join(store, "approvals.json"),
                     encoding="utf-8"))["records"]
            ok = (proc.returncode == 0
                  and result.get("status") == "pending-approval"
                  and len(approvals) == 1
                  and approvals[0]["status"] == "pending"
                  and approvals[0]["action"] == "send")
            check(f"gated {label} -> PENDING, 1 approval, not executed",
                  ok, f"status={result.get('status')}, "
                  f"approvals={len(approvals)}")
        except Exception as e:  # noqa: BLE001
            check(f"gated {label} -> PENDING, 1 approval, not executed",
                  False, str(e))

    # 7. Unknown task kind -> status "unknown-task", known kinds listed
    try:
        store = tempfile.mkdtemp()
        proc = run_runner("agency", "dept_strategy",
                          {"title": "Phase 2 smoke unknown kind",
                           "payload": {"task_kind": "no_such_kind"}},
                          store)
        result = json.loads(proc.stdout)
        chief = result.get("chief_result", result)
        ok = (proc.returncode == 0
              and result.get("status") == "unknown-task"
              and "competitor_research" in (chief.get("output") or ""))
        check("unknown department task kind -> unknown-task, kinds listed",
              ok, f"status={result.get('status')}")
    except Exception as e:  # noqa: BLE001
        check("unknown department task kind -> unknown-task, kinds listed",
              False, str(e))

    # 8. No stale wiring claims in departments/ + registry.md
    try:
        stale = []
        needles = ("Chief এখনো", "এখনো Agency Chief", "wiring Phase 2 —",
                   "handoff এখন manual", "manager-রা standalone")
        targets = []
        for root, dirs, files in os.walk(DEPARTMENTS_DIR):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                if name.endswith((".py", ".md")):
                    targets.append(os.path.join(root, name))
        targets.append(os.path.join(
            AGENCY_DIR, "agents", "agent-registry", "registry.md"))
        for path in targets:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for needle in needles:
                if needle in text:
                    stale.append(f"{os.path.relpath(path, BASE)}: {needle}")
        check("no stale wiring claims (Chief এখনো / ডাকে না / manual)",
              not stale, "; ".join(stale[:5]) if stale else "clean")
    except Exception as e:  # noqa: BLE001
        check("no stale wiring claims (Chief এখনো / ডাকে না / manual)",
              False, str(e))

    # 9. ROUTING (15) + SECTION_ROUTING (6) unchanged
    # ROUTING-এর value-তে class name (ast.Name) আছে, তাই literal_eval
    # নয় — শুধু key সংখ্যা গোনা হয়।
    try:
        routing_count = _count_dict_keys(CHIEF_PATH, "ROUTING")
        section_count = _count_dict_keys(CHIEF_PATH, "SECTION_ROUTING")
        ok = routing_count == 15 and section_count == 6
        check("ROUTING 15 + SECTION_ROUTING 6 unchanged",
              ok, f"ROUTING={routing_count}, SECTION_ROUTING={section_count}")
    except Exception as e:  # noqa: BLE001
        check("ROUTING 15 + SECTION_ROUTING 6 unchanged", False, str(e))

    # 10. Forbidden terms in departments/ + chief file
    try:
        bad = []
        needles = ("Retell Integration", "PostgreSQL", "Sophia Demo",
                   "Paperclip", "UroNex", "NexaFlow", "90-second demo")
        targets = [CHIEF_PATH]
        for root, dirs, files in os.walk(DEPARTMENTS_DIR):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                if name.endswith((".py", ".md")):
                    targets.append(os.path.join(root, name))
        for path in targets:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for needle in needles:
                if needle in text:
                    bad.append(f"{os.path.relpath(path, BASE)}: {needle}")
        check("no forbidden terms in departments/ + chief",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no forbidden terms in departments/ + chief", False, str(e))

    # 11. Real store untouched
    try:
        with open(os.path.join(BASE, "store", "tasks.json"),
                  encoding="utf-8") as f:
            real_tasks = json.load(f)
        with open(os.path.join(BASE, "store", "approvals.json"),
                  encoding="utf-8") as f:
            real_appr = json.load(f)
        no_calls = not os.path.exists(
            os.path.join(BASE, "store", "tool_calls.json"))
        check("real store untouched (tasks 0, approvals 0, no tool_calls)",
              real_tasks.get("records") == []
              and real_appr.get("records") == [] and no_calls)
    except Exception as e:  # noqa: BLE001
        check("real store untouched (tasks 0, approvals 0, no tool_calls)",
              False, str(e))

    # 12. Earlier checks still PASS
    try:
        codes = []
        for script in ("check_phase0.py", "check_phase1.py",
                       "check_phase2.py", "check_phase3.py",
                       "check_phase4.py", "check_engines.py",
                       "check_phase6.py", "check_phase7.py"):
            proc = subprocess.run(
                [sys.executable, os.path.join(BASE, "scripts", script)],
                capture_output=True, text=True, timeout=600)
            codes.append(proc.returncode)
        ok = all(c == 0 for c in codes)
        check("check_phase0/1/2/3/4 + engines + phase6 + phase7 still PASS",
              ok, f"p0={codes[0]}, p1={codes[1]}, p2={codes[2]}, "
              f"p3={codes[3]}, p4={codes[4]}, engines={codes[5]}, "
              f"p6={codes[6]}, p7={codes[7]}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0/1/2/3/4 + engines + phase6 + phase7 still PASS",
              False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 2 (departments) self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
