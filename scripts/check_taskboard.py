#!/usr/bin/env python3
"""check_taskboard.py — Phase 9 task-board self-check (C1, 2026-11-21).

What it checks (in-process server on an ephemeral port, TEMP store):
  1. GET /api/tasks returns the seeded records (incl. a done record
     with a result).
  2. POST valid body (find_skill + payload) -> 201, queued record.
  3. POST invalid bodies -> 400 (missing title, bad type, bad
     business, non-object payload, non-JSON body).
  4. GET / serves the board page with the find_skill datalist option
     and the payload textarea.
  5. DELETE a queued task -> 200 (cancelled); DELETE again -> 404;
     DELETE a done task -> 409 (queued-only).
  6. The TEMP tasks file holds exactly the expected records.
  7. Real store/tasks.json is untouched by this check run.

Stdlib only, no network beyond localhost, no send, no spend.
Exit 0 = PASS.
"""

import json
import os
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE, "scripts")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _snapshot_real_tasks():
    try:
        with open(os.path.join(BASE, "store", "tasks.json"),
                  encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def main():
    real_before = _snapshot_real_tasks()
    tmp_dir = tempfile.mkdtemp()
    tmp_tasks = os.path.join(tmp_dir, "tasks.json")
    tmp_status = os.path.join(tmp_dir, "status.json")
    seeded_done = {
        "id": "done00000001",
        "status": "done",
        "business": "agency",
        "type": "research",
        "title": "verify the booking link is live",
        "payload": {},
        "queued_at": "2026-11-21T00:00:00+00:00",
        "result": "VERIFIED LIVE — booking page loads.",
        "drained_at": "2026-11-21T00:05:00+00:00",
    }
    with open(tmp_tasks, "w", encoding="utf-8") as f:
        json.dump({"schema": "tasks-v1", "records": [seeded_done]}, f, indent=2)
    with open(tmp_status, "w", encoding="utf-8") as f:
        json.dump({"phase": 11}, f)

    # Env overrides BEFORE importing the server module (it reads them
    # at import time, like the MCP server).
    os.environ["TALVENOR_TASKBOARD_TASKS"] = tmp_tasks
    os.environ["TALVENOR_TASKBOARD_STATUS"] = tmp_status
    os.environ["TALVENOR_TASKBOARD_PAGE"] = os.path.join(
        BASE, "dashboards", "taskboard.html")
    sys.path.insert(0, SCRIPTS_DIR)
    import taskboard_server  # noqa: PLC0415

    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 taskboard_server.TaskboardHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    def _req(method, path, body=None, raw=None):
        data = raw if raw is not None else (
            json.dumps(body).encode("utf-8") if body is not None else None)
        req = urllib.request.Request(base_url + path, data=data, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8")

    try:
        # 1. GET /api/tasks — seeded done record.
        status, body = _req("GET", "/api/tasks")
        data = json.loads(body) if status == 200 else {}
        ok1 = (status == 200 and len(data.get("records", [])) == 1
               and data["records"][0]["id"] == "done00000001"
               and data["records"][0]["result"].startswith("VERIFIED LIVE"))
        check("GET /api/tasks returns seeded done record with result",
              ok1, f"status={status}")

        # 2. POST valid (find_skill + payload) -> 201.
        status, body = _req("POST", "/api/tasks", {
            "title": "find skill: backup",
            "type": "find_skill",
            "business": "agency",
            "payload": {"query": "backup"}})
        created = json.loads(body) if status == 201 else {}
        ok2 = (status == 201 and created.get("status") == "queued"
               and created.get("type") == "find_skill"
               and created.get("payload") == {"query": "backup"}
               and created.get("id"))
        check("POST valid body (find_skill + payload) -> 201 queued",
              ok2, f"status={status}, id={created.get('id')}")
        created_id = created.get("id")

        # 3. POST invalid bodies -> 400.
        invalid_cases = [
            ("missing title", {"type": "research"}),
            ("bad type", {"title": "x", "type": "Bad Type!"}),
            ("bad business", {"title": "x", "type": "research",
                             "business": "nowhere"}),
            ("non-object payload", {"title": "x", "type": "research",
                                   "payload": ["a"]}),
        ]
        invalid_ok = True
        for label, payload in invalid_cases:
            status, _body = _req("POST", "/api/tasks", payload)
            if status != 400:
                invalid_ok = False
                print(f"  invalid case {label!r} -> {status} (want 400)")
        status, _body = _req("POST", "/api/tasks", raw=b"{not json")
        if status != 400:
            invalid_ok = False
        check("POST invalid bodies -> 400 (title/type/business/payload/JSON)",
              invalid_ok)

        # 4. GET / serves the board with find_skill + payload textarea.
        status, body = _req("GET", "/")
        ok4 = (status == 200 and 'value="find_skill"' in body
               and 'id="payload"' in body and "truncateResult" in body)
        check("GET / serves board with find_skill datalist + payload field",
              ok4, f"status={status}")

        # 5. DELETE queued -> 200; again -> 404; done -> 409.
        status, body = _req("DELETE", f"/api/tasks/{created_id}")
        del_ok = status == 200
        status, _body = _req("DELETE", f"/api/tasks/{created_id}")
        del_ok = del_ok and status == 404
        status, _body = _req("DELETE", "/api/tasks/done00000001")
        del_ok = del_ok and status == 409
        check("DELETE queued -> 200; again -> 404; done -> 409 (queued-only)",
              del_ok)

        # 6. TEMP tasks file holds exactly the seeded done record.
        with open(tmp_tasks, encoding="utf-8") as f:
            after = json.load(f)["records"]
        check("TEMP tasks file holds only the seeded done record",
              len(after) == 1 and after[0]["id"] == "done00000001",
              f"records={len(after)}")
    except Exception as exc:  # noqa: BLE001
        for name in ("GET /api/tasks returns seeded done record with result",
                     "POST valid body (find_skill + payload) -> 201 queued",
                     "POST invalid bodies -> 400 (title/type/business/payload/JSON)",
                     "GET / serves board with find_skill datalist + payload field",
                     "DELETE queued -> 200; again -> 404; done -> 409 (queued-only)",
                     "TEMP tasks file holds only the seeded done record"):
            if not any(r[0] == name for r in results):
                check(name, False, f"{type(exc).__name__}: {exc}")
    finally:
        server.shutdown()
        server.server_close()

    # 7. Real store untouched.
    try:
        check("real store/tasks.json untouched by this check run",
              _snapshot_real_tasks() == real_before,
              "unchanged" if _snapshot_real_tasks() == real_before else "CHANGED")
    except Exception as exc:  # noqa: BLE001
        check("real store/tasks.json untouched by this check run", False, str(exc))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_taskboard: ALL PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
