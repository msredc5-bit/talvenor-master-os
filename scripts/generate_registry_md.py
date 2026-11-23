#!/usr/bin/env python3
"""Regenerate the agent registry markdown from registry.json (Phase 1).

registry.json is the single source of truth. registry.md is a GENERATED
view of it — never edit it by hand. Edit registry.json, then run:

  python3 scripts/generate_registry_md.py

The generator reproduces the hand-written registry.md's structure:
status table, LOCKED truths, per-department counts, per-department
role tables, the 8-manager section, and the update rules. The counts
table row ("| **Total** | **62** | ...") is computed from the JSON —
scripts/check_specialists.py asserts that exact row, so the generator
must keep producing it.

Deterministic: the "Generated" line uses registry.json's own mtime,
so re-running without a JSON change writes byte-identical output.

Stdlib only. No network, no send, no publish, no spend.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_JSON = os.path.join(
    ROOT, "01-Agency-Department", "agents", "agent-registry", "registry.json")
REGISTRY_MD = os.path.join(
    ROOT, "01-Agency-Department", "agents", "agent-registry", "registry.md")

STATUS_MEANINGS = """## What Status means (in this registry)

| Status | Meaning |
|---|---|
| EXISTING | The real worker/agent file is in the repo. Path given. Runs on mock brain ($0); no claim of live work. |
| ROLE-ONLY | Only the role definition. Skill `.md` exists or will be written — no worker code, no claim of live work. |
| GAP | Not built, and there is no plan yet. Why — written in notes. |
"""

LOCKED_TRUTHS = """## LOCKED truths (the basis of this registry)

- **Voice stack LIVE:** Vapi — Sophia, live receptionist, +1 (947) 223-0244, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3. Sophia is the production receptionist — she does no demo work.
- **Retell DROPPED 2026-10-26** — never production. `RetellBuilder` only makes a DRAFT plan; live stack is Vapi/Sophia. Ava was a demo agent — deleted from the new Vapi account; rebuild pending (Boss will bring a demo account).
- **DB = JSON store files** (`store/tasks.json`, `store/approvals.json`). CRM = n8n Cloud Data Tables — PLANNED, not live.
- **Calendar:** Google Calendar Appointment Schedule — booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time).
- **Brain = mock ($0);** live MetaSpark UNPROVEN.
- **Email PAUSED since 2026-11-14** (DNS fix pending). First mail 163. Paying client 0. Spend cap $0.
- **Gate words:** `ok` / `"post it"` / `send` / `go` / `"upload it"` — nothing is sent/published/spent/deleted without Boss's exact word.
- **Pricing LOCKED, internal only** — never quote it to a prospect. Dental/medical businesses are never a target — always DQ.
- **Brand Talvenor only.** No invented client, price, stat, testimonial, or guarantee.
- **Agency Chief wiring** (connecting 8 department managers to the Chief) **Phase 2 DONE** — done in this phase.
- **Phase 3 DONE 2026-11-19** — workers + skills built for 43 ROLE-ONLY specialists; all EXISTING (DRAFT only, mock brain). **2026-11-21** — workers + skills built for the remaining 4 GAP roles (Ad Campaign, CRM Integration, Expense Tracking, Backup & Recovery); now 47 specialists EXISTING, GAP 0.
- Existing Agency staff = **21** (15 workers + 6 section agents). This registry has 69 entries: 62 roles from the brief + 7 existing workers outside the brief.
"""

MANAGERS_SECTION = """## Department Managers (8) — verified in Phase 1, outside this registry's 69 entries

> **Verified 2026-11-19:** the 8 managers' `.py` + skill files are on disk (paths below). Status **EXISTING** — but **Chief wiring Phase 2 DONE** — the Agency Chief now calls them via DEPARTMENT_ROUTING; managers are DRAFT-only. They have no entry in `registry.json` (69 = 62 brief roles + 7 extra existing workers; the 8 managers are a separate list).

