#!/usr/bin/env python3
"""Phase 1 self-check — Talvenor Master OS, Agency department.

Verifies:
  1. Agency Chief imports + ROUTING has 15 real workers
  2. outreach_draft -> OutreachDrafter, returns draft-ready (mock brain, DRAFT ONLY)
  3. prospect_research -> ProspectResearcher (no gate)
  4. Gated send is refused: status pending-approval, PENDING record written
     , no approval granted, no send happens
  5. Unknown task type -> error, not a crash
  6. Main CEO Bot -> Chief end-to-end routing works
  7. tasks.json stays valid + other departments' entries are not deleted
  8. No test record is written to the real store/approvals.json
  9. The dashboard has Phase 1 + PAUSED true state
 10. config.json's gate ON + $0 cap are correct

All checks run in TEMP files — the real store/ is only read in check 8,
never written. Stdlib only, no network, no spend, no send. Exit 0 = PASS.

Checks 1–11 are the OLD Phase 1 (Agency Chief). Checks 12–21 are the
NEW Unified OS Phase 1 (2026-11-22): registry canonical + runtime load,
permissions enforced, task schema + drain, audit log, goals summary,
agent runs, memory search + boxes, skills dedup, store_io, backup.
"""

import json
import os
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))
sys.path.insert(0, os.path.join(BASE, "01-Agency-Department"))

EXPECTED_PHASE1_FILES = [
    "01-Agency-Department/chief_of_staff_agency.py",
    "01-Agency-Department/pipeline.md",
    "01-Agency-Department/sub_agents/README.md",
    "skills/chief-agency.md",
    "scripts/check_phase1.py",
]

