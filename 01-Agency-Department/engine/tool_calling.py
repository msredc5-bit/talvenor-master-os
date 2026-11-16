"""Agency engine — tool-calling wrapper (Phase 5).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(ToolRegistry.load_from_json + call_tool)। এই ফাইল শুধু Agency-র
tools.json-টা load করে, আর call / list_tools forward করে — নিজে কোনো
tool execute করে না, কোনো send/publish/spend করে না।
"""

import importlib.util
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CEO_CORE_DIR = os.path.join(os.path.dirname(os.path.dirname(ENGINE_DIR)), "00-CEO-Core")
CORE_PATH = os.path.join(CEO_CORE_DIR, "tool_calling.py")
TOOLS_PATH = os.path.join(ENGINE_DIR, "tools.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — কেন plain `import tool_calling` নয়: এই wrapper file-এর নামও
# tool_calling.py। Engine dir sys.path-এ থাকলে `import tool_calling`
# shared core-এর বদলে এই file-কেই (partially initialized) ফেরত দেয় —
# circular import, AttributeError। তাই shared core-কে তার file path
# থেকে explicit ভাবে load করা হয় (একই module, একই API)।
_spec = importlib.util.spec_from_file_location(
    "agency_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, approvals_path=None, calls_log_path=None):
    """একটা tool call করা — shared core-এর call_tool-এ forward করা হয়।

    Gated tool (send_email / publish_post / spend) হলে core approval
    ছাড়া আটকে দেয়; mock tool হলে mock handler চলে (DRAFT only)।
    """
    return tool_calling.call_tool(
        name, args, registry=REGISTRY,
        approvals_path=approvals_path, calls_log_path=calls_log_path,
    )


def list_tools():
    """Registry-র সব tool-এর তালিকা।"""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if t.get("status") == "mock"]
    print(f"Agency engine tools: {len(tools)} total, {len(mock)} mock, {len(gated)} gated")
    print("Tools:", ", ".join(t.get("name", "?") for t in tools))
    print("Gated (stub, never executes):", ", ".join(t.get("name", "?") for t in gated))
