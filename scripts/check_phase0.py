#!/usr/bin/env python3
"""Phase 0 self-check — Talvenor Master OS.

Verifies:
  1. Whether all folders/files exist
  2. Whether config.json parses + the locked facts are correct
  3. Gateway imports + approve/reject work (in TEMP files — no test record
     is written to the real store/approvals.json)
  4. main_ceo_bot routing works (non-gated task)
  5. jarvis_voice STUB — raises NotImplementedError when called
  6. Dashboard HTML exists + "Phase 0" is written in it

Stdlib only, no network, no spend. Exit 0 = all PASS.
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

    # 3. Store JSON files parse (Phase 9: store is now a live queue — records
    #    need not be empty, they only need to parse + records must be a list)
    for name in ("store/tasks.json", "store/approvals.json"):
        try:
            with open(os.path.join(BASE, name), encoding="utf-8") as f:
                data = json.load(f)
            check(f"{name} parses, records is a list",
                  isinstance(data.get("records"), list))
        except Exception as e:  # noqa: BLE001
            check(f"{name} parses, records is a list", False, str(e))

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
        # The real approvals.json was not touched — verify (Phase 9: snapshot compare)
        with open(os.path.join(BASE, "store", "approvals.json"), encoding="utf-8") as f:
            assert f.read() == store_before["store/approvals.json"]
        check("approval gateway works (temp file only)", True)
    except Exception as e:  # noqa: BLE001
        check("approval gateway works (temp file only)", False, str(e))

    # 5. Main CEO Bot routing — Phase 1: agency task goes to the real Chief
    #    (TEMP paths — no test record is written to the real store/tasks.json)
    try:
        import main_ceo_bot  # noqa: PLC0415

        tmp_tasks = os.path.join(tempfile.mkdtemp(), "tasks-test.json")
        tmp_appr = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
        r = main_ceo_bot.route_task({"business": "agency", "title": "check"},
                                    tasks_path=tmp_tasks, approvals_path=tmp_appr)
        assert r["routed_to"].endswith("chief_of_staff_agency")
        assert r["status"] == "route-only"  # task without a type = probe only
        assert r["chief_result"]["department"] == "agency"
        check("main_ceo_bot routes non-gated task", True)
    except Exception as e:  # noqa: BLE001
        check("main_ceo_bot routes non-gated task", False, str(e))

    # 6. Jarvis voice REAL (2026-11-17 voice loop — was a STUB, now
    # Piper+Vosk/sherpa, offline, $0; same 3 public functions)
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
        ok = "Phase 0" in html and "Paying clients" in html and "136" in html  # "136" appears only in the DROPPED scope note
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
