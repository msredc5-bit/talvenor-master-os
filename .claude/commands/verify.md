---
description: Run the Master OS check suites and report PASS/FAIL numbers
---

Verify the repo is healthy. No live calls, no keys needed. From the repo
folder, run each and report the exact numbers:

1. `python scripts\check_providers.py` — expect 56/56.
2. `python scripts\check_live_brain.py` (no `--live`) — expect 13/13.
3. `python scripts\check_dev_brain.py` — expect 13/13.
4. `python -m pytest tests/ -q` — expect 230 passed, 2 skipped,
   1 xfailed. If pytest is missing: `pip install pytest` first.

Report in Bengali, short: each suite's PASS/FAIL count. If anything
fails, show the failing check names and stop — do not claim the repo is
healthy. Fix only what Boss asks you to fix, one thing at a time.
