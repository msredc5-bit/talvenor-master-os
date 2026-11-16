#!/usr/bin/env python3
"""Phase 3 self-check — Talvenor Master OS, Content Creation department.

যাচাই করে:
  1. Phase 3 ফাইল আছে (Chief, pipeline.md, toolpilot-status.md, skill)
  2. Chief import হয় + ROUTING-এ ৬টা task type আছে
  3. content_plan -> draft-ready, TopicResearcher, gate ok, mock brain
  4. script_write -> draft-ready + VOICE.md DRAFT সতর্কতা আছে
  5. video_produce (input ছাড়া) -> draft-ready, video_file None,
     video_built False, missing_inputs >= 2 (ভুয়া video নেই)
  6. caption_write -> draft-ready, CaptionWriter
  7. publish_prep -> draft-ready, ready_to_publish False, gate "post it"
  8. gated upload -> blocked-upload-off (stage 9 OFF, upload হয়নি)
  9. gated publish -> pending-approval, granted 0, worker চালানো হয়নি
 10. অচেনা task type -> error, crash নয়
 11. Main CEO Bot -> Content Chief end-to-end routing কাজ করে
 12. pipeline.md-এ ১৩ stage আছে, REAL 0 / MOCK 10 / BLOCKED 3, VOICE.md
     + GPU নামের কথা আছে
 13. toolpilot-status.md-এ @ToolPilotai69, 0 subs, READY TO RECORD,
     [FILL AFTER TEST], ToolPilot-vs-new-channel প্রশ্ন unanswered
 14. tasks.json valid থাকে + অন্য department-এর entry মোছা হয় না
 15. আসল store/tasks.json + approvals.json এখনো খালি (0 record)
 16. Dashboard-এ Phase 3 BUILT + Content Engine REAL + upload OFF আছে
 17. config.json-এর gate ON + $0 cap + phase 3 ঠিক আছে
 18. check_phase0.py + check_phase1.py + check_phase2.py এখনো PASS

সব check TEMP file-এ চলে — আসল store/ শুধু ১৫ নম্বর check-এ পড়া হয়,
লেখা হয় না। Stdlib only, no network, no spend, no send, no upload।
Exit 0 = PASS।
"""

import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))
sys.path.insert(0, os.path.join(BASE, "03-Content-Creation-Department"))

EXPECTED_PHASE3_FILES = [
    "03-Content-Creation-Department/chief_of_staff_content.py",
    "03-Content-Creation-Department/pipeline.md",
    "03-Content-Creation-Department/toolpilot-status.md",
    "skills/chief-content.md",
    "scripts/check_phase3.py",
]

EXPECTED_ROUTING = {
    "content_plan": ("TopicResearcher", "ok"),
    "script_write": ("ScriptWriter", "ok"),
    "video_produce": ("VisualProducer", "ok"),
    "caption_write": ("CaptionWriter", "ok"),
    "publish_prep": ("PublishPrep", "post it"),
    "performance_track": ("PerformanceTracker", "ok"),
}

EXPECTED_STAGES = [
    "0a-niche", "0b-plan", "1-research", "2a-concept", "2b-script",
    "3-visual-pack", "4-video", "5-edit", "6-caption-seo",
    "7-publish-prep", "8-report", "9-upload", "10-next-plan",
]

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def tmp_paths():
    d = tempfile.mkdtemp()
    return (os.path.join(d, "tasks.json"), os.path.join(d, "approvals.json"))


