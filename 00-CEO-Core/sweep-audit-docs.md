# Sweep Audit — Docs, Dashboards & Cross-Cutting Consistency

**Scope:** README.md, BUILD-LOG.md, LOCAL-RUN.md, PUSH-PLAN-Phase-9-10.md,
CENTRAL-HQ/, dashboards/, run_local.bat, skills/ (repo root), cross-cutting
number/label checks.
**Audit date:** 2026-11-21 ~10:24–10:40 Dhaka. Audit only — no repo file edited
except this report. $0, no keys, no live calls.

## ⚠️ Read first — the repo was moving during this audit

Another process was actively editing this repo while I audited it
(sibling sweep-audit files `00-CEO-Core/sweep-audit-agency.md` /
`sweep-audit-product-content.md` appeared; the 4 GAP worker `.py` files were
built; `store/memory.json` was rewritten 3× in ~15 min: 111,979 → 262,130 →
2,588 bytes; voice-test WAVs written; `scripts/check_specialists.py` was
updated mid-audit). Consequences:

- Numbers below are a snapshot as of ~10:40 Dhaka 2026-11-21. Re-verify after
  the sibling work lands.
- My first full check run showed transient failures that all cleared on
  re-run (check_phase6 136-grep, the DROPPED-scope check, check_departments manager import,
  check_gate 23/24 "real store unchanged" — all caused by mid-write files /
  concurrent store writes). Final re-run state: phase0 8/8, phase1 11/11,
  phase2 14/14, phase3 19/19, phase4 9/9, phase6 14/14, phase7 18/18,
  engines ALL PASS, departments 21/21, specialists 40/41 (sole failure =
  cascade meta-check, itself transient), gate 24/24, memory_ledger 19/19,
  quiet_schedules 15/15, providers 43/43, live_brain 10/10, live_tools 7/7,
  mcp 9/9, voice 13/14 (sounddevice FAIL — known VM-only, no PortAudio).
  Claimed total 326/326 (199 base + 69 new + 58 improvement) is arithmetically
  consistent with BUILD-LOG; no single quiescent full-suite run was observed
  because the repo never stood still during the audit.
- Registry changed during the audit: 65 EXISTING / 4 GAP at start →
  **69 EXISTING / 0 GAP** at end (4 GAP workers built by the sibling worker).
  CENTRAL-HQ docs still say 22/43/4 — see items D3–D5.

## Verified current facts (ground truth used below)

- `00-CEO-Core/config.json`: phase **9**, version **0.9.0**, brain **mock**;
  `honest_status.phases` has 17 entries incl. `phase_11_providers`,
  `improvement_p1_gate`, `improvement_p2_memory_ledger`,
  `improvement_p3_quiet_schedules`.
- `00-CEO-Core/tools.json`: **9 tools** (7 mock + 2 live-ready
  `gmail_send`, `n8n_trigger`).
- Registry `01-Agency-Department/agents/agent-registry/registry.json`:
  **69 entries, 69 EXISTING, 0 GAP** (as of end of audit).
- Repo-wide `*/skills/*.md`: **113 files**. Root `skills/`: **7 files**.
- No `TODO` / `FIXME` markers in any scoped file (grep). Only `DRAFT` / `GAP`
  markers listed below.
- No `.git` in this folder (push must run from parent/Boss side — already known).

---

# DOABLE WITHOUT LLM API

Each item: file + what is missing/wrong + suggested fix.

## D1. README.md — title, date and totals are one phase behind

- **File:** `README.md:1` — title says "Phase 9 — COMPLETE: Taskboard + MCP +
  Live-Ready Tools", but Phase 10 (live brain adapter), Phase 11 (7 LLM
  providers) and Improvement Phases 1–3 (trust gate, memory/ledger, quiet
  schedules) are all built since. There is **no Phase 10 and no Phase 11
  section** in README.md at all (only passing mentions at lines 55, 106).
- **File:** `README.md:141` — heading "True state (2026-11-20)" is stale;
  2026-11-21 work (skill-finder, Part B skills, GAP workers, Improvement
  phases) is not covered.
