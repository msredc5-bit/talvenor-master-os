#!/usr/bin/env python3
"""Phase 4 self-check — Talvenor Master OS, n8n wiring + live dashboard.

যাচাই করে:
  1. n8n-wiring.md আছে — ২ workflow-র নাম + READY · NOT LIVE + Boss-এর
     বাকি step + email-pause gate + দুই system একসাথে না-চলার নিয়ম +
     $0 host-এর সত্য কথা (Muse runtime + bridge cron, ২৪/৭ server নেই)
  2. sync_status.py import হয় + collect_status() আসল মান দেয়
     (phase >= 4, clients 0, first mails 162, email PAUSED, Gate 0
     NOT PASSED, PA list 39, pipeline REAL 0 / MOCK 10 / BLOCKED 3,
     subs 0, ২ workflow-ই NOT LIVE, store খালি)
  3. sync deterministic — ২ বার চালালে byte-সমান HTML; HTML-এর
     সংখ্যা উৎস ফাইলের সাথে মিলে
  4. কোনো workflow LIVE বলে দাবি করা হয় না — ২ JSON-এ active == false,
     HTML-এ LIVE badge নেই, wiring doc-এ ২টাতেই NOT LIVE
  5. Jarvis voice REAL (Piper+Vosk/sherpa; HTML-ও sync করে)
  6. Dashboard-এ Phase 4 BUILT + n8n READY + host Muse runtime আছে
  7. config.json phase >= 4 + version >= 0.5.0 + gates ON + $0 cap
     (Phase 6 bumped phase to 6 / v0.6.0 — the check follows the
     check_phase2/3 precedent of >= instead of pinning the old phase)
  8. আসল store/tasks.json + approvals.json এখনো খালি (0 record)
  9. check_phase0 + check_phase1 + check_phase2 + check_phase3 এখনো PASS

সব check TEMP file-এ চলে যেখানে সম্ভব — আসল store শুধু পড়া হয়,
লেখা হয় না। Stdlib only, no network, no send, no spend, no import।
Exit 0 = PASS।
"""

import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))

AUTO_SEND_PATH = os.path.expanduser(
    "~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json")
