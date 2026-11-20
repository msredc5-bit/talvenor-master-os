#!/usr/bin/env python3
"""check_mcp.py — Phase 9 self-check for the MCP client + server.

What it checks (stdio only, no network, no real send):
  1. initialize: server answers with protocolVersion + serverInfo.
  2. tools/list: exactly the 7 mock tools, expected names — the 2
     live-ready gated tools (gmail_send, n8n_trigger) are NOT listed.
  3. tools/call status_read: draft-ready, phase matches config.json.
  4. tools/call draft_email: draft-ready, booking link in the output.
  5. tools/call unknown tool: isError true, nothing crashes.
  6. tools/call bad args (missing required field): isError true.
  7. No network in the MCP files (AST scan: no socket/urllib/requests).
  8. Real store untouched by this check (snapshot before/after).

The server runs as a subprocess with TEMP approvals/log paths, so the
real store is never written. Run: python3 00-CEO-Core/mcp/check_mcp.py
"""

import ast
import json
import os
import sys
import tempfile

MCP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(MCP_DIR))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
CONFIG_JSON = os.path.join(CEO_CORE_DIR, "config.json")
STORE_DIR = os.path.join(BASE, "store")

sys.path.insert(0, MCP_DIR)
sys.path.insert(0, CEO_CORE_DIR)

from mcp_client import MCPClient, MCPError, local_server_client  # noqa: E402

CHECKS = []
EXPECTED_TOOLS = {
    "draft_email", "research_notes", "draft_caption", "draft_script",
    "kit_outline_read", "status_read", "booking_reply",
}


def check(name, ok, detail=""):
    CHECKS.append(ok)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def _snapshot_store():
    snap = {}
    for name in ("tasks.json", "approvals.json"):
        try:
            with open(os.path.join(STORE_DIR, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["tool_calls"] = os.path.exists(
        os.path.join(STORE_DIR, "tool_calls.json"))
    return snap


def _call_text(result):
    """tools/call result -> the text payload (first content item)."""
    content = result.get("content") or []
    if content and isinstance(content[0], dict):
        return content[0].get("text", "")
    return ""


def main():
    with open(CONFIG_JSON, encoding="utf-8") as f:
        config_phase = json.load(f).get("phase")

    tmp = tempfile.mkdtemp()
    env = {
        "TALVENOR_MCP_APPROVALS": os.path.join(tmp, "approvals-test.json"),
        "TALVENOR_MCP_CALLS_LOG": os.path.join(tmp, "tool_calls-test.json"),
    }
    store_before = _snapshot_store()

    try:
        with local_server_client(env=env) as client:
            # 1. initialize
            try:
                init = client.initialize()
                ok = (init.get("protocolVersion") == "2024-11-05"
                      and init.get("serverInfo", {}).get("name")
                      == "talvenor-master-os-mcp")
                check("initialize: protocolVersion + serverInfo", ok,
                      f"version={init.get('protocolVersion')}, "
                      f"server={init.get('serverInfo', {}).get('name')}")
            except MCPError as e:
                check("initialize: protocolVersion + serverInfo", False, str(e))

            # 2. tools/list — exactly 7 mock tools, no live-ready tools
            try:
                listed = client.list_tools()
                names = {t["name"] for t in listed.get("tools", [])}
                ok = (names == EXPECTED_TOOLS
                      and "gmail_send" not in names
                      and "n8n_trigger" not in names)
                check("tools/list: exactly 7 mock tools, no live-ready",
                      ok, f"names={sorted(names)}")
            except MCPError as e:
                check("tools/list: exactly 7 mock tools, no live-ready",
                      False, str(e))

            # 3. tools/call status_read — draft-ready, phase matches config
            try:
                result = client.call_tool("status_read", {})
                payload = json.loads(_call_text(result))
                ok = (result.get("isError") is False
                      and payload.get("status") == "draft-ready"
                      and json.loads(payload.get("output", "{}")).get("phase")
                      == config_phase)
                check("tools/call status_read: draft-ready, real phase",
                      ok, f"status={payload.get('status')}, "
                      f"phase={config_phase}")
            except (MCPError, ValueError) as e:
                check("tools/call status_read: draft-ready, real phase",
                      False, str(e))

            # 4. tools/call draft_email — draft-ready, booking link present
            try:
                result = client.call_tool(
                    "draft_email",
                    {"business_name": "ABC Plumbing",
                     "topic": "missed calls"})
                payload = json.loads(_call_text(result))
                ok = (payload.get("status") == "draft-ready"
                      and "calendar.app.google" in payload.get("output", ""))
                check("tools/call draft_email: draft-ready + booking link",
                      ok, f"status={payload.get('status')}")
            except (MCPError, ValueError) as e:
                check("tools/call draft_email: draft-ready + booking link",
                      False, str(e))

            # 5. tools/call unknown tool — isError, server stays alive
            try:
                result = client.call_tool("no_such_tool", {})
                ok = result.get("isError") is True
                check("tools/call unknown tool: isError, server alive",
                      ok, f"isError={result.get('isError')}")
            except MCPError as e:
                check("tools/call unknown tool: isError, server alive",
                      False, str(e))

            # 6. tools/call bad args — isError (missing required field)
            try:
                result = client.call_tool("draft_email", {})
                ok = result.get("isError") is True
                check("tools/call bad args: isError (missing field)",
                      ok, f"isError={result.get('isError')}")
            except MCPError as e:
                check("tools/call bad args: isError (missing field)",
                      False, str(e))

            # 7. ping still works after errors (server didn't die)
            try:
                client.ping()
                check("ping after errors: server still alive", True)
            except MCPError as e:
                check("ping after errors: server still alive", False, str(e))
    except Exception as e:  # noqa: BLE001
        check("MCP client/server session", False, str(e))

    # 8. No network in the MCP files (AST scan)
    try:
        forbidden = set()
        for fname in ("mcp_client.py", "mcp_server.py"):
            path = os.path.join(MCP_DIR, fname)
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.split(".")[0] in (
                                "socket", "urllib", "requests", "http"):
                            forbidden.add(f"{fname}:{alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if (node.module or "").split(".")[0] in (
                            "socket", "urllib", "requests", "http"):
                        forbidden.add(f"{fname}:{node.module}")
        check("no network in MCP files (stdio only)",
              not forbidden,
              "; ".join(sorted(forbidden)) if forbidden else "clean")
    except Exception as e:  # noqa: BLE001
        check("no network in MCP files (stdio only)", False, str(e))

    # 9. Real store untouched by this check
    try:
        after = _snapshot_store()
        check("real store untouched by this check",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store untouched by this check", False, str(e))

    total = len(CHECKS)
    passed = sum(1 for c in CHECKS if c)
    print(f"\ncheck_mcp: {passed}/{total} PASS")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
