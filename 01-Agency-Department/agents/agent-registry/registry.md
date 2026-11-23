# Agent Registry — Talvenor Master OS, Agentic Agency Office (Phase 1)

**Generated:** 2026-11-22 from `registry.json` by `scripts/generate_registry_md.py` — do not edit by hand; edit `registry.json` and re-run the generator.
**Status:** 69 entries, 69 EXISTING, 0 ROLE-ONLY, 0 GAP
**Repo:** `talvenor-master-os` | **Department:** `01-Agency-Department`
**Machine-readable copy:** `registry.json` (the source of truth; this file is its generated view)

---

## What Status means (in this registry)

| Status | Meaning |
|---|---|
| EXISTING | The real worker/agent file is in the repo. Path given. Runs on mock brain ($0); no claim of live work. |
| ROLE-ONLY | Only the role definition. Skill `.md` exists or will be written — no worker code, no claim of live work. |
| GAP | Not built, and there is no plan yet. Why — written in notes. |

## LOCKED truths (the basis of this registry)

- **Voice stack LIVE:** Vapi — Sophia, live receptionist, +1 (947) 223-0244, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3. Sophia is the production receptionist — she does no demo work.
- **Retell DROPPED 2026-10-26** — never production. `RetellBuilder` only makes a DRAFT plan; live stack is Vapi/Sophia. Ava was a demo agent — deleted from the new Vapi account; rebuild pending (Boss will bring a demo account).
- **DB = JSON store files** (`store/tasks.json`, `store/approvals.json`). CRM = n8n Cloud Data Tables — PLANNED, not live.
- **Calendar:** Google Calendar Appointment Schedule — booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time).
- **Brain = mock ($0);** live MetaSpark UNPROVEN.
- **Email PAUSED since 2026-11-14** (DNS fix pending). First mail 163. Paying client 0. Spend cap $0.
- **Gate words:** `ok` / `"post it"` / `send` / `go` / `"upload it"` — nothing is sent/published/spent/deleted without Boss's exact word.
- **Pricing LOCKED, internal only** — never quote it to a prospect. Dental/medical businesses are never a target — always DQ.
- **Brand Talvenor only.** No invented client, price, stat, testimonial, or guarantee.
- **Agency Chief wiring** (connecting 8 department managers to the Chief) **Phase 2 DONE** — done in this phase.
- **Phase 3 DONE 2026-11-19** — workers + skills built for 43 ROLE-ONLY specialists; all EXISTING (DRAFT only, mock brain). **2026-11-21** — workers + skills built for the remaining 4 GAP roles (Ad Campaign, CRM Integration, Expense Tracking, Backup & Recovery); now 47 specialists EXISTING, GAP 0.
- Existing Agency staff = **21** (15 workers + 6 section agents). This registry has 69 entries: 62 roles from the brief + 7 existing workers outside the brief.

## Numbers at a glance

| Department | Brief role | Extra existing worker | Total | EXISTING | ROLE-ONLY | GAP |
|---|---|---|---|---|---|---|
| 01 Sales & Growth | 8 | 5 | 13 | 13 | 0 | 0 |
| 02 Marketing | 8 | 1 | 9 | 9 | 0 | 0 |
| 03 AI Engineering | 10 | 0 | 10 | 10 | 0 | 0 |
| 04 Client Operations | 8 | 1 | 9 | 9 | 0 | 0 |
| 05 Research & Strategy | 7 | 0 | 7 | 7 | 0 | 0 |
| 06 Finance & Admin | 7 | 0 | 7 | 7 | 0 | 0 |
| 07 Quality & Security | 8 | 0 | 8 | 8 | 0 | 0 |
| 08 Product & Innovation | 6 | 0 | 6 | 6 | 0 | 0 |
| **Total** | **62** | **7** | **69** | **69** | **0** | **0** |

> QAEngineer is counted in two places (Dept 03 Testing & Debugging + Dept 07 Voice Quality Testing) — the same worker, shared. So EXISTING role-entries are 69, but separate workers are 68.

