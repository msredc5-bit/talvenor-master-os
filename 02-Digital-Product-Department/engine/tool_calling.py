"""Digital Product Engine — tool_calling wrapper (thin).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(ToolRegistry.load_from_json + call_tool) — এই wrapper শুধু এই engine-এর
tools.json load করে আর call forward করে। নিজে কোনো tool চালায় না, কোনো
gated action execute করে না।

Gate 0 NOT PASSED — launch_kit / sell_kit stub, handler null; call করলে
shared core-এর gate-এ আটকাবে (blocked-gate0 / pending-approval)।
"""

import importlib.util
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CEO_CORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(ENGINE_DIR)),
    "00-CEO-Core",
)
CORE_PATH = os.path.join(CEO_CORE_DIR, "tool_calling.py")
TOOLS_PATH = os.path.join(ENGINE_DIR, "tools.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — কেন plain `import tool_calling` নয়: এই wrapper file-এর নামও
# tool_calling.py। Engine dir sys.path-এ থাকলে `import tool_calling`
# shared core-এর বদলে এই file-কেই (partially initialized) ফেরত দেয় —
# circular import, AttributeError। তাই shared core-কে তার file path
# থেকে explicit ভাবে load করা হয় (একই module, একই API)।
_spec = importlib.util.spec_from_file_location(
    "products_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, approvals_path=None, calls_log_path=None):
    """একটা tool call করা — shared core-এর call_tool-এ forward করে।"""
    return tool_calling.call_tool(
        name, args, registry=REGISTRY,
        approvals_path=approvals_path, calls_log_path=calls_log_path,
    )


def list_tools():
    """Engine-এর সব tool-এর তালিকা ফেরত দেয়।"""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    import tempfile

    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if not t.get("gated")]
    print("Digital Product Engine tools:", len(tools))
    print("Gated (stub, blocked-gate0):", len(gated))
    print("Mock:", len(mock))
    # TEMP files only — আসল approvals/calls log ছোঁয়া হয় না।
    tmp = tempfile.mkdtemp()
    print("Temp dir (test only):", tmp)
    print("Tools:", ", ".join(sorted(t.get("name", "?") for t in tools)))
