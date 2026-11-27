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

## Push — 2026-11-23 (Unified OS Phases 0–4)

PUSHED to GitHub (msredc5-bit/talvenor-master-os, branch main) on Boss's
word "push": 20 batches, 133 files (28 new + 105 modified), 1.16 MB.
Remote head before: 5723355abd1facbb4e4e3bbaeb5c6653bebb51aa (2026-11-21).
Remote head after batch 20: b054eac25cf266c75e7eae90a32b5dbede892ce9.
Sync record: ~/workspace/talvenor-master-os.muse-github-snapshot-sync.json
(97 entries after batch 20).
Batch 21 (this changelog note itself): pushed after batch 20; remote head
2c6d57170cfcccaef1aed5384e189a2680c6374d; sync record 98 entries.

NOT pushed in this push (deliberate): store/leads.json — 524 real prospect
businesses with emails/phones; the repo is PUBLIC. It stays local-only
until Boss explicitly says "push with leads".
Still on GitHub (snapshot push cannot delete): LOCAL-RUN-BANGLA.md and
00-CEO-Core/PROVIDERS-SETUP-BANGLA.md — stale old-named files, deletion
needs Boss's separate approval.
Voice models (~361 MB) stay gitignored and were never pushed.

## Skill cleanup — Agent Skills format + progressive-disclosure loader (2026-11-24)

Step 1 of the Anthropic-vs-Master-OS comparison brief
(~/workspace/anthropic-agentic-brief/comparison-2026-11-24.md). Boss's
word "Skill সাজানো শুরু করো". $0, no live brain, no push, local only.
Gates, trust gate, tool allowlist, $0 ledger: untouched.

Inventory (verified, not assumed): 118 .md files in skills dirs = 114
real skills + 3 Phase-1 pointer files + the SKILL_INDEX.md manifest.
The comparison brief's "~118 skill files" is confirmed; the "many
duplicates" is NOT confirmed — hash scan found ZERO byte-identical
groups (the 3 Phase-1 pointers were already deduped in Phase 1).
Same-stem groups: 17, all already recorded as differing-and-kept in
skills/SKILL_INDEX.md. One new precision finding: the two kit-qa
copies differ by exactly ONE word (line 71: engine "output has",
section "the output has") — both still kept per the rule, noted in
the manifest.

Reformat (114 files): each real skill file now carries a YAML
frontmatter block at the top — `name` (file stem) + one-line
`description` (Agent Skills format, agentskills.io: metadata name +
description at minimum). Content below the frontmatter verified
byte-identical to the pre-change backup for all 114 files. The 3
pointer files and the manifest were not reformatted (they are not
skills). No Bengali added anywhere; the 3 verbatim memory quotes and
all known exceptions untouched.

Loader (00-CEO-Core/skill_finder.py): now a real progressive-
disclosure loader. build_index() reads frontmatter only (name +
description, never full text); find_skills() ranks the index by task
keywords; load_skill() / load_skill_for_task() read the FULL file,
but only for a match. SKILL_ROOTS expanded from the 15 Agency roots
to ALL 28 skills dirs — the 34 Products/Content skills were invisible
to the finder before this change (registry was 84, now 114).
Pointer files and the manifest are excluded from the index; a pointer
stem (e.g. growth-agent) resolves to its canonical engine copy.
Wired into the Main CEO Bot's find_skill route
(00-CEO-Core/main_ceo_bot.py), which now also returns `loaded_skill`
(full text of the top match, or None) — additive key only, existing
keys unchanged. The Agency Chief has NO skill hook today, so nothing
was forced into its routing; the hook is marked as a NEXT STEP in its
module docstring (needs live-brain proof first). Same-name skills
across departments (caption-writer x3, content-planner x3,
publish-prep x3) stay separate; load by repo path when a name is
ambiguous.

Dedupe: no new pointer files — there was nothing byte-identical left
to point. The 14 differing pairs stay kept, as recorded.

**Tests:** skill_finder.py self-test PASS (registry 114, index 114,
loader loads full text on match only, pointer resolves to canonical,
unknown skill raises ValueError); main_ceo_bot.py self-test PASS.
Full suite re-run after the change: **683/689 PASS — identical to
the before baseline (683/689)**. The 6 failures are all in
check_voice (8/14) and are a pre-existing environment gap in this
VM: piper-tts, vosk, sherpa-onnx and sounddevice are not installed
(`pip list` shows none of them), so the import checks and the two
dependent checks fail. They failed identically before this change
and are unrelated to it (no skill file or loader code is imported by
the voice checks). Do not chase them here. Real store verified
unchanged after the change (all 8 store JSONs hash-identical;
memory still 3 entries / 13 boxes; leads still 524 / 163 first
mails). Backup of every modified file:
 /tmp/skill-cleanup-backup/repo/ (122 files, original paths kept).
One backup gap, recorded honestly: chief_of_staff_agency.py was not
in the pre-edit backup set — its change was a pure insertion of 8
docstring lines (comment only, no code touched); the original is
recoverable exactly by deleting those 8 lines, and from the GitHub
snapshot (remote head 2c6d5717). Also observed, not fixed (out of
scope): this changelog has no batch-21 push note for the 2026-11-23
push although the sync record holds 98 entries — worth checking
before the next push.

## Local-first Phase 1 — Development Brain + free-only guard (2026-11-24)

Boss approved the local-first plan 2026-11-24 ~23:30 Dhaka
(~/workspace/unified-business-os/local-development-strategy-2026-11-24.md).
Built by 3 parallel workers + coordinator integration. Local only, no push,
no live calls, no keys, $0.

- Config separation (00-CEO-Core/config.json): new top-level
  `development_brain` (enabled false, provider gemini,
  model gemini-2.5-flash-lite, free_only true, test_data_only true,
  fallback_chain gemini:gemini-2.5-flash-lite + openrouter:openrouter/free)
  and `production_brain` (mode mock, unlocked false). `brain` stays
  "mock", phase 11, version 0.9.0, spend cap $0. Gemini models updated
  to gemini-2.5-flash-lite / gemini-3.5-flash-lite (deprecated
  gemini-2.5-flash removed); OpenRouter free_only true, :free pinning kept.
- Brain modes (00-CEO-Core/brain.py): BRAIN_MODES now
  ("mock", "development", "live"). "development" builds the dev chain
  through the free-only guard; "live" raises RuntimeError unless
  production_brain.unlocked is exactly true (production stays locked).
  Mock paths unchanged. FreeOnlyViolation propagates unwrapped from
  _development_brain (fail-closed guard decision, not a config error).
- Free-only guard (NEW 00-CEO-Core/free_only_guard.py, v1.0): allowlist
  gemini {2.5-flash-lite, 3.5-flash-lite, 2.0-flash} + OpenRouter ids
  ending :free / openrouter/free; everything else (incl. unknown
  providers) is a violation. Enforced in LiveBrainAdapter.complete()
  (00-CEO-Core/live_brain.py, mode="development" only): check before
  each provider call (0 calls on violation), HTTP 429 / RESOURCE_EXHAUSTED
  is a hard stop (remaining providers NOT tried, rate_limited flag set),
  every call logged (provider, model, status, error, usage) to
  logs/dev_brain_calls.jsonl (new, gitignored) + in-memory log.
  In development mode build_provider_chain ignores the production
  `enabled` flags (the dev fallback_chain is the explicit selection;
  the allowlist is the gate); live mode keeps skipping disabled
  providers. DEFAULT_MODELS gemini is now gemini-2.5-flash-lite.
- Provider error surfacing: gemini_provider.py / openrouter_provider.py
  prefix re-raised errors with `HTTP {code}:` so 429s are detectable.
  GeminiProvider DEFAULT_MODEL is now gemini-2.5-flash-lite; docs updated
  (PROVIDERS-SETUP.md, SOURCE.md). Historical README/BUILD-LOG lines
  naming gemini-2.5-flash were left as history.
- Tests: NEW scripts/check_dev_brain.py 13/13 (allowlist, 429 hard stop,
  block-before-call, bad-key/timeout fallback, structured output,
  reasoning, tool selection with 0 tool executions, call-log shape,
  no-secrets, store unchanged — all offline, fake providers only).
  check_providers.py extended 43 -> 47 (dev/prod config checks, lock
  semantics, FreeOnlyViolation at build). check_live_brain.py 12 -> 13:
  --live probe rewritten to the Gemini free-tier dev-brain path
  (requires GEMINI_API_KEY; prints setup steps and exits 1 with no call
  attempted when the key is absent). check_phase6.py §6 updated to the
  lock semantics (it asserted the old live-mode behavior; phase7 /
  departments / specialists cascaded from it).
- Full suite re-run after the change: **703/709 PASS (baseline 683/689)**.
  The 6 failures are all in check_voice (8/14) — the same pre-existing
  environment gap in this VM (piper-tts, vosk, sherpa-onnx, sounddevice
  not installed); identical before and after. Real store verified
  unchanged by the check scripts. Dev-call log starts empty (29 stub
  lines written by worker verification runs were truncated).
- Live proof is Boss's step on his PC (not run here — no key exists in
  this VM): 1. key at aistudio.google.com/apikey (no card, no billing);
  2. setx GEMINI_API_KEY; 3. curl test with gemini-2.5-flash-lite;
  4. python scripts\check_live_brain.py --live (PASS only if mode live
  AND brain_kind development). Full steps in check_live_brain.py header.
