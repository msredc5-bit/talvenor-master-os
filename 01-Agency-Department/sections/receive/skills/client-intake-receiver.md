# Skill: Client Intake Receiver — Agency (Phase 7)

**Role:** Client Intake Receiver · **Worker:** `ClientIntakeReceiverAgent` (Phase 7, receive section)
· **Task type:** `client_intake` · **Gate:** `send`
· **SOP ভিত্তি:** agency-os SKILL 02-lead-generation + SOP prospect-qualification-talvenor.md

**ব্যবসা:** Talvenor AI Receptionist — নতুন lead এলে তার তথ্য নেওয়া,
intake log লেখা, আর intake checklist-এর DRAFT বানানো। কোনো reply পাঠানো নয়।

## Input

- `business`: ব্যবসার নাম (আসল source থেকে; না থাকলে BOSS INPUT REQUIRED)।
- `owner`: owner-এর নাম, `trade`: plumbing / HVAC / roofing / garage door /
  septic / tree / foundation / restoration / pest / vet।
- `city`, `state`, `source` (কোথা থেকে lead এলো), `contact`।

## পদ্ধতি (step-by-step)

1. Lead-এর তথ্য নেওয়া — শুধু আসল source থেকে; নাম/ঠিকানা/ফোন কখনো অনুমান নয়।
2. Trade যাচাই করা Talvenor niche-এর মধ্যে কি না — dental/medical/
   patient-health হলে intake নয়, বাদ।
3. Intake log লেখা (returned draft-এ): business, owner, trade, শহর,
   source, contact — missing তথ্যে "BOSS INPUT REQUIRED"।
4. Intake checklist বানানো (DRAFT): তথ্য confirm করা, niche যাচাই,
   missed-call pain signal নোট করা, ProspectResearcher-কে research-এর জন্য দেওয়া।
5. কোনো reply পাঠানো নয় — reply দরকার হলে InboxTriager/OutreachDrafter-এর
   draft, Boss-এর "send" ছাড়া কিছু যায় না।

## Output format

```text
[MOCK DRAFT] Client Intake — DRAFT ONLY
Lead: [business] | Owner: [owner] | Trade: [trade] | City: [city, state] | Source: [source] | Contact: [contact]
Intake checklist (DRAFT):
1. [confirm business + owner from a real source]
2. [niche check — Talvenor niche, dental/medical নয়]
3. [missed-call pain signal, if seen]
4. [hand to ProspectResearcher]
5. [no reply sent from intake]
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: send — intake-সংক্রান্ত কিছু পাঠাতে Boss-এর exact শব্দ লাগবে।
```

## Gate

`send` — Boss-এর exact শব্দ লাগে, আর পাঠানোর কাজ Boss নিজে করেন
(main chat থেকে)। এই system শুধু DRAFT বানায়।

## সৎ সীমা (honest limits)

- Mock brain ($0) — output DRAFT। Intake নিজে কিছু পাঠায় না, call করে না।
- তথ্য না থাকলে "BOSS INPUT REQUIRED" — বানানো client তথ্য নেই।
- কোনো price, guarantee, বানানো client/testimonial/statistic নেই।
- Dental/medical/patient-health কখনো নয়।

## Worked example (আসল তথ্য দিয়ে)

Input: `business` = "BOSS INPUT REQUIRED" (নতুন lead, নাম এখনো confirm হয়নি),
`trade` = plumbing, `city` = Allentown, `state` = PA,
`source` = Facebook Page, `contact` = BOSS INPUT REQUIRED।

Output: উপরের format-এ intake log + checklist — নাম/contact-এ
"BOSS INPUT REQUIRED", booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
ফোন +1 (947) 223-0244। কোনো reply পাঠানো হয়নি, কোনো তথ্য বানানো হয়নি।
