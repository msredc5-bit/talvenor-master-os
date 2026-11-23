#!/usr/bin/env python3
"""Phase 5 check — thin wrapper around check_engines.py (Phase 1, Unified OS).

Phase 5 IS the engines check: there is no separate Phase 5 suite.
This file exists so `scripts/check_phase*.py` is complete (Phase 0–9)
and so the full-suite runner can call every phase by the same name.
It imports check_engines.main() and propagates its exit code — it
adds no checks of its own.

Stdlib only. No network, no send, no publish, no spend.
"""

import os
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

import check_engines  # noqa: E402


if __name__ == "__main__":
    sys.exit(check_engines.main())
