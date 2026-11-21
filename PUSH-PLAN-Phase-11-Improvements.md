# PUSH PLAN — Phase 11 + Improvements 1–3 + Skill-finder + GAP workers (Talvenor Master OS)

**Status: READY — NOT PUSHED.** Push only on Boss's "push koro", in the main chat (Elora).
**Made:** 2026-11-21 Dhaka. **Repo:** msredc5-bit/talvenor-master-os, branch `main`.
**What this plan has:** Phase 11 (7 LLM providers) + Improvements 1–3 (trust gate, memory/ledger,
quiet schedules) + skill-finder + Part B skills + 4 GAP worker + Memory LIVE wiring +
docs-sweep (README, BUILD-LOG, CENTRAL-HQ, dashboards, run docs) — **50 file, 5 batch**.

## ⚠️ Remote head — must be verified FRESH at push time

- **The sync record's latest entry (verified 2026-11-21): `aba411934803ea77b83d0ab4a37d0249ae11971c`**
  (3 file: `00-CEO-Core/config.json`, `BUILD-LOG.md`, `README.md` — Phase 11 ZIP head).
- **The `b649b9bd` head in PUSH-PLAN-Phase-9-10.md is now STALE** — that is an old sync record entry,
  not the current remote head. `b649b9bd` must not be used in this plan.
- **Before pushing (before each batch):** verify the remote head with `list_commits` (read-only) —
  the remote head must == the sync record's latest head. If they do not match, **stop** and rebuild
  this plan.
- **Files already in the sync record:** the record's entries for Phase 11's provider files
  `c1fda4a7` (6 provider + `PROVIDERS-SETUP.md` + `check_providers.py` +
  `live_brain.py` + `brain.py`) and the `config.json`/`BUILD-LOG.md`/`README.md` entries
  are in `aba41193`. At push time, check which files are already on the remote and remove them from the batch
  — do not blindly push again. This mismatch (BUILD-LOG says "NOT PUSHED" yet the record has
  entries) must be resolved at push time, not by guessing.

## What will be pushed — 50 files, 5 batches (all UTF-8 text, no binary)

- **NEW 31:** 6 provider + PROVIDERS-SETUP.md + check_providers.py + trust_gate.py +
  owner_memory.py + usage_ledger.py + quiet_schedules.py + check_gate.py +
  check_memory_ledger.py + check_quiet_schedules.py + check_drawer_memory.py +
  MEMORY-STRUCTURE-DECISION doc + skill_finder.py + 3 root skill + agent-skill-audit doc +
  agent-tool-assignments-DRAFT.md + 4 GAP worker .py + store/README.md + 2 audit doc +
  this plan.
- **MODIFIED 19:** live_brain.py, brain.py, tool_calling.py (00), main_ceo_bot.py,
  chief_of_staff_agency.py, 01 engine tool_calling.py, README.md, BUILD-LOG.md,
  config.json, 3 CENTRAL-HQ doc, sync_engines.py, engines.html, dashboard-3d.html,
  n8n-wiring.md, LOCAL-RUN.md, run_local.bat, mcp/README.md.
- **No voice models/output (gitignored) or `__pycache__`. No keys/secrets.**
- **Phase 9 + Phase 10 files are not in this plan** — they are in PUSH-PLAN-Phase-9-10.md
  (33 files, 4 batches). If both plans are pushed together, batch order: Phase 9-10 first, then this plan.

## Batch 1/5 — Phase 11: providers (10 file, 8 NEW + 2 MOD)

Commit message: `Talvenor Master OS — Phase 11 (1/5): 6 LLM providers + setup guide`

1. `01-Agency-Department/engine/workers/src/live/openai_provider.py` (NEW)
2. `01-Agency-Department/engine/workers/src/live/anthropic_provider.py` (NEW)
3. `01-Agency-Department/engine/workers/src/live/gemini_provider.py` (NEW)
4. `01-Agency-Department/engine/workers/src/live/kimi_provider.py` (NEW)
5. `01-Agency-Department/engine/workers/src/live/grok_provider.py` (NEW)
6. `01-Agency-Department/engine/workers/src/live/openrouter_provider.py` (NEW)
7. `00-CEO-Core/PROVIDERS-SETUP.md` (NEW)
8. `scripts/check_providers.py` (NEW)
9. `00-CEO-Core/live_brain.py` (MOD — provider chain)
10. `00-CEO-Core/brain.py` (MOD — factory chain)

## Batch 2/5 — Improvements 1–3: gate + memory/ledger + schedules (10 file, 9 NEW + 1 MOD)

Commit message: `Talvenor Master OS — Improvements 1-3 (2/5): trust gate + memory/ledger + quiet schedules`

1. `00-CEO-Core/trust_gate.py` (NEW)
2. `00-CEO-Core/owner_memory.py` (NEW)
3. `00-CEO-Core/usage_ledger.py` (NEW)
4. `00-CEO-Core/quiet_schedules.py` (NEW)
5. `scripts/check_gate.py` (NEW)
6. `scripts/check_memory_ledger.py` (NEW)
7. `scripts/check_quiet_schedules.py` (NEW)
8. `00-CEO-Core/check_drawer_memory.py` (NEW)
9. `00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md` (NEW)
10. `00-CEO-Core/tool_calling.py` (MOD — trust pre-check + ledger threading)

