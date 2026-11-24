"""Workflow engine package — Talvenor Master OS, local-first Phase 4.

Public API (each import is defensive — Workers A/B build
``queue``/``scheduler`` in parallel, so if a sibling module is
missing the package must still import):

  queue       — task queue hardening (DLQ, recovery scan) [Worker A]
  scheduler   — real job definitions, created PAUSED [Worker B]
  engine      — provider-independent workflow engine [Worker C]
  n8n_adapter — localhost-only n8n REST + webhook adapter [Worker C]
  test_double — local n8n test double for tests/checks [Worker C]

Stdlib only. $0. No live calls, no keys, no send/publish/spend/
delete/deploy. Scheduler jobs stay PAUSED until Boss activates
one with an explicit approval.
"""

from __future__ import annotations

import importlib

__all__ = [
    "queue",
    "scheduler",
    "engine",
    "WorkflowEngine",
    "execute",
    "N8nAdapter",
    "N8nError",
    "N8nTestDouble",
]

# NOTE: the public names below are assigned via importlib (not
# ``from . import X``) on purpose — pre-assigning ``engine = None``
# etc. would make ``from . import engine`` return the None
# attribute instead of importing the submodule.
queue = None
scheduler = None
engine = None
WorkflowEngine = None
execute = None
N8nAdapter = None
N8nError = None
N8nTestDouble = None

_missing = []


def _load(submodule, *attrs):
    """Import ``workflow_engine.<submodule>`` and bind attrs.

    Returns True on success. On ImportError the names stay None
    and the submodule is recorded in _missing — the package still
    imports (a sibling built in parallel may simply not exist
    yet)."""
    try:
        module = importlib.import_module(
            f".{submodule}", __package__)
    except ImportError:
        _missing.append(submodule)
        return False
    for attr in attrs:
        globals()[attr] = getattr(module, attr, None)
    globals()[submodule] = module
    return True


_load("queue")
_load("scheduler")
_load("engine", "WorkflowEngine", "execute")
_load("n8n_adapter", "N8nAdapter", "N8nError")
_load("test_double", "N8nTestDouble")
