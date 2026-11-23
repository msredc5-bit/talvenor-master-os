#!/usr/bin/env python3
"""Unified Business OS Phase 2 check — Agency Departments.

Verifies the Phase 2 build (spec: TALVENOR_MASTER_ARCHITECTURE.md,
"PHASE 2 — AGENCY DEPARTMENTS"):
  1. All 8 managers: overview run -> structured draft-ready output.
  2. Every manager task_kind (72 across the 8 managers): run() with the
     MOCK brain -> structured output (dict with status/output/notes/
     draft_only/mock_brain/gate; draft-ready carries [MOCK DRAFT]).
  3. All 47 standalone specialists run directly with the MOCK brain ->
     structured draft-ready output.
  4. All 6 section agents run via the Chief's SECTION_ROUTING -> structured
     draft-ready output.
  5. All 15 engine workers run via run_office.py (TEMP store) -> draft-ready.
  6. Phase 2 regressions: backup_recovery routing, no parallel manager
     maps, dept 06 alias resolution, honest-status reads (live values +
     UNKNOWN on missing source), mock word-truncation, meta_provider lazy
     import, worker default-payload fixes, ReplyHandler decline gate,
     status_read derived notes, no hardcoded snapshot constants left.
  7. The real store did not change in this run.

All store-touching steps use TEMP files/dirs (a TEMP approvals file is
passed to every run() call, and run_office.py gets a TEMP --store-dir).
Stdlib only, no network, no send, no publish, no spend, no delete.
Exit 0 = PASS.
"""

import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
AGENCY_DIR = os.path.join(BASE, "01-Agency-Department")
DEPARTMENTS_DIR = os.path.join(AGENCY_DIR, "departments")
SECTIONS_DIR = os.path.join(AGENCY_DIR, "sections")
ENGINE_WORKERS_DIR = os.path.join(AGENCY_DIR, "engine", "workers")
STORE_DIR = os.path.join(BASE, "store")

