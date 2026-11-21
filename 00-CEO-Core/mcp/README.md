# MCP — Model Context Protocol (Phase 9)

## What is MCP? (in one paragraph)

MCP is a standard plug for an AI agent — just as any device plugs into the same
port via USB, any tool (Gmail, Calendar, n8n, database) plugs into the AI by the
same rules via MCP. The client (the one asking) and the server (the one giving)
talk in JSON-RPC 2.0 — `initialize`, `tools/list`, `tools/call`. This folder holds
the Master OS's own small MCP server + client (stdio, no network): the server
shows the Master OS's 7 mock tools as MCP tools, and the client calls them.

## Running it (entry point)

```bash
python3 scripts/run_mcp_server.py
# same thing:
python3 00-CEO-Core/mcp/mcp_server.py
```

The server speaks JSON-RPC 2.0 on stdio (newline-delimited JSON in/out) —
no network, no daemon; when run, it reads stdin and answers on stdout.
Environment (optional — the default is the real store path):
`TALVENOR_MCP_APPROVALS`, `TALVENOR_MCP_CALLS_LOG`,
`TALVENOR_MCP_LEDGER` (usage-ledger path, $0 receipt). In tests,
all three must be given TEMP paths, so the real store is never touched.

## What is in this folder

- `mcp_server.py` — stdio MCP server: exposes 7 mock tools
  (draft-only). The live-ready gated tools (gmail_send, n8n_trigger)
  are not here — live connections go only through the ApprovalGateway.
- `mcp_client.py` — stdio MCP client: runs the server as a subprocess,
  gives `initialize()` / `list_tools()` / `call_tool()`.
- `check_mcp.py` — self-check: runs the server as a subprocess, then initialize,
  tools/list (exactly 7), tools/call (status_read + draft_email),
  errors on an unknown tool + bad args, ping, no-network, real store
  untouched. It uses TEMP approvals/log paths.
  **Location exception:** this is the only check script not in `scripts/` —
  all other check scripts live in `scripts/`. It stays here because it was built
  as a self-check beside the MCP server; it was not moved (moving it would have
  changed PUSH-PLAN Batch 1 + this README — D15, 2026-11-21).

## Attaching a client to a real MCP server later (key never in a file)

```python
from mcp_client import MCPClient

# Example: a real MCP server (command + env — the key only in env)
client = MCPClient("npx", ["-y", "some-mcp-server"], env={
    "SOME_API_KEY": os.environ["SOME_API_KEY"],  # from env, never in a file
})
client.initialize()
print(client.list_tools())
print(client.call_tool("tool-name", {"arg": "value"}))
client.close()
```

Rule: the server command + env var names may be written in a README, but
a key/token/URL value must never be written in any file — it must come only
from an environment variable.

## Status

- MCP wiring: **CODE — Phase 9** (stdio client + server, self-check).
- Entry point: `scripts/run_mcp_server.py` (2026-11-21) — the one command to
  run the stdio server.
- Live MCP server connection: **NOT CONNECTED** — not yet connected to any
  outside MCP server; it will happen on Boss's decision.
- The brain is still mock — the MCP tools are draft-only, they send nothing.
