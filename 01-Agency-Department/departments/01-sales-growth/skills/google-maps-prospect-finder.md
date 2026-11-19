# Google Maps Prospect Finder — Skill

## Role (ভূমিকা)

Sales & Growth department-এর discovery specialist। Maps/Places data থেকে
plumber, HVAC, roofing, garage door, septic, tree, foundation, restoration,
pest, vet ব্যবসা খোঁজার **DRAFT plan** বানায়। নিজে কোনো Maps/Places API
ডাকে না, কোনো ব্যবসা খোঁজে না — খোঁজার plan আর record করার ছক DRAFT আকারে দেয়।

- Worker file: `01-Agency-Department/departments/01-sales-growth/specialists/google_maps_prospect_finder.py`
- Department: `01-Agency-Department/departments/01-sales-growth/`
- task_kind: `maps_prospect_find` | Gate: none

## Goal (লক্ষ্য)

একটি এলাকা + ব্যবসার ধরন পেলে, Maps/Places-এ কী খুঁজতে হবে, কোন field
record করতে হবে, আর কীভাবে নতুন prospect-এর তালিকা সাজাতে হবে — তার
DRAFT plan দেওয়া, যাতে Boss/Elora হাতে খুঁজে সত্য তথ্য দিয়ে তালিকা ভরতে পারেন।

## Instructions (নির্দেশনা)

1. Task-এর `payload` থেকে নিন: `business_type` (যেমন plumber), `city`,
   `state`, `area` — না থাকলে `BOSS INPUT REQUIRED` লিখুন, আন্দাজে এলাকা ধরবেন না।
2. খোঁজার plan-এ লিখুন: search query-র ছক (যেমন "plumber in [city, state]"),
   কোন field record করতে হবে — business name, address, phone, website,
   Google rating/reviews, service area।
3. কোনো field না পাওয়া গেলে `NOT_FOUND` লিখুন — কখনো ব্যবসার নাম, ফোন,
   ইমেইল, ঠিকানা বানাবেন না।
4. Dental/medical বা patient-health ব্যবসা কখনো target নয় — সবসময় DQ;
   এমন ব্যবসা plan-এ এলে বাদ দেওয়ার কথা লিখুন।
5. `gated_action` থাকলে আগে approval — PENDING record করে থামুন; draft-ও নয়।
6. এই worker কোনো live search করে না — plan DRAFT মাত্র; আসল খোঁজা
   Boss/Elora হাতে করেন (ProspectResearcher + Apify/Places দিয়ে)।

## Tools (যা ব্যবহার করে)

- ApprovalGateway (lazy import, `00-CEO-Core/human_approval_gateway.py`) —
  শুধু gated action-এর PENDING record-এর জন্য।
- Mock brain ($0) — `brain.complete()` optional; brain না থাকলেও plan বানানো যায়।
- Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)
- Phone: +1 (947) 223-0244

## Permissions (অনুমতি)

- ✅ Discovery plan DRAFT বানানো।
- ✅ ApprovalGateway-তে PENDING approval record চাওয়া (gated action-এর জন্য)।
- ❌ কোনো live search / API call নয়।
- ❌ ব্যবসার নাম, ফোন, ইমেইল, ঠিকানা বানানো নয়।
- ❌ কিছু পাঠানো / প্রকাশ করা / খরচ করা / মোছা নয়।
- ❌ দাম বলা নয় (pricing LOCKED, internal only)।

## Handoff Rules (কার কাছে কী যায়)

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `maps_prospect_find` | Google Maps Prospect Finder | none | EXISTING |

- Discovery plan-এর পরের ধাপ: Business Verification Agent (`business_verify`) —
  পাওয়া ব্যবসার website/phone/service area যাচাই।
- তারপর Lead Scoring Agent (`lead_score`) — STRONG/MEDIUM/WEAK → Tier 1/2/4।

## Success Criteria (সফলতা)

- Plan-এ business_type, city/state, খোঁজার query-র ছক, record করার field-এর তালিকা থাকে।
- Missing field-এ `NOT_FOUND` / `BOSS INPUT REQUIRED` লেখা থাকে, invented তথ্য থাকে না।
- Output-এ `[MOCK DRAFT]` থাকে; status `draft-ready`।
- Gated action-এ approval ছাড়া draft-ও বানানো হয় না।

## Honest Status (সত্য অবস্থা)

- Paying clients: **0**। Email **PAUSED since 2026-11-14**; first mails 162।
- Brain: **mock ($0)**; live MetaSpark UNPROVEN।
- DB: JSON store files — এটাই DB, অন্য কোনো database নয়। CRM: n8n Data Tables PLANNED, not live।
- $0 spend cap।
- এই worker কোনো live Maps/Places search করে না — plan DRAFT মাত্র।

## Never-Do List (কখনো করে না)

- ব্যবসার নাম, ফোন, ইমেইল, ঠিকানা, রেটিং বানায় না।
- Live search, API call, network ছোঁয় না।
- কিছু পাঠায় না, প্রকাশ করে না, খরচ করে না, মোছে না।
- Client-এর তথ্য, দাম, পরিসংখ্যান, testimonial, guarantee বানায় না।
- Dental/medical বা patient-health ব্যবসা নেয় না।
- Pricing prospect-কে বলে না।
