"""Phase 8 pytest layout — Talvenor Master OS (Worker C, 2026-11-25).

Created by Worker C: no tests/ directory existed when Phase 8
started (Worker A was to create it in parallel; this is the single
layout — do NOT create a second one).

Path setup follows how scripts/check_*.py import 00-CEO-Core
modules: 00-CEO-Core goes on sys.path so `import control`,
`import audit`, `import reply_triage`, `import tenant_schema`,
`from lead_chain import ChainRunner` and
`from ceo_reporting.report import generate_report` all work.

RULES for every test in this directory:
  * Temp stores only (tmp_path). NEVER the real store/ — no test
    reads or writes ~/workspace/talvenor-master-os/store/.
  * TEST fixtures only (lead_chain.fixtures, tenant_schema
    .synthetic_tenant). Never real records from store/leads.json.
  * No network, no live LLM calls, no send/publish/spend/delete/
    deploy. $0 everywhere (cost_usd is always 0.0).
  * Plain asserts; pytest markers only where a gap is documented
    (see test_scenarios.py::test_scenario_d_qa_failure).
"""
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CEO_CORE = REPO_ROOT / "00-CEO-Core"
SCRIPTS_DIR = REPO_ROOT / "scripts"
DEPARTMENTS_DIR = REPO_ROOT / "01-Agency-Department" / "departments"

# Order matters: 00-CEO-Core FIRST (its approval_centre.py is the
# importable module; scripts/approval_centre.py is a CLI script of
# the same name that imports it — scripts/ must never shadow it).
for _p in (str(REPO_ROOT), str(DEPARTMENTS_DIR), str(SCRIPTS_DIR),
           str(CEO_CORE)):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

# The repo root must be findable for modules that resolve store paths
# relative to it (e.g. ceo_reporting._collect_config / _collect_gate0
# derive repo_root = dirname(store_dir), so temp stores work as-is).
os.environ.setdefault("TALVENOR_MASTER_OS_ROOT", str(REPO_ROOT))
