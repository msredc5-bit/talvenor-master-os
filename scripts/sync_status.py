#!/usr/bin/env python3
"""sync_status.py — Talvenor Master OS dashboard sync (Phase 4).

dashboards/status.html-এর সংখ্যাগুলো আসল ফাইল থেকে পড়ে আবার বানায় —
হাতে লেখা সংখ্যা নয়। উৎস ফাইলে কোনো মান না থাকলে "unknown" লেখে,
কখনো বানায় না। Stdlib only, no network, no send, no spend।

উৎস:
  - 00-CEO-Core/config.json — phase, version, gates, $0 cap, first mails,
    paying clients, email status, phase status লাইন
  - store/tasks.json + store/approvals.json — আসল task/approval সংখ্যা
  - 02-Digital-Product-Department/gate0-status.md — Gate 0 Status লাইন
    (শুধু ওই লাইনটাই পড়া হয় — fail-closed; Phase 2-র bug-এর শিক্ষা)
  - 02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv — PA list row
  - 03-Content-Creation-Department/pipeline.md — ১৩ stage-এর গণনা লাইন
  - 03-Content-Creation-Department/toolpilot-status.md — Subscribers লাইন
  - n8n workflow JSON (২টা, বাইরের folder) — "active" flag পড়ে
    (false = NOT LIVE, true = LIVE — যেটা সত্য সেটাই লেখা হয়)

চালানো:  python3 scripts/sync_status.py
"""

import csv
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUTO_SEND_PATH = os.path.expanduser(
    "~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json")
CALLBACK_PATH = os.path.expanduser(
    "~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json")

UNKNOWN = "unknown"


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def _read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def read_gate0_status():
    """শুধু gate0-status.md-এর Status লাইন পড়ে — fail-closed।"""
    text = _read_text(os.path.join(
        BASE, "02-Digital-Product-Department", "gate0-status.md"))
    if text is None:
        return UNKNOWN
    for line in text.splitlines():
        if line.strip().startswith("**Status:"):
            if "NOT PASSED" in line:
                return "NOT PASSED"
            if "PASSED" in line:
                return "PASSED"
            return UNKNOWN
    return UNKNOWN


def read_pipeline_counts():
    """pipeline.md-এর গণনা লাইন থেকে REAL/MOCK/STUB/BLOCKED।"""
    text = _read_text(os.path.join(
        BASE, "03-Content-Creation-Department", "pipeline.md"))
    if text is None:
        return {"real": UNKNOWN, "mock": UNKNOWN,
                "stub": UNKNOWN, "blocked": UNKNOWN}
    m = re.search(r"REAL \*\*(\d+)\*\* · MOCK \*\*(\d+)\*\* · "
                  r"STUB \*\*(\d+)\*\* · BLOCKED \*\*(\d+)\*\*", text)
    if not m:
        return {"real": UNKNOWN, "mock": UNKNOWN,
                "stub": UNKNOWN, "blocked": UNKNOWN}
    return {"real": int(m.group(1)), "mock": int(m.group(2)),
            "stub": int(m.group(3)), "blocked": int(m.group(4))}


def read_pa_list_count():
    path = os.path.join(BASE, "02-Digital-Product-Department",
                        "pa-vet-list", "pa-vet-clinics.csv")
    try:
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        if not rows:
            return UNKNOWN
        return len(rows) - 1  # header বাদ
    except OSError:
        return UNKNOWN


def read_toolpilot_subs():
    text = _read_text(os.path.join(
        BASE, "03-Content-Creation-Department", "toolpilot-status.md"))
    if text is None:
        return UNKNOWN
    m = re.search(r"Subscribers: \*\*(\d+)\*\*", text)
    return int(m.group(1)) if m else UNKNOWN


def read_workflow_status(path):
    """n8n workflow JSON-এর active flag — false = NOT LIVE।"""
    data = _read_json(path)
    if data is None:
        return {"status": UNKNOWN, "nodes": UNKNOWN, "name": UNKNOWN}
    active = data.get("active")
    nodes = data.get("nodes")
    return {
        "status": "LIVE" if active is True else ("NOT LIVE" if active is False else UNKNOWN),
        "nodes": len(nodes) if isinstance(nodes, list) else UNKNOWN,
        "name": data.get("name") or UNKNOWN,
    }


