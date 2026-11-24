"""Runtime context — Talvenor Master OS, Phase 3 (local-first).

Holds one run's task, limits, clock, cost, and trace. The task is
deep-copied on entry so the caller's dict is never mutated, and
``child_context()`` returns a fully isolated copy: mutating the
child's trace or cost leaves the parent untouched.

Stdlib only. No network, no spend, no keys.
"""

from __future__ import annotations

import copy
import time

from .limits import RuntimeLimits


class RuntimeContext:
    """State for a single bounded agent run."""

    def __init__(self, task: dict, limits: RuntimeLimits | None = None) -> None:
        if not isinstance(task, dict):
            raise TypeError("RuntimeContext: task must be a dict")
        self.task: dict = copy.deepcopy(task)
        self.limits: RuntimeLimits = limits if limits is not None else RuntimeLimits()
        self.task_id: str = str(self.task.get("id") or "untitled")
        self.iteration: int = 0
        self.started_at: float = time.monotonic()
        self.deadline: float = self.started_at + float(self.limits.wall_clock_seconds)
        self.cost_usd: float = 0.0
        self.trace: list[dict] = []

    def log_step(self, step: str, status: str, detail: object = None) -> None:
        """Append one entry to the run trace."""
        self.trace.append(
            {
                "step": str(step),
                "status": str(status),
                "detail": detail,
                "iteration": self.iteration,
                "elapsed_seconds": round(self.elapsed(), 6),
            }
        )

    def elapsed(self) -> float:
        """Seconds since the run started."""
        return time.monotonic() - self.started_at

    def remaining_seconds(self) -> float:
        """Seconds left before the wall-clock deadline (never negative)."""
        return max(0.0, self.deadline - time.monotonic())

    def child_context(self) -> "RuntimeContext":
        """Return an ISOLATED deep copy of this context.

        The child gets its own task dict, trace list, and cost, so
        mutating the child never changes the parent. Limits are
        shared (they are never mutated by a run). The child inherits
        the parent's deadline (the earlier of the two): a child must
        never outlive the parent's wall-clock budget.
        """
        child = RuntimeContext(copy.deepcopy(self.task), self.limits)
        child.task_id = self.task_id
        child.iteration = self.iteration
        child.cost_usd = self.cost_usd
        child.trace = copy.deepcopy(self.trace)
        child.deadline = min(self.deadline, child.deadline)
        return child