## Dept 01 — Sales & Growth (13)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 1.1 | Lead Research Agent | EXISTING | `ProspectResearcher` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`prospect_research`); skill `01-Agency-Department/engine/skills/prospect-researcher.md` | — (no gate) | Research notes; field not found means NOT_FOUND, never invented. |
| 1.2 | Google Maps Prospect Finder | EXISTING | `GoogleMapsProspectFinder` — `01-Agency-Department/departments/01-sales-growth/specialists/google_maps_prospect_finder.py` (`maps_prospect_find`); skill `01-Agency-Department/departments/01-sales-growth/skills/google-maps-prospect-finder.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 1.3 | Business Verification Agent | EXISTING | `BusinessVerificationAgent` — `01-Agency-Department/departments/01-sales-growth/specialists/business_verification_agent.py` (`business_verify`); skill `01-Agency-Department/departments/01-sales-growth/skills/business-verification-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 1.4 | Lead Scoring Agent | EXISTING | `LeadScoringAgent` — `01-Agency-Department/departments/01-sales-growth/specialists/lead_scoring_agent.py` (`lead_score`); skill `01-Agency-Department/departments/01-sales-growth/skills/lead-scoring-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 1.5 | Email Outreach Agent | EXISTING | `OutreachDrafter` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`outreach_draft`); skill `01-Agency-Department/engine/skills/outreach-drafter.md` | `send` | Drafts only, never sends. Email PAUSED since 2026-11-14. |
| 1.6 | Follow-up Agent | EXISTING | `FollowUpAgent` — `01-Agency-Department/sections/sell/agents/followup_agent.py` (`followup_draft`); skill `01-Agency-Department/sections/sell/skills/followup-agent.md` | `send` | PARKED by the 100-mail rule: PA has 39 first mails (2026-11-12 count), no state at 100 yet. |
| 1.7 | CRM Manager Agent | EXISTING | `CRMManagerAgent` — `01-Agency-Department/departments/01-sales-growth/specialists/crm_manager_agent.py` (`crm_manage`); skill `01-Agency-Department/departments/01-sales-growth/skills/crm-manager-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. CRM (n8n Cloud Data Tables) PLANNED, not live — worker drafts the CRM plan only. |
| 1.8 | Sales Intelligence Agent | EXISTING | `SalesIntelligenceAgent` — `01-Agency-Department/departments/01-sales-growth/specialists/sales_intelligence_agent.py` (`sales_intelligence`); skill `01-Agency-Department/departments/01-sales-growth/skills/sales-intelligence-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 1.9 | ReplyHandler | EXISTING | `ReplyHandler` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`reply_triage`); skill `01-Agency-Department/engine/skills/reply-triager.md` | `send` | Locked rules: decline means polite exit; interest means draft only, never price, booking link allowed. |
| 1.10 | NegotiationCoach | EXISTING | `NegotiationCoach` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`negotiation_prep`); skill `01-Agency-Department/engine/skills/negotiation-coach.md` | `ok` | Never quotes prices; pricing is internal only. |
| 1.11 | ObjectionSimulator | EXISTING | `ObjectionSimulator` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`objection_sim`); skill `01-Agency-Department/engine/skills/objection-simulator.md` | `ok` | Objection practice/sim draft. |
| 1.12 | SalesCloser | EXISTING | `SalesCloserAgent` — `01-Agency-Department/sections/sell/agents/sales_closer.py` (`sales_close`); skill `01-Agency-Department/sections/sell/skills/sales-closer.md` | `ok` | Close prep only; contracts/signing stay with Boss. |
| 1.13 | SchedulerAssistant | EXISTING | `SchedulerAssistant` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`schedule_help`); skill `01-Agency-Department/engine/skills/scheduler.md` | — (no gate) | Booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time). |

## Dept 02 — Marketing (9)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 2.1 | Market Positioning Agent | EXISTING | `MarketPositioningAgent` — `01-Agency-Department/departments/02-marketing/specialists/market_positioning_agent.py` (`market_position`); skill `01-Agency-Department/departments/02-marketing/skills/market-positioning-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 2.2 | Content Strategy Agent | EXISTING | `ContentPlanner` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`content_plan`); skill `01-Agency-Department/engine/skills/content-planner.md` | `ok` | Weekly content plan draft. |
| 2.3 | Social Media Agent | EXISTING | `SocialMediaAgent` — `01-Agency-Department/departments/02-marketing/specialists/social_media_agent.py` (`social_manage`); skill `01-Agency-Department/departments/02-marketing/skills/social-media-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Never posts — planning draft only. |
| 2.4 | Ad Campaign Agent | EXISTING | `AdCampaignAgent` — `01-Agency-Department/departments/02-marketing/specialists/ad_campaign_agent.py` (`ad_campaign`); skill `01-Agency-Department/departments/02-marketing/skills/ad-campaign-agent.md` | `ok` | Built 2026-11-21 — skill + worker EXISTING (DRAFT only, mock brain). Paid ad DRAFT plan + analysis only; live ads never run, $0 spend cap, no ad account connected. |
| 2.5 | Copywriting Agent | EXISTING | `CaptionWriter` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`caption_write`); skill `01-Agency-Department/engine/skills/caption-writer.md` | — (no gate) | Caption + hashtag + CTA pack draft; IG 5-8 / LinkedIn 3 / Facebook 0-2 hashtags. |
| 2.6 | Video Creative Agent | EXISTING | `VideoProducer` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`video_produce`); skill `01-Agency-Department/engine/skills/video-producer.md` | `ok` | Script + shot list draft; hook in first 2 seconds, REAL footage, 9:16. |
| 2.7 | SEO Agent | EXISTING | `SEOAgent` — `01-Agency-Department/departments/02-marketing/specialists/seo_agent.py` (`seo`); skill `01-Agency-Department/departments/02-marketing/skills/seo-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 2.8 | Analytics Agent | EXISTING | `AnalyticsAgent` — `01-Agency-Department/departments/02-marketing/specialists/analytics_agent.py` (`analytics`); skill `01-Agency-Department/departments/02-marketing/skills/analytics-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Visible metrics only. |
| 2.9 | PublishPrep | EXISTING | `PublishPrep` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`publish_prep`); skill `01-Agency-Department/engine/skills/publish-prep.md` | `post it` | Prep only, never posts; publishing is done by Boss himself from main chat. |

## Dept 03 — AI Engineering (10)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 3.1 | AI Solution Architect | EXISTING | `AISolutionArchitect` — `01-Agency-Department/departments/03-ai-engineering/specialists/ai_solution_architect.py` (`solution_architect`); skill `01-Agency-Department/departments/03-ai-engineering/skills/ai-solution-architect.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 3.2 | Voice Agent Builder | EXISTING | `RetellBuilder` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_build`); skill `01-Agency-Department/engine/skills/receptionist-builder.md` | `ok` | DRAFT plan ONLY. Live stack is Vapi/Sophia; Retell was dropped 2026-10-26 and is never production. |
| 3.3 | Conversation Designer | EXISTING | `ConversationDesigner` — `01-Agency-Department/departments/03-ai-engineering/specialists/conversation_designer.py` (`conversation_design`); skill `01-Agency-Department/departments/03-ai-engineering/skills/conversation-designer.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 3.4 | Prompt Engineering Agent | EXISTING | `PromptEngineeringAgent` — `01-Agency-Department/departments/03-ai-engineering/specialists/prompt_engineering_agent.py` (`prompt_engineering`); skill `01-Agency-Department/departments/03-ai-engineering/skills/prompt-engineering-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 3.5 | Vapi Integration Agent | EXISTING | `VapiIntegrationAgent` — `01-Agency-Department/departments/03-ai-engineering/specialists/vapi_integration_agent.py` (`vapi_integration`); skill `01-Agency-Department/departments/03-ai-engineering/skills/vapi-integration-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Brief's Retell name corrected to Vapi. |
| 3.6 | CRM Integration Agent | EXISTING | `CRMIntegrationAgent` — `01-Agency-Department/departments/03-ai-engineering/specialists/crm_integration_agent.py` (`crm_integration`); skill `01-Agency-Department/departments/03-ai-engineering/skills/crm-integration-agent.md` | `ok` | Built 2026-11-21 — skill + worker EXISTING (DRAFT only, mock brain). CRM integration DRAFT plan only; CRM (n8n Cloud Data Tables) PLANNED, not live — no live record, no sync. |
| 3.7 | Calendar Integration Agent | EXISTING | `CalendarIntegrationAgent` — `01-Agency-Department/departments/03-ai-engineering/specialists/calendar_integration_agent.py` (`calendar_integration`); skill `01-Agency-Department/departments/03-ai-engineering/skills/calendar-integration-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Booking link live. |
| 3.8 | n8n Automation Engineer | EXISTING | `N8nAutomationEngineer` — `01-Agency-Department/departments/03-ai-engineering/specialists/n8n_automation_engineer.py` (`n8n_automation`); skill `01-Agency-Department/departments/03-ai-engineering/skills/n8n-automation-engineer.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Workflows READY, not LIVE. |
| 3.9 | Testing & Debugging Agent | EXISTING | `QAEngineer` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_qa`); skill `01-Agency-Department/engine/skills/qa-engineer.md` | — (no gate) | Partial: QA checklist only. Shared with Dept 07 Voice Quality Testing. |
| 3.10 | Deployment Agent | EXISTING | `DeploymentAgent` — `01-Agency-Department/departments/03-ai-engineering/specialists/deployment_agent.py` (`deployment`); skill `01-Agency-Department/departments/03-ai-engineering/skills/deployment-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Deploy needs Boss's ok + manual step. |

