# Agent Registry — Talvenor Master OS, Agentic Agency Office (Phase 1)

**তারিখ:** 2026-11-19 | **Status:** Phase 1 — registry + workflow docs (DRAFT, Boss-এর review-এর জন্য)
**Repo:** `talvenor-master-os` | **Department:** `01-Agency-Department`
**Machine-readable copy:** `registry.json` (এই ফাইলের সাথে একই তথ্য, 69টি entry)

## Status-এর মানে (এই registry-তে)

| Status | মানে |
|---|---|
| EXISTING | আসল worker/agent ফাইল repo-তে আছে। Path দেওয়া আছে। Mock brain ($0) দিয়ে চলে; live কাজের দাবি নয়। |
| ROLE-ONLY | শুধু role-এর সংজ্ঞা। Skill `.md` আছে বা লেখা হবে — কোনো worker code নেই, live কাজের দাবি নেই। |
| GAP | বানানো হয়নি, এখন plan-ও নেই। কেন — notes-এ লেখা আছে। |

## LOCKED সত্য (এই registry-র ভিত্তি)

- **Voice stack LIVE:** Vapi — Sophia, live receptionist, +1 (947) 223-0244, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3। Sophia production receptionist — demo-র কাজ করে না।
- **Retell DROPPED 2026-10-26** — কখনো production নয়। `RetellBuilder` শুধু DRAFT plan বানায়; live stack Vapi/Sophia। Ava ছিল demo agent — নতুন Vapi account থেকে delete করা হয়েছে; rebuild pending (Boss demo account আনবেন)।
- **DB = JSON store files** (`store/tasks.json`, `store/approvals.json`)। CRM = n8n Cloud Data Tables — PLANNED, live নয়।
- **Calendar:** Google Calendar Appointment Schedule — booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)।
- **Brain = mock ($0);** live MetaSpark UNPROVEN।
- **Email PAUSED 2026-11-14 থেকে** (DNS fix pending)। প্রথম মেইল 162। Paying client 0। Spend cap $0।
- **Gate words:** `ok` / `"post it"` / `send` / `go` / `"upload it"` — Boss-এর exact word ছাড়া send/publish/spend/delete কিছু হয় না।
- **Pricing LOCKED, internal only** — prospect-কে কখনো quote করা যাবে না। Dental/medical ব্যবসা কখনো target নয় — সবসময় DQ।
- **Brand Talvenor only।** কোনো invented client, price, stat, testimonial, guarantee নেই।
- **Agency Chief wiring** (8 department manager-এর Chief-এর সাথে সংযোগ) **Phase 2 DONE** — এই phase-এ করা হয়েছে।
- বিদ্যমান Agency staff = **21** (15 worker + 6 section agent)। এই registry-তে 69টি entry: brief-এর 62টি role + brief-এর বাইরে থাকা 7টি existing worker।

## সংখ্যা এক নজরে

| Department | Brief role | Extra existing worker | মোট | EXISTING | ROLE-ONLY | GAP |
|---|---|---|---|---|---|---|
| 01 Sales & Growth | 8 | 5 | 13 | 8 | 5 | 0 |
| 02 Marketing | 8 | 1 | 9 | 4 | 4 | 1 |
| 03 AI Engineering | 10 | 0 | 10 | 2 | 7 | 1 |
| 04 Client Operations | 8 | 1 | 9 | 5 | 4 | 0 |
| 05 Research & Strategy | 7 | 0 | 7 | 0 | 7 | 0 |
| 06 Finance & Admin | 7 | 0 | 7 | 2 | 4 | 1 |
| 07 Quality & Security | 8 | 0 | 8 | 1 | 6 | 1 |
| 08 Product & Innovation | 6 | 0 | 6 | 0 | 6 | 0 |
| **মোট** | **62** | **7** | **69** | **22** | **43** | **4** |

> QAEngineer দুই জায়গায় গোনা হয়েছে (Dept 03 Testing & Debugging + Dept 07 Voice Quality Testing) — একই worker, shared। তাই EXISTING role-entry 22, কিন্তু আলাদা worker 21।

---

