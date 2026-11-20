"""MCP client — minimal JSON-RPC 2.0 client over stdio (Phase 9).

Spawns an MCP server as a subprocess (default: this repo's own
mcp_server.py) and speaks newline-delimited JSON-RPC 2.0 to it:
initialize, tools/list, tools/call. No network — stdio only.

To point the client at a REAL MCP server later (see mcp/README.md):
  client = MCPClient("npx", ["-y", "some-mcp-server"], env={...})
  client.initialize()
  client.list_tools()
  client.call_tool("tool-name", {"arg": "value"})

Stdlib only.
"""

import json
import os
import select
import subprocess
import sys

DEFAULT_TIMEOUT = 30


class MCPError(Exception):
    """The server answered with a JSON-RPC error, or the call failed."""


class MCPClient:
    """One MCP server subprocess + JSON-RPC over its stdin/stdout."""

    def __init__(self, command, args=None, env=None, timeout=DEFAULT_TIMEOUT):
        self.command = command
        self.args = list(args or [])
        self.timeout = timeout
        full_env = dict(os.environ)
        if env:
            full_env.update(env)
        self.proc = subprocess.Popen(
            [command] + self.args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1, env=full_env)
        self._next_id = 1
        self._initialized = False

    def _send(self, method, params=None):
        req_id = self._next_id
        self._next_id += 1
        request = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params is not None:
            request["params"] = params
        line = json.dumps(request, ensure_ascii=False) + "\n"
        try:
            self.proc.stdin.write(line)
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise MCPError(f"Cannot write to MCP server: {exc}") from exc
        return self._read_response(req_id)

    def _read_response(self, req_id):
        """Read one response line, with a timeout (never hang forever)."""
        fd = self.proc.stdout.fileno()
        ready, _, _ = select.select([fd], [], [], self.timeout)
        if not ready:
            raise MCPError(
                f"MCP server did not answer within {self.timeout}s "
                f"(request id {req_id}).")
        line = self.proc.stdout.readline()
        if not line:
            raise MCPError("MCP server closed stdout (it may have crashed).")
        try:
            response = json.loads(line)
        except json.JSONDecodeError as exc:
            raise MCPError(f"MCP server sent invalid JSON: {exc}") from exc
        if response.get("id") != req_id:
            raise MCPError(
                f"MCP response id mismatch: got {response.get('id')}, "
                f"expected {req_id}.")
        if "error" in response:
            err = response["error"]
            raise MCPError(
                f"MCP error {err.get('code')}: {err.get('message')}")
        return response.get("result", {})

    def initialize(self):
        """MCP handshake. Returns the server's initialize result."""
        result = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "talvenor-master-os-mcp-client",
                           "version": "0.9.0"},
        })
        self._initialized = True
        return result

    def ping(self):
        return self._send("ping")

    def list_tools(self):
        """Returns the server's tools list: {"tools": [...]}."""
        if not self._initialized:
            self.initialize()
        return self._send("tools/list")

    def call_tool(self, name, arguments=None):
        """Call one tool. Returns the tools/call result dict."""
        if not self._initialized:
            self.initialize()
        return self._send("tools/call",
                          {"name": name,
                           "arguments": arguments or {}})

    def close(self):
        """Stop the server subprocess (terminate, then kill if needed)."""
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=5)
        except Exception:  # noqa: BLE001 — close must never raise
            pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def local_server_client(env=None, timeout=DEFAULT_TIMEOUT):
    """Client pointed at this repo's own mcp_server.py (for tests)."""
    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")
    return MCPClient(sys.executable, [server_path], env=env, timeout=timeout)
