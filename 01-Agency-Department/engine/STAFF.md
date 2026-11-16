# STAFF.md — Agency Engine-র কর্মী তালিকা (Phase 5)

Talvenor AI Receptionist Agency — Boss-এর প্রথম ব্যবসা, MAIN।
এই তালিকার ১৫টা role = `01-Agency-Department/engine/workers/src/workers/`-এর ১৫টা আসল (vendored copy; upstream `~/workspace/boss-ceo/src/workers/`)
worker, একটাও বানানো নয়। নাম, division, gate — Chief-এর ROUTING
(`../chief_of_staff_agency.py`) থেকে হুবহু নেওয়া।

সত্য অবস্থা (2026-11-16): Email PAUSED (2026-11-14 থেকে, DNS fix বাকি) —
draft-ই শেষ কথা, send নয়। Paying client 0। প্রথম মেইল 162।
Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।
সব worker MockLLMProvider (mock brain, $0) দিয়ে চলে — সব output DRAFT।
Live stack Vapi/Sophia — RetellBuilder-এর output শুধু DRAFT build plan।

Gate শব্দের মানে: output পাঠাতে/ব্যবহার করতে Boss-এর যে exact শব্দ লাগবে।
None = draft নিজেই নিরাপদ, কোনো gate নেই।

---

## 1. Prospect Researcher

- **Worker:** `ProspectResearcher` · **Division:** ACQ · **Task type:** `prospect_research` · **Gate:** None
- **কী করে:** US home-service SMB (plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet) খুঁজে বের করে — owner-এর নাম, missed-call pain signal, tech gap, আর personalization angle সহ। Dental/medical/patient-health কখনো নয়।
- **Input:** `niche` (default: plumbing), `region` (default: Texas)।
- **Output:** ১০টা prospect-এর research notes — field: name, owner, pain_signals, angle।
- **Skill:** `skills/prospect-researcher.md` · **SOP ভিত্তি:** agency-os SKILL 02-lead-generation + SOP prospect-qualification-talvenor.md।

## 2. Outreach Drafter

- **Worker:** `OutreachDrafter` · **Division:** ACQ · **Task type:** `outreach_draft` · **Gate:** `send`
- **কী করে:** Cold email / Instagram DM-এর draft লেখে — short, plain US English, hook প্রথমে, একটা CTA (short call)। Email 20–30/day, IG 5–10/day warm-up। Draft ONLY — পাঠানো Boss-এর কাজ।
- **Input:** `channel` (email | instagram, default: email)।
- **Output:** ৫টা draft — email হলে from `hello@talvenorai.agency`, IG হলে `@talvenor_ai`। কোনো price, guarantee, বানানো client নয়।
- **Skill:** `skills/outreach-drafter.md` · **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach। **সীমা:** Email PAUSED — draft-ই শেষ কথা।

## 3. Reply Triager

- **Worker:** `ReplyHandler` · **Division:** ACQ · **Task type:** `reply_triage` · **Gate:** `send`
- **কী করে:** Prospect-এর reply আলাদা করে — interest / question / pricing / demo request / decline। Decline হলে polite exit; বাকিগুলো DRAFT reply only — price quote নয়, short call-এর offer, Boss-কে নাম + platform + message সহ flag করা।
- **Input:** `reply_type` (default: interest)।
- **Output:** Triage verdict + draft reply (interest-ধরনের reply-তে gate `send`, decline-এ gate None)।
- **Skill:** `skills/reply-triager.md` · **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (reply rule 2026-10-14)।

## 4. Negotiation Coach

- **Worker:** `NegotiationCoach` · **Division:** ACQ · **Task type:** `negotiation_prep` · **Gate:** `ok`
- **কী করে:** Founder-কে live sales call-এর জন্য তৈরি করে — ৩টা সম্ভাব্য প্রশ্ন + শক্ত উত্তর, এড়ানোর মতো ২টা trap, আর ৬০ সেকেন্ডের opening script (plain US English)। Call Boss নিজে নেন — এটা শুধু prep।
- **Input:** `prospect` (profile, default: খালি), `goal` (default: book the demo call)।
- **Output:** Prep pack — ৩ Q&A, ২ trap, ৬০-sec opening script। Boss-এর সিদ্ধান্ত লাগে এমন কিছু থাকলে GATE হিসেবে flag করা। কোনো price quote নয়।
- **Skill:** `skills/negotiation-coach.md` · **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (call prep / objection handling)।

## 5. Receptionist Builder

