# Sweep Audit — Agency Department (01-Agency-Department)

- **Date:** 2026-11-21 (Dhaka)
- **Scope:** `01-Agency-Department/` only — `engine/`, `sections/`, `departments/01-08/`, `agents/agent-registry/`, `chief_of_staff_agency.py`, `workflows/`, `sub_agents/`, `governance/`, `pipeline.md`
- **Method:** file inventory + registry cross-check (scripted: every `registry.json` entry verified on disk) + grep for `TODO`/`FIXME`/`GAP`/`ROLE-ONLY`/stubs + manager routing-table cross-check (scripted: every specialist `task_kind` vs its manager's `DEPARTMENT_TASKS` keys) + `python3 -m compileall` over all `.py`
- **Headline:** 69 registry roles — **65 EXISTING (all verified: worker `.py` + skill `.md` present on disk), 4 GAP** (Ad Campaign, CRM Integration, Expense Tracking, Backup & Recovery — handled by another agent, see note below). **Zero stub workers, zero `NotImplementedError`, zero `TODO`/`FIXME` in code.** All 83 `.py` files compile. All 8 department managers route every one of their specialists. All 5 section rosters are complete.

## GAP-roles note (NOT my work — another agent is handling)

The 4 GAP roles are **skill-ready, worker-missing** — this matches Boss's 2026-11-21 note (skill exists, no worker code):

| Role | Skill file (EXISTS on disk, 2026-11-21 04:18) | Worker `.py` |
|---|---|---|
| Ad Campaign Agent | `01-Agency-Department/departments/02-marketing/skills/ad-campaign-agent.md` (`task_kind: ad_campaign`, gate `ok`) | MISSING |
| CRM Integration Agent | `01-Agency-Department/departments/03-ai-engineering/skills/crm-integration-agent.md` (`task_kind: crm_integrate`, gate `ok`) | MISSING |
| Expense Tracking Agent | `01-Agency-Department/departments/06-finance-admin/skills/expense-tracking-agent.md` (`task_kind: expense_track`, gate none) | MISSING |
| Backup & Recovery Agent | `01-Agency-Department/departments/07-quality-security/skills/backup-recovery-agent.md` (`task_kind: backup_recovery`, gate `ok`) | MISSING |

**Registry staleness the GAP agent should fix when adding the workers** (flagged here, not done by me): `agents/agent-registry/registry.json` still has `skill_file: null` for all 4, and `agents/agent-registry/registry.md` (§2.4, §3.6, §6.2, §7.7) + the four department `SECTION.md` files + the four manager files still say "no worker/skill" / "no worker, no skill yet". The skill half of that sentence is now wrong. Files carrying the stale sentence:
- `departments/02-marketing/SECTION.md:43`, `departments/03-ai-engineering/SECTION.md:40`, `departments/06-finance-admin/SECTION.md:45`, `departments/07-quality-security/SECTION.md:48`
- `departments/02-marketing/manager/marketing_director_agent.py:69-71,275`, `departments/03-ai-engineering/manager/cto_ai_engineering_agent.py:70-72,302`, `departments/06-finance-admin/manager/cfo_finance_agent.py:47,82-84`, `departments/07-quality-security/manager/chief_quality_security_agent.py:37,85-87`
- Manager routing placeholders already exist with `status: "GAP"` (same lines above) — the GAP agent only needs to swap `file`/`class` + `status` to `EXISTING` when the worker lands.

---

# DOABLE WITHOUT LLM API

## 1. `workflows/*.md` still claim 13 roles are ROLE-ONLY — all 13 now have worker code (Phase 3, 2026-11-19)

These workflow docs predate Phase 3 and contradict the registry + the actual `.py` files. Fix: change each table row / step from ROLE-ONLY to EXISTING and point at the worker file. No code change, docs only.

**`workflows/lead-generation.md`** — 5 roles, lines 15–19 + line 63:
- Google Maps Prospect Finder → `departments/01-sales-growth/specialists/google_maps_prospect_finder.py` (`maps_prospect_find`)
- Business Verification Agent → `departments/01-sales-growth/specialists/business_verification_agent.py` (`business_verify`)
- Lead Scoring Agent → `departments/01-sales-growth/specialists/lead_scoring_agent.py` (`lead_score`; deterministic tier logic verified: STRONG ≥80 → Tier 1, 60–79 → Tier 2, MEDIUM caps Tier 2, WEAK → Tier 4)
- Niche Selection Agent → `departments/05-research-strategy/specialists/niche_selection_agent.py` (`niche_selection`)
- Competitor Research Agent → `departments/05-research-strategy/specialists/competitor_research_agent.py` (`competitor_research`)
- Line 63 sentence ("Google Maps Finder, Verification, Scoring have no worker code") is now false — rewrite to say the workers exist and output DRAFTs.

**`workflows/client-support.md`** — 3 roles, lines 17–19, 50, 52, 59:
- Client Reporting Agent → `departments/04-client-operations/specialists/client_reporting.py` (`client_reporting`)
- Retention Agent → `departments/04-client-operations/specialists/retention.py` (`retention`)
- Renewal & Upsell Agent → `departments/04-client-operations/specialists/renewal_upsell.py` (`renewal_upsell`)
- §Step 4 (lines 50–52) and the summary bullet (line 59) must be rewritten: the step now runs the worker for a DRAFT plan instead of "no worker".

**`workflows/receptionist-deployment.md`** — 5 roles, lines 15–20, 64, 66, 72:
- Vapi Integration Agent → `departments/03-ai-engineering/specialists/vapi_integration_agent.py` (`vapi_integration`)
- Conversation Designer → `departments/03-ai-engineering/specialists/conversation_designer.py` (`conversation_design`)
- Prompt Engineering Agent → `departments/03-ai-engineering/specialists/prompt_engineering_agent.py` (`prompt_engineering`)
- Deployment Agent → `departments/03-ai-engineering/specialists/deployment_agent.py` (`deployment`)
- Call Monitoring Agent → `departments/04-client-operations/specialists/call_monitoring.py` (`call_monitoring`)
- §Step 5 (lines 64–66) must be rewritten: monitoring worker exists but outputs a checklist DRAFT, never live monitoring (see BLOCKED §9).

## 2. Stale Retell/Ava naming in the delivery engine workers

**File:** `01-Agency-Department/engine/workers/src/workers/delivery.py`
- Line 10: `RetellBuilder.task_kind = "retell_build"` — every router, manager and doc uses `"receptionist_build"` (`chief_of_staff_agency.py:117` ROUTING key, `departments/03-ai-engineering/manager/cto_ai_engineering_agent.py:32,285`). Same mismatch line 30: `QAEngineer.task_kind = "retell_qa"` vs routing key `"receptionist_qa"` (`chief_of_staff_agency.py:118`, cto manager lines 38, 292, `departments/07-quality-security/manager/chief_quality_security_agent.py:39`).
- **Impact today:** none on routing — the Chief dispatches on the ROUTING dict key and only passes `worker_cls.task_kind` into `EngineTask.kind` (`chief_of_staff_agency.py:485`). But task logs (`store/tasks.json`) record kind `retell_build`/`retell_qa`, which no other file, doc, or lookup uses. Any future code matching on `Task.kind == "receptionist_build"` would silently miss these two workers.
- **Suggested fix:** rename the two class attributes to `"receptionist_build"` / `"receptionist_qa"`. Do NOT rename the classes themselves (`RetellBuilder`/`QAEngineer` are referenced by Chief ROUTING, both managers, STAFF.md, sub_agents/README.md) unless all references are updated in the same pass.
- Line 1 docstring: `"DEL division workers — Talvenor receptionist delivery (Ava's lineage)."` — Ava was deleted; live stack is Vapi/Sophia. Reword to drop "Ava's lineage".
- Line 33: `QAEngineer.default_payload = {"agent": "ava-apex-plumbing-demo"}` — default agent id names the deleted Ava demo. Change to the live Sophia demo id (or `"BOSS INPUT REQUIRED"` if no live demo id is on record). The class docstring (line 29) already says the right thing (Vapi/Sophia) — only the default payload is stale.

## 3. Empty directories in the marketing section

- `01-Agency-Department/sections/marketing/agents/` — empty
- `01-Agency-Department/sections/marketing/skills/` — empty

`sections/marketing/SECTION.md` is explicit that Phase 7 added no NEW marketing agent — the 4 staff (ContentPlanner, VideoProducer, CaptionWriter, PublishPrep) are MAPPED from `engine/workers/src/workers/marketing.py` + `engine/skills/`. So the empty dirs are not missing work, just confusing scaffolding. **Suggested fix:** either delete the two empty dirs, or add a one-line `README.md` in `sections/marketing/` stating staff are MAPPED from the engine (no section-local agents by design).

## 4. `engine/tools.json` covers only 8 generic tools — confirm intent, then either leave or extend

- `01-Agency-Department/engine/tools.json` registers 8 tools (`draft_email`, `research_notes`, `draft_caption`, `draft_script`, `status_read`, `send_email`, `publish_post`, `spend`) — all `status: "mock"`, the last 3 gated stubs that never execute. It is loaded by `engine/tool_calling.py` (shared core `00-CEO-Core/tool_calling.py`).
- The 43 Phase-3 specialists and the 6 Phase-7 section agents have **no tool entries** anywhere; they are reachable only via Chief/manager routing (`chief_of_staff_agency.py` ROUTING / SECTION_ROUTING / DEPARTMENT_ROUTING), not via the ToolRegistry/MCP path.
- **Suggested fix:** verify against Boss's 2026-11-21 tool decision (ONE central Tool Gateway + per-agent allowed-tool lists; workers get skill + gateway only, NO per-agent MCP servers). If that decision stands, this is **by design — no action**, just record the intent in `engine/README.md` so the next audit doesn't re-flag it. If the intent is that every worker should be callable as a tool, add one mock tool entry per `task_kind` (65 entries) with `status: "mock"` and the worker's gate — a mechanical edit, no LLM needed.

## 5. (Cosmetic, verified-not-a-gap) Empty `__init__.py` files

- `01-Agency-Department/engine/workers/src/workers/__init__.py` (0 bytes) and `engine/workers/src/live/__init__.py` (0 bytes) are normal empty package markers. No action.

---

# BLOCKED

Each item needs a live LLM API, Boss's account/action, or Boss's decision. Nothing in this section can be completed by code alone.

## B1. Live brain unproven — every worker output is a mock DRAFT
- **Reason:** live Muse Spark probe failed 2026-11-20 ~01:44 (tunnel 403, `api.meta.ai` unreachable from this VM; $0 spent, key validity still unproven). All 65 workers run on `engine/workers/src/mock/provider.py` (MockLLMProvider). The 7 live provider files (`engine/workers/src/live/*_provider.py` — Meta, OpenAI, Anthropic, Gemini, Kimi, Grok, OpenRouter) are complete code, never run against a real key.
- **Unblocks when:** Boss proves a live brain on his PC (OpenRouter key via Windows env var only, per the 2026-11-20 API-key rule) and says so. No further live retry from this VM without his new word.

## B2. Email sending PAUSED — OutreachDrafter / FollowUpAgent / ReplyHandler are draft-only
- **Reason:** Boss paused sending 2026-11-14; SPF lacks the Gmail include, DMARC missing, DKIM not aligned; bounce 6/186 ≈ 3.2%. The DNS fix is Boss's panel step (SPF `v=spf1 include:_spf.google.com include:zohomail.com ~all`, `_dmarc` TXT). Recheck 2026-11-16: fix still not applied.
- **Files affected:** `engine/workers/src/workers/acquisition.py` (OutreachDrafter, ReplyHandler), `sections/sell/agents/followup_agent.py`.

## B3. Follow-up work parked by the 100-mail rule
- **Reason:** Boss's standing rule (2026-11-10): no follow-up in a state until 100 first mails in that state are complete. No state is at 100 (PA 37; first mails 162 total). The 20 ready PA follow-up drafts stay parked. `FollowUpAgent` (`sections/sell/agents/followup_agent.py`) is built and correct — it just has no due work.
- **Unblocks when:** a state reaches 100 first mails, or Boss changes the rule. (Known tension: research names zero follow-ups as the top cause of zero replies — Boss's decision only.)

## B4. CRM not live — CRM Manager drafts plans only; CRM Integration is a GAP role
- **Reason:** n8n Cloud Data Tables (the planned CRM) is PLANNED, not live. `CRMManagerAgent` (`departments/01-sales-growth/specialists/crm_manager_agent.py`) can only draft the CRM plan. The `CRM Integration Agent` worker is a GAP role (other agent) and cannot integrate with a CRM that does not exist.
- **Unblocks when:** Boss sets up / approves the n8n CRM and the GAP worker lands.

## B5. Paid ads — Ad Campaign Agent is a GAP role under a $0 spend cap
- **Reason:** paid ads are blocked by the $0 spend cap; no budget, no ad account spend. Worker build is the GAP agent's job; any real campaign needs Boss funding + his explicit "ok".
- **File:** `departments/02-marketing/skills/ad-campaign-agent.md` (skill exists; worker missing).

## B6. Zero paying clients — delivery/ops workers untested on a real client
- **Reason:** paying clients 0. `OnboardingAgent`, `ServiceDeliveryManager`, `ClientSuccessAgent`, `ClientReportingAgent`, `RetentionAgent`, `RenewalUpsellAgent`, `BillingInvoiceAgent`, `QAEngineer` (12-check verdict) all produce DRAFTs/templates only; none has run on a real client. Invoice worker must only issue on Boss's word for a paying client at LOCKED pricing.
- **Files:** `engine/workers/src/workers/delivery.py`, `sections/delivery/agents/*.py`, `sections/ops/agents/billing_invoice_agent.py`, `departments/04-client-operations/specialists/{retention,renewal_upsell,client_reporting,call_monitoring}.py`.

## B7. Vapi live integration is plan-only
- **Reason:** `VapiIntegrationAgent` (`departments/03-ai-engineering/specialists/vapi_integration_agent.py`) and `RetellBuilder` (`engine/workers/src/workers/delivery.py`) output DRAFT plans; no worker touches the live Vapi account. Live build/deploy needs Boss's Vapi account + his "ok" + manual steps.
- **Related:** `DeploymentAgent` (`departments/03-ai-engineering/specialists/deployment_agent.py`) is a deployment-plan DRAFT by design.

## B8. n8n workflows READY, not LIVE
- **Reason:** `N8nAutomationEngineer` (`departments/03-ai-engineering/specialists/n8n_automation_engineer.py`) drafts workflow notes; no live n8n instance is wired. Needs Boss's n8n Cloud account + webhook/credential setup.

## B9. Live call monitoring does not exist
- **Reason:** `CallMonitoringAgent` (`departments/04-client-operations/specialists/call_monitoring.py`) outputs a monitoring checklist DRAFT; there are no live calls to monitor (0 clients, Vapi not wired to this system). Needs a live client + Vapi call data + Boss's decision on what monitoring means.

## B10. Live prospect discovery (Google Maps) needs an API key + Boss decision
- **Reason:** `GoogleMapsProspectFinder` (`departments/01-sales-growth/specialists/google_maps_prospect_finder.py`) drafts a discovery plan; it makes no live Maps/API call (no key, $0 cap). Live discovery needs a Google Maps/Places key and Boss's approval to spend/use it.

## B11. Backup & Recovery — GAP role; restore testing needs Boss's ok
- **Reason:** no backup system exists in the repo. Worker build is the GAP agent's job; a restore test (the skill's own gate) needs Boss's "ok" before it runs.

## B12. Expense Tracking — GAP role; nothing to track under the $0 cap
- **Reason:** $0 spend cap means there are no expenses to track. Worker build is the GAP agent's job; real tracking starts only if/when Boss approves spend.

---

# Verified OK (no action needed)

- **Registry:** 69 entries = 62 brief roles + 7 extra existing workers; 65 EXISTING / 0 ROLE-ONLY / 4 GAP. Every EXISTING entry's `worker_file` + `skill_file` exists on disk (scripted check). Registry totals table (`agents/agent-registry/registry.md` §Numbers at a glance) matches `registry.json` exactly (65/69; QAEngineer counted twice as shared Dept 03 + Dept 07, noted in the file).
- **Managers:** all 8 managers' `DEPARTMENT_TASKS` route every specialist `task_kind` in their department (scripted check, 0 missing). Dept 03 manager routes `n8n_automation`; all 4 GAP task_kinds have `status: "GAP"` placeholders in their managers.
- **Sections:** all 5 rosters complete — receive 4 staff (incl. ClientIntakeReceiver, NEW Phase 7), sell 6, delivery 5, marketing 4 MAPPED, ops 2 (incl. BillingInvoiceAgent, NEW Phase 7). No section is missing worker code for a rostered role.
- **Engine workers:** 15 classes in `engine/workers/src/workers/{acquisition,marketing,delivery,admin}.py` all extend `WorkerBase` with real `do_work()` implementations; 6 section agents in `sections/*/agents/*.py` all have real `run()` implementations (spot-checked: lead scoring has deterministic tier logic; retention/call-monitoring/etc. follow the same gated draft pattern).
- **Chief wiring:** `chief_of_staff_agency.py` ROUTING (15 engine workers) + SECTION_ROUTING (6 section agents) + DEPARTMENT_ROUTING (8 managers) all present and consistent with the registry gates.
- **No stubs:** zero `NotImplementedError`, zero empty/`pass`-only handlers in any `.py` under the department; zero `TODO`/`FIXME` markers in any `.py`/`.md` (excluding the 4 GAP skill files' own "Worker code: none (GAP)" notes).
- **Live providers:** 7 provider files in `engine/workers/src/live/` are complete implementations (env-only keys, raise on missing key/network error) — untested live, which is B1, not a code gap.
- **Governance / pipeline:** `governance/*.md`, `pipeline.md`, `engine/STAFF.md`, `engine/README.md`, `sub_agents/README.md` carry no GAP/ROLE-ONLY/TODO markers.
