# TALVENOR MASTER OS — BUILD CHANGELOG

Append-only. One entry per phase. Numbers are verified by running the
check suite — never hand-written.

## Phase 0 — Audit and Preservation (2026-11-22)

- Full repository audit (read-only): 649 files, 191 directories, 380/381
  checks passing across 21 check scripts (sole failure: `check_voice`
  sounddevice import — no PortAudio on this VM, VM-only).
- Local-vs-remote verified: GitHub head `5723355a` == local sync record;
  remote 392 files = local 390 source files + 2 stale old-named files
  (`LOCAL-RUN-BANGLA.md`, `00-CEO-Core/PROVIDERS-SETUP-BANGLA.md`).
- Architecture + gap analysis + phased plan:
  `TALVENOR_MASTER_ARCHITECTURE.md` (267 lines).
- Architecture diagram: `~/workspace/your_files/talvenor-master-os-architecture.png`
  (rendered from `~/workspace/unified-business-os/render_architecture_diagram.py`).
- Verdict delivered to the Founder: draft factory with a locked gate,
  not a live business system. 0 live agents. Brain still MOCK.

## Phase 1 — CEO Core and Central HQ (2026-11-22)

Functional Central Control System. $0, no live brain, no push, no
send/publish/spend/delete. Backup of every modified file in
`/tmp/phase1-backup/` (2.5 MB). Real store verified unchanged at the end
(`store/tasks.json` still 1 record; `store/memory.json` 3 seed entries
intact; no `agent_runs.json` / `audit.log` / `tool_calls.json` in the
real store — Phase 1 writes went to TEMP).

1. **Registry canonical** — `scripts/generate_registry_md.py` regenerates
   `registry.md` from `registry.json` (69 entries, deterministic);
   `chief_of_staff_agency.py` loads the registry at runtime (read-only,
   never crashes routing) and records per-agent runs in
   `store/agent_runs.json`.
2. **Permissions enforced** — `00-CEO-Core/permissions.py` (33 agents x 9
   tools, from `agent-tool-assignments-DRAFT.md`); `call_tool()` denies
   with `denied-permission`; `TALVENOR_PERMISSION_MATRIX.md` generated
   from the enforced table (`scripts/generate_permission_matrix.py`).
3. **Memory** — `search()` over entries; `context_for()` isolation
   verified (shared + own box only); `products` and `content` boxes added
   (13 boxes total); `store/memory.json` migrated 11→13 boxes, entries
   byte-identical.
4. **Task orchestration** — `00-CEO-Core/store_io.py` (atomic writes +
   flock locking); tasks-v1 extended (`priority`, `depends_on`,
   `retries`/`max_retries`, `cancelled`, `idempotency_key`); drain honors
   priority, dependencies, cancellation, idempotency; taskboard validates
   the new fields and returns the existing record on duplicate key.
5. **Audit log + secrets** — `00-CEO-Core/audit.py` (JSON-lines
   `store/audit.log`); `.gitignore` widened (`.env`, `*.pem`,
   `credentials*`, `*.key`, `*.lock`, `backups/`; `store/` deliberately
   NOT ignored); `scripts/backup_store.py` + restore test.
