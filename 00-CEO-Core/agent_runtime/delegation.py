"""Delegation engine — Phase 3 (local-first) bounded agent runtime.

Splits one task into steps and runs each step as a subagent through a
SubagentManager. MOCK ONLY: every step returns a DRAFT result — no live
API calls, no network, no gated actions, $0 cost. A gated action is
never executed here; see gate.py (a gated step comes back as a
pending-approval draft, never as an execution).

Status rules for execute():
  * "completed" — every step returned "ok";
  * "partial"   — some steps "ok", some "error"/"timeout";
  * "error"     — no step "ok", or decomposition itself failed.
execute() never raises on a step failure.

Stdlib only. No network, no keys, no file writes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .subagents import SubagentManager, SubagentResult, SubagentSpec, validate_result

__all__ = ["DelegationEngine", "decompose_task"]


def decompose_task(task: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Split a task into steps.

    A task with a "steps" list gives one step per entry:
    {"name", "kind", "input"} — name defaults to f"step-{i}", kind to
    "default", input is the step dict itself. Any other task gives a
    single step named after the task id/name, or "only-step".
    """
    if not isinstance(task, dict):
        raise ValueError(f"task must be a dict, got {type(task).__name__}")
    steps = task.get("steps")
    if isinstance(steps, list):
        out: List[Dict[str, Any]] = []
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                raise ValueError(f"task['steps'][{i}] must be a dict")
            out.append({
                "name": step.get("name") or f"step-{i}",
                "kind": step.get("kind") or "default",
                "input": step,
            })
        return out
    if steps is not None:
        raise ValueError("task['steps'] must be a list when present")
    name = task.get("id") or task.get("name") or "only-step"
    return [{"name": name, "kind": "default", "input": task}]


def _run_step(child_context: Any, step_input: Dict[str, Any]) -> Dict[str, Any]:
    """The mock step worker: draft only, never a live call or gated action.

    Returns a contract-shaped draft dict. The child_context is accepted
    (isolated per step) but deliberately unused — a mock step reads
    nothing live and writes nothing anywhere.
    """
    _ = child_context  # isolated context available; mock step needs nothing from it
    name = step_input.get("name", "step")
    kind = step_input.get("kind", "default")
    return {
        "name": name,
        "status": "ok",
        "output": (
            f"[DRAFT] step {name!r} (kind={kind!r}) — draft only. "
            "No live call, no send/publish/spend/delete/deploy."
        ),
        "evidence": ["mock-path: no live call", f"kind={kind}"],
        "cost_usd": 0.0,
    }


class DelegationEngine:
    """Decomposes a task and runs its steps as parallel subagents."""

    def __init__(self, manager: Optional[SubagentManager] = None):
        self.manager = manager if manager is not None else SubagentManager()

    def decompose(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split a task into steps (see decompose_task)."""
        return decompose_task(task)

    def execute(self, task: Dict[str, Any],
                parent_context: Any) -> Dict[str, Any]:
        """Run a task's steps via the manager and summarize.

        Returns {"status": "completed"|"partial"|"error",
        "steps": [SubagentResult, ...], "cost_usd": total}.
        Never raises on a step failure; a decomposition failure returns
        status "error" with an empty steps list.
        """
        try:
            steps = self.decompose(task)
        except (ValueError, TypeError):
            return {"status": "error", "steps": [], "cost_usd": 0.0}

        specs: List[SubagentSpec] = []
        inputs: List[Any] = []
        for step in steps:
            timeout = step["input"].get("timeout_seconds", 30.0)
            try:
                timeout = float(timeout)
            except (TypeError, ValueError):
                timeout = 30.0
            specs.append(SubagentSpec(
                name=step["name"], fn=_run_step, timeout_seconds=timeout))
            inputs.append(step["input"])

        results: List[SubagentResult] = self.manager.run_parallel(
            specs, inputs, parent_context)

        # Validate every result contract; an invalid one becomes "error".
        checked: List[SubagentResult] = []
        for spec, result in zip(specs, results):
            try:
                validate_result(result)
                checked.append(result)
            except ValueError as exc:
                checked.append({
                    "name": spec.name,
                    "status": "error",
                    "output": f"Invalid subagent result: {exc}",
                    "evidence": [],
                    "cost_usd": 0.0,
                })
        results = checked

        total_cost = sum(float(r["cost_usd"]) for r in results)
        ok_count = sum(1 for r in results if r["status"] == "ok")
        if results and ok_count == len(results):
            status = "completed"
        elif ok_count > 0:
            status = "partial"
        else:
            status = "error"
        return {"status": status, "steps": results, "cost_usd": total_cost}
