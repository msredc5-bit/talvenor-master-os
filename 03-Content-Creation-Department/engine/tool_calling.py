"""Content Engine — tool-calling wrapper (thin, Phase 5).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(parallel build) — এখানে কোনো tool logic নেই, শুধু forward করা হয়।
এই engine-এর নিজের registry: এই folder-এর tools.json।

নিয়ম:
  - Gated tool (publish_post, upload_video, spend) — core-এর
    ApprovalGateway দিয়ে আটকে থাকে; এই wrapper কখনো publish /
    upload / spend করে না।
  - Mock tool (draft_script, draft_caption, draft_email,
    research_notes, status_read) — DRAFT ONLY, [MOCK DRAFT]।
  - Stdlib only, no network, no pip। কোনো file লেখা হয় না —
    approvals / calls log-এর path caller দিলে core সেটা ব্যবহার করে।
"""

import importlib.util
import json
import os
import sys

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
CEO_CORE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(ENGINE_DIR)), "00-CEO-Core"
)
CORE_PATH = os.path.join(CEO_CORE_DIR, "tool_calling.py")
TOOLS_PATH = os.path.join(ENGINE_DIR, "tools.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — কেন plain `import tool_calling` নয়: এই wrapper file-এর নামও
# tool_calling.py। Engine dir sys.path-এ থাকলে `import tool_calling`
# shared core-এর বদলে এই file-কেই (partially initialized) ফেরত দেয় —
# circular import, AttributeError। তাই shared core-কে তার file path
# থেকে explicit ভাবে load করা হয় (একই module, একই API:
# ToolRegistry.load_from_json + call_tool)। sys.path insert-টা
# contract অনুযায়ী রাখা হয়েছে — core-এর নিজের relative import-এর জন্য।
_spec = importlib.util.spec_from_file_location(
    "content_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, approvals_path=None, calls_log_path=None):
    """একটা tool call করো — shared core-এ forward করা হয়।

    name: tools.json-এর tool name (যেমন "draft_script")।
    args: dict — tool-এর params অনুযায়ী।
    approvals_path / calls_log_path: caller দিলে core সেটা ব্যবহার
    করে; না দিলে core-এর default।
    Returns: core-এর call_tool-এর result (dict)।
    Gated tool-এ approval না থাকলে core PENDING ফেরত দেয় — কিছু
    publish/upload/spend হয় না।
    """
    return tool_calling.call_tool(
        name,
        args,
        registry=REGISTRY,
        approvals_path=approvals_path,
        calls_log_path=calls_log_path,
    )


def list_tools():
    """Registry-র সব tool-এর list ফেরত দেয়।"""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if not t.get("gated")]
    print(f"Content Engine tools: {len(tools)} (mock: {len(mock)}, gated: {len(gated)})")
    print("Mock:", ", ".join(t.get("name", "?") for t in mock))
    print("Gated:", ", ".join(t.get("name", "?") for t in gated))
    print("NOTE: এই run-এ কোনো tool call করা হয়নি, কোনো file লেখা হয়নি — শুধু count ছাপা হয়েছে।")