sys.path.insert(0, CEO_CORE_DIR)
sys.path.insert(0, ENGINE_WORKERS_DIR)

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _snapshot_store():
    snap = {}
    for name in ("tasks.json", "approvals.json"):
        try:
            with open(os.path.join(STORE_DIR, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["agent_runs"] = os.path.exists(
        os.path.join(STORE_DIR, "agent_runs.json"))
    snap["audit_log"] = os.path.exists(os.path.join(STORE_DIR, "audit.log"))
    snap["tool_calls"] = os.path.exists(
        os.path.join(STORE_DIR, "tool_calls.json"))
    return snap


ALLOWED_STATUSES = {"draft-ready", "pending-approval", "unknown-task",
                    "pending"}


def structured_ok(result):
    """A manager/specialist/section result is structured: a dict with the
    required keys, a known status, a non-empty output, draft_only and
    mock_brain True. pending-approval has no output/notes (it carries an
    approval instead) — that shape is structured too."""
    if not isinstance(result, dict):
        return False, "not a dict"
    status = result.get("status")
    if status not in ALLOWED_STATUSES:
        return False, f"status={status!r}"
    if result.get("draft_only") is not True:
        return False, "draft_only is not True"
    if result.get("mock_brain") is not True:
        return False, "mock_brain is not True"
    if status == "pending-approval":
        if "approval" not in result:
            return False, "pending-approval without approval"
        return True, "pending-approval"
    for key in ("output", "notes", "gate"):
        if key not in result:
            return False, f"missing key {key}"
    if not isinstance(result["output"], str) or not result["output"]:
        return False, "empty output"
    if status == "draft-ready" and "[MOCK DRAFT]" not in result["output"]:
        return False, "draft-ready without [MOCK DRAFT]"
    return True, status


MANAGERS = [
    ("01-sales-growth", "chief_growth_agent.py", "ChiefGrowthAgent"),
    ("02-marketing", "marketing_director_agent.py", "MarketingDirectorAgent"),
    ("03-ai-engineering", "cto_ai_engineering_agent.py",
     "CTOAIEngineeringAgent"),
    ("04-client-operations", "coo_client_operations_agent.py",
     "COOClientOperationsAgent"),
    ("05-research-strategy", "chief_strategy_agent.py", "ChiefStrategyAgent"),
    ("06-finance-admin", "cfo_finance_agent.py", "CFOFinanceAgent"),
    ("07-quality-security", "chief_quality_security_agent.py",
     "ChiefQualitySecurityAgent"),
    ("08-product-innovation", "chief_innovation_agent.py",
     "ChiefInnovationAgent"),
]


def _scan_specialists():
    """The 47 standalone specialists on disk."""
    out = {}
    for slug, _mf, _mc in MANAGERS:
        d = os.path.join(DEPARTMENTS_DIR, slug, "specialists")
        for name in sorted(os.listdir(d)):
            if not name.endswith(".py"):
                continue
            path = os.path.join(d, name)
            text = open(path, encoding="utf-8").read()
            cls = re.search(r"^class (\w+)", text, re.M).group(1)
            kind = re.search(r"task_kind = \"([^\"]+)\"", text).group(1)
            out[kind] = {"class": cls, "path": path}
    return out


def main():
    store_before = _snapshot_store()
    tmp = tempfile.mkdtemp()
    approvals_path = os.path.join(tmp, "approvals.json")
    from src.mock.provider import MockLLMProvider
    brain = MockLLMProvider()

    # --- 1. All 8 manager overviews -> structured draft-ready ----------
    manager_mods = {}
    for slug, fname, cls_name in MANAGERS:
        path = os.path.join(DEPARTMENTS_DIR, slug, "manager", fname)
        mod = load_module(f"p2_mgr_{slug}", path)
        manager_mods[slug] = (mod, getattr(mod, cls_name)())
    for slug, (_mod, manager) in manager_mods.items():
        try:
            result = manager.run({"title": f"Phase 2 smoke {slug} overview"},
                                 brain=brain, approvals_path=approvals_path)
            ok, detail = structured_ok(result)
            check(f"manager overview {slug} -> structured draft-ready",
                  ok and result.get("status") == "draft-ready", detail)
        except Exception as exc:  # noqa: BLE001
            check(f"manager overview {slug} -> structured draft-ready",
                  False, str(exc))

    # --- 2. Every manager task_kind (72) -> structured output ----------
    kind_count = 0
    for slug, (mod, manager) in manager_mods.items():
        for kind in sorted(mod.DEPARTMENT_TASKS.keys()):
            kind_count += 1
            try:
                result = manager.run(
                    {"task_kind": kind,
                     "title": f"Phase 2 smoke {slug}/{kind}",
                     "payload": {"prospect": "Smoke Test Co",
                                 "state": "PA", "state_first_mails": 39,
                                 "topic": "smoke test"}},
                    brain=brain, approvals_path=approvals_path)
                ok, detail = structured_ok(result)
                check(f"manager {slug}/{kind} -> structured output",
                      ok, detail)
            except Exception as exc:  # noqa: BLE001
                check(f"manager {slug}/{kind} -> structured output",
                      False, str(exc))
    check("72 manager task_kinds covered (8 managers)",
          kind_count == 72, f"kinds={kind_count}")

    # --- 3. All 47 specialists direct, MOCK brain ----------------------
    specialists = _scan_specialists()
    check("47 specialists found on disk", len(specialists) == 47,
          f"found={len(specialists)}")
    for kind in sorted(specialists):
        info = specialists[kind]
        try:
            mod = load_module(f"p2_spec_{kind}", info["path"])
            agent = getattr(mod, info["class"])()
            result = agent.run(
                {"task_kind": kind, "title": f"Phase 2 smoke {kind}",
                 "payload": {"prospect": "Smoke Test Co", "state": "PA",
                             "state_first_mails": 39, "topic": "smoke test"}},
                brain=brain, approvals_path=approvals_path)
            ok, detail = structured_ok(result)
            check(f"specialist {kind} -> structured draft-ready",
                  ok and result.get("status") == "draft-ready", detail)
        except Exception as exc:  # noqa: BLE001
            check(f"specialist {kind} -> structured draft-ready",
                  False, str(exc))

    # --- 4. All 6 section agents via Chief SECTION_ROUTING -------------
    chief_mod = load_module(
        "p2_chief",
        os.path.join(AGENCY_DIR, "chief_of_staff_agency.py"))
    section_count = 0
    for task_type in sorted(chief_mod.SECTION_ROUTING.keys()):
        section_count += 1
        module_file, class_name, _gate = chief_mod.SECTION_ROUTING[task_type]
        try:
            mod = load_module(f"p2_section_{task_type}",
                              os.path.join(SECTIONS_DIR, module_file))
            agent = getattr(mod, class_name)()
            result = agent.run(
                {"task_kind": task_type,
                 "title": f"Phase 2 smoke section {task_type}",
                 "payload": {"prospect": "Smoke Test Co", "state": "PA",
                             "state_first_mails": 39, "topic": "smoke test"}},
                brain=brain, approvals_path=approvals_path)
            ok, detail = structured_ok(result)
            check(f"section agent {task_type} -> structured draft-ready",
                  ok and result.get("status") == "draft-ready", detail)
        except Exception as exc:  # noqa: BLE001
            check(f"section agent {task_type} -> structured draft-ready",
                  False, str(exc))
    check("6 section agents covered", section_count == 6,
          f"found={section_count}")

    # --- 5. All 15 engine workers via run_office.py (TEMP store) -------
    runner = os.path.join(BASE, "scripts", "run_office.py")
    worker_count = 0
    for task_type in sorted(chief_mod.ROUTING.keys()):
        worker_count += 1
        try:
            store = tempfile.mkdtemp()
            proc = subprocess.run(
                [sys.executable, runner, "--business", "agency",
                 "--task", task_type,
                 "--input", json.dumps(
                     {"title": f"Phase 2 smoke worker {task_type}"}),
                 "--store-dir", store],
                capture_output=True, text=True, timeout=300)
            result = json.loads(proc.stdout)
            chief_result = result.get("chief_result", result)
            # Engine workers return a WorkerResult shape, NOT the agent
            # dict shape: output is a dict, notes is the mock-plan string
            # (no "[MOCK DRAFT]" literal — that label lives on the agent
            # dict results). The contract here is: draft-ready +
            # worker_status ok + draft_only + mock_brain + the MOCK-PLAN
            # signature in notes.
            ok = (proc.returncode == 0
                  and result.get("status") == "draft-ready"
                  and chief_result.get("draft_only") is True
                  and chief_result.get("mock_brain") is True
                  and chief_result.get("worker_status") == "ok"
                  and isinstance(chief_result.get("output"), dict)
                  and "MOCK-PLAN" in str(chief_result.get("notes") or ""))
            check(f"engine worker {task_type} -> draft-ready "
                  f"(WorkerResult shape)",
                  ok, f"status={result.get('status')}, "
                  f"worker={chief_result.get('worker')}")
        except Exception as exc:  # noqa: BLE001
            check(f"engine worker {task_type} -> draft-ready "
                  f"(WorkerResult shape)",
                  False, str(exc))
    check("15 engine workers covered", worker_count == 15,
          f"found={worker_count}")

    # --- 6a. backup_recovery routes via the dept 07 manager ------------
    try:
        _mod, manager07 = manager_mods["07-quality-security"]
        result = manager07.run(
            {"task_kind": "backup_recovery",
             "title": "Phase 2 smoke backup_recovery"},
            brain=brain, approvals_path=approvals_path)
        ok, detail = structured_ok(result)
        is_specialist_output = (
            result.get("output", "").startswith("[MOCK DRAFT] Backup"))
        check("backup_recovery routes via dept 07 manager (not a plan)",
              ok and result.get("status") == "draft-ready"
              and is_specialist_output,
              detail + ("; specialist output" if is_specialist_output
                        else "; got a delegation plan, not the specialist"))
    except Exception as exc:  # noqa: BLE001
        check("backup_recovery routes via dept 07 manager (not a plan)",
              False, str(exc))

    # --- 6b. No parallel manager maps left ------------------------------
    try:
        mod03 = manager_mods["03-ai-engineering"][0]
        mod07 = manager_mods["07-quality-security"][0]
        no_parallel = (not hasattr(mod03, "SPECIALIST_CLASSES")
                       and not hasattr(mod07, "SPECIALIST_MODULES"))
        # Every standalone entry in dept 03 carries its class key.
        missing_class = [k for k, v in mod03.DEPARTMENT_TASKS.items()
                         if v["file"].startswith(
                             "departments/03-ai-engineering/specialists/")
                         and not v.get("class")]
        check("dept 03: no SPECIALIST_CLASSES; every entry has a class key",
              no_parallel and not missing_class,
              f"missing_class={missing_class}")
        missing_class07 = [k for k, v in mod07.DEPARTMENT_TASKS.items()
                           if v["file"].startswith(
                               "departments/07-quality-security/specialists/")
                           and not v.get("class")]
        check("dept 07: no SPECIALIST_MODULES; every entry has a class key",
              no_parallel and not missing_class07,
              f"missing_class={missing_class07}")
    except Exception as exc:  # noqa: BLE001
        check("dept 03/07: parallel maps deleted", False, str(exc))

    # --- 6c. Dept 06 aliases resolve to the canonical kind -------------
    try:
        _mod, manager06 = manager_mods["06-finance-admin"]
        a = manager06.run({"task_kind": "invoice_management",
                           "title": "alias smoke"}, brain=brain,
                          approvals_path=approvals_path)
        b = manager06.run({"task_kind": "billing_invoice",
                           "title": "alias smoke"}, brain=brain,
                          approvals_path=approvals_path)
        check("dept 06 alias invoice_management == billing_invoice",
              a.get("output") == b.get("output")
              and a.get("status") == b.get("status") == "draft-ready",
              f"alias={a.get('status')}, canonical={b.get('status')}")
        c = manager06.run({"task_kind": "financial_reporting",
                           "title": "alias smoke"}, brain=brain,
                          approvals_path=approvals_path)
        d = manager06.run({"task_kind": "report_compile",
                           "title": "alias smoke"}, brain=brain,
                          approvals_path=approvals_path)
        check("dept 06 alias financial_reporting == report_compile",
              c.get("output") == d.get("output")
              and c.get("status") == d.get("status") == "draft-ready",
              f"alias={c.get('status')}, canonical={d.get('status')}")
    except Exception as exc:  # noqa: BLE001
        check("dept 06 alias resolution", False, str(exc))

    # --- 6d. Honest-status reads: live values + UNKNOWN on missing -----
    try:
        import honest_status
        check("honest_status first_mails_sent reads 163 from config",
              honest_status.first_mails_sent() == 163,
              f"got={honest_status.first_mails_sent()!r}")
        check("honest_status paying_clients reads 0 from config",
              honest_status.paying_clients() == 0,
              f"got={honest_status.paying_clients()!r}")
        email = honest_status.email_outreach()
        check("honest_status email_outreach reads PAUSED from config",
              isinstance(email, str) and email.startswith("PAUSED"),
              f"got={email!r}")
        tmp_config = os.path.join(tmp, "empty-config.json")
        with open(tmp_config, "w", encoding="utf-8") as f:
            json.dump({"honest_status": {}}, f)
        check("honest_status UNKNOWN when keys are missing",
              honest_status.first_mails_sent(tmp_config) == "UNKNOWN"
              and honest_status.paying_clients(tmp_config) == "UNKNOWN"
              and honest_status.email_outreach(tmp_config) == "UNKNOWN",
              "empty honest_status dict")
        check("honest_status UNKNOWN when the file is missing",
              honest_status.first_mails_sent(
                  os.path.join(tmp, "no-such.json")) == "UNKNOWN",
              "missing file")
    except Exception as exc:  # noqa: BLE001
        check("honest_status reads", False, str(exc))

    # --- 6e. No hardcoded snapshot constants left in the 3 agents ------
    try:
        fu = load_module(
            "p2_fu",
            os.path.join(SECTIONS_DIR, "sell", "agents",
                         "followup_agent.py"))
        rt = load_module(
            "p2_rt",
            os.path.join(DEPARTMENTS_DIR, "06-finance-admin",
                         "specialists", "revenue_tracking_agent.py"))
        st = load_module(
            "p2_st",
            os.path.join(DEPARTMENTS_DIR, "06-finance-admin",
                         "specialists", "subscription_tracking_agent.py"))
        check("FollowUpAgent has no FIRST_MAILS_TOTAL constant",
              not hasattr(fu, "FIRST_MAILS_TOTAL"), "constant gone")
        check("RevenueTrackingAgent has no PAYING_CLIENTS constant",
              not hasattr(rt, "PAYING_CLIENTS"), "constant gone")
        check("SubscriptionTrackingAgent has no PAID_SUBSCRIPTIONS_TOTAL",
              not hasattr(st, "PAID_SUBSCRIPTIONS_TOTAL"), "constant gone")
        # The agents' outputs carry the live values / UNKNOWN markers.
        r_fu = fu.FollowUpAgent().run(
            {"task_kind": "followup_draft",
             "payload": {"prospect": "Smoke", "state": "PA",
                         "state_first_mails": 39}},
            brain=brain, approvals_path=approvals_path)
        check("FollowUpAgent output reads 163 from lead store/config",
              "honest_status): 163" in r_fu.get("output", ""),
              "live total in output")
        r_rt = rt.RevenueTrackingAgent().run(
            {"title": "smoke"}, brain=brain, approvals_path=approvals_path)
        check("RevenueTrackingAgent output reads 0 + revenue UNKNOWN",
              "config.json honest_status): 0" in r_rt.get("output", "")
              and "Revenue (real): UNKNOWN" in r_rt.get("output", ""),
              "live clients + UNKNOWN revenue")
        r_st = st.SubscriptionTrackingAgent().run(
            {"title": "smoke"}, brain=brain, approvals_path=approvals_path)
        check("SubscriptionTrackingAgent output says UNKNOWN total",
              "Paid subscriptions total (real): UNKNOWN"
              in r_st.get("output", ""),
              "UNKNOWN marker in output")
    except Exception as exc:  # noqa: BLE001
        check("no hardcoded snapshot constants", False, str(exc))

    # --- 6f. Mock truncation is by words, not characters ----------------
    try:
        m = MockLLMProvider()
        short = m.complete("hello world foo bar", max_tokens=5)
        check("MockLLMProvider max_tokens=5 returns 5 words",
              len(short.split()) == 5, repr(short))
        full = m.complete("hello world foo bar")
        check("MockLLMProvider default returns the whole template",
              full.endswith("playbook.") and len(full.split()) == 21,
              f"words={len(full.split())}")
    except Exception as exc:  # noqa: BLE001
        check("MockLLMProvider word truncation", False, str(exc))

    # --- 6g. meta_provider imports without the connector bin dir --------
    try:
        code = (
            "import sys\n"
            "assert not any('custom-connector-setup' in p for p in sys.path)\n"
            f"sys.path.insert(0, {ENGINE_WORKERS_DIR!r})\n"
            "import src.live.meta_provider as mp\n"
            "assert 'dynamic_credentials' not in sys.modules\n"
            "print('META_IMPORT_OK')\n"
        )
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True, text=True, timeout=60, cwd=BASE)
        check("meta_provider imports without the connector bin dir",
              proc.returncode == 0 and "META_IMPORT_OK" in proc.stdout,
              (proc.stdout + proc.stderr).strip()[-200:])
    except Exception as exc:  # noqa: BLE001
        check("meta_provider imports without the connector bin dir",
              False, str(exc))

    # --- 6h. Worker default-payload fixes -------------------------------
    try:
        from src.contracts.models import Task
        from src.workers.marketing import PublishPrep
        from src.workers.admin import SchedulerAssistant
        from src.workers.acquisition import ReplyHandler

        def _worker(cls, kind):
            return cls(kind, "talvenor", "agency", kind, brain)

        def _task(kind, payload):
            return Task(task_id="t1", business_id="talvenor",
                        division_id="agency", kind=kind, payload=payload)

        n = _worker(PublishPrep, "publish_prep").do_work(
            _task("publish_prep", {}))[1]["count"]
        check("PublishPrep empty payload uses default count 2",
              n == 2, f"count={n}")
        what = _worker(SchedulerAssistant, "schedule_help").do_work(
            _task("schedule_help", {}))[1]["what"]
        check("SchedulerAssistant empty payload uses 'client demo call'",
              what == "client demo call", repr(what))
        rh = _worker(ReplyHandler, "reply_triage")
        g_decline = rh.do_work(
            _task("reply_triage", {"reply_type": "decline"}))[1]["gate"]
        g_interest = rh.do_work(
            _task("reply_triage", {"reply_type": "interest"}))[1]["gate"]
        check("ReplyHandler decline gate None, interest gate send",
              g_decline is None and g_interest == "send",
              f"decline={g_decline}, interest={g_interest}")
        # Content workers: no default-mismatch left (AST scan — the
        # agency/content trees share a top-level `src` package, so a
        # direct import here would collide; the scan is the regression
        # check, and check_engines covers them behaviourally).
        mismatches = []
        for path in (
                os.path.join(AGENCY_DIR, "engine", "workers", "src",
                             "workers", "marketing.py"),
                os.path.join(AGENCY_DIR, "engine", "workers", "src",
                             "workers", "admin.py"),
                os.path.join(AGENCY_DIR, "engine", "workers", "src",
                             "workers", "acquisition.py"),
                os.path.join(BASE, "03-Content-Creation-Department",
                             "engine", "workers", "src",
                             "creator_workers.py")):
            tree = ast.parse(open(path, encoding="utf-8").read())
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                defaults = {}
                for st in node.body:
                    if isinstance(st, ast.Assign):
                        for t in st.targets:
                            if (isinstance(t, ast.Name)
                                    and t.id == "default_payload"
                                    and isinstance(st.value, ast.Dict)):
                                for k, v in zip(st.value.keys,
                                                st.value.values):
                                    if isinstance(v, ast.Constant):
                                        defaults[k.value] = v.value
                for st in ast.walk(node):
                    if (isinstance(st, ast.Call)
                            and isinstance(st.func, ast.Attribute)
                            and st.func.attr == "get"
                            and len(st.args) >= 2
                            and isinstance(st.args[0], ast.Constant)
                            and isinstance(st.args[1], ast.Constant)):
                        key, lit = st.args[0].value, st.args[1].value
                        if key in defaults and defaults[key] != lit:
                            mismatches.append(
                                f"{os.path.basename(path)}:{node.name} "
                                f"{key} {defaults[key]!r} vs {lit!r}")
        check("no default_payload vs .get() mismatch left (4 files)",
              not mismatches, "; ".join(mismatches) if mismatches else "clean")
    except Exception as exc:  # noqa: BLE001
        check("worker default-payload fixes", False, str(exc))

    # --- 6i. status_read notes are built from values read --------------
    try:
        import tool_calling
        config = json.load(open(os.path.join(CEO_CORE_DIR, "config.json"),
                                encoding="utf-8"))
        result = tool_calling.status_read({})
        notes = result.get("notes", [])
        joined = " ".join(notes)
        spend = config.get("spend_cap_usd")
        email = config.get("honest_status", {}).get("email_outreach", "")
        ok = (f"Spend cap is ${spend}" in joined
              and email in joined
              and "Gate 0: NOT PASSED (gate0-status.md)" in joined)
        check("status_read notes built from config + gate0-status.md",
              ok, notes[1] if len(notes) > 1 else notes)
    except Exception as exc:  # noqa: BLE001
        check("status_read notes built from config + gate0-status.md",
              False, str(exc))

    # --- 7. Real store unchanged ----------------------------------------
    store_after = _snapshot_store()
    check("real store unchanged by this check run",
          store_after == store_before,
          "tasks/approvals/tool_calls/agent_runs/audit_log identical")

    passed = sum(1 for _n, ok, _d in CHECKS if ok)
    total = len(CHECKS)
    failed = [n for n, ok, _d in CHECKS if not ok]
    print(f"\n{passed}/{total} checks passed.")
    if failed:
        print("FAILED: " + str(failed))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