## Dept 04 — Client Operations (9)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 4.1 | Client Onboarding Agent | EXISTING | `OnboardingAgent` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`onboarding_draft`); skill `01-Agency-Department/engine/skills/onboarding-agent.md` | `ok` | Onboarding pack draft; untested on a real client (0 paying clients). |
| 4.2 | Business Requirement Analyst | EXISTING | `ClientIntakeReceiverAgent` — `01-Agency-Department/sections/receive/agents/client_intake_receiver.py` (`client_intake`); skill `01-Agency-Department/sections/receive/skills/client-intake-receiver.md` | `send` | Intake: hours, services, FAQs, emergency routing, booking rules, escalation. |
| 4.3 | Client Configuration Agent | EXISTING | `ServiceDeliveryManagerAgent` — `01-Agency-Department/sections/delivery/agents/service_delivery_manager.py` (`delivery_manage`); skill `01-Agency-Department/sections/delivery/skills/service-delivery-manager.md` | `ok` | Manages delivery/configuration. |
| 4.4 | Call Monitoring Agent | EXISTING | `CallMonitoringAgent` — `01-Agency-Department/departments/04-client-operations/specialists/call_monitoring.py` (`call_monitoring`); skill `01-Agency-Department/departments/04-client-operations/skills/call_monitoring.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Not live call monitoring — checklist draft. |
| 4.5 | Client Reporting Agent | EXISTING | `ClientReportingAgent` — `01-Agency-Department/departments/04-client-operations/specialists/client_reporting.py` (`client_reporting`); skill `01-Agency-Department/departments/04-client-operations/skills/client_reporting.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 4.6 | Support Agent | EXISTING | `ClientSuccessAgent` — `01-Agency-Department/sections/delivery/agents/client_success_agent.py` (`client_success`); skill `01-Agency-Department/sections/delivery/skills/client-success-agent.md` | `send` | Support draft only; send gate required. |
| 4.7 | Retention Agent | EXISTING | `RetentionAgent` — `01-Agency-Department/departments/04-client-operations/specialists/retention.py` (`retention`); skill `01-Agency-Department/departments/04-client-operations/skills/retention.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Client 0 — no work yet. |
| 4.8 | Renewal & Upsell Agent | EXISTING | `RenewalUpsellAgent` — `01-Agency-Department/departments/04-client-operations/specialists/renewal_upsell.py` (`renewal_upsell`); skill `01-Agency-Department/departments/04-client-operations/skills/renewal_upsell.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Client 0 — no work yet. |
| 4.9 | InboxTriager | EXISTING | `InboxTriager` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`inbox_triage`); skill `01-Agency-Department/engine/skills/inbox-triager.md` | — (no gate) | Triages inbox; reads and sorts, never sends. |

