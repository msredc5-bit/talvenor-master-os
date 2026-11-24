"""Local n8n test double — Talvenor Master OS, local-first Phase 4.

A stdlib ``http.server``-based stand-in for the n8n REST/webhook
contract (strategy §5), used ONLY by tests and checks. It is never a
live n8n, it is never started automatically on import, and it only
ever binds ``127.0.0.1`` on an ephemeral port.

Contract implemented:
  POST /api/v1/workflows            -> create (201, {"id", ...})
  GET  /api/v1/workflows            -> list ({"data": [...]})
  POST /api/v1/workflows/{id}/activate   -> active true
  POST /api/v1/workflows/{id}/deactivate -> active false
  POST /webhook/<path>              -> requires the shared-secret
       header (401 without it); creates an execution
  POST /webhook-test/<path>         -> same, test mode
  GET  /api/v1/executions/<id>      -> execution status
  GET  /api/v1/executions           -> list ({"data": [...]})

Double behaviour, documented honestly: an execution goes
queued -> running -> finished SYNCHRONOUSLY inside the webhook
call (a real n8n runs it asynchronously — poll
``GET /api/v1/executions/<id>`` there). The status read back is
therefore always "finished" here; the point of the double is to
prove the adapter's create/activate/list/trigger/status round
trip, not to simulate n8n's scheduler.

Shared secret: the double checks the SAME header the adapter
sends, ``X-Talvenor-Webhook-Secret`` (Talvenor convention — the
real n8n Webhook node must be configured with the same header
name/value). The API key (``X-N8N-API-KEY``) is accepted when
sent but NOT required by the double — requiring it would make
every offline check depend on a key existing.

Usage (tests only):
  double = N8nTestDouble(secret="test-secret")
  with double:
      adapter = N8nAdapter(base_url=double.base_url, ...)
      ...

Stdlib only. In-memory state only — nothing is written to disk.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

__all__ = ["N8nTestDouble", "WEBHOOK_SECRET_HEADER"]

WEBHOOK_SECRET_HEADER = "X-Talvenor-Webhook-Secret"


class _DoubleState:
    """In-memory workflows + executions, guarded by one lock."""

    def __init__(self, secret):
        self.secret = secret
        self.lock = threading.Lock()
        self.workflows = {}
        self.executions = {}
        self.next_workflow = 1
        self.next_execution = 1


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # -- helpers --------------------------------------------------------
    @property
    def _state(self):
        return self.server.double_state

    def log_message(self, *args):  # noqa: D102 — keep test output clean
        pass

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def _not_found(self, what):
        self._send_json(404, {"message": f"{what} not found"})

    # -- routing ----------------------------------------------------------
    def do_GET(self):  # noqa: N802 — http.server naming
        path = self.path.split("?", 1)[0]
        if path == "/api/v1/workflows":
            with self._state.lock:
                workflows = list(self._state.workflows.values())
            self._send_json(200, {"data": workflows})
            return
        if path == "/api/v1/executions":
            with self._state.lock:
                executions = list(self._state.executions.values())
            self._send_json(200, {"data": executions})
            return
        if path.startswith("/api/v1/executions/"):
            execution_id = path[len("/api/v1/executions/"):].strip("/")
            with self._state.lock:
                execution = self._state.executions.get(execution_id)
            if execution is None:
                self._not_found(f"execution {execution_id!r}")
                return
            self._send_json(200, dict(execution))
            return
        self._not_found(f"route {path!r}")

    def do_POST(self):  # noqa: N802 — http.server naming
        path = self.path.split("?", 1)[0]
        if path == "/api/v1/workflows":
            self._create_workflow()
            return
        if path.startswith("/api/v1/workflows/"):
            self._workflow_action(path)
            return
        if path.startswith("/webhook/") or path.startswith("/webhook-test/"):
            self._webhook(path)
            return
        self._not_found(f"route {path!r}")

    # -- handlers ---------------------------------------------------------
    def _create_workflow(self):
        body = self._read_json()
        if body is None:
            self._send_json(400, {"message": "body must be a JSON object"})
            return
        with self._state.lock:
            workflow_id = f"wf-{self._state.next_workflow}"
            self._state.next_workflow += 1
            workflow = {"id": workflow_id,
                        "name": body.get("name", "Untitled workflow"),
                        "nodes": body.get("nodes", []),
                        "connections": body.get("connections", {}),
                        "active": bool(body.get("active", False)),
                        "settings": body.get("settings", {}),
                        "tags": body.get("tags", [])}
            self._state.workflows[workflow_id] = workflow
        self._send_json(201, dict(workflow))

    def _workflow_action(self, path):
        rest = path[len("/api/v1/workflows/"):]
        parts = [p for p in rest.split("/") if p]
        if len(parts) != 2 or parts[1] not in ("activate", "deactivate"):
            self._not_found(f"route {path!r}")
            return
        workflow_id, action = parts
        with self._state.lock:
            workflow = self._state.workflows.get(workflow_id)
            if workflow is None:
                self._not_found(f"workflow {workflow_id!r}")
                return
            workflow["active"] = action == "activate"
            result = dict(workflow)
        self._send_json(200, result)

    def _webhook(self, path):
        test_mode = path.startswith("/webhook-test/")
        prefix = "/webhook-test/" if test_mode else "/webhook/"
        webhook_path = path[len(prefix):].strip("/")
        if not webhook_path:
            self._send_json(400, {"message": "webhook path is empty"})
            return
        secret = self.headers.get(WEBHOOK_SECRET_HEADER)
        if secret != self._state.secret:
            self._send_json(401, {"message": "unauthorized — missing or "
                                             "wrong webhook secret header"})
            return
        body = self._read_json()
        if body is None:
            self._send_json(400, {"message": "body must be a JSON object"})
            return
        with self._state.lock:
            execution_id = f"exec-{self._state.next_execution}"
            self._state.next_execution += 1
            # Double behaviour: the execution finishes synchronously
            # (a real n8n would be queued -> running -> finished).
            execution = {
                "id": execution_id,
                "status": "finished",
                "mode": "test" if test_mode else "production",
                "webhook_path": webhook_path,
                "payload": body,
            }
            self._state.executions[execution_id] = execution
        self._send_json(200, {"executionId": execution_id,
                              "status": "finished"})


class N8nTestDouble:
    """A local n8n stand-in. Start it explicitly; never on import.

    Binds 127.0.0.1 on an ephemeral port (port 0). ``base_url`` is
    only valid while the double is running.
    """

    def __init__(self, secret="test-secret"):
        self.secret = secret
        self._server = None
        self._thread = None

    @property
    def base_url(self):
        if self._server is None:
            raise RuntimeError("test double is not running — call "
                               "start() first")
        host, port = self._server.server_address[:2]
        return f"http://{host}:{port}"

    @property
    def port(self):
        if self._server is None:
            raise RuntimeError("test double is not running — call "
                               "start() first")
        return self._server.server_address[1]

    def start(self):
        if self._server is not None:
            return self
        server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        server.double_state = _DoubleState(self.secret)
        server.daemon_threads = True
        self._server = server
        self._thread = threading.Thread(target=server.serve_forever,
                                        kwargs={"poll_interval": 0.05},
                                        daemon=True)
        self._thread.start()
        return self

    def stop(self):
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def __enter__(self):
        return self.start()

    def __exit__(self, *exc):
        self.stop()
        return False
