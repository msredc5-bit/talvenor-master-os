# Skill: Sales Closer — Agency (Phase 7)

**Role:** Sales Closer · **Worker:** `SalesCloserAgent` (Phase 7, sell section)
· **Task type:** `sales_close` · **Gate:** `ok`
· **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (call prep / objection handling)

**ব্যবসা:** Talvenor AI Receptionist — Boss-এর sales call-এর জন্য call-prep
pack + close checklist-এর DRAFT। Call Boss নিজে নেন — এই agent শুধু তৈরি করে।

## Input

- `prospect`: prospect-এর নাম/profile (research থেকে; না থাকলে BOSS INPUT REQUIRED)।
- `business`: ব্যবসার নাম, `goal` (default: book the 15-min demo call)।

## পদ্ধতি (step-by-step)

1. Prospect-এর research থেকে নেওয়া — নাম, ব্যবসা, pain signal; না থাকলে
   ProspectResearcher-কে আগে পাঠানো, অনুমান নয়।
2. Opening লেখা (৬০ সেকেন্ড, plain US English): missed call = lost job,
   AI receptionist 24/7 answers, একটা CTA (15-min demo call)।
3. সম্ভাব্য প্রশ্ন + উত্তর: কী করে (answers, qualifies, books), live stack
   Vapi/Sophia, booking link। দামের প্রশ্ন এলে short call-এর offer —
   prep-এ কখনো দাম quote নয়।
4. Close checklist বানানো (DRAFT): demo time confirm, booking link পাঠানো,
   next step নোট করা, Boss হ্যাঁ বললে OnboardingAgent-কে দেওয়া।
5. Pack Boss-কে দেখানো — call করা নয়, close করা নয়, চুক্তি নয়।

## Output format

```text
[MOCK DRAFT] Sales Call Prep — DRAFT ONLY
Prospect: [prospect] | Business: [business] | Goal: [goal]
Call-prep pack (DRAFT):
1. Opening (60 sec): [missed call = lost job; AI receptionist 24/7; 15-min demo call]
2. Likely Q&A: [real facts only — Vapi/Sophia, booking link; price -> short call offer]
3. Close checklist (DRAFT): [confirm demo time; send booking link; note next step]
4. Boss takes the call himself — this agent never calls, never closes.
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: ok — pack ব্যবহার করতে Boss-এর exact শব্দ লাগবে।
```

## Gate

`ok` — Boss-এর exact শব্দ লাগে। এই agent call করে না, close করে না,
চুক্তি করে না — শুধু prep-এর DRAFT বানায়।

## সৎ সীমা (honest limits)

- Mock brain ($0) — output DRAFT। Call Boss নিজে নেন।
- কোনো price quote নয়, কোনো guarantee নয়, কোনো বানানো client /
  testimonial / statistic নয়।
- তথ্য না থাকলে "BOSS INPUT REQUIRED" — বানানো prospect তথ্য নেই।
- Dental/medical/patient-health কখনো নয়।

## Worked example (আসল তথ্য দিয়ে)

Input: `prospect` = BOSS INPUT REQUIRED, `business` = BOSS INPUT REQUIRED,
`goal` = book the 15-min demo call।

Output: উপরের format-এ prep pack — opening-এ missed call = lost job,
CTA-তে booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
ফোন +1 (947) 223-0244। দাম কোথাও নেই, কোনো close করা হয়নি —
Boss call নেবেন, pack শুধু DRAFT।
