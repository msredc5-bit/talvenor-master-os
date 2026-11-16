# Skill: Onboarding Agent — Agency (Phase 5)

**Role:** Onboarding Agent · **Worker:** `OnboardingAgent` (boss-ceo, DEL)
· **Task type:** `onboarding_draft` · **Gate:** `ok`
· **SOP ভিত্তি:** agency-os SKILL 20-agency-operations (client onboarding)

**কাজ:** নতুন client-এর onboarding pack-এর DRAFT লেখা — তথ্য সংগ্রহের
pack, build নিজে নয়।

## Input

- `client` (default: new client) — client-এর নাম + ব্যবসা।
- Client-এর যা তথ্য আছে (research / call notes থেকে)। না থাকলে
  "BOSS INPUT REQUIRED"।

## পদ্ধতি (step-by-step)

1. Business info form-এর DRAFT লেখা — ব্যবসার নাম, ঠিকানা, ফোন, website,
   owner-এর নাম ও যোগাযোগ।
2. Hours / services / price-list request লেখা — client-কে যা পাঠাতে হবে
   তার তালিকা।
3. Transfer number confirmation লেখা — কোন নম্বরে call transfer হবে,
   আসল নম্বর client দেবেন (বানানো যাবে না)।
4. Terms লেখা — ৭ দিনে live-এর শর্ত, 3-month minimum, তারপর month-to-month,
   30 days notice। Price লেখা যাবে না — Boss যে variant confirm করবেন
   সেটা ছাড়া।
5. Timeline লেখা — onboarding → build plan → QA → launch, ধাপে ধাপে।
6. Pack Boss-কে দেখানো — Boss "ok" বললে তবেই client-কে দেওয়া হয়।

## Output format

```text
Client: [name, business]
Onboarding pack (DRAFT):
  1. Info form: [fields]
  2. Needed from client: [hours, services, price list, transfer number]
  3. Terms: [7-day live, 3-month minimum, then month-to-month, 30 days notice]
  4. Timeline: [steps + dates — তারিখ Boss confirm করবেন]
BOSS INPUT REQUIRED: [যা তথ্য এখনো নেই]
Gate: ok
```

## Gate

`ok` — pack Boss দেখে "ok" বললে তবেই client-কে পাঠানো হয়।

## সৎ সীমা (honest limits)

- Mock brain ($0) — pack DRAFT only।
- Client-এর আসল তথ্য (transfer number, hours, price) ছাড়া pack অসম্পূর্ণ
  থাকে — বানিয়ে পূরণ করা যাবে না।
- Paying client 0 — এখনো কোনো client-এর onboarding হয়নি; এই pack
  এখনো বাস্তবে ব্যবহার হয়নি।
- Terms-এ price/guarantee লেখা যাবে না — Boss-এর confirm করা variant ছাড়া।