## Dept 01 — Sales & Growth (13)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 1.1 | Lead Research Agent | EXISTING | `ProspectResearcher` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`prospect_research`); skill `01-Agency-Department/engine/skills/prospect-researcher.md` | — (no gate) | Research notes বানায়; field না পেলে NOT_FOUND — বানানো হয় না। |
| 1.2 | Google Maps Prospect Finder | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Discovery-র কাজ আজ ProspectResearcher + Apify/Places দিয়ে হাতে হয়। |
| 1.3 | Business Verification Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Website/phone/service area যাচাই — SOP 11-signal scoring-এর কাজ, এখনো worker-এ বাঁধা হয়নি। |
| 1.4 | Lead Scoring Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | STRONG/MEDIUM/WEAK → Tier 1/2/4 scoring — এখনো worker-এ বাঁধা হয়নি। |
| 1.5 | Email Outreach Agent | EXISTING | `OutreachDrafter` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`outreach_draft`); skill `01-Agency-Department/engine/skills/outreach-drafter.md` | `send` | DRAFT লেখে মাত্র — কখনো পাঠায় না। Email PAUSED থাকতে এটাই শেষ কথা। |
| 1.6 | Follow-up Agent | EXISTING | `FollowUpAgent` — `01-Agency-Department/sections/sell/agents/followup_agent.py` (`followup_draft`); skill `01-Agency-Department/sections/sell/skills/followup-agent.md` | `send` | **100-mail rule: PARKED।** PA-তে প্রথম মেইল 37 — 100 না হওয়া পর্যন্ত কোনো state-এ follow-up নয়। |
| 1.7 | CRM Manager Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | CRM (n8n Cloud Data Tables) PLANNED, live নয় — CRM ছাড়া CRM manager-এর worker হয় না। |
| 1.8 | Sales Intelligence Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Reply/lead signal থেকে insight — এখনো worker-এ বাঁধা হয়নি। |
| 1.9 | ReplyHandler *(brief-এর বাইরে, existing)* | EXISTING | `ReplyHandler` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`reply_triage`); skill `01-Agency-Department/engine/skills/reply-triager.md` | `send` | Reply triage। Locked rule: decline = polite exit; interest = draft only, কখনো price নয়, booking link দেওয়া যায়। |
| 1.10 | NegotiationCoach *(brief-এর বাইরে, existing)* | EXISTING | `NegotiationCoach` — `01-Agency-Department/engine/workers/src/workers/acquisition.py` (`negotiation_prep`); skill `01-Agency-Department/engine/skills/negotiation-coach.md` | `ok` | Negotiation prep draft। Price quote করে না — pricing internal only। |
| 1.11 | ObjectionSimulator *(brief-এর বাইরে, existing)* | EXISTING | `ObjectionSimulator` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`objection_sim`); skill `01-Agency-Department/engine/skills/objection-simulator.md` | `ok` | Objection practice/sim draft। |
| 1.12 | SalesCloser *(brief-এর বাইরে, existing)* | EXISTING | `SalesCloser` — `01-Agency-Department/sections/sell/agents/sales_closer.py` (`sales_close`); skill `01-Agency-Department/sections/sell/skills/sales-closer.md` | `ok` | Close prep। Contract/sign — Boss ছাড়া হয় না। |
| 1.13 | SchedulerAssistant *(brief-এর বাইরে, existing)* | EXISTING | `SchedulerAssistant` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`schedule_help`); skill `01-Agency-Department/engine/skills/scheduler.md` | — (no gate) | Booking link + সময় নিয়ে সাহায্য। Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 |

## Dept 02 — Marketing (9)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 2.1 | Market Positioning Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Positioning/messaging — এখনো worker-এ বাঁধা হয়নি। |
| 2.2 | Content Strategy Agent | EXISTING | `ContentPlanner` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`content_plan`); skill `01-Agency-Department/engine/skills/content-planner.md` | `ok` | Weekly content plan draft। |
| 2.3 | Social Media Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Posting করে না। Prep-এর কাজ `PublishPrep` করে (2.9 দেখুন) — prep only, কখনো post নয়। |
| 2.4 | Ad Campaign Agent | GAP | — | — | **Paid ads — $0 spend cap।** Paid ad-এর plan নেই, worker নেই, budget নেই। |
| 2.5 | Copywriting Agent | EXISTING | `CaptionWriter` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`caption_write`); skill `01-Agency-Department/engine/skills/caption-writer.md` | — (no gate) | Caption + hashtag + CTA pack draft। IG 5–8 / LinkedIn 3 / Facebook 0–2 hashtag। |
| 2.6 | Video Creative Agent | EXISTING | `VideoProducer` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`video_produce`); skill `01-Agency-Department/engine/skills/video-producer.md` | `ok` | Script + shot list draft। Hook প্রথম 2 সেকেন্ডে, REAL footage, 9:16। |
| 2.7 | SEO Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | SEO কাজ এখনো worker-এ বাঁধা হয়নি। |
| 2.8 | Analytics Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Weekly reporting-এর কাজ `ReportCompiler` করে (Dept 06, 6.5 দেখুন) — visible metrics only, কখনো estimate নয়। |
| 2.9 | PublishPrep *(brief-এর বাইরে, existing)* | EXISTING | `PublishPrep` — `01-Agency-Department/engine/workers/src/workers/marketing.py` (`publish_prep`); skill `01-Agency-Department/engine/skills/publish-prep.md` | `"post it"` | Publish-এর prep মাত্র — post করে না। Publish শুধু main chat থেকে Boss নিজে করেন। |