## Dept 05 — Research & Strategy (7)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 5.1 | Competitor Research Agent | EXISTING | `CompetitorResearchAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/competitor_research_agent.py` (`competitor_research`); skill `01-Agency-Department/departments/05-research-strategy/skills/competitor-research-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 5.2 | Industry Research Agent | EXISTING | `IndustryResearchAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/industry_research_agent.py` (`industry_research`); skill `01-Agency-Department/departments/05-research-strategy/skills/industry-research-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 5.3 | Pricing Research Agent | EXISTING | `PricingResearchAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/pricing_research_agent.py` (`pricing_research`); skill `01-Agency-Department/departments/05-research-strategy/skills/pricing-research-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Internal only — never quote a prospect. |
| 5.4 | Niche Selection Agent | EXISTING | `NicheSelectionAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/niche_selection_agent.py` (`niche_selection`); skill `01-Agency-Department/departments/05-research-strategy/skills/niche-selection-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Dental/medical always DQ. |
| 5.5 | Offer Development Agent | EXISTING | `OfferDevelopmentAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/offer_development_agent.py` (`offer_development`); skill `01-Agency-Department/departments/05-research-strategy/skills/offer-development-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. No guarantees. |
| 5.6 | Market Opportunity Agent | EXISTING | `MarketOpportunityAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/market_opportunity_agent.py` (`market_opportunity`); skill `01-Agency-Department/departments/05-research-strategy/skills/market-opportunity-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 5.7 | Business Intelligence Agent | EXISTING | `BusinessIntelligenceAgent` — `01-Agency-Department/departments/05-research-strategy/specialists/business_intelligence_agent.py` (`business_intelligence`); skill `01-Agency-Department/departments/05-research-strategy/skills/business-intelligence-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |

