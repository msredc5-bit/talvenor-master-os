"""n8n adapter — Talvenor Master OS, local-first Phase 4.

Talks to n8n ONLY through (a) the public REST API
(``/api/v1``, header ``X-N8N-API-KEY``) and (b) webhook URLs
(``/webhook/<path>``, header-auth shared secret) — exactly the
surface verified in
``~/workspace/unified-business-os/local-development-strategy-2026-11-24.md``
§5 (official n8n docs, 2026-11-24). No direct database access, no
n8n internals. Swapping the engine later = swapping this adapter.

Operations (strategy §5 "Suggested adapter operations"):
  create_workflow(workflow_json), activate_workflow(id),
  deactivate_workflow(id), list_workflows(),
  trigger_via_webhook(path, payload), get_execution_status(id).

Rules (hard):
  * LOCALHOST ONLY. Any base URL whose host is not ``localhost``
    or ``127.0.0.1`` is refused with ValueError at construction —
    the adapter is localhost-only by design. Never call a real or
    remote n8n instance from this code.
  * Credentials come ONLY from environment variables, never from
    files: ``N8N_BASE_URL`` (default ``http://localhost:5678``),
    ``N8N_API_KEY``, ``N8N_WEBHOOK_SECRET``. They are never logged,
    never printed, and never appear in an error message (errors
    carry method + path + HTTP status only — never headers or a
    body, which could echo a secret or a payload).
  * Transport is stdlib ``http.client`` only. No ``requests``, no
    ``urllib``.
  * Webhook trigger is the verified on-demand run path: the
    official pages read for §5 confirmed NO dedicated "run
    workflow" REST endpoint, so triggering goes through the
    workflow's webhook URL. Production webhook:
    ``/webhook/<path>``; test webhook (listening only while the
    editor listens): ``/webhook-test/<path>``.
  * Webhook header auth: Talvenor convention, header
    ``X-Talvenor-Webhook-Secret`` carrying the shared secret — the
    n8n Webhook node must be configured with the same header name
    and value (Header Auth). The test double enforces the same
    header.
  * This adapter is NOT a live-n8n client in this VM: n8n lives on
    Boss's PC, not here. In this VM it is exercised only against
    the local test double (``test_double.py``). Real-n8n
    end-to-end is [NOT TESTED] here.
"""

from __future__ import annotations

import http.client
import json
import os

__all__ = ["N8nAdapter", "N8nError"]

# Env vars — the ONLY places credentials may live (same rule as
# every Master OS key: Windows env vars on Boss's PC, never files).
ENV_BASE_URL = "N8N_BASE_URL"
ENV_API_KEY = "N8N_API_KEY"
ENV_WEBHOOK_SECRET = "N8N_WEBHOOK_SECRET"

DEFAULT_BASE_URL = "http://localhost:5678"

# Hosts this adapter will ever talk to. Anything else is refused.
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1"})

# Talvenor webhook header-auth convention (see module docstring).
WEBHOOK_SECRET_HEADER = "X-Talvenor-Webhook-Secret"
API_KEY_HEADER = "X-N8N-API-KEY"

# Characters allowed in a workflow id / webhook path without
# quoting (keeps urllib out of this module entirely).
_SAFE_PATH_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._/")