| # | Manager | Department | Status (verified) | Notes |
|---|---|---|---|---|
| M1 | Chief Growth Agent | 01 Sales & Growth | EXISTING — `01-Agency-Department/departments/01-sales-growth/manager/chief_growth_agent.py` (`manage_sales_growth`, gate `ok`); skill `departments/01-sales-growth/skills/chief-growth-agent.md` | Chief wiring Phase 2 DONE. |
| M2 | Marketing Director Agent | 02 Marketing | EXISTING — `01-Agency-Department/departments/02-marketing/manager/marketing_director_agent.py` (`manage_marketing`, gate `ok`); skill `departments/02-marketing/skills/marketing-director-agent.md` | Chief wiring Phase 2 DONE. |
| M3 | CTO / AI Engineering Agent | 03 AI Engineering | EXISTING — `01-Agency-Department/departments/03-ai-engineering/manager/cto_ai_engineering_agent.py` (`manage_ai_engineering`, gate `ok`); skill `departments/03-ai-engineering/skills/cto-ai-engineering-agent.md` | Chief wiring Phase 2 DONE. |
| M4 | COO / Client Operations Agent | 04 Client Operations | EXISTING — `01-Agency-Department/departments/04-client-operations/manager/coo_client_operations_agent.py` (`manage_client_operations`, gate `ok`); skill `departments/04-client-operations/skills/coo-client-operations-agent.md` | Chief wiring Phase 2 DONE. |
| M5 | Chief Strategy Agent | 05 Research & Strategy | EXISTING — `01-Agency-Department/departments/05-research-strategy/manager/chief_strategy_agent.py` (`manage_research_strategy`, gate `ok`); skill `departments/05-research-strategy/skills/chief-strategy-agent.md` | Chief wiring Phase 2 DONE. |
| M6 | CFO / Finance Agent | 06 Finance & Admin | EXISTING — `01-Agency-Department/departments/06-finance-admin/manager/cfo_finance_agent.py` (`manage_finance_admin`, gate `ok`); skill `departments/06-finance-admin/skills/cfo-finance-agent.md` | Chief wiring Phase 2 DONE. |
| M7 | Chief Quality & Security Agent | 07 Quality & Security | EXISTING — `01-Agency-Department/departments/07-quality-security/manager/chief_quality_security_agent.py` (`manage_quality_security`, gate `ok`); skill `departments/07-quality-security/skills/chief-quality-security-agent.md` | Chief wiring Phase 2 DONE. |
| M8 | Chief Innovation Agent | 08 Product & Innovation | EXISTING — `01-Agency-Department/departments/08-product-innovation/manager/chief_innovation_agent.py` (`manage_product_innovation`, gate `ok`); skill `departments/08-product-innovation/skills/chief-innovation-agent.md` | Chief wiring Phase 2 DONE. |

## How to update

1. When you make a new worker file: set status EXISTING, give the repo-relative path + gate, and update `registry.json` the same way — then run `python3 scripts/generate_registry_md.py` to regenerate this file.
2. When ROLE-ONLY becomes EXISTING, also give the skill file's path.
3. When an entry's status changes, write the date + reason in notes.
4. Never claim live work until a real run is verified in Boss's signed-in session.
"""

_WORKER_RE = re.compile(r"Worker: (\w+) \((\w+)\)")
_KIND_RE = re.compile(r"no brief counterpart \((\w+)\)")
_CLASS_RE = re.compile(r"^class (\w+)", re.M)
_TASK_KIND_RE = re.compile(r'task_kind = "([^"]+)"')


def _classes_in_file(path):
    """[(class name, task_kind)] for every worker class in the file,
    pairing each task_kind with the nearest class above it."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return []
    classes = [(m.group(1), m.start())
               for m in _CLASS_RE.finditer(text)]
    kinds = [(m.group(1), m.start())
             for m in _TASK_KIND_RE.finditer(text)]
    out = []
    for name, pos in classes:
        kind = ""
        for k, kpos in kinds:
            if kpos > pos:
                kind = k
                break
        out.append((name, kind))
    return out


def _worker_and_kind(entry):
    """(worker name, task kind) for a registry entry.

    The notes carry the kind — "Worker: X (kind)" for brief roles,
    "no brief counterpart (kind)" for the 7 extra workers. The worker
    file is read and the class is matched BY THAT KIND, because the
    engine worker files hold several classes each (taking the first
    class in the file would name the wrong worker). Falls back to the
    "Worker: X" name, then the role name."""
    notes = entry.get("notes", "") or ""
    m = _WORKER_RE.search(notes)
    kind = m.group(2) if m else ""
    if not kind:
        m = _KIND_RE.search(notes)
        kind = m.group(1) if m else ""
    worker_file = entry.get("worker_file", "") or ""
    if worker_file:
        classes = _classes_in_file(os.path.join(ROOT, worker_file))
        if kind:
            for name, k in classes:
                if k == kind:
                    return name, kind
        if len(classes) == 1:
            # Single-class worker file (all specialist files) — the
            # only class in it is the worker, whatever the notes say.
            return classes[0][0], classes[0][1] or kind
    if m and _WORKER_RE.search(notes):
        return _WORKER_RE.search(notes).group(1), kind
    return entry.get("role", ""), kind


def _notes_text(entry):
    """The notes column: the raw notes with the "Worker: X (kind);
    skill PATH." prefix (or the "Existing worker with no brief
    counterpart (kind)." prefix) stripped, so the worker/skill cell
    does not repeat itself."""
    notes = (entry.get("notes", "") or "").strip()
    notes = re.sub(r"^Worker: \w+ \(\w+\); skill \S+\.?\s*", "", notes)
    notes = re.sub(r"^Worker: \w+ \(\w+\)\.\s*", "", notes)
    notes = re.sub(r"^Existing worker with no brief counterpart "
                   r"\(\w+\)\.\s*", "", notes)
    return notes.replace("|", "/").strip()


