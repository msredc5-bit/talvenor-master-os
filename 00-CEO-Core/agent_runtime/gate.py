"""Runtime gate — Phase 3 (local-first) bounded agent runtime.

The runtime NEVER executes a gated action. A gated action inside a
runtime run always comes back as a pending-approval draft result
(enforce_gate -> {"allowed": False, "status": "pending-approval"}).

Real gate files/functions consulted (read-only — this module weakens
nothing, writes nothing, records no approval):
  * ``00-CEO-Core/human_approval_gateway.py`` — ``GATED_ACTIONS``
    ("send", "publish", "spend", "delete", "upload"),
    ``GATE_WORD_FOR_ACTION`` (send->"send"/"পাঠাও", publish->"post it"/
    "post all", spend/delete->"go", upload->"upload it"), and the
    ``ApprovalGateway`` class (request/approve/reject/is_approved).
    This module does NOT call ApprovalGateway: classifying an action
    as gated is not requesting approval, and no approval is ever
    recorded or granted from the runtime.
  * ``00-CEO-Core/trust_gate.py`` — ``COMMIT_ACTIONS`` ("send",
    "publish", "spend", "delete", "upload", "book", "pay", "order",
    "cancel"), ``READ_ACTIONS`` ("read", "draft", "status", "search",
    "list"), ``GATE_WORD_FOR_ACTION``, and ``trust_check(action, args,
    owner_words=None, ...)``. trust_check is consulted as a second
    opinion for bare action verbs that match no known tool: a decision
    other than "allow" means gated (fail-safe — an unknown action is
    treated as gated, never as free).
  * ``00-CEO-Core/tools.json`` — the tool registry. The gated tools
    are gmail_send (gated_action "send") and n8n_trigger (gated_action
    "send"); every other listed tool (draft_email, research_notes,
    draft_caption, draft_script, kit_outline_read, status_read,
    booking_reply) is ungated/draft-only. A known tool's "gated" flag
    is trusted directly; an unknown tool name falls through to the
    verb check and then to trust_check.
  * ``00-CEO-Core/tool_calling.py`` — observed only, not imported:
    its call_tool() gated intercept (gated tool -> trust_check ->
    PENDING approval, never executes) is the behaviour this module
    mirrors at the runtime layer.

Stdlib only. No network, no keys, no file writes (tools.json is read
lazily and cached; if it cannot be read, the fallback is the gated
tool set recorded above).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Set

__all__ = [
    "GATED_TOOL_NAMES",
    "GATED_ACTIONS",
    "COMMIT_ACTIONS",
    "READ_ACTIONS",
    "is_gated_action",
    "enforce_gate",
]

# --- Real gate constants (mirrors; the imports below override them) -------
try:
    from human_approval_gateway import (  # noqa: F401
        GATE_WORD_FOR_ACTION as _GATEWAY_GATE_WORDS,
        GATED_ACTIONS as _GATEWAY_GATED_ACTIONS,
    )
    GATED_ACTIONS = tuple(_GATEWAY_GATED_ACTIONS)
except ImportError:  # pragma: no cover - 00-CEO-Core not on sys.path
    GATED_ACTIONS = ("send", "publish", "spend", "delete", "upload")

try:
    from trust_gate import (  # noqa: F401
        COMMIT_ACTIONS as _TRUST_COMMIT_ACTIONS,
        READ_ACTIONS as _TRUST_READ_ACTIONS,
        trust_check as _trust_check,
    )
    COMMIT_ACTIONS = tuple(_TRUST_COMMIT_ACTIONS)
    READ_ACTIONS = tuple(_TRUST_READ_ACTIONS)
    trust_check = _trust_check
except ImportError:  # pragma: no cover - 00-CEO-Core not on sys.path
    COMMIT_ACTIONS = ("send", "publish", "spend", "delete", "upload",
                      "book", "pay", "order", "cancel")
    READ_ACTIONS = ("read", "draft", "status", "search", "list")
    trust_check = None  # type: ignore[assignment]

_TOOLS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools.json")

# Fallback = the gated tools actually listed in tools.json (2026-11-24).
_FALLBACK_GATED_TOOLS = {"gmail_send": "send", "n8n_trigger": "send"}

_gated_tools_cache: Optional[Dict[str, str]] = None
_known_tools_cache: Optional[Set[str]] = None


def _load_tools_registry() -> Dict[str, str]:
    """Gated tools from tools.json: {tool_name: gated_action}.

    Read-only, cached after the first load. Falls back to the recorded
    gated set when the file cannot be read.
    """
    global _gated_tools_cache, _known_tools_cache
    if _gated_tools_cache is not None:
        return _gated_tools_cache
    gated: Dict[str, str] = dict(_FALLBACK_GATED_TOOLS)
    known: Set[str] = set(_FALLBACK_GATED_TOOLS)
    try:
        with open(_TOOLS_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for tool in data.get("tools", []):
            name = tool.get("name")
            if not isinstance(name, str):
                continue
            known.add(name)
            if tool.get("gated") is True:
                gated[name] = tool.get("gated_action") or "send"
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass  # fallback set above stands
    _gated_tools_cache = gated
    _known_tools_cache = known
    return gated


def _known_tools() -> Set[str]:
    _load_tools_registry()
    return set(_known_tools_cache or set())


#: {tool_name: gated_action} for every gated tool in tools.json.
GATED_TOOL_NAMES: Dict[str, str] = _load_tools_registry()


def _action_verb(action: Dict[str, Any]) -> str:
    verb = (
        action.get("action")
        or action.get("type")
        or action.get("tool")
        or action.get("tool_name")
        or action.get("name")
        or ""
    )
    return str(verb).strip().lower()


def _action_args(action: Dict[str, Any]) -> Dict[str, Any]:
    args = action.get("args") or action.get("params") or {}
    return args if isinstance(args, dict) else {}


def is_gated_action(action: Dict[str, Any]) -> bool:
    """True when the action would send/publish/spend/delete/deploy/go-live.

    Decision order (first match wins, fail-safe at the end):
      1. explicit "gated": true in the action dict;
      2. tool name is a gated tool in tools.json (gmail_send, n8n_trigger);
      3. the action verb is in trust_gate.COMMIT_ACTIONS or
         human_approval_gateway.GATED_ACTIONS -> gated (checked BEFORE
         the known-ungated-tool shortcut, so a commit verb on an
         ungated tool — e.g. {"tool": "draft_email", "action": "send"}
         — is still gated; the old order let that slip through);
      4. tool name is a known UNGATED tool in tools.json -> not gated;
      5. the verb is in trust_gate.READ_ACTIONS -> not gated;
      6. otherwise consult trust_gate.trust_check(verb, args): any
         decision other than "allow" -> gated; if trust_check is
         unavailable, an unclassified action is gated (fail-safe).
    """
    if not isinstance(action, dict):
        raise ValueError(f"action must be a dict, got {type(action).__name__}")
    if action.get("gated") is True:
        return True

    tool = str(action.get("tool") or action.get("tool_name")
               or action.get("name") or "").strip()
    gated_tools = _load_tools_registry()
    if tool in gated_tools:
        return True

    verb = _action_verb(action)
    if verb in COMMIT_ACTIONS or verb in GATED_ACTIONS:
        return True
    if tool and tool in _known_tools():
        return False  # known tool, listed ungated in tools.json

    if verb in READ_ACTIONS:
        return False

    # Unknown verb: ask the real trust gate; anything but "allow" is gated.
    if trust_check is not None:
        try:
            decision = trust_check(verb, _action_args(action))
            return decision.get("decision") != "allow"
        except Exception:  # noqa: BLE001 - trust gate failure must fail closed
            return True
    return True  # fail-safe: unclassified action is gated


def enforce_gate(action: Dict[str, Any]) -> Dict[str, Any]:
    """Gate verdict for one action. Never executes anything.

    Gated -> {"allowed": False, "status": "pending-approval",
    "reason": ...} — the runtime returns this as a draft result and
    Boss's exact gate word (human_approval_gateway.GATE_WORD_FOR_ACTION)
    is the only thing that can ever move it forward, outside the runtime.
    Ungated -> {"allowed": True, "status": "allowed"}.
    """
    if is_gated_action(action):
        tool = str(action.get("tool") or action.get("tool_name")
                   or action.get("name") or "").strip()
        verb = _action_verb(action)
        label = tool or verb or "unknown action"
        gated_action = _load_tools_registry().get(tool, verb)
        return {
            "allowed": False,
            "status": "pending-approval",
            "reason": (
                f"Gated action {label!r} (gated_action={gated_action!r}) — "
                "send/publish/spend/delete/deploy needs Boss's exact gate "
                "word (human_approval_gateway.GATE_WORD_FOR_ACTION); the "
                "runtime never executes a gated action, it returns a "
                "pending-approval draft only. Sources: "
                "human_approval_gateway.GATED_ACTIONS, "
                "trust_gate.COMMIT_ACTIONS, tools.json gated tools."
            ),
        }
    return {"allowed": True, "status": "allowed"}