def main():
    # 1. Files exist
    missing = [f for f in EXPECTED_PHASE3_FILES if not os.path.isfile(os.path.join(BASE, f))]
    check("phase 3 files exist", not missing,
          f"{len(EXPECTED_PHASE3_FILES) - len(missing)}/{len(EXPECTED_PHASE3_FILES)}"
          + (f", missing: {missing}" if missing else ""))

    # 2. Chief imports + ROUTING has 6 task types
    try:
        import chief_of_staff_content as chief  # noqa: PLC0415

        routed = {k: (v[0].__name__, v[1]) for k, v in chief.ROUTING.items()}
        check("chief imports + 6 task types routed", routed == EXPECTED_ROUTING,
              f"{len(routed)}/6" if routed != EXPECTED_ROUTING else "6/6")
        check("chief pipeline has 13 stages", chief.PIPELINE_STAGES == EXPECTED_STAGES,
              f"{len(chief.PIPELINE_STAGES)}/13")
    except Exception as e:  # noqa: BLE001
        check("chief imports + 6 task types routed", False, str(e))
        check("chief pipeline has 13 stages", False, str(e))
        print(f"\n0/{len(results)} checks passed.")
        return 1

    # 3. content_plan -> draft-ready, TopicResearcher, gate ok, mock brain
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "content_plan", "title": "check plan",
             "payload": {"niche": "AI tools", "audience": "US viewers"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["worker"] == "TopicResearcher"
              and r["gate"] == "ok" and r["mock_brain"] is True
              and r["draft_only"] is True)
        check("content_plan -> draft-ready (TopicResearcher, gate ok, mock)",
              ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("content_plan -> draft-ready (TopicResearcher, gate ok, mock)", False, str(e))

    # 4. script_write -> draft-ready + VOICE.md DRAFT warning
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "script_write", "title": "check script",
             "payload": {"topic": "Nano Banana 2", "format": "long video"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["worker"] == "ScriptWriter"
              and "DRAFT" in (r.get("voice_status") or "")
              and "VOICE.md" in r["note"])
        check("script_write -> draft-ready + VOICE.md DRAFT warning", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("script_write -> draft-ready + VOICE.md DRAFT warning", False, str(e))

    # 5. video_produce without inputs -> no fake video
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "video_produce", "title": "check video no inputs",
             "payload": {"topic": "Nano Banana 2"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        missing = r.get("missing_inputs") or []
        ok = (r["status"] == "draft-ready"
              and r.get("video_file") is None
              and r.get("video_built") is False
              and len(missing) >= 2
              and any("footage" in m for m in missing))
        check("video_produce (no inputs) -> no fake video, missing_inputs>=2",
              ok, f"missing={len(missing)}")
    except Exception as e:  # noqa: BLE001
        check("video_produce (no inputs) -> no fake video, missing_inputs>=2", False, str(e))

    # 6. caption_write -> draft-ready, CaptionWriter
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "caption_write", "title": "check caption",
             "payload": {"topic": "Nano Banana 2"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = r["status"] == "draft-ready" and r["worker"] == "CaptionWriter"
        check("caption_write -> draft-ready (CaptionWriter)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("caption_write -> draft-ready (CaptionWriter)", False, str(e))

    # 7. publish_prep -> draft-ready, ready_to_publish False, gate "post it"
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "publish_prep", "title": "check prep",
             "payload": {"topic": "Nano Banana 2"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["worker"] == "PublishPrep"
              and r.get("ready_to_publish") is False
              and r["gate"] == "post it")
        check("publish_prep -> draft-ready, ready_to_publish False, gate post it",
              ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("publish_prep -> draft-ready, ready_to_publish False, gate post it", False, str(e))

    # 8. Gated upload -> blocked-upload-off, nothing uploaded
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "publish_prep", "title": "check upload blocked",
             "gated_action": "upload"},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = r["status"] == "blocked-upload-off"
        check("gated upload -> blocked-upload-off (stage 9 OFF)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("gated upload -> blocked-upload-off (stage 9 OFF)", False, str(e))

    # 9. Gated publish -> PENDING, granted 0, worker not run
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "publish_prep", "title": "check gated publish",
             "gated_action": "publish"},
            tasks_path=tasks_p, approvals_path=appr_p)
        with open(appr_p, encoding="utf-8") as f:
            appr = json.load(f)
        granted = [x for x in appr["records"] if x["status"] == "approved"]
        pending = [x for x in appr["records"] if x["status"] == "pending"]
        ok = (r["status"] == "pending-approval"
              and r["approval"]["status"] == "pending"
              and len(pending) == 1 and len(granted) == 0)
        check("gated publish refused (PENDING, nothing granted)", ok,
              f"status={r['status']}, pending={len(pending)}, granted={len(granted)}")
    except Exception as e:  # noqa: BLE001
        check("gated publish refused (PENDING, nothing granted)", False, str(e))

    # 10. Unknown task type -> error, no crash
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task({"type": "fly_to_moon", "title": "check unknown"},
                              tasks_path=tasks_p, approvals_path=appr_p)
        check("unknown task type -> error (no crash)", r["status"] == "error", r["status"])
    except Exception as e:  # noqa: BLE001
        check("unknown task type -> error (no crash)", False, str(e))

    # 11. Main CEO Bot -> Content Chief end-to-end (TEMP paths)
    try:
        import main_ceo_bot  # noqa: PLC0415

        tasks_p, appr_p = tmp_paths()
        r = main_ceo_bot.route_task(
            {"business": "content", "type": "content_plan",
             "title": "check end-to-end",
             "payload": {"niche": "AI tools", "audience": "US viewers"}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["chief_result"]["worker"] == "TopicResearcher")
        check("main_ceo_bot -> chief -> content_plan", ok, f"status={r['status']}")
    except Exception as e:  # noqa: BLE001
        check("main_ceo_bot -> chief -> content_plan", False, str(e))

    # 12. pipeline.md: 13 stages, counts REAL 0 / MOCK 10 / BLOCKED 3
    try:
        with open(os.path.join(BASE, "03-Content-Creation-Department", "pipeline.md"),
                  encoding="utf-8") as f:
            md = f.read()
        stages_found = sum(1 for s in EXPECTED_STAGES if s in md)
        counts_ok = ("REAL **0**" in md and "MOCK **10**" in md
                     and "BLOCKED **3**" in md)
        ok = stages_found == 13 and counts_ok and "VOICE.md" in md and "GPU" in md
        check("pipeline.md: 13 stages, REAL 0 / MOCK 10 / BLOCKED 3",
              ok, f"stages={stages_found}/13")
    except Exception as e:  # noqa: BLE001
        check("pipeline.md: 13 stages, REAL 0 / MOCK 10 / BLOCKED 3", False, str(e))

    # 13. toolpilot-status.md facts
    try:
        with open(os.path.join(BASE, "03-Content-Creation-Department",
                               "toolpilot-status.md"), encoding="utf-8") as f:
            md = f.read()
        ok = ("@ToolPilotai69" in md and "Subscribers: **0**" in md
              and "READY TO RECORD" in md and "[FILL AFTER TEST]" in md
              and "ToolPilot, নাকি brand-new channel" in md)
        check("toolpilot-status.md: channel facts + unanswered question", ok)
    except Exception as e:  # noqa: BLE001
        check("toolpilot-status.md: channel facts + unanswered question", False, str(e))

    # 14. tasks.json valid + other departments' entries preserved
    try:
        d = tempfile.mkdtemp()
        tasks_p = os.path.join(d, "tasks.json")
        appr_p = os.path.join(d, "approvals.json")
        seed = {"schema": "tasks-v1", "records": [
            {"id": "seed00000003", "department": "agency",
             "title": "seeded other-department entry", "type": None,
             "worker": None, "status": "draft-ready", "logged_at": "2026-11-16T00:00:00Z"}]}
        with open(tasks_p, "w", encoding="utf-8") as f:
            json.dump(seed, f)
        chief.handle_task({"type": "content_plan", "title": "check preserve",
                           "payload": {"niche": "x", "audience": "y"}},
                          tasks_path=tasks_p, approvals_path=appr_p)
        with open(tasks_p, encoding="utf-8") as f:
            data = json.load(f)
        kept = any(x["id"] == "seed00000003" for x in data["records"])
        ok = kept and len(data["records"]) == 2 and data["schema"] == "tasks-v1"
        check("tasks.json valid + other dept entry preserved", ok,
              f"records={len(data['records'])}, seed kept={kept}")
    except Exception as e:  # noqa: BLE001
        check("tasks.json valid + other dept entry preserved", False, str(e))

    # 15. Real store files untouched (still empty)
    try:
        with open(os.path.join(BASE, "store", "approvals.json"), encoding="utf-8") as f:
            real_appr = json.load(f)
        with open(os.path.join(BASE, "store", "tasks.json"), encoding="utf-8") as f:
            real_tasks = json.load(f)
        check("real store files untouched by checks",
              real_appr.get("records") == [] and real_tasks.get("records") == [])
    except Exception as e:  # noqa: BLE001
        check("real store files untouched by checks", False, str(e))

    # 16. Dashboard shows Phase 3 BUILT + Content Engine REAL + upload OFF
    try:
        with open(os.path.join(BASE, "dashboards", "status.html"), encoding="utf-8") as f:
            html = f.read()
        ok = ("Phase 3" in html and "BUILT" in html
              and "Content Engine" in html and "REAL" in html
              and "upload" in html.lower() and "OFF" in html)
        check("dashboard shows Phase 3 BUILT + upload OFF", ok)
    except Exception as e:  # noqa: BLE001
        check("dashboard shows Phase 3 BUILT + upload OFF", False, str(e))

    # 17. config.json gates ON + $0 cap + phase 3
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        ok = (cfg.get("spend_cap_usd") == 0
              and cfg.get("gates", {}).get("enabled") is True
              and cfg.get("phase", 0) >= 3)
        check("config.json gates ON + $0 cap + phase >= 3", ok)
    except Exception as e:  # noqa: BLE001
        check("config.json gates ON + $0 cap + phase 3", False, str(e))

    # 18. Phase 0 + 1 + 2 checks still pass
    try:
        outs = []
        for script in ("check_phase0.py", "check_phase1.py", "check_phase2.py"):
            p = subprocess.run([sys.executable, os.path.join(BASE, "scripts", script)],
                               capture_output=True, text=True, timeout=180)
            outs.append(p.returncode)
        ok = all(code == 0 for code in outs)
        check("check_phase0 + check_phase1 + check_phase2 still PASS", ok,
              f"p0={outs[0]}, p1={outs[1]}, p2={outs[2]}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0 + check_phase1 + check_phase2 still PASS", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 3 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
