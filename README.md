# Talvenor Master OS — the real system (Phase 11 + Improvements 1–3 COMPLETE: Live Brain adapter + 8 LLM providers + Trust Gate + Memory/Ledger + Quiet Schedules — brain still mock)

**What this is:** the folder of Boss's 3 businesses' real operating system. It is
not a picture or a mock — Phase 0's skeleton + CEO Core + approval
gateway really works.

## 3 businesses (only these 3 — 136 DROPPED)

1. **Agency** — Talvenor AI Receptionist, for US home-service businesses (MAIN)
2. **Digital Product** — Vet No-Show Recovery Kit, $49 one-time (Gate 0 remaining)
3. **Content Creation Engine** — Creator OS / ToolPilot @ToolPilotai69

## Unified OS layer — Central HQ (2026-11-19)

One HQ (00-CEO-Core: Main CEO Bot + Jarvis voice + Approval Gate + ONE mock
brain), below it 3 Business OS — separate Chiefs, separate departments, separate
data, but CEO/Dashboard/Finance/Governance are one. The name "TALVENOR UNIFIED OS"
is only the architecture layer's name (in docs) — the repo's name has not changed, it is not a new repo.
- **CENTRAL-HQ/** — unified-os.md (master map + audit) + shared-services.md
  (10 shared departments → real things) + data-isolation.md (DATA policy:
  agency/commerce/media separate, no cross-read without Boss's permission) +
  cross-business.md (internal project rules) + BUSINESS-01-AGENCY.md +
  BUSINESS-02-COMMERCE.md + BUSINESS-03-MEDIA.md (wrapper docs, not code)
- **Commerce truth:** Amazon GATED (until 5 clients + $5K MRR), Etsy
  CLOSED (Bangladesh), Shopify PARKED (Boss's direct project), Dropshipping
  RESEARCH-ONLY, the real digital product = Vet Kit $49 (Gate 0 NOT PASSED)
- **Dashboard:** a new "Unified OS — 3 Business OS" card in status.html
  (from sync_status.py, numbers from the real files) — dashboard-3d.html untouched
- **Remaining:** Phase 3 specialists DONE 2026-11-19 (see "Agentic Agency
  Office Phase 3" below); Commerce/Media OS specialist builds remaining —
  Gate 0 / upload OFF / $0 cap as they are

## Hierarchy (Boss's definition, 2026-11-16)

1. **Conversation starts: Jarvis** — Boss talks with Jarvis.
2. **Jarvis is connected to the super intelligent second brain — Main CEO Bot.**
3. **The Main CEO Bot maintains everything.** 3 systems run from the second brain:
   - Agency Office
   - Digital Product Business Office
   - Creator OS / Content Machine and Engine

Boss → Jarvis (voice) → Main CEO Bot (second brain) → 3 Chiefs of Staff →
worker → results return to the Main CEO Bot → Boss's approval if needed.

**Jarvis and the Main CEO Bot are separate** — Jarvis only listens/speaks (voice engine),
brain Main CEO Bot (second brain system).

## Folder

```
talvenor-master-os/
├── 00-CEO-Core/            # brain + gate + config + shared tool-calling core
│   ├── main_ceo_bot.py         # REAL (router)
│   ├── human_approval_gateway.py  # REAL (approve/reject)
│   ├── brain.py                # REAL (Phase 6 + Phase 10 + Phase 11 — BrainFactory: mock default / live via LiveBrainAdapter, loud mock fallback; provider chain: openrouter → meta → mock; live probe 2026-11-20 tunnel-403 BLOCKED, key unproven)
│   ├── live_brain.py           # REAL (Phase 10 — LiveBrainAdapter: provider chain + loud mock fallback; live probe 2026-11-20 tunnel-403 FAILED, $0, key UNPROVEN; brain still mock)
│   ├── live_tools.py           # REAL (Phase 9 — gmail_send + n8n_trigger, CODE ONLY, gated, never executes)
│   ├── trust_gate.py           # REAL (Improvement 1 — rule-based trust_check + ConfirmationStore)
│   ├── owner_memory.py         # REAL (Improvement 2 + Memory LIVE — quote-verified owner memory, central store + box)
│   ├── usage_ledger.py         # REAL (Improvement 2 — $0 ledger, mock always $0.00)
│   ├── quiet_schedules.py      # REAL (Improvement 3 — watchMarker, quiet schedule)
│   ├── skill_finder.py         # REAL (2026-11-21 — local skill search + DRAFT proposals; find_skill task type)
│   ├── check_drawer_memory.py  # REAL (Memory check 26/26)
│   ├── mcp/                    # REAL (Phase 9 — mcp_server.py + mcp_client.py + check_mcp.py 9/9 + README.md; check_mcp.py is the only check script not in scripts/)
│   ├── tool_calling.py         # REAL (Phase 5 — ToolRegistry + dispatcher, 9 handler: 7 mock + 2 live-ready gated)
│   ├── tools.json              # REAL (registry of 9 tools — 7 mock + gmail_send/n8n_trigger live-ready, gated)
│   ├── agent-tool-assignments-DRAFT.md  # DRAFT policy (Boss's review remaining)
│   ├── agent-skill-audit-2026-11-21.md # skill audit (81-file scope; 113 */skills/*.md in total in the repo)
│   ├── MEMORY-STRUCTURE-DECISION-2026-11-21.md  # memory structure decided on merit (central store + box)
│   ├── PROVIDERS-SETUP.md  # Phase 11 — 8 providers' keys + env var guide (a key never goes in a file)
│   ├── jarvis_voice.py         # REAL (2026-11-17 — Piper+Vosk/sherpa, offline, $0; same 3 functions)
│   ├── voice/                  # REAL (2026-11-17) — speak.py (Piper TTS), listen.py (Vosk en + sherpa-onnx bn), loop.py (listen → brain → speak + gate); models/ + output/ do not go to git
│   ├── VOICE-SETUP.md          # Windows setup guide (Bengali)
│   ├── config.json             # REAL (locked facts; brain: mock, phase 11, v0.9.0, built 2026-11-21 + voice block + providers section: 8 LLM provider + fallback_chain)
│   └── CEO-README.md
├── 01-Agency-Department/   # REAL (Phase 1 + Agentic 1–3) — Chief calls 15 workers + 8 department managers + 47 specialists, draft-only; workers are now vendored inside (Phase 6)
│   ├── chief_of_staff_agency.py  # REAL — ROUTING (15) + SECTION_ROUTING (6) + DEPARTMENT_ROUTING (8)
│   ├── pipeline.md             # 10 steps + honest state (mail 162, email PAUSED)
│   ├── governance/             # NEW (Agentic Phase 1) — office-charter.md + agent-permissions.md + approval-policy.md + security-policy.md
│   ├── departments/            # NEW (Agentic Phase 1–3) — 8 departments (01-sales-growth … 08-product-innovation); each has SECTION.md + manager/ + skills/ + specialists/ (47 worker .py — 43 Phase 3 + 4 GAP, 2026-11-21)
│   ├── agents/agent-registry/  # NEW (Agentic Phase 1–3) — registry.md + registry.json (69 entries: EXISTING 69, GAP 0)
│   ├── workflows/              # NEW (Agentic Phase 1) — 5 pipeline doc + README.md
│   ├── sub_agents/README.md    # sub-agent notes
│   ├── engine/                 # REAL (Phase 5) — 15 staff, 8 tool (5 mock / 3 gated), 15 skill; workers/ (vendored boss-ceo engine, SOURCE.md + src/; src/live/ — Phase 11: 6 provider openai/anthropic/gemini/kimi/grok/openrouter + meta_provider.py)
│   └── sections/               # REAL (Phase 7) — 5 sections (receive/sell/delivery/marketing/ops), 6 new agents + 6 skills, 15 mapped staff
├── 02-Digital-Product-Department/  # REAL* (Phase 2) — Chief does real work, kit blueprint + PA list 39/100; launch/sales stuck at Gate 0
│   ├── chief_of_staff_products.py + README.md + kit-outline.md + gate0-status.md
│   ├── pa-vet-list/            # 39 verified PA vet clinic (goal 100)
│   ├── engine/                 # REAL* (Phase 5) — 5 staff, 8 tool (6 mock / 2 gated), 5 skill
│   └── sections/               # REAL* (Phase 7) — 6 section (product/research/launch/sales/support/finance), 7 agent + 7 skill; Gate 0 fail-closed
├── 03-Content-Creation-Department/ # REAL (Phase 3) — Chief calls 6 Creator OS workers, draft-only; 13 stages REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; workers are now vendored inside (Phase 6)
│   ├── chief_of_staff_content.py + README.md + pipeline.md + VOICE.md (DRAFT) + toolpilot-status.md
│   ├── engine/                 # REAL (Phase 5) — 8 staff, 8 tool (5 mock / 3 gated), 8 skill; workers/ (vendored Creator OS, SOURCE.md + src/)
│   └── sections/               # REAL (Phase 7) — 5 section (plan/produce/publish/analyze/growth), 10 agent + 10 skill; upload OFF
├── CENTRAL-HQ/             # NEW (2026-11-19) — Unified OS layer, docs only (no code): unified-os.md + shared-services.md + data-isolation.md + cross-business.md + BUSINESS-01-AGENCY.md + BUSINESS-02-COMMERCE.md + BUSINESS-03-MEDIA.md
├── store/                  # LIVE queue + live state: tasks.json (1 done record — booking-link verification 2026-11-20), approvals.json, MEMORY.md, memory.json, schedules.json, confirmations.json, usage_ledger.json, vault/README.md (policy: store/README.md)
├── dashboards/             # status.html + status.json (made by sync_status.py — numbers from the real files) + engines.html (made by sync_engines.py — 9 tools, from tools.json) + dashboard-3d.html (3D dashboard, reads status.json) + n8n-wiring.md (map of 2 workflows, READY NOT LIVE) + taskboard.html + TASKBOARD-README.md (Phase 9 — local queue board, port 8766)
├── skills/                 # 7 manual skills (main-ceo-bot + chief-agency/chief-content/chief-products + drawer-memory-box + skill-finder + tool-allowlist)
├── scripts/                # check_phase0..4.py + check_engines.py + check_phase6.py + check_phase7.py + check_departments.py + check_specialists.py + run_office.py (runner) + sync_status.py + sync_engines.py + voice_test.py + check_voice.py + jarvis_voice_loop.py + check_gate.py + check_memory_ledger.py + check_quiet_schedules.py + check_providers.py + check_live_brain.py + check_live_tools.py + taskboard_server.py (port 8766)
├── .gitignore              # voice models/ + output/ are not pushed
├── LOCAL-RUN.md     # instructions for running on your PC + run_local.bat (Windows)
├── README.md               # this file
└── BUILD-LOG.md
```

## Running the Phase 0 checks

```bash
python3 ~/workspace/talvenor-master-os/scripts/check_phase0.py
```

If all PASS, Phase 0 is fine.

## REAL vs STUB vs REUSED (honest table)

| Item | State |
|---|---|
| Approval gateway (approve/reject) | **REAL** — really records, no auto-approve |
| BrainFactory (`brain.py`) | **REAL (Phase 6 + Phase 10 + Phase 11)** — config flag `brain: mock` (default, $0, draft-only) / `live` (via `live_brain.py` LiveBrainAdapter, loud mock fallback; provider chain from `fallback_chain`: openrouter → meta → mock; 8 providers: meta/openai/anthropic/gemini/kimi/grok/openrouter/ollama, models from config; live verification 2026-11-06 TIMEOUT + 2026-11-20 tunnel-403, key path UNPROVEN, no live call made yet) |
| Runner (`scripts/run_office.py`) | **REAL (Phase 6)** — runs the office in one command (Main CEO Bot → Chief → worker); gated work gets stuck in PENDING; `--drain-queue --max 2` |
| Shared tool-calling core (`tool_calling.py`) | **REAL (Phase 5)** — registry + dispatcher; mock tools return DRAFT, gated tools get stuck in PENDING, all calls are logged |
| Agency Engine (15 staff, 8 tool, 15 skill) | **REAL (Phase 5)** — draft-only, email PAUSED; send/publish/spend gated |
| Products Engine (5 staff, 8 tools, 5 skills) | **REAL* (Phase 5)** — launch/sales stuck at Gate 0 |
| Content Engine (8 staff, 8 tools, 8 skills) | **REAL (Phase 5)** — upload OFF, VOICE.md DRAFT, GPU AMD Radeon integrated 496 MB VRAM (verified 2026-11-17 — FramePack/WanGP will not run) |
| Phase 7 sections (16 sections, 23 agents, 23 skills) | **REAL** — draft-only, gated PENDING; Agency 5 sections / 6 new agents, Products 6 / 7 (Gate 0 fail-closed), Content 5 / 10 (upload OFF) |
| Main CEO Bot router | **REAL** — sends tasks to the right Chief |
| config.json | **REAL** — locked facts |
| Dashboard status.html | **REAL** — made by sync_status.py, numbers from the real files |
| n8n workflows (auto-send + callback) | **READY · NOT LIVE** — import files ready, Boss's import + connect + test remaining |
| Jarvis voice | **REAL (2026-11-17)** — Piper TTS + Vosk (en) + sherpa-onnx (bn), offline, $0; mic connected; brain mock (voice does not make Jarvis smart); gated work by voice only becomes PENDING, never executes |
| Agency Chief of Staff | **REAL (Phase 1 + Agentic Phase 2 + 3)** — 15 workers + 8 department managers + 47 specialists routing (DEPARTMENT_ROUTING + manager→specialist importlib), draft-only, gated work gets stuck in PENDING |
| Products Chief of Staff | **REAL* (Phase 2)** — 4 task types routing, Gate 0 fail-closed, launch/sales blocked |
| Content Chief of Staff | **REAL (Phase 3)** — 6 Creator OS workers routing, draft-only, blocked at upload OFF, makes no video files |
| boss-ceo engine (15 workers) | **VENDORED (Phase 6)** — the copy is now inside `01-Agency-Department/engine/workers/`; upstream `~/workspace/boss-ceo/` stays canonical, not a runtime dependency |
| talvenor-office | **REUSED** — `~/workspace/talvenor-office/` (reference only) |
| Creator OS (6 workers) | **VENDORED (Phase 6)** — the copy is now inside `03-Content-Creation-Department/engine/workers/`; upstream `~/workspace/creator-os-combined/` stays canonical, not a runtime dependency |
| Jarvis concept/code | **REUSED** — `~/workspace/jarvis-ceo-os-concept/`, jarvis-os repo |
| 136 businesses / 1,189 workers | **DROPPED (Boss 2026-11-16)** — scope = 3 businesses only |

## Jarvis voice (REAL — 2026-11-17, not a phase, a voice addition)

- **Speaking (TTS):** Piper, offline, $0. Bengali voice `bn_BD-google-medium` (the only Bengali voice in the Piper catalog, CC-BY-SA-4.0) + English `en_US-lessac-medium` (Lessac licence — personal use OK, check the licence before commercial use).
- **Listening (STT):** English Vosk `vosk-model-small-en-us-0.15` (40 MB, Apache-2.0); Bengali sherpa-onnx `vosk-model-small-streaming-bn` (~96 MB, Zipformer2, Apache-2.0, WER self-reported 17.9–32.9). Truth: classic Vosk's official list has no Bengali model — Bengali is heard by sherpa-onnx, not Vosk.
- **Running (Boss's PC, Windows):** `python scripts\jarvis_voice_loop.py` (default Bengali; `--lang en` for English). Test: `python scripts\voice_test.py` (without mic) + `python scripts\check_voice.py`. Setup: `00-CEO-Core/VOICE-SETUP.md`.
- **Verification (this VM, 2026-11-17):** voice_test 7/7 PASS (en synth 71,724 B → Vosk "hello i am jarvis" exact; bn synth 82,988 B → sherpa "Ami Jarfish shunchhi" — "Jarvis"→"Jarfish", one phoneme wrong, within WER); check_voice 13/14 (only sounddevice FAIL — no PortAudio on this VM, VM-only; bundled in the Windows wheel). Phase 0 8/8, Phase 7 18/18, total 138/138 — no regressions.
- **Honest limits:** nobody has heard the Bengali voice's quality (Boss will hear it first); Bengali STT will make mistakes (small model); brain mock — answers are MOCK-PLAN drafts; live mic test only on Boss's PC (no PortAudio on this VM); RAM is tight (8 GB, ~1.4 GB free) — keep Chrome closed while running voice.
- **Gate:** saying "send"/"post it" by voice only writes PENDING in the ApprovalGateway; it does not execute. "upload it"/spend/delete cannot be requested by voice.

## Gate (the law)

`ok` / `post it` / `upload it` / `send` / `go` — Boss's exact
word — without it, no send/publish/spend/delete. Spend cap **$0**.

## True state (2026-11-21)

- Paying client: **0**
- Registry: **69 entries — EXISTING 69, GAP 0** (4 GAP workers built on 2026-11-21; specialists 43 → 47)
- Total checks: **390/391** (verified 2026-11-22 by independent re-run after Phase 1: audit 380/381 + 10 new checks in check_phase1.py 11→21; check_phase5.py is a wrapper over check_engines.py — its 44 checks are the same 44, not double-counted; check_voice 13/14 — sounddevice import FAIL, no PortAudio on this VM, VM-only)
- Phase 11 + Improvements 1–3: **BUILT 2026-11-20/21** — brain still **mock** (live probe 2026-11-20 tunnel-403 FAILED, key UNPROVEN)
- store/tasks.json: **1 done record** (booking-link verification, 2026-11-20) — store is now a live queue
- Jarvis voice: **REAL (2026-11-17)** — Piper+Vosk/sherpa, offline, $0; first live mic test still remaining on Boss's PC
- Email: **PAUSED** (since 2026-11-14) — the SPF/DMARC DNS fix is still in Boss's hands
- First mail: 162
- Vet Kit Gate 0: **NOT PASSED** — the Lemon Squeezy test is Boss's step
- n8n workflows: **READY · NOT LIVE** — auto-send (8 node) + callback (3 node)
- Host: **Muse runtime + 10-min bridge cron `master-os-3d-bridge` ($0)** — no 24/7 server. The old ceo-office-dashboard + ceo-office-bridge were deleted on 2026-11-20 — there is now one dashboard, the Talvenor Master OS 3D Dashboard.

## Next phases

- **Phase 1 — Agency:** ✅ BUILT 2026-11-16 (Chief REAL, 15 worker wired, check 11/11 PASS).
- **Phase 2 — Digital Product:** ✅ BUILT 2026-11-16 *as far as Gate 0 allows* (Chief REAL, kit blueprint, PA list 39/100, checks PASS) — kit build/sale/launch stuck at Gate 0.
- **Phase 3 — Creator OS:** ✅ BUILT 2026-11-16 (Chief REAL, 6 worker wired, 13 stage REAL 0 / MOCK 10 / BLOCKED 3, upload OFF, check PASS).
- **Phase 4 — n8n wiring:** ✅ BUILT 2026-11-16 (wiring doc + sync_status.py, 2 workflows READY NOT LIVE, dashboard runs on sync, checks 9/9 PASS).
- **Phase 5 — Three Engines:** ✅ BUILT 2026-11-16 (shared tool-calling core + 3 engines — Agency 15 staff / 8 tools / 15 skills, Products 5 / 8 / 5, Content 8 / 8 / 8; engines dashboard runs on sync, checks 45/45 PASS).
- **Phase 6 — Full Complete Agent Offices:** ✅ BUILT 2026-11-16 (workers vendored inside — Agency 18 files + Content 4 files + SOURCE.md; BrainFactory mock default / live unwired; `run_office.py` runner — the office runs in one command, `--drain-queue --max 2`; 136 DROPPED, scope 3 businesses only; config phase 6 / v0.6.0; checks 14/14 PASS).
- **Phase 7 — Full Offices (Sections):** ✅ BUILT 2026-11-17 (16 sections — Agency 5, Products 6, Content 5; 23 section agents + 23 section skills; the Agency's 15 workers mapped + 6 new agents, Products' 7 agents (Gate 0 fail-closed — kit/sales never written), Content's 10 agents (6 wrappers + 2 chief-level + 2 new; upload OFF); SECTION_ROUTING in the 3 Chiefs; config phase 7 / v0.7.0; checks 18/18 PASS) — Phase 7 does not end here: Agentic Phase 1–3 + Unified OS came after (see below). Total checks at Phase 7's time were 200/200 (138 phases+engines + 21 departments + 41 specialists) + voice 13/14 — the current total is 390/391, see "True state" above.
- **Agentic Agency Office Phase 1 — Foundation:** ✅ BUILT 2026-11-19 (Boss's order — audit another AI's blueprint and combine it with the Agency office; not a new repo, inside 01-Agency-Department): governance/ (charter, permissions, approval policy, security policy — 4 files), departments/ (8 departments — Sales & Growth, Marketing, AI Engineering, Client Operations, Research & Strategy, Finance & Admin, Quality & Security, Product & Innovation; each has SECTION.md + manager .py + skill .md — 24 files), agents/agent-registry/ (registry.md + registry.json — 69 entries: EXISTING 22 role-entries = 21 distinct workers, ROLE-ONLY 43, GAP 4; 8 managers EXISTING in a separate list), workflows/ (5 pipeline docs — lead-generation, sales-outreach, client-onboarding, receptionist-deployment, client-support). 21 existing staff mapped: Sales 8, Marketing 4, AI Eng 1, Client Ops 5, Research 0 (GAP dept), Finance 2, Quality 1, Innovation 0 (GAP dept). Audit corrections: Retell is not in production — Vapi live (Sophia +19472230244); DB is JSON store, not PostgreSQL; CRM n8n planned, not live; Sophia is the live receptionist, not a demo. 8 managers live test PASS (TEMP store — draft-ready + unknown-task + pending-approval); all checks 138/138 + voice 13/14 PASS; sync byte-identical; store pristine. Agency Chief wiring **Phase 2 DONE 2026-11-19** — the Chief now calls the 8 managers via DEPARTMENT_ROUTING (see "Agentic Agency Office Phase 2" below). PUSHED 2026-11-19 ~23:40, head 162921aa (on Boss's "finish everything + push", 55 files, 6 batches — Phase 1 + Phase 2 + Unified OS together).
- **Agentic Agency Office Phase 2 — Executive wiring:** ✅ BUILT 2026-11-19 (Boss's order "whatever is left, finish all the work" — connect Phase 1's 8 managers to the Agency Chief): new DEPARTMENT_ROUTING in chief_of_staff_agency.py — 8 task types (dept_sales, dept_marketing, dept_engineering, dept_operations, dept_strategy, dept_finance, dept_quality, dept_innovation) → 8 managers (ChiefGrowthAgent / MarketingDirectorAgent / CTOAIEngineeringAgent / COOClientOperationsAgent / ChiefStrategyAgent / CFOFinanceAgent / ChiefQualitySecurityAgent / ChiefInnovationAgent), all gates `ok`, the payload's task_kind → top-level translate (managers read task.get("task_kind")), the same SECTION_ROUTING pattern (importlib load + mock brain + tasks.json log), gated action → ApprovalGateway PENDING, unknown kind → "unknown-task". ROUTING (15) and SECTION_ROUTING (6) unchanged. New check script scripts/check_departments.py — 21/21 PASS (8 manager loads + 8 routes draft-ready [MOCK DRAFT] + 2 gated PENDING + 1 unknown-task + stale-claim grep clean + old checks 138/138 + voice 13/14). Stale wiring notes fixed in 25 files (76 replacements + 3 extra variant fixes — "Chief still does not call" → "Chief now calls via DEPARTMENT_ROUTING"). PUSHED 2026-11-19 ~23:40, head 162921aa (on Boss's "finish everything + push", 55 files, 6 batches).
- **Agentic Agency Office Phase 3 — Specialists:** ✅ BUILT 2026-11-19 (Boss's order "go" — build Phase 1's 43 ROLE-ONLY roles as real worker code): each role's skill .md written first, then the worker .py from that skill (Phase 7 section-agent pattern — stdlib-only, Bengali docstring, run(task, brain, gateway, approvals_path), mock brain, DRAFT-labelled output, gated action → ApprovalGateway PENDING, never executes). Per-dept: 01 Sales & Growth 5 (Google Maps Prospect Finder, Business Verification, Lead Scoring, CRM Manager, Sales Intelligence), 02 Marketing 4 (Market Positioning, Social Media, SEO, Analytics — worker files renamed to snake_case), 03 AI Engineering 7 (AI Solution Architect, Conversation Designer, Prompt Engineering, Vapi Integration — the brief's Retell name corrected, Calendar Integration, n8n Automation, Deployment), 04 Client Operations 4 (Call Monitoring, Client Reporting, Retention, Renewal & Upsell), 05 Research & Strategy 7 (Competitor, Industry, Pricing, Niche Selection, Offer Development, Market Opportunity, Business Intelligence), 06 Finance & Admin 4 (Revenue Tracking, Subscription Tracking, Document Management, Compliance Calendar), 07 Quality & Security 6 (Call Scenario Testing, Workflow Testing, Data Validation, Security Monitoring, Access Control, Compliance Review), 08 Product & Innovation 6 (New AI Product Research, New Feature Research, Automation R&D, Technology Evaluation, Product Improvement, Prototype Builder). All 8 managers load and run their own specialists via importlib (the same Chief→manager pattern) — the old engine/section workers' plan-draft behavior unchanged, the Chief's DEPARTMENT_ROUTING unchanged. Registry: 69 entries — EXISTING 65 (22 role-entries + 43 specialists = 65 role-entries, 64 distinct workers), ROLE-ONLY 0, GAP 4 (Ad Campaign — $0 cap; CRM Integration — CRM not live; Expense Tracking — $0 spend; Backup & Recovery — no backup system) — no worker/skill built for the 4 GAP roles. New check script scripts/check_specialists.py — 41/41 PASS (43 loads + 43 draft-runs + 43 gated PENDING + 8 manager routes + 8 manager gated + GAP + registry + stale-claim grep + forbidden terms + real store + old checks 138/138 + check_departments 21/21). Dept 02's 4 worker files renamed to snake_case + 68 stale-claim fixes (manager .py/skill/SECTION.md — "No worker executes" → scoped truth: managers run the new specialists, not the old engine/section workers). PUSHED 2026-11-20 ~00:21–01:19, head aab7dc03 (on Boss's "push koro", 117 files, 12 batches).
- **Phase 9 — Connections:** ✅ BUILT 2026-11-20 (taskboard + MCP + live-ready tools): taskboard (`dashboards/taskboard.html` + `scripts/taskboard_server.py`, port 8766, `store/tasks.json` live queue — 1 research task POST-verified, booking link LIVE, status done); MCP wiring (`00-CEO-Core/mcp/` — stdio server + client, only 7 mock tools, checks 9/9); live-ready tools (`00-CEO-Core/live_tools.py` — gmail_send + n8n_trigger, CODE ONLY, gated, never executes; `tools.json` now 9 tools; checks 7/7). Store is now a live queue — "store empty" is no longer an invariant (snapshot-compare in 12 check scripts). Total 215/215 PASS.
- **Phase 10 — Live Brain:** ✅ BUILT 2026-11-20 (adapter only — the body untouched): `00-CEO-Core/live_brain.py` (LiveBrainAdapter — vendored MetaSparkProvider wrap, LOUD mock fallback if live fails, no retry) + `scripts/check_live_brain.py` (10 checks, `--live` probe default OFF). LIVE PROBE 2026-11-20 ~21:45 — FAILED (tunnel 403, api.meta.ai unreachable, $0, key validity UNPROVEN; the adapter fell back correctly). Decision: the brain **stays mock**, config phase 9 / v0.9.0 unchanged, no retry — live proof on Boss's PC network. Total 225/225 PASS.
- **Phase 11 — LLM Providers:** ✅ BUILT 2026-11-20 (7 providers, one interface): 6 new files in `01-Agency-Department/engine/workers/src/live/` — openai (ChatGPT gpt-4o), anthropic (Claude claude-sonnet-4-5), gemini (gemini-2.5-flash), kimi (Moonshot kimi-k2.5), grok (xAI grok-4), openrouter (`openrouter/free` auto-route) — alongside MetaSparkProvider; provider chain in `live_brain.py` (fallback_chain: openrouter → meta → mock); `providers` section in config + `PROVIDERS-SETUP.md` guide (keys only in Windows env vars, never in a file). No key was given — going live needs Boss's key + the "live" flip + a probe. Checks: `scripts/check_providers.py` **43/43 PASS**; total **268/268 PASS**.
- **GAP worker build (2026-11-21):** workers `.py` + skills built for Phase 3's 4 GAP roles (Ad Campaign, CRM Integration, Expense Tracking, Backup & Recovery) — the registry is now **69 EXISTING / 0 GAP**; specialists 43 → 47. The Phase 3 bullet's line "no worker/skill built for the 4 GAP roles" was Phase 3's truth at the time (2026-11-19) — not anymore.
- **Old system delete + new bridge (2026-11-20):** the old `ceo-office-dashboard` artifact + `ceo-office-bridge` cron FULLY DELETED on Boss's order (backup `~/workspace/backups/ceo-office-dashboard-state-2026-11-20.json`); there is now one dashboard — the Talvenor Master OS 3D Dashboard (artifact `talvenor-master-os-3d-dashboard`). The new bridge cron `master-os-3d-bridge` (every 10 minutes) reads the repo's `store/tasks.json` queue, does real work (max 2/run, draft/result only — no send/publish/spend/delete), regenerates `dashboards/status.json`. Gate 0's state is now recorded by telling Elora in chat (no way to record it from the dashboard anymore).

## Running the office (Phase 6 runner)

```bash
# One task (mock brain, draft-only) — writes to the real store
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --business agency --task caption_write --input '{"title": "Caption pack", "platform": "instagram"}'

# Drain the queue (max 2 per run)
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --drain-queue --max 2

# Test — in a TEMP store (does not touch the real store)
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --business content --task script_write --input '{}' --store-dir /tmp/store-test
```

Gated work (send/publish/spend/delete) will not run via the runner — it gets stuck in PENDING,
and needs Boss's gate word. To make the brain `live`, in config.json
`"brain": "live"` — only on Boss's word, after live verification.

## Running the dashboard sync

```bash
python3 ~/workspace/talvenor-master-os/scripts/sync_status.py
python3 ~/workspace/talvenor-master-os/scripts/check_phase4.py
```

Running sync rebuilds `dashboards/status.html` from the real files again —
if numbers were changed by hand, sync reverts them. If a value is not found, it writes "unknown"
and does not invent one.

## Running the taskboard + skill-finder + live-brain probe

### Taskboard (Phase 9 — local queue board)

```bash
python scripts\taskboard_server.py   # Windows; on Linux, python3
# Open: http://localhost:8766/
```

- The board only writes tasks to `store/tasks.json` (queued) — the bridge cron does the work
  (every 10 minutes, max 2/run, draft/result only). Details:
  `dashboards/TASKBOARD-README.md`. `run_local.bat` does not run the taskboard —
  it must be run in a separate command.

### Skill-finder (2026-11-21 — finding new skills)

```bash
python scripts\run_office.py --business agency --task find_skill --input "{\"query\": \"backup\"}"
```

- The Main CEO Bot's task type `find_skill`: first searches the local registry,
  and if not found, makes a DRAFT proposal (`store/skill-proposals.json` — the file does not exist yet,
  it will be made when a proposal comes); upstream clone/adapt only on Boss's
  "ok", never copy-paste. Skill: `skills/skill-finder.md`; code:
  `00-CEO-Core/skill_finder.py`.

### Live-brain probe (Phase 10 — only on Boss's word)

```bash
python3 scripts/check_live_brain.py --live
```

- Default mock mode — no live calls. `--live` runs a single probe;
  the 2026-11-20 probe FAILED (tunnel 403, api.meta.ai unreachable, $0,
  key UNPROVEN). No more retries from this VM — live proof on Boss's PC network.

## Improvement Phases 1–3 — Nod Gate + Memory/Ledger + Quiet Schedules (2026-11-21)

Boss's order (2026-11-21 voice call): complete the rest of the already-built ~50% without a live brain, at $0, locally. Mira-shift / API-voice ideas dropped. Pattern: n8n Nod's RE (trust.ts / approvals.ts / memory.ts / ledger.ts / schedules.ts).

- **Phase 1 — Trust gate as code** (`00-CEO-Core/trust_gate.py`): rule-based `trust_check()` — read/draft free; for gated work, verify Boss's quote (verbatim) + coverage (gate word + material target); standing deny: over the $0 spend cap, dental/medical hard DQ; email PAUSED is not a deny — PENDING approval is the restart path. `ConfirmationStore` — run-once confirmation, wired to the ApprovalGateway; on failure -> UNCERTAIN, never re-run. Trust pre-check in the dispatcher (`tool_calling.py`): on deny, `blocked-trust`, and no approval is recorded either. Checks: `scripts/check_gate.py` **24/24 PASS**.
- **Phase 2 — Owner memory + usage ledger** (`00-CEO-Core/owner_memory.py`, `usage_ledger.py`): memory only learns from Boss's own messages, each entry with a verbatim quote + source (256 KiB cap); 3 seeds — the Mira name, answering in Bengali, gate words (`store/memory.json` + `store/MEMORY.md`). Ledger: the $0 cap is now a measurement — mock always $0.00, any live spend trips a task check-in + monthly cap. Ledger threading in the dispatcher (opt-in `ledger_path`). Checks: `scripts/check_memory_ledger.py` **19/19 PASS**.
- **Phase 3 — Quiet schedules** (`00-CEO-Core/quiet_schedules.py`): watchMarker (state hash) — if the state has not changed, the run is skipped, quiet; only one run at a time; a correction only changes the stated field; on failed work the marker stays the previous one. Seed schedule `taskboard-queue-watch` (paused — no runner attached). Checks: `scripts/check_quiet_schedules.py` **16/16 PASS**.
- **Memory system LIVE** (`00-CEO-Core/owner_memory.py` + `MEMORY-STRUCTURE-DECISION-2026-11-21.md`): structure decided on merit — one central store + boxes inside (shared Boss words + per-agent box); CEO route + Chief handle read memory on every task; Boss's words are learned with quote verification, forgetting only with the gate's approval ("go"); maintenance (stale archive + dedupe) + proposal validation (not auto-write). Checks: `00-CEO-Core/check_drawer_memory.py` **26/26 PASS**. The brain is still mock.
- **Total count:** Improvements 1–3 = 24 + 19 + 16 = **59 checks**; Memory LIVE checks 26/26 in a separate suite. The full suite is **390/391 PASS** (verified 2026-11-22 after Phase 1 — count in "True state" above).

The brain is still **mock**. Phase 4 team factory is blocked without a live brain. Most Phase 1–3 files are still LOCAL only (trust_gate.py + owner_memory.py are going in the memory batch) — push only on Boss's "push koro".
