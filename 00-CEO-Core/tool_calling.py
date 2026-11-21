"""Shared Tool-Calling Core — Talvenor Master OS (Phase 5).

What this file is:
  The Master OS's three departments (Agency, Digital Product, Content) —
  all run on the same tool-calling rules. A tool means a name + what
  arguments it needs + whether it is gated + whether it is mock / real / stub.
  Engine wrappers import this file to build a ToolRegistry, and run tools
  with call_tool().

Gate rules (Boss's decision, written in code):
  - A gated tool (send / publish / spend / delete) never executes.
    call_tool() first runs trust_gate.trust_check() (Improvement
    Phase 1 — Nod pattern): if a standing rule (spend cap $0, dental/medical
    DQ) refuses, status is "blocked-trust" — no approval is recorded either.
    Otherwise it writes one PENDING approval request to the ApprovalGateway and
    stops. Even with an approval ID — Boss does gated work himself; this
    dispatcher only records the request. Even when trust says "allow", the gateway
    is the final authority — nothing moves without Boss's exact gate word.
  - Gate words: ok / "post it" / "upload it" / send / go — nothing moves without
    Boss's exact word. There is no auto-approve path.
  - Gate words: ok / "post it" / "upload it" / send / go — nothing moves without
    Boss's exact word. There is no auto-approve path.
  - Spend limit $0. Paying clients 0. Email PAUSED. Gate 0 NOT PASSED.
    Upload OFF. No invented clients / numbers / testimonials / prices.
    Not dental / medical. Brand is Talvenor only.

7 mock handlers (all DRAFT ONLY — nothing is sent / published / spent):
  1. draft_email      — cold-email draft (Talvenor brand line + booking link)
  2. research_notes   — research-notes template, every field "TO VERIFY"
  3. draft_caption    — social caption draft, first line is the hook
  4. draft_script     — short video script outline (hook, problem, solution, CTA)
  5. kit_outline_read — reads the real kit-outline.md file (not invented content)
  6. status_read      — reads the real config.json (honest status, phase, spend cap)
  7. booking_reply    — given a lead's name, a one-line reply draft with the booking link
                        (Boss's 2026-11-17 question's example tool — DRAFT ONLY)

2 live-ready handlers (Phase 9 — live_tools.py, CODE ONLY, gated):
  8. gmail_send       — real mail via hatch_gws_cli (LOUD DRAFT fallback without a
                        credential; the dispatcher never runs the handler)
  9. n8n_trigger      — n8n webhook via urllib POST (LOUD DRAFT fallback without a
                        credential; the URL is never printed in full)
  A live-ready tool's status is "live-ready" — after the gated intercept in the
  dispatcher there is no direct execution path (fail-closed). This module has no
  subprocess / urlopen calls — live execution is not in Phase 9.

Usage:
  import tool_calling
  registry = tool_calling.ToolRegistry.load_from_json("tools.json")
  result = tool_calling.call_tool("draft_email",
      {"business_name": "ABC Plumbing", "topic": "missed calls"},
      registry=registry)
  # result["status"] = "draft-ready" | "pending-approval" | "blocked-stub" | "error"

Stdlib only — no network, no pip.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_approval_gateway import GATED_ACTIONS, ApprovalGateway  # noqa: E402
from live_tools import LIVE_HANDLERS  # noqa: E402
from trust_gate import trust_check  # noqa: E402
from usage_ledger import UsageLedger  # noqa: E402

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_CALLS_LOG_PATH = os.path.join(_STORE_DIR, "tool_calls.json")
KIT_OUTLINE_PATH = os.path.join(
    _MASTER_OS_DIR, "02-Digital-Product-Department", "kit-outline.md"
)
CONFIG_PATH = os.path.join(_MASTER_OS_DIR, "00-CEO-Core", "config.json")

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"
BRAND_LINE = "You run the jobs. We run the phone."
DRAFT_LABEL = "DRAFT ONLY — never sent"

_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Mock handlers — each fn(args, context) -> {"output": str, "notes": [str]}
# No handler goes to the network, nothing sends / publishes / spends.
# A file-reading handler (kit_outline_read, status_read) returns
# {"error": ...} if the file is missing — never invented content.
# ---------------------------------------------------------------------------

def draft_email(args, context=None):
    """DRAFT cold-email body — Talvenor brand line + booking link, no price."""
    business = args.get("business_name", "")
    topic = args.get("topic", "")
    output = (
        f"[DRAFT ONLY — never sent] Subject: Missed calls at {business}?\n\n"
        f"Hi {business} team,\n\n"
        f"{BRAND_LINE}\n\n"
        f"When a customer calls about {topic} and nobody picks up, "
        "that job usually goes to the next plumber on the list. "
        "Talvenor's AI receptionist answers every call, 24/7, books the job, "
        "and hands it to you — so no call is ever missed.\n\n"
        f"Want to hear how it sounds? Book a 15-minute demo call here: {BOOKING_LINK}\n\n"
        "Thanks,\n"
        "Talvenor — AI receptionist for service businesses"
    )
    notes = [
        DRAFT_LABEL,
        "No prices, no invented statistics, no invented client claims.",
        "Email sending is PAUSED — this draft was never sent.",
    ]
    return {"output": output, "notes": notes}


def research_notes(args, context=None):
    """DRAFT research-notes template — every field still to verify."""
    business = args.get("business_name", "")
    output = (
        f"Research notes (DRAFT) — {business}\n"
        "1. Business name: TO VERIFY — do not present as fact\n"
        "2. Services offered: TO VERIFY — do not present as fact\n"
        "3. Service area / city: TO VERIFY — do not present as fact\n"
        "4. Phone answered? (missed-call signal): TO VERIFY — do not present as fact\n"
        "5. Website / Google listing: TO VERIFY — do not present as fact\n"
        "6. Owner name: TO VERIFY — do not present as fact\n"
        "7. Contact email: TO VERIFY — do not present as fact (never guess an email)\n"
        "8. Why they may need a receptionist: TO VERIFY — do not present as fact"
    )
    notes = [
        "DRAFT ONLY — template, not researched facts.",
        "Every field is marked TO VERIFY — do not present as fact.",
    ]
    return {"output": output, "notes": notes}


def draft_caption(args, context=None):
    """DRAFT social caption — first line is the hook."""
    topic = args.get("topic", "")
    platform = args.get("platform", "")
    output = (
        f"[DRAFT ONLY — never published] {topic} — and nobody picked up the phone.\n\n"
        f"{BRAND_LINE}\n\n"
        "Talvenor's AI receptionist answers every call, 24/7, and books the job "
        "while you're still on the last one.\n\n"
        "Book a call with Talvenor. Link in bio."
    )
    notes = [
        "DRAFT ONLY — never published.",
        f"Platform: {platform}. First line is the hook.",
        "No prices, no invented statistics, no invented client claims.",
    ]
    return {"output": output, "notes": notes}


def draft_script(args, context=None):
    """DRAFT short video script outline — hook, problem, solution, CTA."""
    topic = args.get("topic", "")
    duration = args.get("duration_seconds", args.get("duration_sec", ""))
    topic_lower = topic.lower()
    if "talvenor" in topic_lower or "receptionist" in topic_lower:
        solution = "Talvenor's AI receptionist answers 24/7, books the job, and hands it to you."
        cta = "Book a call with Talvenor. Link in bio."
    else:
        solution = f"Show how {topic} works, step by step, with a real on-screen test."
        cta = "End with a clear call to action for the viewer (subscribe / learn more — per the brief)."
    output = (
        f"Video script outline (DRAFT) — {topic} ({duration}s)\n"
        f"1. HOOK (first 2 seconds): Open on the problem — {topic}.\n"
        f"2. PROBLEM: The viewer struggles with {topic} and needs a clear answer.\n"
        f"3. SOLUTION: {solution}\n"
        f"4. CTA: {cta}"
    )
    notes = [
        "DRAFT ONLY — script not final.",
        "VOICE.md DRAFT — script not final until Boss corrects VOICE.md.",
        "No invented clients, statistics, or testimonials.",
    ]
    return {"output": output, "notes": notes}


def booking_reply(args, context=None):
    """Given a lead's name, a one-line reply DRAFT with the booking link.

    Boss's example tool (2026-11-17, 02:43 Dhaka — "How do you create a tool
    with GitHub?"): input is only the lead's name, output is one line of reply
    + booking link. DRAFT ONLY — never sent; to send it needs the gated
    send_email tool + Boss's exact gate word. No price,
    no invented clients / numbers / testimonials.
    """
    lead_name = (args.get("lead_name") or "").strip()
    channel = (args.get("channel") or "email").strip().lower()
    if not lead_name:
        return {
            "output": "",
            "notes": ["DRAFT ONLY — no lead name was given."],
            "error": "booking_reply needs a lead_name.",
        }
    if channel == "instagram":
        cta = "Book a call with Talvenor. Link in bio."
    else:
        cta = f"Book a 15-minute demo call here: {BOOKING_LINK}"
    output = (
        f"Hi {lead_name} — {BRAND_LINE} "
        "Talvenor's AI receptionist answers every call, 24/7, and books "
        f"the job while you're still on the last one. {cta}"
    )
    notes = [
        "DRAFT ONLY — never sent.",
        f"Channel: {channel}. One line, booking link included.",
        "No prices, no invented statistics, no invented client claims.",
    ]
    return {"output": output, "notes": notes}


def kit_outline_read(args, context=None):
    """Reads the first ~1500 characters of the real kit-outline.md file. Error if the file is missing."""
    try:
        with open(KIT_OUTLINE_PATH, "r", encoding="utf-8") as f:
            text = f.read(1500)
    except (FileNotFoundError, OSError) as exc:
        return {
            "output": "",
            "notes": ["Kit outline file could not be read — no content invented."],
            "error": f"Kit outline file not found or unreadable: {KIT_OUTLINE_PATH} ({exc})",
        }
    return {
        "output": text,
        "notes": ["Kit blueprint only — kit NOT built, Gate 0 NOT PASSED."],
    }


def status_read(args, context=None):
    """Reads the real config.json and returns the honest status + phase + spend cap."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as exc:
        return {
            "output": "",
            "notes": ["Config file could not be read — no status invented."],
            "error": f"Config file unreadable: {CONFIG_PATH} ({exc})",
        }
    honest = config.get("honest_status", {})
    status = {
        "honest_status": honest,
        "phase": config.get("phase"),
        "spend_cap_usd": config.get("spend_cap_usd"),
    }
    return {
        "output": json.dumps(status, indent=2, ensure_ascii=False),
        "notes": [
            "Read from the real config.json — not invented.",
            "Spend cap is $0. Email outreach is PAUSED. Gate 0 NOT PASSED.",
        ],
    }