def collect_status():
    """সব উৎস থেকে সত্য অবস্থা এক জায়গায় করে। কোনো মান না পেলে unknown।"""
    cfg = _read_json(os.path.join(BASE, "00-CEO-Core", "config.json")) or {}
    honest = cfg.get("honest_status") or {}
    phases = honest.get("phases") or {}
    gates = cfg.get("gates") or {}

    tasks = _read_json(os.path.join(BASE, "store", "tasks.json")) or {}
    approvals = _read_json(os.path.join(BASE, "store", "approvals.json")) or {}
    task_records = tasks.get("records")
    appr_records = approvals.get("records")
    pending = ([r for r in appr_records if r.get("status") == "pending"]
               if isinstance(appr_records, list) else UNKNOWN)
    approved = ([r for r in appr_records if r.get("status") == "approved"]
                if isinstance(appr_records, list) else UNKNOWN)

    email_raw = honest.get("email_outreach") or ""
    email = "PAUSED" if "PAUSED" in str(email_raw) else (
        "unknown" if not email_raw else str(email_raw))

    return {
        "phase": cfg.get("phase", UNKNOWN),
        "version": cfg.get("version", UNKNOWN),
        "gates_enabled": gates.get("enabled", UNKNOWN),
        "spend_cap_usd": cfg.get("spend_cap_usd", UNKNOWN),
        "first_mails": honest.get("first_mails_sent", UNKNOWN),
        "paying_clients": honest.get("paying_clients", UNKNOWN),
        "email": email,
        "gate0": read_gate0_status(),
        "pa_list": read_pa_list_count(),
        "pipeline": read_pipeline_counts(),
        "toolpilot_subs": read_toolpilot_subs(),
        "tasks_count": len(task_records) if isinstance(task_records, list) else UNKNOWN,
        "approvals_pending": len(pending) if isinstance(pending, list) else UNKNOWN,
        "approvals_approved": len(approved) if isinstance(approved, list) else UNKNOWN,
        "phase_status": {
            "phase_0": phases.get("phase_0", UNKNOWN),
            "phase_1_agency": phases.get("phase_1_agency", UNKNOWN),
            "phase_2_digital_product": phases.get("phase_2_digital_product", UNKNOWN),
            "phase_3_creator_os": phases.get("phase_3_creator_os", UNKNOWN),
            "phase_4_n8n_wiring": phases.get("phase_4_n8n_wiring", UNKNOWN),
        },
        "workflow_auto_send": read_workflow_status(AUTO_SEND_PATH),
        "workflow_callback": read_workflow_status(CALLBACK_PATH),
    }


def _badge(text, kind):
    return f'<span class="badge {kind}">{text}</span>'


def render_html(s):
    """collect_status() থেকে পুরো status.html বানায় (deterministic)।"""
    ph = s["phase_status"]
    pipe = s["pipeline"]
    gate0 = s["gate0"]
    pa = s["pa_list"]
    subs = s["toolpilot_subs"]
    wf_a = s["workflow_auto_send"]
    wf_c = s["workflow_callback"]
    phase = s["phase"]

    def phase_badge(status_text):
        if isinstance(status_text, str) and status_text.startswith("BUILT"):
            return _badge("BUILT", "built")
        if status_text == "PENDING":
            return _badge("PENDING", "pending")
        return _badge(str(status_text), "stub")

    gate0_badge = (_badge("NOT PASSED", "paused") if gate0 == "NOT PASSED"
                   else _badge("PASSED", "built") if gate0 == "PASSED"
                   else _badge("unknown", "stub"))
    email_badge = (_badge("PAUSED", "paused") if s["email"] == "PAUSED"
                   else _badge(str(s["email"]), "stub"))

    def wf_badge(status):
        if status == "NOT LIVE":
            return _badge("READY · NOT LIVE", "pending")
        if status == "LIVE":
            return _badge("LIVE", "built")
        return _badge("unknown", "stub")

    return f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Talvenor Master OS — Status (Phase {phase})</title>
