"""Bounded agent loop — Talvenor Master OS, Phase 3 (local-first).

Runs a step function inside hard limits. Before EACH iteration the
loop checks, in order: wall-clock timeout, cost limit, iteration
cap. A step that raises never crashes the caller — the run ends
with status "error" and the exception text recorded.

Stdlib only. No network, no spend, no keys.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .context import RuntimeContext
from .limits import CostTracker, RuntimeLimits


@dataclass
class RunResult:
    """Outcome of one bounded run."""

    status: str  # completed | iteration_limit | timeout | cost_limit | error
    iterations: int
    cost_usd: float
    output: object
    trace: list[dict] = field(default_factory=list)
    error: str | None = None


class BoundedLoop:
    """Executes ``step_fn(context)`` until it finishes or a limit hits.

    step_fn contract: return a dict with
      {"status": "continue" | "done" | "error",
       "output": <anything>, "cost_usd": <float, optional>,
       "error": <str, optional — used when status is "error">}.
    """

    def __init__(self, limits: RuntimeLimits | None = None) -> None:
        self.limits = limits if limits is not None else RuntimeLimits()

    def run(self, step_fn, context: RuntimeContext) -> RunResult:
        limits = context.limits
        tracker = CostTracker(limits.max_cost_usd)
        tracker.record(context.cost_usd)

        def finish(status: str, output: object = None, error: str | None = None) -> RunResult:
            return RunResult(
                status=status,
                iterations=context.iteration,
                cost_usd=tracker.cost,
                output=output,
                trace=list(context.trace),
                error=error,
            )

        while True:
            # Check 1 — wall-clock timeout.
            if context.remaining_seconds() <= 0:
                context.log_step("limit", "timeout",
                                 "wall-clock budget exhausted")
                return finish("timeout", error="wall-clock timeout")
            # Check 2 — cost limit.
            if tracker.exceeded():
                context.log_step("limit", "cost_limit",
                                 f"cost ${tracker.cost:.4f} over cap "
                                 f"${limits.max_cost_usd:.4f}")
                return finish("cost_limit",
                              error=f"cost ${tracker.cost:.4f} exceeded cap "
                                    f"${limits.max_cost_usd:.4f}")
            # Check 3 — iteration cap.
            if context.iteration >= limits.max_iterations:
                context.log_step("limit", "iteration_limit",
                                 f"reached {limits.max_iterations} iterations")
                return finish("iteration_limit",
                              error=f"iteration limit {limits.max_iterations} reached")

            try:
                result = step_fn(context)
            except Exception as exc:  # noqa: BLE001 — loop must never crash caller
                context.log_step("step", "error", f"{type(exc).__name__}: {exc}")
                return finish("error", error=f"{type(exc).__name__}: {exc}")

            if not isinstance(result, dict):
                context.log_step("step", "error",
                                 "step_fn must return a dict")
                return finish("error",
                              error="step_fn must return a dict")

            try:
                cost = float(result.get("cost_usd", 0.0) or 0.0)
            except (TypeError, ValueError):
                context.log_step("step", "error", "cost_usd must be numeric")
                return finish("error", error="cost_usd must be numeric")
            if cost < 0:
                # Negative cost is a step error, same pattern as the
                # non-numeric-cost check above. NOT a raising guard in
                # CostTracker.record (that call sits outside the loop's
                # try/except and must never crash the caller).
                context.log_step("step", "error",
                                 "cost_usd must not be negative")
                return finish("error",
                              error="cost_usd must not be negative")
            tracker.record(cost)
            context.cost_usd = tracker.cost
            context.iteration += 1

            # Cost check AFTER recording: a step returning "done" AND
            # reporting cost over the cap must end "cost_limit", never
            # "completed". (The top-of-loop check only catches cost
            # recorded by an earlier step.)
            if tracker.exceeded():
                context.log_step("limit", "cost_limit",
                                 f"cost ${tracker.cost:.4f} over cap "
                                 f"${limits.max_cost_usd:.4f}")
                return finish("cost_limit",
                              error=f"cost ${tracker.cost:.4f} exceeded cap "
                                    f"${limits.max_cost_usd:.4f}")

            status = result.get("status", "continue")
            output = result.get("output")
            context.log_step("step", str(status), output)

            if status == "done":
                return finish("completed", output=output)
            if status == "error":
                err = result.get("error") or (str(output) if output is not None
                                              else "step reported error")
                return finish("error", output=output, error=str(err))
            if status != "continue":
                return finish("error", output=output,
                              error=f"unknown step status {status!r}")
            # status == "continue": loop again; the top checks enforce limits.
