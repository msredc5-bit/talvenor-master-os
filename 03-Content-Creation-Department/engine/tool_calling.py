"""Content Engine — tool-calling wrapper (thin, Phase 5).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(parallel build) — there is no tool logic here, only forwarding.
This engine's own registry: this folder's tools.json.

Rules:
  - Gated tools (upload_video, spend) — held by the core's
    ApprovalGateway; this wrapper never publishes /
    uploads / spends.
  - Mock tool (draft_script, draft_caption, draft_email,
    research_notes, status_read, publish_post) — DRAFT ONLY, [MOCK DRAFT].
    publish_post: PublishPrep checklist DRAFT (ready_to_publish: false),
    never a publish (sweep 2026-11-21).
  - Stdlib only, no network, no pip. No file is written —
    if the caller gives an approvals / calls log path, the core uses it.
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
_MASTER_OS_DIR = os.path.dirname(os.path.dirname(ENGINE_DIR))
STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_LEDGER_PATH = os.path.join(STORE_DIR, "usage_ledger.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — why not a plain `import tool_calling`: this wrapper file is also named
# tool_calling.py. If the engine dir is on sys.path, `import tool_calling`
# returns this file itself (partially initialized) instead of the shared core —
# circular import, AttributeError. So the shared core is loaded explicitly from its file path
# (same module, same API:
# ToolRegistry.load_from_json + call_tool). The sys.path insert is
# kept per contract — for the core's own relative imports.
_spec = importlib.util.spec_from_file_location(
    "content_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)


# ---------------------------------------------------------------------------
# Dept-local mock handler — publish_post (sweep 2026-11-21).
# HANDLERS pattern (00-CEO-Core/tool_calling.py): fn(args, context) ->
# {"output": str, "notes": [str]}. Returns the PublishPrep checklist DRAFT
# for the given post_id (hook, readable text, no invented claim, platform,
# best posting time) with ready_to_publish: false — a prep checklist,
# never a publish. Registered into this wrapper's loaded copy of the
# shared core (00-CEO-Core/tool_calling.py is NOT edited).
# ---------------------------------------------------------------------------

PUBLISH_PREP_CHECKLIST_DRAFT = [
    "Hook — is there a hook in the first line",
    "Readable text — is the on-screen text short, verbatim, readable",
    "No invented claim — no made-up client / stat / testimonial / price",
    "Platform — Facebook / Instagram / LinkedIn, which one it goes to",
    "Best posting time — set in US Eastern time",
]


def publish_post(args, context=None):
    """Publish-prep checklist DRAFT — does not publish, ready_to_publish: false."""
    post_id = (args.get("post_id") or "").strip()
    platform = (args.get("platform") or "").strip()
    checklist = "\n".join(
        "  %d. %s" % (i, item)
        for i, item in enumerate(PUBLISH_PREP_CHECKLIST_DRAFT, 1))
    output = (
        "[DRAFT ONLY — never published] Publish-prep checklist"
        + (f" — post_id: {post_id}" if post_id else "")
        + (f" — platform: {platform}" if platform else "")
        + "\n" + checklist + "\n"
        "ready_to_publish: false — upload stage 9 OFF. To publish, "
        "Boss's gate word is needed: 'post it' (for video upload "
        "'upload it'), and Boss does that himself.")
    notes = [
        "DRAFT ONLY — publish-prep checklist, never a publish.",
        "ready_to_publish: false",
        "Upload stage 9 OFF — this engine never runs upload_youtube.py.",
    ]
    return {"output": output, "notes": notes}


tool_calling.HANDLERS["publish_post"] = publish_post

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, approvals_path=None, calls_log_path=None, ledger_path=None):
    """Make one tool call — forwarded to the shared core.

    name: tool name in tools.json (e.g. "draft_script").
    args: dict — per the tool's params.
    approvals_path / calls_log_path: if the caller gives them, the core uses them;
    otherwise the core's defaults.
    ledger_path: if not given, the real default store/usage_ledger.json is used
    ($0.00 receipt written on each call); for a TEMP ledger the
    caller passes ledger_path.
    Returns: the core's call_tool result (dict).
    Without approval on a gated tool, the core returns PENDING — nothing is
    published/uploaded/spent.
    """
    return tool_calling.call_tool(
        name,
        args,
        registry=REGISTRY,
        approvals_path=approvals_path,
        calls_log_path=calls_log_path,
        ledger_path=ledger_path if ledger_path is not None else DEFAULT_LEDGER_PATH,
    )


def list_tools():
    """Returns the list of all tools in the registry."""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if not t.get("gated")]
    print(f"Content Engine tools: {len(tools)} (mock: {len(mock)}, gated: {len(gated)})")
    print("Mock:", ", ".join(t.get("name", "?") for t in mock))
    print("Gated:", ", ".join(t.get("name", "?") for t in gated))
    print("NOTE: no tool call was made in this run, no file was written — only the count was printed.")
