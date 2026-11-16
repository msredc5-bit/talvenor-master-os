# Skill: Client Success Agent — Agency (Phase 7)

**Role:** Client Success Agent · **Worker:** `ClientSuccessAgent` (Phase 7, delivery section)
· **Task type:** `client_success` · **Gate:** `send`
· **SOP ভিত্তি:** agency-os SKILL 20-agency-operations (client success / retention)

**ব্যবসা:** Talvenor AI Receptionist — paying client-এর check-in draft +
renewal-reminder draft। কখনো পাঠানো নয়।

## Input

- `client`: client-এর নাম (paying client হলে, Boss-এর কথায়; না থাকলে
  BOSS INPUT REQUIRED — paying client 0, 2026-11-16)।
- `kind`: `check-in` (default) বা `renewal`।

## পদ্ধতি (step-by-step)

1. Client confirm করা — আসল paying client না থাকলে draft TEMPLATE only,
   কাউকে পাঠানোর মতো করে লেখা যাবে না।
2. Check-in draft লেখা — short, plain US English, একটা CTA (15-min call —
   booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8)।
   Renewal-reminder draft একইভাবে, renewal তারিখ না থাকলে BOSS INPUT REQUIRED।
3. Check করা: কোনো price নেই, কোনো guarantee নেই, কোনো বানানো client /
   testimonial / statistic / ফলাফল নেই।
4. Draft Boss-কে দেখানো — পাঠানো নয়। পাঠানো Boss নিজে করেন, "send" বললে।

## Output format

```text
[MOCK DRAFT] Client Success — DRAFT ONLY
Client: [client] | Kind: [check-in | renewal]
Honest note: paying clients = 0 (2026-11-16). If no real client is named, this draft is a TEMPLATE only.
Check-in draft: "[Hi — quick check-in. Is the receptionist catching every call the way you wanted? ... Book here: https://calendar.app.google/WLoxBfnLGTdjK3LB8]"
Renewal-reminder draft: "[Hi — your receptionist plan renews soon. Want to keep the same setup, or change anything first? ... Book here: https://calendar.app.google/WLoxBfnLGTdjK3LB8]"
Phone: +1 (947) 223-0244
---
Gate: send — Boss-এর exact শব্দ ছাড়া পাঠানো যাবে না।
```

## Gate

`send` — Boss-এর exact শব্দ লাগে, আর পাঠানোর কাজ Boss নিজে করেন
(main chat থেকে)। এই system শুধু DRAFT বানায়।

## সৎ সীমা (honest limits)

- **Paying client 0 (2026-11-16)** — client তথ্য না থাকলে "BOSS INPUT
  REQUIRED"; কোনো client-এর নাম/ফলাফল বানানো হয় না। Client ছাড়া draft
  TEMPLATE only — কাউকে পাঠানো যাবে না।
- Mock brain ($0) — output DRAFT। কোনো price, guarantee, testimonial নেই।
- Dental/medical/patient-health কখনো নয়।

## Worked example (আসল তথ্য দিয়ে)

Input: `client` = BOSS INPUT REQUIRED, `kind` = check-in।

Output: উপরের format-এ check-in + renewal draft — Client:
BOSS INPUT REQUIRED, honest note: paying clients = 0, draft TEMPLATE only।
Booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
ফোন +1 (947) 223-0244। কাউকে পাঠানো হয়নি, কোনো client বানানো হয়নি।
