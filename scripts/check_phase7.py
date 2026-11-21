#!/usr/bin/env python3
"""Phase 7 self-check — Talvenor Master OS, Full Offices (sections).

Verifies:
  1. Each of the 16 sections has a SECTION.md
     (Agency 5, Products 6, Content 5)
  2. The 23 new section agent files exist + under python3 -I
     they import standalone (stdlib only) + class attrs correct
     (task_kind / gate / section / role)
  3. The 23 section skill files exist (one per agent)
  4. The Agency's 15 mapped staff have engine skills + names in SECTION.md
  5. The Chiefs route the new task types (run_office.py, TEMP store):
     agency client_intake / followup_draft, products kit_qa,
     content plan_weekly — draft-ready, [MOCK DRAFT]
  6. Gated action -> PENDING, never executes (TEMP store):
     agency followup_draft + send, products kit_sales + send,
     content growth_research + send — exactly 1 pending approval in each
  7. Gate 0 fail-closed: KitBuilder / LaunchManager -> blocked-gate0
     (mark_sold / mark_launched payloads too); the KitSales draft has a
     "Gate 0 NOT passed" warning; no section file has
     "status": "sold" / "launched"
  8. Content: VisualProducer wrapper -> video_file None +
     missing-inputs; no section .py has YOUTUBE_UPLOAD_ENABLED /
     no upload_youtube( call (upload OFF)
  9. New section files have no ~/workspace/boss-ceo /
     ~/workspace/creator-os-combined reference
 10. config.json phase 11 + v0.9.0 + brain mock + 3 business +
     phase_7_sections + agentic_phase_3 + unified_os + phase_9 entry
     + phase_11 entry (2026-11-21: config drift fix D1 — phase 9 -> 11)
 11. Real store unchanged by this run (Phase 9: live queue)
 12. Old checks (phase0/1/2/3/4 + engines + phase6) still PASS

Chief-level tests run in a run_office.py subprocess (to avoid the vendored `src` collision of two Chiefs in one process).
Agent run() tests
are in-process: agency + products agents with a brain, content wrappers
in a separate subprocess (content brain only). All store-touching steps
use TEMP files. Stdlib only, no network, no send, no publish,
no spend, no delete. Exit 0 = PASS.
"""

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
PRODUCTS_DIR = os.path.join(BASE, "02-Digital-Product-Department")
CONTENT_DIR = os.path.join(BASE, "03-Content-Creation-Department")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# section -> (agent file, class, task_kind, gate)
AGENCY_AGENTS = {
    "receive": [
        ("client_intake_receiver.py", "ClientIntakeReceiverAgent",
         "client_intake", "send"),
    ],
    "sell": [
        ("sales_closer.py", "SalesCloserAgent", "sales_close", "ok"),
        ("followup_agent.py", "FollowUpAgent", "followup_draft", "send"),
    ],
    "delivery": [
        ("service_delivery_manager.py", "ServiceDeliveryManagerAgent",
         "delivery_manage", "ok"),
        ("client_success_agent.py", "ClientSuccessAgent",
         "client_success", "send"),
    ],
    "ops": [
        ("billing_invoice_agent.py", "BillingInvoiceAgent",
         "billing_invoice", "ok"),
    ],
}
AGENCY_SECTIONS = ["receive", "sell", "delivery", "marketing", "ops"]
AGENCY_MAPPED = {  # staff -> (engine skill file, section)
    "ProspectResearcher": ("prospect-researcher.md", "receive"),
    "InboxTriager": ("inbox-triager.md", "receive"),
    "SchedulerAssistant": ("scheduler.md", "receive"),
    "OutreachDrafter": ("outreach-drafter.md", "sell"),
    "ReplyHandler": ("reply-triager.md", "sell"),
    "NegotiationCoach": ("negotiation-coach.md", "sell"),
    "ObjectionSimulator": ("objection-simulator.md", "sell"),
    "RetellBuilder": ("receptionist-builder.md", "delivery"),
    "QAEngineer": ("qa-engineer.md", "delivery"),
    "OnboardingAgent": ("onboarding-agent.md", "delivery"),
    "ContentPlanner": ("content-planner.md", "marketing"),
    "VideoProducer": ("video-producer.md", "marketing"),
    "CaptionWriter": ("caption-writer.md", "marketing"),
    "PublishPrep": ("publish-prep.md", "marketing"),
    "ReportCompiler": ("report-compiler.md", "ops"),
}

