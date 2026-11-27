#!/usr/bin/env python3
"""Task board server — Talvenor Master OS (Phase 9).

A tiny local web server (stdlib only) that serves the task board page
and a small JSON API. It does NOT run tasks — it only queues them.
The bridge cron (every 10 minutes) picks queued tasks up, does real
work (drafts/results only), and marks them done.

Endpoints (localhost only — no auth, never expose publicly):
  GET  /                -> dashboards/taskboard.html
  GET  /taskboard.html  -> the board page
  GET  /api/status      -> dashboards/status.json (fresh read)
  GET  /api/tasks       -> {"records": [...]} from store/tasks.json
  POST /api/tasks       -> validate + append one queued record:
      {"title": "...", "type": "research",
       "business": "agency", "payload": {...}}
      title: non-empty string, max 200 chars (required)
      type: snake_case task type, e.g. research, caption_write (required)
      business: agency | digital-product | content (default: agency)
      payload: object (optional, default {})
      priority: integer, higher drains first (optional, default 0)
      depends_on: list of task ids that must be done first (optional)
      max_retries: integer >= 0 (optional, default 0)
      idempotency_key: string (optional) — a second POST with a key
        that already exists returns 200 + the existing record, and
        queues nothing new
      -> 201 with the created record:
      {"id": "...", "status": "queued", "business": "agency",
       "type": "research", "title": "...", "payload": {...},
       "queued_at": "...", "priority": 0, "depends_on": [],
       "retries": 0, "max_retries": 0, "cancelled": false,
       "idempotency_key": null, "last_error": null}
  DELETE /api/tasks/<id> -> cancel one QUEUED task only (done/failed
      tasks cannot be deleted — history stays); missing id -> 404,
      non-queued -> 409.
  GET  /api/approvals    -> {"pending": [...]} via the REAL approval
      gateway (ApprovalCentre) — enriched records with allowed gate
      words, age and TTL expiry (same as the CLI's list command).
  POST /api/approvals/decide -> {"id": "...", "decision": "approve" |
      "reject", "gate_word": "..."} — approve REQUIRES the exact gate
      word; reject needs none. Both go straight through
      ApprovalCentre.decide -> the gateway (approve/reject). Wrong
      gate word, expired record, already-decided or unknown id ->
      400 with the gateway's own message. -> 200 with the decided
      record + the fresh pending list. CORS is allowed ONLY for the
      Command Center origin (http://localhost:8765); no other origin.

Environment (optional — defaults are the real repo paths, like the
MCP server's TALVENOR_MCP_* vars):
  TALVENOR_TASKBOARD_TASKS  — tasks JSON path
  TALVENOR_TASKBOARD_STATUS — status JSON path (/api/status)
  TALVENOR_TASKBOARD_PAGE   — board HTML path (/)
  TALVENOR_TASKBOARD_APPROVALS — approvals JSON path (/api/approvals)

Environment (optional — defaults are the real repo paths, like the
MCP server's TALVENOR_MCP_* vars):
  TALVENOR_TASKBOARD_TASKS  — tasks JSON path
  TALVENOR_TASKBOARD_STATUS — status JSON path (/api/status)
  TALVENOR_TASKBOARD_PAGE   — board HTML path (/)
Set them to TEMP paths in tests so the real store stays untouched.

Run:  python3 scripts/taskboard_server.py [--port 8766]
Then: http://localhost:8766/

Stdlib only. No send, no publish, no spend, no delete.
"""

import argparse
import json
import os
import re
import sys
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "00-CEO-Core"))

from audit import audit_log  # noqa: E402
from store_io import read_json, write_json_atomic  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARDS_DIR = os.path.join(BASE, "dashboards")
TASKS_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_TASKS", os.path.join(BASE, "store", "tasks.json"))
STATUS_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_STATUS", os.path.join(DASHBOARDS_DIR, "status.json"))
BOARDPAGE_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_PAGE", os.path.join(DASHBOARDS_DIR, "taskboard.html"))
APPROVALS_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_APPROVALS",
    os.path.join(BASE, "store", "approvals.json"))
# F2 batch 1 — the ONLY cross-origin caller allowed: the Command
# Center served by run_local.bat on localhost:8765. Never broaden.
COMMAND_CENTER_ORIGIN = "http://localhost:8765"

BUSINESSES = ("agency", "digital-product", "content")
TYPE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
MAX_TITLE_LEN = 200

_store_lock = threading.Lock()


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _read_tasks():
    # Phase 1 (Unified OS): locked read via store_io; a corrupt file
    # reads as empty (same as before — the board never crashes on it).
    try:
        data = read_json(TASKS_PATH,
                         default={"schema": "tasks-v1", "records": []})
    except json.JSONDecodeError:
        return []
    records = data.get("records", []) if isinstance(data, dict) else []
    return list(records) if isinstance(records, list) else []


def _write_tasks(records):
    # Phase 1 (Unified OS): atomic write — the in-process _store_lock
    # stays (same-process threads); store_io adds the cross-process
    # file lock.
    write_json_atomic(TASKS_PATH, {"schema": "tasks-v1", "records": records})


