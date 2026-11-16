# Skill: Scheduler — Agency (Phase 5)

**Role:** Scheduler · **Worker:** `SchedulerAssistant` (boss-ceo, OPS)
· **Task type:** `schedule_help` · **Gate:** None
· **SOP ভিত্তি:** agency-os SKILL 20-agency-operations

**কাজ:** Scheduling-এ সাহায্য — slot প্রস্তাব + invite draft। Boss
confirm করার আগে কিছু পাঠানো হয় না।

## Input

- `what` (default: client demo call) — কীসের জন্য schedule।
- Boss-এর availability (না থাকলে "BOSS INPUT REQUIRED")।

## পদ্ধতি (step-by-step)

1. কী schedule করতে হবে ঠিক করা (demo call / onboarding call / follow-up)।
2. ৩টা slot প্রস্তাব করা — Asia/Dhaka সময় + US-Eastern equivalent সহ।
3. Invite-এর draft লেখা — short, plain: কী, কখন, কোথায় (booking link:
   https://calendar.app.google/WLoxBfnLGTdjK3LB8 — Talvenor Demo,
   15 min, New York Time)।
4. Boss-কে দেখানো — Boss confirm করলে তবেই invite যায় (Boss নিজে পাঠান)।

## Output format

```text
What: [client demo call]
Slots (Asia/Dhaka + US-Eastern):
  1. [Dhaka time] = [US-Eastern time]
  2. ...
  3. ...
Draft invite:
[short text + booking link]
Gate: None (invite পাঠাতে Boss-এর confirm লাগে — আলাদা সিদ্ধান্ত)
```

## Gate

কোনো gate নেই — slot + draft নিজেই নিরাপদ। Invite পাঠানো Boss-এর
confirm ছাড়া হয় না।

## সৎ সীমা (honest limits)

- Mock brain ($0) — slot + draft DRAFT only।
- Boss-এর calendar না দেখে slot "free" দাবি করা যাবে না — প্রস্তাব
  মাত্র, confirm Boss করবেন।
- Booking link-এর সময় New York Time — ভুল timezone-এ invite লেখা যাবে না।