HANDLERS = {
    "draft_email": draft_email,
    "research_notes": research_notes,
    "draft_caption": draft_caption,
    "draft_script": draft_script,
    "kit_outline_read": kit_outline_read,
    "status_read": status_read,
    "booking_reply": booking_reply,
}


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------

REQUIRED_TOOL_KEYS = ("name", "description", "params", "gated", "status")


class ToolRegistry:
    """Registry of tool definitions. Engine wrappers read from here."""

    def __init__(self):
        self.tools = {}

    def register(self, tool_dict):
        """Validates and registers one tool definition. ValueError if wrong."""
        if not isinstance(tool_dict, dict):
            raise ValueError("Tool definition must be a dict.")
        for key in REQUIRED_TOOL_KEYS:
            if key not in tool_dict:
                raise ValueError(f"Tool definition missing required key: {key!r}")
        name = tool_dict["name"]
        if not isinstance(name, str) or not name:
            raise ValueError("Tool 'name' must be a non-empty string.")
        if not isinstance(tool_dict["description"], str):
            raise ValueError(f"Tool {name!r}: 'description' must be a string.")
        params = tool_dict["params"]
        if not isinstance(params, dict) or params.get("type") != "object":
            raise ValueError(f"Tool {name!r}: 'params' must be an object schema dict.")
        if not isinstance(params.get("properties", {}), dict):
            raise ValueError(f"Tool {name!r}: 'params.properties' must be a dict.")
        if not isinstance(tool_dict["gated"], bool):
            raise ValueError(f"Tool {name!r}: 'gated' must be a boolean.")
        if tool_dict["status"] not in ("mock", "real", "stub", "live-ready"):
            raise ValueError(
                f"Tool {name!r}: 'status' must be 'mock', 'real', 'stub', "
                "or 'live-ready'."
            )
        if tool_dict["status"] == "live-ready" and not tool_dict["gated"]:
            raise ValueError(
                f"Live-ready tool {name!r} must be gated — a live "
                "connection without a gate is not allowed."
            )
        gated_action = tool_dict.get("gated_action")
        if tool_dict["gated"]:
            if gated_action not in GATED_ACTIONS:
                raise ValueError(
                    f"Gated tool {name!r} must have 'gated_action' set to one of "
                    f"{list(GATED_ACTIONS)}."
                )
        handler = tool_dict.get("handler")
        if tool_dict["status"] == "mock":
            if not isinstance(handler, str) or handler not in HANDLERS:
                raise ValueError(
                    f"Mock tool {name!r} must have a 'handler' name that exists "
                    f"in HANDLERS. Known: {sorted(HANDLERS)}"
                )
        if tool_dict["status"] == "live-ready":
            # A live-ready handler must be in live_tools.LIVE_HANDLERS —
            # no live handler gets into the registry under a wrong name.
            # This is only validation: after the gated intercept in the
            # dispatcher, a live-ready tool still has no execution path.
            if not isinstance(handler, str) or handler not in LIVE_HANDLERS:
                raise ValueError(
                    f"Live-ready tool {name!r} must have a 'handler' name "
                    f"that exists in LIVE_HANDLERS. Known: "
                    f"{sorted(LIVE_HANDLERS)}"
                )
        self.tools[name] = dict(tool_dict)
        return self.tools[name]

    def get(self, name):
        """Find a tool by name — KeyError if absent."""
        if name not in self.tools:
            raise KeyError(f"Unknown tool {name!r}. Known: {sorted(self.tools)}")
        return self.tools[name]

    def list_tools(self):
        """List of all registered tool definitions."""
        return [dict(tool) for tool in self.tools.values()]

    @classmethod
    def load_from_json(cls, path):
        """Reads tools.json ({"tools": [...]}) and registers each tool."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        tools = data.get("tools", []) if isinstance(data, dict) else []
        registry = cls()
        for tool_dict in tools:
            registry.register(tool_dict)
        return registry


# ---------------------------------------------------------------------------
# Calls log — every call (including errors / refusals) is appended, never overwritten.
# If writing the log fails, the call's result is still returned, with "log_error".
# ---------------------------------------------------------------------------

def _log_call(record, calls_log_path=None):
    path = calls_log_path or DEFAULT_CALLS_LOG_PATH
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    records.append(record)
    payload = {"schema": "tool-calls-v1", "records": records}
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _validate_args(tool, args):
    """Validate args against the params schema. An error string if wrong, None if right."""
    if not isinstance(args, dict):
        return "Invalid args: args must be a dict."
    params = tool.get("params") or {}
    properties = params.get("properties", {}) or {}
    required = params.get("required", []) or []
    for field in required:
        if field not in args:
            return f"Invalid args: missing required field {field!r}."
    for field, value in args.items():
        spec = properties.get(field)
        if not spec:
            continue  # extra field — allowed, ignored
        expected = spec.get("type")
        checker = _TYPE_CHECKS.get(expected)
        if checker is None:
            continue  # unknown declared type — schema bug, not a call failure
        if not checker(value):
            return (
                f"Invalid args: field {field!r} must be of type {expected!r}, "
                f"got {type(value).__name__}."
            )
    return None


def call_tool(name, args, context=None, registry=None, approvals_path=None,
              calls_log_path=None, ledger_path=None):
    """Run one tool — gate first, handler after, everything in the log.

    Order:
      1. Unknown tool -> error
      2. args validation fail -> error
      3. gated tool -> trust_check (Phase 1): on deny, "blocked-trust"
         (no approval is recorded); otherwise a PENDING request in the
         ApprovalGateway, the handler does not run
      4. stub -> blocked-stub
      4b. live-ready (if it got past the gated intercept) -> error, fail-closed
      5. mock -> run HANDLERS[handler], draft-ready
      6. real + no handler -> error (a bug, not a silent pass)
      7. Every call is appended to the calls log (log_error if the log fails);
         with ledger_path, a receipt is also written to the usage ledger (cost $0.00).
    """
    args = args if isinstance(args, dict) else {}
    requested_by = "Main CEO Bot"
    task_id = None
    if context and isinstance(context, dict):
        requested_by = context.get("requested_by", "Main CEO Bot") or "Main CEO Bot"
        task_id = context.get("task_id")
    reg = registry if registry is not None else ToolRegistry()

    result = None
    try:
        tool = reg.get(name)
    except KeyError:
        result = {"status": "error", "tool": name, "error": f"Unknown tool {name!r}."}
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    validation_error = _validate_args(tool, args)
    if validation_error:
        result = {"status": "error", "tool": name, "error": validation_error}
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    # 3. Gated tool — the handler never runs at all, even with an approval_id.
    if tool.get("gated"):
        gated_action = tool.get("gated_action")
        if gated_action not in GATED_ACTIONS:
            result = {
                "status": "error",
                "tool": name,
                "error": f"Gated tool {name!r} has invalid gated_action {gated_action!r}.",
            }
            _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
            return result
        # 3a. Trust pre-check (Improvement Phase 1, Nod pattern):
        # No gated-work decision happens without Boss's word. If a standing rule
        # (spend cap $0, dental/medical DQ) refuses, no approval is
        # recorded either — "blocked-trust". Email PAUSED is not a deny:
        # a PENDING approval is the restart path, so the decision stays "ask".
        owner_words = None
        owner_source = None
        if context and isinstance(context, dict):
            owner_words = context.get("owner_words")
            owner_source = context.get("owner_source")
        decision = trust_check(gated_action, args,
                               owner_words=owner_words,
                               owner_source=owner_source,
                               tool_name=name)
        if decision["decision"] == "deny":
            result = {
                "status": "blocked-trust",
                "tool": name,
                "gated_action": gated_action,
                "trust": decision,
                "note": ("Trust check refused — no approval recorded, "
                         "nothing was executed."),
            }
            _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
            return result
        gateway = ApprovalGateway(approvals_path=approvals_path)
        approval = gateway.request(
            gated_action, detail=f"tool:{name}", requested_by=requested_by
        )
        result = {
            "status": "pending-approval",
            "tool": name,
            "gated_action": gated_action,
            "approval": approval,
            "trust": decision,
            "note": "Gated tool refused — PENDING approval recorded. Nothing was executed.",
        }
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    # 4. Stub — absent, cannot be run.
    if tool.get("status") == "stub":
        result = {
            "status": "blocked-stub",
            "tool": name,
            "note": "Tool is a stub — not available.",
        }
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    # 4b. Live-ready — fail-closed if it gets here after the gated intercept:
    # no direct execution path exists. (A gated live-ready tool never
    # gets here — it becomes PENDING in step 3. This branch is only defense.)
    if tool.get("status") == "live-ready":
        result = {
            "status": "error",
            "tool": name,
            "error": f"Live-ready tool {name!r} has no direct execution "
                     "path — gated only, nothing executed.",
        }
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    # 5. Mock — run the handler, return a DRAFT.
    if tool.get("status") == "mock":
        handler_name = tool.get("handler")
        handler = HANDLERS.get(handler_name)
        if handler is None:
            result = {
                "status": "error",
                "tool": name,
                "error": f"Mock tool {name!r} has unknown handler {handler_name!r}.",
            }
            _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
            return result
        handler_result = handler(args, context)
        if isinstance(handler_result, dict) and handler_result.get("error"):
            result = {
                "status": "error",
                "tool": name,
                "error": handler_result["error"],
                "notes": handler_result.get("notes", []),
            }
            _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
            return result
        result = {
            "status": "draft-ready",
            "tool": name,
            "draft_only": True,
            "mock": True,
            "output": handler_result.get("output", ""),
            "notes": handler_result.get("notes", []),
        }
        _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
        return result

    # 6. Real tool, no handler — a bug, not a silent pass.
    result = {
        "status": "error",
        "tool": name,
        "error": f"Real tool {name!r} has no implementation (no handler).",
    }
    _finish(result, name, args, requested_by, calls_log_path, ledger_path, task_id)
    return result


def _finish(result, name, args, requested_by, calls_log_path, ledger_path=None,
            task_id=None):
    """Append a call's result to the log. If the log fails, log_error is set on the result.
    With ledger_path, a receipt is also written to the usage ledger (mock call = $0.00);
    even if the ledger write fails, the call's result is returned, with ledger_error."""
    record = {
        "id": uuid.uuid4().hex[:12],
        "tool": name,
        "args": args,
        "status": result.get("status"),
        "logged_at": _now_iso(),
        "requested_by": requested_by,
    }
    try:
        _log_call(record, calls_log_path=calls_log_path)
    except Exception as exc:  # noqa: BLE001 — the log must never crash the call
        result["log_error"] = f"Could not write calls log: {exc}"
    if ledger_path is not None:
        try:
            kind = {"draft-ready": "mock", "pending-approval": "gate",
                    "blocked-trust": "gate"}.get(result.get("status"), "error")
            ledger = UsageLedger(ledger_path=ledger_path)
            ledger.record(kind, "mock", "mock", cost_usd=0.0,
                          task_id=task_id, action=name,
                          note=f"tool_call status={result.get('status')}")
        except Exception as exc:  # noqa: BLE001 — the ledger must never crash the call
            result["ledger_error"] = f"Could not write usage ledger: {exc}"
    return result