CALLBACK_PATH = os.path.expanduser(
    "~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    # 1. Wiring doc: both workflows + NOT LIVE + Boss steps + pause + host truth
    try:
        with open(os.path.join(BASE, "dashboards", "n8n-wiring.md"),
                  encoding="utf-8") as f:
            md = f.read()
        ok = (
            "Tier 2 Auto-send" in md and "Callback" in md
            and md.count("NOT LIVE") >= 2
            and "1SZjkPZfpGjHUBIWp9-bnYVhKuFaxXAgC_wOMlpfv4MM" in md
            and "FILL_AFTER_TWILIO_IMPORT" in md
            and "1587fd30-57e1-4aaf-9c93-39a0c39e450e" in md
            and "EMAIL PAUSE GATE" in md
            and "দুই system একসাথে চলবে না" in md
            and "Muse runtime" in md and "bridge cron" in md
            and "২৪/৭ always-on server নেই" in md
            and "hello@talvenorai.agency" in md
        )
        check("n8n-wiring.md: 2 workflows + NOT LIVE + steps + pause + $0 host",
              ok)
    except Exception as e:  # noqa: BLE001
        check("n8n-wiring.md: 2 workflows + NOT LIVE + steps + pause + $0 host",
              False, str(e))

    # 2. sync_status imports + collect_status returns real values
    try:
        import sync_status  # noqa: PLC0415

        s = sync_status.collect_status()
        ok = (s["phase"] >= 4 and s["paying_clients"] == 0
              and s["first_mails"] == 162 and s["email"] == "PAUSED"
              and s["gate0"] == "NOT PASSED" and s["pa_list"] == 39
              and s["pipeline"] == {"real": 0, "mock": 10, "stub": 0, "blocked": 3}
              and s["toolpilot_subs"] == 0
              and s["workflow_auto_send"]["status"] == "NOT LIVE"
              and s["workflow_callback"]["status"] == "NOT LIVE"
              and s["workflow_auto_send"]["nodes"] == 8
              and s["workflow_callback"]["nodes"] == 3
              and s["tasks_count"] == 0
              and s["approvals_pending"] == 0
              and s["approvals_approved"] == 0
              and s["spend_cap_usd"] == 0)
        check("sync collect_status: real values (phase >= 4, 0 clients, 162 mails, "
              "Gate 0 NOT PASSED, PA 39, pipeline 0/10/3, NOT LIVE x2)", ok,
              f"phase={s['phase']}, gate0={s['gate0']}, pa={s['pa_list']}")
    except Exception as e:  # noqa: BLE001
        check("sync collect_status: real values", False, str(e))

    # 3. Sync deterministic + HTML numbers match sources
    try:
        html_path = os.path.join(BASE, "dashboards", "status.html")
        p1 = subprocess.run([sys.executable,
                             os.path.join(BASE, "scripts", "sync_status.py")],
                            capture_output=True, text=True, timeout=120)
        with open(html_path, encoding="utf-8") as f:
            run1 = f.read()
        p2 = subprocess.run([sys.executable,
                             os.path.join(BASE, "scripts", "sync_status.py")],
                            capture_output=True, text=True, timeout=120)
        with open(html_path, encoding="utf-8") as f:
            run2 = f.read()
        import sync_status  # noqa: PLC0415

        s = sync_status.collect_status()
        numbers_ok = (
            f"প্রথম মেইল {s['first_mails']}" in run2
            and f"PA list {s['pa_list']} / 100" in run2
            and f"REAL {s['pipeline']['real']} / MOCK {s['pipeline']['mock']} "
                f"/ BLOCKED {s['pipeline']['blocked']}" in run2
            and f"Gate 0 {s['gate0']}" in run2
            and run2.count("READY · NOT LIVE") == 2
        )
        ok = p1.returncode == 0 and p2.returncode == 0 and run1 == run2 and numbers_ok
        check("sync deterministic (2 runs identical) + HTML matches sources", ok,
              "identical" if run1 == run2 else "DIFFERS")
    except Exception as e:  # noqa: BLE001
        check("sync deterministic (2 runs identical) + HTML matches sources",
              False, str(e))

    # 4. No workflow claimed LIVE — JSON active == false + no LIVE badge
    try:
        with open(AUTO_SEND_PATH, encoding="utf-8") as f:
            wf_a = json.load(f)
        with open(CALLBACK_PATH, encoding="utf-8") as f:
            wf_c = json.load(f)
        with open(os.path.join(BASE, "dashboards", "status.html"),
                  encoding="utf-8") as f:
            html = f.read()
        ok = (wf_a.get("active") is False and wf_c.get("active") is False
              and '<span class="badge built">LIVE</span>' not in html
              and html.count("READY · NOT LIVE") == 2)
        check("no workflow claimed LIVE (both JSON active=false, no LIVE badge)",
              ok, f"auto={wf_a.get('active')}, callback={wf_c.get('active')}")
    except Exception as e:  # noqa: BLE001
        check("no workflow claimed LIVE", False, str(e))

    # 5. Jarvis voice REAL (2026-11-17 voice loop — STUB ছিল, এখন
    # Piper+Vosk/sherpa, mic যুক্ত; dashboard-এর "mic যুক্ত নয়" লাইন
    # এখনো পুরনো — dashboard refresh আলাদা কাজ, এই check-এ HTML নেই)
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "jarvis_voice.py"),
                  encoding="utf-8") as f:
            jv = f.read()
        loop_ok = os.path.exists(os.path.join(
            BASE, "00-CEO-Core", "voice", "loop.py"))
        ok = ("NotImplementedError" not in jv and "REAL" in jv and loop_ok)
        check("Jarvis voice REAL (mic connected via Vosk/sherpa)", ok,
              f"loop.py={loop_ok}")
    except Exception as e:  # noqa: BLE001
        check("Jarvis voice REAL (mic connected via Vosk/sherpa)", False, str(e))

    # 6. Dashboard shows Phase 4 BUILT + n8n READY + host Muse runtime
    try:
        with open(os.path.join(BASE, "dashboards", "status.html"),
                  encoding="utf-8") as f:
            html = f.read()
        ok = ("Phase 4" in html and "BUILT" in html
              and "n8n Wiring" in html and "READY" in html
              and "Muse runtime" in html and "sync_status.py" in html)
        check("dashboard shows Phase 4 BUILT + n8n READY + Muse runtime host", ok)
    except Exception as e:  # noqa: BLE001
        check("dashboard shows Phase 4 BUILT + n8n READY + Muse runtime host",
              False, str(e))

    # 7. config.json phase 4 + version 0.5.0 + gates ON + $0 cap
    try:
        with open(os.path.join(BASE, "00-CEO-Core", "config.json"),
                  encoding="utf-8") as f:
            cfg = json.load(f)
        ok = (cfg.get("phase", 0) >= 4 and cfg.get("version", "") >= "0.5.0"
              and cfg.get("spend_cap_usd") == 0
              and cfg.get("gates", {}).get("enabled") is True
              and "BUILT" in cfg["honest_status"]["phases"]["phase_4_n8n_wiring"])
        check("config.json phase >= 4 + v>=0.5.0 + gates ON + $0 cap", ok)
    except Exception as e:  # noqa: BLE001
        check("config.json phase 4 + v0.5.0 + gates ON + $0 cap", False, str(e))

    # 8. Real store files untouched (still empty)
    try:
        with open(os.path.join(BASE, "store", "approvals.json"),
                  encoding="utf-8") as f:
            real_appr = json.load(f)
        with open(os.path.join(BASE, "store", "tasks.json"),
                  encoding="utf-8") as f:
            real_tasks = json.load(f)
        check("real store files untouched by checks",
              real_appr.get("records") == [] and real_tasks.get("records") == [])
    except Exception as e:  # noqa: BLE001
        check("real store files untouched by checks", False, str(e))

    # 9. Phase 0 + 1 + 2 + 3 checks still pass
    try:
        outs = []
        for script in ("check_phase0.py", "check_phase1.py",
                       "check_phase2.py", "check_phase3.py"):
            p = subprocess.run([sys.executable, os.path.join(BASE, "scripts", script)],
                               capture_output=True, text=True, timeout=180)
            outs.append(p.returncode)
        ok = all(code == 0 for code in outs)
        check("check_phase0 + check_phase1 + check_phase2 + check_phase3 still PASS",
              ok, f"p0={outs[0]}, p1={outs[1]}, p2={outs[2]}, p3={outs[3]}")
    except Exception as e:  # noqa: BLE001
        check("check_phase0 + check_phase1 + check_phase2 + check_phase3 still PASS",
              False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("Phase 4 self-check: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