## Dept 03 — AI Engineering (10)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 3.1 | AI Solution Architect | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Solution design — এখনো worker-এ বাঁধা হয়নি। |
| 3.2 | Voice Agent Builder | EXISTING | `RetellBuilder` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_build`); skill `01-Agency-Department/engine/skills/receptionist-builder.md` | `ok` | **DRAFT plan ONLY।** নামে Retell থাকলেও live stack Vapi/Sophia — Retell production নয়, DROPPED 2026-10-26। |
| 3.3 | Conversation Designer | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Call flow / conversation design — এখনো worker-এ বাঁধা হয়নি। |
| 3.4 | Prompt Engineering Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Prompt লেখা/টিউন — এখনো worker-এ বাঁধা হয়নি। |
| 3.5 | Vapi Integration Agent *(brief-এর ভুল নাম CORRECTED)* | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | নাম ঠিক করা হয়েছে: brief-এ Retell-এর নামে লেখা ছিল; live stack Vapi, তাই Vapi Integration। Vapi assistant/Sophia-র সাথে সংযোগের কাজ — এখনো worker নেই। |
| 3.6 | CRM Integration Agent | GAP | — | — | **CRM live নয়** (n8n Cloud Data Tables PLANNED) — সংযোগ করার মতো CRM-ই নেই। |
| 3.7 | Calendar Integration Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Booking link live (Google Calendar Appointment Schedule) — কিন্তু কোনো worker code নেই; link হাতে দেওয়া হয়। |
| 3.8 | n8n Automation Engineer | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | n8n workflows READY, LIVE নয় — Boss-এর import + test বাকি। |
| 3.9 | Testing & Debugging Agent | EXISTING | `QAEngineer` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_qa`); skill `01-Agency-Department/engine/skills/qa-engineer.md` | — (no gate) | **Partial — QA checklist মাত্র।** Dept 07-এর সাথে shared (7.1 দেখুন)। |
| 3.10 | Deployment Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Deployment-এ Boss-এর `ok` + manual step লাগে; কোনো worker নেই। |

## Dept 04 — Client Operations (9)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 4.1 | Client Onboarding Agent | EXISTING | `OnboardingAgent` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`onboarding_draft`); skill `01-Agency-Department/engine/skills/onboarding-agent.md` | `ok` | Onboarding pack draft। এখনো কোনো real client-এ test হয়নি (paying client 0)। |
| 4.2 | Business Requirement Analyst | EXISTING | `ClientIntakeReceiver` — `01-Agency-Department/sections/receive/agents/client_intake_receiver.py` (`client_intake`); skill `01-Agency-Department/sections/receive/skills/client-intake-receiver.md` | `send` | Intake নেয়: hours, services, FAQs, emergency routing, booking rules, escalation। |
| 4.3 | Client Configuration Agent | EXISTING | `ServiceDeliveryManager` — `01-Agency-Department/sections/delivery/agents/service_delivery_manager.py` (`delivery_manage`); skill `01-Agency-Department/sections/delivery/skills/service-delivery-manager.md` | `ok` | Delivery/configuration manage করে। |
| 4.4 | Call Monitoring Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | **Live monitoring worker এখনো নেই।** Sophia-র call দেখার কোনো automated worker নেই। |
| 4.5 | Client Reporting Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Client-কে report — এখনো worker-এ বাঁধা হয়নি। |
| 4.6 | Support Agent | EXISTING | `ClientSuccessAgent` — `01-Agency-Department/sections/delivery/agents/client_success_agent.py` (`client_success`); skill `01-Agency-Department/sections/delivery/skills/client-success-agent.md` | `send` | Support draft। DRAFT only — send gate ছাড়া পাঠায় না। |
| 4.7 | Retention Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Client 0 — retention-এর worker এখনো দরকার হয়নি। |
| 4.8 | Renewal & Upsell Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Client 0 — renewal/upsell-এর worker এখনো দরকার হয়নি। |
| 4.9 | InboxTriager *(brief-এর বাইরে, existing)* | EXISTING | `InboxTriager` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`inbox_triage`); skill `01-Agency-Department/engine/skills/inbox-triager.md` | — (no gate) | Inbox triage — পড়ে, সাজায়, পাঠায় না। |

