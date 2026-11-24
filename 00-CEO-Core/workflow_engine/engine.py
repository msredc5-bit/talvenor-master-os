"""Provider-independent workflow engine — Talvenor Master OS,
local-first Phase 4.

A workflow is a dict with a "steps" list. Each step is a dict:

  {"id": "research", "kind": "draft", "input": {...}}
  {"id": "send-mail", "tool": "gmail_send", "action": "send",
   "input": {...}}

``WorkflowEngine.execute(workflow, context=None, adapter=None)``
runs the steps in order and returns a structured dict::

  {"status": "completed" | "partial" | "error",
   "steps": [{"id", "name", "kind", "status", "output",
              "evidence", "cost_usd"}, ...],
   "cost_usd": 0.0, "error": <str or None>}

Rules (hard):
  * Every step consults the Phase 3 gate
    (``agent_runtime/gate.py`` ``enforce_gate``) BEFORE running. A
    step whose tool/action is gated (send/publish/spend/delete/
    upload, incl. the ``n8n_trigger`` tool) comes back as a
    "pending-approval" step and NEVER executes. Boss's exact gate
    word is the only thing that can ever move it forward, outside
    this engine.
  * Steps are mock/draft-only ($0, no live calls). The ONLY live-ish
    path is an "n8n" step routed through an ``N8nAdapter`` — and
    even that path is gate-checked first, so today (``n8n_trigger``
    is a gated tool) it always lands pending-approval too. The
    adapter itself only ever talks to a local test double in this
    VM; real n8n lives on Boss's PC, not here.
  * ``execute`` never raises on a step failure: a bad step becomes
    an "error" step, a bad workflow becomes an "error" result.
  * Runtime limits are honoured when a ``RuntimeContext`` is
    passed: the wall clock stops the run (status "partial") and the
    context's ``max_iterations`` caps how many steps run.
  * Mock kinds (draft/research/report/qa/status/search/list/read/
    mock) with no explicit tool/action are gate-checked as a
    "draft" action — a read/draft verb that the trust gate allows.
    An explicit tool/action is ALWAYS passed to the gate verbatim;
    nothing is silently re-labelled to dodge it.

Stdlib only. No network, no keys, no spend.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

__all__ = ["WorkflowEngine", "execute", "MOCK_KINDS"]

# Step kinds that are pure mock/draft work. With no explicit
# tool/action they are gate-checked as the "draft" verb (a
# trust_gate READ_ACTION — runs free). Any other kind with no
# explicit tool/action is passed to the gate as its own verb and
# fails closed there (unknown verb -> pending-approval).
MOCK_KINDS = frozenset({
    "draft", "research", "report", "qa", "status", "search", "list",
    "read", "mock",
})

# Gated sets used ONLY as a fallback when the real Phase 3 gate
# cannot be imported (the real gate is always preferred; this
# fallback gates MORE, never less — an unclassified step is gated).
_FALLBACK_GATED_TOOLS = frozenset({"gmail_send", "n8n_trigger"})
_FALLBACK_GATED_ACTIONS = frozenset({
    "send", "publish", "spend", "delete", "upload", "book", "pay",
    "order", "cancel",
})


def _load_enforce_gate():
    """The real Phase 3 gate, or None when it cannot be imported."""
    try:
        from agent_runtime.gate import enforce_gate  # noqa: PLC0415
        return enforce_gate
    except ImportError:
        return None


def _fallback_gate(action: Dict[str, Any]) -> Dict[str, Any]:
    """Fail-closed gate verdict used only if agent_runtime.gate is
    missing. Mirrors the real gate's decision order in miniature:
    gated tool or gated verb -> pending-approval; known mock verb
    "draft"/"read"/"status"/"search"/"list" -> allowed; anything
    else -> pending-approval (fail-safe)."""
    tool = str(action.get("tool") or "").strip()
    verb = str(action.get("action") or action.get("tool") or "").strip().lower()
    if tool in _FALLBACK_GATED_TOOLS or verb in _FALLBACK_GATED_ACTIONS:
        return {"allowed": False, "status": "pending-approval",
                "reason": "fallback gate: gated tool/action (real "
                          "agent_runtime.gate unavailable)"}
    if verb in ("draft", "read", "status", "search", "list"):
        return {"allowed": True, "status": "allowed"}
    return {"allowed": False, "status": "pending-approval",
            "reason": "fallback gate: unclassified action fails closed"}


def _gate_action_for_step(step: Dict[str, Any]) -> Dict[str, Any]:
    """The action dict the gate sees for one workflow step.

    Explicit tool/action win verbatim (never re-labelled). A mock
    kind with neither is checked as {"action": "draft"}.
    """
    tool = step.get("tool") or step.get("tool_name")
    action = step.get("action") or step.get("type")
    kind = str(step.get("kind") or "").strip().lower()
    gate_action: Dict[str, Any] = {}
    if tool:
        gate_action["tool"] = tool
    if action:
        gate_action["action"] = action
    elif kind:
        gate_action["action"] = "draft" if kind in MOCK_KINDS else kind
    elif tool:
        gate_action["action"] = tool
    else:
        gate_action["action"] = "draft"
    args = step.get("args") or step.get("params") or step.get("input")
    if isinstance(args, dict):
        gate_action["args"] = args
    return gate_action


def _step_name(step: Dict[str, Any], index: int) -> str:
    name = step.get("id") or step.get("name")
    return str(name) if name else f"step-{index + 1}"


class WorkflowEngine:
    """Runs a workflow's steps in order, inside the gate and the
    runtime limits. Mock/draft-only; $0; never raises on a step
    failure."""

    def execute(self, workflow, context=None, adapter=None) -> Dict[str, Any]:
        """Execute one workflow dict. See the module docstring for
        the return shape."""
        if not isinstance(workflow, dict):
            return {"status": "error", "steps": [], "cost_usd": 0.0,
                    "error": f"workflow must be a dict, got "
                             f"{type(workflow).__name__}"}
        steps_in = workflow.get("steps")
        if steps_in is None:
            steps_in = []
        if not isinstance(steps_in, list):
            return {"status": "error", "steps": [], "cost_usd": 0.0,
                    "error": "workflow 'steps' must be a list"}

        enforce_gate = _load_enforce_gate()
        results: list[Dict[str, Any]] = []
        max_iterations = None
        if context is not None:
            limits = getattr(context, "limits", None)
            if limits is not None:
                try:
                    max_iterations = int(limits.max_iterations)
                except (TypeError, ValueError):
                    max_iterations = None

        for index, step in enumerate(steps_in):
            # Runtime limits: wall clock first, then iteration cap.
            if context is not None:
                remaining = getattr(context, "remaining_seconds", None)
                if callable(remaining) and remaining() <= 0:
                    return self._finish(results, "partial",
                                        "workflow wall-clock budget "
                                        "exhausted")
            if (max_iterations is not None
                    and len(results) >= max_iterations):
                return self._finish(results, "partial",
                                    f"workflow stopped at the runtime "
                                    f"iteration cap ({max_iterations} "
                                    f"steps)")
            results.append(self._run_step(step, index, enforce_gate,
                                          adapter))

        return self._finish(results, None, None)

    @staticmethod
    def _finish(results, status, error):
        """Overall status from the per-step results."""
        if status is None:
            if not results:
                status = "completed"
            elif all(s["status"] == "ok" for s in results):
                status = "completed"
            elif (not any(s["status"] == "ok" for s in results)
                    and not any(s["status"] == "pending-approval"
                                for s in results)):
                status = "error"
            else:
                status = "partial"
            if status == "error" and error is None:
                failed = [s["name"] for s in results
                          if s["status"] != "ok"]
                error = ("workflow error: failed steps: "
                         + (", ".join(failed) if failed else "unknown"))
            elif status == "partial" and error is None:
                pending = [s["name"] for s in results
                           if s["status"] == "pending-approval"]
                failed = [s["name"] for s in results
                          if s["status"] == "error"]
                parts = []
                if pending:
                    parts.append("pending-approval: " + ", ".join(pending))
                if failed:
                    parts.append("failed: " + ", ".join(failed))
                error = "workflow partial: " + "; ".join(parts)
        return {"status": status, "steps": results, "cost_usd": 0.0,
                "error": error}

    @staticmethod
    def _run_step(step, index, enforce_gate, adapter) -> Dict[str, Any]:
        """Run one step: gate first, then mock work (or the n8n
        adapter when the gate allows it — it never does for
        n8n_trigger today). Never raises."""
        if not isinstance(step, dict):
            return {"id": f"step-{index + 1}",
                    "name": f"step-{index + 1}", "kind": "",
                    "status": "error",
                    "output": None,
                    "evidence": ["step is not a dict"],
                    "cost_usd": 0.0,
                    "error": f"step {index + 1} must be a dict, got "
                             f"{type(step).__name__}"}
        name = _step_name(step, index)
        kind = str(step.get("kind") or "").strip().lower()
        tool = str(step.get("tool") or step.get("tool_name") or "")

        try:
            gate_action = _gate_action_for_step(step)
            if enforce_gate is not None:
                verdict = enforce_gate(gate_action)
            else:
                verdict = _fallback_gate(gate_action)
        except Exception as exc:  # noqa: BLE001 — gate failure fails closed
            return {"id": name, "name": name, "kind": kind,
                    "status": "pending-approval", "output": None,
                    "evidence": ["gate check failed — failing closed"],
                    "cost_usd": 0.0,
                    "error": f"gate error: {type(exc).__name__}: {exc}"}

        if not verdict.get("allowed", False):
            return {"id": name, "name": name, "kind": kind,
                    "status": "pending-approval",
                    "output": {"status": "pending-approval",
                               "gate": verdict},
                    "evidence": ["gate: pending-approval — never "
                                 "executed",
                                 str(verdict.get("reason", ""))],
                    "cost_usd": 0.0}

        # Gate allowed. An n8n step goes through the adapter; every
        # other allowed step is mock draft work.
        is_n8n = (kind in ("n8n", "webhook", "n8n_trigger")
                  or tool == "n8n_trigger")
        if is_n8n:
            return WorkflowEngine._run_n8n_step(step, name, kind, adapter)

        try:
            output = {
                "status": "draft-ready",
                "mock": True,
                "draft_only": True,
                "step": name,
                "kind": kind or "draft",
                "input": step.get("input"),
                "note": "[DRAFT] mock step — no live call, no "
                        "send/publish/spend/delete/deploy.",
            }
            return {"id": name, "name": name, "kind": kind,
                    "status": "ok", "output": output,
                    "evidence": ["mock-path: no live call",
                                 f"kind={kind or 'draft'}"],
                    "cost_usd": 0.0}
        except Exception as exc:  # noqa: BLE001 — a step never breaks execute()
            return {"id": name, "name": name, "kind": kind,
                    "status": "error", "output": None,
                    "evidence": [f"{type(exc).__name__}: {exc}"],
                    "cost_usd": 0.0,
                    "error": f"{type(exc).__name__}: {exc}"}

    @staticmethod
    def _run_n8n_step(step, name, kind, adapter) -> Dict[str, Any]:
        """An n8n step that passed the gate. Today the gate never
        allows ``n8n_trigger``, so this path is wiring for a future
        approved flow — it is exercised directly through the adapter
        (see n8n_adapter + test_double), not by smuggling a trigger
        past the gate."""
        if adapter is None:
            return {"id": name, "name": name, "kind": kind,
                    "status": "error", "output": None,
                    "evidence": ["gate allowed the step but no n8n "
                                 "adapter was supplied"],
                    "cost_usd": 0.0,
                    "error": "n8n step allowed but no adapter configured"}
        path = str(step.get("webhook_path") or step.get("path") or "")
        payload = step.get("payload")
        if isinstance(step.get("input"), dict):
            payload = step["input"].get("payload", payload)
            path = (step["input"].get("webhook_path")
                    or step["input"].get("path") or path)
        if not path:
            return {"id": name, "name": name, "kind": kind,
                    "status": "error", "output": None,
                    "evidence": ["n8n step needs a webhook_path"],
                    "cost_usd": 0.0,
                    "error": "n8n step needs a webhook_path"}
        if not isinstance(payload, dict):
            payload = {}
        try:
            result = adapter.trigger_via_webhook(path, payload)
            return {"id": name, "name": name, "kind": kind,
                    "status": "ok",
                    "output": {"triggered": True, "result": result},
                    "evidence": ["n8n adapter: webhook triggered",
                                 f"path={path}"],
                    "cost_usd": 0.0}
        except Exception as exc:  # noqa: BLE001 — adapter failure is a step error
            return {"id": name, "name": name, "kind": kind,
                    "status": "error", "output": None,
                    "evidence": [f"{type(exc).__name__}: {exc}"],
                    "cost_usd": 0.0,
                    "error": f"{type(exc).__name__}: {exc}"}


def execute(workflow, context=None, adapter=None) -> Dict[str, Any]:
    """Module-level convenience: ``WorkflowEngine().execute(...)``."""
    return WorkflowEngine().execute(workflow, context=context,
                                    adapter=adapter)
