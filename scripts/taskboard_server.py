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
      -> 201 with the created record:
      {"id": "...", "status": "queued", "business": "agency",
       "type": "research", "title": "...", "payload": {...},
       "queued_at": "..."}
  DELETE /api/tasks/<id> -> cancel one QUEUED task only (done/failed
      tasks cannot be deleted — history stays); missing id -> 404,
      non-queued -> 409.

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
import threading
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARDS_DIR = os.path.join(BASE, "dashboards")
TASKS_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_TASKS", os.path.join(BASE, "store", "tasks.json"))
STATUS_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_STATUS", os.path.join(DASHBOARDS_DIR, "status.json"))
BOARDPAGE_PATH = os.environ.get(
    "TALVENOR_TASKBOARD_PAGE", os.path.join(DASHBOARDS_DIR, "taskboard.html"))

BUSINESSES = ("agency", "digital-product", "content")
TYPE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
MAX_TITLE_LEN = 200

_store_lock = threading.Lock()


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _read_tasks():
    try:
        with open(TASKS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", []) if isinstance(data, dict) else []
        return list(records) if isinstance(records, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _write_tasks(records):
    payload = {"schema": "tasks-v1", "records": records}
    tmp_path = TASKS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, TASKS_PATH)


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
    record = {
        "id": uuid.uuid4().hex[:12],
        "status": "queued",
        "business": business,
        "type": task_type,
        "title": title.strip(),
        "payload": payload,
        "queued_at": _now_iso(),
    }
    return record, None


class TaskboardHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep stdout quiet
        pass

    def _send_json(self, status, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
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
            with _store_lock:
                records = _read_tasks()
            self._send_json(200, {"records": records})
        else:
            self._send_json(404, {"error": f"Unknown path: {self.path}"})

    def do_POST(self):
        if self.path != "/api/tasks":
            self._send_json(404, {"error": f"Unknown path: {self.path}"})
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return
        if length <= 0 or length > 65536:
            self._send_json(400, {"error": "Body is empty or too large."})
            return
        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self._send_json(400, {"error": "Body is not valid JSON."})
            return
        record, error = validate_task_body(body)
        if error is not None:
            self._send_json(400, {"error": error})
            return
        with _store_lock:
            # Re-read first: the bridge may have written meanwhile.
            records = _read_tasks()
            records.append(record)
            _write_tasks(records)
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