## Dept 06 — Finance & Admin (7)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 6.1 | Revenue Tracking Agent | EXISTING | `RevenueTrackingAgent` — `01-Agency-Department/departments/06-finance-admin/specialists/revenue_tracking_agent.py` (`revenue_tracking`); skill `01-Agency-Department/departments/06-finance-admin/skills/revenue-tracking-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. Revenue $0. |
| 6.2 | Expense Tracking Agent | EXISTING | `ExpenseTrackingAgent` — `01-Agency-Department/departments/06-finance-admin/specialists/expense_tracking_agent.py` (`expense_tracking`); skill `01-Agency-Department/departments/06-finance-admin/skills/expense-tracking-agent.md` | — (no gate) | Built 2026-11-21 — skill + worker EXISTING (DRAFT only, mock brain). Expense entry DRAFT + monthly report only; ledger empty ($0 spent); never approves spend. |
| 6.3 | Invoice Management Agent | EXISTING | `BillingInvoiceAgent` — `01-Agency-Department/sections/ops/agents/billing_invoice_agent.py` (`billing_invoice`); skill `01-Agency-Department/sections/ops/skills/billing-invoice-agent.md` | `ok` | Invoice ONLY for a paying client on Boss's word; no invoice made yet. |
| 6.4 | Subscription Tracking Agent | EXISTING | `SubscriptionTrackingAgent` — `01-Agency-Department/departments/06-finance-admin/specialists/subscription_tracking_agent.py` (`subscription_tracking`); skill `01-Agency-Department/departments/06-finance-admin/skills/subscription-tracking-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 6.5 | Financial Reporting Agent | EXISTING | `ReportCompiler` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`report_compile`); skill `01-Agency-Department/engine/skills/report-compiler.md` | — (no gate) | Visible metrics only; never estimated or invented. |
| 6.6 | Document Management Agent | EXISTING | `DocumentManagementAgent` — `01-Agency-Department/departments/06-finance-admin/specialists/document_management_agent.py` (`document_management`); skill `01-Agency-Department/departments/06-finance-admin/skills/document-management-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 6.7 | Compliance Calendar Agent | EXISTING | `ComplianceCalendarAgent` — `01-Agency-Department/departments/06-finance-admin/specialists/compliance_calendar_agent.py` (`compliance_calendar`); skill `01-Agency-Department/departments/06-finance-admin/skills/compliance-calendar-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |

## Dept 07 — Quality & Security (8)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 7.1 | Voice Quality Testing Agent | EXISTING | `QAEngineer` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_qa`); skill `01-Agency-Department/engine/skills/qa-engineer.md` | — (no gate) | Partial: 12-check QA checklist only. Shared with Dept 03 Testing & Debugging. |
| 7.2 | Call Scenario Testing Agent | EXISTING | `CallScenarioTestingAgent` — `01-Agency-Department/departments/07-quality-security/specialists/call_scenario_testing_agent.py` (`call_scenario_testing`); skill `01-Agency-Department/departments/07-quality-security/skills/call-scenario-testing-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 7.3 | Workflow Testing Agent | EXISTING | `WorkflowTestingAgent` — `01-Agency-Department/departments/07-quality-security/specialists/workflow_testing_agent.py` (`workflow_testing`); skill `01-Agency-Department/departments/07-quality-security/skills/workflow-testing-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 7.4 | Data Validation Agent | EXISTING | `DataValidationAgent` — `01-Agency-Department/departments/07-quality-security/specialists/data_validation_agent.py` (`data_validation`); skill `01-Agency-Department/departments/07-quality-security/skills/data-validation-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 7.5 | Security Monitoring Agent | EXISTING | `SecurityMonitoringAgent` — `01-Agency-Department/departments/07-quality-security/specialists/security_monitoring_agent.py` (`security_monitoring`); skill `01-Agency-Department/departments/07-quality-security/skills/security-monitoring-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 7.6 | Access Control Agent | EXISTING | `AccessControlAgent` — `01-Agency-Department/departments/07-quality-security/specialists/access_control_agent.py` (`access_control`); skill `01-Agency-Department/departments/07-quality-security/skills/access-control-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 7.7 | Backup & Recovery Agent | EXISTING | `BackupRecoveryAgent` — `01-Agency-Department/departments/07-quality-security/specialists/backup_recovery_agent.py` (`backup_recovery`); skill `01-Agency-Department/departments/07-quality-security/skills/backup-recovery-agent.md` | `ok` | Built 2026-11-21 — skill + worker EXISTING (DRAFT only, mock brain). Backup DRAFT plan + DR runbook only; no backup system yet, restore test never run — NOT VERIFIED, it cannot be called protected. |
| 7.8 | Compliance Review Agent | EXISTING | `ComplianceReviewAgent` — `01-Agency-Department/departments/07-quality-security/specialists/compliance_review_agent.py` (`compliance_review`); skill `01-Agency-Department/departments/07-quality-security/skills/compliance-review-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |

## Dept 08 — Product & Innovation (6)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 8.1 | New AI Product Research Agent | EXISTING | `NewAIProductResearchAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/new_ai_product_research.py` (`new_ai_product_research`); skill `01-Agency-Department/departments/08-product-innovation/skills/new-ai-product-research-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 8.2 | New Feature Research Agent | EXISTING | `NewFeatureResearchAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/new_feature_research.py` (`new_feature_research`); skill `01-Agency-Department/departments/08-product-innovation/skills/new-feature-research-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 8.3 | Automation R&D Agent | EXISTING | `AutomationRDAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/automation_rd.py` (`automation_rd`); skill `01-Agency-Department/departments/08-product-innovation/skills/automation-rd-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 8.4 | Technology Evaluation Agent | EXISTING | `TechnologyEvaluationAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/technology_evaluation.py` (`technology_evaluation`); skill `01-Agency-Department/departments/08-product-innovation/skills/technology-evaluation-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 8.5 | Product Improvement Agent | EXISTING | `ProductImprovementAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/product_improvement.py` (`product_improvement`); skill `01-Agency-Department/departments/08-product-innovation/skills/product-improvement-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |
| 8.6 | Prototype Builder Agent | EXISTING | `PrototypeBuilderAgent` — `01-Agency-Department/departments/08-product-innovation/specialists/prototype_builder.py` (`prototype_builder`); skill `01-Agency-Department/departments/08-product-innovation/skills/prototype-builder-agent.md` | — (no gate) | Phase 3 DONE 2026-11-19; DRAFT only, mock brain. |

