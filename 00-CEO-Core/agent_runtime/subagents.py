"""Subagent manager — Phase 3 (local-first) bounded agent runtime.

Runs ONE subagent at a time (spawn) or several concurrently
(run_parallel), each inside its own isolated child context taken from
the parent RuntimeContext (``00-CEO-Core/agent_runtime/context.py``,
Worker A). A subagent is a plain callable ``fn(child_context,
input_data)``; it runs on the MOCK path only — no live API calls, no
network, no gated actions, $0 cost.

Contract
--------
Every subagent result is a plain dict with EXACTLY these keys::

    {"name": str, "status": "ok" | "error" | "timeout",
     "output": <anything JSON-able>, "evidence": [str, ...],
     "cost_usd": float}

Rules:
  * a fn raising an exception -> status "error", never crashes the manager;
  * a fn running past its timeout -> status "timeout" (ThreadPoolExecutor
    + future.result(timeout=...); the thread itself cannot be killed, it
    finishes in the background — a CPython limitation, documented here);
  * a single subagent failing never fails a parallel batch;
  * the child context is isolated: mutating it must not touch the parent
    or a sibling child (RuntimeContext.child_context() deep-copies).

Stdlib only. No network, no keys, no file writes.
"""

from __future__ import annotations

import concurrent.futures
import copy
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:  # Worker A owns context.py; duck-typed use only (see spawn()).
    from .context import RuntimeContext  # noqa: F401  (type hint / documentation)
except ImportError:  # pragma: no cover - context.py not built yet
    RuntimeContext = None  # type: ignore[assignment]

__all__ = [
    "SubagentSpec",
    "SubagentResult",
    "RESULT_KEYS",
    "VALID_STATUSES",
    "validate_result",
    "SubagentManager",
    "run_parallel",
]

RESULT_KEYS = ("name", "status", "output", "evidence", "cost_usd")
VALID_STATUSES = ("ok", "error", "timeout")

# Backwards-friendly alias: the contract is a plain dict.
SubagentResult = Dict[str, Any]


@dataclass
class SubagentSpec:
    """What to run: a name, a callable, and a wall-clock timeout."""

    name: str
    fn: Callable[[Any, Any], Any]
    timeout_seconds: float = 30.0


def validate_result(result: Any) -> bool:
    """Check a subagent result against the contract.

    Returns True when valid, otherwise raises ValueError naming the
    violated key (missing key, extra key, bad status, non-list
    evidence, non-numeric cost).
    """
    if not isinstance(result, dict):
        raise ValueError(f"result must be a dict, got {type(result).__name__}")
    for key in RESULT_KEYS:
        if key not in result:
            raise ValueError(f"result is missing required key {key!r}")
    for key in result:
        if key not in RESULT_KEYS:
            raise ValueError(f"result has unexpected extra key {key!r}")
    if result["status"] not in VALID_STATUSES:
        raise ValueError(
            f"result['status'] must be one of {list(VALID_STATUSES)}, "
            f"got {result['status']!r}"
        )
    if not isinstance(result["evidence"], list):
        raise ValueError(
            f"result['evidence'] must be a list, "
            f"got {type(result['evidence']).__name__}"
        )
    cost = result["cost_usd"]
    if isinstance(cost, bool) or not isinstance(cost, (int, float)):
        raise ValueError(
            f"result['cost_usd'] must be numeric, got {cost!r}"
        )
    if not isinstance(result["name"], str):
        raise ValueError(
            f"result['name'] must be a str, got {type(result['name']).__name__}"
        )
    return True


def _normalize_return(spec: SubagentSpec, value: Any) -> SubagentResult:
    """Normalize whatever fn returned into a contract-shaped dict.

    A dict that already carries contract keys is used (missing keys get
    defaults); anything else — a plain value, or a dict with no contract
    keys — becomes the "output" with empty evidence and $0 cost.
    """
    if isinstance(value, dict) and any(k in value for k in RESULT_KEYS):
        return {
            "name": spec.name,
            "status": value.get("status", "ok"),
            "output": value.get("output"),
            "evidence": value.get("evidence", []),
            "cost_usd": float(value.get("cost_usd", 0.0)),
        }
    return {
        "name": spec.name,
        "status": "ok",
        "output": value,
        "evidence": [],
        "cost_usd": 0.0,
    }


class SubagentManager:
    """Runs subagents, each in an isolated child context."""

    def spawn(self, spec: SubagentSpec, input_data: Any,
              parent_context: Any) -> SubagentResult:
        """Run ONE subagent and return its validated result.

        Builds an isolated child context from
        ``parent_context.child_context()``, calls
        ``spec.fn(child_context, input_data)``, and wraps the return into
        a validated SubagentResult. Never raises for a subagent failure:
        exception -> "error", overrun -> "timeout".
        """
        child_context = parent_context.child_context()
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            future = pool.submit(spec.fn, child_context, input_data)
            try:
                value = future.result(timeout=spec.timeout_seconds)
            except concurrent.futures.TimeoutError:
                # Do NOT use `with pool:` here: its shutdown(wait=True)
                # would wait out the overrunning thread and defeat the
                # timeout. The thread finishes in the background instead.
                pool.shutdown(wait=False, cancel_futures=True)
                return {
                    "name": spec.name,
                    "status": "timeout",
                    "output": (
                        f"Subagent {spec.name!r} exceeded its timeout "
                        f"of {spec.timeout_seconds:g}s — no result; "
                        "the run keeps finishing in the background and "
                        "its output is discarded."
                    ),
                    "evidence": [],
                    "cost_usd": 0.0,
                }
            pool.shutdown(wait=True)  # future already done; returns at once
        except Exception as exc:  # noqa: BLE001 - a subagent must never crash the manager
            pool.shutdown(wait=False, cancel_futures=True)
            return {
                "name": spec.name,
                "status": "error",
                "output": f"{type(exc).__name__}: {exc}",
                "evidence": [],
                "cost_usd": 0.0,
            }
        try:
            result = _normalize_return(spec, value)
            validate_result(result)
        except (ValueError, TypeError) as exc:
            return {
                "name": spec.name,
                "status": "error",
                "output": f"Invalid subagent result: {exc}",
                "evidence": [],
                "cost_usd": 0.0,
            }
        return result

    def run_parallel(self, specs: List[SubagentSpec], inputs: List[Any],
                     parent_context: Any) -> List[SubagentResult]:
        """Run all specs concurrently, each in its own child context.

        Returns list[SubagentResult] in input order. A single subagent
        failing never fails the batch (spawn() already converts every
        failure into an "error"/"timeout" result).
        """
        if len(specs) != len(inputs):
            raise ValueError(
                f"specs ({len(specs)}) and inputs ({len(inputs)}) must "
                "have the same length"
            )
        if not specs:
            return []
        results: List[Optional[SubagentResult]] = [None] * len(specs)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures = [
                pool.submit(self.spawn, spec, data, parent_context)
                for spec, data in zip(specs, inputs)
            ]
            for i, future in enumerate(futures):
                try:
                    results[i] = future.result()
                except Exception as exc:  # noqa: BLE001 - belt and braces; spawn() should not raise
                    results[i] = {
                        "name": specs[i].name,
                        "status": "error",
                        "output": f"{type(exc).__name__}: {exc}",
                        "evidence": [],
                        "cost_usd": 0.0,
                    }
        return [r for r in results if r is not None]


def run_parallel(specs: List[SubagentSpec], inputs: List[Any],
                 parent_context: Any) -> List[SubagentResult]:
    """Module-level convenience: run specs concurrently via a fresh manager."""
    return SubagentManager().run_parallel(specs, inputs, parent_context)