def _dept_key(department):
    """'01 Sales & Growth' -> ('01', 'Sales & Growth')."""
    parts = (department or "").split(" ", 1)
    return parts[0], (parts[1] if len(parts) > 1 else department)


def generate(registry, generated_date):
    total = len(registry)
    n_exist = sum(1 for e in registry if e.get("status") == "EXISTING")
    n_role = sum(1 for e in registry if e.get("status") == "ROLE-ONLY")
    n_gap = sum(1 for e in registry if e.get("status") == "GAP")
    extra = sum(1 for e in registry
                if "no brief counterpart" in (e.get("notes") or ""))
    brief = total - extra

    lines = [
        "# Agent Registry — Talvenor Master OS, Agentic Agency Office (Phase 1)",
        "",
        f"**Generated:** {generated_date} from `registry.json` by "
        "`scripts/generate_registry_md.py` — do not edit by hand; edit "
        "`registry.json` and re-run the generator.",
        f"**Status:** {total} entries, {n_exist} EXISTING, {n_role} ROLE-ONLY, "
        f"{n_gap} GAP",
        "**Repo:** `talvenor-master-os` | **Department:** `01-Agency-Department`",
        "**Machine-readable copy:** `registry.json` (the source of truth; "
        "this file is its generated view)",
        "",
        "---",
        "",
        STATUS_MEANINGS.rstrip(),
        "",
        LOCKED_TRUTHS.rstrip(),
        "",
        "## Numbers at a glance",
        "",
        "| Department | Brief role | Extra existing worker | Total | EXISTING | ROLE-ONLY | GAP |",
        "|---|---|---|---|---|---|---|",
    ]
    departments = []
    seen = set()
    for entry in registry:
        if entry.get("department") not in seen:
            seen.add(entry.get("department"))
            departments.append(entry.get("department"))
    for dept in departments:
        entries = [e for e in registry if e.get("department") == dept]
        d_extra = sum(1 for e in entries
                      if "no brief counterpart" in (e.get("notes") or ""))
        d_exist = sum(1 for e in entries if e.get("status") == "EXISTING")
        d_role = sum(1 for e in entries if e.get("status") == "ROLE-ONLY")
        d_gap = sum(1 for e in entries if e.get("status") == "GAP")
        num, name = _dept_key(dept)
        lines.append(
            f"| {dept} | {len(entries) - d_extra} | {d_extra} | "
            f"{len(entries)} | {d_exist} | {d_role} | {d_gap} |")
    lines.append(
        f"| **Total** | **{brief}** | **{extra}** | **{total}** | "
        f"**{n_exist}** | **{n_role}** | **{n_gap}** |")
    lines.append("")
    lines.append("> QAEngineer is counted in two places (Dept 03 Testing & Debugging + Dept 07 Voice Quality Testing) — the same worker, shared. So EXISTING role-entries are 69, but separate workers are 68.")
    lines.append("")

    for dept in departments:
        entries = [e for e in registry if e.get("department") == dept]
        num, name = _dept_key(dept)
        lines.append(f"## Dept {num} — {name} ({len(entries)})")
        lines.append("")
        lines.append("| # | Role | Status | Worker / Skill | Gate | Notes |")
        lines.append("|---|---|---|---|---|---|")
        for i, entry in enumerate(entries, 1):
            worker, kind = _worker_and_kind(entry)
            worker_file = entry.get("worker_file", "")
            skill_file = entry.get("skill_file", "")
            if kind:
                worker_cell = (f"`{worker}` — `{worker_file}` (`{kind}`); "
                               f"skill `{skill_file}`")
            else:
                worker_cell = (f"`{worker}` — `{worker_file}`; "
                               f"skill `{skill_file}`")
            gate = entry.get("gate")
            gate_cell = f"`{gate}`" if gate else "— (no gate)"
            notes = _notes_text(entry)
            row_num = f"{int(num)}.{i}"
            lines.append(
                f"| {row_num} | {entry.get('role', '')} | "
                f"{entry.get('status', '')} | {worker_cell} | {gate_cell} | "
                f"{notes} |")
        lines.append("")

    lines.append(MANAGERS_SECTION.rstrip())
    lines.append("")
    return "\n".join(lines)


def main():
    with open(REGISTRY_JSON, "r", encoding="utf-8") as f:
        registry = json.load(f)
    if not isinstance(registry, list):
        print("generate_registry_md: registry.json is not a list",
              file=sys.stderr)
        return 1
    mtime = os.path.getmtime(REGISTRY_JSON)
    generated_date = datetime.fromtimestamp(
        mtime, tz=timezone.utc).strftime("%Y-%m-%d")
    text = generate(registry, generated_date)
    with open(REGISTRY_MD, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"generate_registry_md: {len(registry)} entries -> {REGISTRY_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
