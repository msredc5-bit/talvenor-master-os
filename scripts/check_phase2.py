#!/usr/bin/env python3
"""Phase 2 self-check — Talvenor Master OS, Digital Product department.

যাচাই করে:
  1. Phase 2 ফাইল আছে (Chief, kit blueprint, Gate 0 status, PA list, skill)
  2. Chief import হয় + ROUTING-এ ৪টা task type আছে
  3. kit_build -> draft-ready, blueprint আছে, ৬ অংশ, Gate 0 NOT PASSED
  4. gate0_check -> NOT PASSED (fail-closed)
  5. mark_launched চাইলে blocked-gate0 — কোনো sale লেখা হয় না
  6. gated send refuse হয়: PENDING, granted 0, worker চালানো হয় না
  7. অচেনা task type -> error, crash নয়
  8. Main CEO Bot -> Products Chief end-to-end routing কাজ করে
  9. PA list CSV: ≥25 row, প্রতিটা row-এ নাম/শহর/website আছে, email
     হয় @ থাকে নইলে "Not publicly listed" (বানানো email নেই)
  10. tasks.json valid থাকে + অন্য department-এর entry মোছা হয় না
  11. আসল store এই run-এ বদলায়নি (Phase 9: live queue)
  12. Dashboard-এ Phase 2 + Gate 0 NOT PASSED + PA list সংখ্যা আছে
  13. config.json-এর gate ON + $0 cap + phase 2 ঠিক আছে
  14. check_phase0.py + check_phase1.py এখনো PASS (Phase 0/1 ভাঙেনি)

সব check TEMP file-এ চলে — আসল store/ শুধু ১১ নম্বর check-এ পড়া হয়,
লেখা হয় না। Stdlib only, no network, no spend, no send। Exit 0 = PASS।
"""

import csv
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))
sys.path.insert(0, os.path.join(BASE, "02-Digital-Product-Department"))

EXPECTED_PHASE2_FILES = [
    "02-Digital-Product-Department/chief_of_staff_products.py",
    "02-Digital-Product-Department/kit-outline.md",
    "02-Digital-Product-Department/gate0-status.md",
    "02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv",
    "02-Digital-Product-Department/pa-vet-list/README.md",
    "skills/chief-products.md",
    "scripts/check_phase2.py",
]

EXPECTED_ROUTING = {
    "kit_build": "blueprint",
    "clinic_research": "pa-list",
    "gate0_check": "gate0-status",
    "launch_prep": "launch-checklist-draft",
}

