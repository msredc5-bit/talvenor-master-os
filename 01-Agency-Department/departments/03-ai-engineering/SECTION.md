# 03 — AI Engineering Department

## উদ্দেশ্য (Purpose)

Talvenor-এর AI receptionist build-এর engineering পথ এক জায়গায় রাখা: solution
design, voice agent build (DRAFT plan only), conversation design, prompt
engineering, Vapi integration, calendar integration, n8n automation, QA, আর
deployment plan। এই department শুধু plan আর DRAFT বানায় — production-এ কিছু
বদলায় না, কিছু deploy করে না।

## Manager

- **CTO AI Engineering Agent** — `CTOAIEngineeringAgent`, task_kind `manage_ai_engineering`, gate `ok`
- Manager file: `01-Agency-Department/departments/03-ai-engineering/manager/cto_ai_engineering_agent.py`
- Skill file: `01-Agency-Department/departments/03-ai-engineering/skills/cto-ai-engineering-agent.md`
- Manager কোনো worker execute করে না, কিছু deploy করে না।
- Agency Chief wiring **Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।

## Mapped Existing Staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| RetellBuilder | `receptionist_build` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | ok | EXISTING — DRAFT plan ONLY |
| QAEngineer | `receptionist_qa` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | none | EXISTING — shared with dept 07, partial (QA checklist) |

Note: RetellBuilder-এর আসল worker task_kind `delivery.py`-তে `retell_build`;
এই department-এ delegation key `receptionist_build`। RetellBuilder **DRAFT plan
only** — live production stack **Vapi/Sophia**, Retell নয়। QAEngineer dept 07
(Quality & Security)-এর সঙ্গে shared; QA checklist মাত্র, full testing worker নয়।

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| AI Solution Architect | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Voice Agent Builder | EXISTING — RetellBuilder | `receptionist_build`, gate ok — DRAFT plan only; live stack Vapi/Sophia |
| Conversation Designer | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Prompt Engineering Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Vapi Integration Agent | ROLE-ONLY | Brief-এর integration role-এর নাম সংশোধন করা হয়েছে — live provider Vapi; কোনো worker code নেই |
| CRM Integration Agent | **GAP** | CRM (n8n Data Tables) live নয় — integration সম্ভব নয়; কোনো worker/skill নেই |
| Calendar Integration Agent | ROLE-ONLY | Booking link live (Google Calendar Appointment Schedule, 15 min, New York Time); কোনো worker code নেই |
| n8n Automation Engineer | ROLE-ONLY | n8n workflows READY, not LIVE; কোনো worker code নেই |
| Testing & Debugging Agent | EXISTING — QAEngineer (partial) | `receptionist_qa`, QA checklist; dept 07-এর সঙ্গে shared |
| Deployment Agent | ROLE-ONLY | Deployment-এ Boss-এর ok + manual steps লাগে; কোনো worker deploy করে না |

## Missing Roles

- **CRM Integration Agent — GAP।** CRM live না হওয়া পর্যন্ত এই role তৈরি করা
  যায় না; কোনো worker code বা skill নেই।
- ROLE-ONLY ৭টি role-এর (AI Solution Architect, Conversation Designer, Prompt
  Engineering, Vapi Integration, Calendar Integration, n8n Automation, Deployment)
  কোনো worker code নেই; এগুলো skill doc-এর role হিসেবে থাকে।

## Honest Status

- **LIVE production voice: Vapi — Sophia, live receptionist, +1 (947) 223-0244**,
  org 1861a735, GPT-4o-mini, Emma voice, Deepgram nova-3। Sophia কোনো demo agent নয়;
  Ava ছিল demo (deleted; rebuild pending, separate demo account-এ)।
- **Retell DROPPED 2026-10-26** — Retell কখনো production নয়; RetellBuilder শুধু
  DRAFT plan।
- **Paying clients: 0** — এখনো কোনো paying client নেই।
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; সব output DRAFT।
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — এটাই DB, অন্য কোনো database নয়।
- **CRM: n8n Cloud Data Tables PLANNED, not live।**
- **Calendar: Google Calendar Appointment Schedule LIVE** — booking link
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)।
- **n8n workflows READY, not LIVE।**
- **Deployment: Boss-এর ok + manual steps** — কোনো worker deploy করে না।
- **$0 spend cap** — কিছু খরচ করা হয় না।
- **Agency Chief wiring Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই department-এর manager-কে call করে।
- **Pricing LOCKED, internal only** — prospect-কে কখনো দাম বলা হয় না।
- **No dental/medical ever** — dental/medical বা patient-health ব্যবসা target নয়।
- Brand **Talvenor only**। কোনো invented client, price, statistic, testimonial, guarantee নেই।
