"""Lead chain package — Talvenor Master OS, local-first Phase 6.

The §10.C lead chain (brief lines 561-647) in sandbox mode:
``chain.py`` holds the 13-step table and the ``ChainRunner``;
``steps.py`` (Worker B) holds the per-step executors;
``fixtures.py`` holds TEST-only prospects; ``crm_dryrun.py``
(Worker B) wraps the real CRM adapter in dry-run mode.

Stdlib only. $0. No send/publish/spend/delete/deploy, no network.
"""

from __future__ import annotations

from .chain import CHAIN_STEPS, ChainRunner, run_lead_chain
from .fixtures import (
    FIXTURES,
    MEDIUM_TIER2_PROSPECT,
    STRONG_TIER1_PROSPECT,
    WEAK_INCOMPLETE_PROSPECT,
)

__all__ = [
    "CHAIN_STEPS",
    "ChainRunner",
    "run_lead_chain",
    "FIXTURES",
    "STRONG_TIER1_PROSPECT",
    "MEDIUM_TIER2_PROSPECT",
    "WEAK_INCOMPLETE_PROSPECT",
]
