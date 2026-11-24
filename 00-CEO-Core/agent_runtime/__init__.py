"""Bounded agent runtime — Talvenor Master OS, Phase 3 (local-first).

Public API:
  RuntimeLimits  — hard bounds (iterations, wall clock, $0 cost cap)
  LimitExceeded  — exception with .kind in {"iterations","timeout","cost"}
  CostTracker    — spend tracking; any cost over a 0.0 cap is exceeded
  RuntimeContext — per-run task/clock/cost/trace state (+ isolated child)
  BoundedLoop    — runs a step_fn inside the limits, never crashes caller
  RunResult      — run outcome (status, iterations, cost, output, trace)
  AgentRuntime   — entry point; default step is a MOCK draft, never live

Stdlib only. No network, no spend, no keys. Mock/dev-brain path only.
"""

from __future__ import annotations

from .context import RuntimeContext
from .limits import CostTracker, LimitExceeded, RuntimeLimits
from .loop import BoundedLoop, RunResult
from .runner import AgentRuntime

__all__ = [
    "RuntimeLimits",
    "LimitExceeded",
    "CostTracker",
    "RuntimeContext",
    "BoundedLoop",
    "RunResult",
    "AgentRuntime",
]
