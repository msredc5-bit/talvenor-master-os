# Agent Skill Audit — 2026-11-21 (Agency hierarchy)

> **Audit only — no skill was built, no skill file was changed.**
> Scope: Main CEO Bot → Agency Chief of Staff → 8 Department Managers →
> their specialist workers. Digital Product + Content departments are outside
> this audit (see the note below).
> Counted from the repo's real files — verified 2026-11-21.

## Total count

| Agent level | Number of agents | Has a skill | No skill |
|---|---|---|---|
| Main CEO Bot | 1 | 1 | 0 |
| Agency Chief of Staff | 1 | 1 | 0 |
| Department Manager | 8 | 8 | 0 |
| Specialist worker (EXISTING) | 65 | 65 | 0 |
| GAP role (no worker/skill) | 4 | 0 | 4 |
| **Total** | **79** | **75** | **4** |

Distinct skill files (in this audit's scope): **74** — 2 root +
51 department skills + 15 engine skills + 6 section skills.
(`qa-engineer.md` is shared by two roles, so 74 files, 75 assignments.)
No stub skills — every file is real content (even the smallest file is
over 10 lines).

---

## (A) Skills that already exist — with each agent's real path

### Main CEO Bot — 1 skill

- `skills/main-ceo-bot.md`

### Agency Chief of Staff — 1 skill

- `skills/chief-agency.md`

### Department Managers — 8 skills (1 each)

| Manager | Skill file |
|---|---|
| Sales — Chief Growth Agent | `01-Agency-Department/departments/01-sales-growth/skills/chief-growth-agent.md` |
| Marketing — Marketing Director | `01-Agency-Department/departments/02-marketing/skills/marketing-director-agent.md` |
| AI Engineering — CTO | `01-Agency-Department/departments/03-ai-engineering/skills/cto-ai-engineering-agent.md` |
| Client Operations — COO | `01-Agency-Department/departments/04-client-operations/skills/coo-client-operations-agent.md` |
| Research & Strategy — Chief Strategy | `01-Agency-Department/departments/05-research-strategy/skills/chief-strategy-agent.md` |
| Finance & Admin — CFO | `01-Agency-Department/departments/06-finance-admin/skills/cfo-finance-agent.md` |
| Quality & Security — Chief Quality | `01-Agency-Department/departments/07-quality-security/skills/chief-quality-security-agent.md` |
| Product Innovation — Chief Innovation | `01-Agency-Department/departments/08-product-innovation/skills/chief-innovation-agent.md` |

### Specialist workers — 65 people, everyone has a skill

#### 01 Sales Growth — 13/13

| Specialist | Skill file |
|---|---|
| ProspectResearcher | `01-Agency-Department/engine/skills/prospect-researcher.md` |
| OutreachDrafter | `01-Agency-Department/engine/skills/outreach-drafter.md` |
| ReplyHandler | `01-Agency-Department/engine/skills/reply-triager.md` (inside the file it says Worker: ReplyHandler) |
| NegotiationCoach | `01-Agency-Department/engine/skills/negotiation-coach.md` |
| ObjectionSimulator | `01-Agency-Department/engine/skills/objection-simulator.md` |
| SalesCloser | `01-Agency-Department/sections/sell/skills/sales-closer.md` |
| FollowUpAgent | `01-Agency-Department/sections/sell/skills/followup-agent.md` |
| SchedulerAssistant | `01-Agency-Department/engine/skills/scheduler.md` |
| Google Maps Prospect Finder | `01-Agency-Department/departments/01-sales-growth/skills/google-maps-prospect-finder.md` |
| Business Verification Agent | `01-Agency-Department/departments/01-sales-growth/skills/business-verification-agent.md` |
| Lead Scoring Agent | `01-Agency-Department/departments/01-sales-growth/skills/lead-scoring-agent.md` |
| CRM Manager Agent | `01-Agency-Department/departments/01-sales-growth/skills/crm-manager-agent.md` |
| Sales Intelligence Agent | `01-Agency-Department/departments/01-sales-growth/skills/sales-intelligence-agent.md` |

#### 02 Marketing — 8/8 (excluding 1 GAP)

| Specialist | Skill file |
|---|---|
| ContentPlanner | `01-Agency-Department/engine/skills/content-planner.md` |
| VideoProducer | `01-Agency-Department/engine/skills/video-producer.md` |
| CaptionWriter | `01-Agency-Department/engine/skills/caption-writer.md` |
| PublishPrep | `01-Agency-Department/engine/skills/publish-prep.md` |
| Market Positioning Agent | `01-Agency-Department/departments/02-marketing/skills/market-positioning-agent.md` |
| Social Media Agent | `01-Agency-Department/departments/02-marketing/skills/social-media-agent.md` |
| SEO Agent | `01-Agency-Department/departments/02-marketing/skills/seo-agent.md` |
| Analytics Agent | `01-Agency-Department/departments/02-marketing/skills/analytics-agent.md` |
| Ad Campaign Agent | **GAP — no skill** (see Part B) |

#### 03 AI Engineering — 9/9 (excluding 1 GAP)

| Specialist | Skill file |
|---|---|
| RetellBuilder | `01-Agency-Department/engine/skills/receptionist-builder.md` (inside: Worker: RetellBuilder; live stack written as Vapi/Sophia) |
| QAEngineer | `01-Agency-Department/engine/skills/qa-engineer.md` (also shared with the Quality department) |
| AI Solution Architect | `01-Agency-Department/departments/03-ai-engineering/skills/ai-solution-architect.md` |
| Conversation Designer | `01-Agency-Department/departments/03-ai-engineering/skills/conversation-designer.md` |
| Prompt Engineering Agent | `01-Agency-Department/departments/03-ai-engineering/skills/prompt-engineering-agent.md` |
| Vapi Integration Agent | `01-Agency-Department/departments/03-ai-engineering/skills/vapi-integration-agent.md` |
| Calendar Integration Agent | `01-Agency-Department/departments/03-ai-engineering/skills/calendar-integration-agent.md` |
| n8n Automation Engineer | `01-Agency-Department/departments/03-ai-engineering/skills/n8n-automation-engineer.md` |
| Deployment Agent | `01-Agency-Department/departments/03-ai-engineering/skills/deployment-agent.md` |
| CRM Integration Agent | **GAP — no skill** (see Part B) |

#### 04 Client Operations — 9/9

| Specialist | Skill file |
|---|---|
| ClientIntakeReceiver | `01-Agency-Department/sections/receive/skills/client-intake-receiver.md` |
| OnboardingAgent | `01-Agency-Department/engine/skills/onboarding-agent.md` |
| ServiceDeliveryManager | `01-Agency-Department/sections/delivery/skills/service-delivery-manager.md` |
| ClientSuccessAgent | `01-Agency-Department/sections/delivery/skills/client-success-agent.md` |
| InboxTriager | `01-Agency-Department/engine/skills/inbox-triager.md` |
| Call Monitoring Agent | `01-Agency-Department/departments/04-client-operations/skills/call_monitoring.md` |
| Client Reporting Agent | `01-Agency-Department/departments/04-client-operations/skills/client_reporting.md` |
| Retention Agent | `01-Agency-Department/departments/04-client-operations/skills/retention.md` |
| Renewal & Upsell Agent | `01-Agency-Department/departments/04-client-operations/skills/renewal_upsell.md` |

#### 05 Research & Strategy — 7/7

| Specialist | Skill file |
|---|---|
| Competitor Research Agent | `01-Agency-Department/departments/05-research-strategy/skills/competitor-research-agent.md` |
| Industry Research Agent | `01-Agency-Department/departments/05-research-strategy/skills/industry-research-agent.md` |
| Pricing Research Agent | `01-Agency-Department/departments/05-research-strategy/skills/pricing-research-agent.md` |
| Niche Selection Agent | `01-Agency-Department/departments/05-research-strategy/skills/niche-selection-agent.md` |
| Offer Development Agent | `01-Agency-Department/departments/05-research-strategy/skills/offer-development-agent.md` |
| Market Opportunity Agent | `01-Agency-Department/departments/05-research-strategy/skills/market-opportunity-agent.md` |
| Business Intelligence Agent | `01-Agency-Department/departments/05-research-strategy/skills/business-intelligence-agent.md` |

#### 06 Finance & Admin — 6/6 (excluding 1 GAP)

| Specialist | Skill file |
|---|---|
| BillingInvoiceAgent | `01-Agency-Department/sections/ops/skills/billing-invoice-agent.md` |
| ReportCompiler | `01-Agency-Department/engine/skills/report-compiler.md` |
| Revenue Tracking Agent | `01-Agency-Department/departments/06-finance-admin/skills/revenue-tracking-agent.md` |
| Subscription Tracking Agent | `01-Agency-Department/departments/06-finance-admin/skills/subscription-tracking-agent.md` |
| Document Management Agent | `01-Agency-Department/departments/06-finance-admin/skills/document-management-agent.md` |
| Compliance Calendar Agent | `01-Agency-Department/departments/06-finance-admin/skills/compliance-calendar-agent.md` |
| Expense Tracking Agent | **GAP — no skill** (see Part B) |

#### 07 Quality & Security — 7/7 (excluding 1 GAP)

| Specialist | Skill file |
|---|---|
| QAEngineer | `01-Agency-Department/engine/skills/qa-engineer.md` (also shared with AI Engineering) |
| Call Scenario Testing Agent | `01-Agency-Department/departments/07-quality-security/skills/call-scenario-testing-agent.md` |
| Workflow Testing Agent | `01-Agency-Department/departments/07-quality-security/skills/workflow-testing-agent.md` |
| Data Validation Agent | `01-Agency-Department/departments/07-quality-security/skills/data-validation-agent.md` |
| Security Monitoring Agent | `01-Agency-Department/departments/07-quality-security/skills/security-monitoring-agent.md` |
| Access Control Agent | `01-Agency-Department/departments/07-quality-security/skills/access-control-agent.md` |
| Compliance Review Agent | `01-Agency-Department/departments/07-quality-security/skills/compliance-review-agent.md` |
| Backup & Recovery Agent | **GAP — no skill** (see Part B) |

#### 08 Product Innovation — 6/6

| Specialist | Skill file |
|---|---|
| New AI Product Research Agent | `01-Agency-Department/departments/08-product-innovation/skills/new-ai-product-research-agent.md` |
| New Feature Research Agent | `01-Agency-Department/departments/08-product-innovation/skills/new-feature-research-agent.md` |
| Automation R&D Agent | `01-Agency-Department/departments/08-product-innovation/skills/automation-rd-agent.md` |
| Technology Evaluation Agent | `01-Agency-Department/departments/08-product-innovation/skills/technology-evaluation-agent.md` |
| Product Improvement Agent | `01-Agency-Department/departments/08-product-innovation/skills/product-improvement-agent.md` |
| Prototype Builder Agent | `01-Agency-Department/departments/08-product-innovation/skills/prototype-builder-agent.md` |

### Outside the scope (not audited, but skills exist)

- `skills/chief-content.md`, `skills/chief-products.md` — the Content +
  Digital Product Chiefs' skills.
- The `02-Digital-Product-Department/` + `03-Content-Creation-Department/`
  skills/ folders hold ~30 more skill files (113 `*/skills/*.md` files in
  the repo in total). These are outside the Agency hierarchy, so they were
  not counted in this audit.

---

## (B) Seem needed, but missing — list only (nothing was built)

| # | Which skill is missing | Which agent needs it | Why it seems needed |
|---|---|---|---|
| 1 | Ad Campaign Agent skill | Marketing — Ad Campaign Agent (GAP) | To run paid ads, this role needs a skill; ads are not in the plan now under the $0 cap, so it is only listed |
| 2 | CRM Integration Agent skill | AI Engineering — CRM Integration Agent (GAP) | n8n Data Tables CRM is planned, not live — when the CRM goes live, an integration skill will be needed |
| 3 | Expense Tracking Agent skill | Finance & Admin — Expense Tracking Agent (GAP) | Under the $0 cap there is no spend now; when spending starts, a tracking skill will be needed |
| 4 | Backup & Recovery Agent skill | Quality & Security — Backup & Recovery Agent (GAP) | The repo has no backup system; if there is a backup, a recovery skill will be needed |
| 5 | Drawer memory-box skill | All agents (CEO, Chief, 8 Managers, all workers) | The code for reading/writing boxes exists (`00-CEO-Core/owner_memory.py`), but there is no skill doc on how an agent uses its own box + the shared compartment |
| 6 | Tool-allowlist enforcement skill | Agency Chief of Staff | A DRAFT policy for per-agent tool assignment exists (`00-CEO-Core/agent-tool-assignments-DRAFT.md`), but there is no skill doc on how the allowlist is enforced at the gate |

**Nothing in Part (B) was built** — it will only be built when Boss says "add it".

---

## Update — 2026-11-21 (skill-finder FIRST + Part B's 6 skills have been built)

Boss's order (voice call ~10:13 Dhaka): first find the skill-finder and connect
it to the Main CEO Bot, then use that skill-finder to find everyone else's skills.
Online search FIRST, clone + reverse-engineer, adapt for Talvenor (not a copy).
All LOCAL ONLY — nothing pushed to GitHub.

### Skill-finder (connected to the CEO Bot)

- **Skill file:** `skills/skill-finder.md` — procedure (local first →
  skills.sh leaderboard → verify → shortlist → Boss confirm → adapt).
- **Code:** `00-CEO-Core/skill_finder.py` — local registry search
  (`find_skill_local`), DRAFT proposal (`propose_skill` →
  `store/skill-proposals.json`), quality gate, `doctor()`.
- **Wiring:** `00-CEO-Core/main_ceo_bot.py` — when the task type is `find_skill`,
  the router goes to `skill_finder` (not to a Chief); it is in the self-test.
  A Skill-finder section was added to `skills/main-ceo-bot.md`.
- **Source:** cubicyyy/auto-research-skills `skill-finder` (MIT,
  frontmatter) + vercel-labs/skills `find-skills` (MIT). The method is theirs;
  the mechanism (submodule + symlink + npx CLI) does not fit Talvenor, so it
  was dropped — no symlink on Windows; the adapted file is copied.
- Research notes: `~/workspace/skill-research-2026-11-21/REVERSE-ENGINEERING.md`.

### Part (B) — all 6 have been built (2026-11-21)

| # | Skill | File | Source + license | Worker code |
|---|---|---|---|---|
| 1 | Ad Campaign Agent | `01-Agency-Department/departments/02-marketing/skills/ad-campaign-agent.md` | adkit/ads-skills (MIT) + superamped/ai-marketing-skills (MIT) | ⚠️ GAP — skill exists, no worker `.py` |
| 2 | CRM Integration Agent | `01-Agency-Department/departments/03-ai-engineering/skills/crm-integration-agent.md` | anthropics/knowledge-work-plugins `crm-autopilot` (Apache-2.0) | ⚠️ GAP — skill exists, no worker `.py` |
| 3 | Expense Tracking Agent | `01-Agency-Department/departments/06-finance-admin/skills/expense-tracking-agent.md` | openclaw/skills `expense-tracker` (MIT) + AgentLedger pattern | ⚠️ GAP — skill exists, no worker `.py` |
| 4 | Backup & Recovery Agent | `01-Agency-Department/departments/07-quality-security/skills/backup-recovery-agent.md` | makash/godmode `backup` (MIT) | ⚠️ GAP — skill exists, no worker `.py` |
| 5 | Drawer memory-box | `skills/drawer-memory-box.md` | poorangryman/ai-agent-pro-kit `agent-memory` (MIT) | ✅ Code exists (`00-CEO-Core/owner_memory.py`) |
| 6 | Tool-allowlist enforcement | `skills/tool-allowlist.md` | frankxai/skills `tool-allowlist` (MIT) + braydos-h/BreachPilot (Apache-2.0) | ✅ Code exists (`tools.json`, `tool_calling.py`, gate) |

### New total count (after the 2026-11-21 update)

| | Before | Now |
|---|---|---|
| Skill assignment | 75 | **81** (75 + 6) |
| Distinct skill file | 74 | **80** (74 + 6) |
| + skill-finder (a CEO Bot sub-skill, outside Part B) | — | **81 files** in total |

### CEO / Chief / Manager review (using the find-skills method)

`skills/chief-agency.md` was read — the gate table, honest status, and
"unknown task type → admit the mistake and stop" are already there; the gate
taught by the online skills (verify before claiming, stop on unknown) is in it.
**No CEO/Chief/Manager skill was rewritten** — there was only one real gap:
the CEO Bot had no way to find skills; that is filled by the skill-finder.

### Update — 2026-11-21 (GAP worker code built)

The worker `.py` files for the 4 GAP roles have been built — the skill's "Worker code: missing (GAP)" flag is no longer a GAP:

| # | Role | Worker file | Status |
|---|---|---|---|
| 1 | Ad Campaign Agent | `01-Agency-Department/departments/02-marketing/specialists/ad_campaign_agent.py` | ✅ EXISTING |
| 2 | CRM Integration Agent | `01-Agency-Department/departments/03-ai-engineering/specialists/crm_integration_agent.py` | ✅ EXISTING |
| 3 | Expense Tracking Agent | `01-Agency-Department/departments/06-finance-admin/specialists/expense_tracking_agent.py` | ✅ EXISTING |
| 4 | Backup & Recovery Agent | `01-Agency-Department/departments/07-quality-security/specialists/backup_recovery_agent.py` | ✅ EXISTING |

Registry: 69 EXISTING / 0 GAP; specialists 43 → 47; `scripts/check_specialists.py` 41/41 PASS. All workers are DRAFT/mock only — no send/publish/spend/live API. Two skills' task_kind routing keys were matched (CRM: `crm_integrate` → `crm_integration`; Expense: `expense_track` → `expense_tracking`).
