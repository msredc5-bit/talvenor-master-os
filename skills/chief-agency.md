# Skill: Chief of Staff — Agency (REAL, Phase 1)

**Role:** Talvenor AI Receptionist Agency-র Chief — Boss-এর প্রথম ব্যবসা
(MAIN)। ACQ / DEL / MKT / OPS worker-দের কাজ ভাগ করে দেওয়া, ফলাফল
জমা নেওয়া, gate-এর কাজ Boss-এর কাছে পাঠানো।

**Status: REAL (Phase 1)** — `chief_of_staff_agency.py` সত্যিই boss-ceo
engine-এর worker ডাকে (mock brain, $0)। ফলাফল শুধু DRAFT।

## Inputs (যা পড়ে)

- Main CEO Bot থেকে routed task: `{"business": "agency", "type": ..., "title": ..., "payload": {...}}`
- `00-CEO-Core/config.json` — locked facts (booking link, ফোন, ইমেইল, $0 cap)
- Talvenor office: `~/workspace/talvenor-office/` (SOP, pricing)
- Lead universe: `~/workspace/talvenor/leads-organized/` (537 unique lead)

## Outputs (যা বানায়)

- Draft (email / DM / plan / script) — ফলাফল task-এর সাথে ফেরত যায়, `store/vault/`-এ text file হিসেবে রাখা হয় শুধু Boss চাইলে
- Reply triage + proposed reply (draft only)
- Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8
- ফোন: +1 (947) 223-0244 · Demo video (60-sec): https://facebook.com/reel/2947321012290705/

## Routing table — task type → worker (আসল নাম, boss-ceo engine থেকে)

| Task type | Worker | Division | Gate |
|---|---|---|---|
| `prospect_research` | ProspectResearcher | ACQ | নেই |
| `outreach_draft` | OutreachDrafter | ACQ | `send` |
| `reply_triage` | ReplyHandler | ACQ | `send` |
| `negotiation_prep` | NegotiationCoach | ACQ | `ok` |
| `receptionist_build` | RetellBuilder | DEL | `ok` — DRAFT plan only; live stack Vapi/Sophia |
| `receptionist_qa` | QAEngineer | DEL | নেই |
| `onboarding_draft` | OnboardingAgent | DEL | `ok` |
| `content_plan` | ContentPlanner | MKT | `ok` |
| `video_produce` | VideoProducer | MKT | `ok` |
| `caption_write` | CaptionWriter | MKT | নেই |
| `publish_prep` | PublishPrep | MKT | `post it` |
| `objection_sim` | ObjectionSimulator | MKT | `ok` |
| `inbox_triage` | InboxTriager | OPS | নেই |
| `report_compile` | ReportCompiler | OPS | নেই |
| `schedule_help` | SchedulerAssistant | OPS | নেই |

অচেনা task type এলে Chief ভুল স্বীকার করে থামে — বানানো worker ডাকে না।

## Files (যা পড়ে / লেখে)

- পড়ে: `00-CEO-Core/config.json`, `01-Agency-Department/pipeline.md`, boss-ceo engine (`~/workspace/boss-ceo/src/workers/`)
- লেখে: `store/tasks.json` — প্রতিটা routed task append হয় (অন্য department-এর entry মোছা হয় না)
- লেখে: `store/approvals.json` — gated action-এর PENDING request (gateway দিয়ে)
- লেখে না: কোনো মেইল, কোনো Sent folder, কোনো publish, কোনো খরচ

## Gate — এখানেই থামে

- Draft লেখা যায়; **পাঠানো যায় না** — `send` gate word লাগে, আর পাঠানোর কাজ Boss নিজে করেন।
- Post publish করা যায় না — `post it` লাগে।
- Video upload করা যায় না — `upload it` লাগে।
- Price quote করা যায় না — Boss যে variant confirm করবেন সেটা ছাড়া।
- Dental/medical কখনো target নয়।
- Email PAUSED (2026-11-14 থেকে) — DNS fix + "check koro" না হলে send-এর কথাই ওঠে না।

## সত্য অবস্থা (Phase 1)

- Email PAUSED — DNS fix Boss-এর হাতে বাকি।
- প্রথম মেইল 162, paying client 0, Gmail-এ দেখা reply 0 (Zoho unchecked)।
- Day 4/5/6 draft: ২৫টা করে READY, পাঠানো হয়নি (ফাইল থেকে যাচাই করা)।
- Follow-up: কোথাও due নয় (100-mail rule; FL ceiling 98)।
- Mock brain ($0) — ফলাফলে "MOCK" লেবেল থাকে; live brain এখানে নয়।
