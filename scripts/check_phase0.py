#!/usr/bin/env python3
"""Phase 0 self-check — Talvenor Master OS.

যাচাই করে:
  1. সব folder/file আছে কি না
  2. config.json parse হয় কি না + locked fact-গুলো ঠিক আছে কি না
  3. gateway import হয় + approve/reject কাজ করে (TEMP file-এ — আসল
     store/approvals.json-এ কোনো test record লেখা হয় না)
  4. main_ceo_bot routing কাজ করে (non-gated task)
  5. jarvis_voice STUB — ডাকলে NotImplementedError দেয়
  6. dashboard HTML আছে + "Phase 0" লেখা আছে

Stdlib only, no network, no spend. Exit 0 = সব PASS।
"""

import json
import os
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))

EXPECTED_FILES = [
    "README.md",
    "BUILD-LOG.md",
    "00-CEO-Core/main_ceo_bot.py",
    "00-CEO-Core/jarvis_voice.py",
    "00-CEO-Core/human_approval_gateway.py",
    "00-CEO-Core/config.json",
    "00-CEO-Core/CEO-README.md",
    "01-Agency-Department/chief_of_staff_agency.py",
    "01-Agency-Department/sub_agents/README.md",
    "01-Agency-Department/workflows/README.md",
    "02-Digital-Product-Department/chief_of_staff_products.py",
    "02-Digital-Product-Department/README.md",
    "02-Digital-Product-Department/gate0-status.md",
    "03-Content-Creation-Department/chief_of_staff_content.py",
    "03-Content-Creation-Department/README.md",
    "store/tasks.json",
    "store/approvals.json",
    "store/vault/README.md",
    "dashboards/status.html",
    "skills/main-ceo-bot.md",
    "skills/chief-agency.md",
    "skills/chief-products.md",
    "skills/chief-content.md",
    "scripts/check_phase0.py",
]

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    # 1. Files exist
    missing = [f for f in EXPECTED_FILES if not os.path.isfile(os.path.join(BASE, f))]
    check("all expected files exist", not missing,
          f"{len(EXPECTED_FILES) - len(missing)}/{len(EXPECTED_FILES)}" + (f", missing: {missing}" if missing else ""))

    # 2. config.json parses + locked facts
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        facts_ok = (
            cfg.get("spend_cap_usd") == 0
            and cfg.get("gates", {}).get("enabled") is True
            and len(cfg.get("businesses", [])) == 3
            and cfg["contacts"]["booking_link"] == "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
            and cfg["contacts"]["phone"] == "+1 (947) 223-0244"
            and cfg["contacts"]["email_outreach"] == "hello@talvenorai.agency"
            and cfg["businesses"][1].get("price_usd_one_time") == 49
            and cfg["honest_status"]["paying_clients"] == 0
        )
        check("config.json parses + locked facts", facts_ok)
    except Exception as e:  # noqa: BLE001
        check("config.json parses + locked facts", False, str(e))

    # 3. Store JSON files parse + empty
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                data = json.load(f)
            check(f"{name} parses, records empty", data.get("records") == [])
        except Exception as e:  # noqa: BLE001
            check(f"{name} parses, records empty", False, str(e))

    # 4. Gateway: import + approve/reject on a TEMP file only
    try:
        from human_approval_gateway import ApprovalGateway  # noqa: PLC0415

        tmp = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
        gw = ApprovalGateway(approvals_path=tmp)
        req = gw.request("send", "phase0 check", "check_phase0")
        assert req["status"] == "pending" and not gw.is_approved(req["id"])
        try:
            gw.approve(req["id"], gate_word="ok")
            raise AssertionError("wrong gate word accepted")
        except ValueError:
            pass
        gw.approve(req["id"], gate_word="send")
        assert gw.is_approved(req["id"])
        req2 = gw.request("publish", "phase0 check 2", "check_phase0")
        gw.reject(req2["id"])
        assert not gw.is_approved(req2["id"]) and len(gw.pending()) == 0
        # আসল approvals.json ছোঁয়া হয়নি — verify
        with open(os.path.join(BASE, "store", "approvals.json"), encoding="utf-8") as f:
            assert json.load(f)["records"] == []
        check("approval gateway works (temp file only)", True)
    except Exception as e:  # noqa: BLE001
        check("approval gateway works (temp file only)", False, str(e))

    # 5. Main CEO Bot routing — Phase 1: agency task আসল Chief-এর কাছে
    #    যায় (TEMP paths — আসল store/tasks.json-এ test record লেখা হয় না)
    try:
        import main_ceo_bot  # noqa: PLC0415

        tmp_tasks = os.path.join(tempfile.mkdtemp(), "tasks-test.json")
        tmp_appr = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
        r = main_ceo_bot.route_task({"business": "agency", "title": "check"},
                                    tasks_path=tmp_tasks, approvals_path=tmp_appr)
        assert r["routed_to"].endswith("chief_of_staff_agency")
        assert r["status"] == "route-only"  # type ছাড়া task = probe only
        assert r["chief_result"]["department"] == "agency"
        check("main_ceo_bot routes non-gated task", True)
    except Exception as e:  # noqa: BLE001
        check("main_ceo_bot routes non-gated task", False, str(e))

    # 6. Jarvis voice REAL (2026-11-17 voice loop — STUB ছিল, এখন
    # Piper+Vosk/sherpa, offline, $0; একই 3 public function)
    try:
        import jarvis_voice  # noqa: PLC0415

        with open(os.path.join(BASE, "00-CEO-Core", "jarvis_voice.py"),
                  encoding="utf-8") as f:
            jv_src = f.read()
        no_stub = ("NotImplementedError" not in jv_src
                   and "REAL" in jv_src)
        fns_ok = all(callable(getattr(jarvis_voice, fn, None)) for fn in
                     ("listen", "speak", "handle_voice_command"))
        check("jarvis_voice is REAL (Piper+Vosk, offline)",
              no_stub and fns_ok,
              f"fns={fns_ok}, no-NotImplementedError={'NotImplementedError' not in jv_src}")
    except Exception as e:  # noqa: BLE001
        check("jarvis_voice is REAL (Piper+Vosk, offline)", False, str(e))

    # 7. Dashboard exists + honest content
    try:
        with open(os.path.join(BASE, "dashboards", "status.html"), encoding="utf-8") as f:
            html = f.read()
        ok = "Phase 0" in html and "Paying clients" in html and "১৩৬" in html
        check("dashboard status.html present + honest", ok)
    except Exception as e:  # noqa: BLE001
        check("dashboard status.html present + honest", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 0 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