## Dept 05 — Research & Strategy (7, সব ROLE-ONLY)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 5.1 | Competitor Research Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Competitor research — এখনো worker-এ বাঁধা হয়নি। |
| 5.2 | Industry Research Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Industry research — এখনো worker-এ বাঁধা হয়নি। |
| 5.3 | Pricing Research Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Pricing research internal only — prospect-কে কখনো quote নয়। |
| 5.4 | Niche Selection Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Niche বাছাই — এখনো worker-এ বাঁধা হয়নি। Dental/medical ব্যবসা কখনো target নয় — সবসময় DQ। |
| 5.5 | Offer Development Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Offer বানানো — এখনো worker-এ বাঁধা হয়নি। কোনো guarantee নয়। |
| 5.6 | Market Opportunity Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Opportunity খোঁজা — এখনো worker-এ বাঁধা হয়নি। |
| 5.7 | Business Intelligence Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | BI — এখনো worker-এ বাঁধা হয়নি। |

## Dept 06 — Finance & Admin (7)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 6.1 | Revenue Tracking Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Revenue $0 (paying client 0) — track করার মতো revenue নেই। |
| 6.2 | Expense Tracking Agent | GAP | — | — | **$0 spend cap — track করার মতো expense নেই।** কোনো খরচের অনুমোদন নেই। |
| 6.3 | Invoice Management Agent | EXISTING | `BillingInvoiceAgent` — `01-Agency-Department/sections/ops/agents/billing_invoice_agent.py` (`billing_invoice`); skill `01-Agency-Department/sections/ops/skills/billing-invoice-agent.md` | `ok` | **Invoice ONLY for a paying client, Boss-এর কথায়।** Client 0 — এখনো কোনো invoice বানানো হয়নি। |
| 6.4 | Subscription Tracking Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Subscription track — এখনো worker-এ বাঁধা হয়নি। |
| 6.5 | Financial Reporting Agent | EXISTING | `ReportCompiler` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`report_compile`); skill `01-Agency-Department/engine/skills/report-compiler.md` | — (no gate) | **Visible metrics only** — যা দেখা যায় তাই; কখনো estimate/invent নয়। |
| 6.6 | Document Management Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Document manage — এখনো worker-এ বাঁধা হয়নি। |
| 6.7 | Compliance Calendar Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Compliance dates — এখনো worker-এ বাঁধা হয়নি। |

## Dept 07 — Quality & Security (8)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 7.1 | Voice Quality Testing Agent | EXISTING | `QAEngineer` — `01-Agency-Department/engine/workers/src/workers/delivery.py` (`receptionist_qa`); skill `01-Agency-Department/engine/skills/qa-engineer.md` | — (no gate) | **Partial — QA checklist মাত্র (12-check)।** Dept 03-এর সাথে shared (3.9 দেখুন)। |
| 7.2 | Call Scenario Testing Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Call scenario test — এখনো worker-এ বাঁধা হয়নি। |
| 7.3 | Workflow Testing Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Workflow test — এখনো worker-এ বাঁধা হয়নি। |
| 7.4 | Data Validation Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Data validation — এখনো worker-এ বাঁধা হয়নি। |
| 7.5 | Security Monitoring Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Security monitoring — এখনো worker-এ বাঁধা হয়নি। |
| 7.6 | Access Control Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Access control — এখনো worker-এ বাঁধা হয়নি। |
| 7.7 | Backup & Recovery Agent | GAP | — | — | **Repo-তে কোনো backup system নেই।** Backup/recovery-র কিছু বানানো হয়নি। |
| 7.8 | Compliance Review Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Compliance review — এখনো worker-এ বাঁধা হয়নি। |

## Dept 08 — Product & Innovation (6, সব ROLE-ONLY)

