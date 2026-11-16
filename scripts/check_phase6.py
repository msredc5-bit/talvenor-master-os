#!/usr/bin/env python3
"""Phase 6 self-check — Talvenor Master OS, Brain + Runner.

যাচাই করে:
  1. Vendored agency workers import with ONLY the repo on sys.path
     (python3 -I, clean env) — no boss-ceo path anywhere
  2. Vendored content workers import the same way — no
     creator-os-combined path anywhere
  3. Neither Chief (nor brain.py) references ~/workspace/boss-ceo or
     ~/workspace/creator-os-combined
  4. BrainFactory returns each department's own mock by default
     (agency MockLLMProvider, content MockLLM), 0 calls, $0
  5. Vendored live provider class imports + constructs with NO network
     call (0 calls, fast return)
  6. Live-mode temp config returns the live brain; bad mode raises
  7. run_office.py smoke: agency draft task on a TEMP store
  8. run_office.py smoke: gated action -> PENDING on a TEMP store
  9. run_office.py smoke: content draft, [MOCK DRAFT] labelled
 10. run_office.py --drain-queue on a TEMP store (max respected,
     mixed businesses, Chief log entries preserved)
 11. config.json phase 6 + v0.6.0 + brain mock + 3 businesses +
     phase_6 entry + vendored reused_systems
 12. No live 136 scope remains in repo docs (only DROPPED notes)
 13. Real store untouched (tasks 0 records, approvals 0 records)
 14. check_phase0/1/2/3/4 + check_engines still PASS

Every store-touching step uses TEMP files only. Stdlib only, no
network, no send, no publish, no spend, no delete. Exit 0 = PASS.
"""

import json
import os
import subprocess
import sys
import tempfile
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

OUTSIDE_DIRS = ("boss-ceo", "creator-os-combined")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _isolated_import_test(workers_dir, imports_code, label):
    """Run `python3 -I -c` with ONLY the repo on sys.path.

    The repo itself lives under ~/workspace, so the assertion is on
    the specific outside dirs (boss-ceo / creator-os-combined), never
    on the word "workspace".
    """
    code = (
        "import sys\n"
        f"sys.path.insert(0, {workers_dir!r})\n"
        f"sys.path.insert(0, {CEO_CORE_DIR!r})\n"
        + imports_code +
        "assert not any(d in p for p in sys.path for d in "
        f"{OUTSIDE_DIRS!r}), sys.path\n"
        f"print({label!r} + ' isolated import OK')\n"
    )
    proc = subprocess.run(
        [sys.executable, "-I", "-c", code],
        capture_output=True, text=True, timeout=120, cwd=BASE)
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()[-300:]


