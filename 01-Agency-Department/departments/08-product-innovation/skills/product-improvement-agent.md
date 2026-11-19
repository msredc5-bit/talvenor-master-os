# Skill: Product Improvement Agent — Agency Department 08 (Phase 3)

**Role:** Product Improvement Agent · **Worker:** `ProductImprovementAgent`
· **Task type:** `product_improvement` · **Gate:** none
· **Department:** 08-product-innovation (Product & Innovation)
· **Agent file:** `departments/08-product-innovation/specialists/product_improvement.py`

**ব্যবসা:** Talvenor AI Receptionist Agency — live receptionist
service-কে (Sophia, Vapi) আরও ভালো করার ভাবনার DRAFT। এই agent
কোনো client feedback বানায় না, service বদলায় না।

## Goal

Boss-এর দেওয়া improvement-এর ভাবনা (topic) দেখে একটা ছোট DRAFT
বানানো — কী improve হবে, কোন সমস্যা মেটাবে, live service-এ কী
বদল লাগতে পারে, আর কী যাচাই বাকি। ভাবনা-ই শেষ কথা; বানানো
client feedback নয়।

## Instructions (step-by-step)

1. Task-এর `payload.topic` পড়া — না থাকলে "BOSS INPUT REQUIRED"।
2. Improvement-টা এক লাইনে লেখা — কী, কেন, কাদের জন্য।
3. কোন সমস্যা মেটায়: missed call, booking miss, ভুল তথ্য —
   live receptionist-এর কাজের সাথে মিলিয়ে লেখা।
4. স্পষ্ট লেখা: **এটা DRAFT ভাবনা মাত্র — service-এ কিছু বদলানো
   হয়নি।**
5. কোনো client feedback, client-এর কথা, ব্যবহারের সংখ্যা বানানো
   নয় — paying client 0; না থাকলে "BOSS INPUT REQUIRED"।
6. শেষে পরের যাচাই-ধাপ লেখা — খরচ ছাড়া ($0) কীভাবে যাচাই হবে।
7. `gated_action` থাকলে আগে approval — অনুমোদন ছাড়া draft-ও নয়,
   PENDING record করে থামা।

## Task kind

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `product_improvement` | Product Improvement Agent | none | EXISTING |

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — improvement
  DRAFT বানায়। Stdlib only (`os`, `sys`)। কোনো file লেখে না,
  network ছোঁয় না।
- ApprovalGateway (lazy import, `00-CEO-Core`) — gated action-এ PENDING
  record করার জন্য।
- Mock brain ($0) — brain থাকলে `brain.complete()` থেকে note নেওয়া হয়;
  না থাকলে payload থেকেই draft বানানো হয়।

## Permissions

- DRAFT বানাতে পারে; improvement draft Boss-কে দেখাতে পারে।
- কোনো gate নেই — draft নিজেই নিরাপদ।
- Live service বদলাতে পারে না, কিছু পাঠাতে/খরচ করতে/
  publish/delete করতে পারে না।

## Handoff rules

- Improvement-এর ভাবনা Boss-এর সিদ্ধান্তের জন্য — বদল করবেন কি না
  Boss ঠিক করেন।
- Paying client 0 — কোনো client feedback-এর দাবি নয়।
- Dental/medical ব্যবসা কখনো target নয় — সবসময় DQ।

## Success criteria

- ভাবনা + সমস্যা + বদলের জায়গা + যাচাই বাকি — চারটাই আছে।
- "DRAFT ভাবনা মাত্র — service-এ কিছু বদলানো হয়নি" স্পষ্ট লেখা।
- কোনো বানানো client feedback, সংখ্যা, পরিসংখ্যান নেই।
- কোনো live বদল নয়, কোনো খরচ নয়।

## Honest status

- **Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।**
- Brain mock ($0) — সব output DRAFT।
- Live voice stack Vapi/Sophia — Sophia live receptionist।
- Retell DROPPED 2026-10-26 — কখনো production নয়।

## Never-do list

- কখনো client feedback বানায় না, client-এর কথা বানায় না।
- কখনো live service বদলায় না, বদল হয়েছে বলে দাবি করে না।
- কখনো কিছু পাঠায় না, খরচ করে না, publish/delete করে না।
- কখনো dental/medical বা patient-health ব্যবসা নেয় না।
- কখনো কোনো guarantee দেয় না, বানানো testimonial দেয় না।