- Backups: /tmp/phase1-backup-2026-11-24/{agent-a,agent-b,agent-c,
  coordinator}/ + durable ~/workspace/backups/phase1-2026-11-24-{agent-a,
  agent-b,agent-c,coordinator}/. Note: /tmp proved unreliable during this
  phase (worker A's first backup dir vanished between exec calls);
  durable workspace copies were made for every worker.
- Observed, not fixed (out of scope): dashboards/status.json +
  status.html were re-written during this phase by the running 3D
  dashboard bridge cron (it propagated the new honest_status
  local_dev_phase_1 entry) — no Phase 1 code touched the dashboards.
  Audit gaps remain open for later phases: store/leads.json not
  gitignored, permission holes, unauthenticated taskboard, non-atomic
  safety-critical writers, no emergency stop.

## Local-first Phase 2 — Skill finder hardening, dedup, Chief skill hook (2026-11-25)

Boss ordered Phase 2 to start 2026-11-25 ~00:12 Dhaka
(~/workspace/unified-business-os/local-development-strategy-2026-11-24.md
§8 Phase 2). Built by 3 parallel workers + coordinator integration.
Local only, no push, no live calls, no keys, $0. Gates, trust gate,
tool allowlist, free-only guard, $0 cap: untouched.

- Finder hardening (Worker A, `00-CEO-Core/skill_finder.py`, now
  770 lines): validation (`validate_skill_frontmatter`,
  `validate_index`, wired into `doctor()`); `version:` frontmatter
  parsed with `"1.0"` default (0 of 114 files carry one — none
  rewritten); execution tracking to `logs/skill_executions.jsonl`
  (LOG_PATH monkeypatchable; logging never raises); bare-name
  collision warns (UserWarning) + logs `ambiguous_bare_name`, then
  loads the FIRST match (behavior preserved). New API:
  `find_candidates(name)` → all matching paths;
  `load_skill_for_task` returns additive `"ambiguous"` + `"candidates"`.
  All signatures backward-compatible.
- Dedup (Worker B): index is now **112 real skills** (was 114),
  **5 pointer files** (growth-agent, kit-sales, repurpose-agent,
  kit-qa, script-writer). kit-qa merged (differed by 1 word, line 76);
  script-writer merged (6 lines; attribution folded into the engine
  copy). 12 same-stem groups KEPT with verified reasons (45–113
  changed lines each; renames unsafe — `scripts/check_phase7.py`
  check #3 derives section skill filenames from agent filenames, and
  engine renames break registry.json/STAFF.md). Ambiguity is bounded:
  by-name lookup deterministically returns the ENGINE copy
  (SKILL_ROOTS order); section copies reachable only by explicit repo
  path. `doctor()` → 112 skills, 0 problems; `validate_index()` → [].
- Chief skill hook (Worker C,
  `01-Agency-Department/chief_of_staff_agency.py`): in
  `_handle_task_inner`, AFTER the gated-action block (gated tasks
  return before any skill work — the gate path is byte-identical in
  behavior), non-gated tasks derive a query from title + type +
  payload `task_kind` and call `load_skill_for_task`; the result is
  attached as an additive `"skill"` key (name, repo path, loaded
  bool, `ambiguous`, `candidates`) on every non-gated result, and
  the skill name/path ride on the department managers' task copy as
  advisory context (managers ignore unknown keys; nothing is
  injected into any engine `EngineTask` payload). No existing result
  key or status changed. Loading is read-only and never executes a
  gated action; a lookup failure never breaks routing. The NEXT STEP
  docstring now records the wiring and the caveat that live-model
  skill execution still awaits Boss's PC live proof. Tested on the
  dev-brain MOCK path only — no live calls, no keys, no network.
- Tests: NEW `scripts/check_skills.py` — **14/14 decided checks pass**
  (2 skipped + 1 blocked, all on the environment write block, see
  below): 112 counts, frontmatter validation, progressive disclosure,
  finder locates (backup → backup-recovery-agent; "kit builder" →
  kit-builder, ambiguous, exactly 2 candidates; xyznoskill → none),
  Chief end-to-end on the mock path (caption_write → draft-ready +
  skill caption-writer, Agency engine copy), gated task returns
  before any skill work (no `skill` key), dept manager runs with the
  advisory skill context, kit-qa/script-writer 1 entry each (engine
  copy), 5 pointers excluded, all index paths + pointer targets
  exist, real store unchanged. `scripts/check_phase1.py` §19 extended
  to the 5 pointers and renamed "5 pointers + manifest" (only that
  check changed; it passes).
- Full suite re-run after the change: **NO MEANINGFUL PRINTED TOTAL —
  the environment write block was still active** (exec/shell/Python
  writes EPERM-blocked VM-wide since ~00:18 Dhaka;
  `tempfile.mkdtemp()` raises `FileNotFoundError: [Errno 2] No usable
  temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp',
  '/home/hatch/workspace/talvenor-master-os']`). Baseline was
  703/709 printed (scripts/) + 738/744 repo-wide; the new denominator
  is 726 scripts / 761 repo-wide (check_skills adds 17). Observed
  this run: **163 passes** (142 from the 10 scripts that printed
  totals + 21 PASS lines from scripts that crashed before printing a
  summary). Every other check either crashed on that exact tempfile
  error, failed with it in the detail, or is a knock-on of it (audit
  appends with no TEMP audit files; "still PASS" meta-checks because
  the sub-script exits 1; dashboard checks because
  `dashboards/status.html` is 0 bytes and `dashboards/status.json` is
  missing — bridge-cron write damage from 2026-11-24 18:29, before
  this work started, not touched by Phase 2). `check_voice` is 7/14
  (was 8/14): the extra failure is its "check_phase0 still PASS"
  knock-on. **Zero failures attributable to Phase 2 code** — the
  coordinator must re-run the full suite after the block clears.
  No check script was edited to remove tempfile usage.
- Backups: durable
  `~/workspace/backups/phase2-2026-11-25-agent-c/` (chief,
  check_phase1.py, changelog — all verified byte-identical to the
  pre-edit files by diff) + `/tmp/phase2-backup-2026-11-25/agent-c/`
  (same three files, also diff-verified identical). /tmp copies were
  made via the `muse.write` channel — the exec `cp` path is EPERM-blocked
  (0-byte files) — and /tmp proved unreliable in Phase 1, so the
  workspace copies are the durable ones.
- Observed, not fixed (out of scope): `logs/test-write.txt` (6 bytes,
  2026-11-24 18:27) sits in `logs/` from an earlier probe — not Phase
  2's. `logs/skill_executions.jsonl` (483 bytes, 2026-11-24 18:17)
  was NOT appended to by Phase 2 runs (the write block swallows the
  append inside `_log_execution`, as designed).
- Live-model skill execution through the Chief is [NOT TESTED] — it
  awaits Boss's PC live proof, same as the Phase 1 live brain.

## Local-first Phase 3 — Bounded Agent Runtime + subagents (2026-11-25)

Boss approved Phase 3 to start 2026-11-25 ~00:41 Dhaka
(~/workspace/unified-business-os/local-development-strategy-2026-11-24.md
§8 Phase 3). Built by Workers A + B, integrated + verified by Worker C
(this entry). Local only, no push, no live calls, no keys, $0. Gates,
trust gate, tool allowlist, free-only guard, $0 cap, 100-mail rule:
untouched (gate.py fix (d) below only closes a fail-open edge; it
gates MORE, never less).

- Runtime (Worker A, `00-CEO-Core/agent_runtime/`, now 8 files):
  `limits.py` (RuntimeLimits, CostTracker, $0 default cap),
  `context.py` (RuntimeContext + isolated child_context),
  `loop.py` (BoundedLoop: wall-clock / cost / iteration checks before
  every step, raising step -> "error", never crashes the caller),
  `runner.py` (AgentRuntime, mock draft step only; skill loaded
  read-only via skill_finder only when the task carries
  "skill_query"), `subagents.py` + `delegation.py` + `gate.py`
  (Worker B, see below), `__init__.py` (public API).
- Subagents (Worker B, `subagents.py`): SubagentManager spawn +
  run_parallel (results in input order, one failure never fails the
  batch), each fn in its own isolated child context; result contract
  {"name", "status" ok/error/timeout, "output", "evidence",
  "cost_usd"} validated by validate_result; raising fn -> "error",
  overrun -> "timeout" (thread finishes in the background — CPython
  limitation, documented in the module).
- Delegation (Worker B, `delegation.py`): decompose_task (steps list
  -> one step each; any other task -> single step) + DelegationEngine
  .execute(task, parent_context) -> {"status": "completed"|"partial"
  |"error", "steps": [...], "cost_usd": total}; mock draft steps
  only, $0; execute() never raises on a step failure.
- Gate (Worker B, `gate.py`): consults the REAL gate files read-only
  (human_approval_gateway.GATED_ACTIONS, trust_gate.COMMIT_ACTIONS /
  READ_ACTIONS / trust_check, tools.json gated tools gmail_send +
  n8n_trigger). enforce_gate never executes: gated -> {"allowed":
  False, "status": "pending-approval"}; unknown action fails closed.
- Coordinator-directed fixes (Worker C, all four verified by the new
  check script):
  (a) `loop.py` cost gap: a step returning "done" AND reporting cost
  over the $0 cap now ends "cost_limit" (post-record check before
  the step status is processed); a negative cost_usd ends "error"
  (same pattern as the non-numeric-cost check). No raising guard
  was added inside CostTracker.record — record() sits outside the
  loop's try/except and must never crash the caller (verified:
  record(-0.5) returns -0.5, no raise).
  (b) `context.py` child_context(): the child now inherits the
  parent's deadline — `child.deadline = min(parent deadline, child
  deadline)` — so a child can never outlive the parent's budget
  (verified: parent and child deadlines byte-equal).
  (c) `runner.py` delegation wiring: probe order is now
  ("execute", "run_task", "run", "delegate") — the old order could
  never engage Worker B's engine. _coerce_result handles the
  delegation dict properly: "completed"->"completed",
  "partial"->"error" (error text names the failed steps),
  "error"->"error"; output is the WHOLE delegation dict (steps
  evidence preserved); iterations = len(steps); cost_usd from the
  dict.
  (d) `gate.py` fail-open edge (coordinator follow-up, found while
  verifying Worker B's gate.py by reading it): the known-ungated-
  tool shortcut returned False without looking at the action verb,
  so {"tool": "draft_email", "action": "send"} was classified
  UNGATED. The verb is now checked against COMMIT_ACTIONS /
  GATED_ACTIONS BEFORE the known-ungated-tool shortcut. Verified:
  draft_email+send -> gated, draft_email alone -> allowed,
  action "draft" -> allowed.
- Integration verification (in-memory, stdin only, no files
  written): (i) multi-step task via AgentRuntime.run_task(task,
  delegate=True) -> "completed", 3/3 steps ok, cost 0.0; (ii) mock
  step with skill_query="backup" loads backup-recovery-agent
  read-only; (iii) {"tool": "gmail_send"}, {"action": "send"} and
  {"tool": "draft_email", "action": "send"} all go through
  gate.enforce_gate -> pending-approval, never executed, while
  {"tool": "draft_email"} and {"action": "draft"} stay allowed;
  (iv) store/*.json mtimes identical before/after.
- Acceptance run (Phase 3 proof, mock path): 3-step Talvenor draft
  task "research -> draft caption -> QA" via AgentRuntime with
  delegate=True -> status "completed", iterations 3, cost_usd 0.0,
  error None, all 3 steps "ok" with "[DRAFT] ... draft only. No live
  call, no send/publish/spend/delete/deploy." evidence
  ["mock-path: no live call", "kind=..."]. Trace length 0 on the
  delegated path (delegation does not log steps into the context
  trace; the steps evidence lives in the output dict instead —
  observed, not changed).
- Tests: NEW `scripts/check_agent_runtime.py` (661 lines) — **29/29
  checks pass** (0 skipped, 0 blocked): iteration cap; wall-clock
  timeout (0s budget + slow-step overrun); cost $0 (continue-step,
  done-step fix (a), negative cost fix (a), non-numeric cost);
  raising step -> error; child deadline inheritance (fix b) +
  child isolation; subagent spawn / parallel order / isolation /
  contract validation / raising -> error / overrun -> timeout;
  delegation decompose + execute completed / partial / decompose
  failure never raises; runner delegation wiring (fix c) +
  _coerce_result mapping + single-step fallback to the mock loop;
  gate preservation (6 gated actions, 3 draft allowed, unknown
  fails closed, fix (d) trio); skill loading via the runtime
  (backup -> backup-recovery-agent); no-live-calls source-scan of
  agent_runtime (requests / urllib / http.client / socket — none
  found) + mock_brain/draft_only flags; real store unchanged.
  First run was 25/29: the 4 failures were check-script bugs (the
  script set limits on BoundedLoop instead of the context — the
  loop enforces context.limits — and a live-read timing flake in
  the deadline assertion), fixed in the script; no runtime code
  changed for them.
- Full suite re-run after the change: **NO MEANINGFUL PRINTED TOTAL
  — the environment write block was still active** (exec/shell/
  Python writes EPERM-blocked VM-wide since ~00:18 Dhaka;
  `tempfile.mkdtemp()` raises `FileNotFoundError: [Errno 2] No usable
  temporary directory found`). Per-script, run once each (25
  scripts): PASS exit 0 — check_agent_runtime 29/29, check_skills
  14/14 decided (2 skipped + 1 blocked, all write-block). Printed
  totals, exit 1 — check_phase0 6/8, check_phase1 7/21,
  check_phase2 6/14, check_phase3 8/19, check_phase4 7/9,
  check_departments 8/21, check_live_tools 6/7 (sole FAIL cites
  the tempfile error), check_specialists 16/41,
  check_unified_phase4 69/70 (sole FAIL is the tempfile error in
  the acceptance-flow section), check_voice 7/14 (same as Phase 2:
  4 missing voice packages + gate-test TEMP + voice_test +
  check_phase0 knock-on). Crashed at startup on the tempfile error
  with no checks printed (13 scripts): check_dev_brain,
  check_providers, check_gate, check_phase5, check_phase6,
  check_phase7, check_engines, check_live_brain, check_memory_ledger,
  check_quiet_schedules, check_taskboard, check_unified_phase2,
  check_unified_phase3. Observed PASS lines across the 12 scripts
  that printed totals: 183 — this is NOT a suite total (13 scripts
  printed nothing, and the "still PASS" meta-checks double-count
  sub-scripts). Every failure observed either cites the tempfile
  error directly or is a knock-on of sub-scripts exiting 1 on it.
  **Zero failures attributable to Phase 3 code** — the coordinator
  must re-run the full suite after the block clears. No check
  script was edited to remove tempfile usage. Real store verified
  unchanged after the whole run (all 8 store JSONs, mtimes
  identical to the pre-run stat).
- Backups: durable `~/workspace/backups/phase3-2026-11-25-agent-c/`
  (loop.py, context.py, runner.py, gate.py, TALVENOR_CHANGELOG.md —
  all five verified byte-identical to the pre-edit files by diff).
- Observed, not fixed (out of scope): BoundedLoop.__init__ takes
  limits but run() enforces context.limits instead — the stored
  self.limits is never read. No live effect today (AgentRuntime
  always passes the same limits to both), but a caller passing
  different limits to the loop than to the context would be
  surprised. Delegated runs carry trace length 0 (see acceptance
  run above). The 3D-dashboard bridge cron is PAUSED (Phase 2);
  the dashboards are INTACT — coordinator re-checked during Phase 3
  verification: dashboards/status.html 10,626 bytes and
  dashboards/status.json 6,263 bytes, both valid, last good sync
  (the Phase 2 coordinator's "0 bytes / missing" observation and
  this entry's earlier wording of it were a transient mid-write
  state, not the files' actual state) — not touched by Phase 3.
- Live-brain skill execution through the runtime is [NOT TESTED] —
  it awaits Boss's PC live proof, same as the Phase 1 live brain.
  No live API call was made anywhere in Phase 3.

## Local-first Phase 4 — Workflow Engine + n8n adapter (Worker C part, 2026-11-25)

Boss approved Phase 4 to start 2026-11-25 ~01:04 Dhaka
(~/workspace/unified-business-os/local-development-strategy-2026-11-24.md
§8 Phase 4). This entry covers the Worker C scope only — workflow
engine, n8n adapter, test double, example workflow, runtime wiring,
and the new check script. Workers A (queue.py) and B (scheduler.py)
built in parallel in the same package; their files are covered by
the same check script below. Local only, no push, no live calls, no
keys, $0. Gates, trust gate, tool allowlist, free-only guard, $0
cap, 100-mail rule: untouched. Scheduler jobs stay PAUSED.

- Engine (NEW `00-CEO-Core/workflow_engine/engine.py`, 330 lines):
  `WorkflowEngine.execute(workflow, context=None, adapter=None)` →
  {"status": "completed"|"partial"|"error", "steps": [...],
  "cost_usd": 0.0}. A workflow is a list of steps (id, kind, input,
  optional tool/action). Every step consults the REAL Phase 3 gate
  (`agent_runtime/gate.py` `enforce_gate`) BEFORE running — a gated
  step (send/publish/spend/delete/upload, incl. `n8n_trigger`)
  comes back "pending-approval" and never executes. Mock kinds
  (draft/research/report/qa/status/search/list/read/mock) with no
  explicit tool/action are gate-checked as the "draft" verb; an
  explicit tool/action is always passed to the gate verbatim.
  `execute` never raises on a step failure (bad step → "error"
  step, bad workflow → "error" result). Runtime limits honoured
  when a RuntimeContext is passed (wall clock stops the run as
  "partial"; the context's max_iterations caps steps run). An
  "n8n" step that passed the gate would go through an adapter —
  the gate never allows `n8n_trigger` today, so that path is
  wiring only; the adapter is exercised directly against the test
  double, not by smuggling a trigger past the gate.
- n8n adapter (NEW `00-CEO-Core/workflow_engine/n8n_adapter.py`,
  274 lines): REST + webhooks ONLY, per strategy §5 (verified
  official n8n surface): create_workflow, activate_workflow,
  deactivate_workflow, list_workflows (`/api/v1`, header
  `X-N8N-API-KEY`), trigger_via_webhook (`/webhook/<path>`,
  `/webhook-test/<path>` for test — no dedicated "run workflow"
  REST endpoint was confirmed, so triggering is webhook-only),
  get_execution_status (`/api/v1/executions/<id>`). Base URL from
  env `N8N_BASE_URL` (default http://localhost:5678), API key
  from `N8N_API_KEY`, webhook shared secret from
  `N8N_WEBHOOK_SECRET` — env only, never files, never logged,
  never in error messages (errors carry method + path + HTTP
  status only). HARD CONSTRAINT: any base URL whose host is not
  localhost/127.0.0.1 is refused with ValueError at construction.
  Transport is stdlib `http.client` only. Webhook header auth is
  the Talvenor convention `X-Talvenor-Webhook-Secret`. Aligned
  with the existing `n8n_trigger` tool (tools.json gated, send;
  `live_tools.py` builds the request but never opens it) — this
  adapter does not duplicate or contradict it: the tool stays the
  gated draft-only entry point, the adapter is the localhost
  execution path behind the same gate.
- Test double (NEW `00-CEO-Core/workflow_engine/test_double.py`,
  257 lines): stdlib `http.server` on 127.0.0.1, ephemeral port,
  in-memory workflows + executions; POST /api/v1/workflows,
  GET list, POST activate/deactivate, POST /webhook/<path> (401
  without the shared-secret header), GET /api/v1/executions/<id>.
  Executions finish SYNCHRONOUSLY in the double (documented
  double behaviour — a real n8n runs async). Never started on
  import; tests/checks only; never a live n8n.
- Example (NEW `00-CEO-Core/workflow_engine/examples/
  talvenor-lead-triage.json`, 3 nodes): valid n8n workflow shape
  (Webhook → Code "Draft triage note" → Set "Draft reply
  fields"), active false, draft/report-only nodes, no send/
  publish node, no credential keys. Header note field states
  MANUAL IMPORT ONLY and NO credentials embedded.
- Package (`00-CEO-Core/workflow_engine/__init__.py`, 72 lines):
  public exports for queue, scheduler, engine, adapter, test
  double; each import defensive via importlib (a missing sibling
  leaves None + `_missing`, the package still imports). One fix
  found while testing: pre-assigning `engine = None` made
  `from . import engine` return None instead of the submodule —
  fixed by importing through importlib.
- Runtime wiring (`00-CEO-Core/agent_runtime/runner.py`, 188 →
  302 lines, additive only): a task carrying a "workflow" dict
  runs through the workflow engine, still bounded by the
  runtime's limits and the gate; missing engine falls back to the
  plain loop. `run_task` signature unchanged; single-step and
  delegation paths untouched. `check_agent_runtime.py` still
  29/29 after the edit (re-run, see below).
- Queue + scheduler (parallel Workers A/B, same package, covered
  by the same check script): `queue.py` (798 lines — DLQ status
  "dead_letter", requeue manual + explicit reason only,
  structured execution records inline, restart-recovery scan;
  finding: no writer today produces a stuck state, the scan is
  defensive) and `scheduler.py` (686 lines — 4 real job
  definitions, created PAUSED, activation only with an explicit
  Boss approval for scope `scheduler-activation:<job_id>`,
  paused job never due).
- Tests: NEW `scripts/check_workflow_engine.py` (1,024 lines) —
  **28/28 decided checks pass, 0 skipped, 1 blocked, exit 0**:
  queue 5/5 (DLQ transition, DLQ never drains, requeue reason,
  recovery scan + stubbed-store requeue/mark_failed, old-schema
  unchanged — real API, in-memory); scheduler 3/4 decided
  (definitions validate, activate-without-approval refuses 7/7,
  paused never due — the 4th, creation into a temp store, is
  BLOCKED on the environment write block, see below); adapter
  6/6 vs the test double (end-to-end, 401, non-localhost
  refused, key/secret never in errors, deactivate + 404, test
  webhook); example JSON 1/1; engine 4/4; gate 4/4; runtime
  wiring 3/3; no-live-calls source scan 1/1 (token-based, so
  docstring mentions and self-test string literals do not count);
  real store unchanged 1/1. First run was 27/28: the scan check
  failed on substring matches inside docstrings/string literals
  — fixed in the check (tokenize-based scan), no engine code
  changed for it.
- Acceptance run (Phase 4 Worker C proof, test double — run by
  hand, in-memory, $0, localhost-only): create example workflow
  → wf-1, active False; activate → True; list → ['wf-1'];
  trigger webhook talvenor-lead-triage with an Example Plumbing
  Co. payload → execution exec-1, status finished; status read
  back → finished, mode production. Runtime wiring proof in the
  same run: 3-step draft workflow via AgentRuntime → completed,
  iterations 3, cost 0.0. Real-n8n end-to-end is [NOT TESTED] —
  n8n lives on Boss's PC, not this VM; no n8n was installed here
  and no real n8n instance was called.
- Full suite re-run after the change: **NO MEANINGFUL PRINTED
  TOTAL — the environment write block was still active**
  (exec/shell/Python writes EPERM-blocked VM-wide since ~00:18
  Dhaka; `tempfile.mkdtemp()` raises `FileNotFoundError`).
  Per-script, run once each (26 scripts): PASS exit 0 —
  check_agent_runtime 29/29, check_skills 14/14 decided
  (2 skipped + 1 blocked, all write-block),
  check_workflow_engine 28/28 decided (1 blocked, write-block).
  Printed totals, exit 1 — check_departments 8/21,
  check_live_tools 6/7, check_phase0 6/8, check_phase1 7/21,
  check_phase2 6/14, check_phase3 8/19, check_phase4 7/9,
  check_specialists 16/41, check_unified_phase4 69/70,
  check_voice 7/14 (same as Phase 3: 4 missing voice packages +
  gate-test TEMP + voice_test + check_phase0 knock-on). Crashed
  at startup on the tempfile error with no checks printed
  (13 scripts): check_dev_brain, check_engines, check_gate,
  check_live_brain, check_memory_ledger, check_phase5,
  check_phase6, check_phase7, check_providers,
  check_quiet_schedules, check_taskboard, check_unified_phase2,
  check_unified_phase3. Observed PASS lines across the 13
  scripts that printed totals: 217 — this is NOT a suite total
  (13 scripts printed nothing, and the "still PASS" meta-checks
  double-count sub-scripts). Every failure observed either cites
  the tempfile error directly or is a knock-on of sub-scripts
  exiting 1 on it. **Zero failures attributable to Phase 4
  Worker C code** — the coordinator must re-run the full suite
  after the block clears. No check script was edited to remove
  tempfile usage. Real store verified unchanged after the whole
  run (all 8 store JSONs, sizes + mtimes identical to the
  pre-run stat).
- Backups: durable `~/workspace/backups/phase4-2026-11-25-agent-c/`
  (runner.py, TALVENOR_CHANGELOG.md — both verified
  byte-identical to the pre-edit files by diff).
- Observed, not fixed (out of scope): the scheduler-creation
  check stays BLOCKED until the write block clears (re-run then;
  scheduler.py's own self-test covers the same path with a real
  temp store). `scripts/run_office.py` carries a Phase 4 drain
  hook (dead_letter fields in its docstring) — Worker A's
  change, not this worker's; not verified here. The 3D-dashboard
  bridge cron is PAUSED (Phase 2); the dashboards are INTACT —
  re-checked during this work: dashboards/status.html 10,626
  bytes and dashboards/status.json 6,263 bytes, both valid, last
  good sync — not touched by Phase 4 Worker C.
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC
  (n8n installed there, npm Path A pinned 2.x). No live API call
  was made anywhere in Phase 4 Worker C work.

## Phase 5 (local-first) — Worker C: shared department runtime wiring + Chief hook — 2026-11-25 ~02:00 Dhaka

- Scope: this entry covers Worker C only (shared runtime module,
  Chief DEPARTMENT_ROUTING hook, run_office "execute" forwarding,
  check_phase5_local.py). The 8 departments' workflows/*.json and
  reports/report.py were built by sibling Phase 5 workers in the
  same window (one workflow JSON + one report.py per department,
  each workflow 3 steps with exactly one gated gmail_send/send
  step); Worker C verified them read-only and did NOT edit them.
  Worker C briefly created 8 duplicate "*-default.json" workflow
  files, then removed them to recoverable trash (trash_ids
  20261124-195717-a2c6814e…, 3aaa0b3a…, 23f7dd8d…, 06a89040…,
  614d3ff6…, f5146ab0…, 758e6b45…, 0ce83cf2…) once the sibling files
  were found — the repo now holds exactly one workflow JSON per
  department.
- Created: `01-Agency-Department/departments/department_runtime.py`
  (341 lines, stdlib only) — load_department_workflow() (first
  workflows/*.json sorted; dict + "steps" list or ValueError),
  execute_department_task() (builds {"title", "type":
  "dept_execute", "workflow"} and runs it through AgentRuntime;
  runtime "completed" -> "executed", a pending-approval gated step
  -> "executed-partial" (the gated step NEVER executed — designed
  outcome, not a failure), any other error -> "error"; returns the
  workflow-engine result dict, iterations, cost_usd 0.0, and a
  Phase 4-shaped execution_record {attempt, task_id, started_at,
  finished_at, status completed/partial/error, error, cost_usd};
  NEVER raises), compile_department_report() (importlib-loads the
  department's reports/report.py, calls compile_report(store_dir=,
  tasks=, runs=); any failure returns {"department", "error"} and
  never raises). 00-CEO-Core is added to sys.path inside the
  module; a missing AgentRuntime degrades to an "error" result.
  Self-test: `python3 .../department_runtime.py` prints OK
  (executed-partial, 3 iterations, $0.00).
- Modified: `01-Agency-Department/chief_of_staff_agency.py`
  (734 -> 770 lines; diff vs backup: +36 net, 0 lines removed
  except the restructured _log_task call) — DEPARTMENT_ROUTING
  branch only. When the incoming task has task.get("execute") is
  True AND the manager result is "draft-ready", the Chief lazily
  imports department_runtime and calls execute_department_task(),
  attaches result["execution"], sets result["status"] to
  "executed" / "executed-partial" (or "error" when execution
  itself errors), and adds "executions": [execution_record] to
  the _log_task record. Without "execute", or for
  pending-approval / unknown-task manager results, behaviour is
  EXACTLY as before (no new keys, no status change, no
  "executions" in the log). A failed lazy import attaches
  result["execution"] = {"status": "error", "error": ...}
  WITHOUT changing result["status"].
- Modified: `scripts/run_office.py` (592 lines, 2 lines changed,
  no behaviour change otherwise) — build_task() and the drain
  subprocess input now forward the "execute" key (additive only;
  verified: build_task(..., {"execute": True}) carries it).
- Created: `scripts/check_phase5_local.py` (new file; the old
  `scripts/check_phase5.py` unified-OS wrapper was NOT touched).
  9 decided checks, stdlib only, no tempfile anywhere (all store
  writes stubbed in-memory by patching
  chief_of_staff_agency.update_json before handle_task; the gated
  check stubs ApprovalGateway in-memory too). Result on first
  run: **PASS 9/9 decided, 0 BLOCKED, exit 0**.
- Acceptance (run by hand, in-memory stub, $0, TEST data only):
  Main CEO Bot -> Chief -> ChiefGrowthAgent -> LeadScoringAgent,
  business "agency", type "dept_sales", task_kind "lead_score",
  prospect "TEST Prospect LLC", "execute": True. CEO status
  **executed-partial**; Chief status **executed-partial**;
  execution status partial; steps research ok, draft ok, send
  **pending-approval** (gated step never executed); iterations 3;
  cost_usd 0.0; workflow 01-sales-growth-prospect_research;
  manager output is the real LeadScoringAgent draft (STRONG 85 ->
  Tier 1); the task log record carries "executions" with 1 record
  (status partial, cost 0.0). run_office.py carries "execute"
  through build_task (verified True); the CLI subprocess path was
  not run end-to-end (acceptance used the sanctioned in-memory
  stub route via main_ceo_bot.route_task).
- Regressions re-run by hand: check_workflow_engine.py **29/29**
  (was 28/28 decided + 1 BLOCKED in Phase 4 — the blocked
  scheduler-creation check now passes), check_agent_runtime.py
  **29/29**, check_departments.py **21/21 ALL PASS** (was 8/21
  under the block). No Phase 5 Worker C regression.
- Environment blocker: the VM-wide exec-write block reported since
  ~00:18 Dhaka appears CLEARED during this run — `cp` backups
  verified by sha256, and the tempfile-dependent scheduler-creation
  check in check_workflow_engine.py now passes. Not claimed as a
  fix (no system change was attempted); the coordinator should
  re-verify with a fresh tempfile probe and re-run the full suite.
  Real store verified unchanged by this work (sha256 of
  store/tasks.json + store/approvals.json before/after check 9,
  hashes match; the check-9 hashes were
  tasks.json 7541cff25c… / approvals.json 3c7e372f… at start).
- Backups: durable `~/workspace/backups/phase5-2026-11-25-agent-c/`
  (chief_of_staff_agency.py, run_office.py,
  TALVENOR_CHANGELOG.md — all three verified byte-identical to the
  pre-edit files by sha256 before editing).
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC
  (n8n installed there, npm Path A pinned 2.x). No live API call
  was made anywhere in Phase 5 Worker C work. Dashboards not
  touched; the bridge cron stays PAUSED.

## Phase 6 (local-first) — Agency lead chain in sandbox + run_office lead_chain wiring (Worker C, 2026-11-25)

- Wiring (ADDITIVE ONLY, `scripts/run_office.py` 592 -> 726 lines,
  +134): new `lead_chain` task type. `build_task()` forwards the
  top-level `prospect` (fixture id string or prospect dict; a
  prospect inside `payload` is honoured too). `run_one()` routes
  `lead_chain` to new `run_lead_chain()` -> `ChainRunner` from
  `00-CEO-Core/lead_chain` (package export first, fallback
  `lead_chain.chain.ChainRunner`), run against the `--store-dir`
  passed on the CLI, NEVER the real store by default. Fixture-id
  strings resolve via `lead_chain.fixtures` (`FIXTURES` key, or the
  prospect's own `id` field); dicts pass through unchanged. The
  result is returned as `{routed_to:
  "00-CEO-Core.lead_chain.ChainRunner", status: <chain status>,
  chain_result: <full ChainRunner record>, cost_usd}` and a
  `lead_chain` record is appended to `<store-dir>/tasks.json`
  (tasks-v1 shape; a failed log write never breaks the run). The
  drain-subprocess input forwards `prospect` for queued
  `lead_chain` records. `lead_chain` deliberately bypasses the
  CEO -> Chief route (the chain is its own router; it is
  draft-only and holds every gated step itself). Diff vs backup
  verified: only the `import uuid` line, the `build_task()`
  branch, the three new helpers + `run_one()` intercept, and the
  drain forwarding changed.
- Checks (NEW, `scripts/check_phase6_local.py`, 676 lines, stdlib
  only): **10/10 decided checks, 0 skipped, 0 blocked, exit 0**.
  (1) lead_chain imports + 13 steps in §10.C order
  (discovery -> verification -> qualification -> CRM dry-run ->
  outreach draft -> reply monitoring -> meeting -> sales ->
  onboarding -> service delivery -> QA -> deployment ->
  monitoring); (2) all 3 TEST fixtures load, TEST data only
  (ids TEST-L-0001/0002/0003, names TEST-*, .invalid emails,
  +1-555-01xx phones, .example websites); (3) happy path on the
  STRONG fixture in a temp store: status blocked, 13 steps, cost
  0.0, outreach pending-approval with [DRAFT] detail, nothing
  executed; (4) deployment always blocked; (5) missing-email
  fixture: chain failed, verification error "verification failed:
  missing email", later 11/11 steps skipped with reason
  "dependency: lead_verification", failure recorded in the chain
  state file under `<store>/chains/`; (6) duplicate re-run with
  the same prospect id returns the stored result (status
  duplicate, duplicate True, identical steps, no new files);
  (7) CRM dry-run via the real adapter: health NOT CONNECTED,
  would-be payload table leads / action upsert / key
  {domain: test-prospect.example}, live False; (8) gate: a step
  carrying {"tool": "gmail_send", "action": "send"} returns
  pending-approval through the REAL Phase 3 gate (WorkflowEngine
  + agent_runtime.gate), never executes, cost 0.0; (9)
  run_office.py --task lead_chain end-to-end via the REAL CLI
  on a temp store (rc 0, blocked, cost 0.0, 1 lead_chain log
  record); (10) real store hashes unchanged (tasks.json
  7541cff25c..., approvals.json 3c7e372f..., leads.json
  ba837980f8... before/after). Every temp store is a per-run
  `tempfile.mkdtemp()` dir (Phase 5 check-7 isolation lesson).
  The old `scripts/check_phase6.py` wrapper was NOT touched.
- Acceptance (REAL CLI path, temp store dirs, $0, TEST data
  only): (a) happy path `--input
  '{"prospect":"TEST-L-0001","execute":true}'` -> status blocked,
  cost 0.0, steps: discovery ok, verification ok, qualification
  ok, crm_dryrun ok, outreach_draft pending-approval,
  reply_monitoring ok, meeting ok, sales_process ok,
  client_onboarding ok, service_delivery ok, qa ok, deployment
  blocked, monitoring skipped (dependency: deployment); chain
  record + chain_log.jsonl under `<store>/chains/`, 1 lead_chain
  record in temp tasks.json. (b) failure path
  '{"prospect":"TEST-L-0003","execute":true}' -> status failed,
  cost 0.0, verification error "verification failed: missing
  email", stopped_by lead_verification, later 11/11 skipped.
  (c) duplicate re-run of (a) in the SAME store dir -> status
  duplicate, duplicate True, identical steps, no step
  re-executed; temp tasks.json holds both records (blocked, then
  duplicate). Real store hashes identical before/after all three
  runs (same three hashes as check 10).
- Adaptation note: the task brief's example id "TEST-STRONG" does
  NOT exist in Workers A/B's fixtures (keys are strong_tier1 /
  medium_tier2 / weak_incomplete; prospect ids TEST-L-0001/0002/
  0003). The literal input fails honestly: `run_office: FAILED:
  ValueError: prospect must be a dict, got str` (rc 1, temp store
  only). Acceptance used the real ids per the brief's "adapt the
  input shape" instruction. The resolver also accepts the
  FIXTURES key ("strong_tier1").
- Regressions re-run by hand: old `check_phase6.py` **14/14**,
  `check_phase5_local.py` **9/9**. Not touched: gate core
  (trust_gate.py, human_approval_gateway.py, permissions.py,
  tools.json), free_only_guard.py, Phase 3 runtime limits, any
  store/ file, the 100-mail rule, pricing, niches, the 112
  skills, dashboards, the bridge cron, `scripts/check_phase6.py`,
  the n8n Cloud MCP connector (never imported).
- Backups: durable `~/workspace/backups/phase6-2026-11-25-agent-c/`
  (run_office.py, TALVENOR_CHANGELOG.md — both verified
  byte-identical to the pre-edit files by sha256 before editing).
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC.
  Live-brain proof is [NOT TESTED] — mock/dev brain only. No live
  API call was made anywhere in Phase 6 Worker C work. No send,
  publish, spend, delete, or deploy happened or can happen on
  this path (gated send held pending-approval; deployment always
  blocked).

## Phase 7 (local-first) — Founder Dashboard + Main CEO reporting: control plane + approval centre (Worker C, 2026-11-25)

- Control plane (NEW, `00-CEO-Core/control.py`, 424 lines, stdlib
  only): `ControlState` over `store/control.json`, schema
  "control-v1" (`paused`, `emergency_stop`, derived `state` label
  running/paused/emergency_stop, `reason`, `set_by`, `set_at`,
  append-only `history` capped at 100 with `history_dropped`
  counting every drop, never silent). `pause` / `resume` /
  `emergency_stop` / `clear_emergency_stop` — resume clears ONLY
  `paused` and REFUSES (ControlRefused) while an emergency stop is
  set; clearing a stop needs a non-empty reason (ValueError
  otherwise). Load: missing/unreadable file = running state, never
  an exception (fail-open only when no state was ever written);
  existing-but-corrupt JSON (or wrong schema) raises
  ControlCorruptError — fail-closed on corruption. Writes via
  `store_io` (atomic + locked). Self-check in-module passes.
  The derived `state` label was added so Worker A's dashboard
  reader (`sync_status.read_control`) shows paused/running instead
  of "unknown"; the flags stay the truth.
- Wiring (ADDITIVE ONLY): `scripts/run_office.py` 726 -> 751 lines
  (+27/-2) — `drain_queue()` consults the control plane FIRST,
  before any task executes: halted (paused / emergency_stop /
  corrupt control file) -> nothing runs, nothing is deleted, a
  `control_halt` note is recorded in `store/audit.log`, summary
  reports `halted: True`, exit 0; running drains gain
  `"halted": False` in the summary. `00-CEO-Core/workflow_engine/
  scheduler.py` 686 -> 729 lines (+44/-1) — new `_control_halted()`
  consults `<store>/control.json` next to the store's
  `schedules.json`; `activate_job` refuses (ActivationRefused)
  while halted, `should_run_job` returns (False, "control halted")
  and `due_jobs` reports every job not-due while halted. No
  behaviour change while the control state is running (default).
- Approval centre (NEW, `00-CEO-Core/approval_centre.py`, 215
  lines, stdlib only): `ApprovalCentre` + module functions
  `list_pending(gateway)` (pending records with age_minutes,
  expires_in_minutes, expired flag, allowed_gate_words),
  `request_approval(action, detail, requested_by)` ->
  `gateway.request`, `decide(approval_id, decision,
  gate_word=None, decided_by="Boss")` -> `gateway.approve` /
  `gateway.reject`. It NEVER writes approvals.json directly — the
  gateway's `_save` is the only writer; wrong gate word, expired
  record, or already-decided record raises the gateway's own error,
  never swallowed, never auto-retried. `scripts/approve.py` was
  read first and is a FULL gateway wrapper already (list/approve/
  reject, --approvals-path) — so the centre reuses the gateway
  rather than duplicating it, and the new thin CLI
  `scripts/approval_centre.py` (85 lines: `list` / `approve <id>
  <gate-word>` / `reject <id>`, --approvals-path before or after
  the subcommand, prints JSON) delegates to the centre module.
  Decisions are Boss-only (`decided_by` defaults to "Boss").
- Checks (NEW, `scripts/check_phase7_local.py`, 500 lines, stdlib
  only, per-run `tempfile.mkdtemp()` dirs): **11/11 decided
  checks, 0 skipped, 0 failed, exit 0**. (1) missing control file
  loads as running; (2) pause halts drain consult + scheduler due
  (due True -> False, due_jobs all not-due), resume restores due;
  (3) emergency_stop survives resume (resume refused), clear
  restores running; (4) clear needs a non-empty reason (3/3 empty
  refused, stop stayed); (5) corrupt control.json halts
  fail-closed (consult raises; real drain rc 0, halted True, task
  still queued, `control_halt` in audit.log); (6) centre lists
  pending via the real gateway (2 records, age/expiry present);
  (7) wrong gate word raises, right word records approved
  (decided_by Boss); (8) reject records rejected, expired record
  cannot be approved (fresh gateway re-reads the backdated file);
  (9) dashboard: `sync_status.py` on a temp copy shows the new
  Phase 7 keys AND seeded numbers match (task_counts queued 1 /
  done 1 / total 2, approvals pending 1 id a1, control paused True
  state "paused", 8 departments, ceo_report available False) —
  Worker A landed mid-run and the check was re-run against the
  landed code instead of skipping; (10) CEO report: Worker B's
  `generate_report(tmp, "weekly")` on a seeded temp store returns
  tasks total 2 (done 1, queued 1), approvals pending 1, window 7
  days, Markdown twin carries "2 task(s) in the store", temp store
  untouched — Worker B landed mid-run and the check was built
  against the real `ceo_reporting.generate_report` /
  `render_markdown` API instead of skipping; (11) real store
  hashes unchanged (tasks.json 7541cff25c..., approvals.json
  3c7e372f..., leads.json ba837980f8... before/after). The old
  `scripts/check_phase7.py` (unified-OS wrapper) was NOT touched.
  Two check-writing lessons: the gateway only reads approvals.json
  at construction, so an expiry test must decide through a FRESH
  centre/CLI run; `scheduler.py`'s own `__main__` token scan is
  self-defeating (its literal token list contains every token it
  scans for) — pre-existing, NOT a Worker C regression, left
  untouched, reported to the coordinator.
- Acceptance (REAL CLI path, temp store dirs, $0, TEST data only):
  (a) pause -> `run_office.py --drain-queue` rc 0, halted True,
  reason "paused: ...", 1 queued caption_write task NOT executed,
  record intact, `control_halt` in audit.log; resume -> drain
  executes it (status done). (b) emergency_stop ->
  `activate_job` refused (ActivationRefused, "control plane
  halted"), `due_jobs` all 4 jobs not-due with "control halted"
  reason; `clear_emergency_stop` with reason -> activation
  allowed again (active + activated marker). (c) approval centre:
  request "send" on a temp approvals file -> approve with gate
  word "send" -> approved in the file (decided_by Boss);
  dashboard (`sync_status.collect_status` on the temp store)
  showed pending 1 / approved 0 before and pending 0 / approved 1
  after. Real store hashes identical before/after all three runs
  (same three hashes as check 11); no `store/control.json` was
  created in the real store.
- Regressions re-run by hand: `check_phase6_local.py` **10/10**,
  `check_phase5_local.py` **9/9**, `check_workflow_engine.py`
  **29/29**, `check_agent_runtime.py` **29/29**, `check_skills.py`
  **17/17**, `check_departments.py` **21/21**. Not touched: gate
  core (trust_gate.py, human_approval_gateway.py, permissions.py,
  tools.json), free_only_guard.py, Phase 3 runtime limits, any
  store/ file's real data, the 100-mail follow-up rule, pricing,
  niches, the 112 skills, store/leads.json, dashboards/status.html
  + status.json directly (Worker A owns them via sync_status.py),
  the bridge cron, the n8n Cloud MCP connector (never imported),
  Worker A's `sync_status.py` / Worker B's `ceo_reporting/` /
  `reports/ceo/` (read-only consultation + checks only).
- Backups: durable `~/workspace/backups/phase7-2026-11-25-agent-c/`
  (run_office.py, scheduler.py, TALVENOR_CHANGELOG.md — all
  verified byte-identical to the pre-edit files by sha256 before
  editing).
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC.
  Live-brain proof is [NOT TESTED] — mock/dev brain only. No live
  API call was made anywhere in Phase 7 Worker C work. No send,
  publish, spend, delete, or deploy happened or can happen on
  this path (drain halts under control; gated send held
  pending-approval; deployment always blocked).

## Phase 7 (local-first) — Founder Dashboard + Main CEO reporting: dashboard extension + CEO reporting generator + coordinator verification (2026-11-25)

- Dashboard extension (Worker A): `scripts/sync_status.py` 554 -> 862
  lines (+308), additive only — new helpers `read_departments()`,
  `read_task_counts()`, `read_approvals_detail()`, `read_control()`,
  `read_ceo_report()` + 3 new cards (Founder Control, Departments,
  CEO Report — latest). `dashboards/status.json` gains `departments`
  (8/8, workflow present, report compiles, last_execution "unknown"),
  `task_counts` (real counts from store/tasks.json), `approvals`
  (pending list + count), `control` (paused/emergency_stop/state),
  `ceo_report` (latest report, period, generated_at, counts).
  Backup: `~/workspace/backups/phase7-2026-11-25-agent-a/sync_status.py`
  (sha256 96f9b14ea16b1c69089b8c3734a51860acf6a1d346b528cacc0995632c211d7b,
  verified byte-identical to the pre-edit file by the coordinator).
  A loop-variable shadowing bug found + fixed in the same edit.
  Verified: sync exit 0, old-vs-new diff shows only the 3 added cards
  + 5 new keys, `check_phase7.py` 18/18, determinism (identical sha256
  on re-run).
- CEO reporting generator (Worker B): NEW `00-CEO-Core/ceo_reporting/`
  (`__init__.py` 29 lines, `report.py` 919 lines) + NEW
  `scripts/generate_ceo_report.py` (144 lines) +
  `00-CEO-Core/CEO-README.md` +14 lines. Generates
  `reports/ceo/daily|weekly|monthly-<date>.md` + `.json` from the real
  store (tasks, approvals, usage ledger, memory, schedules, config,
  lead chain, departments) — every figure cites its source file;
  missing sources read "unknown", never invented. `store/leads.json`
  is never read (grep-verified by the coordinator). Monthly = last
  30 days (labelled, not a calendar month). First run: window end
  2026-11-24 20:31 UTC — tasks 1 (1 done), approvals 0 pending,
  usage 64 calls / $0.00, lead chain 0 runs, Gate 0 NOT PASSED, email
  PAUSED since 2026-11-14. Verified: seeded/empty temp stores,
  determinism, independent grep/count match.
- Coordinator verification (2026-11-25 ~02:40 Dhaka): read every
  new/modified file; diffs of sync_status.py / run_office.py /
  scheduler.py against backups are additive only; full suite re-run
  by hand — **808/814 scripts printed (843/849 repo-wide), distinct
  764/770 (799/805 repo-wide)** — delta vs Phase 6 exactly +11
  (the new `check_phase7_local.py`), zero regressions; only failures
  the 6 baseline `check_voice` environment gaps. Acceptance re-run
  by hand on temp stores: paused drain executed nothing (task stayed
  queued, `control_halt` in audit.log), resumed drain executed it to
  done; emergency_stop refused scheduler activation and reported no
  job due; clear-with-reason restored running; approval-centre CLI
  request -> list -> approve with gate word "send" -> approved,
  decided_by Boss. Real weekly CEO report regenerated from the real
  store (tasks=1 in window, approvals 0 pending, 64 calls, $0.00);
  dashboard refreshed by `sync_status.py` shows all 3 new cards and
  `ceo_report.available: true`.
- Coordinator fix (1 line, `scripts/sync_status.py` `read_ceo_report`):
  the dashboard looked up `data["task_counts"]` but Worker B's report
  JSON uses the key `"tasks"` (with `by_status` inside), so the card
  showed task_counts "unknown" while the report had the numbers. Fixed
  to read `tasks.by_status` (with a `task_counts` key fallback);
  re-ran sync — dashboard now shows `task_counts: {"done": 1}`.
- Known issue (pre-existing, NOT a Phase 7 regression, left untouched):
  `00-CEO-Core/workflow_engine/scheduler.py` `__main__` self-test is
  self-defeating — its forbidden-token tuple contains "requests.", so
  the scan trips on its own literal; confirmed identical in the
  pre-Phase-7 backup (line 678). The real regression gate
  `check_workflow_engine.py` is 29/29. Fix the scan (exclude its own
  literal / docstrings) in a later phase.
- Gap (remaining): no operator CLI for pause/resume/emergency-stop
  yet — the control plane is an importable API (`ControlState`) only;
  Boss would pause via a Python one-liner until a `scripts/control.py`
  CLI exists (recommend for Phase 8 or a small follow-up).
- Not touched: gate core, free_only_guard.py, Phase 3 runtime limits,
  any store/ file's real data (hashes unchanged — see the Phase 7
  completion report), the 100-mail follow-up rule, pricing, niches,
  the 112 skills, store/leads.json, the bridge cron (still running
  every 10 min), the n8n Cloud MCP connector (never imported), the
  old `scripts/check_phase7.py` wrapper (18/18, untouched).
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC.
  Live-brain proof is [NOT TESTED] — mock/dev brain only. No live
  API call was made anywhere in Phase 7. No send, publish, spend,
  delete, or deploy happened. STOP after Phase 7 — no Phase 8 until
  Boss approves it.

## Phase 8 — Complete local end-to-end tests (2026-11-25, local-first)

- Built a pytest suite ALONGSIDE (not instead of) the check_*.py
  scripts: new `tests/` layout (conftest.py + 11 test files, 3,308
  lines) covering brief §21 items 1–24 + scenarios A–G in sandbox.
  Run: `~/workspace/phase8-pytest-venv/bin/python -m pytest tests/ -q`
  (pytest 9.2.0 in a venv — plain `pip install --user pytest` fails
  on this VM with PEP 668 externally-managed-environment; the venv
  lives at `~/workspace/phase8-pytest-venv`, outside the repo).
- Result (coordinator's own run): **230 passed, 2 skipped, 1 xfailed,
  0 failed, 233 collected, in 2.33s.** Skips: event-bus test (item 9
  — no event bus exists) and policy-engine test (item 14 — the
  bounded policy model was approved in principle but never built);
  both marked [NOT TESTED] with reasons, never faked. Xfail:
  Scenario D (QA failure → recovery task + manager notification —
  `tenant_qa.run_qa` returns a fail verdict only; no mechanism
  creates a recovery task or notifies a manager).
- Full check suite re-run by the coordinator: **808/814 printed
  (843/849 repo-wide), distinct 764/770 (799/805 repo-wide)** —
  identical to the Phase 7 baseline, zero regressions; only failures
  are the 6 baseline check_voice environment gaps. Phase 8 adds no
  check_*.py script, so the check denominator is unchanged.
- Candidate fixes, both done: (1) scheduler.py `__main__` self-test
  fixed (+10/−2 lines, self-test block only — scan now excludes its
  own block and checks `sk-` as a key-like regex; self-test prints
  OK, exit 0; regression tests added; scheduler logic untouched).
  (2) `scripts/control.py` operator CLI built (95 lines, status /
  pause / resume / emergency-stop / clear over the real ControlState;
  exit codes 0/2/3/4) — closes the Phase 7 remaining task.
- Acceptance re-run by the coordinator through the real CLI path
  (temp stores, $0): lead_chain TEST-L-0001 → blocked, cost $0.0,
  chain record + chain_log.jsonl written; control CLI full cycle
  (status → pause → resume → emergency-stop → clear) with correct
  state transitions and history; CEO weekly report regenerated from
  the real store (1 task done, 0 approvals pending, 64 calls,
  $0.00). The end-to-end pytest (`tests/test_end_to_end.py`) runs
  CEO → departments → workflows (n8n via the Phase 4 test double on
  127.0.0.1) → dashboard readers → CEO report, $0.
- Coordinator incident, fixed: the first CEO-report invocation used
  `--store-dir <tmp>` without `--out-dir`, so the CLI wrote the
  temp-store report over `reports/ceo/weekly-2026-11-24.md` + `.json`
  (the Phase 7 first weekly report). Restored immediately by
  regenerating from the real store — figures identical to Phase 7
  (1 task done, 0 pending, 64 calls, $0.00); only the Generated
  timestamp changed. Lesson recorded in the Phase 8 report: the CLI
  reads from `--store-dir` but writes to `--out-dir` (default
  `reports/ceo/`); acceptance runs must pass both flags.
- Not touched: gate core, free_only_guard.py, Phase 3 runtime limits,
  any store/ file's real data (hashes unchanged — tasks
  7541cff25c…, approvals 3c7e372f…, leads ba837980f8…), the 100-mail
  follow-up rule, pricing, niches, the 112 skills, store/leads.json,
  the bridge cron (still running), the n8n Cloud MCP connector
  (never imported — grep-verified), the 3D dashboard artifact.
  No send, publish, spend, delete, or deploy happened. $0 spent.
- Real-n8n end-to-end is [NOT TESTED] — it awaits Boss's PC.
  Live-brain proof is [NOT TESTED] — mock/dev brain only. No live
  API call was made anywhere in Phase 8. STOP after Phase 8 — no
  Phase 9 until Boss approves it.

## Push 2026-11-25 — Part 1: Muse Spark key slot + PC package (Worker A)

Boss's order 2026-11-25 ~03:17 Dhaka (voice call): ready everything for
the GitHub push + a PC package to download. This entry covers Part 1
only — the Muse Spark key slot and the PC-package refresh. Parts 2
(push) and 3 (ZIP) are the coordinator's. Local only, no push, no ZIP
built here, no live calls, no keys, $0. Email PAUSED, deployment
BLOCKED — untouched.

- Muse Spark key slot (Worker A): `meta_provider.py` reads NO env var
  today — it uses only the connector Secure Vault surrogate
  (`custom.meta-model-api-2`), which does not exist on Boss's PC. So
  the slot uses **`META_API_KEY`** (the name the task fixed for the
  no-env-var case). The provider now has two key paths, in order:
  (1) `META_API_KEY` env var — the PC path (Bearer auth, key read
  only inside `complete()`); (2) the connector surrogate — the Muse
  VM path, used only when no env var is set, error message updated
  to name `META_API_KEY` as the PC alternative. A missing key with
  no surrogate gives a clean error naming `META_API_KEY`, no network
  attempted. `config.json` `providers.meta.env_var` is now
  `"META_API_KEY"` (was `null`); model stays `muse-spark-1.3`;
  `key_via` + a note record that Muse Spark is paid/credit-based and
  PRODUCTION-brain only. `brain` stays `"mock"`, `production_brain.
  unlocked` stays `false`, dev brain (Gemini free) untouched.
- Free-only guard UNCHANGED and still blocks Meta in dev mode:
  `free_only_guard.py` was not edited (meta is in
  `_NEVER_FREE_PROVIDERS`); verified in-memory —
  `is_free_model("meta", "muse-spark-1.3")` is False,
  `check_call("meta", "muse-spark-1.3")` raises `FreeOnlyViolation`,
  and `build_provider_chain` in development mode with a meta entry
  raises `FreeOnlyViolation` before any provider is built. No paid
  fallback was added; no allowlist change.
- Docs: `PROVIDERS-SETUP.md` — Meta row now names `META_API_KEY`
  (key from dev.meta.ai; the connector cannot read it back) + new
  §4 "Muse Spark — the production brain key (paid, PC only)":
  `setx META_API_KEY "paste-key-here"`, direct curl test to
  api.meta.ai first (the 2026-11-20 probe failed tunnel 403, $0
  spent, key validity still unproven), full adapter proof only
  after Boss unlocks the production brain (his separate word);
  `check_live_brain.py --live` proves the Gemini DEV brain, not
  Meta. Old §4/§5 renumbered §5/§6; §6 status notes the slot exists
  but no key value is on record. `LOCAL-RUN.md` — new Step 5 (brain
  keys: Gemini free dev proof + Muse Spark paid proof), NOT LIVE
  table gains Muse Spark / Gemini key rows, file list gains
  PROVIDERS-SETUP.md. `run_local.bat` — new step [0/3] prints key
  status (set / not set — values never printed); dashboard flow
  otherwise unchanged. `live_brain.py` / `brain.py` docstrings
  corrected (Meta key is no longer "connector only").
- Checks: `scripts/check_providers.py` updated to the new slot —
  PROVIDERS table meta env var `META_API_KEY`; the old
  "uses connector path, not env var" check replaced by a dual-path
  check + a missing-key-with-no-surrogate check (surrogate loader
  patched out); sections 4–6 (simulated success / API error /
  timeout) now run for Meta too with a fake key in-process; §9 now
  requires `meta.env_var == "META_API_KEY"`; §10 secret scan now
  covers `meta_provider.py`. Count moves 47 → 51 checks in that
  script. No other check script was edited.
- Verification (in-memory, offline — the environment write block
  below prevents running the check scripts themselves):
  16/16 passed — provider constructs key-unset (0 calls,
  muse-spark-1.3); dual path present; missing key + no surrogate
  errors naming `META_API_KEY` with no network; simulated success
  via the env path (text + 15 tokens); simulated API error +
  timeout; env var takes precedence over a broken surrogate;
  guard blocks meta (above); dev chain with meta raises;
  live chain `[openai, meta, mock]` builds
  `[openai-live, meta-spark-live]` with models
  `[gpt-4o, muse-spark-1.3]`; config slot + mock/lock/dev-brain
  assertions; meta absent from the dev fallback chain. No live
  call was attempted (no key exists in this VM; fake opener only).
  Secret scans (the check scripts' own regexes) over all changed
  files: clean — the one hit is the pre-existing regex literal
  inside `check_providers.py` §10 itself, which that section
  excludes by design. No key value exists anywhere in the repo
  (placeholders only: `"paste-key-here"`).
- Full suite re-run: **NOT POSSIBLE in this session — the
  environment write block is still active** (exec/shell/Python
  writes EPERM-blocked VM-wide since 2026-11-25 ~00:18 Dhaka, same
  condition the Phase 2 and Phase 3 changelog entries record;
  `tempfile.mkdtemp()` raises `FileNotFoundError: [Errno 2] No
  usable temporary directory found`). Before-baseline run once
  each in this session (pre-edit): check_agent_runtime 29/29,
  check_departments 8/21, check_phase0 6/8, check_phase1 7/21,
  check_phase2 6/14, check_phase3 8/19, check_phase4 7/9,
  check_phase5_local 9/9, check_phase6_local 5/10,
  check_phase7_local 1/11, check_specialists 16/41,
  check_unified_phase4 69/70, check_voice 7/14, check_skills +
  check_workflow_engine ALL PASS; 13 scripts crash at startup on
  the tempfile error (incl. check_providers, check_live_brain,
  check_dev_brain) and both out-of-scripts checks
  (check_drawer_memory, check_mcp). The after-run shows the
  identical pattern — **zero failures attributable to this Part 1
  work** — but it is NOT a suite total; the coordinator must
  re-run the full suite after the block clears. No check script
  was edited to remove tempfile usage. The Phase 8 baseline
  (808/814 printed, 843/849 repo-wide) is unchanged as the
  reference until that re-run.
- Backups: durable `~/workspace/backups/push-2026-11-25-agent-a/`
  (config.json, PROVIDERS-SETUP.md, live_brain.py,
  meta_provider.py, check_providers.py, run_local.bat,
  LOCAL-RUN.md, TALVENOR_CHANGELOG.md — all pre-edit copies +
  SHA256-BEFORE.txt + baseline-scripts-BEFORE.log).
- Live-brain proof is [NOT TESTED] — it awaits Boss's PC
  (META_API_KEY + curl test, then his production-unlock word).
  No live API call was made anywhere in Part 1. STOP — no push,
  no ZIP from this worker.

## FOUNDER OS F1 — Agency Core and Brain Preservation (2026-11-26)

- Founder approved the FOUNDER OS Phase 0 audit ("ok", 2026-11-26 17:55
  Dhaka). FOUNDER OS Phases F0–F10 are now the only numbering (M0):
  `README.md` + `TALVENOR_MASTER_ARCHITECTURE.md` headers updated to
  FOUNDER OS (docs only, no code, no renames).
- **Live-brain proof recorded as a FACT (M1), not a file:** Boss's PC,
  2026-11-26 04:13 Dhaka — `setup_brain.py` saved the dev brain as
  `ollama:qwen2.5-coder:1.5b`, chain
  [ollama:qwen2.5-coder:1.5b, ollama:gemma4:12b,
  gemini:gemini-3.5-flash-lite, openrouter:openrouter/free];
  `check_live_brain.py --live` PASS in 1.9s, tokens 83/23/106
  ("Talvenor Master OS is a personal CEO agent designed to assist
  solo founders in managing their businesses effectively.");
  second probe PASS 2.7s at 06:03. Source: Boss's screenshots.
  This snapshot's brain stays `mock` — the PC config was NOT copied
  here. Full note: `docs/live-brain-proof-2026-11-26.md` + the
  `development_brain.note` in `00-CEO-Core/config.json`.
- **gemma4:12b removed from the dev fallback chain (F1):** it cannot
  run on an 8 GB PC (llama-server OOM crash, verified twice
  2026-11-26) and keeping it wasted a 5-minute timeout on every
  cold start. New chain: [ollama:qwen2.5-coder:1.5b,
  gemini:gemini-3.5-flash-lite, openrouter:openrouter/free].
  Changed: `config.json` fallback_chain + note, `live_brain.py`
  DEFAULT_MODELS, `brain.py` _DEV_DEFAULT_MODELS,
  `ollama_provider.py` DEFAULT_MODEL, `setup_brain.py`
  OLLAMA_PREFERENCE, `check_providers.py` fixture, setup-step help
  text in `check_live_brain.py`, `PROVIDERS-SETUP.md`, `LOCAL-RUN.md`,
  `CLAUDE-CODE-PROMPT.md` (Claude Code now runs on
  qwen2.5-coder:1.5b — gemma4:12b crashed it). NOT changed: the
  Ollama adapter itself; gemma4:12b stays listed as an available
  model (`providers.ollama.models`) and in the free-only guard tests
  (any Ollama model is free-only). This change stays LOCAL — no push.
- **Environment checker (C1–C5) built:** `check_pc_env.bat` (repo
  root, double-click, CRLF) + `scripts/check_pc_env.py` — checks only,
  installs nothing, writes `pc-env-check.txt` and opens it in
  Notepad. C1 Git, C2 Node.js, C3 Antigravity, C4 n8n, C5 voice
  models. ZIP delivered to Boss separately (see the F1 completion
  report, `~/workspace/unified-business-os/f1-completion-report-2026-11-26.md`).
- **PENDING (not done in F1):** M2 — push the 3 Ollama-timeout files
  to GitHub; needs Boss's separate "push" word. The gemma4-removal
  change also stays local until that push. Bengali voice-prompt
  decision (restore Bengali prompts/triggers in `voice/loop.py` or
  keep English) — prepared as a question for Boss, `voice/loop.py`
  untouched.
- Verification: check suite + pytest re-run (see the F1 completion
  report for totals). Nothing in F1 sends, publishes, spends, or
  deploys.

## FOUNDER OS F2 batch 1 — Founder Command Center, first live modules (2026-11-26)

- Founder approved F2 ("F2 shuru koro", 2026-11-26 18:47 Dhaka).
  Batch 1 builds Command Center modules 1, 5, 6, 7, 11 only — the
  other 14 modules are batch 2+ and were NOT built.
- **New page:** `dashboards/command-center.html` (static HTML + JS,
  no framework). Sidebar lists all 19 modules (audit §11): the 5
  live ones link to their sections, the other 14 are marked with
  their planned batch (batch 2 / batch 3 / F7 / F8). Open at
  http://localhost:8765/command-center.html (run_local.bat).
  1. Founder Overview — phase, paying clients, first mails, email,
     Gate 0, spend, tasks done, voice, approvals pending.
  5. Agent Team Roster — all 69 registry agents with worker state
     (draft/coded/unknown from the [MOCK DRAFT] marker) and last
     skill-load time from logs/skill_executions.jsonl; search +
     department/worker filters. Roster cross-check: 53 draft /
     16 coded matches the audit's 53/69 [MOCK DRAFT] count.
  6. Main CEO Dashboard — the generated weekly CEO report, shown
     as generated (executive summary, tasks, approvals, next
     actions, risks/blocked).
  7. Agency Dashboard — the 8 departments: workflow present,
     report compiles, last execution.
  11. Approval Center — pending approval cards with the 20-minute
      TTL countdown. Allow needs the exact gate word typed by Boss;
      there is no auto-approve and no "always allow". Decisions go
      through the EXISTING gateway only (ApprovalCentre.decide);
      no new approval path was invented.
- **Data contract (no fake data):** every card reads only
  `dashboards/status.json` and/or `dashboards/ceo-report.json` —
  the same files the check suite verifies. No card reads a store
  file directly. A missing source shows "unknown", never a guessed
  number. New keys in status.json (additive only):
  `founder_os` (phase F2, batch 1, source audit §14) and `roster`
  (69 entries + counts), published by `scripts/sync_status.py`,
  which also copies the latest CEO report JSON byte-for-byte to
  `dashboards/ceo-report.json` (a stale copy is removed when no
  report is available).
- **Approval server (actionable, not display-only):**
  `scripts/taskboard_server.py` (port 8766) gained
  `GET /api/approvals` and `POST /api/approvals/decide`, both
  straight through ApprovalCentre (list_pending / decide). The
  gateway's own errors (wrong gate word, expired, already
  decided, unknown id) surface unchanged as HTTP 400. CORS is
  allowed ONLY for the Command Center origin
  (http://localhost:8765). If the server is not running, the
  Approval Center shows display-only cards with the terminal CLI
  command instead. The task POST body parsing was factored into
  `_read_json_body()` (shared by both POST routes).
- **3D dashboard honesty fixes (`dashboards/dashboard-3d.html`):**
  the dated fallback snapshot is now labelled with a visible
  banner ("Last known snapshot, 2026-11-20 — status.json could not
  be read") whenever it is in use, and the detail-panel numbers
  (first mails, PA list, approvals pending, paying clients,
  email) are placeholders filled from the live status file — the
  hardcoded 162 / 39/100 / 374 literals are gone (the FALLBACK
  object keeps 162 as the dated snapshot value). A Command Center
  link was added to the sidebar. The static 3D dashboard stays
  until the Command Center is verified — nothing was deleted.
- **Checks:** `scripts/check_command_center.py` (per-module checks
  + no-fake-data test) and `tests/test_command_center.py`
  (server approvals flow on TEMP store paths). See the F2 batch 1
  completion report for totals.
- **PENDING (not done in batch 1):** batch 2 modules (Task Center,
  Reports Center, Financial Dashboard, System Health, Settings &
  Permissions) — need their own Founder ask. `store/leads.json`
  untouched. `voice/loop.py` untouched. Nothing pushed to GitHub.
  Nothing sends, publishes, spends, or deploys.
- Note: F1's M2 push DID complete 2026-11-26 18:41–18:47 (heads
  894c7065 + bf9d2eab); the F1 entry above still lists it as
  pending — that line is stale, the push is done.

## FOUNDER OS F2 batch 2 — Founder Command Center, second live modules (2026-11-27)

- Founder approved batch 2 ("F2 batch 2 shuru koro", 2026-11-27
  05:48 Dhaka). Batch 2 builds Command Center modules 10, 15, 17,
  18, 19 only — the other 9 modules stay greyed with their planned
  batch (batch 3 / F7 / F8). Nothing pushed to GitHub, no ZIP.
  10. Task Center — the live task queue: 1 task (done, booking-link
      verification, 2026-11-20). Live refresh from the taskboard API
      (GET /api/tasks) when the server runs, snapshot otherwise;
      queue-watch status (taskboard-queue-watch, paused, 10-minute
      interval, 0 runs) and the manual drain CLI.
  15. Reports Center — all 6 generated reports in reports/ceo/
      (daily/monthly/weekly JSON + MD, all 2026-11-24; latest weekly
      JSON, 2 days old — shown honestly). Performance and leads
      reports do not exist yet and are shown as "none".
  17. Financial Dashboard — the spend ledger (64 records, $0.00,
      all provider "mock"), per-provider cost view (all $0.00),
      pricing tiers (LOCKED 2026-11-12, internal display only),
      Gate 0 economics (kit $49 one-time, launch $39 for the first
      30 buyers, 0 sales, NOT PASSED; wedge 1 in 20 -> $1,109/mo
      receptionist, UNTESTED). Revenue $0.00 with 0 paying clients
      — shown, never invented.
  18. System Health — check-suite and pytest totals with run dates
      from dashboards/health-record.json (written by the
      verification run; "unknown" when no record exists): suite
      865/871 (6 pre-existing voice-environment failures), pytest
      249 passed / 2 skipped / 1 xfailed. Plus Python, disk, voice
      models (piper/sherpa-bn/vosk present, 371.2 MB voice dir),
      provider enablement (configured, never "connected" without a
      live probe), check-script and test-file counts, brain mode.
  19. Settings & Permissions — READ-ONLY view of the approval
      policy: gate words, 20-minute TTL, $0 cap, gated actions,
      production brain locked, free-only guard present, email
      PAUSED, and the full 33-row permission matrix. No edit
      controls of any kind.
- **Data contract (additive only):** five new status.json keys
  published by `scripts/sync_status.py` — `task_queue`,
  `reports`, `finance`, `health`, `policy`. New source file
  `00-CEO-Core/pricing.json` (the LOCKED 2026-11-12 tiers).
  `GET /api/tasks` now sends CORS for the Command Center origin
  only. The page still reads only status.json + ceo-report.json
  (plus the taskboard API when it runs); no card reads a store
  file directly. No hardcoded metric literal in the page — the
  no-fake-data test now also bans the pricing literals, 524, and
  the overage rates.
- **Checks:** `scripts/check_command_center.py` 48/48 PASS
  (per-module + batch-2 data-contract checks against the real
  sources + no-fake-data + the server flow on TEMP store);
  `tests/test_command_center.py` 19/19 passed. Full suite
  865/871 (6 failures, the same pre-existing voice-environment
  gaps as the batch 1 baseline — see the F2 batch 2 completion
  report for the baseline-arithmetic note); full pytest 249
  passed / 2 skipped / 1 xfailed, 0 failed. Live render verified
  by serving (HTTP 200s on 8765 + 8766, CORS, node --check
  clean). `store/leads.json` untouched. `voice/loop.py`
  untouched. Nothing sends, publishes, spends, or deploys.
- **PENDING (not done in batch 2):** batch 3 modules (2, 3, 4,
  12, 13, 14, 16) and F7/F8 (8, 9) — each needs its own Founder
  ask. Taskboard auto-start in run_local.bat and CEO report
  regeneration stay UNDECIDED from batch 1.
