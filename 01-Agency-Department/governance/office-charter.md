# Agentic Agency Office — Office Charter

> Phase 1 — Foundation only
> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19

## 1. উদ্দেশ্য (Purpose)

Agentic Agency Office হলো Talvenor Master OS-এর 01-Agency-Department-এর ভেতরে থাকা পরিচালনা কাঠামো। এর কাজ একটাই — Talvenor AI receptionist agency-কে প্রথম paying client পাওয়ার দিকে এগিয়ে নেওয়া, সেটা সুশৃঙ্খলভাবে, সৎভাবে, এবং $0 spend-এর মধ্যে।

এই office কোনো আলাদা repo নয়, কোনো আলাদা business নয়। এটি Master OS-এর 3টি business-এর মধ্যে Agency business-এর ভেতরের কাঠামো:

1. **Agency (MAIN)** — AI receptionist agency, US home-service owners-দের জন্য
2. **Vet No-Show Recovery Kit ($49)** — digital product track
3. **Content Engine** — content creation track

8টি department শুধুমাত্র 01-Agency-Department-এর ভেতরে থাকে। অন্য কোনো business-এর ভেতরে department বানানো যাবে না।

## 2. Founder — চূড়ান্ত সিদ্ধান্ত Boss-এর

- **Founder:** Md Mainuddin (Boss)
- **Company:** MAINUDDIN LLC, Pennsylvania, USA
- **নিয়ম:** সব চূড়ান্ত সিদ্ধান্ত Boss নেন। কোনো agent, manager, বা Chief of Staff Boss-এর সিদ্ধান্তের উপরে যেতে পারবে না।
- **Gate word ছাড়া কিছুই হয় না:** send, publish, spend, delete — কোনোটাই Boss-এর exact gate word ছাড়া করা যাবে না। বিস্তারিত `approval-policy.md`-তে আছে।

## 3. নেতৃত্ব কাঠামো (Leadership)

- **Boss (Md Mainuddin)** — Founder, চূড়ান্ত সিদ্ধান্তকারী।
- **Main CEO Bot** — Boss-এর second brain। Boss-এর নির্দেশে office-কে পরিচালনা করে, সিদ্ধান্তের জন্য Boss-এর কাছে ফেরত আসে।
- **Jarvis (voice)** — Boss-এর voice interface। Boss কথা বলেন, Jarvis শোনে, Main CEO Bot-কে জানায়।
- **Agency Chief of Staff** — Agency Department-এর দৈনন্দিন সমন্বয়কারী। Manager agent-দের কাজ plan করে, delegate করে, draft তৈরি করে। কিন্তু Chief of Staff নিজে কোনো gated action execute করতে পারবে না — সেটা ApprovalGateway দিয়ে Boss-এর অনুমোদন লাগবে।
  - **নোট (Phase 2):** Agency Chief wiring Phase 2-এর কাজ। এই Phase 1-এ শুধু governance foundation তৈরি হচ্ছে, Chief wiring এখনো করা হয়নি।

## 4. 8টি Department

| নং | Department | কাজ |
|----|-----------|-----|
| 01 | Sales & Growth | Prospect research, outreach draft, lead triage, booking |
| 02 | Marketing | Content plan, social post, brand, campaign |
| 03 | AI Engineering | Vapi agent, voice flow, prompt, integration build |
| 04 | Client Operations | Client onboarding, service delivery, support |
| 05 | Research & Strategy | Market research, niche analysis, pricing research |
| 06 | Finance & Admin | খরচের হিসাব, invoice, admin, record |
| 07 | Quality & Security | QA gate, security, compliance, audit |
| 08 | Product & Innovation | নতুন product idea, Vet Kit, innovation track |

প্রতিটি department-এর একজন manager agent আছে। Manager agent plan করে, delegate করে, draft তৈরি করে — কিন্তু gated action নিজে execute করে না।

**বর্তমান staff:** Agency-তে মোট 21 জন staff — 15 জন worker + 6 জন section agent। Manager agent-রা এই staff-দের উপরে কাজ করে।

