"""CEO reporting generator — Talvenor Master OS, Phase 7 (Worker B).

Builds the daily / weekly / monthly Founder CEO report from the REAL
store files and audit records only. Stdlib only, read-only on the store
(no store file is ever written here), no network, no send, no publish,
no spend, no deployment.

Rule (same as scripts/sync_status.py): a missing or unreadable source
is reported as "unknown" — never invented, never silently treated as 0
unless the file exists and is genuinely empty. Every figure cites its
source file.

Periods are rolling windows ending at ``end`` (default: now, UTC):
  - "daily":   last 24 hours
  - "weekly":  last 7 days
  - "monthly": last 30 days — a 30-day window, NOT a calendar month.

The Phase 4 scheduler already defines a paused ``weekly-ceo-report``
job (00-CEO-Core/workflow_engine/scheduler.py); this generator is what
that job would draft. This module never activates any job.
"""

from .report import (  # noqa: F401
    PERIODS,
    generate_report,
    render_markdown,
)

__version__ = "1.0.0"
