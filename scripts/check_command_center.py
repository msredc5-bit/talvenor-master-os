#!/usr/bin/env python3
"""check_command_center.py — FOUNDER OS F2 batch 2 self-check.

What it checks:
  A. Data contract (static, from the generated files):
     1. dashboards/status.json has founder_os {phase F2, batch 2}
        and a roster with total == len(entries), draft+coded+unknown
        == total, with_activity <= total.
     2. Every roster skill_file and worker_file exists on disk.
     3. The roster draft count matches an INDEPENDENT recount
        (read registry.json, check each worker file for the
        [MOCK DRAFT] marker) — the audit's 53/69 is the cross-check.
     4. dashboards/ceo-report.json exists and is byte-identical to
        the file status.json ceo_report.path points to.
  B. No-fake-data (static, the pages themselves):
     5. command-center.html has all 10 live sections (batch 1 +
        batch 2), fetches only status.json + ceo-report.json (no
        store/ read anywhere), taskboard calls only /api/tasks +
        /api/approvals (+ decide), and contains no hardcoded metric
        literal (162 / 163 / 39/100 / 374 / standalone 69 / the
        pricing literals / 524 / the overage rates) outside CSS hex
        colours, and no metric-field number assignment in its script.
     6. dashboard-3d.html: the dated fallback snapshot is banner-
        labelled ("Last known snapshot, 2026-11-20"); the detail
        panel numbers are placeholders filled from the live status
        file — no hardcoded 162 / 39/100 / 374 outside the FALLBACK
        object; the Command Center link exists in the sidebar.
     7. run_local.bat mentions command-center.html.
     8. Module 19 (Settings & Permissions) has no edit controls —
        no form/input/button/select in its section; module 17 has
        no purchase action (no button in its section).
  D. Batch 2 data contract (static, status.json vs its sources):
     9. task_queue: total == len(records), by_status sums to total,
        records match store/tasks.json field-for-field, queue_watch
        matches store/schedules.json, drain is the documented CLI.
    10. reports: total == files in reports/ceo/, each file exists
        with matching size, latest is the newest by generated_at,
        age_days recomputed; performance/leads are "none".
    11. finance: ledger totals recount from store/usage_ledger.json
        (64 records, $0.00, by-provider, by-kind, first/last);
        pricing tiers equal 00-CEO-Core/pricing.json; kit prices
        match kit-outline.md's Price line; wedge cross-checked
        against 02-Digital-Product-Department/README.md; revenue
        $0.00 with 0 paying clients.
    12. health: when dashboards/health-record.json exists, the
        suite/pytest totals in status.json equal it; otherwise both
        are "unknown". Python, disk, voice-model ONNX counts,
        provider enablement, check-script and test-file counts and
        brain all recount from their sources.
    13. policy: gate words / gated actions / spend cap match
        00-CEO-Core/config.json; TTL equals the gateway's own
        APPROVAL_TTL_MINUTES; production brain locked; the
        permission-matrix text is byte-identical to
        TALVENOR_PERMISSION_MATRIX.md and its row count recounts.
  C. Approval + task server (in-process, TEMP store — the real store
     is never touched):
    14. GET /api/approvals returns the seeded pending records with
        allowed_gate_words + TTL, and the CORS header for the
        Command Center origin only.
    15. OPTIONS preflight on /api/approvals/decide -> 204 + CORS.
    16. POST decide approve with a WRONG gate word -> 400, record
        still pending; with the RIGHT word -> 200 APPROVED, pending
        list shrinks; deciding the same id again -> 400.
    17. POST decide reject (no gate word) -> 200 REJECTED.
    18. POST decide with a bad decision value / missing id /
        unknown id -> 400.
    19. Task endpoints still work (GET /api/tasks, POST /api/tasks
        -> 201) — no regression from the refactor; GET /api/tasks
        returns the seeded record and the CORS header for the
        Command Center origin only.
    20. Real store/approvals.json + store/tasks.json untouched.
    21. Regression (2026-11-27 fix): the Voice card renders
        voice.label + voice.detail (not fmt(s.voice) on the voice
        object); the CEO Tasks breakdown renders nested objects
        (by_business / by_status / by_type) as small lists (not
        String(ceo.tasks[k])); and a node DOM-stub render harness
        executes the real page script with real data and proves
        "[object Object]" appears nowhere on the page.

Stdlib only, no network beyond localhost, no send, no spend.
Exit 0 = PASS.
"""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE, "scripts")
DASH = os.path.join(BASE, "dashboards")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _strip_style(text):
    return re.sub(r"<style>.*?</style>", "", text, flags=re.S)


def _snapshot(path):
    try:
        return _read(path)
    except OSError:
        return None


