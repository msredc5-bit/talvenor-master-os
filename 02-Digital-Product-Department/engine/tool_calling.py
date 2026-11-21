"""Digital Product Engine — tool_calling wrapper (thin).

Shared core: ~/workspace/talvenor-master-os/00-CEO-Core/tool_calling.py
(ToolRegistry.load_from_json + call_tool) — this wrapper only loads this
engine's tools.json and forwards calls. It runs no tool itself and executes
no gated action.

Gate 0 NOT PASSED — sell_kit stub, handler null; calling it is caught by the
shared core's gate (blocked-gate0 / pending-approval).
launch_kit: MOCK draft handler (sweep 2026-11-21) — only returns a launch-checklist
DRAFT, launch_blocked: true; it never launches.
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
DEPT_DIR = os.path.dirname(ENGINE_DIR)
GATE0_STATUS_PATH = os.path.join(DEPT_DIR, "gate0-status.md")
_MASTER_OS_DIR = os.path.dirname(os.path.dirname(ENGINE_DIR))
STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_LEDGER_PATH = os.path.join(STORE_DIR, "usage_ledger.json")

sys.path.insert(0, CEO_CORE_DIR)

# NOTE — why not plain `import tool_calling`: this wrapper file is also named
# tool_calling.py. If the engine dir is on sys.path, `import tool_calling`
# returns this file itself (partially initialized) instead of the shared core —
# a circular import, AttributeError. So the shared core is loaded explicitly
# from its file path (same module, same API).
_spec = importlib.util.spec_from_file_location(
    "products_engine_core_tool_calling", CORE_PATH
)
tool_calling = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool_calling)


# ---------------------------------------------------------------------------
# Dept-local mock handler — launch_kit (sweep 2026-11-21).
# HANDLERS pattern (00-CEO-Core/tool_calling.py): fn(args, context) ->
# {"output": str, "notes": [str]}. Returns the SAME launch-checklist DRAFT
# the Chief's launch_prep returns (Gate 0, 6 kit parts, Gate 1, listings,
# sales page, 25/day mail plan) with launch_blocked: true — a draft
# checklist, never a launch. Registered into this wrapper's loaded copy
# of the shared core (00-CEO-Core/tool_calling.py is NOT edited).
# ---------------------------------------------------------------------------

LAUNCH_CHECKLIST_DRAFT = [
    "Gate 0 passed (does the Lemon Squeezy store open?) — still NOT PASSED",
    "The kit's 6 parts built (Sheets + Docs + script) — not done yet",
    "Cadence checked against AAHA/PetDesk guidance (Gate 1) — not done yet",
    "Lemon Squeezy listing + Gumroad backup listing — not done yet",
    "Sales page — Boss will review before launch",
    "Email 100 clinics, 25 a day (4 days) — email channel is now PAUSED",
]


def _read_gate0_status():
    """Reads the Status line of gate0-status.md — NOT PASSED unless
    PASSED is written (fail-closed)."""
    try:
        with open(GATE0_STATUS_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except (FileNotFoundError, OSError):
        return "NOT PASSED"
    for line in lines:
        stripped = line.strip().lstrip("*").strip()
        if stripped.startswith("Status:"):
            value = stripped[len("Status:"):].strip().lstrip("*").strip()
            return "PASSED" if value.startswith("PASSED") else "NOT PASSED"
    return "NOT PASSED"


def launch_kit(args, context=None):
    """Launch-checklist DRAFT — does not launch, launch_blocked: true."""
    gate0 = _read_gate0_status()
    checklist = "\n".join(
        "  %d. %s" % (i, item)
        for i, item in enumerate(LAUNCH_CHECKLIST_DRAFT, 1))
    output = (
        "[DRAFT ONLY — never launched] Launch checklist — "
        "Vet No-Show Recovery Kit ($49 one-time)\n"
        + checklist + "\n"
        f"Gate 0: {gate0}. Kit built: 0/6. PA list: 39/100. Sale: 0.\n"
        "launch_blocked: true — launch is blocked until Gate 0 passes. "
        "This is a DRAFT checklist, not a launch.")
    notes = [
        "DRAFT ONLY — launch checklist, never a launch.",
        "launch_blocked: true",
        f"Gate 0: {gate0} (read from gate0-status.md).",
        "No sale recorded — sales are still 0.",
    ]
    return {"output": output, "notes": notes}


tool_calling.HANDLERS["launch_kit"] = launch_kit

REGISTRY = tool_calling.ToolRegistry.load_from_json(TOOLS_PATH)


def call(name, args, approvals_path=None, calls_log_path=None, ledger_path=None):
    """Makes one tool call — forwards to the shared core's call_tool.

    If ledger_path is not given, the real default store/usage_ledger.json is used
    (a $0.00 receipt is written for every call); for a TEMP ledger the caller
    passes ledger_path."""
    return tool_calling.call_tool(
        name, args, registry=REGISTRY,
        approvals_path=approvals_path, calls_log_path=calls_log_path,
        ledger_path=ledger_path if ledger_path is not None else DEFAULT_LEDGER_PATH,
    )


def list_tools():
    """Returns the list of all the engine's tools."""
    return REGISTRY.list_tools()


if __name__ == "__main__":
    import tempfile

    tools = list_tools()
    gated = [t for t in tools if t.get("gated")]
    mock = [t for t in tools if not t.get("gated")]
    print("Digital Product Engine tools:", len(tools))
    print("Gated (stub):", len(gated))
    print("Mock:", len(mock))
    # TEMP files only — the real approvals/calls log is not touched.
    tmp = tempfile.mkdtemp()
    print("Temp dir (test only):", tmp)
    print("Tools:", ", ".join(sorted(t.get("name", "?") for t in tools)))