def _approval_centre():
    """The REAL approval centre (F2 batch 1) — imported lazily so a
    broken gateway only fails the approvals endpoints, never the
    task board. All reads/writes go through the gateway; this
    server never touches approvals.json itself."""
    from approval_centre import ApprovalCentre  # noqa: PLC0415
    return ApprovalCentre(approvals_path=APPROVALS_PATH)


def validate_task_body(body):
    """POST body -> (record dict, None) or (None, error string)."""
    if not isinstance(body, dict):
        return None, "Body must be a JSON object."
    title = body.get("title")
    if not isinstance(title, str) or not title.strip():
        return None, "Field 'title' is required (non-empty string)."
    if len(title.strip()) > MAX_TITLE_LEN:
        return None, f"Field 'title' is too long (max {MAX_TITLE_LEN} chars)."
    task_type = body.get("type")
    if not isinstance(task_type, str) or not TYPE_RE.match(task_type):
        return None, ("Field 'type' is required (snake_case, e.g. "
                      "'research' or 'caption_write').")
    business = body.get("business", "agency")
    if business not in BUSINESSES:
        return None, ("Field 'business' must be one of: "
                      + ", ".join(BUSINESSES) + ".")
    payload = body.get("payload", {})
    if not isinstance(payload, dict):
        return None, "Field 'payload' must be an object."
    # Phase 1 (Unified OS) tasks-v1 fields.
    priority = body.get("priority", 0)
    if isinstance(priority, bool) or not isinstance(priority, int):
        return None, "Field 'priority' must be an integer."
    depends_on = body.get("depends_on", [])
    if (not isinstance(depends_on, list)
            or any(not isinstance(d, str) for d in depends_on)):
        return None, "Field 'depends_on' must be a list of task ids."
    max_retries = body.get("max_retries", 0)
    if (isinstance(max_retries, bool) or not isinstance(max_retries, int)
            or max_retries < 0):
        return None, "Field 'max_retries' must be an integer >= 0."
    idempotency_key = body.get("idempotency_key")
    if idempotency_key is not None and (
            not isinstance(idempotency_key, str)
            or not idempotency_key.strip()
            or len(idempotency_key) > 128):
        return None, ("Field 'idempotency_key' must be a non-empty "
                      "string (max 128 chars).")
    if body.get("cancelled") not in (None, False):
        return None, "A new task cannot be created cancelled."
    if body.get("retries") not in (None, 0):
        return None, "Field 'retries' starts at 0."
    record = {
        "id": uuid.uuid4().hex[:12],
        "status": "queued",
        "business": business,
        "type": task_type,
        "title": title.strip(),
        "payload": payload,
        "priority": priority,
        "depends_on": depends_on,
        "retries": 0,
        "max_retries": max_retries,
        "cancelled": False,
        "idempotency_key": idempotency_key,
        "last_error": None,
        "queued_at": _now_iso(),
    }
    return record, None


class TaskboardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep stdout quiet
        pass

    def _cors_headers(self):
        # F2 batch 1 — Command Center only (localhost:8765). The
        # task board's other endpoints stay same-origin (no CORS).
        # F2 batch 2 — GET /api/tasks also sends these headers so
        # the Command Center's Task Center can live-read the queue.
        self.send_header("Access-Control-Allow-Origin",
                         COMMAND_CENTER_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _send_json(self, status, obj, cors=False):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        if cors:
            self._cors_headers()
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        try:
            with open(path, "rb") as f:
                body = f.read()
        except OSError:
            self._send_json(404, {"error": f"File not found: {path}"})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/taskboard.html"):
            self._send_file(BOARDPAGE_PATH, "text/html; charset=utf-8")
        elif self.path == "/api/status":
            self._send_file(STATUS_PATH, "application/json; charset=utf-8")
        elif self.path == "/api/tasks":
            # F2 batch 2 — CORS for the Command Center's Task Center
            # (same origin restriction as /api/approvals: localhost:8765
            # only). Read-only list; the page never queues from here.
            with _store_lock:
                records = _read_tasks()
            self._send_json(200, {"records": records}, cors=True)
        elif self.path == "/api/approvals":
            # F2 batch 1 — pending approvals via the REAL gateway.
            try:
                with _store_lock:
                    pending = _approval_centre().list_pending()
            except Exception as exc:  # gateway/file error — 500, not a crash
                self._send_json(500, {"error": str(exc)}, cors=True)
                return
            self._send_json(200, {"pending": pending}, cors=True)
        else:
            self._send_json(404, {"error": f"Unknown path: {self.path}"})

    def do_OPTIONS(self):
        # F2 batch 1 — preflight for the Command Center's JSON POSTs.
        if self.path.startswith("/api/approvals"):
            self.send_response(204)
            self._cors_headers()
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self._send_json(404, {"error": f"Unknown path: {self.path}"})

    def _read_json_body(self):
        """POST body -> (parsed dict, None) or (None, error string)."""
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return None, "Invalid Content-Length."
        if length <= 0 or length > 65536:
            return None, "Body is empty or too large."
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None, "Body is not valid JSON."
        if not isinstance(body, dict):
            return None, "Body must be a JSON object."
        return body, None

    def _handle_approve_decide(self):
        # F2 batch 1 — POST /api/approvals/decide, straight through
        # ApprovalCentre.decide -> the gateway. No new approval path.
        body, error = self._read_json_body()
        if error is not None:
            self._send_json(400, {"error": error}, cors=True)
            return
        approval_id = body.get("id")
        if not isinstance(approval_id, str) or not approval_id.strip():
            self._send_json(400, {"error": "Field 'id' is required."},
                            cors=True)
            return
        decision = body.get("decision")
        if decision not in ("approve", "reject"):
            self._send_json(400, {
                "error": "Field 'decision' must be 'approve' or 'reject'."},
                cors=True)
            return
        gate_word = body.get("gate_word")
        if decision == "approve":
            if not isinstance(gate_word, str) or not gate_word:
                self._send_json(400, {
                    "error": "Field 'gate_word' is required to approve."},
                    cors=True)
                return
        try:
            with _store_lock:
                centre = _approval_centre()
                record = centre.decide(approval_id, decision,
                                       gate_word=gate_word)
                pending = centre.list_pending()
        except ValueError as exc:
            # Gateway's own errors: wrong gate word, expired record,
            # already decided — surfaced unchanged.
            self._send_json(400, {"error": str(exc)}, cors=True)
            return
        except KeyError as exc:
            # Gateway's _find: unknown id is a client error, not a
            # server error.
            self._send_json(400, {"error": str(exc)}, cors=True)
            return
        except Exception as exc:  # gateway/file error — 500, not a crash
            self._send_json(500, {"error": str(exc)}, cors=True)
            return
        audit_log("approval_decided", {
            "approval_id": approval_id, "decision": decision,
            "status": record.get("status"),
        }, audit_path=os.path.join(os.path.dirname(APPROVALS_PATH),
                                   "audit.log"))
        self._send_json(200, {"record": record, "pending": pending},
                        cors=True)

    def do_POST(self):
        if self.path == "/api/approvals/decide":
            self._handle_approve_decide()
            return
        if self.path != "/api/tasks":
            self._send_json(404, {"error": f"Unknown path: {self.path}"})
            return
        body, error = self._read_json_body()
        if error is not None:
            self._send_json(400, {"error": error})
            return
        record, error = validate_task_body(body)
        if error is not None:
            self._send_json(400, {"error": error})
            return
        with _store_lock:
            # Re-read first: the bridge may have written meanwhile.
            records = _read_tasks()
            key = record.get("idempotency_key")
            if key:
                existing = next(
                    (r for r in records
                     if r.get("idempotency_key") == key), None)
                if existing is not None:
                    # Same key twice = one execution — queue nothing new.
                    self._send_json(200, existing)
                    return
            records.append(record)
            _write_tasks(records)
        audit_log("task_queued", {
            "task_id": record["id"], "business": record["business"],
            "type": record["type"],
        }, audit_path=os.path.join(os.path.dirname(TASKS_PATH),
                                   "audit.log"))
        self._send_json(201, record)

    def do_DELETE(self):
        # DELETE /api/tasks/<id> — queued-only cancel.
        if not self.path.startswith("/api/tasks/"):
            self._send_json(404, {"error": f"Unknown path: {self.path}"})
            return
        task_id = self.path[len("/api/tasks/"):].strip("/").split("/")[0]
        if not task_id:
            self._send_json(400, {"error": "Task id is required."})
            return
        with _store_lock:
            records = _read_tasks()
            target = next((r for r in records if r.get("id") == task_id),
                          None)
            if target is None:
                self._send_json(404, {"error": f"No task with id {task_id!r}."})
                return
            if target.get("status") != "queued":
                self._send_json(409, {
                    "error": f"Only queued tasks can be cancelled — "
                             f"task {task_id!r} is {target.get('status')!r}."})
                return
            records = [r for r in records if r.get("id") != task_id]
            _write_tasks(records)
        audit_log("task_cancelled", {
            "task_id": task_id, "title": target.get("title"),
        }, audit_path=os.path.join(os.path.dirname(TASKS_PATH),
                                   "audit.log"))
        self._send_json(200, {"cancelled": target})


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Talvenor Master OS task board server (localhost only).")
    parser.add_argument("--host", default="127.0.0.1",
                        help="bind host (default 127.0.0.1 — localhost only)")
    parser.add_argument("--port", type=int, default=8766,
                        help="bind port (default 8766)")
    args = parser.parse_args(argv)
    server = ThreadingHTTPServer((args.host, args.port), TaskboardHandler)
    print(f"taskboard running — http://{args.host}:{args.port}/")
    print("Stop with Ctrl+C. Queued tasks are picked up by the bridge "
          "cron (every 10 min, max 2/run, drafts/results only).")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\ntaskboard stopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