if __name__ == "__main__":
    # Self-test — TEMP files only, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_approvals = os.path.join(tmp_dir, "approvals-test.json")
    tmp_log = os.path.join(tmp_dir, "tool_calls-test.json")

    registry = ToolRegistry()
    registry.register({
        "name": "draft_email",
        "description": "Draft a cold email (mock, draft-only).",
        "params": {
            "type": "object",
            "properties": {
                "business_name": {"type": "string", "description": "Business name."},
                "topic": {"type": "string", "description": "Email topic."},
            },
            "required": ["business_name", "topic"],
        },
        "gated": False,
        "gated_action": None,
        "status": "mock",
        "handler": "draft_email",
    })
    registry.register({
        "name": "send_email",
        "description": "Send an email (gated — never executes here).",
        "params": {
            "type": "object",
            "properties": {
                "business_name": {"type": "string", "description": "Business name."},
                "topic": {"type": "string", "description": "Email topic."},
            },
            "required": ["business_name", "topic"],
        },
        "gated": True,
        "gated_action": "send",
        "status": "mock",
        "handler": "draft_email",
    })

    mock_result = call_tool(
        "draft_email",
        {"business_name": "ABC Plumbing", "topic": "missed calls"},
        registry=registry, approvals_path=tmp_approvals, calls_log_path=tmp_log,
    )
    assert mock_result["status"] == "draft-ready", mock_result
    assert mock_result["draft_only"] is True and mock_result["mock"] is True
    assert BRAND_LINE in mock_result["output"]

    gated_result = call_tool(
        "send_email",
        {"business_name": "ABC Plumbing", "topic": "missed calls"},
        registry=registry, approvals_path=tmp_approvals, calls_log_path=tmp_log,
    )
    assert gated_result["status"] == "pending-approval", gated_result
    assert gated_result["approval"]["status"] == "pending"
    assert "Nothing was executed" in gated_result["note"]

    bad_result = call_tool(
        "draft_email",
        {"business_name": "ABC Plumbing"},
        registry=registry, approvals_path=tmp_approvals, calls_log_path=tmp_log,
    )
    assert bad_result["status"] == "error", bad_result
    assert "Invalid args" in bad_result["error"]

    unknown_result = call_tool(
        "no_such_tool", {},
        registry=registry, approvals_path=tmp_approvals, calls_log_path=tmp_log,
    )
    assert unknown_result["status"] == "error", unknown_result

    with open(tmp_log, "r", encoding="utf-8") as f:
        logged = json.load(f)
    assert logged["schema"] == "tool-calls-v1"
    assert len(logged["records"]) == 4, logged  # mock + gated + bad + unknown

    print("tool_calling: OK")
