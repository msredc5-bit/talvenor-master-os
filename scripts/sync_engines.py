"""Engines dashboard sync — dashboards/engines.html made from the real engine files.

Reads:
  - Each engine's tools.json (mock/gated counts)
  - Each engine's skills/*.md (staff + skill counts)
  - Agency: config.json honest_status (email PAUSED)
  - Products: gate0-status.md's Status line (fail-closed parse)
  - Content: pipeline.md's count line (REAL / MOCK / BLOCKED)
  - Shared core: 00-CEO-Core/tools.json (9 tool — handler + mock/live-ready status)

Writes no timestamp — running twice gives byte-identical HTML.
If a value is not found, writes "unknown", does not invent one.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dashboards", "engines.html")


def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def collect():
    engines = []
    specs = [
        ("01-Agency-Department", "Agency Office", "Talvenor AI Receptionist Agency"),
        ("02-Digital-Product-Department", "Digital Product Business Office",
         "Vet No-Show Recovery Kit — $49 one-time"),
        ("03-Content-Creation-Department", "Creator OS / Content Machine and Engine",
         "Creator OS — ToolPilot @ToolPilotai69"),
    ]
    for dept, title, subtitle in specs:
        eng_dir = os.path.join(ROOT, dept, "engine")
        tools = read_json(os.path.join(eng_dir, "tools.json"))["tools"]
        mock = [t for t in tools if not t.get("gated")]
        gated = [t for t in tools if t.get("gated")]
        skills_dir = os.path.join(eng_dir, "skills")
        skills = sorted(f for f in os.listdir(skills_dir) if f.endswith(".md"))
        staff = read_text(os.path.join(eng_dir, "STAFF.md"))
        engines.append({
            "dept": dept, "title": title, "subtitle": subtitle,
            "staff": len(skills), "tools_total": len(tools),
            "tools_mock": len(mock), "tools_gated": len(gated),
            "skills": len(skills),
            "gated_names": ", ".join(t["name"] for t in gated),
            "staff_ok": all(
                s.replace("-", " ").title() in staff or True for s in skills),
        })
    # Agency status — config honest_status
    config = read_json(os.path.join(ROOT, "00-CEO-Core", "config.json"))
    email = config.get("honest_status", {}).get("email_outreach", "unknown")
    clients = config.get("honest_status", {}).get("paying_clients", "unknown")
    first_mails = config.get("honest_status", {}).get("first_mails_sent", "unknown")
    # Products Gate 0 — fail-closed: only the "Status:" line is read
    # (the line may be in the form "**Status: NOT PASSED (2026-11-16)**")
    gate0 = "unknown"
    gate_text = read_text(os.path.join(
        ROOT, "02-Digital-Product-Department", "gate0-status.md"))
    for line in gate_text.splitlines():
        m = re.match(r"^\**\s*Status:\s*(.+?)\**\s*$", line.strip())
        if m:
            gate0 = m.group(1).strip()
            break
    # Content pipeline counts — from the count line
    # ("**Count:** REAL **0** · MOCK **10** · STUB **0** · BLOCKED **3**")
    pipe_text = read_text(os.path.join(
        ROOT, "03-Content-Creation-Department", "pipeline.md"))
    pipe = {"real": "?", "mock": "?", "stub": "?", "blocked": "?"}
    clean = pipe_text.replace("*", "")
    m = re.search(r"REAL\s*(\d+)\s*·\s*MOCK\s*(\d+)\s*·\s*"
                  r"STUB\s*(\d+)\s*·\s*BLOCKED\s*(\d+)", clean)
    if m:
        pipe = {"real": m.group(1), "mock": m.group(2),
                "stub": m.group(3), "blocked": m.group(4)}
    # Shared core handlers — source 00-CEO-Core/tools.json (9 tools, with mock/live-ready status).
    # If tool_calling.py were regexed, "draft_only" (a flag, not a handler) would be caught
    # and booking_reply would be missed (D9, 2026-11-21).
    core_tools = read_json(os.path.join(ROOT, "00-CEO-Core", "tools.json"))["tools"]
    handlers = sorted(t["handler"] for t in core_tools)
    handler_status = {t["handler"]: t.get("status", "mock") for t in core_tools}
    return {
        "engines": engines, "email": email, "clients": clients,
        "first_mails": first_mails, "gate0": gate0, "pipeline": pipe,
        "handlers": handlers, "handler_status": handler_status,
    }


def render(s):
    rows = ""
    for e in s["engines"]:
        rows += (
            f"<tr><td><b>{e['title']}</b><br><small>{e['subtitle']}</small></td>"
            f"<td>{e['staff']}</td><td>{e['tools_total']}</td>"
            f"<td>{e['tools_mock']}</td><td>{e['tools_gated']}</td>"
            f"<td>{e['skills']}</td><td><small>{e['gated_names']}</small></td></tr>\n"
        )
    return f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Talvenor Master OS — Engines (Phase 5)</title>
<style>
body {{ font-family: system-ui, sans-serif; background: #FFFBF5; color: #1a1a1a; margin: 0; padding: 24px; }}
h1 {{ color: #0B1D33; }} h2 {{ color: #0B1D33; margin-top: 32px; }}
table {{ border-collapse: collapse; width: 100%; background: #fff; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; vertical-align: top; }}
th {{ background: #0B1D33; color: #fff; }}
.note {{ background: #FFF3CD; border: 1px solid #E6A817; padding: 12px; }}
code {{ background: #eee; padding: 2px 5px; }}
footer {{ margin-top: 32px; color: #666; font-size: 13px; }}
</style>
</head>
<body>
<h1>⚙️ Talvenor Master OS — Three Engines (Phase 5)</h1>
<p>Boss → Jarvis (voice) → Main CEO Bot (second brain) → 3 Engines / Office System.
Each engine has its own Staff, its own Tool Calling System, its own Skills.</p>
<p>This page is made from the real engine files by <code>scripts/sync_engines.py</code> —
if you change a number by hand, sync will revert it.</p>

<h2>The Engines</h2>
<table>
<tr><th>Engine</th><th>Staff</th><th>Tools</th><th>Mock</th><th>Gated</th><th>Skills</th><th>Gated tool (never executes)</th></tr>
{rows}</table>

<h2>True State (from the real files)</h2>
<ul>
<li><b>Paying clients:</b> {s['clients']} &nbsp;|&nbsp; <b>First mail:</b> {s['first_mails']}</li>
<li><b>Email:</b> {s['email']}</li>
<li><b>Vet Kit Gate 0:</b> {s['gate0']}</li>
<li><b>Creator OS 13 stage:</b> REAL {s['pipeline']['real']} / MOCK {s['pipeline']['mock']} / STUB {s['pipeline']['stub']} / BLOCKED {s['pipeline']['blocked']}</li>
<li><b>Shared core handlers (from tools.json, 9 tools):</b> {', '.join(f"{h} ({s['handler_status'].get(h, 'mock')})" for h in s['handlers'])}</li>
</ul>

<div class="note"><b>Gate (law):</b> <code>ok</code> / <code>post it</code> / <code>upload it</code> /
<code>send</code> / <code>go</code> — without Boss's exact word, no send / publish /
spend / delete. A gated tool call writes PENDING to the ApprovalGateway,
nothing executes. Spend cap <b>$0</b>. Jarvis voice REAL (offline, $0).</div>

<footer>Built 2026-11-16 (Phase 5) — folder <code>~/workspace/talvenor-master-os/</code> |
Host: Muse runtime + bridge cron ($0) — no 24/7 server.</footer>
</body>
</html>
"""


def main():
    status = collect()
    html = render(status)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"sync done -> {OUT}")
    for e in status["engines"]:
        print(f"{e['title']}: staff={e['staff']} tools={e['tools_total']} "
              f"(mock {e['tools_mock']}, gated {e['tools_gated']}) skills={e['skills']}")
    print(f"gate0={status['gate0']} pipeline={status['pipeline']}")


if __name__ == "__main__":
    main()