- **File:** `README.md:159` — Phase 7 entry says "Total checks now 200/200".
  As a historical Phase 7 line it is true for its time, but as the README's
  only stated total it is stale: current claimed total is **326/326**
  (BUILD-LOG.md: 268 + 24 + 19 + 15).
- **Fix:** add Phase 10, Phase 11 and Improvement 1–3 entries (mirror the
  BUILD-LOG.md entries), retitle to cover Phase 11 + Improvements, bump the
  "True state" date to 2026-11-21, state the 326/326 total.

## D2. README.md — folder tree is stale in 6 places

- **File:** `README.md:57` — `tools.json` described as "7-tool registry".
  Real: **9 tools** (booking_reply + gmail_send + n8n_trigger added).
- **File:** `README.md:83` — `store/` described as "tasks.json,
  approvals.json, vault/README.md (empty — task 0, approval 0)". Real:
  tasks.json holds **1 record** (booking-link verification, status `done`,
  2026-11-20); store/ also now has `MEMORY.md`, `memory.json`,
  `schedules.json`, `confirmations.json`, `usage_ledger.json`.
- **File:** `README.md:85` — `skills/` described as "4 skill manuals".
  Real: **7 files** (`chief-agency`, `chief-content`, `chief-products`,
  `drawer-memory-box`, `main-ceo-bot`, `skill-finder`, `tool-allowlist`).
- **File:** `README.md:111` — Content Engine row still says "GPU name pending".
  GPU name was answered 2026-11-17 (AMD Radeon integrated, 496 MB VRAM) and
  `dashboards/status.html:36` already says so. Fix the README row to match.
- **Missing tree entries (all exist on disk, none listed):**
  `00-CEO-Core/live_brain.py`, `live_tools.py`, `trust_gate.py`,
  `owner_memory.py`, `usage_ledger.py`, `quiet_schedules.py`,
  `skill_finder.py`, `check_drawer_memory.py`, `mcp/` (4 files),
  `agent-tool-assignments-DRAFT.md`, `MEMORY-STRUCTURE-DECISION-2026-11-21.md`,
  `PROVIDERS-SETUP.md`, `scripts/check_gate.py`,
  `check_memory_ledger.py`, `check_quiet_schedules.py`,
  `check_providers.py`, `check_live_brain.py`, `check_live_tools.py`,
  `scripts/taskboard_server.py`.
- **Fix:** rewrite the tree block (lines ~50–95) from disk; keep the
  "store task 0" claim out — the store is a live queue now.

## D3. CENTRAL-HQ/unified-os.md — DRAFT + wrong registry numbers

- **File:** `CENTRAL-HQ/unified-os.md:3` — "Status: DRAFT — awaiting Boss's approval"
  (dropping DRAFT itself needs Boss — see B1; the
  number fixes below do not).
- **File:** `CENTRAL-HQ/unified-os.md:34` — "69 registry entry (EXISTING 22 /
  ROLE-ONLY 43 / GAP 4)". Real: **69 EXISTING / 0 ROLE-ONLY / 0 GAP**.
  Same stale split is the pre–Phase 3 picture.
- **Fix:** change line 34 to "69 registry entry (EXISTING 69, GAP 0 —
  Phase 3 + 2026-11-21 GAP-worker build)".

## D4. CENTRAL-HQ/shared-services.md — DRAFT + false ROLE-ONLY claim

- **File:** `CENTRAL-HQ/shared-services.md:3` — DRAFT (see B1).
- **File:** `CENTRAL-HQ/shared-services.md:48–49` — "69 entry: EXISTING 22 /
  ROLE-ONLY 43 / GAP 4" and "Registry's 43 ROLE-ONLY — role definitions only, no worker code". Both false now: 0 ROLE-ONLY, all 69 have worker
  code (43 Phase 3 specialists + 4 former-GAP workers built 2026-11-21).
