#!/usr/bin/env python3
"""Phase 3 self-check — 47 specialists (worker code + skills).

2026-11-21: the 4 GAP roles (Ad Campaign, CRM Integration, Expense
Tracking, Backup & Recovery) got worker code — 43 -> 47 specialists,
registry 69 EXISTING / 0 GAP.

Verifies:
  1. The 47 specialist worker files exist (registry.json paths match disk)
  2. All 47 import standalone under python3 -I (stdlib only) +
     class attrs correct (task_kind / gate None / department / role)
  3. The 47 skill files exist (registry.json paths are on disk)
  4. All 47 run in-process in a TEMP store -> draft-ready, [MOCK DRAFT],
     draft_only, mock_brain, gate None
  5. All 47 on a gated action (send) -> pending-approval, in TEMP approvals
     exactly 1 pending record (specialist count per dept = record count)
  6. All 8 managers route the new specialist kinds via run_office.py
     (TEMP store) -> draft-ready, [MOCK DRAFT]
  7. In all 8 depts, gated (send) -> PENDING, exactly 1 pending approval,
     never executes (TEMP store, run_office.py)
  8. GAP roles 0 — the earlier 4 GAP kinds now route via managers to real specialists
     -> draft-ready [MOCK DRAFT]
  9. Registry consistency: 69 EXISTING / 0 ROLE-ONLY / 0 GAP;
     all EXISTING paths are on disk; registry.md's counts table matches
 10. departments/ + registry.md — no stale "manager never executes"
     claims
 11. No forbidden terms in departments/ + registry (Retell Integration /
     PostgreSQL / Sophia Demo / Paperclip / UroNex / NexaFlow /
     90-second demo; Etsy/Amazon only in CLOSED/GATED sentences)
 12. Real store unchanged by this run (Phase 9: live queue)
 13. Old checks (phase0/1/2/3/4 + engines + phase6 + phase7 +
     check_departments 21/21) still PASS

All store-touching steps use TEMP files. Stdlib only, no network,
no send, no publish, no spend, no delete. Exit 0 = PASS.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

AGENCY_DIR = os.path.join(BASE, "01-Agency-Department")
DEPARTMENTS_DIR = os.path.join(AGENCY_DIR, "departments")
REGISTRY_JSON = os.path.join(
    AGENCY_DIR, "agents", "agent-registry", "registry.json")
REGISTRY_MD = os.path.join(
    AGENCY_DIR, "agents", "agent-registry", "registry.md")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# (department folder, chief task type, manager file, manager class)
DEPTS = [
    ("01-sales-growth", "dept_sales", "chief_growth_agent.py",
     "ChiefGrowthAgent"),
    ("02-marketing", "dept_marketing", "marketing_director_agent.py",
     "MarketingDirectorAgent"),
    ("03-ai-engineering", "dept_engineering", "cto_ai_engineering_agent.py",
     "CTOAIEngineeringAgent"),
    ("04-client-operations", "dept_operations",
     "coo_client_operations_agent.py", "COOClientOperationsAgent"),
    ("05-research-strategy", "dept_strategy", "chief_strategy_agent.py",
     "ChiefStrategyAgent"),
    ("06-finance-admin", "dept_finance", "cfo_finance_agent.py",
     "CFOFinanceAgent"),
    ("07-quality-security", "dept_quality",
     "chief_quality_security_agent.py", "ChiefQualitySecurityAgent"),
    ("08-product-innovation", "dept_innovation",
     "chief_innovation_agent.py", "ChiefInnovationAgent"),
]
DEPT_BY_SLUG = {d[0]: d for d in DEPTS}

# Registry department display name -> folder slug
DEPT_SLUG = {
    "01 Sales & Growth": "01-sales-growth",
    "02 Marketing": "02-marketing",
    "03 AI Engineering": "03-ai-engineering",
    "04 Client Operations": "04-client-operations",
    "05 Research & Strategy": "05-research-strategy",
    "06 Finance & Admin": "06-finance-admin",
    "07 Quality & Security": "07-quality-security",
    "08 Product & Innovation": "08-product-innovation",
}


def _norm(s):
    s = s.lower().replace("&", "")
    s = re.sub(r"[-_]", " ", s)
    s = re.sub(r"\bagents?\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _scan_specialists():
    """The 43 specialists on disk: role -> {class, task_kind, dept, path}."""
    out = {}
    for slug, _tt, _mf, _mc in DEPTS:
        d = os.path.join(DEPARTMENTS_DIR, slug, "specialists")
        for name in sorted(os.listdir(d)):
            if not name.endswith(".py"):
                continue
            path = os.path.join(d, name)
            text = open(path, encoding="utf-8").read()
            cls = re.search(r"^class (\w+)", text, re.M).group(1)
            kind = re.search(r"task_kind = \"([^\"]+)\"", text).group(1)
            gate = re.search(r"gate = (\w+)", text).group(1)
            dept = re.search(r"department = \"([^\"]+)\"", text).group(1)
            role = re.search(r"role = \"([^\"]+)\"", text).group(1)
            out[role] = {"class": cls, "task_kind": kind, "gate": gate,
                         "dept": dept, "path": path}
    return out


def _load_file(mod_name, path):
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _snapshot_store():
    """Snapshot of the real store (Phase 9: store is now a live queue — taskboard /
    bridge really writes tasks, so 'empty' is no longer an invariant). The check's
    only job is to prove this run did not change the store."""
    snap = {}
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["tool_calls"] = os.path.exists(
        os.path.join(BASE, "store", "tool_calls.json"))
    return snap


def main():
    store_before = _snapshot_store()
    registry = json.load(open(REGISTRY_JSON, encoding="utf-8"))
    built = [e for e in registry if e["status"] == "EXISTING"
             and e["worker_file"]
             and "/specialists/" in e["worker_file"]]
    scanned = _scan_specialists()

    # 1. 47 specialist files exist (registry path + disk agree)
    try:
        missing = [e["worker_file"] for e in built
                   if not os.path.isfile(os.path.join(BASE, e["worker_file"]))]
        disk_paths = {os.path.relpath(v["path"], BASE)
                      for v in scanned.values()}
        reg_paths = {e["worker_file"] for e in built}
        ok = (len(built) == 47 and len(scanned) == 47
              and not missing and disk_paths == reg_paths)
        check("47 specialist files exist (registry + disk agree)",
              ok, f"registry={len(built)}, disk={len(scanned)}, "
              f"missing={missing}" if missing else
              f"registry={len(built)}, disk={len(scanned)}")
    except Exception as e:  # noqa: BLE001
        check("47 specialist files exist (registry + disk agree)",
              False, str(e))

    # 2. All 47 import standalone (python3 -I) + class attrs
    try:
        payload = [(v["path"], v["class"], v["task_kind"], v["dept"], role)
                   for role, v in sorted(scanned.items())]
        code_lines = ["import importlib.util"]
        code_lines.append(f"SPECS = {payload!r}")
        code_lines.append("out = []")
        code_lines.append("for path, cls, kind, dept, role in SPECS:")
        code_lines.append("    spec = importlib.util.spec_from_file_location('p3_' + kind, path)")
        code_lines.append("    mod = importlib.util.module_from_spec(spec)")
        code_lines.append("    spec.loader.exec_module(mod)")
        code_lines.append("    c = getattr(mod, cls)")
        code_lines.append("    assert c.task_kind == kind, (cls, c.task_kind, kind)")
        code_lines.append("    assert c.gate is None, (cls, c.gate)")
        code_lines.append("    assert c.department == dept, (cls, c.department, dept)")
        code_lines.append("    assert c.role == role, (cls, c.role, role)")
        code_lines.append("    out.append(kind)")
        code_lines.append("print('SPECIALISTS_OK ' + str(len(out)))")
        proc = subprocess.run(
            [sys.executable, "-I", "-c", "\n".join(code_lines)],
            capture_output=True, text=True, timeout=180, cwd=BASE)
        ok = proc.returncode == 0 and "SPECIALISTS_OK 47" in proc.stdout
        detail = (proc.stdout + proc.stderr).strip()[-300:]
        check("47 specialists import standalone + class attrs correct",
              ok, f"47 specialists; " + detail)
    except Exception as e:  # noqa: BLE001
        check("47 specialists import standalone + class attrs correct",
              False, str(e))

    # 3. All 47 skill files exist (registry path on disk)
    try:
        missing = [e["skill_file"] for e in built
                   if not e["skill_file"]
                   or not os.path.isfile(os.path.join(BASE, e["skill_file"]))]
        check("47 specialist skill files exist (registry paths on disk)",
              not missing,
              f"missing={missing}" if missing else "47/47")
    except Exception as e:  # noqa: BLE001
        check("47 specialist skill files exist (registry paths on disk)",
              False, str(e))

    # 4. All 47 run in-process on TEMP store -> draft-ready [MOCK DRAFT]
    for slug, _tt, _mf, _mc in DEPTS:
        try:
            members = {r: v for r, v in scanned.items()
                       if v["dept"] == slug}
            bad = []
            for role, v in sorted(members.items()):
                mod = _load_file("p3_run_" + v["task_kind"], v["path"])
                agent = getattr(mod, v["class"])()
                res = agent.run({"title": f"Phase 3 smoke {v['task_kind']}",
                                 "payload": {}}, brain=None)
                if not (res.get("status") == "draft-ready"
                        and "[MOCK DRAFT]" in (res.get("output") or "")
                        + (res.get("notes") or "")
                        and res.get("draft_only") is True
                        and res.get("mock_brain") is True
                        and res.get("gate") is None):
                    bad.append(v["task_kind"])
            check(f"dept {slug}: {len(members)} specialists run -> "
                  f"draft-ready [MOCK DRAFT]",
                  not bad, f"{len(members) - len(bad)}/{len(members)}; "
                  f"bad={bad}" if bad else f"{len(members)}/{len(members)}")
        except Exception as e:  # noqa: BLE001
            check(f"dept {slug}: specialists run -> draft-ready [MOCK DRAFT]",
                  False, str(e))

    # 5. All 47 gated (send) -> pending-approval, 1 pending record each
    for slug, _tt, _mf, _mc in DEPTS:
        try:
            members = {r: v for r, v in scanned.items()
                       if v["dept"] == slug}
            store = tempfile.mkdtemp()
            appr_path = os.path.join(store, "approvals.json")
            bad = []
            for role, v in sorted(members.items()):
                mod = _load_file("p3_gate_" + v["task_kind"], v["path"])
                agent = getattr(mod, v["class"])()
                res = agent.run(
                    {"title": f"Phase 3 gated smoke {v['task_kind']}",
                     "gated_action": "send"},
                    brain=None, approvals_path=appr_path)
                if res.get("status") != "pending-approval":
                    bad.append((v["task_kind"], res.get("status")))
            records = json.load(
                open(appr_path, encoding="utf-8"))["records"]
            ok = (not bad and len(records) == len(members)
                  and all(r["status"] == "pending" and r["action"] == "send"
                          for r in records))
            check(f"dept {slug}: {len(members)} specialists gated (send) -> "
                  f"PENDING, 1 record each",
                  ok, f"records={len(records)}/{len(members)}; "
                  f"bad={bad}" if (bad or len(records) != len(members))
                  else f"records={len(records)}/{len(members)}")
        except Exception as e:  # noqa: BLE001
            check(f"dept {slug}: specialists gated (send) -> PENDING",
                  False, str(e))

    # 6+7. Managers route specialist kinds end-to-end via run_office.py
    runner = os.path.join(BASE, "scripts", "run_office.py")

    def run_runner(business, task_type, input_data, store_dir):
        return subprocess.run(
            [sys.executable, runner, "--business", business,
             "--task", task_type, "--input", json.dumps(input_data),
             "--store-dir", store_dir],
            capture_output=True, text=True, timeout=300)

    for slug, task_type, _mf, _mc in DEPTS:
        kind = sorted(v["task_kind"] for v in scanned.values()
                      if v["dept"] == slug)[0]
        # 6. Route -> draft-ready [MOCK DRAFT]
        try:
            store = tempfile.mkdtemp()
            proc = run_runner("agency", task_type,
                              {"title": f"Phase 3 route smoke {kind}",
                               "payload": {"task_kind": kind}},
                              store)
            result = json.loads(proc.stdout)
            chief = result.get("chief_result", result)
            ok = (proc.returncode == 0
                  and result.get("status") == "draft-ready"
                  and chief.get("mock_brain") is True
                  and chief.get("draft_only") is True
                  and "[MOCK DRAFT]" in (chief.get("output") or "")
                  + (chief.get("notes") or ""))
            check(f"manager routes {kind} via run_office -> draft-ready",
                  ok, f"status={result.get('status')}")
        except Exception as e:  # noqa: BLE001
            check(f"manager routes {kind} via run_office -> draft-ready",
                  False, str(e))
        # 7. Gated (send) on specialist kind -> PENDING, 1 approval
        try:
            store = tempfile.mkdtemp()
            proc = run_runner("agency", task_type,
                              {"title": f"Phase 3 gated smoke {kind}",
                               "payload": {"task_kind": kind},
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
            check(f"gated {task_type} + {kind} + send -> PENDING, 1 approval",
                  ok, f"status={result.get('status')}, "
                  f"approvals={len(approvals)}")
        except Exception as e:  # noqa: BLE001
            check(f"gated {task_type} + {kind} + send -> PENDING, 1 approval",
                  False, str(e))

    # 8. 0 GAP roles: the 4 former GAP kinds now route via their manager
    #    to a real specialist -> draft-ready [MOCK DRAFT]
    try:
        gaps = [e for e in registry if e["status"] == "GAP"]
        bad = []
        if len(gaps) != 0:
            bad.append(f"gap count={len(gaps)}")
        for kind, slug in (("ad_campaign", "02-marketing"),
                           ("crm_integration", "03-ai-engineering"),
                           ("expense_tracking", "06-finance-admin"),
                           ("backup_recovery", "07-quality-security")):
            _s, _tt, mfile, mcls = DEPT_BY_SLUG[slug]
            mod = _load_file("p3_formergap_mgr_" + slug, os.path.join(
                DEPARTMENTS_DIR, slug, "manager", mfile))
            mgr = getattr(mod, mcls)()
            res = mgr.run({"title": f"Phase 3 former-GAP smoke {kind}",
                           "task_kind": kind}, brain=None)
            if not (res.get("status") == "draft-ready"
                    and "[MOCK DRAFT]" in (res.get("output") or "")
                    + (res.get("notes") or "")
                    and res.get("draft_only") is True
                    and res.get("mock_brain") is True):
                bad.append(f"{kind}: manager status={res.get('status')}")
        check("0 GAP roles: former GAP kinds route via manager -> draft-ready",
              not bad, "; ".join(bad) if bad
              else "ad_campaign / crm_integration / expense_tracking / "
              "backup_recovery")
    except Exception as e:  # noqa: BLE001
        check("0 GAP roles: former GAP kinds route via manager -> draft-ready",
              False, str(e))

    # 9. Registry consistency: 69/0/0, paths on disk, md counts match
    try:
        n_exist = sum(1 for e in registry if e["status"] == "EXISTING")
        n_role = sum(1 for e in registry if e["status"] == "ROLE-ONLY")
        n_gap = sum(1 for e in registry if e["status"] == "GAP")
        missing = [e["worker_file"] for e in registry
                   if e["worker_file"]
                   and not os.path.isfile(os.path.join(BASE, e["worker_file"]))]
        missing += [e["skill_file"] for e in registry
                    if e["skill_file"]
                    and not os.path.isfile(os.path.join(BASE, e["skill_file"]))]
        md = open(REGISTRY_MD, encoding="utf-8").read()
        md_ok = ("| **Total** | **62** | **7** | **69** | **69** | **0** | **0** |"
                 in md)
        ok = (n_exist == 69 and n_role == 0 and n_gap == 0
              and not missing and md_ok)
        check("registry consistent: 69 EXISTING / 0 ROLE-ONLY / 0 GAP",
              ok, f"json={n_exist}/{n_role}/{n_gap}, "
              f"missing={missing}, md_counts={'ok' if md_ok else 'BAD'}")
    except Exception as e:  # noqa: BLE001
        check("registry consistent: 69 EXISTING / 0 ROLE-ONLY / 0 GAP",
              False, str(e))

    # 10. No stale "manager never executes" claims
    try:
        stale = []
        needles = ("No worker executes",
                   "No worker is executing",
                   "does not call the worker",
                   "no worker code, must be done by hand",
                   "All ROLE-ONLY",
                   "GAP department —",
                   "Mapped staff 2",
                   "Boss/Elora do the ROLE-ONLY role's work by hand")
        targets = []
        for slug, _tt, mfile, _mc in DEPTS:
            targets.append(os.path.join(DEPARTMENTS_DIR, slug, "manager",
                                        mfile))
            targets.append(os.path.join(DEPARTMENTS_DIR, slug, "SECTION.md"))
            sdir = os.path.join(DEPARTMENTS_DIR, slug, "skills")
            for name in os.listdir(sdir):
                if name.endswith(".md"):
                    targets.append(os.path.join(sdir, name))
        targets.append(REGISTRY_MD)
        for path in targets:
            text = open(path, encoding="utf-8").read()
            for needle in needles:
                if needle in text:
                    stale.append(f"{os.path.relpath(path, BASE)}: {needle}")
        check("no stale 'manager never executes' claims",
              not stale, "; ".join(stale[:5]) if stale else "clean")
    except Exception as e:  # noqa: BLE001
        check("no stale 'manager never executes' claims", False, str(e))

    # 11. Forbidden terms in departments/ + registry
    try:
        bad = []
        needles = ("Retell Integration", "PostgreSQL", "Sophia Demo",
                   "Paperclip", "UroNex", "NexaFlow", "90-second demo")
        targets = []
        for root, dirs, files in os.walk(DEPARTMENTS_DIR):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for name in files:
                if name.endswith((".py", ".md")):
                    targets.append(os.path.join(root, name))
        targets += [REGISTRY_MD, REGISTRY_JSON,
                    os.path.join(AGENCY_DIR, "chief_of_staff_agency.py")]
        for path in targets:
            text = open(path, encoding="utf-8").read()
            for needle in needles:
                if needle in text:
                    bad.append(f"{os.path.relpath(path, BASE)}: {needle}")
            # Etsy/Amazon only in CLOSED/GATED sentences, not live claims
            for i, line in enumerate(text.split("\n"), 1):
                if ("Etsy" in line or "Amazon" in line) and \
                        "CLOSED" not in line and "GATED" not in line:
                    bad.append(f"{os.path.relpath(path, BASE)}:{i}: "
                               f"live claim? {line.strip()[:60]}")
        check("no forbidden terms in departments/ + registry",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no forbidden terms in departments/ + registry", False, str(e))

    # 12. Real store unchanged by this check run (Phase 9: live queue)
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 13. Earlier checks still PASS
    try:
        codes = []
        names = []
        for script in ("check_phase0.py", "check_phase1.py",
                       "check_phase2.py", "check_phase3.py",
                       "check_phase4.py", "check_engines.py",
                       "check_phase6.py", "check_phase7.py",
                       "check_departments.py"):
            proc = subprocess.run(
                [sys.executable, os.path.join(BASE, "scripts", script)],
                capture_output=True, text=True, timeout=600)
            codes.append(proc.returncode)
            names.append(script.replace("check_", "").replace(".py", ""))
        ok = all(c == 0 for c in codes)
        check("phase0/1/2/3/4 + engines + phase6 + phase7 + departments PASS",
              ok, ", ".join(f"{n}={c}" for n, c in zip(names, codes)))
    except Exception as e:  # noqa: BLE001
        check("phase0/1/2/3/4 + engines + phase6 + phase7 + departments PASS",
              False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 3 (specialists) self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
