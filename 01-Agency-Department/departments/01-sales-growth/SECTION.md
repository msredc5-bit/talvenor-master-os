# 01 — Sales & Growth Department

## উদ্দেশ্য (Purpose)

Talvenor-এর client hunting-এর পুরো sales পথ এক জায়গায় রাখা: prospect খোঁজা,
research করা, outreach draft করা, reply triage করা, negotiation-এর প্রস্তুতি,
objection practice, close-এর plan, follow-up draft, আর call schedule-এ সাহায্য।
এই department শুধু plan আর DRAFT বানায় — কিছু পাঠায় না, কিছু বিক্রি করে না।

## Manager

- **Chief Growth Agent** — `ChiefGrowthAgent`, task_kind `manage_sales_growth`, gate `ok`
- Manager file: `01-Agency-Department/departments/01-sales-growth/manager/chief_growth_agent.py`
- Skill file: `01-Agency-Department/departments/01-sales-growth/skills/chief-growth-agent.md`
- Manager delegation plan-এর DRAFT বানায় + Phase 3 specialist-দের load করে চালায় (DRAFT only); engine/section-এর পুরনো worker execute করে না।
- Agency Chief wiring **Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।

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

Note: ObjectionSimulator-এর file `marketing.py` — acquisition worker নয়, marketing
worker file-এ থাকে। FollowUpAgent-এর 100-mail rule: Pennsylvania-তে 37 first mail
হয়েছে, তাই follow-up **PARKED** — কোনো state-এ 100 first mail না হলে follow-up নয়।

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Lead Research Agent | EXISTING — ProspectResearcher | `prospect_research`, gate none |
| Google Maps Prospect Finder | EXISTING — GoogleMapsProspectFinder | `maps_prospect_find`, gate none — Phase 3, `departments/01-sales-growth/specialists/google_maps_prospect_finder.py` |
| Business Verification Agent | EXISTING — BusinessVerificationAgent | `business_verify`, gate none — Phase 3, `departments/01-sales-growth/specialists/business_verification_agent.py` |
| Lead Scoring Agent | EXISTING — LeadScoringAgent | `lead_score`, gate none — Phase 3, `departments/01-sales-growth/specialists/lead_scoring_agent.py` |
| Email Outreach Agent | EXISTING — OutreachDrafter | `outreach_draft`, gate send — DRAFT only, Boss পাঠান |
| Follow-up Agent | EXISTING — FollowUpAgent | `followup_draft`, gate send — 100-mail rule-এ PARKED |
| CRM Manager Agent | EXISTING — CRMManagerAgent | `crm_manage`, gate none — Phase 3, `departments/01-sales-growth/specialists/crm_manager_agent.py`; CRM (n8n Cloud Data Tables) planned, not live — plan DRAFT মাত্র |
| Sales Intelligence Agent | EXISTING — SalesIntelligenceAgent | `sales_intelligence`, gate none — Phase 3, `departments/01-sales-growth/specialists/sales_intelligence_agent.py` |

## Missing Roles

- এই department-এ কোনো GAP role নেই — brief-এর ৮টি role-ই EXISTING হিসেবে covered।
- Phase 3-এ ৫টি নতুন specialist বানানো হয়েছে (Google Maps Prospect Finder,
  Business Verification Agent, Lead Scoring Agent, CRM Manager Agent,
  Sales Intelligence Agent) — কোনো ROLE-ONLY role আর বাকি নেই।

## Honest Status

- **Paying clients: 0** — এখনো কোনো paying client নেই।
- **Email PAUSED since 2026-11-14** — SPF/DMARC fix না হওয়া পর্যন্ত কোনো email যায় না;
  first mails 162-এ থেমে আছে।
- **Follow-ups PARKED** — 100-mail rule; Pennsylvania 37 first mails।
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; সব output DRAFT।
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — এটাই DB, অন্য কোনো database নয়।
- **CRM: n8n Cloud Data Tables PLANNED, not live।**
- **$0 spend cap** — কিছু খরচ করা হয় না।
- **Agency Chief wiring Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই department-এর manager-কে call করে।
- **Pricing LOCKED, internal only** — prospect-কে কখনো দাম বলা হয় না।
- **No dental/medical ever** — dental/medical বা patient-health ব্যবসা target নয়।
- Brand **Talvenor only**। কোনো invented client, price, statistic, testimonial, guarantee নেই।