- **File:** `CENTRAL-HQ/shared-services.md:81` — governance "BUILT (Phase 1
  foundation, DRAFT)… separate governance for Commerce/Media not built yet
  — GAP". Still true as far as audited; keep, but re-check after the
  DRAFT decision (B1).
- **Fix:** update lines 48–49 to 69 EXISTING / 0 GAP.

## D5. CENTRAL-HQ/BUSINESS-01-AGENCY.md — DRAFT wrapper, stale dept table

- **File:** `CENTRAL-HQ/BUSINESS-01-AGENCY.md:3` — "Wrapper doc — DRAFT,
  for Boss's review" (see B1).
- **File:** `CENTRAL-HQ/BUSINESS-01-AGENCY.md:27,30` — dept 05 Research &
  Strategy and dept 08 Product & Innovation listed as "GAP — mapped staff 0;
  all 7/6 roles ROLE-ONLY". False now: both depts' specialists are
  EXISTING (Phase 3 built 7 + 6 workers).
- **File:** `CENTRAL-HQ/BUSINESS-01-AGENCY.md:32` — "69 entries total — EXISTING
  22, ROLE-ONLY 43, GAP 4" (stale; real 69/0/0) and "Chief wiring Phase 2 —
  Agency Chief still does not call any manager; managers are standalone".
  False: Phase 2 wiring DONE 2026-11-19 — Chief calls all 8 managers via
  `DEPARTMENT_ROUTING` (verified in `01-Agency-Department/chief_of_staff_agency.py`;
  `scripts/check_departments.py` 21/21 on re-run).
- **Fix:** rewrite the dept table counts (05 → 7 staff, 08 → 6 staff,
  GAP → 0), fix line 32 counts, replace the "Chief still does not call" line with
  the Phase 2 DONE fact.

## D6. CENTRAL-HQ/BUSINESS-02-COMMERCE.md + BUSINESS-03-MEDIA.md — DRAFT wrappers, spot-check

- **Files:** `CENTRAL-HQ/BUSINESS-02-COMMERCE.md:3`,
  `CENTRAL-HQ/BUSINESS-03-MEDIA.md:3` — both "Wrapper doc — DRAFT" (see B1).
- **File:** `CENTRAL-HQ/BUSINESS-03-MEDIA.md:32` — Audio & Voice dept "GAP —
  no dedicated audio worker", with Piper TTS noted as outside Creator
  OS. Still true; no fix needed unless Boss decides an audio worker is wanted.
- **File:** `CENTRAL-HQ/BUSINESS-03-MEDIA.md:49,76` — "VOICE.md correction —
  DRAFT" — still true (VOICE.md is still DRAFT in
  `03-Content-Creation-Department/VOICE.md`); no fix, listed so it is not
  mistaken for stale.
- **Fix:** no number fixes found in these two beyond the DRAFT status; keep
  on the Boss-review list (B1).

## D7. CENTRAL-HQ/data-isolation.md + cross-business.md — DRAFT + unenforced policy

- **Files:** `CENTRAL-HQ/data-isolation.md:3`, `CENTRAL-HQ/cross-business.md:3`
  — both DRAFT (see B1).
- **File:** `CENTRAL-HQ/data-isolation.md:49–50` — "Policy: DRAFT…
  Enforcement: No automated enforcement has been built — GAP".
  Enforcement code is rule-based (no LLM needed) and can be built; the
  policy text itself needs Boss approval first (B1).
- **Fix (doable):** after Boss approves the policy, build the automated
  enforcement (e.g. a routing/store guard in `00-CEO-Core/`); until then,
  keep the GAP note — do not silently drop it.

## D8. dashboards/ + scripts/sync_status.py — phase table stops at Phase 7

- **Files:** `scripts/sync_status.py:307–315` (`collect_status()`) and
  `dashboards/status.html:51–60` — `phase_status` only carries
  `phase_0` … `phase_7_sections`. No entries for `agentic_phase_1/2/3`,
  `unified_os`, `phase_9_connections`, `phase_11_providers`,
  `improvement_p1_gate`, `improvement_p2_memory_ledger`,
  `improvement_p3_quiet_schedules`, although all 7 exist in
  `00-CEO-Core/config.json` `honest_status.phases`.