def main():
    # 1. Agency workers: isolated import, repo-only sys.path
    try:
        agency_dir = os.path.join(BASE, "01-Agency-Department", "engine", "workers")
        code = (
            "from src.mock.provider import MockLLMProvider\n"
            "from src.workers.marketing import CaptionWriter\n"
            "from src.live.meta_provider import MetaSparkProvider\n"
            "import src.mock.provider as _m\n"
            f"assert _m.__file__.startswith({BASE!r}), _m.__file__\n"
            "p = MockLLMProvider(seed='check6')\n"
            "assert p.complete('test prompt').startswith('MOCK-PLAN')\n"
            "assert p.health()['cost_usd'] == 0.0\n"
        )
        ok, detail = _isolated_import_test(agency_dir, code, "agency")
        check("agency workers import isolated (repo-only sys.path)", ok, detail)
    except Exception as e:  # noqa: BLE001
        check("agency workers import isolated (repo-only sys.path)", False, str(e))

    # 2. Content workers: isolated import, repo-only sys.path
    try:
        content_dir = os.path.join(BASE, "03-Content-Creation-Department", "engine", "workers")
        code = (
            "from src.workers.base import MockLLM\n"
            "from src.creator_workers import ScriptWriter\n"
            "import src.workers.base as _b\n"
            f"assert _b.__file__.startswith({BASE!r}), _b.__file__\n"
            "m = MockLLM(seed='check6')\n"
            "assert m.complete('test prompt').startswith('[MOCK DRAFT')\n"
            "assert m.health()['spend_usd'] == 0.0\n"
        )
        ok, detail = _isolated_import_test(content_dir, code, "content")
        check("content workers import isolated (repo-only sys.path)", ok, detail)
    except Exception as e:  # noqa: BLE001
        check("content workers import isolated (repo-only sys.path)", False, str(e))

    # 3. No outside-checkout references in either Chief or brain.py
    try:
        files = [
            os.path.join(BASE, "01-Agency-Department", "chief_of_staff_agency.py"),
            os.path.join(BASE, "03-Content-Creation-Department", "chief_of_staff_content.py"),
            os.path.join(BASE, "00-CEO-Core", "brain.py"),
        ]
        bad = []
        for path in files:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            for needle in ("~/workspace/boss-ceo", "~/workspace/creator-os-combined"):
                if needle in text:
                    bad.append(f"{os.path.basename(path)}: {needle}")
        check("Chiefs + brain.py: no boss-ceo / creator-os-combined refs",
              not bad, "; ".join(bad) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("Chiefs + brain.py: no boss-ceo / creator-os-combined refs", False, str(e))

    # 4. BrainFactory: mock by default, each department's own mock
    try:
        from brain import BrainFactory  # noqa: PLC0415

        assert BrainFactory.get_brain_mode() == "mock"
        agency_brain = BrainFactory.get_brain("agency")
        content_brain = BrainFactory.get_brain("content")
        ok = (
            type(agency_brain).__name__ == "MockLLMProvider"
            and agency_brain.health()["provider"] == "mock"
            and agency_brain.complete("smoke").startswith("MOCK-PLAN")
            and type(content_brain).__name__ == "MockLLM"
            and content_brain.health()["provider"] == "MockLLM"
            and content_brain.complete("smoke").startswith("[MOCK DRAFT")
        )
        check("BrainFactory returns each dept's mock by default ($0)",
              ok, f"agency={type(agency_brain).__name__}, "
              f"content={type(content_brain).__name__}")
    except Exception as e:  # noqa: BLE001
        check("BrainFactory returns each dept's mock by default ($0)", False, str(e))

    # 5. Live provider: import + construct, NO network call (0 calls, fast)
    try:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, "
             f"{os.path.join(BASE, '01-Agency-Department', 'engine', 'workers')!r}); "
             "from src.live.meta_provider import MetaSparkProvider; "
             "p = MetaSparkProvider(); h = p.health(); "
             "assert h['provider'] == 'meta-spark-live' and h['calls'] == 0; "
             "print('live import+construct OK, calls=0')"],
            capture_output=True, text=True, timeout=30, cwd=BASE)
        elapsed = time.time() - t0
        ok = proc.returncode == 0 and elapsed < 10
        check("vendored live provider imports + constructs, 0 calls, no network",
              ok, f"{elapsed:.2f}s, rc={proc.returncode}, "
              + (proc.stdout + proc.stderr).strip()[-200:])
    except Exception as e:  # noqa: BLE001
        check("vendored live provider imports + constructs, 0 calls, no network",
              False, str(e))

    # 6. Live-mode temp config -> live brain; bad mode -> ValueError
    try:
        from brain import BrainFactory  # noqa: PLC0415

        tmpdir = tempfile.mkdtemp()
        live_cfg = os.path.join(tmpdir, "config-live.json")
        with open(live_cfg, "w", encoding="utf-8") as f:
            json.dump({"brain": "live"}, f)
        live_brain = BrainFactory.get_brain("agency", config_path=live_cfg)
        live_ok = (type(live_brain).__name__ == "MetaSparkProvider"
                   and live_brain.health()["calls"] == 0)
        bad_cfg = os.path.join(tmpdir, "config-bad.json")
        with open(bad_cfg, "w", encoding="utf-8") as f:
            json.dump({"brain": "bogus"}, f)
        try:
            BrainFactory.get_brain("agency", config_path=bad_cfg)
            bad_ok = False
        except ValueError:
            bad_ok = True
        check("live-mode config returns live brain; bad mode raises",
              live_ok and bad_ok,
              f"live={type(live_brain).__name__}, bad-mode-raises={bad_ok}")
    except Exception as e:  # noqa: BLE001
        check("live-mode config returns live brain; bad mode raises", False, str(e))

    # 7-10. Runner smoke tests on TEMP stores only
    tmp_store = tempfile.mkdtemp()
    runner = os.path.join(BASE, "scripts", "run_office.py")

    def run_runner(*argv):
        return subprocess.run([sys.executable, runner, *argv],
                              capture_output=True, text=True, timeout=300)

    # 7. Agency draft task
    try:
        proc = run_runner("--business", "agency", "--task", "caption_write",
                          "--input", '{"title": "Phase 6 smoke caption"}',
                          "--store-dir", tmp_store)
        result = json.loads(proc.stdout)
        chief = result["chief_result"]
        tasks = json.load(open(os.path.join(tmp_store, "tasks.json"),
                               encoding="utf-8"))["records"]
        ok = (proc.returncode == 0 and result["status"] == "draft-ready"
              and chief.get("mock_brain") is True and chief.get("draft_only") is True
              and chief.get("worker") == "CaptionWriter"
              and (chief.get("notes") or "").startswith("MOCK-PLAN")
              and len(tasks) == 1 and tasks[0]["status"] == "draft-ready")
        check("run_office smoke: agency draft (mock, DRAFT, logged)", ok,
              f"status={result.get('status')}, worker={chief.get('worker')}")
    except Exception as e:  # noqa: BLE001
        check("run_office smoke: agency draft (mock, DRAFT, logged)", False, str(e))

    # 8. Gated action -> PENDING, nothing executed
    try:
        proc = run_runner("--business", "agency", "--task", "outreach_draft",
                          "--input", '{"title": "Phase 6 smoke send", '
                                     '"gated_action": "send"}',
                          "--store-dir", tmp_store)
        result = json.loads(proc.stdout)
        approvals = json.load(open(os.path.join(tmp_store, "approvals.json"),
                                   encoding="utf-8"))["records"]
        ok = (proc.returncode == 0 and result["status"] == "pending-approval"
              and result.get("approval", {}).get("status") == "pending"
              and len(approvals) == 1 and approvals[0]["status"] == "pending"
              and approvals[0]["action"] == "send")
        check("run_office smoke: gated send -> PENDING, not executed", ok,
              f"status={result.get('status')}, "
              f"approval={result.get('approval', {}).get('status')}")
    except Exception as e:  # noqa: BLE001
        check("run_office smoke: gated send -> PENDING, not executed", False, str(e))

    # 9. Content draft, [MOCK DRAFT] labelled
    try:
        proc = run_runner("--business", "content", "--task", "script_write",
                          "--input", '{"title": "Phase 6 smoke script", '
                                     '"payload": {"topic": "AI tools"}}',
                          "--store-dir", tmp_store)
        result = json.loads(proc.stdout)
        chief = result["chief_result"]
        ok = (proc.returncode == 0 and result["status"] == "draft-ready"
              and chief.get("mock_brain") is True and chief.get("draft_only") is True
              and "[MOCK DRAFT" in (chief.get("notes") or ""))
        check("run_office smoke: content draft ([MOCK DRAFT] labelled)", ok,
              f"status={result.get('status')}, worker={chief.get('worker')}")
    except Exception as e:  # noqa: BLE001
        check("run_office smoke: content draft ([MOCK DRAFT] labelled)", False, str(e))

    # 10. Drain queue: 3 queued (agency + content mix), max 2
    try:
        drain_store = tempfile.mkdtemp()
        seed = [
            {"id": "q1", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "Q1 caption", "payload": {}},
            {"id": "q2", "status": "queued", "business": "content",
             "type": "caption_write", "title": "Q2 caption", "payload": {}},
            {"id": "q3", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "Q3 over max", "payload": {}},
        ]
        with open(os.path.join(drain_store, "tasks.json"), "w", encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": seed}, f)
        proc = run_runner("--drain-queue", "--max", "2",
                          "--store-dir", drain_store)
        summary = json.loads(proc.stdout)
        records = json.load(open(os.path.join(drain_store, "tasks.json"),
                                 encoding="utf-8"))["records"]
        by_id = {r["id"]: r for r in records}
        ok = (proc.returncode == 0
              and len(summary["processed"]) == 2
              and by_id["q1"]["status"] == "done"
              and by_id["q1"]["result"]["status"] == "draft-ready"
              and by_id["q2"]["status"] == "done"
              and by_id["q2"]["result"]["status"] == "draft-ready"
              and by_id["q3"]["status"] == "queued"
              and len(records) == 5)  # 3 queued + 2 Chief log entries kept
        check("run_office --drain-queue: max 2, mixed biz, logs kept", ok,
              f"processed={len(summary.get('processed', []))}, "
              f"records={len(records)}")
    except Exception as e:  # noqa: BLE001
        check("run_office --drain-queue: max 2, mixed biz, logs kept", False, str(e))

    # 11. Config: phase 6 + v0.6.0 + brain mock + 3 businesses + vendored truth
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        phases = cfg.get("honest_status", {}).get("phases", {})
        reused = cfg.get("reused_systems", {})
        ok = (cfg.get("phase", 0) >= 6 and cfg.get("version", "") >= "0.6.0"
              and cfg.get("brain") == "mock"
              and len(cfg.get("businesses", [])) == 3
              and "phase_6_brain_runner" in phases
              and reused.get("engine_15_workers", "").startswith("VENDORED")
              and reused.get("creator_os", "").startswith("VENDORED")
              and "no longer a runtime dependency"
              in reused.get("engine_15_workers", "")
              and "no longer a runtime dependency"
              in reused.get("creator_os", ""))
        check("config.json phase 6 + v0.6.0 + brain mock + 3 biz + vendored",
              ok, f"phase={cfg.get('phase')}, version={cfg.get('version')}, "
              f"brain={cfg.get('brain')}")
    except Exception as e:  # noqa: BLE001
        check("config.json phase 6 + v0.6.0 + brain mock + 3 biz + vendored",
              False, str(e))

    # 12. No live 136 scope in repo docs — only DROPPED notes allowed.
    # (This file itself is excluded: it holds the search pattern.)
    try:
        needles = ("136", "1189", "1,189")
        bad_lines = []
        for root, dirs, files in os.walk(BASE):
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
            for name in files:
                if not name.endswith((".md", ".json", ".html", ".py")):
                    continue
                path = os.path.join(root, name)
                if os.path.abspath(path) == os.path.abspath(__file__):
                    continue
                with open(path, encoding="utf-8", errors="replace") as f:
                    for lineno, line in enumerate(f, 1):
                        if any(n in line for n in needles) and "DROPPED" not in line:
                            bad_lines.append(f"{os.path.relpath(path, BASE)}:{lineno}")
        check("no live 136 scope in repo docs (only DROPPED notes)", not bad_lines,
              "; ".join(bad_lines[:5]) if bad_lines else "clean")
    except Exception as e:  # noqa: BLE001
        check("no live 136 scope in repo docs (only DROPPED notes)", False, str(e))

    # 13. Real store untouched
    try:
        with open(os.path.join(BASE, "store", "tasks.json"), encoding="utf-8") as f:
            real_tasks = json.load(f)
        with open(os.path.join(BASE, "store", "approvals.json"), encoding="utf-8") as f:
            real_appr = json.load(f)
        check("real store untouched (tasks 0, approvals 0)",
              real_tasks.get("records") == [] and real_appr.get("records") == [])
    except Exception as e:  # noqa: BLE001
        check("real store untouched (tasks 0, approvals 0)", False, str(e))

    # 14. Earlier checks still PASS
    try:
        codes = []
        for script in ("check_phase0.py", "check_phase1.py", "check_phase2.py",
                       "check_phase3.py", "check_phase4.py", "check_engines.py"):
            proc = subprocess.run([sys.executable, os.path.join(BASE, "scripts", script)],
                                  capture_output=True, text=True, timeout=300)
            codes.append(proc.returncode)
        ok = all(c == 0 for c in codes)
        check("check_phase0/1/2/3/4 + check_engines still PASS", ok,
              f"p0={codes[0]}, p1={codes[1]}, p2={codes[2]}, p3={codes[3]}, "
              f"p4={codes[4]}, engines={codes[5]}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0/1/2/3/4 + check_engines still PASS", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 6 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