EXPECTED_WORKERS = {
    "prospect_research": "ProspectResearcher",
    "outreach_draft": "OutreachDrafter",
    "reply_triage": "ReplyHandler",
    "negotiation_prep": "NegotiationCoach",
    "receptionist_build": "RetellBuilder",
    "receptionist_qa": "QAEngineer",
    "onboarding_draft": "OnboardingAgent",
    "content_plan": "ContentPlanner",
    "video_produce": "VideoProducer",
    "caption_write": "CaptionWriter",
    "publish_prep": "PublishPrep",
    "objection_sim": "ObjectionSimulator",
    "inbox_triage": "InboxTriager",
    "report_compile": "ReportCompiler",
    "schedule_help": "SchedulerAssistant",
}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def tmp_paths():
    d = tempfile.mkdtemp()
    return (os.path.join(d, "tasks.json"), os.path.join(d, "approvals.json"))


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
    # 1. Files exist
    missing = [f for f in EXPECTED_PHASE1_FILES if not os.path.isfile(os.path.join(BASE, f))]
    check("phase 1 files exist", not missing,
          f"{len(EXPECTED_PHASE1_FILES) - len(missing)}/{len(EXPECTED_PHASE1_FILES)}"
          + (f", missing: {missing}" if missing else ""))

    # 2. Chief imports + ROUTING has all 15 real workers
    try:
        import chief_of_staff_agency as chief  # noqa: PLC0415

        routed = {k: v[0].__name__ for k, v in chief.ROUTING.items()}
        check("chief imports + 15 real workers routed", routed == EXPECTED_WORKERS,
              f"{len(routed)}/15" if routed != EXPECTED_WORKERS else "15/15")
    except Exception as e:  # noqa: BLE001
        check("chief imports + 15 real workers routed", False, str(e))
        print(f"\n0/{len(results)} checks passed.")
        return 1

    # 3. outreach_draft -> OutreachDrafter, draft-ready, mock brain
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "outreach_draft", "title": "check draft",
             "payload": {"channel": "email"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready" and r["worker"] == "OutreachDrafter"
              and r["draft_only"] is True and r["mock_brain"] is True
              and r["gate"] == "send")
        check("outreach_draft -> OutreachDrafter (draft-ready)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("outreach_draft -> OutreachDrafter (draft-ready)", False, str(e))

    # 4. prospect_research -> ProspectResearcher, no gate
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "prospect_research", "title": "check research",
             "payload": {"niche": "plumbing", "region": "Texas"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready" and r["worker"] == "ProspectResearcher"
              and r["gate"] is None)
        check("prospect_research -> ProspectResearcher (no gate)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("prospect_research -> ProspectResearcher (no gate)", False, str(e))

    # 5. Gated send refused — PENDING, nothing granted, nothing sent
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "outreach_draft", "title": "check gated send",
             "payload": {"channel": "email"}, "gated_action": "send"},
            tasks_path=tasks_p, approvals_path=appr_p)
        with open(appr_p, encoding="utf-8") as f:
            appr = json.load(f)
        granted = [x for x in appr["records"] if x["status"] == "approved"]
        pending = [x for x in appr["records"] if x["status"] == "pending"]
        ok = (r["status"] == "pending-approval"
              and r["approval"]["status"] == "pending"
              and len(pending) == 1 and len(granted) == 0
              and r.get("worker") is None)  # worker not run at all
        check("gated send refused (PENDING, nothing granted)", ok,
              f"status={r['status']}, pending={len(pending)}, granted={len(granted)}")
    except Exception as e:  # noqa: BLE001
        check("gated send refused (PENDING, nothing granted)", False, str(e))

    # 6. Unknown task type -> error, no crash
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task({"type": "fly_to_moon", "title": "check unknown"},
                              tasks_path=tasks_p, approvals_path=appr_p)
        check("unknown task type -> error (no crash)", r["status"] == "error", r["status"])
    except Exception as e:  # noqa: BLE001
        check("unknown task type -> error (no crash)", False, str(e))

    # 7. Main CEO Bot -> Chief end-to-end (TEMP paths)
    try:
        import main_ceo_bot  # noqa: PLC0415

        tasks_p, appr_p = tmp_paths()
        r = main_ceo_bot.route_task(
            {"business": "agency", "type": "reply_triage",
             "title": "check end-to-end", "payload": {"reply_type": "interest"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["chief_result"]["worker"] == "ReplyHandler")
        check("main_ceo_bot -> chief -> ReplyHandler", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("main_ceo_bot -> chief -> ReplyHandler", False, str(e))

    # 8. tasks.json valid + other departments' entries preserved
    try:
        d = tempfile.mkdtemp()
        tasks_p = os.path.join(d, "tasks.json")
        appr_p = os.path.join(d, "approvals.json")
        seed = {"schema": "tasks-v1", "records": [
            {"id": "seed00000001", "department": "content",
             "title": "seeded other-department entry", "type": None,
             "worker": None, "status": "draft-ready", "logged_at": "2026-11-16T00:00:00Z"}]}
        with open(tasks_p, "w", encoding="utf-8") as f:
            json.dump(seed, f)
        chief.handle_task({"type": "caption_write", "title": "check preserve"},
                          tasks_path=tasks_p, approvals_path=appr_p)
        with open(tasks_p, encoding="utf-8") as f:
            data = json.load(f)
        kept = any(x["id"] == "seed00000001" for x in data["records"])
        ok = kept and len(data["records"]) == 2 and data["schema"] == "tasks-v1"
        check("tasks.json valid + other dept entry preserved", ok,
              f"records={len(data['records'])}, seed kept={kept}")
    except Exception as e:  # noqa: BLE001
        check("tasks.json valid + other dept entry preserved", False, str(e))

    # 9. Real store unchanged by this check run (Phase 9: live queue)
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 10. Dashboard shows Phase 1 + PAUSED
    try:
        with open(os.path.join(BASE, "dashboards", "status.html"), encoding="utf-8") as f:
            html = f.read()
        ok = "Phase 1" in html and "PAUSED" in html and "Agency" in html
        check("dashboard shows Phase 1 + PAUSED", ok)
    except Exception as e:  # noqa: BLE001
        check("dashboard shows Phase 1 + PAUSED", False, str(e))

    # 11. config.json gates ON + $0 cap
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        ok = cfg.get("spend_cap_usd") == 0 and cfg.get("gates", {}).get("enabled") is True
        check("config.json gates ON + $0 cap", ok)
    except Exception as e:  # noqa: BLE001
        check("config.json gates ON + $0 cap", False, str(e))

    # --- NEW Unified OS Phase 1 checks (2026-11-22) -------------------------
    # 12. Registry: registry.json loads (69) and the generated registry.md
    # matches it — the generator is re-run in memory, nothing is written.
    try:
        import importlib.util  # noqa: PLC0415
        from datetime import datetime, timezone  # noqa: PLC0415

        gen_path = os.path.join(BASE, "scripts", "generate_registry_md.py")
        spec = importlib.util.spec_from_file_location(
            "generate_registry_md", gen_path)
        gen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gen)
        reg_json = os.path.join(
            BASE, "01-Agency-Department", "agents", "agent-registry",
            "registry.json")
        reg_md = os.path.join(
            BASE, "01-Agency-Department", "agents", "agent-registry",
            "registry.md")
        with open(reg_json, encoding="utf-8") as f:
            registry = json.load(f)
        mtime = os.path.getmtime(reg_json)
        date = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        generated = gen.generate(registry, date)
        with open(reg_md, encoding="utf-8") as f:
            committed = f.read()
        check("registry.json loads (69) and generated registry.md matches",
              len(registry) == 69 and generated == committed,
              f"entries={len(registry)}, match={generated == committed}")
    except Exception as e:  # noqa: BLE001
        check("registry.json loads (69) and generated registry.md matches",
              False, str(e))

    # 13. Permission deny: Main CEO Bot cannot draft_email (denied-permission);
    # OutreachDrafter can (draft-ready). TEMP calls log only.
    audit_dir_13 = None
    try:
        import tool_calling  # noqa: PLC0415

        audit_dir_13 = tempfile.mkdtemp()
        calls_p = os.path.join(audit_dir_13, "tool_calls.json")
        appr_p = os.path.join(audit_dir_13, "approvals.json")
        # call_tool with registry=None builds an EMPTY registry, so the
        # real tools.json registry must be loaded explicitly.
        registry = tool_calling.ToolRegistry.load_from_json(
            os.path.join(BASE, "00-CEO-Core", "tools.json"))
        args = {"business_name": "ABC Plumbing", "topic": "missed calls"}
        r_denied = tool_calling.call_tool(
            "draft_email", args, context={"agent": "main_ceo_bot"},
            registry=registry, approvals_path=appr_p, calls_log_path=calls_p)
        r_allowed = tool_calling.call_tool(
            "draft_email", args, context={"agent": "OutreachDrafter"},
            registry=registry, approvals_path=appr_p, calls_log_path=calls_p)
        ok = (r_denied["status"] == "denied-permission"
              and r_allowed["status"] == "draft-ready")
        check("permission deny: CEO cannot draft_email, OutreachDrafter can",
              ok, f"ceo={r_denied['status']}, drafter={r_allowed['status']}")
    except Exception as e:  # noqa: BLE001
        check("permission deny: CEO cannot draft_email, OutreachDrafter can",
              False, str(e))

    # 14. Task schema + drain ordering + idempotency (TEMP store).
    # C (priority 10) drains before A (priority 5); B waits on A;
    # D (cancelled) is marked cancelled; E (same key as A) is duplicate.
    drain_dir = None
    try:
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        import run_office  # noqa: PLC0415

        drain_dir = tempfile.mkdtemp()
        seed = {"schema": "tasks-v1", "records": [
            {"id": "taskA0000001", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "A low pri", "payload": {},
             "queued_at": "2026-11-22T00:00:01+00:00", "priority": 5,
             "idempotency_key": "key-A"},
            {"id": "taskB0000002", "status": "queued", "business": "agency",
             "type": "prospect_research", "title": "B depends on A",
             "payload": {"niche": "plumbing", "region": "Texas"},
             "queued_at": "2026-11-22T00:00:02+00:00", "priority": 1,
             "depends_on": ["taskA0000001"]},
            {"id": "taskC0000003", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "C high pri", "payload": {},
             "queued_at": "2026-11-22T00:00:03+00:00", "priority": 10},
            {"id": "taskD0000004", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "D cancelled", "payload": {},
             "queued_at": "2026-11-22T00:00:04+00:00", "cancelled": True},
            {"id": "taskE0000005", "status": "queued", "business": "agency",
             "type": "caption_write", "title": "E dup of A key", "payload": {},
             "queued_at": "2026-11-22T00:00:05+00:00",
             "idempotency_key": "key-A"},
        ]}
        with open(os.path.join(drain_dir, "tasks.json"), "w",
                  encoding="utf-8") as f:
            json.dump(seed, f)
        run_office.drain_queue(drain_dir, 10)
        with open(os.path.join(drain_dir, "tasks.json"),
                  encoding="utf-8") as f:
            after = {r["id"]: r for r in json.load(f)["records"]
                     if r["id"].startswith("task")}
        order_ok = (after["taskC0000003"]["drained_at"]
                    < after["taskA0000001"]["drained_at"]
                    < after["taskB0000002"]["drained_at"])
        ok = (after["taskC0000003"]["status"] == "done"
              and after["taskA0000001"]["status"] == "done"
              and after["taskB0000002"]["status"] == "done"
              and after["taskD0000004"]["status"] == "cancelled"
              and after["taskE0000005"]["status"] == "duplicate"
              and after["taskA0000001"]["priority"] == 5
              and order_ok)
        check("drain: priority order + deps + cancelled + idempotency",
              ok, f"C={after['taskC0000003']['status']}, "
              f"A={after['taskA0000001']['status']}, "
              f"B={after['taskB0000002']['status']}, "
              f"D={after['taskD0000004']['status']}, "
              f"E={after['taskE0000005']['status']}")
    except Exception as e:  # noqa: BLE001
        check("drain: priority order + deps + cancelled + idempotency",
              False, str(e))

    # 15. Audit log appends: the permission denial (check 13) and the
    # drain transitions (check 14) are in TEMP audit.log files.
    try:
        events_13 = []
        if audit_dir_13:
            audit_p = os.path.join(audit_dir_13, "audit.log")
            if os.path.exists(audit_p):
                with open(audit_p, encoding="utf-8") as f:
                    events_13 = [json.loads(line) for line in f if line.strip()]
        denied_logged = any(e.get("event") == "permission_denied"
                            for e in events_13)
        events_14 = []
        if drain_dir:
            audit_p = os.path.join(drain_dir, "audit.log")
            if os.path.exists(audit_p):
                with open(audit_p, encoding="utf-8") as f:
                    events_14 = [json.loads(line) for line in f if line.strip()]
        transitions = {e.get("to") for e in events_14
                       if e.get("event") == "task_transition"}
        ok = denied_logged and {"done", "cancelled", "duplicate"} <= transitions
        check("audit log appends (permission_denied + task transitions)",
              ok, f"denied={denied_logged}, transitions={sorted(transitions)}")
    except Exception as e:  # noqa: BLE001
        check("audit log appends (permission_denied + task transitions)",
              False, str(e))

    # 16. Goals summary reads real counts (TEMP store with known numbers).
    try:
        import goals  # noqa: PLC0415

        d = tempfile.mkdtemp()
        with open(os.path.join(d, "tasks.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": [
                {"id": "t1", "status": "done"},
                {"id": "t2", "status": "done"},
                {"id": "t3", "status": "queued"},
            ]}, f)
        with open(os.path.join(d, "usage_ledger.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "usage-ledger-v1", "monthly_cap_usd": 0,
                       "records": [
                           {"cost_usd": 0.0}, {"cost_usd": 0.0},
                           {"cost_usd": 0.0}]}, f)
        with open(os.path.join(d, "approvals.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "approvals-v1", "records": [
                {"id": "a1", "status": "pending"}]}, f)
        with open(os.path.join(d, "goals.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "goals-v1", "goals": [
                {"id": "g1", "title": "first paying client",
                 "metric": "first_mails_sent"}]}, f)
        summary = goals.executive_summary(store_dir=d)
        ok = (summary["tasks"]["total"] == 3
              and summary["tasks"]["by_status"] == {"done": 2, "queued": 1}
              and summary["ledger"]["total_calls"] == 3
              and summary["ledger"]["total_usd"] == 0.0
              and summary["approvals"]["total"] == 1
              and summary["goals"][0]["progress"] == 163)
        check("goals summary reads real counts (TEMP store)",
              ok, f"tasks={summary['tasks']['total']}, "
              f"ledger={summary['ledger']['total_calls']}, "
              f"first_mails={summary['goals'][0]['progress']}")
    except Exception as e:  # noqa: BLE001
        check("goals summary reads real counts (TEMP store)", False, str(e))

    # 17. Agent runs recorded: a worker run lands in agent_runs.json with
    # in_registry=True + role; a manager run lands with in_registry=False.
    try:
        d = tempfile.mkdtemp()
        tasks_p = os.path.join(d, "tasks.json")
        appr_p = os.path.join(d, "approvals.json")
        chief.handle_task({"type": "outreach_draft", "title": "check runs",
                           "payload": {"channel": "email"}},
                          tasks_path=tasks_p, approvals_path=appr_p)
        chief.handle_task({"type": "dept_sales", "title": "check mgr runs"},
                          tasks_path=tasks_p, approvals_path=appr_p)
        with open(os.path.join(d, "agent_runs.json"),
                  encoding="utf-8") as f:
            runs = json.load(f)["records"]
        worker_run = next((r for r in runs
                           if r["worker"] == "OutreachDrafter"), None)
        mgr_run = next((r for r in runs
                        if r["worker"] == "ChiefGrowthAgent"), None)
        ok = (worker_run is not None
              and worker_run["in_registry"] is True
              and worker_run["role"] == "Email Outreach Agent"
              and worker_run["department"] == "01 Sales & Growth"
              and mgr_run is not None and mgr_run["in_registry"] is False)
        check("agent runs recorded (worker in registry, manager not)",
              ok, f"runs={len(runs)}")
    except Exception as e:  # noqa: BLE001
        check("agent runs recorded (worker in registry, manager not)",
              False, str(e))

    # 18. Memory search + boxes: substring search finds a seed, respects
    # box isolation, and the products/content boxes exist.
    try:
        from owner_memory import BOXES, OwnerMemory  # noqa: PLC0415

        d = tempfile.mkdtemp()
        mem_path = os.path.join(d, "memory.json")
        mem = OwnerMemory(memory_path=mem_path)
        mem.seed_defaults()
        found = mem.search("Mira")
        mem.note_work("dept_sales", "day-note", "Sales: 5 draft ready.",
                      area="lessons")
        hidden = mem.search("day-note", box="dept_marketing")
        visible = mem.search("day-note", box="dept_sales")
        ok = ("products" in BOXES and "content" in BOXES
              and len(BOXES) == 13
              and any(e["slug"] == "assistant-name" for e in found)
              and hidden == [] and len(visible) == 1)
        check("memory search (substring, per-box) + 13 boxes", ok,
              f"boxes={len(BOXES)}, found={[e['slug'] for e in found]}")
    except Exception as e:  # noqa: BLE001
        check("memory search (substring, per-box) + 13 boxes", False, str(e))

    # 19. Skills dedup: the 5 pointer files exist, point at the canonical
    # engine copy, and are not skills (no heading); the manifest lists them.
    try:
        pointers = [
            ("02-Digital-Product-Department/sections/sales/skills/kit-sales.md",
             "02-Digital-Product-Department/engine/skills/kit-sales.md"),
            ("03-Content-Creation-Department/sections/growth/skills/growth-agent.md",
             "03-Content-Creation-Department/engine/skills/growth-agent.md"),
            ("03-Content-Creation-Department/sections/growth/skills/repurpose-agent.md",
             "03-Content-Creation-Department/engine/skills/repurpose-agent.md"),
            ("02-Digital-Product-Department/sections/product/skills/kit-qa.md",
             "02-Digital-Product-Department/engine/skills/kit-qa.md"),
            ("03-Content-Creation-Department/sections/produce/skills/script-writer.md",
             "03-Content-Creation-Department/engine/skills/script-writer.md"),
        ]
        ok = True
        for ptr_rel, canon_rel in pointers:
            ptr_p = os.path.join(BASE, ptr_rel)
            canon_p = os.path.join(BASE, canon_rel)
            with open(ptr_p, encoding="utf-8") as f:
                text = f.read()
            rel = os.path.relpath(canon_p, os.path.dirname(ptr_p))
            if (not os.path.isfile(canon_p)
                    or f"canonical copy: {rel}" not in text
                    or any(line.startswith("# ") for line in text.splitlines())):
                ok = False
        with open(os.path.join(BASE, "skills", "SKILL_INDEX.md"),
                  encoding="utf-8") as f:
            manifest = f.read()
        ok = ok and all(s in manifest for s in
                        ("growth-agent", "kit-sales", "repurpose-agent",
                         "kit-qa", "script-writer"))
        check("skills dedup: 5 pointers + manifest", ok)
    except Exception as e:  # noqa: BLE001
        check("skills dedup: 5 pointers + manifest", False, str(e))

    # 20. store_io: atomic write + locked read-modify-write round-trip
    # in TEMP; no lock file is left behind.
    try:
        from store_io import read_json, update_json, write_json_atomic  # noqa: PLC0415

        d = tempfile.mkdtemp()
        p = os.path.join(d, "data.json")
        write_json_atomic(p, {"schema": "t-v1", "records": []})
        update_json(p, lambda data: {**data, "records": data["records"] + [
            {"id": "x1"}]}, default={"schema": "t-v1", "records": []})
        data = read_json(p)
        # The flock lock file correctly persists (unlinking it would race
        # another process's lock) — it must just be empty, and the data
        # must round-trip.
        lock_size = (os.path.getsize(p + ".lock")
                     if os.path.exists(p + ".lock") else 0)
        ok = data["records"] == [{"id": "x1"}] and lock_size == 0
        check("store_io atomic write + locked update (TEMP)", ok)
    except Exception as e:  # noqa: BLE001
        check("store_io atomic write + locked update (TEMP)", False, str(e))

    # 21. Backup: snapshot a TEMP store, verify it, restore-test it.
    try:
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        import backup_store  # noqa: PLC0415

        src = tempfile.mkdtemp()
        with open(os.path.join(src, "tasks.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "tasks-v1", "records": [
                {"id": "b1", "status": "done"}]}, f)
        with open(os.path.join(src, "goals.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"schema": "goals-v1", "goals": []}, f)
        dest = os.path.join(tempfile.mkdtemp(), "store-backup")
        made = backup_store.backup_store(store_dir=src, out=dest)
        ok_verify, _detail = backup_store.verify_backup(made)
        ok_restore, _detail2 = backup_store.restore_test(made)
        ok = ok_verify and ok_restore and os.path.isfile(
            os.path.join(made, "tasks.json"))
        check("backup snapshot + verify + restore-test (TEMP)", ok)
    except Exception as e:  # noqa: BLE001
        check("backup snapshot + verify + restore-test (TEMP)", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 1 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
