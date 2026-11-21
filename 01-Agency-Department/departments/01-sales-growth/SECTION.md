# 01 — Sales & Growth Department

## Purpose

Talvenor's whole client-hunting sales path in one place: finding prospects,
doing research, drafting outreach, triaging replies, preparing negotiation,
objection practice, close plans, follow-up drafts, and help with call scheduling.
This department only makes plans and DRAFTs — it sends nothing, sells nothing.

## Manager

- **Chief Growth Agent** — `ChiefGrowthAgent`, task_kind `manage_sales_growth`, gate `ok`
- Manager file: `01-Agency-Department/departments/01-sales-growth/manager/chief_growth_agent.py`
- Skill file: `01-Agency-Department/departments/01-sales-growth/skills/chief-growth-agent.md`
- Manager makes a DRAFT of the delegation plan + loads and runs the Phase 3 specialists (DRAFT only); does not execute the engine/section's old workers.
- Agency Chief wiring **Phase 2 DONE** — the Chief now calls this manager via DEPARTMENT_ROUTING.

## Mapped Existing Staff (13)

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| ProspectResearcher | `prospect_research` | `01-Agency-Department/engine/workers/src/workers/acquisition.py` | none | EXISTING |
| OutreachDrafter | `outreach_draft` | `01-Agency-Department/engine/workers/src/workers/acquisition.py` | send | EXISTING |
| ReplyHandler | `reply_triage` | `01-Agency-Department/engine/workers/src/workers/acquisition.py` | send | EXISTING |
| NegotiationCoach | `negotiation_prep` | `01-Agency-Department/engine/workers/src/workers/acquisition.py` | ok | EXISTING |
| ObjectionSimulator | `objection_sim` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | ok | EXISTING |
| SalesCloser | `sales_close` | `01-Agency-Department/sections/sell/agents/sales_closer.py` | ok | EXISTING |
| FollowUpAgent | `followup_draft` | `01-Agency-Department/sections/sell/agents/followup_agent.py` | send | EXISTING |
| SchedulerAssistant | `schedule_help` | `01-Agency-Department/engine/workers/src/workers/admin.py` | none | EXISTING |
| GoogleMapsProspectFinder | `maps_prospect_find` | `01-Agency-Department/departments/01-sales-growth/specialists/google_maps_prospect_finder.py` | none | EXISTING (Phase 3) |
| BusinessVerificationAgent | `business_verify` | `01-Agency-Department/departments/01-sales-growth/specialists/business_verification_agent.py` | none | EXISTING (Phase 3) |
| LeadScoringAgent | `lead_score` | `01-Agency-Department/departments/01-sales-growth/specialists/lead_scoring_agent.py` | none | EXISTING (Phase 3) |
| CRMManagerAgent | `crm_manage` | `01-Agency-Department/departments/01-sales-growth/specialists/crm_manager_agent.py` | none | EXISTING (Phase 3) |
| SalesIntelligenceAgent | `sales_intelligence` | `01-Agency-Department/departments/01-sales-growth/specialists/sales_intelligence_agent.py` | none | EXISTING (Phase 3) |

Note: ObjectionSimulator's file is `marketing.py` — not an acquisition worker, it is in the marketing
worker file. FollowUpAgent's 100-mail rule: 37 first mails in Pennsylvania,
so follow-up is **PARKED** — no follow-up in any state until 100 first mails.

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Lead Research Agent | EXISTING — ProspectResearcher | `prospect_research`, gate none |
| Google Maps Prospect Finder | EXISTING — GoogleMapsProspectFinder | `maps_prospect_find`, gate none — Phase 3, `departments/01-sales-growth/specialists/google_maps_prospect_finder.py` |
| Business Verification Agent | EXISTING — BusinessVerificationAgent | `business_verify`, gate none — Phase 3, `departments/01-sales-growth/specialists/business_verification_agent.py` |
| Lead Scoring Agent | EXISTING — LeadScoringAgent | `lead_score`, gate none — Phase 3, `departments/01-sales-growth/specialists/lead_scoring_agent.py` |
| Email Outreach Agent | EXISTING — OutreachDrafter | `outreach_draft`, gate send — DRAFT only, Boss sends |
| Follow-up Agent | EXISTING — FollowUpAgent | `followup_draft`, gate send — PARKED under the 100-mail rule |
| CRM Manager Agent | EXISTING — CRMManagerAgent | `crm_manage`, gate none — Phase 3, `departments/01-sales-growth/specialists/crm_manager_agent.py`; CRM (n8n Cloud Data Tables) planned, not live — plan DRAFT only |
| Sales Intelligence Agent | EXISTING — SalesIntelligenceAgent | `sales_intelligence`, gate none — Phase 3, `departments/01-sales-growth/specialists/sales_intelligence_agent.py` |

## Missing Roles

- This department has no GAP role — all 8 roles in the brief are covered as EXISTING.
- In Phase 3, 5 new specialists were built (Google Maps Prospect Finder,
  Business Verification Agent, Lead Scoring Agent, CRM Manager Agent,
  Sales Intelligence Agent) — no ROLE-ONLY role is left.

## Honest Status

- **Paying clients: 0** — there is still no paying client.
- **Email PAUSED since 2026-11-14** — no email goes out until the SPF/DMARC fix;
  first mails are stuck at 162.
- **Follow-ups PARKED** — 100-mail rule; Pennsylvania 37 first mails.
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; all output is DRAFT.
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — this is the DB, no other database.
- **CRM: n8n Cloud Data Tables PLANNED, not live.**
- **$0 spend cap** — nothing is spent.
- **Agency Chief wiring Phase 2 DONE** — the Chief now calls this department's manager via DEPARTMENT_ROUTING.
- **Pricing LOCKED, internal only** — prices are never stated to a prospect.
- **No dental/medical ever** — dental/medical or patient-health businesses are not a target.
- Brand **Talvenor only**. No invented client, price, statistic, testimonial, or guarantee.