EXPECTED_KIT_PARTS = [
    "reminder-cadence-pack",
    "same-day-rebooking",
    "waitlist-fill-sop",
    "no-show-log-tracker",
    "deposit-policy-template",
    "front-desk-quick-card",
]

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
    missing = [f for f in EXPECTED_PHASE2_FILES if not os.path.isfile(os.path.join(BASE, f))]
    check("phase 2 files exist", not missing,
          f"{len(EXPECTED_PHASE2_FILES) - len(missing)}/{len(EXPECTED_PHASE2_FILES)}"
          + (f", missing: {missing}" if missing else ""))

    # 2. Chief imports + ROUTING has 4 task types
    try:
        import chief_of_staff_products as chief  # noqa: PLC0415

        routed = {k: v[0] for k, v in chief.ROUTING.items()}
        check("chief imports + 4 task types routed", routed == EXPECTED_ROUTING,
              f"{len(routed)}/4" if routed != EXPECTED_ROUTING else "4/4")
    except Exception as e:  # noqa: BLE001
        check("chief imports + 4 task types routed", False, str(e))
        print(f"\n0/{len(results)} checks passed.")
        return 1

    # 3. kit_build -> draft-ready, blueprint present, 6 parts, Gate 0 NOT PASSED
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "kit_build", "title": "check kit build"},
            tasks_path=tasks_p, approvals_path=appr_p)
        out = r.get("output", {})
        ok = (r["status"] == "draft-ready"
              and out.get("blueprint_present") is True
              and out.get("parts") == EXPECTED_KIT_PARTS
              and out.get("price_usd_one_time") == 49
              and r["gate0"]["status"] == "NOT PASSED"
              and r["draft_only"] is True and r["gate"] == "ok")
        check("kit_build -> draft-ready (blueprint, 6 parts, Gate 0 NOT PASSED)",
              ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("kit_build -> draft-ready (blueprint, 6 parts, Gate 0 NOT PASSED)", False, str(e))

    # 4. gate0_check -> NOT PASSED (fail-closed)
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task({"type": "gate0_check", "title": "check gate0"},
                              tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["output"]["gate0"]["status"] == "NOT PASSED")
        check("gate0_check -> NOT PASSED (fail-closed)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("gate0_check -> NOT PASSED (fail-closed)", False, str(e))

    # 5. mark_launched -> blocked-gate0, no sale recorded
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "launch_prep", "title": "check blocked launch",
             "payload": {"mark_launched": True}},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "blocked-gate0"
              and r["gate0"]["status"] == "NOT PASSED")
        check("mark_launched -> blocked-gate0 (no sale)", ok, r["status"])
    except Exception as e:  # noqa: BLE001
        check("mark_launched -> blocked-gate0 (no sale)", False, str(e))

    # 6. Gated send refused — PENDING, nothing granted
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task(
            {"type": "kit_build", "title": "check gated send",
             "gated_action": "send"},
            tasks_path=tasks_p, approvals_path=appr_p)
        with open(appr_p, encoding="utf-8") as f:
            appr = json.load(f)
        granted = [x for x in appr["records"] if x["status"] == "approved"]
        pending = [x for x in appr["records"] if x["status"] == "pending"]
        ok = (r["status"] == "pending-approval"
              and r["approval"]["status"] == "pending"
              and len(pending) == 1 and len(granted) == 0)
        check("gated send refused (PENDING, nothing granted)", ok,
              f"status={r['status']}, pending={len(pending)}, granted={len(granted)}")
    except Exception as e:  # noqa: BLE001
        check("gated send refused (PENDING, nothing granted)", False, str(e))

    # 7. Unknown task type -> error, no crash
    try:
        tasks_p, appr_p = tmp_paths()
        r = chief.handle_task({"type": "fly_to_moon", "title": "check unknown"},
                              tasks_path=tasks_p, approvals_path=appr_p)
        check("unknown task type -> error (no crash)", r["status"] == "error", r["status"])
    except Exception as e:  # noqa: BLE001
        check("unknown task type -> error (no crash)", False, str(e))

    # 8. Main CEO Bot -> Products Chief end-to-end (TEMP paths)
    try:
        import main_ceo_bot  # noqa: PLC0415

        tasks_p, appr_p = tmp_paths()
        r = main_ceo_bot.route_task(
            {"business": "digital-product", "type": "clinic_research",
             "title": "check end-to-end"},
            tasks_path=tasks_p, approvals_path=appr_p)
        ok = (r["status"] == "draft-ready"
              and r["chief_result"]["handler"] == "pa-list"
              and r["chief_result"]["output"]["pa_list"]["rows"] >= 25)
        check("main_ceo_bot -> chief -> clinic_research", ok,
              f"status={r['status']}, rows={r['chief_result']['output']['pa_list']['rows']}")
    except Exception as e:  # noqa: BLE001
        check("main_ceo_bot -> chief -> clinic_research", False, str(e))

    # 9. PA list CSV parses: >=25 rows, name/city/website present,
    #    email is real (@) or "Not publicly listed" — nothing invented
    try:
        csv_path = os.path.join(BASE, "02-Digital-Product-Department",
                                "pa-vet-list", "pa-vet-clinics.csv")
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        bad = []
        for i, row in enumerate(rows, start=2):
            if not row.get("clinic_name") or not row.get("city"):
                bad.append(f"line {i}: missing name/city")
            if not (row.get("website") or "").startswith("http"):
                bad.append(f"line {i}: bad website")
            email = row.get("public_email", "")
            if email != "Not publicly listed" and "@" not in email:
                bad.append(f"line {i}: bad email {email!r}")
            if not row.get("source_url", "").startswith("http"):
                bad.append(f"line {i}: missing source_url")
        cities = {r.get("city") for r in rows}
        ok = len(rows) >= 25 and not bad and len(cities) >= 5
        check("PA list CSV parses (>=25 real rows, no invented email)",
              ok, f"rows={len(rows)}, cities={len(cities)}" + (f", bad={bad[:3]}" if bad else ""))
    except Exception as e:  # noqa: BLE001
        check("PA list CSV parses (>=25 real rows, no invented email)", False, str(e))

    # 10. tasks.json valid + other departments' entries preserved
    try:
        d = tempfile.mkdtemp()
        tasks_p = os.path.join(d, "tasks.json")
        appr_p = os.path.join(d, "approvals.json")
        seed = {"schema": "tasks-v1", "records": [
            {"id": "seed00000002", "department": "agency",
             "title": "seeded other-department entry", "type": None,
             "worker": None, "status": "draft-ready", "logged_at": "2026-11-16T00:00:00Z"}]}
        with open(tasks_p, "w", encoding="utf-8") as f:
            json.dump(seed, f)
        chief.handle_task({"type": "gate0_check", "title": "check preserve"},
                          tasks_path=tasks_p, approvals_path=appr_p)
        with open(tasks_p, encoding="utf-8") as f:
            data = json.load(f)
        kept = any(x["id"] == "seed00000002" for x in data["records"])
        ok = kept and len(data["records"]) == 2 and data["schema"] == "tasks-v1"
        check("tasks.json valid + other dept entry preserved", ok,
              f"records={len(data['records'])}, seed kept={kept}")
    except Exception as e:  # noqa: BLE001
        check("tasks.json valid + other dept entry preserved", False, str(e))

    # 11. Real store unchanged by this check run (Phase 9: live queue)
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    # 12. Dashboard shows Phase 2 + Gate 0 NOT PASSED + PA list count
    try:
        with open(os.path.join(BASE, "dashboards", "status.html"), encoding="utf-8") as f:
            html = f.read()
        ok = ("Phase 2" in html and "Gate 0" in html and "NOT PASSED" in html
              and "39" in html and "PA list" in html)
        check("dashboard shows Phase 2 + Gate 0 NOT PASSED + PA list 39", ok)
    except Exception as e:  # noqa: BLE001
        check("dashboard shows Phase 2 + Gate 0 NOT PASSED + PA list 39", False, str(e))

    # 13. config.json gates ON + $0 cap + phase 2
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        ok = (cfg.get("spend_cap_usd") == 0
              and cfg.get("gates", {}).get("enabled") is True
              and cfg.get("phase", 0) >= 2)
        check("config.json gates ON + $0 cap + phase >= 2", ok)
    except Exception as e:  # noqa: BLE001
        check("config.json gates ON + $0 cap + phase 2", False, str(e))

    # 14. Phase 0 + Phase 1 checks still pass
    try:
        p0 = subprocess.run([sys.executable, os.path.join(BASE, "scripts", "check_phase0.py")],
                            capture_output=True, text=True, timeout=120)
        p1 = subprocess.run([sys.executable, os.path.join(BASE, "scripts", "check_phase1.py")],
                            capture_output=True, text=True, timeout=120)
        ok = p0.returncode == 0 and p1.returncode == 0
        check("check_phase0 + check_phase1 still PASS", ok,
              f"p0={p0.returncode}, p1={p1.returncode}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0 + check_phase1 still PASS", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 2 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