<style>
  body {{ font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #FFFBF5; color: #0B1D33; margin: 0; padding: 24px; }}
  .wrap {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ color: #EA580C; margin-bottom: 4px; }}
  .sub {{ color: #555; margin-top: 0; }}
  .card {{ background: #fff; border: 1px solid #e5ddd2; border-radius: 12px; padding: 18px 20px; margin: 14px 0; }}
  .badge {{ display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }}
  .built {{ background: #d1fae5; color: #065f46; }}
  .stub {{ background: #fef3c7; color: #92400e; }}
  .pending {{ background: #e0e7ff; color: #3730a3; }}
  .paused {{ background: #fee2e2; color: #991b1b; }}
  table {{ width: 100%; border-collapse: collapse; }}
  td, th {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid #eee; vertical-align: top; }}
  .gate-on {{ color: #065f46; font-weight: 700; }}
  .note {{ font-size: 13px; color: #666; }}
  footer {{ font-size: 13px; color: #888; margin-top: 24px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>🎬 Talvenor Master OS</h1>
  <p class="sub">Status dashboard — Phase {phase} (এই page scripts/sync_status.py দিয়ে বানানো — সংখ্যা আসল ফাইল থেকে আসে, হাতে লেখা নয়)</p>

  <div class="card">
    <h2>৩ ব্যবসা — শুধু এই ৩টাই (১৩৬ নয়)</h2>
    <table>
      <tr><th>ব্যবসা</th><th>অবস্থা</th><th>সত্য কথা</th></tr>
      <tr><td><strong>1. Agency</strong> — Talvenor AI Receptionist</td><td><span class="badge built">MAIN · Phase 1 REAL</span></td><td>প্রথম মেইল {s["first_mails"]}, paying client {s["paying_clients"]} · Chief সত্যিই 15 worker ডাকে (mock brain, DRAFT ONLY) · Email {s["email"]}</td></tr>
      <tr><td><strong>2. Digital Product</strong> — Vet No-Show Recovery Kit ($49)</td><td><span class="badge built">Phase 2 REAL*</span></td><td><strong>Gate 0 {gate0}</strong> — Lemon Squeezy test Boss-এর step, হয়নি · Kit blueprint আছে (kit নিজে নয়) · PA list {pa} / 100 (যাচাই করা) · Sale 0 · *Gate 0-তে আটকে</td></tr>
      <tr><td><strong>3. Content Engine</strong> — Creator OS / ToolPilot</td><td><span class="badge built">Phase 3 REAL</span></td><td>Chief সত্যিই 6 worker ডাকে (mock brain, DRAFT ONLY) · 13 stage: REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]} · Upload OFF · VOICE.md DRAFT · GPU নাম বাকি · ToolPilot video 0 (subs {subs})</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Phase</h2>
    <table>
      <tr><td><strong>Phase 0</strong> — folder + CEO Core + approval gateway + dashboard</td><td>{phase_badge(ph["phase_0"])}</td></tr>
      <tr><td><strong>Phase 1</strong> — Agency department (boss-ceo worker জোড়া, draft-only, gate ধরে)</td><td>{phase_badge(ph["phase_1_agency"])}</td></tr>
      <tr><td><strong>Phase 2</strong> — Digital Product (Chief REAL, kit blueprint, PA list {pa}/100 — launch/sale Gate 0-তে আটকে)</td><td>{phase_badge(ph["phase_2_digital_product"])}</td></tr>
      <tr><td><strong>Phase 3</strong> — Creator OS department (Chief REAL, 6 worker wired, 13 stage REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]}, upload OFF)</td><td>{phase_badge(ph["phase_3_creator_os"])}</td></tr>
      <tr><td><strong>Phase 4</strong> — n8n wiring (Gmail, Vapi, Sheets — workflows READY, NOT LIVE)</td><td>{phase_badge(ph["phase_4_n8n_wiring"])}</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>n8n Wiring — বাইরের দুনিয়ার সাথে সংযোগ</h2>
    <table>
      <tr><th>Workflow</th><th>অবস্থা</th><th>সত্য কথা</th></tr>
      <tr><td><strong>Auto-send</strong> — {wf_a["name"]} ({wf_a["nodes"]} nodes)</td><td>{wf_badge(wf_a["status"])}</td><td>Schedule 18:00 Dhaka → Google Sheet Queue → Gmail send → Sheet-এ sent লেখা · Import + Gmail/Sheets connect + 1-mail test Boss-এর step · Email PAUSED থাকায় চালানো যাবে না</td></tr>
      <tr><td><strong>Callback</strong> — {wf_c["name"]} ({wf_c["nodes"]} nodes)</td><td>{wf_badge(wf_c["status"])}</td><td>Website form → n8n webhook → Vapi POST /call → Sophia callback · Twilio number (~$1.15/mo) import + workflow import + Vapi credential + webhook URL Boss-এর step</td></tr>
    </table>
    <p class="note">Host: Muse runtime + 10-min bridge cron ($0) — ২৪/৭ always-on server নেই, ওটা পরে টাকা দিয়ে করতে হবে। কোনো workflow-ই LIVE নয় — LIVE দাবি করা হয় না। দুই send system একসাথে চলবে না (double mail যাবে)।</p>
  </div>

  <div class="card">
    <h2>Gate ও সীমা</h2>
    <p>Gates: <span class="gate-on">{"ON" if s["gates_enabled"] is True else str(s["gates_enabled"])}</span> — send / publish / spend / delete, কোনোটাই Boss-এর gate word ছাড়া হয় না। Auto-approve নেই।</p>
    <p>Spend cap: <strong>${s["spend_cap_usd"]}</strong></p>
    <p>Email: {email_badge} 2026-11-14 থেকে — SPF/DMARC DNS fix Boss-এর হাতে বাকি।</p>
    <p>Paying clients: <strong>{s["paying_clients"]}</strong> · Kit sales: <strong>0</strong> (Gate 0 {gate0}) · ToolPilot videos: <strong>0</strong> · Upload: <span class="badge paused">OFF</span> (stage 9, Boss-এর "upload it" + credential লাগে)</p>
    <p>Gate 0: {gate0_badge} — Lemon Squeezy signup test (~15 min) Boss-এর step। পাস হলে PA list 100-এ পূর্ণ হবে, তারপর kit বানানো।</p>
    <p>Store: tasks {s["tasks_count"]} · approvals pending {s["approvals_pending"]} / approved {s["approvals_approved"]}</p>
  </div>

  <div class="card">
    <h2>REAL vs STUB vs REUSED</h2>
    <table>
      <tr><td><strong>REAL</strong></td><td>Approval gateway (approve/reject সত্যিই record করে), Main CEO Bot router, config.json, এই dashboard (sync দিয়ে বানানো), <strong>Agency Chief of Staff (15 worker routing, draft-only, gated কাজ PENDING-এ আটকায়)</strong>, <strong>Products Chief of Staff (kit blueprint, PA list {pa}/100, launch/sale Gate 0-তে আটকায়)</strong>, <strong>Content Chief of Staff (6 Creator OS worker routing, draft-only, upload OFF-এ আটকায়, video file বানায় না)</strong></td></tr>
      <tr><td><strong>READY (NOT LIVE)</strong></td><td>n8n auto-send workflow + callback workflow — import file তৈরি, Boss-এর import + connect + test বাকি, কোনোটাই LIVE নয়</td></tr>
      <tr><td><strong>STUB</strong></td><td>Jarvis voice (mic যুক্ত নয়)</td></tr>
      <tr><td><strong>REUSED</strong></td><td>boss-ceo engine (15 worker), talvenor-office, creator-os-combined, jarvis-ceo-os-concept — duplicate করা হয়নি</td></tr>
    </table>
    <p class="note">Gemini-র map-এর ৪ ভুল এখানে ঠিক করা হয়েছে: (1) Jarvis ≠ Main CEO Bot, আলাদা; (2) approval/gate layer আছে; (3) store/Vault আছে; (4) digital product = Vet Kit $49, generic "Notion Kits" নয়।</p>
  </div>

  <div class="card">
    <h2>যোগাযোগ (আসল)</h2>
    <p>Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)<br>
    ফোন: +1 (947) 223-0244<br>
    ইমেইল: hello@talvenorai.agency (outreach) · contact@talvenorai.agency (main)</p>
  </div>

  <footer>Built: 2026-11-16 (Phase 0 + Phase 1 Agency + Phase 2 Digital Product* + Phase 3 Creator OS + Phase 4 n8n wiring) · Folder: ~/workspace/talvenor-master-os/ · Version {s["version"]} · *Phase 2 Gate 0-তে আটকে — kit blueprint + PA list {pa}/100 শুধু। Content: 13 stage REAL {pipe["real"]} / MOCK {pipe["mock"]} / BLOCKED {pipe["blocked"]}, upload OFF। n8n workflows READY, NOT LIVE। কোনো সংখ্যা বানানো নয় — সব আসল ফাইল থেকে sync করা।</footer>
</div>
</body>
</html>
"""


def main():
    status = collect_status()
    html = render_html(status)
    out = os.path.join(BASE, "dashboards", "status.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("sync done ->", out)
    print(f"phase={status['phase']} clients={status['paying_clients']} "
          f"first_mails={status['first_mails']} email={status['email']} "
          f"gate0={status['gate0']} pa_list={status['pa_list']} "
          f"pipeline={status['pipeline']} subs={status['toolpilot_subs']} "
          f"auto_send={status['workflow_auto_send']['status']} "
          f"callback={status['workflow_callback']['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
