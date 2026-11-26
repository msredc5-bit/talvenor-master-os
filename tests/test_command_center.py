"""FOUNDER OS F2 batch 1 — Command Center tests (2026-11-26).

Real code under test (stdlib only, temp stores for the server,
read-only for the generated dashboard files — no network beyond
localhost, no live LLM calls, no send/publish/spend/delete/deploy,
$0):

  * scripts/taskboard_server.py — GET /api/approvals and
    POST /api/approvals/decide, both straight through the REAL
    approval gateway (ApprovalCentre). The gateway's own errors
    (wrong gate word, expired, already decided, unknown id) must
    surface as HTTP 400, never 500, never swallowed.
  * dashboards/command-center.html — no-fake-data: the page fetches
    only status.json + ceo-report.json, never a store file, and
    contains no hardcoded metric literal.
  * dashboards/status.json (generated) — founder_os F2 batch 1,
    roster counts consistent, draft count matches an independent
    recount of the [MOCK DRAFT] marker.
  * dashboards/ceo-report.json — byte-identical to the CEO report
    status.json points to.
  * dashboards/dashboard-3d.html — the dated fallback snapshot is
    banner-labelled; detail numbers are live placeholders.
"""
import json
import os
import re
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import taskboard_server
from approval_centre import ApprovalCentre

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


# ------------------------------------------------------- generated files
def test_status_founder_os_is_f2_batch_1():
    status = _load_status()
    assert status["founder_os"]["phase"] == "F2"
    assert status["founder_os"]["batch"] == 1


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
    for section in ("m1", "m5", "m6", "m7", "m11"):
        assert f'id="{section}"' in page
    assert set(re.findall(r'fetch\("([^"]+)"', page)) == \
        {"status.json", "ceo-report.json"}
    assert "store/" not in page
    for lit in ("162", "163", "39/100", "374"):
        assert lit not in nostyle
    assert not re.search(r"(?<![0-9])69(?![0-9])", nostyle)
    assert not re.findall(
        r"(first_mails|paying_clients|pending_count|pa_list|total_usd)"
        r"\s*:\s*\d", page)
    assert "no auto-approve" in page and "Always allow" not in page


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