## Department Managers (8) — verified in Phase 1, outside this registry's 69 entries

> **Verified 2026-11-19:** the 8 managers' `.py` + skill files are on disk (paths below). Status **EXISTING** — but **Chief wiring Phase 2 DONE** — the Agency Chief now calls them via DEPARTMENT_ROUTING; managers are DRAFT-only. They have no entry in `registry.json` (69 = 62 brief roles + 7 extra existing workers; the 8 managers are a separate list).

| # | Manager | Department | Status (verified) | Notes |
|---|---|---|---|---|
| M1 | Chief Growth Agent | 01 Sales & Growth | EXISTING — `01-Agency-Department/departments/01-sales-growth/manager/chief_growth_agent.py` (`manage_sales_growth`, gate `ok`); skill `departments/01-sales-growth/skills/chief-growth-agent.md` | Chief wiring Phase 2 DONE. |
| M2 | Marketing Director Agent | 02 Marketing | EXISTING — `01-Agency-Department/departments/02-marketing/manager/marketing_director_agent.py` (`manage_marketing`, gate `ok`); skill `departments/02-marketing/skills/marketing-director-agent.md` | Chief wiring Phase 2 DONE. |
| M3 | CTO / AI Engineering Agent | 03 AI Engineering | EXISTING — `01-Agency-Department/departments/03-ai-engineering/manager/cto_ai_engineering_agent.py` (`manage_ai_engineering`, gate `ok`); skill `departments/03-ai-engineering/skills/cto-ai-engineering-agent.md` | Chief wiring Phase 2 DONE. |
| M4 | COO / Client Operations Agent | 04 Client Operations | EXISTING — `01-Agency-Department/departments/04-client-operations/manager/coo_client_operations_agent.py` (`manage_client_operations`, gate `ok`); skill `departments/04-client-operations/skills/coo-client-operations-agent.md` | Chief wiring Phase 2 DONE. |
| M5 | Chief Strategy Agent | 05 Research & Strategy | EXISTING — `01-Agency-Department/departments/05-research-strategy/manager/chief_strategy_agent.py` (`manage_research_strategy`, gate `ok`); skill `departments/05-research-strategy/skills/chief-strategy-agent.md` | Chief wiring Phase 2 DONE. |
| M6 | CFO / Finance Agent | 06 Finance & Admin | EXISTING — `01-Agency-Department/departments/06-finance-admin/manager/cfo_finance_agent.py` (`manage_finance_admin`, gate `ok`); skill `departments/06-finance-admin/skills/cfo-finance-agent.md` | Chief wiring Phase 2 DONE. |
| M7 | Chief Quality & Security Agent | 07 Quality & Security | EXISTING — `01-Agency-Department/departments/07-quality-security/manager/chief_quality_security_agent.py` (`manage_quality_security`, gate `ok`); skill `departments/07-quality-security/skills/chief-quality-security-agent.md` | Chief wiring Phase 2 DONE. |
| M8 | Chief Innovation Agent | 08 Product & Innovation | EXISTING — `01-Agency-Department/departments/08-product-innovation/manager/chief_innovation_agent.py` (`manage_product_innovation`, gate `ok`); skill `departments/08-product-innovation/skills/chief-innovation-agent.md` | Chief wiring Phase 2 DONE. |

## How to update

1. When you make a new worker file: set status EXISTING, give the repo-relative path + gate, and update `registry.json` the same way — then run `python3 scripts/generate_registry_md.py` to regenerate this file.
2. When ROLE-ONLY becomes EXISTING, also give the skill file's path.
3. When an entry's status changes, write the date + reason in notes.
4. Never claim live work until a real run is verified in Boss's signed-in session.