def main():
    real_appr_before = _snapshot(os.path.join(BASE, "store", "approvals.json"))
    real_tasks_before = _snapshot(os.path.join(BASE, "store", "tasks.json"))

    # ---------- A. Data contract ----------
    try:
        status = json.loads(_read(os.path.join(DASH, "status.json")))
    except (OSError, ValueError) as exc:
        status = None
        print(f"status.json unreadable: {exc}")
    fo = (status or {}).get("founder_os") or {}
    check("status.json founder_os is F2 batch 3 (audit §14)",
          fo.get("phase") == "F2" and fo.get("batch") == 3
          and "Command Center" in str(fo.get("label")),
          f"phase={fo.get('phase')} batch={fo.get('batch')}")

    roster = (status or {}).get("roster") or {}
    entries = roster.get("entries") or []
    counts_ok = (
        isinstance(roster.get("total"), int)
        and roster["total"] == len(entries)
        and isinstance(roster.get("draft"), int)
        and isinstance(roster.get("coded"), int)
        and roster["draft"] + roster["coded"]
        + sum(1 for e in entries if e.get("worker") == "unknown")
        == roster["total"]
        and isinstance(roster.get("with_activity"), int)
        and 0 <= roster["with_activity"] <= roster["total"])
    check("status.json roster counts are consistent",
          counts_ok,
          f"total={roster.get('total')} draft={roster.get('draft')} "
          f"coded={roster.get('coded')} "
          f"with_activity={roster.get('with_activity')}")

    missing = []
    bad_ts = []
    for e in entries:
        for key in ("skill_file", "worker_file"):
            p = e.get(key)
            if not isinstance(p, str) or p == "unknown" \
                    or not os.path.exists(os.path.join(BASE, p)):
                missing.append((e.get("role"), key, p))
        last = e.get("last_skill_load")
        if last != "unknown":
            if not isinstance(last, str) or "T" not in last:
                bad_ts.append((e.get("role"), last))
    check("every roster skill_file and worker_file exists on disk",
          not missing, f"missing={len(missing)}" +
          (f" e.g. {missing[:2]}" if missing else ""))
    check("roster last_skill_load is 'unknown' or an ISO timestamp",
          not bad_ts, f"bad={len(bad_ts)}")

    # Independent recount of the draft marker (audit cross-check).
    try:
        reg = json.loads(_read(os.path.join(
            BASE, "01-Agency-Department", "agents", "agent-registry",
            "registry.json")))
        recount_draft = 0
        for e in reg:
            wf = e.get("worker_file") or ""
            try:
                with open(os.path.join(BASE, wf), encoding="utf-8",
                          errors="ignore") as f:
                    if "MOCK DRAFT" in f.read(65536):
                        recount_draft += 1
            except OSError:
                pass
        check("roster draft count matches independent recount",
              recount_draft == roster.get("draft"),
              f"recount={recount_draft} roster={roster.get('draft')}")
    except (OSError, ValueError) as exc:
        check("roster draft count matches independent recount", False, str(exc))

    ceo = (status or {}).get("ceo_report") or {}
    ceo_out = os.path.join(DASH, "ceo-report.json")
    ceo_ok = False
    ceo_detail = ""
    if ceo.get("available") and isinstance(ceo.get("path"), str) \
            and ceo["path"].endswith(".json"):
        try:
            src = _read(os.path.join(BASE, ceo["path"]))
            out = _read(ceo_out)
            ceo_ok = (src == out)
            ceo_detail = f"source={ceo['path']} identical={ceo_ok}"
        except OSError as exc:
            ceo_detail = str(exc)
    else:
        ceo_detail = "no JSON CEO report available in status.json"
    check("dashboards/ceo-report.json is byte-identical to the CEO report",
          ceo_ok, ceo_detail)

    # ---------- B. No-fake-data ----------
    cc = _read(os.path.join(DASH, "command-center.html"))
    cc_nostyle = _strip_style(cc)
    cc_ids = all(f'id="m{n}"' in cc for n in
                 (1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18,
                  19))
    check("command-center.html has all 17 live sections "
          "(batch 1: m1/m5/m6/m7/m11; batch 2: m10/m15/m17/m18/m19; "
          "batch 3: m2/m3/m4/m12/m13/m14/m16)",
          cc_ids)
    nav = cc[cc.find('<nav id="sidebar">'):cc.find('</nav>')]
    live_nav = all(re.search(r'<a[^>]*class="nav-item[^"]*"[^>]*href="#m%d"' % n,
                             nav) for n in (2, 3, 4, 10, 12, 13, 14, 15, 16,
                                           17, 18, 19))
    check("batch-3 nav entries (m2 m3 m4 m12 m13 m14 m16) are LIVE links",
          live_nav)
    hrefs = re.findall(r'href="#m(\d+)"', nav)
    check("only F7/F8 (m8 m9) still greyed as planned",
          nav.count("planned") >= 2
          and not set(hrefs) & {"8", "9"},
          f"hrefs={hrefs}")
    fetches = re.findall(r'fetch\("([^"]+)"', cc)
    check("command-center.html fetches only status.json + ceo-report.json",
          set(fetches) == {"status.json", "ceo-report.json"},
          f"fetches={fetches}")
    check("command-center.html never reads a store file",
          "store/" not in cc)
    tb_calls = set(re.findall(r'TASKBOARD \+ "([^"]+)"', cc))
    check("taskboard fetch URLs are only /api/tasks, /api/approvals, "
          "/api/approvals/decide",
          tb_calls == {"/api/tasks", "/api/approvals",
                       "/api/approvals/decide"},
          f"calls={sorted(tb_calls)}")
    bad_literals = []
    for lit in ("162", "163", "39/100", "374"):
        if lit in cc_nostyle:
            bad_literals.append(lit)
    if re.search(r"(?<![0-9])69(?![0-9])", cc_nostyle):
        bad_literals.append("69")
    price_literals = [lit for lit in ("$547", "$1,109", "$1,672", "$597",
                                      "$1,297", "$1,997", "$49", "524",
                                      "2.19", "1.85", "1.67")
                      if lit in cc_nostyle]
    bad_literals.extend(price_literals)
    metric_assign = re.findall(
        r"(first_mails|paying_clients|pending_count|pa_list|total_usd)"
        r"\s*:\s*\d", cc)
    check("no-fake-data: no hardcoded metric literal in command-center.html",
          not bad_literals and not metric_assign,
          f"literals={bad_literals} metric_assign={metric_assign}")
    check("approval cards state no auto-approve / no always-allow",
          "no auto-approve" in cc and "no \"always allow\"" in cc
          and "Always allow" not in cc)
    check("regression (2026-11-27 fix): Voice card renders voice.label "
          "+ voice.detail, not fmt(s.voice)",
          'v: fmt(s.voice)' not in cc
          and "voice.label" in cc and "voice.detail" in cc)
    check("regression (2026-11-27 fix): CEO Tasks breakdown renders "
          "nested objects as lists, not String(ceo.tasks[k])",
          "String(ceo.tasks[k])" not in cc
          and 'sub + ": " + fmt(val[sub])' in cc)
    # Execute the real page script with real data under a DOM stub and
    # prove "[object Object]" appears nowhere (voice + CEO Tasks).
    node = shutil.which("node")
    render_js = os.path.join(SCRIPTS_DIR, "render_check_command_center.js")
    if node and os.path.exists(render_js):
        try:
            proc = subprocess.run([node, render_js], capture_output=True,
                                  text=True, timeout=60)
            last = (proc.stdout.strip().splitlines() or [""])[-1]
            check("render check (node DOM-stub): Voice + CEO Tasks + "
                  "batch-3 modules render with no '[object Object]'",
                  proc.returncode == 0, last)
        except (OSError, subprocess.SubprocessError) as exc:
            check("render check (node DOM-stub): Voice + CEO Tasks + "
                  "batch-3 modules render with no '[object Object]'",
                  False, f"harness error: {exc}")
    else:
        check("render check (node DOM-stub): Voice + CEO Tasks + "
              "batch-3 modules render with no '[object Object]'",
              False, "node or render_check_command_center.js missing")
    m19_start = cc.find('id="m19"')
    m19 = cc[m19_start:cc.find('</section>', m19_start)]
    m17 = cc[cc.find('id="m17"'):cc.find('id="m18"')]
    check("module 19 has no edit controls "
          "(no form/input/button/select/contenteditable)",
          "Read-only" in m19
          and not any(tag in m19 for tag in ("<form", "<input", "<button",
                                              "<select", "contenteditable")))
    check("module 17 has no purchase action (no button in its section)",
          "<button" not in m17)

    d3 = _read(os.path.join(DASH, "dashboard-3d.html"))
    check("3D dashboard fallback snapshot is banner-labelled",
          'id="snapshot-banner"' in d3
          and "Last known snapshot, 2026-11-20" in d3)
    d3_no_fb = _strip_style(re.sub(
        r"const FALLBACK = \{.*?\n\};", "", d3, flags=re.S))
    d3_bad = [lit for lit in ("162", "39/100", "374") if lit in d3_no_fb]
    check("3D dashboard: no hardcoded 162/39/100/374 outside FALLBACK",
          not d3_bad, f"found={d3_bad}")
    ph_ok = all(p in d3 for p in ("{first_mails}", "{pa_list}",
                                  "{approvals_pending}", "{paying_clients}",
                                  "{email}"))
    check("3D dashboard detail numbers are live placeholders",
          ph_ok)
    check("3D dashboard sidebar links to the Command Center",
          'href="command-center.html"' in d3)

    bat = _read(os.path.join(BASE, "run_local.bat"))
    check("run_local.bat mentions command-center.html",
          "command-center.html" in bat)

    # ---------- D. Batch 2 data contract ----------
    sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))
    from human_approval_gateway import APPROVAL_TTL_MINUTES  # noqa: PLC0415
    cfg = json.loads(_read(os.path.join(BASE, "00-CEO-Core", "config.json")))

    # 9. task_queue vs store/tasks.json + store/schedules.json.
    tq = (status or {}).get("task_queue") or {}
    try:
        tasks_store = json.loads(_read(os.path.join(BASE, "store", "tasks.json")))
    except (OSError, ValueError):
        tasks_store = {"records": []}
    store_recs = tasks_store.get("records", [])
    tq_recs = tq.get("records", [])
    by = tq.get("by_status") or {}
    by_sum = sum(v for k, v in by.items() if k != "total")
    tq_ok = (
        tq.get("total") == len(tq_recs) == len(store_recs)
        and by.get("total") == len(tq_recs)
        and by_sum == len(tq_recs)
        and all(
            all(s.get(k) == t.get(k) for k in
                ("id", "status", "business", "type", "title",
                 "queued_at", "completed_at"))
            for s, t in zip(tq_recs, store_recs)))
    check("task_queue total/by_status/records match store/tasks.json",
          tq_ok, f"total={tq.get('total')} records={len(tq_recs)}")
    try:
        sched_doc = json.loads(_read(os.path.join(BASE, "store",
                                                  "schedules.json")))
    except (OSError, ValueError):
        sched_doc = {}
    sched = sched_doc.get("records", []) \
        if isinstance(sched_doc, dict) else sched_doc
    watch_src = next((r for r in sched
                      if isinstance(r, dict)
                      and r.get("source") == "store/tasks.json"), {})
    w = tq.get("queue_watch") or {}
    check("task_queue queue_watch matches store/schedules.json",
          w.get("name") == watch_src.get("name")
          and w.get("status") == watch_src.get("status")
          and w.get("interval_minutes") == watch_src.get("interval_minutes")
          and w.get("runs") == watch_src.get("runs"),
          f"watch={w.get('name')} status={w.get('status')}")
    dr = tq.get("drain") or {}
    check("task_queue drain is the documented manual CLI",
          dr.get("method") == "manual CLI"
          and dr.get("command") ==
          "python scripts/run_office.py --drain-queue --max 2"
          and dr.get("runner") == "none attached",
          f"command={dr.get('command')}")

    # 10. reports vs reports/ceo/.
    rp = (status or {}).get("reports") or {}
    ceo_dir = os.path.join(BASE, "reports", "ceo")
    disk_files = sorted(os.listdir(ceo_dir)) if os.path.isdir(ceo_dir) else []

    def _gen(path):
        with open(path, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        try:
            val = json.loads(text).get("generated_at")
            if val:
                return val
        except ValueError:
            pass
        m = re.search(r"Generated:\s*(\S+)", text)
        return m.group(1) if m else None

    gen_map = {fn: _gen(os.path.join(ceo_dir, fn)) for fn in disk_files}
    newest = max(gen_map, key=lambda fn: gen_map.get(fn) or "") \
        if gen_map else None

    def _age_days(iso):
        try:
            dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - dt).days
        except (ValueError, TypeError):
            return None

    rp_files = rp.get("files") or []
    sizes_ok = all(
        os.path.getsize(os.path.join(ceo_dir, f["name"])) == f["size_bytes"]
        for f in rp_files)
    latest = rp.get("latest") or {}
    check("reports total/files/latest match reports/ceo/",
          rp.get("total") == len(disk_files) == len(rp_files)
          and sorted(f["name"] for f in rp_files) == disk_files
          and sizes_ok
          and latest.get("name") == newest
          and _age_days(latest.get("generated_at"))
          == latest.get("age_days"),
          f"total={rp.get('total')} disk={len(disk_files)} "
          f"latest={latest.get('name')}")
    check("performance and leads reports are 'none'",
          rp.get("performance") == "none" and rp.get("leads") == "none")

    # 11. finance vs usage ledger + pricing.json + kit-outline.md.
    fn = (status or {}).get("finance") or {}
    led = fn.get("ledger") or {}
    try:
        ledger = json.loads(_read(os.path.join(BASE, "store",
                                               "usage_ledger.json")))
    except (OSError, ValueError):
        ledger = {"records": []}
    lrecs = ledger.get("records", [])
    rec_by_prov, rec_by_kind, rec_total = {}, {}, 0.0
    for r in lrecs:
        rec_by_prov.setdefault(r.get("provider"), {"records": 0,
                                                   "cost_usd": 0.0})
        rec_by_prov[r["provider"]]["records"] += 1
        rec_by_prov[r["provider"]]["cost_usd"] += \
            float(r.get("cost_usd") or 0)
        rec_by_kind[r.get("kind")] = rec_by_kind.get(r.get("kind"), 0) + 1
        rec_total += float(r.get("cost_usd") or 0)
    led_ok = (
        led.get("records") == len(lrecs)
        and float(led.get("total_usd") or 0) == rec_total
        and led.get("by_provider") == rec_by_prov
        and led.get("by_kind") == rec_by_kind
        and led.get("first_at") ==
        (lrecs[0].get("at") if lrecs else None)
        and led.get("last_at") ==
        (lrecs[-1].get("at") if lrecs else None)
        and float(led.get("monthly_total_usd") or 0) == 0.0
        and float(led.get("monthly_cap_usd") or 0) == 0.0)
    check("finance ledger recounts from store/usage_ledger.json",
          led_ok, f"records={led.get('records')} total={led.get('total_usd')}")
    pricing = json.loads(_read(os.path.join(BASE, "00-CEO-Core",
                                            "pricing.json")))
    check("finance pricing equals 00-CEO-Core/pricing.json",
          fn.get("pricing") == pricing)
    kit_text = _read(os.path.join(BASE, "02-Digital-Product-Department",
                                  "kit-outline.md"))
    km = re.search(r"\*\*Price:\*\*\s*\$(\d+)\s+one-time\s*\(launch price "
                   r"\$(\d+) for the first 30 buyers", kit_text)
    g0 = fn.get("gate0") or {}
    kit_ok = bool(km) and g0.get("kit_price_usd") == int(km.group(1)) \
        and g0.get("kit_launch_price_usd") == int(km.group(2))
    check("finance gate0 kit prices match kit-outline.md Price line",
          kit_ok, f"kit={g0.get('kit_price_usd')} "
          f"launch={g0.get('kit_launch_price_usd')}")
    readme_dp = _read(os.path.join(BASE, "02-Digital-Product-Department",
                                   "README.md"))
    check("finance gate0 wedge cross-checked in Digital Product README",
          "1 of 20" in readme_dp and "$1,109" in readme_dp
          and "UNTESTED" in str(g0.get("wedge"))
          and "$1,109" in str(g0.get("wedge"))
          and g0.get("status") == "NOT PASSED" and g0.get("kit_sales") == 0,
          f"wedge={g0.get('wedge')}")
    rev = fn.get("revenue") or {}
    check("finance revenue is $0.00 with 0 paying clients",
          float(rev.get("revenue_usd") or 0) == 0.0
          and rev.get("paying_clients") == 0
          and rev.get("paying_clients") == (status or {}).get("paying_clients"))

    # 12. health vs its sources (health-record.json when present).
    hl = (status or {}).get("health") or {}
    rec_path = os.path.join(DASH, "health-record.json")
    if os.path.exists(rec_path):
        rec = json.loads(_read(rec_path))
        check("health suite/pytest equal dashboards/health-record.json",
              hl.get("suite") == rec.get("suite")
              and hl.get("pytest") == rec.get("pytest"),
              f"suite={hl.get('suite')} pytest={hl.get('pytest')}")
    else:
        check("health suite/pytest are 'unknown' without a record file",
              hl.get("suite") == "unknown" and hl.get("pytest") == "unknown")
    py_ok = hl.get("python") == sys.version.split()[0]
    du = shutil.disk_usage(BASE)
    disk = hl.get("disk") or {}
    disk_ok = (abs(float(disk.get("free_gb") or -1)
                   - du.free / (1024 ** 3)) <= 0.5
               and abs(float(disk.get("total_gb") or -1)
                       - du.total / (1024 ** 3)) <= 0.5)
    vm = hl.get("voice_models") or {}
    vm_ok = True
    vm_total = 0
    # The published total is the whole voice/ directory (models plus
    # the voice code), matching sync_status.py — not just models/.
    for root, _dirs, files in os.walk(os.path.join(BASE, "00-CEO-Core",
                                                   "voice")):
        for x in files:
            vm_total += os.path.getsize(os.path.join(root, x))
    for name in ("piper", "sherpa-bn", "vosk"):
        vdir = os.path.join(BASE, "00-CEO-Core", "voice", "models", name)
        present = os.path.isdir(vdir)
        onnx = 0
        for root, _dirs, files in os.walk(vdir):
            onnx += sum(1 for x in files if x.endswith(".onnx"))
        if vm.get(name, {}).get("present") is not present \
                or vm.get(name, {}).get("onnx_files") != onnx:
            vm_ok = False
    vm_ok = vm_ok and vm.get("total_size_mb") == \
        round(vm_total / (1024 ** 2), 1)
    prov = hl.get("providers") or {}
    prov_ok = all(prov.get(p, {}).get("enabled") == bool(
        (cfg.get("providers") or {}).get(p, {}).get("enabled"))
        for p in prov)
    check("health python/disk/voice-models/providers recount from sources",
          py_ok and disk_ok and vm_ok and prov_ok,
          f"python={hl.get('python')} disk_free={disk.get('free_gb')} "
          f"voice_ok={vm_ok} prov_ok={prov_ok}")
    cs = len(glob.glob(os.path.join(SCRIPTS_DIR, "check_*.py")))
    tf = len(glob.glob(os.path.join(BASE, "tests", "test_*.py")))
    check("health check-script and test-file counts recount",
          hl.get("check_scripts") == cs and hl.get("test_files") == tf,
          f"check_scripts={hl.get('check_scripts')} (disk {cs}) "
          f"test_files={hl.get('test_files')} (disk {tf})")
    check("health brain matches config brain",
          hl.get("brain") == cfg.get("brain"))

    # 13. policy vs config + gateway + permission matrix.
    pol = (status or {}).get("policy") or {}
    gates = cfg.get("gates") or {}
    prod = pol.get("production_brain") or {}
    pol_ok = (
        pol.get("gate_words") == gates.get("words")
        and pol.get("gated_actions") == gates.get("gated_actions")
        and pol.get("approval_ttl_minutes") == APPROVAL_TTL_MINUTES
        and float(pol.get("spend_cap_usd") or 0)
        == float(cfg.get("spend_cap_usd") or 0)
        and pol.get("brain") == cfg.get("brain")
        and prod.get("mode") == (cfg.get("production_brain") or {}).get("mode")
        and prod.get("unlocked") is False
        and pol.get("free_only_guard") is True
        and pol.get("email") == (status or {}).get("email"))
    check("policy gate words/actions/TTL/cap/brain match config + gateway",
          pol_ok, f"ttl={pol.get('approval_ttl_minutes')} "
          f"cap={pol.get('spend_cap_usd')}")
    matrix_text = _read(os.path.join(BASE, "TALVENOR_PERMISSION_MATRIX.md"))
    pm = pol.get("permission_matrix") or {}
    rows = [ln for ln in matrix_text.splitlines() if ln.startswith("| `")]
    check("policy permission matrix text is byte-identical to the file",
          pm.get("text") == matrix_text, f"len={len(pm.get('text', ''))}")
    check("policy permission matrix row count recounts (33 agent rows)",
          pm.get("agent_rows") == len(rows),
          f"rows={pm.get('agent_rows')} recount={len(rows)}")

    # ---------- E. Batch 3 data contract ----------
    # 14. chat vs config.json + the memory store.
    ch = (status or {}).get("chat") or {}
    mem_store = json.loads(_read(os.path.join(BASE, "store", "memory.json")))
    name_entry = next(
        (e for e in mem_store.get("entries", [])
         if e.get("area") == "about"
         and e.get("slug") == "assistant-name"), {})
    chat_ok = (
        ch.get("brain") == cfg.get("brain")
        and ch.get("brain_chain")
        == (cfg.get("development_brain") or {}).get("fallback_chain")
        and isinstance(ch.get("assistant"), str)
        and ch["assistant"] in str(name_entry.get("text", ""))
        and ch.get("connected") is False
        and ch.get("transcript") == "none"
        and isinstance(ch.get("send"), dict)
        and ch["send"].get("enabled") is False
        and isinstance(ch["send"].get("reason"), str)
        and len(ch["send"]["reason"]) > 20
        and "Muse chat" in str(ch.get("surface")))
    check("chat brain/chain/assistant match config + memory store; "
          "send disabled, transcript none",
          chat_ok, f"brain={ch.get('brain')} assistant={ch.get('assistant')}")

    # 15. voice_command vs voice/loop.py.
    vc = (status or {}).get("voice_command") or {}
    loop_path = os.path.join(BASE, "00-CEO-Core", "voice", "loop.py")
    loop_text = _read(loop_path) if os.path.exists(loop_path) else ""
    gp = vc.get("gate_phrases") or {}
    vc_ok = (
        vc.get("loop_exists") is True
        and vc.get("loop_file") == "00-CEO-Core/voice/loop.py"
        and vc.get("brain") == "mock"
        and vc.get("live_in_browser") is False
        and vc.get("bengali_prompts") == "regressed"
        and all(phrase in loop_text for phrase in gp)
        and all(v in ("send", "publish") for v in gp.values())
        and isinstance(vc.get("engines"), str)
        and vc["engines"] == (status or {}).get("voice", {}).get("detail")
        and "PC-side Python process" in str(vc.get("reason")))
    check("voice_command loop/gate phrases/engines match voice/loop.py; "
          "mic not live in browser",
          vc_ok, f"gate_phrases={sorted(gp)}")

    # 16. personas vs 00-CEO-Core/personas.json.
    ps = (status or {}).get("personas") or {}
    personas_file = json.loads(_read(os.path.join(
        BASE, "00-CEO-Core", "personas.json")))
    src_ok = all(
        isinstance(p.get("source"), str)
        and os.path.exists(os.path.join(BASE, p["source"]))
        for p in ps.get("profiles", []))
    check("personas profiles equal personas.json; default mira; "
          "every profile source file exists",
          ps.get("profiles") == personas_file.get("profiles")
          and ps.get("default") == personas_file.get("default") == "mira"
          and len(ps.get("profiles", [])) == 3 and src_ok,
          f"profiles={len(ps.get('profiles', []))} "
          f"default={ps.get('default')}")

    # 17. execution vs logs/skill_executions.jsonl,
    # logs/dev_brain_calls.jsonl, task_queue. The skill log is an
    # append-only stream that grows while other work runs, so the
    # published values are a SNAPSHOT: they must be genuine log data
    # (a contiguous run of real records, in order), not necessarily
    # equal to the live tail at check time. Counts may only grow
    # since the snapshot; the first timestamp must be a real log
    # timestamp; the dev-brain calls must be a prefix of the log.
    # Replicates the reader's record shape exactly (result_file =
    # basename of "result"; tokens from usage.total_tokens).
    ex = (status or {}).get("execution") or {}
    se = ex.get("skill_executions") or {}
    dc = ex.get("dev_brain_calls") or {}
    skill_lines = _read(os.path.join(BASE, "logs",
                                     "skill_executions.jsonl")).splitlines()
    parsed_recs = []
    skill_errs = 0
    first_ts = None
    last_ts = None
    for ln in skill_lines:
        if not ln.strip():
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        ts = ev.get("timestamp")
        if not isinstance(ts, str):
            continue
        result = ev.get("result")
        parsed_recs.append({
            "timestamp": ts,
            "event": ev.get("event", "unknown"),
            "skill": ev.get("skill", "unknown"),
            "result_file": (result.split("/")[-1]
                            if isinstance(result, str) else "unknown"),
            "error": ev.get("error"),
        })
        if first_ts is None or ts < first_ts:
            first_ts = ts
        if last_ts is None or ts > last_ts:
            last_ts = ts
        if ev.get("error") is not None:
            skill_errs += 1
    published_recent = se.get("recent") or []
    run_found = False
    if published_recent:
        for start in range(0, len(parsed_recs) - len(published_recent) + 1):
            if parsed_recs[start:start + len(published_recent)] \
                    == published_recent:
                run_found = True
                break
    call_lines = _read(os.path.join(BASE, "logs",
                                    "dev_brain_calls.jsonl")).splitlines()
    want_calls = []
    for ln in call_lines:
        if not ln.strip():
            continue
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(rec, dict):
            continue
        usage = rec.get("usage")
        want_calls.append({
            "provider": rec.get("provider", "unknown"),
            "model": rec.get("model", "unknown"),
            "status": rec.get("status", "unknown"),
            "error": rec.get("error"),
            "total_tokens": (usage.get("total_tokens", "unknown")
                             if isinstance(usage, dict) else "unknown"),
            "ts": rec.get("ts", "unknown"),
        })
    tq2 = (status or {}).get("task_queue") or {}
    tk = ex.get("tasks") or {}
    br = ex.get("bridge") or {}
    ex_ok = (
        0 < se.get("total_lines", 0) <= len(skill_lines)
        and 0 < se.get("parsed", 0) <= len(parsed_recs)
        and 0 <= se.get("errors", -1) <= skill_errs
        and any(r["timestamp"] == se.get("first_at")
                for r in parsed_recs)
        and se.get("last_at") is not None
        and any(r["timestamp"] == se.get("last_at")
                for r in parsed_recs)
        and se.get("last_at") <= (last_ts or "")
        and 0 < len(published_recent) <= 8
        and run_found
        and published_recent[-1].get("timestamp") == se.get("last_at")
        and 0 <= dc.get("total", -1) <= len(want_calls)
        and dc.get("records") == want_calls[:len(dc.get("records", []))]
        and tk.get("total") == tq2.get("total")
        and tk.get("done") == (tq2.get("by_status") or {}).get("done", 0)
        and br.get("name") == "master-os-3d-bridge"
        and br.get("state") == "unknown"
        and ex.get("stream") == "none"
        and "No live stream" in str(ex.get("stream_note")))
    check("execution skill log / dev brain calls / tasks / bridge "
          "recount from logs + task_queue",
          ex_ok, f"skill_lines={se.get('total_lines')} "
          f"errors={se.get('errors')} calls={dc.get('total')}")

    # 18. memory vs store/memory.json (READ-ONLY: metadata only,
    # never quote text).
    mm = (status or {}).get("memory") or {}
    store_entries = mem_store.get("entries", [])
    per_box = {}
    for e in store_entries:
        per_box[e.get("box")] = per_box.get(e.get("box"), 0) + 1
    meta_ok = all(
        mm.get("entries_meta", [])[i].get(k) == store_entries[i].get(k)
        for i in range(len(store_entries))
        for k in ("area", "slug", "box", "status", "learned_at",
                  "updated_at"))
    mem_ok = (
        mm.get("entries") == len(store_entries)
        and len(mm.get("entries_meta", [])) == len(store_entries)
        and meta_ok
        and mm.get("boxes") == mem_store.get("boxes")
        and mm.get("per_box") == per_box
        and mm.get("verbatim_quotes")
        == sum(1 for e in store_entries if e.get("quote"))
        and mm.get("store_file") == "store/memory.json"
        and mm.get("schema") == mem_store.get("schema"))
    check("memory entries/boxes/per_box/verbatim-quote count match "
          "store/memory.json (metadata only)",
          mem_ok, f"entries={mm.get('entries')} "
          f"boxes={len(mm.get('boxes', []))}")
    check("memory verbatim quotes are NOT in command-center.html",
          "Your name is Mira" not in cc
          and "তুমি এখন থেকে বাংলায় কথা বলবা" not in cc)

    # 19. library vs disk (docs/, top-level, 00-CEO-Core/,
    # unified-business-os/).
    lb = (status or {}).get("library") or {}
    lib_ok = True
    lib_detail = ""
    groups = {
        "docs": os.path.join(BASE, "docs"),
        "top_level": BASE,
        "ceo_core": os.path.join(BASE, "00-CEO-Core"),
        "unified_business_os": os.path.join(BASE, "..",
                                            "unified-business-os"),
    }
    for key, dpath in groups.items():
        listed = lb.get(key)
        if not isinstance(listed, list):
            lib_ok = False
            lib_detail = f"{key}: not a list"
            break
        # _list_md_files lists only top-level *.md files.
        disk = sorted(f for f in os.listdir(dpath)
                      if f.endswith(".md")
                      and os.path.isfile(os.path.join(dpath, f)))
        if sorted(f["name"] for f in listed) != disk:
            lib_ok = False
            lib_detail = f"{key}: listed {len(listed)} disk {len(disk)}"
            break
        for f in listed:
            fp = os.path.join(dpath, f["name"])
            if os.path.getsize(fp) != f.get("size_bytes"):
                lib_ok = False
                lib_detail = f"{key}/{f['name']}: size mismatch"
                break
            try:
                datetime.fromisoformat(str(f.get("modified_at")))
            except (ValueError, TypeError):
                lib_ok = False
                lib_detail = f"{key}/{f['name']}: bad modified_at"
                break
        if not lib_ok:
            break
    ceo_reports = (lb.get("ceo_reports") or {})
    lib_ok = lib_ok and ceo_reports.get("total") == len(disk_files) \
        and ceo_reports.get("note") == "File list in module 15 " \
        "(Reports Center)."
    check("library file lists/sizes match disk (docs, top-level, "
          "00-CEO-Core, unified-business-os)",
          lib_ok, lib_detail or f"groups={len(groups)}")

    # 20. integrations vs sources (n8n MCP record, workflow files,
    # config providers).
    ig = (status or {}).get("integrations") or {}
    mcp = ig.get("n8n_mcp") or {}
    wf = ig.get("n8n_workflows") or []
    tier2_path = os.path.join(BASE, "..", "talvenor-outreach",
                              "n8n-workflow-tier2-auto-send.json")
    cb_path = os.path.join(BASE, "..", "talvenor-callback",
                           "n8n-workflow-talvenor-callback.json")
    tier2 = json.loads(_read(tier2_path)) if os.path.exists(tier2_path) \
        else {}
    cbw = json.loads(_read(cb_path)) if os.path.exists(cb_path) else {}
    wf_ok = (
        len(wf) == 2
        and wf[0].get("name") == tier2.get("name")
        and wf[0].get("nodes") == len(tier2.get("nodes", [])) == 8
        and wf[0].get("status") == "NOT LIVE"
        and wf[1].get("name") == cbw.get("name")
        and wf[1].get("nodes") == len(cbw.get("nodes", [])) == 3
        and wf[1].get("status") == "NOT LIVE")
    prov = ig.get("providers") or {}
    ig_ok = (
        mcp.get("service") == "n8n Cloud MCP"
        and mcp.get("instance") == "talvenorai.app.n8n.cloud"
        and mcp.get("state") == "connected"
        and mcp.get("tools") == 75 and mcp.get("workflows") == 0
        and mcp.get("allowed_read_only") == 41
        and mcp.get("write_blocked") == 34
        and mcp.get("rest_api") == "blocked on free trial (404)"
        and mcp.get("verified") == "2026-11-25"
        and (ig.get("n8n_adapter") or {}).get("state") == "not connected"
        and wf_ok
        and (prov.get("meta") or {}).get("state")
        == "unreachable from this VM"
        and (prov.get("ollama") or {}).get("state") \
        == "local — not present in this VM"
        and (ig.get("vapi") or {}).get("state") == "unknown"
        and (ig.get("gmail_calendar") or {}).get("state") == "unknown")
    check("integrations n8n MCP record + workflow node counts + "
          "provider states match sources",
          ig_ok, f"mcp_tools={mcp.get('tools')} wf={len(wf)}")

    # 21. Honesty in the page itself: disabled controls, display-only
    # labels, no fake chat.
    m2 = cc[cc.find('id="m2"'):cc.find('id="m3"')]
    m3 = cc[cc.find('id="m3"'):cc.find('id="m4"')]
    m4 = cc[cc.find('id="m4"'):cc.find('id="m12"')]
    honesty_ok = (
        'id="chat-input"' in m2 and 'disabled' in m2
        and "SHELL" in m2 and "not a live chat" in m2
        and "no fake replies" in m2
        and 'id="voice-mic"' in m3 and 'disabled' in m3
        and "SHELL" in m3 and "the mic is off" in m3
        and "DISPLAY ONLY" in m4
        and "the underlying brain does not switch" in m4)
    check("batch-3 honesty: chat send + voice mic disabled in the page; "
          "personas labelled display-only",
          honesty_ok)

    # 22. No "[object Object]" literal in any data file (lesson from
    # the 2026-11-27 fix).
    data_files = [os.path.join(DASH, "status.json"),
                  os.path.join(DASH, "ceo-report.json"),
                  os.path.join(DASH, "health-record.json"),
                  os.path.join(BASE, "00-CEO-Core", "personas.json")]
    bad_data = [p for p in data_files
                if os.path.exists(p) and "[object Object]" in _read(p)]
    check("no '[object Object]' literal in any data file",
          not bad_data, f"bad={bad_data}")

    # ---------- C. Approval server (TEMP store) ----------
    tmp_dir = tempfile.mkdtemp()
    tmp_appr = os.path.join(tmp_dir, "approvals.json")
    tmp_tasks = os.path.join(tmp_dir, "tasks.json")
    tmp_status = os.path.join(tmp_dir, "status.json")
    with open(tmp_tasks, "w", encoding="utf-8") as f:
        json.dump({"schema": "tasks-v1", "records": []}, f)
    with open(tmp_status, "w", encoding="utf-8") as f:
        json.dump({"phase": 11}, f)
    os.environ["TALVENOR_TASKBOARD_TASKS"] = tmp_tasks
    os.environ["TALVENOR_TASKBOARD_STATUS"] = tmp_status
    os.environ["TALVENOR_TASKBOARD_PAGE"] = os.path.join(
        DASH, "taskboard.html")
    os.environ["TALVENOR_TASKBOARD_APPROVALS"] = tmp_appr
    sys.path.insert(0, SCRIPTS_DIR)
    sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))
    import taskboard_server  # noqa: PLC0415
    from approval_centre import ApprovalCentre  # noqa: PLC0415

    centre = ApprovalCentre(approvals_path=tmp_appr)
    rec1 = centre.request_approval("send", "test approval one", "Boss")
    rec2 = centre.request_approval("publish", "test approval two", "Boss")

    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 taskboard_server.TaskboardHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    def _req(method, path, body=None, raw=None, headers=None):
        data = raw if raw is not None else (
            json.dumps(body).encode("utf-8") if body is not None else None)
        req = urllib.request.Request(base_url + path, data=data,
                                     method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return (resp.status, resp.read().decode("utf-8"),
                        dict(resp.headers))
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8"), dict(exc.headers)

    try:
        # 8. GET /api/approvals + CORS header.
        status_c, body, hdrs = _req("GET", "/api/approvals")
        data = json.loads(body) if status_c == 200 else {}
        pend = data.get("pending", [])
        cors_ok = hdrs.get("Access-Control-Allow-Origin") == \
            "http://localhost:8765"
        ok8 = (status_c == 200 and len(pend) == 2
               and all("allowed_gate_words" in r for r in pend)
               and all("expires_in_minutes" in r for r in pend)
               and cors_ok)
        check("GET /api/approvals returns seeded pending + gate words + CORS",
              ok8, f"status={status_c} pending={len(pend)} cors={cors_ok}")

        # 9. OPTIONS preflight.
        status_c, _b, hdrs = _req("OPTIONS", "/api/approvals/decide",
                                  headers={"Origin": "http://localhost:8765",
                                           "Access-Control-Request-Method":
                                           "POST"})
        check("OPTIONS preflight on /api/approvals/decide -> 204 + CORS",
              status_c == 204 and hdrs.get("Access-Control-Allow-Origin")
              == "http://localhost:8765", f"status={status_c}")

        # 10. Wrong gate word -> 400, still pending.
        status_c, body, _h = _req("POST", "/api/approvals/decide",
                                  {"id": rec1["id"], "decision": "approve",
                                   "gate_word": "post it"})
        wrong_ok = status_c == 400
        _s, body2, _h = _req("GET", "/api/approvals")
        still = [r for r in json.loads(body2).get("pending", [])
                 if r["id"] == rec1["id"]]
        check("approve with WRONG gate word -> 400, record still pending",
              wrong_ok and len(still) == 1, f"status={status_c}")

        # 10b. Right gate word -> 200 APPROVED, pending shrinks.
        status_c, body, _h = _req("POST", "/api/approvals/decide",
                                  {"id": rec1["id"], "decision": "approve",
                                   "gate_word": "send"})
        decided = json.loads(body) if status_c == 200 else {}
        ok10b = (status_c == 200
                 and decided.get("record", {}).get("status") == "approved"
                 and len(decided.get("pending", [])) == 1)
        check("approve with RIGHT gate word -> 200 approved, pending 2->1",
              ok10b, f"status={status_c} "
              f"record={decided.get('record', {}).get('status')}")

        # 10c. Deciding the same id again -> 400.
        status_c, _b, _h = _req("POST", "/api/approvals/decide",
                                {"id": rec1["id"], "decision": "approve",
                                 "gate_word": "send"})
        check("deciding an already-decided id -> 400",
              status_c == 400, f"status={status_c}")

        # 11. Reject without gate word -> 200 REJECTED, pending 0.
        status_c, body, _h = _req("POST", "/api/approvals/decide",
                                  {"id": rec2["id"], "decision": "reject"})
        decided = json.loads(body) if status_c == 200 else {}
        ok11 = (status_c == 200
                and decided.get("record", {}).get("status") == "rejected"
                and len(decided.get("pending", [])) == 0)
        check("reject without gate word -> 200 rejected, pending 0",
              ok11, f"status={status_c}")

        # 12. Bad decision / missing id / unknown id -> 400.
        bad_ok = True
        for payload in ({"id": rec2["id"], "decision": "maybe"},
                        {"decision": "approve", "gate_word": "send"},
                        {"id": "no-such-id", "decision": "reject"}):
            status_c, _b, _h = _req("POST", "/api/approvals/decide", payload)
            if status_c != 400:
                bad_ok = False
                print(f"  bad decide case {payload} -> {status_c} (want 400)")
        check("bad decide bodies -> 400 (decision/id/unknown)",
              bad_ok)

        # 13. Task endpoints still work (no regression): seed one
        # task, then GET returns it with the CORS header for the
        # Command Center origin only.
        status_c, body, _h = _req("POST", "/api/tasks",
                                  {"title": "regression probe",
                                   "type": "research"})
        tasks_ok = status_c == 201
        status_c, body, hdrs = _req("GET", "/api/tasks")
        data = json.loads(body) if status_c == 200 else {}
        recs = data.get("records", [])
        tasks_ok = (tasks_ok and status_c == 200
                    and len(recs) == 1
                    and recs[0].get("title") == "regression probe"
                    and recs[0].get("status") == "queued"
                    and hdrs.get("Access-Control-Allow-Origin")
                    == "http://localhost:8765")
        check("task endpoints: POST -> 201, GET returns the record + CORS",
              tasks_ok, f"get_status={status_c} records={len(recs)}")
    except Exception as exc:  # noqa: BLE001
        for name in ("GET /api/approvals returns seeded pending + gate words + CORS",
                     "OPTIONS preflight on /api/approvals/decide -> 204 + CORS",
                     "approve with WRONG gate word -> 400, record still pending",
                     "approve with RIGHT gate word -> 200 approved, pending 2->1",
                     "deciding an already-decided id -> 400",
                     "reject without gate word -> 200 rejected, pending 0",
                     "bad decide bodies -> 400 (decision/id/unknown)",
                     "task endpoints: POST -> 201, GET returns the record + CORS"):
            if not any(r[0] == name for r in results):
                check(name, False, f"{type(exc).__name__}: {exc}")
    finally:
        server.shutdown()
        server.server_close()

    # 14. Real stores untouched.
    check("real store/approvals.json untouched by this check run",
          _snapshot(os.path.join(BASE, "store", "approvals.json"))
          == real_appr_before)
    check("real store/tasks.json untouched by this check run",
          _snapshot(os.path.join(BASE, "store", "tasks.json"))
          == real_tasks_before)

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_command_center: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
