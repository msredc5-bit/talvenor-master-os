#!/usr/bin/env python3
"""check_command_center.py — FOUNDER OS F2 batch 1 self-check.

What it checks:
  A. Data contract (static, from the generated files):
     1. dashboards/status.json has founder_os {phase F2, batch 1}
        and a roster with total == len(entries), draft+coded+unknown
        == total, with_activity <= total.
     2. Every roster skill_file and worker_file exists on disk.
     3. The roster draft count matches an INDEPENDENT recount
        (read registry.json, check each worker file for the
        [MOCK DRAFT] marker) — the audit's 53/69 is the cross-check.
     4. dashboards/ceo-report.json exists and is byte-identical to
        the file status.json ceo_report.path points to.
  B. No-fake-data (static, the pages themselves):
     5. command-center.html has all 5 batch-1 sections, fetches only
        status.json + ceo-report.json (no store/ read anywhere), and
        contains no hardcoded metric literal (162 / 163 / 39/100 /
        374 / standalone 69) outside CSS hex colours, and no
        metric-field number assignment in its script.
     6. dashboard-3d.html: the dated fallback snapshot is banner-
        labelled ("Last known snapshot, 2026-11-20"); the detail
        panel numbers are placeholders filled from the live status
        file — no hardcoded 162 / 39/100 / 374 outside the FALLBACK
        object; the Command Center link exists in the sidebar.
     7. run_local.bat mentions command-center.html.
  C. Approval server (in-process, TEMP store — the real store is
     never touched):
     8. GET /api/approvals returns the seeded pending records with
        allowed_gate_words + TTL, and the CORS header for the
        Command Center origin only.
     9. OPTIONS preflight on /api/approvals/decide -> 204 + CORS.
    10. POST decide approve with a WRONG gate word -> 400, record
        still pending; with the RIGHT word -> 200 APPROVED, pending
        list shrinks; deciding the same id again -> 400.
    11. POST decide reject (no gate word) -> 200 REJECTED.
    12. POST decide with a bad decision value / missing id /
        unknown id -> 400.
    13. Task endpoints still work (GET /api/tasks, POST /api/tasks
        -> 201) — no regression from the refactor.
    14. Real store/approvals.json + store/tasks.json untouched.

Stdlib only, no network beyond localhost, no send, no spend.
Exit 0 = PASS.
"""

import json
import os
import re
import sys
import tempfile
import threading
import urllib.error
import urllib.request
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
    check("status.json founder_os is F2 batch 1 (audit §14)",
          fo.get("phase") == "F2" and fo.get("batch") == 1,
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
    cc_ids = all(f'id="m{n}"' in cc for n in (1, 5, 6, 7, 11))
    check("command-center.html has all 5 batch-1 sections (m1/m5/m6/m7/m11)",
          cc_ids)
    fetches = re.findall(r'fetch\("([^"]+)"', cc)
    check("command-center.html fetches only status.json + ceo-report.json",
          set(fetches) == {"status.json", "ceo-report.json"},
          f"fetches={fetches}")
    check("command-center.html never reads a store file",
          "store/" not in cc)
    bad_literals = []
    for lit in ("162", "163", "39/100", "374"):
        if lit in cc_nostyle:
            bad_literals.append(lit)
    if re.search(r"(?<![0-9])69(?![0-9])", cc_nostyle):
        bad_literals.append("69")
    metric_assign = re.findall(
        r"(first_mails|paying_clients|pending_count|pa_list|total_usd)"
        r"\s*:\s*\d", cc)
    check("no-fake-data: no hardcoded metric literal in command-center.html",
          not bad_literals and not metric_assign,
          f"literals={bad_literals} metric_assign={metric_assign}")
    check("approval cards state no auto-approve / no always-allow",
          "no auto-approve" in cc and "no \"always allow\"" in cc
          and "Always allow" not in cc)

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

        # 13. Task endpoints still work (no regression).
        status_c, body, _h = _req("GET", "/api/tasks")
        tasks_ok = status_c == 200
        status_c, body, _h = _req("POST", "/api/tasks",
                                  {"title": "regression probe",
                                   "type": "research"})
        tasks_ok = tasks_ok and status_c == 201
        check("task endpoints still work (GET /api/tasks, POST -> 201)",
              tasks_ok, f"post_status={status_c}")
    except Exception as exc:  # noqa: BLE001
        for name in ("GET /api/approvals returns seeded pending + gate words + CORS",
                     "OPTIONS preflight on /api/approvals/decide -> 204 + CORS",
                     "approve with WRONG gate word -> 400, record still pending",
                     "approve with RIGHT gate word -> 200 approved, pending 2->1",
                     "deciding an already-decided id -> 400",
                     "reject without gate word -> 200 rejected, pending 0",
                     "bad decide bodies -> 400 (decision/id/unknown)",
                     "task endpoints still work (GET /api/tasks, POST -> 201)"):
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