- **Worker:** `RetellBuilder` · **Division:** DEL · **Task type:** `receptionist_build` · **Gate:** `ok`
- **কী করে:** Client-এর receptionist-এর **DRAFT build plan** লেখে — agent prompt, knowledge base, recording script। Live stack Vapi/Sophia (Boss Retell-এর জন্য টাকা দেবেন না) — তাই এই worker কখনো live build করে না, শুধু plan।
- **Input:** `business` (default: Apex Plumbing), `trade` (default: plumbing)।
- **Output:** DRAFT plan — agent-prompt, knowledge-base, recording-script। In-prompt schedule, emergency flow, callback handling, FAQ, honest AI disclosure, fictional AP- confirmation number, end_call only। কোনো বানানো pricing নয়।
- **Skill:** `skills/receptionist-builder.md` · **SOP ভিত্তি:** agency-os SKILL 06-vapi-voice-agent (Vapi layer) + 05-agent-architecture।

## 6. QA Engineer

- **Worker:** `QAEngineer` · **Division:** DEL · **Task type:** `receptionist_qa` · **Gate:** None
- **কী করে:** Demo receptionist READY বলার আগে ১২টা check-এর QA checklist চালায় — prompt completeness, ভাঙা tool reference নেই, emergency flow, pricing honesty, transfer number আসল-না-অনুপস্থিত, end_call behavior।
- **Input:** `agent` (default: ava-apex-plumbing-demo)।
- **Output:** Checklist + verdict: READY অথবা CHANGES। Verdict-ই শেষ কথা নয় — delivery-তে Boss-এর ok লাগে।
- **Skill:** `skills/qa-engineer.md` · **SOP ভিত্তি:** agency-os SKILL 18-qa-testing (mandatory gate)।

## 7. Onboarding Agent

- **Worker:** `OnboardingAgent` · **Division:** DEL · **Task type:** `onboarding_draft` · **Gate:** `ok`
- **কী করে:** নতুন client-এর onboarding pack-এর draft লেখে — business info form, hours/services/price-list request, transfer number confirmation, ৭ দিনে live-এর শর্ত (3-month minimum, তারপর month-to-month)।
- **Input:** `client` (default: new client)।
- **Output:** Onboarding pack — info-form, terms, timeline। কোনো বানানো detail নয়; client-এর আসল তথ্য না থাকলে "BOSS INPUT REQUIRED"।
- **Skill:** `skills/onboarding-agent.md` · **SOP ভিত্তি:** agency-os SKILL 20-agency-operations (onboarding)।

## 8. Content Planner

- **Worker:** `ContentPlanner` · **Division:** MKT · **Task type:** `content_plan` · **Gate:** `ok`
- **কী করে:** প্রতি রবিবার ৬টা (Dhaka) পরের সপ্তাহের ৫ পোস্টের plan বানায় — Facebook / Instagram / LinkedIn, pillar: missed-call pain, AI receptionist demo, founder voice, social proof (বানানো client ছাড়া), CTA। প্রতি পোস্টে platform, format, hook, best US-Eastern time।
- **Input:** (কোনো default payload নেই — সপ্তাহের plan-ই input)।
- **Output:** ৫ পোস্টের plan। Boss-এর "ok" না পেলে কিছু বানানো হয় না।
- **Skill:** `skills/content-planner.md` · **SOP ভিত্তি:** agency-os SKILL 17-marketing।

## 9. Video Producer

- **Worker:** `VideoProducer` · **Division:** MKT · **Task type:** `video_produce` · **Gate:** `ok`
- **কী করে:** Reel package বানায় — প্রথম ২ সেকেন্ডে hook, REAL footage (frame-verified, stills-motion নয়), US-English voiceover, karaoke caption, Talvenor end card (wave logo, কখনো redraw নয়), hypothetical-এ "Illustrative example"। Format 9:16।
- **Input:** `topic` (default: missed call = lost job)।
- **Output:** Reel package (script + shot list + voiceover + caption spec)। Publish/upload-এ gate `upload it` লাগে — এই worker নিজে upload করে না।
- **Skill:** `skills/video-producer.md` · **SOP ভিত্তি:** agency-os SKILL 17-marketing + reel-factory SOP।

## 10. Caption Writer

- **Worker:** `CaptionWriter` · **Division:** MKT · **Task type:** `caption_write` · **Gate:** None
- **কী করে:** Finished creative-এর caption + hashtag + CTA pack লেখে — প্রথম লাইনে hook, plain US English, একটা CTA ("link in bio" শুধু যখন আসল booking link আছে)। Hashtag: IG 5–8, LinkedIn 3, Facebook 0–2।
- **Input:** `platform` (default: instagram)।
- **Output:** Caption pack — caption, hashtags, CTA। কোনো price, guarantee নয়। Publish-এ তবুও gate লাগে (`post it`) — caption নিজে publish নয়।
- **Skill:** `skills/caption-writer.md` · **SOP ভিত্তি:** agency-os SKILL 17-marketing + caption-pack SOP।

