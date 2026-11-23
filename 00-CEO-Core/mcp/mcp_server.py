#!/usr/bin/env python3
"""MCP server — Talvenor Master OS tools over MCP stdio (Phase 9).

Minimal MCP (Model Context Protocol) JSON-RPC 2.0 server over stdio:
newline-delimited JSON in, newline-delimited JSON out. No network.

Methods:
  initialize   -> protocol version + server info
  ping         -> empty result (liveness)
  tools/list   -> the 7 mock tools from tools.json (draft-only)
  tools/call   -> dispatch one mock tool via tool_calling.call_tool

Only the 7 mock tools are exposed. The 2 live-ready gated tools
(gmail_send, n8n_trigger) are NOT listed here — a live connection
must go through the ApprovalGateway, never through MCP.

Environment (optional — defaults are the real store paths):
  TALVENOR_MCP_APPROVALS   — approvals JSON path for gated calls
  TALVENOR_MCP_CALLS_LOG   — tool-calls log path
  TALVENOR_MCP_LEDGER      — usage-ledger path ($0 receipts; every
                             call_tool call writes one receipt here)
Set all three to TEMP paths in tests so the real store stays untouched.

Stdlib only. Run: python3 00-CEO-Core/mcp/mcp_server.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tool_calling  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_JSON = os.path.join(BASE, "00-CEO-Core", "tools.json")
CONFIG_JSON = os.path.join(BASE, "00-CEO-Core", "config.json")
DEFAULT_LEDGER_PATH = os.path.join(BASE, "store", "usage_ledger.json")

PROTOCOL_VERSION = "2024-11-05"


def _config_version():
    try:
        with open(CONFIG_JSON, encoding="utf-8") as f:
            return json.load(f).get("version", "unknown")
    except (OSError, ValueError):
        return "unknown"


def _mock_tools(registry):
    """Only the 7 mock (draft-only) tools — live-ready tools excluded."""
    return [t for t in registry.list_tools() if t.get("status") == "mock"]


def _error(code, message, req_id):
    return {"jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message}}


def _result(result, req_id):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def handle(request, registry):
    """One JSON-RPC request dict -> response dict (or None for notifications)."""
    if not isinstance(request, dict):
        return _error(-32600, "Invalid Request: expected an object.", None)
    method = request.get("method")
    req_id = request.get("id")
    is_notification = "id" not in request
    params = request.get("params") or {}
    if not isinstance(params, dict):
        return _error(-32602, "Invalid params: expected an object.", req_id)

    if method == "initialize":
        return _result({
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "talvenor-master-os-mcp",
                "version": _config_version(),
            },
        }, req_id)

    if method == "ping":
        return _result({}, req_id)

    if method == "tools/list":
        tools = [{
            "name": t["name"],
            "description": t["description"],
            "inputSchema": t["params"],
        } for t in _mock_tools(registry)]
        return _result({"tools": tools}, req_id)

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        if not isinstance(name, str) or not name:
            return _error(-32602, "tools/call needs a 'name' string.", req_id)
        if not isinstance(arguments, dict):
            return _error(-32602, "tools/call 'arguments' must be an object.",
                          req_id)
        try:
            registry.get(name)
        except KeyError:
            return _result({
                "content": [{"type": "text",
                             "text": f"Unknown tool {name!r}."}],
                "isError": True,
            }, req_id)
        result = tool_calling.call_tool(
            name, arguments, registry=registry,
            # Phase 1 (Unified OS): an MCP client may identify its agent
            # ("agent": "<agent key>" in the call params) — then the
            # permission allowlist is enforced. Without it, the legacy
            # dispatcher path applies (see permissions.py).
            context=({"agent": params["agent"]}
                     if isinstance(params.get("agent"), str)
                     and params["agent"].strip() else None),
            approvals_path=os.environ.get("TALVENOR_MCP_APPROVALS"),
            calls_log_path=os.environ.get("TALVENOR_MCP_CALLS_LOG"),
            ledger_path=os.environ.get("TALVENOR_MCP_LEDGER",
                                       DEFAULT_LEDGER_PATH))
        is_error = result.get("status") == "error"
        return _result({
            "content": [{"type": "text",
                         "text": json.dumps(result, ensure_ascii=False)}],
            "isError": is_error,
        }, req_id)

    if is_notification:
        return None  # notifications get no response
    return _error(-32601, f"Method not found: {method!r}.", req_id)


def main():
    try:
        registry = tool_calling.ToolRegistry.load_from_json(TOOLS_JSON)
    except Exception as exc:  # noqa: BLE001 — fail loudly, never silent
        sys.stderr.write(f"mcp_server: cannot load tools.json: {exc}\n")
        return 1
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(
                _error(-32700, "Parse error: not valid JSON.", None),
                ensure_ascii=False) + "\n")
            sys.stdout.flush()
            continue
        if isinstance(request, list):
            sys.stdout.write(json.dumps(
                _error(-32600, "Batch requests are not supported.", None),
                ensure_ascii=False) + "\n")
            sys.stdout.flush()
            continue
        try:
            response = handle(request, registry)
        except Exception as exc:  # noqa: BLE001 — one bad call never kills the server
            response = _error(-32603, f"Internal error: {exc}",
                              request.get("id") if isinstance(request, dict) else None)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
