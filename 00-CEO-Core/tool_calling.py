"""Shared Tool-Calling Core — Talvenor Master OS (Phase 5).

এই ফাইলটা কী:
  Master OS-এর তিনটা department (Agency, Digital Product, Content) —
  সবাই একই tool-calling নিয়মে চলবে। Tool মানে একটা নাম + কী কী
  argument লাগবে + সেটা gated কি না + mock / real / stub কি না।
  Engine wrapper-রা এই ফাইল import করে ToolRegistry বানায়, আর
  call_tool() দিয়ে tool চালায়।

Gate নিয়ম (Boss-এর সিদ্ধান্ত, কোডে লেখা):
  - Gated tool (send / publish / spend / delete) কখনো execute হয় না।
    call_tool() শুধু ApprovalGateway-এ একটা PENDING approval request
    লেখে আর থেমে যায়। Approval ID থাকলেও না — gated কাজ Boss নিজে
    করেন, এই dispatcher শুধু request রেকর্ড করে।
  - Gate words: ok / "post it" / "upload it" / send / go — Boss-এর
    সঠিক শব্দ ছাড়া কিছু এগোয় না। Auto-approve-এর কোনো পথ নেই।
  - খরচের সীমা $0। Paying client 0। Email PAUSED। Gate 0 NOT PASSED।
    Upload OFF। কোনো বানানো client / সংখ্যা / testimonial / দাম নেই।
    Dental / medical নয়। Brand শুধু Talvenor।

৭টা mock handler (সব DRAFT ONLY — কিছু পাঠানো / পাবলিশ / খরচ হয় না):
  1. draft_email      — cold-email draft (Talvenor brand line + booking link)
  2. research_notes   — research-notes template, সব field "TO VERIFY"
  3. draft_caption    — social caption draft, প্রথম লাইন hook
  4. draft_script     — ছোট ভিডিও script outline (hook, problem, solution, CTA)
  5. kit_outline_read — আসল kit-outline.md ফাইল পড়ে (বানানো content নয়)
  6. status_read      — আসল config.json পড়ে (honest status, phase, spend cap)
  7. booking_reply    — lead-এর নাম দিলে booking link সহ এক লাইনের reply draft
                        (Boss-এর 2026-11-17 প্রশ্নের উদাহরণ tool — DRAFT ONLY)

ব্যবহার:
  import tool_calling
  registry = tool_calling.ToolRegistry.load_from_json("tools.json")
  result = tool_calling.call_tool("draft_email",
      {"business_name": "ABC Plumbing", "topic": "missed calls"},
      registry=registry)
  # result["status"] = "draft-ready" | "pending-approval" | "blocked-stub" | "error"

Stdlib only — কোনো network নেই, কোনো pip নেই।
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from human_approval_gateway import GATED_ACTIONS, ApprovalGateway  # noqa: E402

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
# Mock handlers — প্রতিটা fn(args, context) -> {"output": str, "notes": [str]}
# কোনো handler network-এ যায় না, কিছু পাঠায় / পাবলিশ / খরচ করে না।
# ফাইল পড়া handler (kit_outline_read, status_read) ফাইল না পেলে
# {"error": ...} ফেরত দেয় — বানানো content কখনো নয়।
# ---------------------------------------------------------------------------

def draft_email(args, context=None):
    """DRAFT cold-email body — Talvenor brand line + booking link, দাম নেই।"""
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
    """DRAFT research-notes template — সব field যাচাই বাকি।"""
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
    """DRAFT social caption — প্রথম লাইন hook।"""
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
    """DRAFT short video script outline — hook, problem, solution, CTA।"""
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
    """Lead-এর নাম দিলে booking link সহ এক লাইনের reply DRAFT।

    Boss-এর উদাহরণ tool (2026-11-17, 02:43 Dhaka — "GitHub দিয়ে tool
    কিভাবে create করে?"): input শুধু lead-এর নাম, output এক লাইন reply
    + booking link। DRAFT ONLY — কখনো পাঠায় না; পাঠাতে হলে gated
    send_email tool + Boss-এর exact gate word লাগে। কোনো দাম নেই,
    কোনো বানানো client / সংখ্যা / testimonial নেই।
    """
    lead_name = (args.get("lead_name") or "").strip()
    channel = (args.get("channel") or "email").strip().lower()
    if not lead_name:
        return {
            "output": "",
            "notes": ["DRAFT ONLY — lead-এর নাম দেওয়া হয়নি।"],
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
    """আসল kit-outline.md ফাইলের প্রথম ~1500 অক্ষর পড়ে। ফাইল না থাকলে error।"""
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
    """আসল config.json পড়ে honest status + phase + spend cap ফেরত দেয়।"""
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
    """Tool definition-গুলোর রেজিস্ট্রি। Engine wrapper-রা এখান থেকে পড়ে।"""

    def __init__(self):
        self.tools = {}

    def register(self, tool_dict):
        """একটা tool definition যাচাই করে রেজিস্টার করে। ভুল হলে ValueError।"""
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
        if tool_dict["status"] not in ("mock", "real", "stub"):
            raise ValueError(
                f"Tool {name!r}: 'status' must be 'mock', 'real', or 'stub'."
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
        self.tools[name] = dict(tool_dict)
        return self.tools[name]

    def get(self, name):
        """নামে tool খোঁজা — না থাকলে KeyError।"""
        if name not in self.tools:
            raise KeyError(f"Unknown tool {name!r}. Known: {sorted(self.tools)}")
        return self.tools[name]

    def list_tools(self):
        """রেজিস্টার করা সব tool definition-এর তালিকা।"""
        return [dict(tool) for tool in self.tools.values()]

    @classmethod
    def load_from_json(cls, path):
        """tools.json ({"tools": [...]}) পড়ে প্রতিটা tool রেজিস্টার করে।"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        tools = data.get("tools", []) if isinstance(data, dict) else []
        registry = cls()
        for tool_dict in tools:
            registry.register(tool_dict)
        return registry


# ---------------------------------------------------------------------------
# Calls log — প্রতিটা call (error / refusal সহ) append হয়, কখনো overwrite নয়।
# Log লেখা fail করলে call-এর ফলাফল তবু ফেরত যায়, "log_error" সহ।
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
    """Params schema অনুযায়ী args যাচাই। ভুল হলে error string, ঠিক হলে None।"""
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
              calls_log_path=None):
    """একটা tool চালানো — gate আগে, handler পরে, সবকিছু log-এ।

    Order:
      1. অচেনা tool -> error
      2. args validation fail -> error
      3. gated tool -> ApprovalGateway-এ PENDING request, handler চলে না
      4. stub -> blocked-stub
      5. mock -> HANDLERS[handler] চালিয়ে draft-ready
      6. real + handler নেই -> error (bug, silent pass নয়)
      7. প্রতিটা call calls log-এ append হয় (log fail করলে log_error সহ)।
    """
    args = args if isinstance(args, dict) else {}
    requested_by = "Main CEO Bot"
    if context and isinstance(context, dict):
        requested_by = context.get("requested_by", "Main CEO Bot") or "Main CEO Bot"
    reg = registry if registry is not None else ToolRegistry()

    result = None
    try:
        tool = reg.get(name)
    except KeyError:
        result = {"status": "error", "tool": name, "error": f"Unknown tool {name!r}."}
        _finish(result, name, args, requested_by, calls_log_path)
        return result

    validation_error = _validate_args(tool, args)
    if validation_error:
        result = {"status": "error", "tool": name, "error": validation_error}
        _finish(result, name, args, requested_by, calls_log_path)
        return result

    # 3. Gated tool — handler একদম চলে না, approval_id থাকলেও না।
    if tool.get("gated"):
        gated_action = tool.get("gated_action")
        if gated_action not in GATED_ACTIONS:
            result = {
                "status": "error",
                "tool": name,
                "error": f"Gated tool {name!r} has invalid gated_action {gated_action!r}.",
            }
            _finish(result, name, args, requested_by, calls_log_path)
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
            "note": "Gated tool refused — PENDING approval recorded. Nothing was executed.",
        }
        _finish(result, name, args, requested_by, calls_log_path)
        return result

    # 4. Stub — নেই, চালানো যায় না।
    if tool.get("status") == "stub":
        result = {
            "status": "blocked-stub",
            "tool": name,
            "note": "Tool is a stub — not available.",
        }
        _finish(result, name, args, requested_by, calls_log_path)
        return result

    # 5. Mock — handler চালিয়ে DRAFT ফেরত।
    if tool.get("status") == "mock":
        handler_name = tool.get("handler")
        handler = HANDLERS.get(handler_name)
        if handler is None:
            result = {
                "status": "error",
                "tool": name,
                "error": f"Mock tool {name!r} has unknown handler {handler_name!r}.",
            }
            _finish(result, name, args, requested_by, calls_log_path)
            return result
        handler_result = handler(args, context)
        if isinstance(handler_result, dict) and handler_result.get("error"):
            result = {
                "status": "error",
                "tool": name,
                "error": handler_result["error"],
                "notes": handler_result.get("notes", []),
            }
            _finish(result, name, args, requested_by, calls_log_path)
            return result
        result = {
            "status": "draft-ready",
            "tool": name,
            "draft_only": True,
            "mock": True,
            "output": handler_result.get("output", ""),
            "notes": handler_result.get("notes", []),
        }
        _finish(result, name, args, requested_by, calls_log_path)
        return result

    # 6. Real tool, handler নেই — bug, silent pass নয়।
    result = {
        "status": "error",
        "tool": name,
        "error": f"Real tool {name!r} has no implementation (no handler).",
    }
    _finish(result, name, args, requested_by, calls_log_path)
    return result


def _finish(result, name, args, requested_by, calls_log_path):
    """Call-এর ফলাফল log-এ append করা। Log fail করলে result-এ log_error বসে।"""
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
    except Exception as exc:  # noqa: BLE001 — log কখনো call-কে crash করাবে না
        result["log_error"] = f"Could not write calls log: {exc}"
    return result


if __name__ == "__main__":
    # Self-test — শুধু TEMP ফাইল, আসল store ছোঁয়া হয় না।
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