## 11. Publish Prep

- **Worker:** `PublishPrep` · **Division:** MKT · **Task type:** `publish_prep` · **Gate:** `post it`
- **কী করে:** Approved post publish-এর জন্য তৈরি করে — final file + caption + first comment + scheduled time (US Eastern)। শুধু PREPARE — publish করে না। Detached auto-publish নিষিদ্ধ (2026-10-10 lesson)।
- **Input:** `count` (default: 2)।
- **Output:** Publish-ready pack। Publishing শুধু main chat থেকে, Boss "post it" বললে।
- **Skill:** `skills/publish-prep.md` · **SOP ভিত্তি:** agency-os SKILL 17-marketing + 2026-10-10 publishing lesson।

## 12. Objection Simulator

- **Worker:** `ObjectionSimulator` · **Division:** MKT · **Task type:** `objection_sim` · **Gate:** `ok`
- **কী করে:** আসল outreach যাওয়ার আগে সন্দেহপ্রবণ prospect সেজে draft-কে পরীক্ষা করে — সম্ভাব্য ৫টা objection, prospect-এর নিজের ভাষায়, likelihood অনুযায়ী ranked, প্রতিটার এক লাইনের rebuttal angle। কঠোর হতে হয় — দুর্বল draft টিকতে পারবে না।
- **Input:** `draft`, `prospect` (দুটোই default খালি)।
- **Output:** ৫ objection + rebuttal angle। REVIEW ONLY — কখনো prospect-কে পাঠানো হয় না।
- **Skill:** `skills/objection-simulator.md` · **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (objection handling)।

## 13. Inbox Triager

- **Worker:** `InboxTriager` · **Division:** OPS · **Task type:** `inbox_triage` · **Gate:** None
- **কী করে:** Inbox সাজায় — urgent / prospect / vendor / noise। Boss-এর voice-এ (short, plain) draft reply লেখে। টাকা, প্রতিশ্রুতি, বা পাঠানোর মতো কিছু থাকলে Boss-কে flag করে। কিছু পাঠায় না।
- **Input:** (কোনো default payload নেই — inbox-ই input)।
- **Output:** Triage list + draft reply। Sends: False — DRAFT ONLY।
- **Skill:** `skills/inbox-triager.md` · **SOP ভিত্তি:** agency-os SKILL 20-agency-operations + 15-crm-lead-machine।

## 14. Report Compiler

- **Worker:** `ReportCompiler` · **Division:** OPS · **Task type:** `report_compile` · **Gate:** None
- **কী করে:** সাপ্তাহিক performance report বানায় — কী post হয়েছে, দেখা যায় এমন platform number দিয়ে best/worst, lead list (নাম/platform/message/next step), পরের সপ্তাহে কী বদলাবে। Number না থাকলে "নেই" বলে Boss-কে paste করতে বলে — কখনো অনুমান বা বানানো metric নয়।
- **Input:** (কোনো default payload নেই — সপ্তাহের কাজ + platform number-ই input)।
- **Output:** Report — posted, performance, leads, next-week। Metrics policy: visible-only।
- **Skill:** `skills/report-compiler.md` · **SOP ভিত্তি:** agency-os SKILL 20-agency-operations (reporting) + 15-crm-lead-machine।

## 15. Scheduler

- **Worker:** `SchedulerAssistant` · **Division:** OPS · **Task type:** `schedule_help` · **Gate:** None
- **কী করে:** Scheduling-এ সাহায্য করে — ৩টা slot প্রস্তাব করে (Asia/Dhaka + US-Eastern equivalent), invite-এর draft লেখে। Boss confirm করার আগে কিছু পাঠানো হয় না।
- **Input:** `what` (default: client demo call)।
- **Output:** ৩ slot + draft invite। Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)।
- **Skill:** `skills/scheduler.md` · **SOP ভিত্তি:** agency-os SKILL 20-agency-operations।

---

**Source:** `01-Agency-Department/engine/workers/src/workers/{acquisition,delivery,marketing,admin}.py` (vendored; upstream `~/workspace/boss-ceo/src/workers/`)
(task_kind / default_payload / requires_gate) · `../chief_of_staff_agency.py` (ROUTING)
· `../pipeline.md` · `~/workspace/agency-os/SOP/prospect-qualification-talvenor.md`
· agency-os SKILL 02, 03, 06, 15, 16, 17, 18, 20।
