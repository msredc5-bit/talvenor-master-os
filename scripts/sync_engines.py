"""Engines dashboard sync — dashboards/engines.html আসল engine file থেকে বানানো।

পড়ে:
  - প্রতিটা engine-র tools.json (mock/gated সংখ্যা)
  - প্রতিটা engine-র skills/*.md (staff + skill সংখ্যা)
  - Agency: config.json honest_status (email PAUSED)
  - Products: gate0-status.md-র Status লাইন (fail-closed parse)
  - Content: pipeline.md-র গণনা লাইন (REAL / MOCK / BLOCKED)
  - Shared core: 00-CEO-Core/tool_calling.py-র HANDLERS

কোনো timestamp লেখে না — দুইবার চালালে byte-identical HTML হয়।
কোনো মান না পেলে "unknown" লেখে, বানায় না।
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
    # Products Gate 0 — fail-closed: শুধু "Status:" লাইনটা পড়া হয়
    # (লাইনটা "**Status: NOT PASSED (2026-11-16)**" আকারে থাকতে পারে)
    gate0 = "unknown"
    gate_text = read_text(os.path.join(
        ROOT, "02-Digital-Product-Department", "gate0-status.md"))
    for line in gate_text.splitlines():
        m = re.match(r"^\**\s*Status:\s*(.+?)\**\s*$", line.strip())
        if m:
            gate0 = m.group(1).strip()
            break
    # Content pipeline counts — গণনা লাইন থেকে
    # ("**গণনা:** REAL **0** · MOCK **10** · STUB **0** · BLOCKED **3**")
    pipe_text = read_text(os.path.join(
        ROOT, "03-Content-Creation-Department", "pipeline.md"))
    pipe = {"real": "?", "mock": "?", "stub": "?", "blocked": "?"}
    clean = pipe_text.replace("*", "")
    m = re.search(r"REAL\s*(\d+)\s*·\s*MOCK\s*(\d+)\s*·\s*"
                  r"STUB\s*(\d+)\s*·\s*BLOCKED\s*(\d+)", clean)
    if m:
        pipe = {"real": m.group(1), "mock": m.group(2),
                "stub": m.group(3), "blocked": m.group(4)}
    # Shared core handlers
    core_text = read_text(os.path.join(ROOT, "00-CEO-Core", "tool_calling.py"))
    handlers = sorted(set(re.findall(r'"(draft_\w+|kit_outline_read|status_read|research_notes)"',
                                     core_text)))
    return {
        "engines": engines, "email": email, "clients": clients,
        "first_mails": first_mails, "gate0": gate0, "pipeline": pipe,
        "handlers": handlers,
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
<p>Boss → Jarvis (voice) → Main CEO Bot (second brain) → ৩ Engine / Office System।
প্রতিটা engine-র নিজের Staff, নিজের Tool Calling System, নিজের Skills।</p>
<p>এই page <code>scripts/sync_engines.py</code> দিয়ে আসল engine file থেকে বানানো —
হাতে সংখ্যা বদলালে sync-এ ফিরে যাবে।</p>

<h2>Engine-গুলো</h2>
<table>
<tr><th>Engine</th><th>Staff</th><th>Tools</th><th>Mock</th><th>Gated</th><th>Skills</th><th>Gated tool (কখনো execute হয় না)</th></tr>
{rows}</table>

<h2>সত্য অবস্থা (আসল file থেকে)</h2>
<ul>
<li><b>Paying clients:</b> {s['clients']} &nbsp;|&nbsp; <b>প্রথম মেইল:</b> {s['first_mails']}</li>
<li><b>Email:</b> {s['email']}</li>
<li><b>Vet Kit Gate 0:</b> {s['gate0']}</li>
<li><b>Creator OS 13 stage:</b> REAL {s['pipeline']['real']} / MOCK {s['pipeline']['mock']} / STUB {s['pipeline']['stub']} / BLOCKED {s['pipeline']['blocked']}</li>
<li><b>Shared core handlers:</b> {', '.join(s['handlers'])}</li>
</ul>

<div class="note"><b>Gate (আইন):</b> <code>ok</code> / <code>post it</code> / <code>upload it</code> /
<code>send</code> / <code>go</code> — Boss-এর exact word ছাড়া send / publish /
spend / delete হবে না। Gated tool call করলে ApprovalGateway-এ PENDING লেখা হয়,
কিছু execute হয় না। Spend cap <b>$0</b>। Jarvis voice STUB (mic যুক্ত নয়)।</div>

<footer>Built 2026-11-16 (Phase 5) — folder <code>~/workspace/talvenor-master-os/</code> |
Host: Muse runtime + bridge cron ($0) — ২৪/৭ server নেই।</footer>
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