6. **Goal store** — `00-CEO-Core/goals.py` + `store/goals.json`
   (4 goals from the Founder's stated words); `executive_summary()`
   reads only real store state.
7. **Skills dedup** — 17 multi-copy stems compared: 3 byte-identical
   replaced by pointer files; 14 differing kept and recorded in
   `skills/SKILL_INDEX.md`.
8. **Bug fixes** — `sync_engines.py` dead validation (`or True`) replaced
   with honest computation; quiet-schedule count drift reconciled to
   16/16 (README + config); `scripts/check_phase5.py` wrapper added
   (Phase 5 = engines check).

**Tests:** `scripts/check_phase1.py` 21/21 PASS. Full suite re-run
independently after Phase 1: **390/391 PASS** (sole failure:
`check_voice` sounddevice import, VM-only, pre-existing).

**Corrections made during parent verification (2026-11-22, same day):**
- `sync_engines.py` staff check: the Phase 1 fix matched skill stems by
  title case ("Qa Engineer") and falsely reported `qa-engineer.md`,
  `kit-qa.md`, `payment-rails-checker.md` as missing from STAFF.md.
  All three files exist and are listed. Fixed to stem-substring
  matching; all three engines now report `staff_ok=True`. No STAFF.md
  gap exists.
- README total corrected 337/337 → **390/391** (the 337 figure was the
  README's old internal ledger, never reconciled with the audit's
  380/381).
- Architecture diagram footer updated 380/381 → 390/391 and re-rendered.

## Phase 2 — Agency Departments (2026-11-23)

Real task delegation inside the Agency department. $0, no live brain, no
push, no send/publish/schedule/spend/delete. Backup of every modified
file in `/tmp/phase2-backup/`. Real store verified unchanged at the end
(`store/tasks.json` still 1 record `6e3b269f4533`; `store/memory.json`
3 seed entries intact; no `agent_runs.json` / `audit.log` /
`tool_calls.json` in the real store — all Phase 2 test writes went to
TEMP). No Bengali touched, none added (the 3 verbatim memory quotes,
`voice/loop.py`, voice model data, and the Phase 1 exception lines are
untouched; the full-English rule still stands).

1. **Backup & Recovery routing fixed** — Dept 07 manager's
   `SPECIALIST_MODULES` parallel map omitted `backup_recovery`, so the
   agent was unreachable via its manager. The map is deleted; every
   standalone entry now carries its own `"class"` key and the loader
   reads file + class from the `DEPARTMENT_TASKS` entry itself. All 47
   specialists are reachable via their manager.
2. **Manager loading unified** — Dept 03 manager's parallel
   `SPECIALIST_CLASSES` map deleted (only 1 of 10 entries had a class
   key); all 8 standalone entries now carry `"class"` and `run()` uses
   `entry["class"]`. Dept 06 aliased task_kinds de-duplicated:
   `invoice_management` → alias of `billing_invoice`,
   `financial_reporting` → alias of `report_compile` (one definition
   each, resolved in `run()`; alias runs return byte-identical output
   to their canonical kind).
3. **Real task delegation, validated** — new `scripts/check_unified_phase2.py`
   (177/177 PASS) imports + runs every manager task_kind (72), every
   standalone specialist (47), every section agent (6), and every engine
   worker (15) with the MOCK brain and asserts STRUCTURED output (dict
   with status/output/notes/draft_only/mock_brain/gate; draft-ready
   carries `[MOCK DRAFT]`; engine workers carry the WorkerResult shape).
   No new agents were added (brief §20 Step 5 forbids ~40 new draft
   specialists). The Chief already routes engine workers (15) and
   section agents (6) — that wiring is unchanged; the plan-only
   boundary for engine/section old workers inside managers stays
   deliberate and documented. Consistency fix found by the smoke test:
   Dept 08 manager had no overview branch (a bare call returned
   unknown-task while the other 7 managers return the roster) — added,
   mirroring the other managers.
4. **Hardcoded snapshots replaced by live reads** — new
   `00-CEO-Core/honest_status.py` (read-only): the single source of
   truth is `config.json` → `honest_status`, already read by
   `sync_status.py` / `goals.py` / `sync_engines.py`; there is no
   business-metrics file in `store/`, so no second source was created.
   Removed: `FollowUpAgent.FIRST_MAILS_TOTAL = 162`,
   `RevenueTrackingAgent.PAYING_CLIENTS = 0` / `REVENUE_TOTAL = 0`,
   `SubscriptionTrackingAgent.PAID_SUBSCRIPTIONS_TOTAL = 0`; `status_read`
   notes are now built from the values actually read (spend cap +
   email_outreach from config, Gate 0 from `gate0-status.md`'s Status
   line, same parse as `sync_status.py`). A value with no source returns
   the explicit string `"UNKNOWN"` — never a fresh hardcoded number:
   revenue total and paid-subscriptions total have no source field, so
   both now read UNKNOWN. Also fixed the same snapshot in the Dept 01
   manager (PA 37 → 39, verified against `emailed.csv`) and the Dept 06
   manager overview/plan notes (now read live).
5. **Small audit bugs fixed** — `MockLLMProvider.complete()` truncated by
   CHARACTERS (`text[:max_tokens]`); now truncates by words (the mock has
   no tokenizer). `meta_provider.py` top-level VM-only `sys.path`
   insert + `dynamic_credentials` import removed; the surrogate is now
   imported lazily inside `complete()` — the module imports cleanly on a
   plain checkout, and a missing surrogate fails the live call with a
   clear error (verified with a scrubbed-path subprocess). Only
   `meta_provider` had the VM-only path (verified: no other live
   provider has it). `PublishPrep` count default fixed (`1` → class
   default `2`); the same bug class found + fixed in `SchedulerAssistant`
   (`"client call"` → `"client demo call"`) and Content `ScriptWriter` /
   `VisualProducer` (`""` → `"short video"`). `ReplyHandler` decline
   gate: verified NOT a runtime bug (`requires_gate` is never read by any
   code; `do_work()`'s per-type gate is authoritative) — the class attr
   comment now says so honestly instead of over-claiming.
6. **Stale docs refreshed** — `engine/workers/SOURCE.md` (6 live providers
   added Phase 11 now listed; `__pycache__` note corrected — it exists
   now, created by test runs; `dynamic_credentials` note updated for the
   lazy import). Engine READMEs: Products 5 → 7 staff/skills (Kit QA +
   Kit Sales were missing), Content 8 → 10 skill files (growth-agent +
   repurpose-agent), Agency shared-core "being built" line removed
   (the core exists; check_engines 44/44). Dept 06 `SECTION.md`: "No
   worker execution" corrected (the manager DOES run the 5 Phase 3
   specialists; only section/engine old workers are plan-only) + alias
   notes. Governance: the 3 "Chief wiring Phase 2 / not done yet" lines
   corrected (wiring is DONE since 2026-11-19). Number discrepancies
   reconciled with sourced notes, not silent picks: **507 vs 537** =
   507 pool rows + 30 sent-history-only leads (source:
   `DELETION-LOG-2026-11-10.md`); **PA 39 vs 37** = 39 is the 2026-11-12
   count, verified against `leads-organized/*/emailed.csv` (PA file: 39
   rows + header); 37 was stale — fixed in `sales-outreach.md`,
   `followup-agent.md`, Dept 01 manager + skill docs + `SECTION.md`,
   and `registry.json` (regenerated `registry.md`, 69 entries,
   deterministic).
7. **In-department smoke tests** — `scripts/check_unified_phase2.py`,
   **177/177 PASS** (8 manager overviews + 72 kinds + 47 specialists +
   6 section agents + 15 engine workers + 22 Phase 2 regression
   checks + store-unchanged check).

**Tests:** `scripts/check_unified_phase2.py` 177/177 PASS. Full suite
re-run independently after Phase 2: **567/568 PASS** (baseline 390/391
+ the new 177/177 suite; sole failure remains the pre-existing
`check_voice` sounddevice import, VM-only).

## Phase 3 — Sales and Growth Engine (2026-11-23)

Functional Lead-to-Sales Workflow (drafts + queue + triage; sends gated).
$0, no live brain, no push, no send/publish/schedule/spend/delete, no
network calls to Sheets/n8n/Zoho. Backup of every modified file in
`/tmp/phase3-backup/`. Real store verified unchanged at the end except
the intended new file `store/leads.json` (`store/tasks.json` still 1
record `6e3b269f4533`; `store/memory.json` 3 seed entries / 13 boxes
intact; no `agent_runs.json` / `audit.log` / `tool_calls.json` in the
real store — all Phase 3 test writes went to TEMP). No Bengali touched,
none added (the 3 verbatim memory quotes, `voice/loop.py`, voice model
data, and the Phase 1 exception lines are untouched; the full-English
rule still stands).

1. **Lead store in repo** — new `store/leads.json` (schema `leads-v1`,
   524 unique leads), seeded from the REAL workspace pool by
   `scripts/build_lead_store.py` (reproducible: the builder re-runs
   into a TEMP dir and reproduces the live store byte-for-byte except
   the `built` timestamp) and read through new
   `00-CEO-Core/lead_store.py` (dedup lookups by domain/phone/email,
   per-state first-mail counts computed from the store, missing/corrupt
   store -> "UNKNOWN", never a guess; writes go through store_io
   atomic + flock). Dedup by normalized domain first, falling back to
   phone/email/name+city: 507 pool rows merge to 494 unique pool
   businesses (13 branch rows — same domain/phone, different city,
   e.g. Apex Tampa + St. Petersburg, UGI Harrisburg + Allentown —
   merged into one lead, branch rows kept in `locations`); + 30
   sent-history-only leads (Tier 3/4, kept so we never double-mail)
   = 524 unique leads; source-row total 537 (507 + 30) is kept in
   `meta` for audit. Flags, never silently dropped: 6
   BOUNCED_DEAD_ADDRESS (Athens, Alberto, ServiceProz, Napps,
   All Masters, Thompson & Thompson), 2 NEVER_REMAIL_DOUBLE_SENT
   (Metz, AAA Sewer & Drain), 1 HELD_DO_NOT_CONTACT (Premier
   Plumbing, San Antonio TX — already in the pool, so the flag merged
   into that lead, no duplicate row), 1 HELD_LOW_CONFIDENCE (Always
   Plumbing), 1 OTHER_CHANNEL_CONTACTED (Remarkable Plumbing and
   Heating), 2 SHARED_PHONE (Flow City / Rayne share one number),
   4 SHARED_EMAIL (two Wix sentry relays, one agency inbox — noted
   as relay/agency, not the business's own email).
2. **First-mail total corrected 162 -> 163 (verified)** — the seeder
   found Isackson Plumbing (San Francisco CA): pool says SENT
   2026-11-12, but CA `emailed.csv` has no row (filing gap, same
   class as Ory's Plumbing 2026-10-13). Verified against Gmail Sent
   before seeding: message `1a1cfb0ff25cdb8c`, Thu 12 Nov 2026 18:17
   Dhaka, from hello@talvenorai.agency. True total is 163 (CA 15, not
   the older locked 14); per-state: PA 39, FL 54, GA 16, TX 15, CA 15,
   IL 9, MI 5, NC 5, NY 4, OH 1. `config.json`
   `honest_status.first_mails_sent` corrected 162 -> 163 with a note
   field recording the evidence, and the 162/98 stale-number sweep
   updated 46 files (all current-truth statements; dated audit docs,
   the changelog history, and the `162 filed rows` count itself
   untouched). FL ceiling corrected 98 -> 99 unique leads (the
   2026-11-10 figure of 98 was the Nov 10 pool snapshot; the current
   pool + sent history gives 99 — FL still can never reach 100).
3. **Reply triage + follow-up queue as structured tasks** — new
   `00-CEO-Core/reply_triage.py` (bounce -> log-only; plain decline ->
   one polite-exit DRAFT; interest/question/pricing/demo/call ->
   HOT-LEAD draft that never quotes a price — "we share details on a
   short call" + booking link; demo video link only when asked;
   unclear/dental-medical/empty -> needs_decision; `sendable` is
   ALWAYS False; the module has no send path at all) and new
   `00-CEO-Core/followup_queue.py` (builds tasks-v1 follow-up records
   with stable idempotency keys, DRAFT only). The 100-mail rule is
   enforced in code: the queue refuses ALL 10 real states today
   (PA 39, FL 54, ... — queue empty, every refusal carries its
   reason + counts); a synthetic 101-mail TEMP store queues 100
   eligible leads and skips the bounced one. `FollowUpAgent` now
   reads the per-state count from the lead store when the payload
   carries none (PA 39 -> PARKED, total 163); the payload still wins
   when present.
4. **CRM adapter, dry-run only** — new `00-CEO-Core/crm_adapter.py`:
   `health()` reports NOT CONNECTED (n8n workflow active: false,
   Sheet queue not connected, no credential in the repo); every write
   method returns the exact payload that WOULD be sent (validated,
   serializable) and writes nothing — the module imports no network
   library at all. No live adapter can exist until the n8n import +
   Sheet connection + a passing health check.
5. **Outreach stays DRAFT-ONLY; sending stays BLOCKED** — no send
   path anywhere in Phase 3 code. Verified in the check: the trust
   gate answers "ask" (never "allow") for a send without Boss's
   words, and a fresh ApprovalGateway request stays pending. Email
   is PAUSED since 2026-11-14 (SPF/DMARC fix pending, Boss's DNS
   step).

**Tests:** `scripts/check_unified_phase3.py` 49/49 PASS (lead store +
builder reproducibility + triage + queue + CRM + FollowUpAgent wiring
+ sends-blocked + store-unchanged). Full suite re-run independently
after Phase 3: **616/617 PASS** (baseline 567/568 + the new 49/49
suite; sole failure remains the pre-existing `check_voice`
sounddevice import, VM-only).

## Phase 4 (buildable part only) — AI Receptionist Delivery Engine (2026-11-23)

Boss's go-ahead 2026-11-23 ~03:11 Dhaka was for the BUILDABLE PART
ONLY: tenant schema + deployment checklist + QA-as-code + acceptance
flow. Phase 4 as a whole stays BLOCKED (live-brain proof on Boss's
PC, 0 paying clients, Twilio number import, n8n import + webhook
URL). No live deployment path exists anywhere in this build; live
deployment stays MANUAL + gated by Boss's word.

1. **Tenant config schema** — new `00-CEO-Core/tenant_schema.json`
   (schema `tenant-v1`) + `00-CEO-Core/tenant_schema.py` (validator
   + Vapi assistant config draft). Fields cover onboarding: business
   identity (name, trade, city/state, US IANA timezone, website,
   phone), service area + hours, call-handling rules (greeting with
   {business_name} placeholder, AI disclosure, language locked to
   English, emergency_redirect must be True), qualification
   questions, booking rules (calendar link, appointment length,
   buffer), transfer/escalation rules, voicemail/after-hours, tier
   NAME only (Starter/Growth/Scale — no amounts anywhere in tenant
   output). Validation fails closed: missing field -> CLIENT INPUT
   REQUIRED listing the fields; dental/medical/patient-health trade
   -> refused (hard DQ); bad phone/timezone/state, non-English
   language, emergency_redirect not True -> rejected with a reason.
   The Vapi draft (model gpt-4o-mini, voice Emma, transcriber
   Deepgram nova-3, firstMessage + systemPrompt from the tenant) is
   a plain dict — draft_only + never_sent, never built from an
   invalid tenant, no API call.
2. **Deployment checklist** — new
   `00-CEO-Core/deployment_checklist.py` (evaluate-only). 8 steps:
   schema valid, Vapi config drafted, phone number assigned, booking
   link verified live, greeting approved (GATE, Boss's "ok"), test
   calls passed, billing confirmed, go-live (GATE, Boss's "go").
   Phone / test-calls / billing are BLOCKED with the exact missing
   input (Twilio number not imported — Boss's step; test calls need
   a live number + proven live brain; 0 paying clients, and
   BillingInvoiceAgent refuses any invoice unless
   paying_client_confirmed is True). Gate words are validated — a
   wrong word is rejected, never recorded. Ready stays False for
   every tenant today, honestly, because the blocked steps remain.
3. **QA-as-code** — new `00-CEO-Core/tenant_qa.py`: 8 checks over
   a tenant config + a synthetic call script (greeting names the
   business, AI disclosure present, life-safety check present,
   qualification question asked, booking ends with confirmation +
   booking link, no price quoted, no invented guarantee/superlative
   claim, transfer offered when enabled). Structured verdict
   (pass/fail per check + overall). Transfer check is
   not-applicable when transfer is disabled.
4. **Acceptance flow** — new `00-CEO-Core/acceptance_flow.py` +
   short doc `00-CEO-Core/tenant-acceptance.md`. Record is
   tasks-v1-shaped (id, type, business, title, payload, stage,
   steps, history). Stages: intake -> schema_check -> checklist ->
   qa -> boss_acceptance ("ok") -> deploy (ALWAYS BLOCKED: live
   deployment is manual, Boss executes it). Each advance() either
   completes the current stage or refuses with the reason recorded;
   blocked checklist items and missing gates are recorded as
   outstanding, never skipped. Records persist through store_io
   (atomic) to caller-chosen paths — tests use TEMP dirs only.

Fixtures: the ONLY tenant and the ONLY call scripts are SYNTHETIC
and fictional ("Example Plumbing Co.", Fictional City, PA; phone in
the reserved 555-0100 fictional range; website on the reserved
.example TLD). No real lead from store/leads.json is used anywhere;
0 paying clients exist, so there is no real tenant.

Two fixes found while building (not hidden): (a) the phone
validator first rejected the fictional 555-0100 range (its exchange
starts with 0) — the reserved fictional range is now explicitly
accepted, real NANP rules unchanged; (b) a string split across two
lines without parens in acceptance_flow.py raised IndentationError
— fixed with parens.

**Tests:** `scripts/check_unified_phase4.py` 70/70 PASS (schema
failure classes + Vapi draft + checklist gates/blocked + QA good
and 8 broken variants + acceptance happy path and 3 refusal
paths + no-live-deployment-path + no forbidden scope digits / no Bengali
in new files + store-unchanged). Full suite re-run after Phase 4:
**686/687 PASS** (baseline 616/617 + the new 70/70 suite; sole
failure remains the pre-existing `check_voice` sounddevice import,
VM-only).