class N8nError(Exception):
    """An n8n call failed. Carries the HTTP status only — never a
    key, a secret, or a request body."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def _validate_local_url(base_url):
    """Parse + enforce localhost-only. Returns (scheme, host, port).
    Raises ValueError on anything non-localhost (or unparseable).
    Manual parse — no urllib in this module (http.client only)."""
    text = str(base_url or "").strip()
    scheme = "http"
    rest = text
    if "://" in text:
        scheme, rest = text.split("://", 1)
        scheme = scheme.lower()
    hostport = rest.split("/", 1)[0]
    host = hostport
    port = None
    if hostport.startswith("["):  # IPv6 literal — never local here
        host = hostport.split("]", 1)[0].lstrip("[")
    elif ":" in hostport:
        host, _, port_text = hostport.rpartition(":")
        try:
            port = int(port_text)
        except ValueError as exc:
            raise ValueError(
                f"invalid n8n base URL port: {port_text!r}") from exc
    host = host.lower()
    if host not in LOCAL_HOSTS:
        raise ValueError(
            "n8n adapter is localhost-only by design — refusing "
            f"non-localhost base URL (host={host!r}). n8n lives on "
            "Boss's PC at http://localhost:5678; this adapter never "
            "calls a remote instance.")
    if scheme not in ("http", "https"):
        raise ValueError(
            f"n8n base URL scheme must be http or https, got "
            f"{scheme!r}.")
    return scheme, host, port


def _validate_path_segment(value, label):
    """A workflow id / webhook path must be plain safe characters —
    no query strings, no traversal, no quoting needed."""
    text = str(value or "").strip().strip("/")
    if not text:
        raise ValueError(f"{label} must be a non-empty path")
    if ".." in text.split("/"):
        raise ValueError(f"{label} must not contain '..'")
    bad = sorted({c for c in text if c not in _SAFE_PATH_CHARS})
    if bad:
        raise ValueError(
            f"{label} contains unsafe characters {bad!r} — refusing")
    return text


class N8nAdapter:
    """Localhost-only n8n client (REST + webhooks). Stdlib only."""

    def __init__(self, base_url=None, api_key=None, webhook_secret=None,
                 timeout=10.0):
        raw_url = (base_url if base_url is not None
                   else os.environ.get(ENV_BASE_URL) or DEFAULT_BASE_URL)
        self.base_url = str(raw_url).strip()
        self.scheme, self.host, self.port = _validate_local_url(
            self.base_url)
        # Credentials from env only, never files. They are stored
        # for the request headers and NEVER logged or put in errors.
        self.api_key = (api_key if api_key is not None
                        else os.environ.get(ENV_API_KEY) or "")
        self.webhook_secret = (
            webhook_secret if webhook_secret is not None
            else os.environ.get(ENV_WEBHOOK_SECRET) or "")
        self.timeout = float(timeout)

    # -- low-level ------------------------------------------------------
    def _connection(self):
        if self.scheme == "https":
            return http.client.HTTPSConnection(
                self.host, self.port or 443, timeout=self.timeout)
        return http.client.HTTPConnection(
            self.host, self.port or 5678, timeout=self.timeout)

    def _request(self, method, path, body=None, api_key=True):
        """One HTTP call. Returns the parsed JSON body ({} when the
        body is empty). Non-2xx -> N8nError with status only.
        Never logs, never includes headers or body in the error."""
        headers = {"Content-Type": "application/json"}
        if api_key and self.api_key:
            headers[API_KEY_HEADER] = self.api_key
        data = None
        if body is not None:
            try:
                data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            except (TypeError, ValueError) as exc:
                raise N8nError(f"n8n {method} {path}: body is not "
                               f"JSON-serializable: {exc}") from exc
        conn = self._connection()
        try:
            conn.request(method, path, body=data, headers=headers)
            response = conn.getresponse()
            raw = response.read()
        except (http.client.HTTPException, OSError) as exc:
            raise N8nError(
                f"n8n {method} {path} failed: "
                f"{type(exc).__name__}") from exc
        finally:
            conn.close()
        if not 200 <= response.status < 300:
            raise N8nError(
                f"n8n {method} {path} failed with HTTP "
                f"{response.status}", status=response.status)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise N8nError(
                f"n8n {method} {path}: response is not JSON: {exc}",
                status=response.status) from exc

    # -- REST API (/api/v1) ---------------------------------------------
    def create_workflow(self, workflow_json):
        """POST /api/v1/workflows. workflow_json must be a dict
        (a valid n8n workflow shape). Returns the created workflow
        as parsed JSON."""
        if not isinstance(workflow_json, dict):
            raise ValueError(
                "create_workflow needs a workflow dict, got "
                f"{type(workflow_json).__name__}")
        return self._request("POST", "/api/v1/workflows",
                             body=workflow_json)

    def list_workflows(self):
        """GET /api/v1/workflows. Returns the parsed response
        (n8n wraps the list as {"data": [...]})."""
        return self._request("GET", "/api/v1/workflows")

    def activate_workflow(self, workflow_id):
        """POST /api/v1/workflows/{id}/activate."""
        wid = _validate_path_segment(workflow_id, "workflow_id")
        return self._request(
            "POST", f"/api/v1/workflows/{wid}/activate", body={})

    def deactivate_workflow(self, workflow_id):
        """POST /api/v1/workflows/{id}/deactivate."""
        wid = _validate_path_segment(workflow_id, "workflow_id")
        return self._request(
            "POST", f"/api/v1/workflows/{wid}/deactivate", body={})

    def get_execution_status(self, execution_id):
        """GET /api/v1/executions/{id}. Returns the execution as
        parsed JSON (carries its status)."""
        eid = _validate_path_segment(execution_id, "execution_id")
        return self._request("GET", f"/api/v1/executions/{eid}")

    # -- webhooks ---------------------------------------------------------
    def trigger_via_webhook(self, path, payload, test=False):
        """POST /webhook/<path> (production) or /webhook-test/<path>
        (test). The shared secret travels as the
        X-Talvenor-Webhook-Secret header when one is configured.
        payload must be a dict. Returns the parsed response."""
        clean = _validate_path_segment(path, "webhook path")
        if not isinstance(payload, dict):
            raise ValueError(
                "trigger_via_webhook needs a payload dict, got "
                f"{type(payload).__name__}")
        prefix = "/webhook-test/" if test else "/webhook/"
        headers = {"Content-Type": "application/json"}
        if self.webhook_secret:
            headers[WEBHOOK_SECRET_HEADER] = self.webhook_secret
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        conn = self._connection()
        try:
            conn.request("POST", prefix + clean, body=data,
                         headers=headers)
            response = conn.getresponse()
            raw = response.read()
        except (http.client.HTTPException, OSError) as exc:
            raise N8nError(
                f"n8n POST {prefix}{clean} failed: "
                f"{type(exc).__name__}") from exc
        finally:
            conn.close()
        if not 200 <= response.status < 300:
            raise N8nError(
                f"n8n POST {prefix}{clean} failed with HTTP "
                f"{response.status}", status=response.status)
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError) as exc:
            raise N8nError(
                f"n8n POST {prefix}{clean}: response is not JSON: "
                f"{exc}", status=response.status) from exc
