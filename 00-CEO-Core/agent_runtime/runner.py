"""Agent runtime entry point — Talvenor Master OS, Phase 3 (local-first).

``AgentRuntime.run_task`` builds a RuntimeContext and runs it through
BoundedLoop. The default step is a MOCK draft step: it may load a
skill read-only via skill_finder (only when the task carries a
"skill_query"), and it NEVER calls a live brain, sends, publishes,
spends, or deletes anything.

Delegation is lazy: the delegation engine (built in parallel by
Worker B) is imported inside run_task only. If the module is absent,
delegation is recorded as unavailable in the trace and the plain
loop runs instead — the runner never breaks on a missing module.

Workflow path (Phase 4, additive only): a task carrying a
"workflow" key (a dict with a "steps" list) runs its steps through
the workflow engine (workflow_engine/engine.py) instead of the
plain loop — still inside the runtime's limits (iterations, wall
clock, $0) and still behind the Phase 3 gate: a gated workflow
step comes back pending-approval, never executes. If the workflow
engine is not importable, the task falls back to the plain loop
and the miss is recorded in the trace.

Stdlib only. No network, no spend, no keys.
"""

from __future__ import annotations

from .context import RuntimeContext
from .limits import RuntimeLimits
from .loop import BoundedLoop, RunResult


def _mock_step(context: RuntimeContext) -> dict:
    """Default step: produce a DRAFT result, nothing live.

    Loads a skill read-only via skill_finder.load_skill_for_task
    ONLY when the task has a "skill_query". A missing finder (or a
    load failure) is tolerated — the draft is still produced with
    skill_loaded False.
    """
    task = context.task
    skill_loaded = False
    skill_name = None
    query = task.get("skill_query")
    if query:
        try:
            import skill_finder  # noqa: PLC0415 — lazy; 00-CEO-Core on sys.path
            found = skill_finder.load_skill_for_task(str(query))
            loaded = (found or {}).get("loaded")
            if loaded:
                skill_loaded = True
                skill_name = loaded.get("name")
        except Exception:  # noqa: BLE001 — skill load must never break a draft
            skill_loaded = False
            skill_name = None

    output = {
        "status": "draft-ready",
        "mock_brain": True,
        "draft_only": True,
        "task_id": context.task_id,
        "skill_loaded": skill_loaded,
        "skill": skill_name,
        "note": "MOCK draft — no live brain, nothing sent, published, "
                "spent, or deleted.",
    }
    context.log_step("mock_step", "done", output)
    return {"status": "done", "output": output, "cost_usd": 0.0}