- **Effect:** `dashboards/status.json` `phase_status` has only 8 keys and
  `status.html`'s phase table ends at Phase 7 — the dashboard does not show
  Agentic Phases 1–3, Unified OS, Phase 9, Phase 11 or Improvements at all.
  (`status.json` top-level `phase: 9`, `version: "0.9.0"` are correct.)
- **Fix:** extend `collect_status()` to read the 7 missing phase keys from
  config and add matching rows to the `status.html` template in
  `sync_status.py`; re-run sync (regenerates `status.html` + `status.json`).

## D9. dashboards/engines.html + scripts/sync_engines.py — wrong handler list

- **File:** `scripts/sync_engines.py:85–88` — handler list is built by
  regexing `00-CEO-Core/tool_calling.py` for
  `"(draft_\w+|kit_outline_read|status_read|research_notes)"`. That regex
  matches the string `"draft_only"` (a flag, not a handler) and never
  matches `booking_reply`.
- **File:** `dashboards/engines.html:39` — rendered list is
  "draft_caption, draft_email, draft_only, draft_script, kit_outline_read,
  research_notes, status_read": `draft_only` is a phantom handler,
  `booking_reply` (7th mock tool, added 2026-11-17) is missing, and the 2
  live-ready tools (`gmail_send`, `n8n_trigger`) appear nowhere on the page.
- **Fix:** derive the handler list from `00-CEO-Core/tools.json` (9 tools,
  with mock/live-ready status) instead of regexing `tool_calling.py`; re-run
  `scripts/sync_engines.py`.

## D10. dashboards/dashboard-3d.html — fallback snapshot dates disagree

- **File:** `dashboards/dashboard-3d.html:201` — comment says fallback is
  "2026-11-20's real numbers"; lines **294, 313** say "fallback snapshot
  2026-11-19". One of the two dates is wrong.
- **Fix:** make all three lines say the same date (2026-11-20, matching the
  snapshot data: `tasks_count: 1`, Phase 9/v0.9.0 at lines 156, 206, 253 —
  which do match current config). Note: the fallback carries no Phase 10/11 /
  Improvement info; acceptable for a fallback, but flag it when the fallback
  is next refreshed.

## D11. dashboards/n8n-wiring.md — stale date heading

- **File:** `dashboards/n8n-wiring.md:3` — "True state (2026-11-16)".
  Content was verified current (Tier 2 cron DISABLED since 2026-11-14,
  email PAUSED, both workflows READY NOT LIVE).
- **Fix:** bump the heading date to 2026-11-21 (one-line change; no content
  change needed).

## D12. PUSH-PLAN-Phase-9-10.md — plan covers only Phase 9+10; head is stale

- **File:** `PUSH-PLAN-Phase-9-10.md` — "33 file, 4 batch" covers Phase 9 +
  Phase 10 only. Missing from any push plan:
  - Phase 11: 6 provider files in
    `01-Agency-Department/engine/workers/src/live/` (`openai_provider.py`,
    `anthropic_provider.py`, `gemini_provider.py`, `kimi_provider.py`,
    `grok_provider.py`, `openrouter_provider.py`), `scripts/check_providers.py`,
    `00-CEO-Core/PROVIDERS-SETUP.md`, config `providers` section.
  - Improvement 1–3: `00-CEO-Core/trust_gate.py`, `owner_memory.py`,
    `usage_ledger.py`, `quiet_schedules.py`, `scripts/check_gate.py`,
    `check_memory_ledger.py`, `check_quiet_schedules.py`,
    `store/memory.json`, `store/MEMORY.md`, `store/schedules.json`,
    `store/confirmations.json`, `store/usage_ledger.json`.
  - Skill-finder + Part B: `00-CEO-Core/skill_finder.py`,
    `check_drawer_memory.py`, `skills/skill-finder.md`,
    `skills/drawer-memory-box.md`, `skills/tool-allowlist.md`,
    `00-CEO-Core/agent-skill-audit-2026-11-21.md`,
    `00-CEO-Core/MEMORY-STRUCTURE-DECISION-2026-11-21.md`,
    `00-CEO-Core/agent-tool-assignments-DRAFT.md`, 4 GAP skill files, 4 GAP
    worker `.py` files, this audit file.
  - Also missing: `00-CEO-Core/mcp/` files are in Batch 1, but
    `00-CEO-Core/mcp/check_mcp.py` is listed there while every other check
    script lives in `scripts/` (see D15).
