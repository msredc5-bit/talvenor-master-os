# Workflow 2 — Sales Outreach

**Department:** 01 Sales & Growth
**তারিখ:** 2026-11-19 | **Status:** ⛔ PAUSED — draft only (2026-11-14 থেকে, Boss-এর নির্দেশ)।

## Purpose (উদ্দেশ্য)

Tier 1/2 lead-দের কাছে personalized email + Instagram DM পাঠিয়ে Talvenor AI receptionist-এর কথা জানানো আর 15-min demo call-এ booking নেওয়া — কোনো price quote ছাড়া, কোনো pressure ছাড়া।

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Email Outreach Agent (`OutreachDrafter`) | 01 | EXISTING — draft লেখে মাত্র, কখনো পাঠায় না |
| Follow-up Agent (`FollowUpAgent`) | 01 | EXISTING — PARKED (100-mail rule) |
| ReplyHandler (`reply_triage`) | 01 | EXISTING — reply triage |
| SalesCloser / NegotiationCoach | 01 | EXISTING — close/negotiation prep (draft only) |
| SchedulerAssistant (`schedule_help`) | 01 | EXISTING — booking link সাহায্য |

## সত্য অবস্থা (CURRENT STATE — PAUSED)

- **Email PAUSED 2026-11-14 থেকে।** কারণ: DNS fix বাকি (SPF-এ Gmail include নেই, DMARC missing)। Boss DNS panel-এ fix করলে + "check koro" বললে তবেই restart।
- **প্রথম মেইল 162** — PA 39, TX 15, GA 16, FL 54, CA 14, NC 5, IL 9, MI 5, OH 1, NY 4।
- **Day 4 / Day 5 / Day 6 draft — 25টা করে READY, পাঠানো হয়নি।** Pause উঠলে Boss যেটা বলবেন সেটাই যাবে।
- **Follow-up rule (standing, 2026-11-10):** কোনো state-এ 100টা প্রথম মেইল complete না হওয়া পর্যন্ত ওই state-এর কোনো follow-up নয়। কোনো state-ই 100-তে নেই (FL ceiling 98 — 100-তে পৌঁছাতে পারবে না)। তাই follow-up **PARKED**।
- **IG DM: 5–10/day** via `@talvenor_ai` — Boss-এর approval tap লাগে।
- **n8n auto-send READY, LIVE নয়** — Boss-এর import + 1টা test মেইল বাকি।

## Step-by-step

### ধাপ ১ — Draft লেখা (OutreachDrafter)

1. Lead-এর research notes পড়ুন (business name, owner, pain signal, angle)।
2. **Personalized email draft** লিখুন — একটাই idea, plain US English, একটা CTA: 15-min demo call।
3. **Demo = recorded 60-second demo video:** https://facebook.com/reel/2947321012290705/ — সবসময় "60-second demo" বলুন।
4. Sender: `hello@talvenorai.agency` (outreach address)। `contact@talvenorai.agency` কখনো cold outreach-এ নয়।
5. **কখনো price quote করবেন না** — pricing internal only। কেউ দাম জানতে চাইলে: short call-এ details শেয়ার করব, booking link দিন।
6. **Gate:** draft-এ gate নেই — draft লেখা পাঠানো নয়।

### ধাপ ২ — Send (PAUSED — এখন এই ধাপ বন্ধ)

1. **স্বাভাবিক নিয়ম (pause না থাকলে):** 20–30টা email/day, Boss-এর exact gate word **`send`** ছাড়া কিছু পাঠানো যাবে না।
2. **এখন:** PAUSED। কোনো মেইল যাবে না। Day 4/5/6 draft READY অবস্থায় থাকবে।
3. n8n auto-send LIVE নয় — তাই auto-send-ও এখন হয় না।
4. **Gate:** `send` — Boss-এর exact word। Pause থাকলে `send` বললেও পাঠানো যাবে না যতক্ষণ DNS fix verify না হয়।

### ধাপ ৩ — Instagram DM (5–10/day)

1. Lead-এর Instagram account খুঁজুন; DM পাঠানোর আগে observe করুন — comment-এ কখনো pitch নয়।
2. DM draft লিখুন (OutreachDrafter, channel = instagram) — short, personal, একটা CTA।
3. **Gate:** Boss-এর approval tap ছাড়া DM পাঠানো যাবে না।

### ধাপ ৪ — Follow-up (PARKED)

1. **100-mail rule:** state-এ 100 প্রথম মেইল complete হলে তবেই ওই state-এর lead-দের follow-up।
2. এখন কোনো state 100-তে নেই — **তাই কোনো follow-up নয়**। PA-তে 37 প্রথম মেইল।
3. Follow-up draft (`FollowUpAgent`) লেখা থাকতে পারে, পাঠানো যাবে না।
4. **Gate:** `send` — + 100-mail rule পূরণ।

### ধাপ ৫ — Reply triage (ReplyHandler)

1. Reply এলে triage করুন:
   - **Decline / not interested → polite exit** — আর follow-up নয়, তর্ক নয়।
   - **Interest / question / pricing / demo request → draft only** — reply draft লিখুন, Boss-কে দেখান, Boss-এর কথায় পাঠান। কখনো price নয় — booking link দিন: https://calendar.app.google/WLoxBfnLGTdjK3LB8
   - **Bounce / dead address →** lead row-তে `bounced`/`dead` লিখুন, row delete করবেন না, আর মেইল করবেন না।
2. **Zoho gap:** `hello@`-তে আসা reply Zoho-তে যায় — Elora দেখতে পায় না। **Boss-কে নিজে check করে forward করতে হয়।**
3. **Gate:** reply পাঠাতে `send` লাগে — Boss-এর exact word।

## Honest status

- Outreach **PAUSED** — draft লেখা চলছে, পাঠানো বন্ধ।
- Follow-up **PARKED** — 100-mail rule-এ আটকে আছে।
- Reply triage worker আছে, কিন্তু Zoho-র reply Boss forward না করলে Elora দেখতে পায় না।

## Missing inputs (যা নেই)

- DNS fix (Boss-এর DNS panel): SPF-এ `include:_spf.google.com` + `_dmarc` record — না হলে restart নয়।
- Boss-এর "check koro" + restart-এর কথা।
- Zoho reply forward (Boss-এর কাজ)।
- n8n auto-send-এর import + test (Boss-এর কাজ)।
