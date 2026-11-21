"""Agency engine — tool-calling wrapper (Phase 5).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(ToolRegistry.load_from_json + call_tool). This file only loads the Agency's
tools.json, and forwards call / list_tools — it executes no
tool itself, and does no send/publish/spend.
"""

import importlib.util
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CEO_CORE_DIR = os.path.join(os.path.dirname(os.path.dirname(ENGINE_DIR)), "00-CEO-Core")
CORE_PATH = os.path.join(CEO_CORE_DIR, "tool_calling.py")
TOOLS_PATH = os.path.join(ENGINE_DIR, "tools.json")

# Real ledger default (00-CEO-Core/usage_ledger.py pattern:
# DEFAULT_LEDGER_PATH = <repo>/store/usage_ledger.json) — wrapper calls
# record $0 receipts unless the caller passes its own (e.g. temp) path.
_REPO_DIR = os.path.dirname(os.path.dirname(ENGINE_DIR))
DEFAULT_LEDGER_PATH = os.path.join(_REPO_DIR, "store", "usage_ledger.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — why not plain `import tool_calling`: this wrapper file is also named
# tool_calling.py. If the engine dir is on sys.path, `import tool_calling`
# returns this file itself (partially initialized) instead of the shared core —
# circular import, AttributeError. So the shared core is loaded explicitly from its file path
# (same module, same API).
_spec = importlib.util.spec_from_file_location(
    "agency_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, context=None, approvals_path=None, calls_log_path=None,
         ledger_path=None):
    """Making a tool call — forwarded to the shared core call_tool.

    For a gated tool (send_email / publish_post / spend), the core blocks without approval;
    for a mock tool, the mock handler runs (DRAFT only).
    If owner_words / owner_source are in the context, trust_check verifies them;
    if no ledger_path is given, in the real ledger (store/usage_ledger.json)
    a $0 receipt for every call is written.
    """
    return tool_calling.call_tool(
        name, args, context=context, registry=REGISTRY,
        approvals_path=approvals_path, calls_log_path=calls_log_path,
        ledger_path=ledger_path if ledger_path is not None else DEFAULT_LEDGER_PATH,
    )


def list_tools():
    """List of all tools in the registry."""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if t.get("status") == "mock"]
    print(f"Agency engine tools: {len(tools)} total, {len(mock)} mock, {len(gated)} gated")
    print("Tools:", ", ".join(t.get("name", "?") for t in tools))
    print("Gated (stub, never executes):", ", ".join(t.get("name", "?") for t in gated))