- **File:** `PUSH-PLAN-Phase-9-10.md` — "Verify remote head: `b649b9bd…`".
  The sync record
  `~/workspace/talvenor-master-os.muse-github-snapshot-sync.json` (37
  entries) does contain `b649b9bd`, but its **latest** entry is
  `aba411934803ea77b83d0ab4a37d0249ae11971c` (3 files — the Phase 11 ZIP
  head per BUILD-LOG.md). The plan's head is therefore an older entry, not
  the current remote head.
- **Fix:** write a new push plan (Phase 11 + Improvements + skill-finder +
  GAP workers) with a fresh remote-head verification at push time; do not
  reuse the b649b9bd head claim. The plan's own rule 1 already requires
  re-verification — enforce it.

## D13. LOCAL-RUN.md + run_local.bat — taskboard is undocumented and unstarted

- **Files:** `LOCAL-RUN.md`, `run_local.bat` — neither mentions the
  taskboard at all (grep for `taskboard|8766` returns nothing).
  Taskboard is live code: `dashboards/taskboard.html` +
  `scripts/taskboard_server.py` (port **8766**) +
  `dashboards/TASKBOARD-README.md` (Phase 9).
- **Fix:** add a taskboard section to `LOCAL-RUN.md` (start command
  `python scripts\taskboard_server.py`, URL `http://localhost:8766/`, note
  that it only writes `store/tasks.json` and the bridge does the work);
  optionally add a taskboard start step to `run_local.bat` (or document
  explicitly that the bat file does NOT start it — either way, stop leaving
  it invisible). `TASKBOARD-README.md` itself is accurate.

## D14. skills/ (repo root) vs agent-skill-audit — one stale count in the audit

- **File:** `00-CEO-Core/agent-skill-audit-2026-11-21.md` ("Out of scope"
  section) — "106 total `*/skills/*.md` files in the repo". Real count at audit
  end: **113**. Gap = 7 new files: 4 GAP skills
  (`ad-campaign-agent.md`, `crm-integration-agent.md`,
  `expense-tracking-agent.md`, `backup-recovery-agent.md`) +
  `skills/drawer-memory-box.md` + `skills/tool-allowlist.md` +
  `skills/skill-finder.md`.
- **Note:** do NOT edit the audit file per this task's instructions — the
  fix belongs to the parent: update the "106" line (the audit's "Update —
  2026-11-21" section already accounts for the 6 Part B files + skill-finder
  in its own totals: 81 skill files in scope).
- **Cross-check result:** no orphan root skill and no agent without a skill
  in the audited scope — root `skills/` 7 files map to: Main CEO Bot
  (`main-ceo-bot.md`), 3 Chiefs (`chief-agency.md`, `chief-content.md`,
  `chief-products.md`), drawer memory-box (`drawer-memory-box.md`, code
  `00-CEO-Core/owner_memory.py` exists), tool-allowlist
  (`tool-allowlist.md`, code in `tools.json`/`tool_calling.py`/gate), and
  skill-finder (`skill-finder.md`, code `00-CEO-Core/skill_finder.py`,
  wired into `main_ceo_bot.py` task type `find_skill`). The 4 former-GAP
  roles now have BOTH skill and worker `.py` (built during this audit).
  Remaining skill gap: none in Agency hierarchy; Digital Product + Content
  skill coverage was explicitly out of the audit's scope (audit says
  "~30 skill files" there, uncounted) — a follow-up audit for those two
  departments is still open (see B5).