PRODUCTS_AGENTS = {
    "product": [
        ("kit_builder.py", "KitBuilderAgent", "kit_build", "ok"),
        ("kit_qa.py", "KitQAAgent", "kit_qa", "ok"),
    ],
    "research": [
        ("clinic_researcher.py", "ClinicResearcherAgent",
         "clinic_research", None),
    ],
    "launch": [
        ("launch_manager.py", "LaunchManagerAgent", "launch_prep", "go"),
    ],
    "sales": [
        ("kit_sales.py", "KitSalesAgent", "kit_sales", "send"),
    ],
    "support": [
        ("support_drafter.py", "SupportDrafterAgent",
         "support_draft", "send"),
    ],
    "finance": [
        ("payment_rails_checker.py", "PaymentRailsCheckerAgent",
         "gate0_check", None),
    ],
}
PRODUCTS_SECTIONS = ["product", "research", "launch", "sales",
                     "support", "finance"]

CONTENT_AGENTS = {
    "plan": [
        ("topic_researcher.py", "TopicResearcherAgent",
         "content_plan", "ok"),
        ("content_planner.py", "ContentPlannerAgent",
         "plan_weekly", "ok"),
    ],
    "produce": [
        ("script_writer.py", "ScriptWriterAgent", "script_write", "ok"),
        ("visual_producer.py", "VisualProducerAgent",
         "video_produce", "ok"),
    ],
    "publish": [
        ("caption_writer.py", "CaptionWriterAgent", "caption_write", "ok"),
        ("publish_prep.py", "PublishPrepAgent", "publish_prep", "post it"),
    ],
    "analyze": [
        ("performance_tracker.py", "PerformanceTrackerAgent",
         "performance_track", "ok"),
        ("performance_analyst.py", "PerformanceAnalystAgent",
         "performance_analyze", "ok"),
    ],
    "growth": [
        ("growth_agent.py", "GrowthAgent", "growth_research", "send"),
        ("repurpose_agent.py", "RepurposeAgent", "repurpose_plan", "ok"),
    ],
}
CONTENT_SECTIONS = ["plan", "produce", "publish", "analyze", "growth"]

ALL_AGENTS = []
for dept_dir, sections, mapping in (
        (AGENCY_DIR, AGENCY_SECTIONS, AGENCY_AGENTS),
        (PRODUCTS_DIR, PRODUCTS_SECTIONS, PRODUCTS_AGENTS),
        (CONTENT_DIR, CONTENT_SECTIONS, CONTENT_AGENTS)):
    for section, agents in mapping.items():
        for fname, cls, kind, gate in agents:
            ALL_AGENTS.append((dept_dir, section, fname, cls, kind, gate))


