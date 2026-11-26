# FOUNDER OS — UNIFIED BUSINESS OPERATING SYSTEM
# MASTER ARCHITECTURE

**Version:** 1.0 — FOUNDER OS Phase F0 deliverable (renamed in F1, 2026-11-26: Talvenor Master OS → FOUNDER OS; phases F0–F10 are the only numbering from here)
**Date:** 2026-11-22
**Source brief:** `~/workspace/unified-business-os/brief-2026-11-22.md` (saved as-is)
**Audit basis:** Full repository audit run 2026-11-22 (read-only inspection + 21 check scripts, 380/381 passing). The audit report was delivered to the Founder in chat on 2026-11-22; this document is the architecture + gap analysis + plan that follows from it.

**Status labels** (per brief §3): VERIFIED (tested and confirmed working) · IMPLEMENTED (code exists, needs operational verification) · PARTIAL (some functionality exists, incomplete) · PLANNED (designed, not implemented) · BLOCKED (missing dependency, permission, credential, or decision) · FAILED (implementation or test failed).

**Standing constraints that bound this build** (Founder's locked facts — these override any conflicting line in the brief):
- $0 spend cap. No spend, no paid service, no purchase without the Founder's explicit allocation.
- Brain is MOCK until a live brain is proven on the Founder's own PC. No live-brain retry from this VM without the Founder's new word. Phase 4 (team factory / live autonomous execution) waits for that proof.
- No push to GitHub without the Founder's word (`push koro`).
- Email sending PAUSED since 2026-11-14 (SPF/DMARC fix is the Founder's DNS step). No email goes out until the fix is verified and the Founder restarts it.
- Vet Kit Gate 0 NOT PASSED (Lemon Squeezy signup test is the Founder's manual step).
- No send / publish / spend / delete / upload without the Founder's exact gate word. Approval never causes execution in current code (`approved-not-executed` by design).
- Repo codebase is FULL English (except the Founder's 3 verbatim memory quotes). No Bengali in code/docs/skills.
- Never invent clients, testimonials, case studies, metrics, prices, or guarantees. Never target dental/medical/patient-health.
- Never create empty placeholder agents. Fewer fully-functioning agents beat many nonfunctional ones (brief §20 Step 5).

---

## 1. TARGET ARCHITECTURE

```
FOUNDER (Md Mainuddin — gate words: ok / go / post it / send / upload it)
    |
    v
00-CEO-Core — executive control layer (Main CEO Bot + Brain + Approval Gateway + Memory)
    |
    v
CENTRAL-HQ — shared services (registry, knowledge, memory, governance, scheduler, event bus,
             integrations, monitoring, security, analytics)
    |
    +-- 01 Agency OS (8 departments, MAIN business)
    +-- 02 Digital Product OS (Vet No-Show Recovery Kit)
    +-- 03 Content Creation OS (ToolPilot channel)
    |
    v
FOUNDER COMMAND DASHBOARD — one unified command interface, real backend state only
```

### 1.1 Layers

| Layer | Responsibility | Target state |
|---|---|---|
| Application | CEO Core, department managers, specialist agents, dashboard, client ops interface | CEO + managers + agents exist as code; dashboard is read-only today |
| Intelligence | LLM provider adapter, reasoning, structured outputs, tool calling, memory retrieval, context | 7 providers coded, mock default; tool calling + memory real; reasoning = mock brain |
| Orchestration | Task manager, workflow engine, scheduler, event bus, persistent queue, delegation | Task queue (JSON) + router real; scheduler + event bus partial; workflow engine missing |
| Integration | Email, CRM, Calendar, Voice AI, Telephony, Automation, Webhook, Database adapters | Adapters are dry-run builders / string references only; no live adapter verified |
| Data | Operational store, structured memory, knowledge, logs, audit records, file storage | JSON files only; memory real; logs/audit minimal (print + ledger) |
| Infrastructure | Local dev, background worker, scheduler process, API service, monitoring, backup, deployment | Local CLI + 2 HTTP servers + external 10-min bridge cron; no 24/7 service in repo |

### 1.2 Design principles (from the brief, kept)

- One central CEO Brain; one Central HQ; three separate divisions; eight connected Agency departments.
- Provider-independent interfaces (no permanent tie to one LLM or one voice platform).
- Secrets in environment variables / Secure Vault only — never in files, chat, or the repo.
- Least privilege; approval for every sensitive action; approval for one action never authorizes another.
- Structured logs, execution history, error handling, retries, validation on every workflow.
- Modular: a new division or agent can be added without touching the others.

---

## 2. CURRENT-STATE MAP (audit evidence, 2026-11-22)

Repo: `github.com/msredc5-bit/talvenor-master-os`, public, head `5723355a` (2026-11-21 12:59 Dhaka). Local copy `~/workspace/talvenor-master-os/` — 649 files, 191 directories. Remote 392 files = local 390 source files + 2 stale old-named files (`LOCAL-RUN-BANGLA.md`, `00-CEO-Core/PROVIDERS-SETUP-BANGLA.md`) that snapshot push cannot delete. Only 7 local files changed after the push (5 test .wav + `status.json`/`status.html`, bridge-generated). No `.git` directory locally — snapshot copy, not a checkout.

| Component | Status | Evidence |
|---|---|---|
| Main CEO Bot (`00-CEO-Core/main_ceo_bot.py`) | VERIFIED | Real router; `route_task()` lazy-imports Chiefs, attaches memory; self-test passes |
| CEO Brain (`brain.py`, `live_brain.py`) | PARTIAL | Real code; config `"brain": "mock"`; live adapter built, never proven live (2026-11-20 probe: tunnel 403, $0, key UNPROVEN) |
| Approval Gateway (`trust_gate.py`, `human_approval_gateway.py`) | VERIFIED | 3-layer enforcement in code; `check_gate.py` 24/24 PASS; stores empty — never exercised with a real Founder decision |
| Executive Memory (`owner_memory.py`, `store/memory.json`) | VERIFIED | Quote-verified; 11 boxes; 3 seed entries; `check_memory_ledger.py` 19/19, `check_drawer_memory.py` 26/26 |
| Usage ledger (`usage_ledger.py`) | VERIFIED | $0 cap enforced; 64 records, all $0.00, all from check runs |
| Agent Registry (`01-.../agents/agent-registry/registry.json`) | PARTIAL | 69 entries, all EXISTING, 0 GAP; but EXISTING = "file exists", not "works"; dual copy (`registry.md`) already drifting; no check ties registry to ROUTING dicts |
| Task Orchestration (`run_office.py`, `store/tasks.json`, taskboard server) | PARTIAL | Router + drain work (verified in temp store); queue = JSON file, no locking; 1 done record, 0 queued; taskboard has no auth |
| Quiet schedules (`quiet_schedules.py`, `store/schedules.json`) | PARTIAL | 16/16 checks PASS; seeded watch `taskboard-queue-watch` is paused, 0 runs, "no runner attached yet" |
| MCP (`00-CEO-Core/mcp/`) | VERIFIED | stdio server/client, 7 mock tools only; `check_mcp.py` 9/9 |
| Voice (`00-CEO-Core/voice/`) | PARTIAL | Piper TTS + Vosk en + sherpa-onnx bn, offline $0; `voice_test.py` 7/7; mic path fails on this VM (`sounddevice`); Bengali STT misheard "Jarvis" as "যার বেশ" in the repo's own test; Bengali prompts regressed to English (Founder decision pending since 2026-11-21) |
| Agency Chief (`chief_of_staff_agency.py`) | IMPLEMENTED | Real code, draft-only orchestration; gated action → PENDING or `approved-not-executed`, worker never runs |
| Agency departments (8 managers + 47 specialists) | PARTIAL | REAL 0 / DRAFT 55. All return `[MOCK DRAFT]`; 12 have real deterministic logic inside draft output; no network, no file writes, no sends |
| Agency engine workers (15 classes) | IMPLEMENTED | Real code; prompt → `llm.complete()`; mock brain returns template revenue $38.50/$12.00/$4.25 |
| Live LLM providers (7) | IMPLEMENTED | Real `urllib` code; keys via env vars (Meta via Secure Vault surrogate); 0 live calls proven; `meta_provider.py` has a VM-only hardcoded path (`/opt/muse/skills/...`) |
| Agency sections (6 agents) | PARTIAL | Draft-only; follow-up agent enforces the 100-mail rule; billing agent enforces paying-client-confirmed + LOCKED pricing |
| Agency workflows (`workflows/*.md`) | PLANNED | 5 prose SOPs; `lead-generation.md` calls itself LIVE but states filing is done by hand; no executable workflow; no n8n JSON in repo |
| Governance (`governance/*.md`) | PLANNED | 4 DRAFT docs; per-role permission tables have no code enforcement; docs contradict code (Chief wiring "Phase 2, not done yet" vs Chief already routing 8 managers) |
| Digital Product dept (Chief + 7 agents) | PARTIAL | Real code, draft-only; Gate 0 fail-closed; kit 0/6 built; PA list 39/100 (CSV, 8 emails); no payment code at all |
| Content dept (Chief + 10 agents + 6 vendored workers) | PARTIAL | Real code, mock drafts; pipeline REAL 0 / MOCK 10 / BLOCKED 3; video/edit/upload BLOCKED; ToolPilot 0 videos; `youtube-skills/yt-*` files referenced but absent from repo |
| CENTRAL-HQ (7 .md files) | PLANNED | Doc-only DRAFT wrappers/policy; no code, no agents, no bus/API |
| Dashboards | PARTIAL | 3D dashboard (CDN Three.js, read-only viz) + taskboard UI + generated `status.json`/`status.html`; data is real backend state; no founder controls (approve/pause/resume) in the dashboard |
| Scheduler | PARTIAL | Quiet-schedule engine real; no in-repo runner; 10-min cadence comes from an external bridge cron |
| Event Bus | PLANNED | No event bus in repo. Event-like flows exist only as prose (§10 D) and as the task queue |
| Integration layer | PLANNED | `gmail_send`/`n8n_trigger` are dry-run builders (never execute); Vapi/Twilio/Google are string references; n8n workflow JSONs live outside the repo, both `active: false` |
| Data layer | PARTIAL | JSON files only; no DB, no locking, no `Store` implementation (ABC only); no log files (185 `print()` sites) |
| Skills (117 .md files) | PARTIAL | Doc-only playbooks; no `.py` reads them; every skill duplicated (engine + section copies, 16/17 pairs differ) |
| Tests | VERIFIED (with 1 known failure) | 21 check scripts, **380/381 PASS** (2026-11-22). Sole failure: `sounddevice` import (VM-only). No pytest/unittest/CI; no full-suite runner; checks are largely self-referential |

**Brief §15 historical findings — re-verification result:** 8 of 9 confirmed TRUE as stated (mock brain; draft-only workers; managers plan without a complete execution bridge; email PAUSED; n8n READY NOT LIVE; Vapi callback READY NOT LIVE; 10-min bridge exists, no 24/7 service; live brain not independently verified). The 9th (README "326/326 tests passing") is STALE — independently reproduced as **380/381**.

---

## 3. GAP ANALYSIS

| # | Target component (brief) | Current state | Required change | Final status |
|---|---|---|---|---|
| G1 | CEO Core: goal management, strategic planning agent, decision support, executive reporting, health monitor (§5) | Router + brain + gateway + memory exist; the other 5 are missing or draft-only | Add goal store + reporting that reads real `store/` state; wire dept 05 as the planning source; health = check-suite + status sync | PARTIAL → Phase 1 |
| G2 | Central HQ shared services (§6) | 7 DRAFT .md files, no code | Implement as code under `CENTRAL-HQ/` or `00-CEO-Core/`: single registry (canonical `registry.json`), skill index, permission table enforced in `call_tool()`, task orchestration hardening | PLANNED → Phase 1 |
| G3 | Agent Registry: identity, status, availability, performance, history, versions (§6.1) | Static list of 69; no runtime status/history | Registry becomes the runtime source: load it in the Chief, record per-agent runs in `store/`, generate `registry.md` from JSON | PARTIAL → Phase 1 |
| G4 | Knowledge / Skill Registry + discovery (§6.2) | `skill_finder.py` exists (local search + DRAFT proposals); 117 .md skills, duplicated, unread by code | Deduplicate skills to one copy each; skill-finder becomes the loader; proposals stored in `store/skill-proposals.json` | PARTIAL → Phase 1 |
| G5 | Memory: searchable, permission-controlled, per-division isolation (§6.3) | 1 store, 11 boxes, quote-verified; only `shared` has entries; no search index | Add search over entries; enforce box permissions in `context_for()`; per-division boxes for products/content | PARTIAL → Phase 1 |
| G6 | Task orchestration: priority, dependencies, retry, cancellation, history (§6.4) | Queue + drain + run-once confirmations; no priority/deps/retry/cancel | Add `priority`, `depends_on`, `retries`/`max_retries`, `cancelled` to `tasks-v1`; drain honors them; history kept (never delete records) | PARTIAL → Phase 1/6 |
| G7 | Scheduler: daily/weekly/monthly, tz-aware, quiet hours, pause/resume, missed-task recovery (§6.5) | Quiet-schedule engine (watch-marker) real; seeded watch paused; no in-repo runner | Attach a runner (in-process, triggered by the existing bridge cadence); add quiet-hours + missed-run recovery; Asia/Dhaka + America/New_York tz handling | PARTIAL → Phase 6 |
| G8 | Event Bus (§6.6, §10 D) | None in repo | Add `store/events.json` append-only log + `events.py` (validate, dedupe by idempotency key, dispatch to handlers, never double-execute); 12 event types from §6.6 | PLANNED → Phase 6 |
| G9 | Governance/Security: RBAC, least privilege, audit logs, secret mgmt, backup/recovery, budget (§6.7) | Gate + $0 ledger real; RBAC/permissions prose-only; audit = ledger + task log; no backup procedure in code | Enforce permission table in dispatcher; structured audit log file; backup script (store snapshot) + restore test; widen `.gitignore` (`.env`, `*.pem`, credentials) | PARTIAL → Phase 1/8 |
| G10 | Integration layer: adapter + config + health check + errors + retry + logging + permissions (§6.8, Phase 5) | Dry-run builders only; no live adapter verified | Per-integration adapter module with health check that reports real status; no adapter claims LIVE without a successful check | PLANNED → Phase 5 (BLOCKED on live brain + Founder steps for most) |
| G11 | Agency Dept 01–08: brief §7 wants ~86 specialists; existing 47 + 8 managers | 55 DRAFT agents; execution bridge = Chief → worker (mock) only | DO NOT add ~40 new draft agents (brief §20 Step 5). First wire execution for existing agents; add a new specialist only with a real, tested capability | PARTIAL → Phase 2 |
| G12 | Sales engine: lead DB, dedup, verification, scoring, CRM, outreach, reply, follow-up, analytics (§7 Dept 01, Phase 3) | Scoring/verification logic real inside drafts; lead pool in workspace CSVs outside repo; CRM planned (n8n Data Tables); email PAUSED | Lead store inside repo (`store/leads.json`, dedup by domain/phone); CRM adapter as code (dry-run until n8n is live); outreach stays draft-only until email restart | PARTIAL → Phase 3 (sends BLOCKED) |
| G13 | Marketing engine (§7 Dept 02) | Draft-only (plan/caption/script); publish prep checklist; no publish path | Keep draft-only; add publish-prep validation (checklist gates on real files); publish stays Founder/manual | PARTIAL → Phase 2/3 |
| G14 | Engineering/delivery: reusable templates + per-client tenant isolation (§7 Dept 03, §8, Phase 4) | Build-plan drafts; no tenant model; live stack is external Vapi/Sophia | Tenant config schema (`client_id`, profile, KB, voice, phone, rules, integrations) + QA checklist as code; deployment stays manual + gated | PLANNED → Phase 4 (BLOCKED: 0 clients, live brain, Twilio number) |
| G15 | Client operations (§7 Dept 04) | Intake/onboarding/success drafts; 0 clients, unexercised | Keep draft-only; add intake validation (missing = CLIENT INPUT REQUIRED, already the pattern) | PARTIAL → Phase 2 |
| G16 | Research & strategy (§7 Dept 05) | 7 pure-template specialists | Outputs must label VERIFIED/ESTIMATE/ASSUMPTION/UNKNOWN (already the pattern in drafts); add a real research-notes tool that refuses to invent | PARTIAL → Phase 2 |
| G17 | Finance & admin (§7 Dept 06) | Tracking drafts; hardcoded 0s; no payment code | Replace hardcoded snapshots with reads from `store/`; invoice draft requires paying-client-confirmed (already enforced) | PARTIAL → Phase 2 |
| G18 | Quality & security (§7 Dept 07) | Checklist drafts; Backup & Recovery unreachable via its manager (BUG) | Fix the 1-line routing bug; add QA verdict as structured output; add tenant-isolation test (no client data yet — test the rule, not data) | PARTIAL → Phase 2/8 |
| G19 | Product innovation (§7 Dept 08) | 6 pure-template specialists | Keep as research/proposal only; no deploy path (already the rule) | PARTIAL → Phase 2 |
| G20 | Client-facing receptionist system (§8) | External Vapi/Sophia only; no code in repo | Tenant schema + deployment checklist (G14); runtime stays Vapi (external); monitoring = call-outcome drafts until a live feed exists | PLANNED → Phase 4 (BLOCKED) |
| G21 | Complete business workflow (§9, 21 steps) | Steps exist as drafts + prose; transitions are not structured tasks/events | Encode the 21-step lifecycle as task types + events in the orchestrator; each transition = one task record or one event | PARTIAL → Phase 2/6 |
| G22 | Autonomous daily/weekly/monthly ops (§10 A–C) | Weekly social cadence exists outside repo; daily/weekly/monthly report drafts exist as tools | Report generators that read real `store/` state; scheduler entries for daily/weekly/monthly (quiet schedules) | PARTIAL → Phase 6 |
| G23 | Reliability: persistent queue, idempotency, retry/backoff, timeouts, DLQ, cancellation, history, rate-limit, budget, alerts (§10 E) | Unique IDs + run-once confirmations + 300 s drain timeout exist; the rest missing | Add idempotency keys, retry limits + backoff, DLQ (`store/dead_letter.json`), error log file, budget check before every live attempt | PARTIAL → Phase 6 |
| G24 | Founder Command Dashboard (§11, 20 sections + controls) | Read-only 3D viz + taskboard (POST/DELETE, no auth) + `approve.py` CLI | Extend taskboard into a command center: real state in all sections, approve/reject + pause/resume wired to `ApprovalGateway` + `schedules.json`; auth stays localhost-only until the Founder approves wider access | PARTIAL → Phase 7 |
| G25 | Approval/permission system (§12) | Gate + gateway + confirmations real; per-role matrix prose-only | Central policy engine = `trust_gate.py` + enforced permission table; categories AUTONOMOUS vs APPROVAL REQUIRED as code | PARTIAL → Phase 1 |
| G26 | Data architecture (§13, 26 entity types) | JSON files for tasks/approvals/confirmations/schedules/memory/ledger; no leads/clients/tenants/events/logs schema | Define schemas for the missing entities in `store/` (JSON, versioned); data isolation = per-division boxes + per-tenant files; retention + backup rules documented | PARTIAL → Phase 1/5 |
| G27 | Documentation (§16, 20 docs) | README, BUILD-LOG, sweep audits, SOPs exist; the 20 named docs do not exist as such | Create them phased (this doc = #1; audit doc = #2; the rest land with their phase) — never describe planned work as complete | PLANNED → all phases |
| G28 | Testing (§18, 24 test areas) | 21 check scripts, 380/381 PASS; no framework, no coverage, no E2E live tests | Add `check_*.py` per new capability; add in-department smoke tests; keep the "real store unchanged" discipline; live tests only on the Founder's PC with his word | PARTIAL → Phase 8 (continuous) |

---

## 4. IMPLEMENTATION PLAN (dependency-aware)

**Order rule:** core infrastructure before autonomous workflows; execution bridges before new agents; drafts before live actions; nothing live without the Founder's word + (for brain-dependent work) live-brain proof.

### PHASE 0 — AUDIT AND PRESERVATION [DONE, 2026-11-22]
- Full repo audit (this document's §2 + the chat audit report). Local-vs-remote verified (head `5723355a`, remote 392 = local 390 + 2 stale). Backup = the pushed GitHub state + the local snapshot; no destructive change made.
- Deliverables: audit report (chat) + this architecture doc (`TALVENOR_MASTER_ARCHITECTURE.md`).

### PHASE 1 — CEO CORE AND CENTRAL HQ [READY TO BUILD — $0, no live brain needed]
1. Single canonical registry: `registry.json` is the source; `registry.md` generated from it; Chief loads the registry at runtime; per-agent run history recorded in `store/`.
2. Permission table enforced in code: `agent-tool-assignments` moves from DRAFT doc to an enforced allowlist in `call_tool()`; per-role matrix (`TALVENOR_PERMISSION_MATRIX.md`).
3. Memory: search over entries; box-permission enforcement; add products/content boxes.
4. Task orchestration hardening: `priority`, `depends_on`, `retries`/`max_retries`, `cancelled`, idempotency keys; atomic writes + file locking for `store/*.json`.
5. Structured audit log (`store/audit.log`, JSON lines) + widened `.gitignore` + store backup script + restore test.
6. Goal store (`store/goals.json`) + executive reporting that reads real state.
7. Deduplicate skills to one copy each; skill-finder becomes the loader.
8. Fix the small audit bugs that live here: `sync_engines.py` dead validation (`or True`); check-count drift (15 vs 16); missing `check_phase5.py` naming (add or document).
- Deliverable: Functional Central Control System. Tests: new `check_phase1b`-style checks; full suite must stay green.

### PHASE 2 — AGENCY DEPARTMENTS [READY TO BUILD — $0, no live brain needed]
1. Fix Backup & Recovery routing (1-line map fix in Dept 07 manager).
2. Unify manager loading (Dept 03 drops the parallel `SPECIALIST_CLASSES` map); de-duplicate Dept 06 aliased task kinds.
3. Real task delegation: manager `run()` executes its specialists (already the pattern in most managers) and returns structured outputs — validated, not just draft text.
4. Replace hardcoded snapshots (`FIRST_MAILS_TOTAL = 162`, `PAYING_CLIENTS = 0`, `status_read` text) with reads from `store/`.
5. Fix `MockLLMProvider` char-vs-token truncation; `PublishPrep` count default; `ReplyHandler` decline gate; `meta_provider` VM-only path.
6. Refresh stale docs (`workers/SOURCE.md`, `engine/README.md`, Dept 06 `SECTION.md`, governance "Chief wiring Phase 2" lines); reconcile 507 vs 537 leads and PA 39 vs 37.
7. In-department smoke tests (import + `run()` for all 55 dept agents, 6 section agents, 15 workers — mock brain).
- Deliverable: Operational Agency Management System (draft execution, fully tested).

### PHASE 3 — SALES AND GROWTH ENGINE [READY TO BUILD, SENDS BLOCKED]
1. Lead store in repo (`store/leads.json`, dedup by domain/phone, verification + scoring fields).
2. Reply triage + follow-up queue as structured tasks (100-mail rule enforced in code — already the pattern).
3. CRM adapter as code (dry-run until n8n Data Tables is live).
4. Outreach stays draft-only; sending stays BLOCKED until the email restart (Founder's DNS fix + restart word).
- Deliverable: Functional Lead-to-Sales Workflow (drafts + queue + triage; sends gated).

### PHASE 4 — AI RECEPTIONIST DELIVERY ENGINE [BLOCKED]
- Tenant config schema + deployment checklist + QA-as-code + acceptance flow.
- BLOCKED on: (a) live-brain proof on the Founder's PC (Founder's 2026-11-21 order); (b) 0 paying clients (no tenant exists yet); (c) Twilio number import (~$1.15/mo, Founder's step); (d) n8n import + webhook URL.
- What can be built now without unblocking: the schema + checklists + QA code (no live deployment). Live deployment stays manual + gated.

### PHASE 5 — INTEGRATION LAYER [PARTIALLY READY — most adapters BLOCKED]
- Build the adapter framework + health-check contract first (config, credential reference, auth, validation, timeout, errors, retry, logging, permissions).
- Adapters that can be verified now ($0, no credentials): none live — all stay `PLANNED` with honest health `NOT CONNECTED` until a real check passes.
- Email/CRM/Calendar/Voice/Telephony adapters: BLOCKED on live brain + Founder credentials/steps (email restart, n8n import, Twilio import, Vapi demo account).
- Deliverable: Verified Integration Layer — an adapter counts as verified only after a successful health check, never before.

### PHASE 6 — AUTONOMOUS OPERATIONS [READY TO BUILD (in-process parts); live execution BLOCKED]
1. In-process event bus (`store/events.json` + `events.py`, idempotency keys, dedupe, dispatch).
2. Retry limits + backoff, dead-letter queue, error log, scheduler recovery, budget enforcement.
3. Scheduler runner attached to the existing quiet-schedule engine (daily/weekly/monthly, Asia/Dhaka + America/New_York, quiet hours, pause/resume, missed-run recovery).
4. Daily/weekly/monthly report generators reading real `store/` state.
- Live autonomous execution (sends, publishes, deploys) stays BLOCKED behind the Founder's word + live-brain proof.

### PHASE 7 — FOUNDER DASHBOARD [READY TO BUILD (read + approve parts)]
1. Extend the existing taskboard into the command center: all 20 sections fed by real backend state (no fabricated values).
2. Founder controls wired to real code: approve/reject (`ApprovalGateway`), pause/resume agents + workflows (`schedules.json` + a pause flag), review errors/budgets/history.
3. Stays localhost-only; no public exposure without the Founder's approval.
- Deliverable: Unified Founder Command Center.

### PHASE 8 — TESTING AND CONTROLLED PRODUCTION [CONTINUOUS, FINAL GATE]
- Unit / integration / workflow / permission / security / tenant-isolation / recovery / end-to-end tests per §18 (24 areas).
- Pilot deployment + production readiness review.
- **Production launch requires the Founder's explicit authorization.** Nothing in this plan launches production by itself.

---

## 5. DECISIONS NEEDED FROM THE FOUNDER

**The one decision for now (Phase 1 go-ahead):** Phase 0 is complete. Phase 1 (CEO Core + Central HQ hardening — registry, permissions, memory, task orchestration, audit log, $0, no live brain) is ready to build. Recommended default: **proceed with Phase 1 now.**

**Parked decisions (do not block Phase 1–3):**
- Live-brain proof on the Founder's PC (OpenRouter path first) — unblocks Phase 4 and live execution.
- Email restart (DNS fix + `check koro` + restart word) — unblocks sends in Phase 3/5.
- Gate 0 (Lemon Squeezy signup test) — unblocks the digital-product track.
- Twilio number import + n8n import + webhook URL — unblocks the callback workflow.
- Delete the 2 stale files from GitHub (`LOCAL-RUN-BANGLA.md`, `00-CEO-Core/PROVIDERS-SETUP-BANGLA.md`) — needs a separate approval (snapshot push cannot delete).
- Bengali voice prompts regression (restore Bengali prompts/triggers in `voice/loop.py` or keep English) — pending since 2026-11-21.
- Track 3 = ToolPilot or a brand-new channel — pending since 2026-11-12.

---

## 6. DOCUMENTATION PLAN (§16 — 20 docs, phased)

| # | Document | Lands in |
|---|---|---|
| 1 | TALVENOR_MASTER_ARCHITECTURE.md | Phase 0 — THIS FILE |
| 2 | TALVENOR_SYSTEM_AUDIT.md | Phase 0 — condense the 2026-11-22 chat audit into this file |
| 3 | TALVENOR_AGENCY_OS_ARCHITECTURE.md | Phase 2 |
| 4 | TALVENOR_AGENT_REGISTRY.md | Phase 1 (generated from `registry.json`) |
| 5 | TALVENOR_DEPARTMENT_RESPONSIBILITIES.md | Phase 2 |
| 6 | TALVENOR_WORKFLOW_CATALOG.md | Phase 2/3 |
| 7 | TALVENOR_AUTOMATION_SCHEDULE.md | Phase 6 |
| 8 | TALVENOR_EVENT_CATALOG.md | Phase 6 |
| 9 | TALVENOR_PERMISSION_MATRIX.md | Phase 1 |
| 10 | TALVENOR_APPROVAL_POLICY.md | Phase 1 (from `governance/approval-policy.md` + enforced code) |
| 11 | TALVENOR_DATA_ARCHITECTURE.md | Phase 1/5 |
| 12 | TALVENOR_INTEGRATION_CATALOG.md | Phase 5 |
| 13 | TALVENOR_SECURITY_POLICY.md | Phase 1/8 (from `governance/security-policy.md` + enforced code) |
| 14 | TALVENOR_TESTING_STRATEGY.md | Phase 8 |
| 15 | TALVENOR_DEPLOYMENT_GUIDE.md | Phase 8 |
| 16 | TALVENOR_OPERATIONS_MANUAL.md | Phase 6/8 |
| 17 | TALVENOR_FOUNDER_GUIDE_BN.md | Phase 7 (Bengali — the one doc allowed to be Bengali; repo rule excepts Founder-facing guide) |
| 18 | TALVENOR_BUILD_ROADMAP.md | Phase 0 — §4 of this file is the roadmap; split out when Phase 1 starts |
| 19 | TALVENOR_CHANGELOG.md | Continuous (append per phase) |
| 20 | TALVENOR_SYSTEM_STATUS.md | Continuous (generated from `status.json` + test runs, never hand-written numbers) |

---

## 7. FINAL STATUS TABLE (Phase 0 snapshot, 2026-11-22)

| System Component | Status | Evidence | Remaining Work |
|---|---|---|---|
| CEO Core | PARTIAL | Router + mock brain + gateway + memory VERIFIED; goal mgmt, planning agent, decision support, reporting, health monitor missing/partial | Phase 1 |
| Central HQ | PLANNED | 7 DRAFT .md files, no code | Phase 1 |
| Agent Registry | PARTIAL | 69 entries, all EXISTING; dual copy drifting; no runtime use | Phase 1 |
| Task Orchestration | PARTIAL | Router + drain VERIFIED in temp store; no priority/deps/retry; no locking | Phase 1/6 |
| Agency Departments | PARTIAL | 55 agents DRAFT; execution bridge = mock only | Phase 2 |
| Sales Engine | PARTIAL | Scoring/verification logic real in drafts; no lead store in repo; CRM planned; sends BLOCKED | Phase 3 |
| Marketing Engine | PARTIAL | Draft-only; no publish path | Phase 2/3 |
| Receptionist Delivery | BLOCKED | Draft plans only; 0 clients; live stack external Vapi | Phase 4 (needs live brain + Founder steps) |
| Client Operations | PARTIAL | Drafts only; 0 clients, unexercised | Phase 2 |
| Finance | PARTIAL | Tracking drafts; hardcoded 0s | Phase 2 |
| Quality & Security | PARTIAL | Checklist drafts; 1 routing bug (Backup & Recovery unreachable) | Phase 2 |
| Integrations | PLANNED | Dry-run builders only; 0 live adapters verified | Phase 5 (BLOCKED on live brain + Founder steps) |
| Scheduler | PARTIAL | Engine real; seeded watch paused; runner external | Phase 6 |
| Event Bus | PLANNED | None in repo | Phase 6 |
| Founder Dashboard | PARTIAL | Read-only viz + taskboard; no founder controls in dashboard | Phase 7 |
| Testing | PARTIAL | 380/381 PASS (21 scripts); no framework/CI/E2E-live | Phase 8 (continuous) |