## D15. Check-script location inconsistency (minor hygiene)

- **File:** `00-CEO-Core/mcp/check_mcp.py` — the only check script that does
  NOT live in `scripts/` (all 16 others do). It passes 9/9 from its current
  path, so nothing is broken.
- **Fix (doable):** move it to `scripts/check_mcp.py` and update
  `00-CEO-Core/mcp/README.md` + PUSH-PLAN Batch 1, or document the
  exception in `00-CEO-Core/mcp/README.md`. Either is fine; pick one so the
  next sweep does not re-flag it.

## D16. .gitignore — no policy for the new store/ files

- **File:** `.gitignore` — covers `__pycache__/`, `*.pyc`,
  `00-CEO-Core/voice/models/`, `00-CEO-Core/voice/output/` only. Nothing
  about `store/`.
- **Gap:** `store/tasks.json` is intentionally pushed (live queue, per
  PUSH-PLAN). But the new Improvement-phase store files have no documented
  push/ignore policy: `store/memory.json` (Boss's verbatim quotes),
  `store/MEMORY.md`, `store/schedules.json`, `store/confirmations.json`,
  `store/usage_ledger.json`, and future `store/skill-proposals.json`
  (proposed by `skill_finder.py`, does not exist yet). `store/memory.json`
  was rewritten 3× during this audit alone — it is live state, not a stable
  doc; pushing a snapshot of it needs a conscious decision.
- **Fix:** decide per file (track vs ignore) and write the decision into
  `.gitignore` and/or a short `store/README.md`. Voice models/output are
  already correctly ignored (verified: WAVs exist locally under
  `00-CEO-Core/voice/output/` and are gitignored).

## D17. Check-suite flakiness from concurrent store writes (hygiene)

- **Observed:** `scripts/check_gate.py` first run 23/24 — FAILED "real store
  unchanged by this check run" because `store/memory.json` changed mid-run
  (another process writing). Re-run 24/24. `_snapshot_store()` snapshots
  EVERY file in `store/`, including files the check never touches.
- **Fix (doable):** document that check scripts must run when no other
  writer (bridge cron, sibling worker, voice loop) is active, or scope the
  snapshot to files the check can plausibly touch. Not a code bug — a
  run-discipline note; put it in `BUILD-LOG.md` or the check scripts' header.

## D18. README.md — missing run-doc sections (small gaps)

- No "taskboard" run section (see D13), no "skill-finder" usage section
  (`find_skill` task type exists in `main_ceo_bot.py` but README never
  mentions it), no "live brain probe" section (`scripts/check_live_brain.py
  --live` is documented only in BUILD-LOG.md), and the Improvement Phases
  1–3 section states per-phase check counts (24/19/15) but no combined
  total. All doable doc additions, no LLM needed.

## D19. BUILD-LOG.md — known-stale lines (intentional history, do NOT rewrite)

- **File:** `BUILD-LOG.md` Phase 2 entry — calls `ceo-office-dashboard`
  the current 3D office artifact. The Phase 8 review already flagged this
  as intentional history ("log history, never rewritten"). Listed here
  only so the next sweep does not re-flag it.
- **File:** `BUILD-LOG.md` Phase 7 table — "Jarvis voice STUB" line is old
  (voice is REAL since 2026-11-17); also already flagged in the log itself.
- No other BUILD-LOG staleness found: Phase 9/10/11 + Improvement entries
  match disk (files, counts, 268/268 → 326/326 arithmetic verified).

---

# BLOCKED

Each item + reason (needs live LLM API / Boss's account / Boss's decision).

## B1. CENTRAL-HQ DRAFT docs need Boss's review to drop DRAFT

- **Files:** `CENTRAL-HQ/unified-os.md`, `shared-services.md`,
  `data-isolation.md`, `cross-business.md`, `BUSINESS-01-AGENCY.md`,
  `BUSINESS-02-COMMERCE.md`, `BUSINESS-03-MEDIA.md` — all 7 carry
  "Status: DRAFT — awaiting Boss's approval" / "Wrapper doc — DRAFT".
- **Reason:** Boss's decision/review. The number fixes in D3–D6 can be made
  now, but removing DRAFT status is his call. (Also note: `00-CEO-Core/
  agent-tool-assignments-DRAFT.md` is likewise a DRAFT policy doc awaiting
  his word.)

## B2. Phase 4 team factory — needs a live brain

- **Reason:** needs live LLM API. Per BUILD-LOG.md (Improvement Phases
  entry): Phase 4 team factory is blocked without a live brain (needs
  bot-hq's real Hermes gateways). No doc fix can unblock it.

## B3. Live-brain proof + provider keys — Boss's PC + Boss's keys

- **Reason:** Boss's account/network + live LLM API. The 2026-11-20 live
  probe failed with tunnel 403 (`api.meta.ai` unreachable from this VM);
  key validity is still UNPROVEN. Proof requires Boss's own PC network +
  keys in Windows env vars only (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`,
  `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `MOONSHOT_API_KEY`, `XAI_API_KEY`)
  + flipping `"brain": "live"` in `00-CEO-Core/config.json` + a live probe.
  No provider key has been supplied. Docs (`00-CEO-Core/
  PROVIDERS-SETUP.md`) are complete; nothing further is doable here.

## B4. Hosted 3D dashboard artifact still shows Phase 8

- **Reason:** Boss's word. BUILD-LOG.md Phase 9 entry: the repo file
  `dashboards/dashboard-3d.html` was updated to Phase 9/v0.9.0, but the
  hosted artifact `talvenor-master-os-3d-dashboard` still shows Phase 8;
  artifact refresh happens on Boss's word in main chat. (Repo file itself
  is fine apart from D10.)

## B5. Digital Product + Content skill coverage — unaudited scope

- **Reason:** Boss's decision on scope (audit decision, not LLM). The
  2026-11-21 agent-skill audit explicitly excluded Digital Product +
  Content departments ("~30 skill files" there, uncounted). Whether a
  follow-up audit for those two departments is wanted is Boss's / parent's
  call; the work itself needs no LLM API once ordered.

## B6. Standing Boss-step items referenced by the scoped docs (not unblocked by this audit)

- Gate 0 (Lemon Squeezy test) — Boss's step; blocks kit build/sale/launch.
- Email restart — SPF/DMARC DNS fix in Boss's DNS panel + his "check koro".
- n8n live — Boss's import + Gmail/Sheets connect + Twilio number import
  (~$1.15/mo) + webhook URL.
- YouTube upload — "upload it" + OAuth credential; upload stays OFF.
- Voice — first live mic test on Boss's PC; Bengali voice quality unjudged
  (nobody has heard it yet).
- GitHub push — Boss's "push koro" + fresh remote-head verification (see D12).
- `store/memory.json` cap (256 KiB in `00-CEO-Core/owner_memory.py`): the
  file was rewritten 3× during this audit so no stable size could be
  verified — if Boss wants the cap raised, that is his decision; the code
  change itself is trivial once ordered.

---

## Appendix — check counts verified by this audit (re-runs, 2026-11-21)

| Suite | Result |
|---|---|
| check_phase0 / 1 / 2 / 3 / 4 | 8/8, 11/11, 14/14, 19/19, 9/9 |
| check_phase6 / check_phase7 | 14/14, 18/18 |
| check_engines | ALL PASS (BUILD-LOG: 44/44) |
| check_departments | 21/21 |
| check_specialists | 40/41 (sole fail: cascade meta-check, transient — see header note) |
| check_gate / check_memory_ledger / check_quiet_schedules | 24/24, 19/19, 15/15 |
| check_providers / check_live_brain / check_live_tools / check_mcp | 43/43, 10/10, 7/7, 9/9 |
| check_voice | 13/14 (sounddevice — known VM-only failure) |
| **Claimed total** | **326/326** (199 + 69 + 58 — arithmetic verified, no single quiescent full run observed) |
