"""Runtime limits and cost tracking — Talvenor Master OS, Phase 3 (local-first).

Stdlib only. No network, no spend, no keys. A $0 cost cap is the
default: ANY paid cost counts as exceeded, so a paid step can never
slip through silently.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuntimeLimits:
    """Hard bounds for one bounded agent run.

    max_iterations: maximum steps the loop may execute.
    wall_clock_seconds: wall-clock budget from run start.
    max_cost_usd: cost budget; 0.0 (the default) means no paid cost
        at all is allowed.
    """

    max_iterations: int = 10
    wall_clock_seconds: float = 60.0
    max_cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.max_iterations < 0:
            raise ValueError("RuntimeLimits: max_iterations must be >= 0")
        if self.wall_clock_seconds < 0:
            raise ValueError("RuntimeLimits: wall_clock_seconds must be >= 0")
        if self.max_cost_usd < 0:
            raise ValueError("RuntimeLimits: max_cost_usd must be >= 0")


class LimitExceeded(Exception):
    """Raised when a runtime limit is hit.

    ``kind`` is one of "iterations", "timeout", or "cost".
    """

    KINDS = ("iterations", "timeout", "cost")

    def __init__(self, kind: str, message: str | None = None) -> None:
        if kind not in self.KINDS:
            raise ValueError(f"LimitExceeded: unknown kind {kind!r}")
        self.kind = kind
        super().__init__(message or f"runtime limit exceeded: {kind}")


class CostTracker:
    """Tracks spend against a hard cap.

    ``exceeded()`` is True when recorded cost is strictly greater
    than the cap. With the default cap of 0.0, ANY cost > 0 counts
    as exceeded — a paid cost is never allowed through silently.
    """

    def __init__(self, max_cost_usd: float = 0.0) -> None:
        if max_cost_usd < 0:
            raise ValueError("CostTracker: max_cost_usd must be >= 0")
        self.max_cost_usd = float(max_cost_usd)
        self.cost = 0.0

    def record(self, usd: float) -> float:
        """Add a cost (in USD) and return the running total."""
        self.cost += float(usd)
        return self.cost

    def exceeded(self) -> bool:
        """True when recorded cost is over the cap."""
        return self.cost > self.max_cost_usd

    def remaining(self) -> float:
        """Budget left before the cap is hit (may go negative)."""
        return self.max_cost_usd - self.cost