## Batch 3/5 — Skill-finder + Part B skills + GAP workers (10 files, all NEW)

Commit message: `Talvenor Master OS — Skill-finder + GAP workers (3/5): 6 skills + 4 workers`

1. `00-CEO-Core/skill_finder.py` (NEW)
2. `skills/skill-finder.md` (NEW)
3. `skills/drawer-memory-box.md` (NEW)
4. `skills/tool-allowlist.md` (NEW)
5. `00-CEO-Core/agent-skill-audit-2026-11-21.md` (NEW)
6. `00-CEO-Core/agent-tool-assignments-DRAFT.md` (NEW)
7. `01-Agency-Department/departments/02-marketing/specialists/ad_campaign_agent.py` (NEW)
8. `01-Agency-Department/departments/03-ai-engineering/specialists/crm_integration_agent.py` (NEW)
9. `01-Agency-Department/departments/06-finance-admin/specialists/expense_tracking_agent.py` (NEW)
10. `01-Agency-Department/departments/07-quality-security/specialists/backup_recovery_agent.py` (NEW)

## Batch 4/5 — Memory wiring + docs sweep: core (10 files, all MOD)

Commit message: `Talvenor Master OS — Memory wiring + docs (4/5): CEO/Chief memory + README + CENTRAL-HQ`

1. `00-CEO-Core/main_ceo_bot.py` (MOD — memory wiring; the memory agent's work, push after landing)
2. `01-Agency-Department/chief_of_staff_agency.py` (MOD — memory wiring)
3. `01-Agency-Department/engine/tool_calling.py` (MOD — context + ledger_path forward)
4. `00-CEO-Core/config.json` (MOD — phase 11 + providers section + improvement phase entries + `phase_10_live_brain` entry)
5. `README.md` (MOD — Phase 9/10/11 + Improvement 1–3 + 326/326 total)
6. `BUILD-LOG.md` (MOD — Phase 9/10/11 + Improvement entries + run-discipline note)
7. `CENTRAL-HQ/unified-os.md` (MOD — registry 69 EXISTING / 0 GAP; DRAFT status unchanged)
8. `CENTRAL-HQ/shared-services.md` (MOD — registry 69 EXISTING / 0 GAP; DRAFT status unchanged)
9. `CENTRAL-HQ/BUSINESS-01-AGENCY.md` (MOD — dept 05/08 staff + Phase 2 DONE; DRAFT status unchanged)
10. `scripts/sync_engines.py` (MOD — handler list now from tools.json, 9 tools)

## Batch 5/5 — Docs sweep: dashboards + run docs + audits + this plan (10 files, 4 NEW + 6 MOD)

Commit message: `Talvenor Master OS — Docs sweep (5/5): dashboards + run docs + store policy + push plan`

1. `dashboards/engines.html` (MOD — regenerate with sync_engines.py, 9 handlers)
2. `dashboards/dashboard-3d.html` (MOD — fallback snapshot date 2026-11-20)
3. `dashboards/n8n-wiring.md` (MOD — heading date 2026-11-21)
4. `LOCAL-RUN.md` (MOD — taskboard section)
5. `run_local.bat` (MOD — does not run the taskboard, explicit note)
6. `00-CEO-Core/mcp/README.md` (MOD — check_mcp.py location exception)
7. `store/README.md` (NEW — store push policy)
8. `00-CEO-Core/COMPLETION-SWEEP-AUDIT-2026-11-21.md` (NEW)
9. `00-CEO-Core/sweep-audit-docs.md` (NEW)
10. `PUSH-PLAN-Phase-11-Improvements.md` (NEW — this file)

## Not in this plan (intentional)

- **store live-state file** (`store/memory.json`, `store/MEMORY.md`, `store/schedules.json`,
  `store/confirmations.json`, `store/usage_ledger.json`) — in no push plan; push only
  on Boss's word (policy: `store/README.md`). `store/tasks.json` is in the Phase 9-10 plan.
- **sweep-audit-agency.md / sweep-audit-product-content.md / sweep-audit-ceocore.md** —
  will go in Workstream 1/2/3's plan, not this one.
- **Workstream 1/2/3's code files** (orphan wiring, helper script, quiet-schedule runner,
  MCP entry point, approve.py, etc.) — will go in their own plan.
- **Phase 4 team factory** — blocked without a live brain; no code exists.

## Push rules (per snapshot-push.md)

1. Before each batch, verify remote head == sync-record head (list_commits, read-only).
2. Per batch: make a NUL-delimited manifest file outside the source dir (e.g. `/tmp/push-11-imp-batch-N.txt`), then `github push-files` once.
3. After each batch, append an entry to `~/workspace/talvenor-master-os.muse-github-snapshot-sync.json`, then verify the remote head (new head == record head).
4. No binary files — all UTF-8 text. Do not send `__pycache__`.
5. If any batch fails, do not run the next batch — fix it first.
6. When all batches are done, tell Boss the new head.
7. **The brain is still mock** — pushing will not change that; going live needs Boss's key + the "live" flip + a probe (a separate step).
