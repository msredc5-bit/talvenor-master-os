"""FOUNDER OS F2 batch 2 — Command Center tests (2026-11-27).

Real code under test (stdlib only, temp stores for the server,
read-only for the generated dashboard files — no network beyond
localhost, no live LLM calls, no send/publish/spend/delete/deploy,
$0):

  * scripts/taskboard_server.py — GET /api/approvals and
    POST /api/approvals/decide, both straight through the REAL
    approval gateway (ApprovalCentre). The gateway's own errors
    (wrong gate word, expired, already decided, unknown id) must
    surface as HTTP 400, never 500, never swallowed. Also
    GET /api/tasks (the Task Center live refresh).
  * dashboards/command-center.html — no-fake-data: the page fetches
    only status.json + ceo-report.json, never a store file, and
    contains no hardcoded metric literal (batch 1 + batch 2 sets).
    Module 19 has no edit controls; module 17 has no purchase
    action.
  * dashboards/status.json (generated) — founder_os F2 batch 2,
    roster counts consistent, draft count matches an independent
    recount of the [MOCK DRAFT] marker; batch-2 keys internally
    consistent and cross-checked against their NON-store sources
    (pricing.json, kit-outline.md, the Digital Product README,
    TALVENOR_PERMISSION_MATRIX.md, config.json, reports/ceo/,
    dashboards/health-record.json when present, the voice models
    directory). The store cross-checks (tasks.json, usage_ledger
    .json, schedules.json) live in scripts/check_command_center.py
    — this file never reads the real store/ (conftest rule).
  * dashboards/ceo-report.json — byte-identical to the CEO report
    status.json points to.
  * dashboards/dashboard-3d.html — the dated fallback snapshot is
    banner-labelled; detail numbers are live placeholders.
"""
import glob
import json
import os
import re
import shutil
import sys
import threading
import urllib.error
import urllib.request
from datetime import datetime, timezone
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import taskboard_server
from approval_centre import ApprovalCentre
from human_approval_gateway import APPROVAL_TTL_MINUTES

REPO_ROOT = Path(__file__).resolve().parents[1]
DASH = REPO_ROOT / "dashboards"


def _read(path):
    return Path(path).read_text(encoding="utf-8")


def _load_status():
    return json.loads(_read(DASH / "status.json"))


# ---------------------------------------------------------------- server
@pytest.fixture()
def approvals_server(tmp_path, monkeypatch):
    """Taskboard server on an ephemeral port, TEMP store only.

    The server module reads its paths once at import time, so the
    fixture patches the module attributes (not env vars) — each test
    gets its own temp store, and the real store/ is never touched.
    """
    tmp_appr = tmp_path / "approvals.json"
    tmp_tasks = tmp_path / "tasks.json"
    tmp_status = tmp_path / "status.json"
    tmp_tasks.write_text(json.dumps({"schema": "tasks-v1", "records": []}),
                         encoding="utf-8")
    tmp_status.write_text(json.dumps({"phase": 11}), encoding="utf-8")
    monkeypatch.setattr(taskboard_server, "APPROVALS_PATH", str(tmp_appr))
    monkeypatch.setattr(taskboard_server, "TASKS_PATH", str(tmp_tasks))
    monkeypatch.setattr(taskboard_server, "STATUS_PATH", str(tmp_status))
    monkeypatch.setattr(taskboard_server, "BOARDPAGE_PATH",
                        str(DASH / "taskboard.html"))

    centre = ApprovalCentre(approvals_path=str(tmp_appr))
    rec_send = centre.request_approval("send", "test approval one", "Boss")
    rec_pub = centre.request_approval("publish", "test approval two", "Boss")
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 taskboard_server.TaskboardHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    yield base, rec_send, rec_pub
    server.shutdown()
    server.server_close()