| # | Role | Status | Worker / Skill | Gate | Notes |
|---|---|---|---|---|---|
| 8.1 | New AI Product Research Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | নতুন AI product research — এখনো worker-এ বাঁধা হয়নি। |
| 8.2 | New Feature Research Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | নতুন feature research — এখনো worker-এ বাঁধা হয়নি। |
| 8.3 | Automation R&D Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Automation R&D — এখনো worker-এ বাঁধা হয়নি। |
| 8.4 | Technology Evaluation Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Tech evaluation — এখনো worker-এ বাঁধা হয়নি। |
| 8.5 | Product Improvement Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Product improvement — এখনো worker-এ বাঁধা হয়নি। |
| 8.6 | Prototype Builder Agent | ROLE-ONLY | worker নেই; skill এখনো লেখা হয়নি | — | Prototype build — এখনো worker-এ বাঁধা হয়নি। |

---

## Department Managers (8) — Phase 1-এ যাচাইকৃত, এই registry-র 69 entry-র বাইরে

> **যাচাই 2026-11-19:** 8 manager-এর `.py` + skill ফাইল disk-এ আছে (নিচে path দেওয়া)। Status **EXISTING** — কিন্তু **Chief wiring Phase 2 DONE** — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এদের ডাকে; manager-রা DRAFT-only। `registry.json`-এ এদের entry নেই (69 = 62 brief role + 7 extra existing worker; manager 8 জন আলাদা তালিকা)।

| # | Manager | Department | Status (যাচাইকৃত) | Notes |
|---|---|---|---|---|
| M1 | Chief Growth Agent | 01 Sales & Growth | EXISTING — `01-Agency-Department/departments/01-sales-growth/manager/chief_growth_agent.py` (`manage_sales_growth`, gate `ok`); skill `departments/01-sales-growth/skills/chief-growth-agent.md` | Chief wiring Phase 2 DONE। |
| M2 | Marketing Director Agent | 02 Marketing | EXISTING — `01-Agency-Department/departments/02-marketing/manager/marketing_director_agent.py` (`manage_marketing`, gate `ok`); skill `departments/02-marketing/skills/marketing-director-agent.md` | Chief wiring Phase 2 DONE। |
| M3 | CTO / AI Engineering Agent | 03 AI Engineering | EXISTING — `01-Agency-Department/departments/03-ai-engineering/manager/cto_ai_engineering_agent.py` (`manage_ai_engineering`, gate `ok`); skill `departments/03-ai-engineering/skills/cto-ai-engineering-agent.md` | Chief wiring Phase 2 DONE। |
| M4 | COO / Client Operations Agent | 04 Client Operations | EXISTING — `01-Agency-Department/departments/04-client-operations/manager/coo_client_operations_agent.py` (`manage_client_operations`, gate `ok`); skill `departments/04-client-operations/skills/coo-client-operations-agent.md` | Chief wiring Phase 2 DONE। |
| M5 | Chief Strategy Agent | 05 Research & Strategy | EXISTING — `01-Agency-Department/departments/05-research-strategy/manager/chief_strategy_agent.py` (`manage_research_strategy`, gate `ok`); skill `departments/05-research-strategy/skills/chief-strategy-agent.md` | Chief wiring Phase 2 DONE। |
| M6 | CFO / Finance Agent | 06 Finance & Admin | EXISTING — `01-Agency-Department/departments/06-finance-admin/manager/cfo_finance_agent.py` (`manage_finance_admin`, gate `ok`); skill `departments/06-finance-admin/skills/cfo-finance-agent.md` | Chief wiring Phase 2 DONE। |
| M7 | Chief Quality & Security Agent | 07 Quality & Security | EXISTING — `01-Agency-Department/departments/07-quality-security/manager/chief_quality_security_agent.py` (`manage_quality_security`, gate `ok`); skill `departments/07-quality-security/skills/chief-quality-security-agent.md` | Chief wiring Phase 2 DONE। |
| M8 | Chief Innovation Agent | 08 Product & Innovation | EXISTING — `01-Agency-Department/departments/08-product-innovation/manager/chief_innovation_agent.py` (`manage_product_innovation`, gate `ok`); skill `departments/08-product-innovation/skills/chief-innovation-agent.md` | Chief wiring Phase 2 DONE। |

## কীভাবে update করবেন

1. নতুন worker ফাইল বানালে: status EXISTING করুন, repo-relative path + gate দিন, `registry.json`-ও একইভাবে update করুন।
2. ROLE-ONLY → EXISTING হলে skill ফাইলের path-ও দিন।
3. কোনো entry-র status বদলালে তারিখ + কারণ notes-এ লিখুন।
4. কখনো live কাজের দাবি করবেন না যতক্ষণ real run Boss-এর signed-in session-এ verify না হয়।