class AgentRuntime:
    """Runs tasks inside hard limits (iterations, wall clock, $0 cost)."""

    def __init__(self, limits: RuntimeLimits | None = None) -> None:
        self.limits = limits if limits is not None else RuntimeLimits()

    def run_task(self, task: dict, step_fn=None, delegate: bool = False,
                 limits: RuntimeLimits | None = None) -> RunResult:
        """Run one task and return a RunResult.

        step_fn: optional custom step (same contract as BoundedLoop).
            When None, the MOCK draft step runs.
        delegate: when True AND the task has a non-empty "steps" list
            AND the delegation engine is importable, the task is
            delegated through it instead of the plain loop.
            Single-step tasks always use the loop.
        limits: optional per-task RuntimeLimits (default: self.limits).
        """
        run_limits = limits if limits is not None else self.limits
        context = RuntimeContext(task, run_limits)

        # Phase 4 workflow path (additive): a task carrying a
        # "workflow" dict runs through the workflow engine, still
        # bounded by this runtime's limits and the gate. A missing
        # engine falls back to the plain loop below.
        workflow = task.get("workflow") if isinstance(task, dict) else None
        if isinstance(workflow, dict) and workflow.get("steps") is not None:
            ran = self._try_workflow(task, workflow, context)
            if ran is not None:
                return ran
            context.log_step("workflow", "unavailable",
                             "WorkflowEngine not importable or failed; "
                             "falling back to the plain loop")

        steps = task.get("steps") if isinstance(task, dict) else None
        if delegate and isinstance(steps, list) and steps:
            delegated = self._try_delegate(task, context)
            if delegated is not None:
                return delegated
            context.log_step("delegation", "unavailable",
                             "DelegationEngine not importable or failed; "
                             "falling back to the plain loop")

        loop = BoundedLoop(run_limits)
        return loop.run(step_fn or _mock_step, context)

    def _try_workflow(self, task: dict, workflow: dict,
                      context: RuntimeContext) -> RunResult | None:
        """Try the Phase 4 workflow engine; return None to fall back
        to the plain loop.

        The engine exposes execute(workflow, context=None,
        adapter=None). It is imported lazily (00-CEO-Core on
        sys.path, same pattern as the skill_finder import in
        _mock_step). Any import/call failure returns None — the
        workflow path is best-effort, the loop is the fallback.
        The engine never executes a gated step (it consults the
        Phase 3 gate itself); no adapter is passed here, so no n8n
        step can trigger from the runtime at all.
        """
        try:
            from workflow_engine.engine import WorkflowEngine  # noqa: PLC0415
        except ImportError:
            return None
        try:
            result = WorkflowEngine().execute(workflow, context=context)
            return self._coerce_workflow_result(result, context)
        except Exception as exc:  # noqa: BLE001 — workflow must never break run_task
            context.log_step("workflow", "error",
                             f"{type(exc).__name__}: {exc}")
            return None

    @staticmethod
    def _coerce_workflow_result(result: object,
                                context: RuntimeContext) -> RunResult:
        """Normalise a workflow-engine return dict into a RunResult.

        Workflow dict {"status", "steps", "cost_usd"}:
        "completed" -> "completed", "partial"/"error" -> "error"
        (error text names the pending/failed steps, mirroring the
        delegation coercion). The output is the WHOLE workflow dict
        (steps evidence preserved); iterations = len(steps);
        cost_usd from the dict ($0).
        """
        if isinstance(result, RunResult):
            return result
        if isinstance(result, dict) and "steps" in result:
            steps = result.get("steps") or []
            if not isinstance(steps, list):
                steps = []
            raw_status = str(result.get("status", "completed"))
            pending = [str(s.get("name") or "?") for s in steps
                       if isinstance(s, dict)
                       and s.get("status") == "pending-approval"]
            failed = [str(s.get("name") or "?") for s in steps
                      if isinstance(s, dict)
                      and s.get("status") == "error"]
            if raw_status == "completed":
                status, error = "completed", result.get("error")
            elif raw_status == "partial":
                status = "error"
                parts = []
                if pending:
                    parts.append("pending-approval: " + ", ".join(pending))
                if failed:
                    parts.append("failed: " + ", ".join(failed))
                error = ("workflow partial: "
                         + ("; ".join(parts) if parts else "unknown"))
            elif raw_status == "error":
                status = "error"
                error = result.get("error") or (
                    "workflow error: failed steps: "
                    + (", ".join(failed) if failed else "unknown"))
            else:
                status = "error"
                error = f"unknown workflow status {raw_status!r}"
            try:
                cost = float(result.get("cost_usd", context.cost_usd)
                             or 0.0)
            except (TypeError, ValueError):
                cost = context.cost_usd
            return RunResult(
                status=status,
                iterations=len(steps),
                cost_usd=cost,
                output=result,
                trace=list(context.trace),
                error=error,
            )
        return RunResult(
            status="error",
            iterations=context.iteration,
            cost_usd=context.cost_usd,
            output=result,
            trace=list(context.trace),
            error="workflow engine returned an unexpected result",
        )

    def _try_delegate(self, task: dict, context: RuntimeContext) -> RunResult | None:
        """Try the delegation engine; return None to fall back to the loop.

        The engine exposes execute(task, parent_context) (Worker B),
        so that is probed first, then run_task, run, delegate.
        Any import/call failure returns None — delegation is
        best-effort, the loop is the fallback.
        """
        try:
            from .delegation import DelegationEngine  # noqa: PLC0415
        except ImportError:
            return None
        try:
            engine = DelegationEngine()
            for method_name in ("execute", "run_task", "run", "delegate"):
                method = getattr(engine, method_name, None)
                if callable(method):
                    try:
                        result = method(task, context)
                    except TypeError:
                        result = method(task)
                    return self._coerce_result(result, context)
            context.log_step("delegation", "error",
                             "DelegationEngine has no "
                             "execute/run_task/run/delegate method")
            return None
        except Exception as exc:  # noqa: BLE001 — delegation must never break run_task
            context.log_step("delegation", "error",
                             f"{type(exc).__name__}: {exc}")
            return None

    @staticmethod
    def _coerce_result(result: object, context: RuntimeContext) -> RunResult:
        """Normalise a delegation return value into a RunResult.

        Worker B's delegation dict {"status", "steps", "cost_usd"}:
        "completed" -> "completed", "partial" -> "error" (error text
        names the failed steps), "error" -> "error". The output is
        the WHOLE delegation dict (steps evidence preserved, not
        None); iterations = len(steps); cost_usd from the dict.
        """
        if isinstance(result, RunResult):
            return result
        if isinstance(result, dict):
            if "steps" in result:
                steps = result.get("steps") or []
                if not isinstance(steps, list):
                    steps = []
                raw_status = str(result.get("status", "completed"))
                failed = [str(s.get("name") or "?") for s in steps
                          if isinstance(s, dict)
                          and s.get("status") != "ok"]
                if raw_status == "completed":
                    status, error = "completed", result.get("error")
                elif raw_status == "partial":
                    status = "error"
                    error = ("delegation partial: failed steps: "
                             + (", ".join(failed) if failed else "unknown"))
                elif raw_status == "error":
                    status = "error"
                    error = result.get("error") or (
                        "delegation error: failed steps: "
                        + (", ".join(failed) if failed else "unknown"))
                else:
                    status = "error"
                    error = f"unknown delegation status {raw_status!r}"
                try:
                    cost = float(result.get("cost_usd", context.cost_usd)
                                 or 0.0)
                except (TypeError, ValueError):
                    cost = context.cost_usd
                return RunResult(
                    status=status,
                    iterations=len(steps),
                    cost_usd=cost,
                    output=result,
                    trace=list(context.trace),
                    error=error,
                )
            return RunResult(
                status=str(result.get("status", "completed")),
                iterations=int(result.get("iterations", context.iteration)),
                cost_usd=float(result.get("cost_usd", context.cost_usd) or 0.0),
                output=result.get("output"),
                trace=list(context.trace),
                error=result.get("error"),
            )
        return RunResult(
            status="completed",
            iterations=context.iteration,
            cost_usd=context.cost_usd,
            output=result,
            trace=list(context.trace),
        )