def _req(base, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode("utf-8"), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8"), dict(exc.headers)


def test_approvals_list_returns_seeded_pending(approvals_server):
    base, _rec1, _rec2 = approvals_server
    status, body, headers = _req(base, "GET", "/api/approvals")
    assert status == 200
    pending = json.loads(body)["pending"]
    assert len(pending) == 2
    assert all("allowed_gate_words" in r for r in pending)
    assert all("expires_in_minutes" in r for r in pending)
    assert headers.get("Access-Control-Allow-Origin") == \
        "http://localhost:8765"


def test_approve_wrong_gate_word_is_400_and_still_pending(approvals_server):
    base, rec1, _rec2 = approvals_server
    status, _b, _h = _req(base, "POST", "/api/approvals/decide",
                          {"id": rec1["id"], "decision": "approve",
                           "gate_word": "post it"})
    assert status == 400
    _s, body, _h = _req(base, "GET", "/api/approvals")
    assert any(r["id"] == rec1["id"]
               for r in json.loads(body)["pending"])


def test_approve_right_gate_word_decides(approvals_server):
    base, rec1, _rec2 = approvals_server
    status, body, _h = _req(base, "POST", "/api/approvals/decide",
                            {"id": rec1["id"], "decision": "approve",
                             "gate_word": "send"})
    assert status == 200
    data = json.loads(body)
    assert data["record"]["status"] == "approved"
    assert len(data["pending"]) == 1
    # Deciding the same id again is a client error, not a crash.
    status, _b, _h = _req(base, "POST", "/api/approvals/decide",
                          {"id": rec1["id"], "decision": "approve",
                           "gate_word": "send"})
    assert status == 400


def test_reject_needs_no_gate_word(approvals_server):
    base, rec1, rec2 = approvals_server
    status, body, _h = _req(base, "POST", "/api/approvals/decide",
                            {"id": rec2["id"], "decision": "reject"})
    assert status == 200
    data = json.loads(body)
    assert data["record"]["status"] == "rejected"
    # The other seeded approval is still pending.
    assert [r["id"] for r in data["pending"]] == [rec1["id"]]


def test_decide_unknown_id_is_400_not_500(approvals_server):
    base, _rec1, _rec2 = approvals_server
    status, _b, _h = _req(base, "POST", "/api/approvals/decide",
                          {"id": "no-such-id", "decision": "reject"})
    assert status == 400


def test_decide_bad_bodies_are_400(approvals_server):
    base, _rec1, rec2 = approvals_server
    for payload in ({"id": rec2["id"], "decision": "maybe"},
                    {"decision": "approve", "gate_word": "send"},
                    {"id": rec2["id"], "decision": "approve"}):
        status, _b, _h = _req(base, "POST", "/api/approvals/decide", payload)
        assert status == 400


def test_tasks_api_returns_record_and_cors(approvals_server):
    base, _rec1, _rec2 = approvals_server
    status, body, _h = _req(base, "POST", "/api/tasks",
                            {"title": "pytest probe", "type": "research"})
    assert status == 201
    status, body, headers = _req(base, "GET", "/api/tasks")
    assert status == 200
    records = json.loads(body)["records"]
    assert len(records) == 1
    assert records[0]["title"] == "pytest probe"
    assert records[0]["status"] == "queued"
    assert headers.get("Access-Control-Allow-Origin") == \
        "http://localhost:8765"


# ------------------------------------------------------- generated files
def test_status_founder_os_is_f2_batch_2():
    status = _load_status()
    assert status["founder_os"]["phase"] == "F2"
    assert status["founder_os"]["batch"] == 2


def test_status_roster_counts_are_consistent():
    roster = _load_status()["roster"]
    entries = roster["entries"]
    assert roster["total"] == len(entries)
    assert roster["draft"] + roster["coded"] + sum(
        1 for e in entries if e["worker"] == "unknown") == roster["total"]
    assert 0 <= roster["with_activity"] <= roster["total"]
    for e in entries:
        assert os.path.exists(REPO_ROOT / e["skill_file"])
        assert os.path.exists(REPO_ROOT / e["worker_file"])
        assert e["last_skill_load"] == "unknown" or "T" in e["last_skill_load"]


def test_roster_draft_count_matches_independent_recount():
    reg = json.loads(_read(
        REPO_ROOT / "01-Agency-Department" / "agents" / "agent-registry"
        / "registry.json"))
    recount = 0
    for e in reg:
        text = (REPO_ROOT / e["worker_file"]).read_text(
            encoding="utf-8", errors="ignore")[:65536]
        if "MOCK DRAFT" in text:
            recount += 1
    assert recount == _load_status()["roster"]["draft"]


def test_ceo_report_copy_is_byte_identical():
    status = _load_status()
    src = _read(REPO_ROOT / status["ceo_report"]["path"])
    assert _read(DASH / "ceo-report.json") == src


def test_command_center_no_fake_data():
    page = _read(DASH / "command-center.html")
    nostyle = re.sub(r"<style>.*?</style>", "", page, flags=re.S)
    for section in ("m1", "m5", "m6", "m7", "m10", "m11", "m15", "m17",
                    "m18", "m19"):
        assert f'id="{section}"' in page
    assert set(re.findall(r'fetch\("([^"]+)"', page)) == \
        {"status.json", "ceo-report.json"}
    assert set(re.findall(r'TASKBOARD \+ "([^"]+)"', page)) == \
        {"/api/tasks", "/api/approvals", "/api/approvals/decide"}
    assert "store/" not in page
    for lit in ("162", "163", "39/100", "374", "$547", "$1,109", "$1,672",
                "$597", "$1,297", "$1,997", "$49", "524", "2.19", "1.85",
                "1.67"):
        assert lit not in nostyle
    assert not re.search(r"(?<![0-9])69(?![0-9])", nostyle)
    assert not re.findall(
        r"(first_mails|paying_clients|pending_count|pa_list|total_usd)"
        r"\s*:\s*\d", page)
    assert "no auto-approve" in page and "Always allow" not in page
    nav = page[page.find('<nav id="sidebar">'):page.find("</nav>")]
    for n in (10, 15, 17, 18, 19):
        assert re.search(
            r'<a[^>]*class="nav-item[^"]*"[^>]*href="#m%d"' % n, nav)
    assert not set(re.findall(r'href="#m(\d+)"', nav)) & {
        "2", "3", "4", "8", "9", "12", "13", "14", "16"}


def test_module_19_read_only_and_module_17_no_purchase():
    page = _read(DASH / "command-center.html")
    m19 = page[page.find('id="m19"'):page.find("<footer", page.find('id="m19"'))]
    assert "Read-only" in m19
    for tag in ("<form", "<input", "<button", "<select", "contenteditable"):
        assert tag not in m19
    m17 = page[page.find('id="m17"'):page.find('id="m18"')]
    assert "<button" not in m17


def test_status_task_queue_is_internally_consistent():
    tq = _load_status()["task_queue"]
    records = tq["records"]
    assert tq["total"] == len(records)
    by = tq["by_status"]
    assert by["total"] == len(records)
    assert sum(v for k, v in by.items() if k != "total") == len(records)
    for r in records:
        for key in ("id", "status", "business", "type", "title",
                    "queued_at", "completed_at"):
            assert key in r
    watch = tq["queue_watch"]
    assert watch["name"] == "taskboard-queue-watch"
    assert isinstance(watch["interval_minutes"], int)
    assert isinstance(watch["runs"], int)
    assert tq["drain"]["method"] == "manual CLI"
    assert tq["drain"]["command"] == \
        "python scripts/run_office.py --drain-queue --max 2"
    assert tq["drain"]["runner"] == "none attached"


def _report_generated_at(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        val = json.loads(text).get("generated_at")
        if val:
            return val
    except ValueError:
        pass
    m = re.search(r"Generated:\s*(\S+)", text)
    return m.group(1) if m else None


def test_status_reports_match_disk():
    status = _load_status()
    rp = status["reports"]
    ceo_dir = REPO_ROOT / "reports" / "ceo"
    disk_files = sorted(p.name for p in ceo_dir.iterdir())
    assert rp["total"] == len(disk_files) == len(rp["files"])
    assert sorted(f["name"] for f in rp["files"]) == disk_files
    for f in rp["files"]:
        assert (ceo_dir / f["name"]).stat().st_size == f["size_bytes"]
    gen = {name: _report_generated_at(ceo_dir / name)
           for name in disk_files}
    newest = max(gen, key=lambda name: gen.get(name) or "")
    assert rp["latest"]["name"] == newest
    assert rp["latest"]["generated_at"] == gen[newest]
    dt = datetime.fromisoformat(
        gen[newest].replace("Z", "+00:00"))
    assert rp["latest"]["age_days"] == \
        (datetime.now(timezone.utc) - dt).days
    assert rp["performance"] == "none"
    assert rp["leads"] == "none"


def test_status_finance_is_internally_consistent():
    status = _load_status()
    fn = status["finance"]
    led = fn["ledger"]
    assert float(led["total_usd"]) == 0.0
    assert sum(v["records"] for v in led["by_provider"].values()) == \
        led["records"]
    assert sum(v["cost_usd"] for v in led["by_provider"].values()) == \
        float(led["total_usd"])
    assert sum(led["by_kind"].values()) == led["records"]
    assert led["first_at"] <= led["last_at"]
    assert float(led["monthly_total_usd"]) == 0.0
    assert float(led["monthly_cap_usd"]) == 0.0
    pricing = json.loads(_read(REPO_ROOT / "00-CEO-Core" / "pricing.json"))
    assert fn["pricing"] == pricing
    kit_text = _read(REPO_ROOT / "02-Digital-Product-Department"
                     / "kit-outline.md")
    m = re.search(r"\*\*Price:\*\*\s*\$(\d+)\s+one-time\s*\(launch price "
                  r"\$(\d+) for the first 30 buyers", kit_text)
    assert m is not None
    assert fn["gate0"]["kit_price_usd"] == int(m.group(1))
    assert fn["gate0"]["kit_launch_price_usd"] == int(m.group(2))
    readme_dp = _read(REPO_ROOT / "02-Digital-Product-Department"
                      / "README.md")
    assert "1 of 20" in readme_dp and "$1,109" in readme_dp
    assert "UNTESTED" in str(fn["gate0"]["wedge"])
    assert fn["gate0"]["status"] == "NOT PASSED"
    assert fn["gate0"]["kit_sales"] == 0
    assert float(fn["revenue"]["revenue_usd"]) == 0.0
    assert fn["revenue"]["paying_clients"] == 0
    assert fn["revenue"]["paying_clients"] == status["paying_clients"]


def test_status_health_matches_sources():
    status = _load_status()
    hl = status["health"]
    record_path = DASH / "health-record.json"
    if record_path.exists():
        record = json.loads(_read(record_path))
        assert hl["suite"] == record["suite"]
        assert hl["pytest"] == record["pytest"]
    else:
        assert hl["suite"] == "unknown"
        assert hl["pytest"] == "unknown"
    assert hl["python"] == sys.version.split()[0]
    du = shutil.disk_usage(REPO_ROOT)
    assert abs(float(hl["disk"]["free_gb"]) - du.free / (1024 ** 3)) <= 0.5
    assert abs(float(hl["disk"]["total_gb"]) - du.total / (1024 ** 3)) <= 0.5
    voice_root = REPO_ROOT / "00-CEO-Core" / "voice" / "models"
    total_bytes = 0
    for root, _dirs, files in os.walk(REPO_ROOT / "00-CEO-Core" / "voice"):
        for name in files:
            total_bytes += os.path.getsize(os.path.join(root, name))
    assert hl["voice_models"]["total_size_mb"] == \
        round(total_bytes / (1024 ** 2), 1)
    for name in ("piper", "sherpa-bn", "vosk"):
        sub = voice_root / name
        assert hl["voice_models"][name]["present"] == sub.is_dir()
        onnx = sum(1 for p in sub.rglob("*.onnx"))
        assert hl["voice_models"][name]["onnx_files"] == onnx
    cfg = json.loads(_read(REPO_ROOT / "00-CEO-Core" / "config.json"))
    for name, entry in hl["providers"].items():
        assert entry["enabled"] == bool(
            cfg["providers"][name]["enabled"])
    assert hl["check_scripts"] == len(glob.glob(
        str(REPO_ROOT / "scripts" / "check_*.py")))
    assert hl["test_files"] == len(glob.glob(
        str(REPO_ROOT / "tests" / "test_*.py")))
    assert hl["brain"] == cfg["brain"]


def test_status_policy_matches_config_and_matrix():
    status = _load_status()
    pol = status["policy"]
    cfg = json.loads(_read(REPO_ROOT / "00-CEO-Core" / "config.json"))
    assert pol["gate_words"] == cfg["gates"]["words"]
    assert pol["gated_actions"] == cfg["gates"]["gated_actions"]
    assert pol["approval_ttl_minutes"] == APPROVAL_TTL_MINUTES
    assert float(pol["spend_cap_usd"]) == float(cfg["spend_cap_usd"])
    assert pol["brain"] == cfg["brain"]
    assert pol["production_brain"]["mode"] == \
        cfg["production_brain"]["mode"]
    assert pol["production_brain"]["unlocked"] is False
    assert pol["free_only_guard"] is True
    assert pol["email"] == status["email"]
    matrix_text = _read(REPO_ROOT / "TALVENOR_PERMISSION_MATRIX.md")
    pm = pol["permission_matrix"]
    assert pm["text"] == matrix_text
    rows = [ln for ln in matrix_text.splitlines() if ln.startswith("| `")]
    assert pm["agent_rows"] == len(rows)


def test_3d_dashboard_snapshot_labelled_and_placeholders():
    page = _read(DASH / "dashboard-3d.html")
    assert 'id="snapshot-banner"' in page
    assert "Last known snapshot, 2026-11-20" in page
    no_fb = re.sub(r"const FALLBACK = \{.*?\n\};", "", page, flags=re.S)
    no_fb = re.sub(r"<style>.*?</style>", "", no_fb, flags=re.S)
    for lit in ("162", "39/100", "374"):
        assert lit not in no_fb
    for ph in ("{first_mails}", "{pa_list}", "{approvals_pending}",
               "{paying_clients}", "{email}"):
        assert ph in page
    assert 'href="command-center.html"' in page