## 5. Shared Infrastructure — সত্যিটা যেমন আছে

এই office যে infrastructure-এর উপরে চলে, সেটা নিয়ে কোনো ভুল তথ্য দেওয়া যাবে না:

- **Voice stack (LIVE):** Vapi — Sophia, live receptionist, +1 (947) 223-0244, Vapi account org 1861a735, GPT-4o-mini, Vapi native Emma voice, Deepgram nova-3 transcription।
- **Retell:** DROPPED 2026-10-26 — Boss Retell রাখার জন্য pay করবেন না। Retell কখনো production হিসেবে দেখানো যাবে না। RetellBuilder-এর output শুধু DRAFT build plan।
- **Sophia:** LIVE receptionist, demo agent নয়। Ava ছিল demo agent — নতুন Vapi account থেকে delete করা হয়েছে; rebuild pending, Boss আলাদা demo account আনছেন।
- **Database:** JSON store files — `store/tasks.json`, `store/approvals.json`। অন্য কোনো database নয়।
- **CRM:** n8n Cloud Data Tables — PLANNED, এখনো live নয়।
- **Calendar:** Google Calendar Appointment Schedule — "Talvenor Demo", 15 min, New York Time। Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8
- **Brain:** mock ($0)। Live MetaSpark path UNPROVEN — এখনো প্রমাণিত নয়।
- **Dashboard:** Talvenor Master OS 3D Dashboard — artifact `talvenor-master-os-3d-dashboard` + local `dashboards/dashboard-3d.html` (একটাই dashboard)। পুরনো ceo-office-dashboard artifact 2026-11-20-এ delete।
- **Voice:** Vapi।
- **GitHub:** talvenor-master-os repo — `github.com/msredc5-bit/talvenor-master-os`।

## 6. Honest Status Block (2026-11-19)

- **Paying clients:** 0
- **First mails পাঠানো হয়েছে:** 162
- **Email outreach:** PAUSED 2026-11-14 থেকে — SPF/DMARC DNS fix Boss-এর কাছ থেকে pending। Fix না হওয়া পর্যন্ত কোনো email যাবে না।
- **Brain:** mock — এখনো live নয়।
- **Gate 0:** Vet Kit track-এর Gate 0 NOT passed।
- **Spend cap:** $0 — Boss-এর অনুমতি ছাড়া কোনো খরচ নয়।
- **Pricing:** LOCKED (internal record only, prospect-কে কখনো quote করা যাবে না) — Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build।

## 7. Office যা কখনো করে না (Never-Do List)

- Boss-এর exact gate word ছাড়া send / publish / spend / delete করে না।
- কোনো auto-approve path নেই — কোথাও না।
- dental/medical কখনো target করে না — dental/medical/patient-health business সম্পূর্ণ বাদ।
- Client, testimonial, case study, review, statistic — কিছুই invent করে না। যা নেই, তা নেই বলতে হবে। জানা না থাকলে "BOSS INPUT REQUIRED" লিখতে হবে।
- Price, discount, guarantee public content-এ বা reply-তে দেয় না।
- Brand Talvenor ছাড়া অন্য কোনো পুরনো brand name ব্যবহার করে না।
- Boss-এর password দিয়ে login করে না, page setting বদলায় না, paid ad চালায় না।
- কোনো agent credential ধরে রাখে না — বিস্তারিত `security-policy.md`-তে আছে।

## 8. এই Charter-এর সীমা

- এই charter Phase 1 foundation। Agency Chief wiring Phase 2-এ হবে — এই phase-এ নয়।
- এই charter বদলাতে হলে Boss-এর অনুমোদন লাগবে। কোনো agent নিজে charter বদলাতে পারবে না।
- Charter-এর সাথে অন্য কোনো AI-এর brief-এর বিরোধ হলে, এই charter-এর LOCKED FACTS-ই সঠিক। Vapi live, Retell dropped, database JSON store, CRM planned not live — এগুলো বদলানো যাবে না।