def _load_agent_file(path):
    spec = importlib.util.spec_from_file_location(
        "p7_agent_" + os.path.splitext(os.path.basename(path))[0], path)
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
    # 1. All 16 SECTION.md files exist
    try:
        missing = []
        for dept_dir, sections in (
                (AGENCY_DIR, AGENCY_SECTIONS),
                (PRODUCTS_DIR, PRODUCTS_SECTIONS),
                (CONTENT_DIR, CONTENT_SECTIONS)):
            for section in sections:
                path = os.path.join(dept_dir, "sections", section,
                                    "SECTION.md")
                if not os.path.isfile(path):
                    missing.append(os.path.relpath(path, BASE))
        check("16 section SECTION.md files exist", not missing,
              f"missing={missing}" if missing else "5 agency + 6 products + 5 content")
    except Exception as e:  # noqa: BLE001
        check("16 section SECTION.md files exist", False, str(e))

    # 2. All 23 agent files import standalone (python3 -I) + class attrs
    try:
        code_lines = ["import importlib.util, json, sys"]
        payload = []
        for dept_dir, section, fname, cls, kind, gate in ALL_AGENTS:
            path = os.path.join(dept_dir, "sections", section,
                                "agents", fname)
            payload.append((path, cls, kind, gate, section))
        code_lines.append(f"AGENTS = {payload!r}")
        code_lines.append("out = []")
        code_lines.append("for path, cls, kind, gate, section in AGENTS:")
        code_lines.append("    spec = importlib.util.spec_from_file_location('a_' + cls, path)")
        code_lines.append("    mod = importlib.util.module_from_spec(spec)")
        code_lines.append("    spec.loader.exec_module(mod)")
        code_lines.append("    c = getattr(mod, cls)")
        code_lines.append("    assert c.task_kind == kind, (cls, c.task_kind, kind)")
        code_lines.append("    assert c.gate == gate, (cls, c.gate, gate)")
        code_lines.append("    assert c.section == section, (cls, c.section, section)")
        code_lines.append("    assert isinstance(c.role, str) and c.role")
        code_lines.append("    out.append(cls)")
        code_lines.append("print('AGENTS_OK ' + ','.join(out))")
        proc = subprocess.run(
            [sys.executable, "-I", "-c", "\n".join(code_lines)],
            capture_output=True, text=True, timeout=120, cwd=BASE)
        ok = proc.returncode == 0 and "AGENTS_OK" in proc.stdout
        detail = (proc.stdout + proc.stderr).strip()[-300:]
        check("23 section agents import standalone + class attrs correct",
              ok, f"{len(ALL_AGENTS)} agents; " + detail)
    except Exception as e:  # noqa: BLE001
        check("23 section agents import standalone + class attrs correct",
              False, str(e))

    # 3. All 23 section skill files exist
    try:
        missing = []
        for dept_dir, section, fname, cls, kind, gate in ALL_AGENTS:
            skill = fname[:-3].replace("_", "-") + ".md"
            path = os.path.join(dept_dir, "sections", section,
                                "skills", skill)
            if not os.path.isfile(path):
                missing.append(os.path.relpath(path, BASE))
        check("23 section skill files exist (one per agent)", not missing,
              f"missing={missing}" if missing else "6 agency + 7 products + 10 content")
    except Exception as e:  # noqa: BLE001
        check("23 section skill files exist (one per agent)", False, str(e))

    # 4. 15 mapped agency staff: engine skill exists + named in SECTION.md
    try:
        missing = []
        for worker, (skill, section) in AGENCY_MAPPED.items():
            skill_path = os.path.join(AGENCY_DIR, "engine", "skills", skill)
            if not os.path.isfile(skill_path):
                missing.append(f"skill:{skill}")
            section_path = os.path.join(AGENCY_DIR, "sections", section,
                                        "SECTION.md")
            with open(section_path, encoding="utf-8") as f:
                if worker not in f.read():
                    missing.append(f"SECTION.md:{section}:{worker}")
        check("15 mapped agency staff: engine skill + SECTION.md mention",
              not missing, f"missing={missing}" if missing else "15/15")
    except Exception as e:  # noqa: BLE001
        check("15 mapped agency staff: engine skill + SECTION.md mention",
              False, str(e))

    # 5+6. Chief routing + gated PENDING via run_office.py (TEMP stores)
    runner = os.path.join(BASE, "scripts", "run_office.py")

    def run_runner(business, task_type, input_data, store_dir):
        return subprocess.run(
            [sys.executable, runner, "--business", business,
             "--task", task_type, "--input", json.dumps(input_data),
             "--store-dir", store_dir],
            capture_output=True, text=True, timeout=300)

    tmp_store = tempfile.mkdtemp()

    # 5a. Agency new type via Chief -> draft-ready, [MOCK DRAFT]
    try:
        proc = run_runner("agency", "client_intake",
                          {"title": "Phase 7 smoke intake"}, tmp_store)
        result = json.loads(proc.stdout)
        chief = result.get("chief_result", result)
        ok = (proc.returncode == 0 and result.get("status") == "draft-ready"
              and chief.get("mock_brain") is True
              and chief.get("draft_only") is True
              and "[MOCK DRAFT]" in (chief.get("output") or "")
              + (chief.get("notes") or ""))
        check("Chief routes agency client_intake -> draft-ready [MOCK DRAFT]",
              ok, f"status={result.get('status')}, "
              f"worker={chief.get('worker')}")
    except Exception as e:  # noqa: BLE001
        check("Chief routes agency client_intake -> draft-ready [MOCK DRAFT]",
              False, str(e))

    # 5b. Products new type via Chief -> draft-ready
    try:
        proc = run_runner("products", "kit_qa",
                          {"title": "Phase 7 smoke kit QA"}, tmp_store)
        result = json.loads(proc.stdout)
        chief = result.get("chief_result", result)
        ok = (proc.returncode == 0 and result.get("status") == "draft-ready"
              and chief.get("mock_brain") is True
              and "[MOCK DRAFT]" in (chief.get("output") or "")
              + (chief.get("notes") or ""))
        check("Chief routes products kit_qa -> draft-ready [MOCK DRAFT]",
              ok, f"status={result.get('status')}, "
              f"worker={chief.get('worker')}")
    except Exception as e:  # noqa: BLE001
        check("Chief routes products kit_qa -> draft-ready [MOCK DRAFT]",
              False, str(e))

    # 5c. Content new type via Chief -> draft-ready
    try:
        proc = run_runner("content", "plan_weekly",
                          {"title": "Phase 7 smoke weekly plan"}, tmp_store)
        result = json.loads(proc.stdout)
        chief = result.get("chief_result", result)
        ok = (proc.returncode == 0 and result.get("status") == "draft-ready"
              and chief.get("mock_brain") is True
              and "[MOCK DRAFT]" in (chief.get("output") or "")
              + (chief.get("notes") or ""))
        check("Chief routes content plan_weekly -> draft-ready [MOCK DRAFT]",
              ok, f"status={result.get('status')}, "
              f"worker={chief.get('worker')}")
    except Exception as e:  # noqa: BLE001
        check("Chief routes content plan_weekly -> draft-ready [MOCK DRAFT]",
              False, str(e))

    # 6. Gated actions -> PENDING, exactly 1 pending approval each
    for business, task_type, label in (
            ("agency", "followup_draft", "agency followup_draft + send"),
            ("products", "kit_sales", "products kit_sales + send"),
            ("content", "growth_research", "content growth_research + send")):
        try:
            store = tempfile.mkdtemp()
            proc = run_runner(business, task_type,
                              {"title": f"Phase 7 smoke gated {label}",
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

    # 7. Gate 0 fail-closed (direct agent run, TEMP approvals)
    try:
        from brain import BrainFactory  # noqa: PLC0415

        agency_brain = BrainFactory.get_brain("agency")
        tmp_appr = os.path.join(tempfile.mkdtemp(), "approvals.json")
        prod_dir = os.path.join(PRODUCTS_DIR, "sections")

        kb = _load_agent_file(os.path.join(
            prod_dir, "product", "agents", "kit_builder.py"))
        kb_result = kb.KitBuilderAgent().run(
            {"type": "kit_build", "title": "P7 gate0 kit_build"},
            brain=agency_brain, approvals_path=tmp_appr)
        kb_sold = kb.KitBuilderAgent().run(
            {"type": "kit_build", "title": "P7 gate0 mark_sold",
             "payload": {"mark_sold": True}},
            brain=agency_brain, approvals_path=tmp_appr)
        lm = _load_agent_file(os.path.join(
            prod_dir, "launch", "agents", "launch_manager.py"))
        lm_result = lm.LaunchManagerAgent().run(
            {"type": "launch_prep", "title": "P7 gate0 launch"},
            brain=agency_brain, approvals_path=tmp_appr)
        lm_launched = lm.LaunchManagerAgent().run(
            {"type": "launch_prep", "title": "P7 gate0 mark_launched",
             "payload": {"mark_launched": True}},
            brain=agency_brain, approvals_path=tmp_appr)
        ks = _load_agent_file(os.path.join(
            prod_dir, "sales", "agents", "kit_sales.py"))
        ks_result = ks.KitSalesAgent().run(
            {"type": "kit_sales", "title": "P7 gate0 kit_sales"},
            brain=agency_brain, approvals_path=tmp_appr)
        ok = (kb_result.get("status") == "blocked-gate0"
              and kb_sold.get("status") == "blocked-gate0"
              and lm_result.get("status") == "blocked-gate0"
              and lm_launched.get("status") == "blocked-gate0"
              and ks_result.get("status") == "draft-ready"
              and "Gate 0 NOT passed" in (ks_result.get("output") or "")
              + (ks_result.get("notes") or ""))
        check("Gate 0 fail-closed: kit_build/launch blocked, kit_sales warns",
              ok, f"kit_build={kb_result.get('status')}, "
              f"mark_sold={kb_sold.get('status')}, "
              f"launch={lm_result.get('status')}, "
              f"mark_launched={lm_launched.get('status')}, "
              f"kit_sales={ks_result.get('status')}")
    except Exception as e:  # noqa: BLE001
        check("Gate 0 fail-closed: kit_build/launch blocked, kit_sales warns",
              False, str(e))

    # 7b. No "sold"/"launched" success status in products section code
    try:
        bad = []
        for root, _dirs, files in os.walk(
                os.path.join(PRODUCTS_DIR, "sections")):
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                for needle in ('"status": "sold"', '"status": "launched"',
                               "'status': 'sold'", "'status': 'launched'"):
                    if needle in text:
                        bad.append(os.path.relpath(path, BASE))
        check("no sold/launched success status in products section code",
              not bad, "; ".join(bad) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no sold/launched success status in products section code",
              False, str(e))

    # 8. Content: VisualProducer -> video_file None; no upload code path
    try:
        code = (
            "import importlib.util, json, sys\n"
            "sys.path.insert(0, " + repr(CEO_CORE_DIR) + ")\n"
            "from brain import BrainFactory\n"
            "path = " + repr(os.path.join(
                CONTENT_DIR, "sections", "produce", "agents",
                "visual_producer.py")) + "\n"
            "spec = importlib.util.spec_from_file_location('vp', path)\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            "brain = BrainFactory.get_brain('content')\n"
            "r = mod.VisualProducerAgent().run("
            "{'type': 'video_produce', 'title': 'P7 smoke visual'}, "
            "brain=brain)\n"
            "print('VP ' + json.dumps({"
            "'status': r.get('status'), "
            "'video_file': r.get('video_file'), "
            "'video_built': r.get('video_built'), "
            "'missing': len(r.get('missing_inputs') or [])}, "
            "ensure_ascii=False))\n"
        )
        proc = subprocess.run(
            [sys.executable, "-I", "-c", code],
            capture_output=True, text=True, timeout=120, cwd=BASE)
        line = [ln for ln in proc.stdout.splitlines()
                if ln.startswith("VP ")]
        vp = json.loads(line[0][3:]) if line else {}
        ok = (proc.returncode == 0
              and vp.get("status") == "draft-ready"
              and vp.get("video_file") is None
              and vp.get("video_built") is False
              and (vp.get("missing") or 0) >= 1)
        check("VisualProducer wrapper: video_file None, missing-inputs listed",
              ok, f"rc={proc.returncode}, {vp}, "
              + (proc.stderr.strip()[-200:] if proc.returncode else ""))
    except Exception as e:  # noqa: BLE001
        check("VisualProducer wrapper: video_file None, missing-inputs listed",
              False, str(e))

    try:
        bad = []
        for root, _dirs, files in os.walk(BASE):
            if "__pycache__" in root:
                continue
            if os.path.join("03-Content-Creation-Department", "sections") \
                    not in root and "sections" not in root:
                continue
            for name in files:
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                if "/sections/" not in path.replace(os.sep, "/"):
                    continue
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                # Only real code paths count: env-flag reads / upload calls.
                # Prose mentions (e.g. "needs YOUTUBE_UPLOAD_ENABLED=1")
                # in docstrings are not a code path.
                for needle in ('os.getenv("YOUTUBE_UPLOAD_ENABLED"',
                               "os.getenv('YOUTUBE_UPLOAD_ENABLED'",
                               'os.environ.get("YOUTUBE_UPLOAD_ENABLED"',
                               "os.environ.get('YOUTUBE_UPLOAD_ENABLED'",
                               'os.environ["YOUTUBE_UPLOAD_ENABLED"',
                               "os.environ['YOUTUBE_UPLOAD_ENABLED'",
                               '"YOUTUBE_UPLOAD_ENABLED" in os.environ',
                               "'YOUTUBE_UPLOAD_ENABLED' in os.environ",
                               "upload_youtube(",
                               "import upload_youtube",
                               "from upload_youtube"):
                    if needle in text:
                        bad.append(f"{os.path.relpath(path, BASE)}: {needle}")
        check("no upload code path in any section .py (upload OFF)",
              not bad, "; ".join(bad) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no upload code path in any section .py (upload OFF)",
              False, str(e))

    # 9. No outside-checkout refs in new section files
    try:
        bad = []
        for dept_dir in (AGENCY_DIR, PRODUCTS_DIR, CONTENT_DIR):
            for root, dirs, files in os.walk(
                    os.path.join(dept_dir, "sections")):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for name in files:
                    path = os.path.join(root, name)
                    with open(path, encoding="utf-8",
                              errors="replace") as f:
                        text = f.read()
                    for needle in ("~/workspace/boss-ceo",
                                   "~/workspace/creator-os-combined"):
                        if needle in text:
                            bad.append(
                                f"{os.path.relpath(path, BASE)}: {needle}")
        check("section files: no boss-ceo / creator-os-combined refs",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("section files: no boss-ceo / creator-os-combined refs",
              False, str(e))

    # 10. Config: phase 11 + v0.9.0 + brain mock + 3 businesses + phase_7
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        phases = cfg.get("honest_status", {}).get("phases", {})
        ok = (cfg.get("phase") == 11 and cfg.get("version") == "0.9.0"
              and cfg.get("brain") == "mock"
              and len(cfg.get("businesses", [])) == 3
              and "phase_7_sections" in phases
              and "BUILT" in phases.get("phase_7_sections", "")
              and "phase_5_three_engines" in phases
              and "agentic_phase_3" in phases
              and "unified_os" in phases
              and "phase_9_connections" in phases
              and "phase_11_providers" in phases
              and "phase_10_live_brain" in phases)
        check("config.json phase 11 + v0.9.0 + brain mock + 3 biz + phase_7 + agentic 1-3 + unified + phase_9 + phase_11",
              ok, f"phase={cfg.get('phase')}, version={cfg.get('version')}, "
              f"brain={cfg.get('brain')}")
    except Exception as e:  # noqa: BLE001
        check("config.json phase 11 + v0.9.0 + brain mock + 3 biz + phase_7 + agentic 1-3 + unified + phase_9 + phase_11",
              False, str(e))

    # 11. Real store unchanged by this check run (Phase 9: live queue)
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 12. Earlier checks still PASS
    try:
        codes = []
        for script in ("check_phase0.py", "check_phase1.py",
                       "check_phase2.py", "check_phase3.py",
                       "check_phase4.py", "check_engines.py",
                       "check_phase6.py"):
            proc = subprocess.run(
                [sys.executable, os.path.join(BASE, "scripts", script)],
                capture_output=True, text=True, timeout=300)
            codes.append(proc.returncode)
        ok = all(c == 0 for c in codes)
        check("check_phase0/1/2/3/4 + engines + phase6 still PASS", ok,
              f"p0={codes[0]}, p1={codes[1]}, p2={codes[2]}, p3={codes[3]}, "
              f"p4={codes[4]}, engines={codes[5]}, p6={codes[6]}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0/1/2/3/4 + engines + phase6 still PASS",
              False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 7 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
