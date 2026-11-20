#!/usr/bin/env python3
"""Phase 1 self-check — Talvenor Master OS, Agency department.

যাচাই করে:
  1. Agency Chief import হয় + ROUTING-এ ১৫টা আসল worker আছে
  2. outreach_draft -> OutreachDrafter, draft-ready ফেরত আসে (mock brain, DRAFT ONLY)
  3. prospect_research -> ProspectResearcher (gate নেই)
  4. gated send refuse হয়: status pending-approval, PENDING record লেখা
     হয়, কোনো approval granted হয় না, কোনো send হয় না
  5. অচেনা task type -> error, crash নয়
  6. Main CEO Bot -> Chief end-to-end routing কাজ করে
  7. tasks.json valid থাকে + অন্য department-এর entry মোছা হয় না
  8. আসল store/approvals.json-এ test record লেখা হয় না
  9. Dashboard-এ Phase 1 + PAUSED সত্য অবস্থা আছে
  10. config.json-এর gate ON + $0 cap ঠিক আছে

সব check TEMP file-এ চলে — আসল store/ শুধু ৮ নম্বর check-এ পড়া হয়,
লেখা হয় না। Stdlib only, no network, no spend, no send। Exit 0 = PASS।
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
    """Real store-এর snapshot (Phase 9: store এখন live queue — taskboard /
    bridge সত্যিই task লেখে, তাই 'খালি' আর invariant নয়)। Check-এর
    কাজ শুধু প্রমাণ করা যে এই run store বদলায়নি।"""
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
              and r.get("worker") is None)  # worker একদম চালানো হয়নি
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

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 1 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
