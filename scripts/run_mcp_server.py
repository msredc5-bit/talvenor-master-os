#!/usr/bin/env python3
"""Run the Talvenor MCP server over stdio (A3, 2026-11-21).

Thin entry point for 00-CEO-Core/mcp/mcp_server.py — same server,
same stdio JSON-RPC, just runnable from scripts/ like the other
runners. The server exposes only the 7 mock tools (draft-only); the
2 live-ready gated tools are NOT listed, and gated calls only record
a PENDING approval — nothing executes.

Usage:
  python3 scripts/run_mcp_server.py
  # (equivalent)
  python3 00-CEO-Core/mcp/mcp_server.py

Environment (optional — defaults are the real store paths):
  TALVENOR_MCP_APPROVALS — approvals JSON path for gated calls
  TALVENOR_MCP_CALLS_LOG — tool-calls log path
  TALVENOR_MCP_LEDGER    — usage-ledger path ($0 receipts)
Set all three to TEMP paths in tests so the real store stays untouched.

Stdlib only. No network — stdio JSON-RPC only. No send, no spend.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MCP_DIR = os.path.join(ROOT, "00-CEO-Core", "mcp")

sys.path.insert(0, MCP_DIR)

import mcp_server  # noqa: E402


def main():
    """Delegate to the real server main() (reads stdin, writes stdout)."""
    return mcp_server.main()


if __name__ == "__main__":
    sys.exit(main())
