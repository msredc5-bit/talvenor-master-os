# Skill: Kit Builder

**Role:** Vet No-Show Recovery Kit-এর ৬ অংশ বানানো — blueprint থেকে আসল kit।
**Status: BLOCKED** — Gate 0 NOT PASSED। এখন শুধু blueprint পড়া যায়, kit
বানানো যাবে না।

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (প্রথম ৩০ buyer-এর
  জন্য launch price **$39**, তারপর $49)। Format: Google Sheets + Google Docs
  + copy-paste script। কোড নেই, app নেই, install করতে হয় না।
- **কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet, buyer =
  front-desk / practice manager। Corporate chain নয়, solo mobile vet নয়।
- **Pain (VERIFIED):** no-show rate **~11%** (AAHA) × গড় vet visit **~$200**
  (AVMA 2025) ≈ **~$50k–$150k/yr** ঝুঁকিতে থাকে একটা সাধারণ clinic-এর
  (labeled estimate — ২৫ appointment/day × 11% × 250 দিন)। US-এ **34,296**
  vet practice (Census 2023)। আসল উদাহরণ: PAWS Clinic, 2025-এ 904 no-show
  (clinic Facebook post, 15 Jan 2026)।
- **Price flag:** $49 কোনো verified sale থেকে আসেনি — পাশের product-এর
  anchor ($49 Room Intake + Rounding SOP Pack) থেকে inference। Gate 2-এ
  test হবে।

## Inputs

- `02-Digital-Product-Department/kit-outline.md` — blueprint (একমাত্র উৎস)
- Research report `~/workspace/research_notes/digital-product-final-20261112/report.md` §4.1 (৬ অংশের exact বিবরণ), §4.2 (pain arithmetic)
- Gate 1 যাচাই: AAHA/PetDesk published guidance (cadence + script মেলাতে হবে)
- Gate 0 status: `gate0-status.md` — "Status: PASSED" না থাকলে build শুরু নয়

## ৬ অংশ — step-by-step method (Gate 0-র পরে, Week 2, দিনে ১ ঘণ্টা, $0)

### ১. Reminder Cadence Pack (Docs + script)
1. T-72h / T-24h / T-2h — SMS + email + phone-call script, copy-paste।
2. প্রতিটা script-এ [NAME] / [PET] / [TIME] field রাখতে হবে।
3. **Gate 1:** cadence + script AAHA/PetDesk-এর published guidance-এর সাথে
   মেলাতে হবে। মিল না হলে ঠিক করতে হবে; তাও না মিললে KILL বা re-scope।

### ২. Same-Day Rebooking Scripts (Docs)
1. Client no-show করলে বা late cancel করলে front desk কী বলবে — যাতে
   slot-টা সেদিনই আবার ভরে যায়।
2. Phone script + in-person script, দুটোই plain US English।

### ৩. Waitlist-Fill SOP (Docs, এক পাতা)
1. Slot খালি হলে কাকে আগে ফোন করবে, কোন order-এ — exact call script সহ।
2. এক পাতার procedure — front desk-এ লাগানো যায়।

### ৪. No-Show Log + $ Tracker (Sheets)
1. প্রতিটা no-show log করবে; formula auto-total করবে: এই মাসে কত
   appointment miss হলো, আনুমানিক কত $ হারালো, recovery rate কত।
2. Sample সংখ্যা দিয়ে formula test করতে হবে (build-এর সময়)।
3. **এই $ figure-টাই আসল point:** clinic নিজের চোখে loss-টা দেখবে।

### ৫. Deposit / No-Show Policy Template (Docs)
1. Clinic adopt করতে পারে এমন plain-words policy template।
2. লেখা থাকবে: **"have your own attorney review before using"** — এটা
   legal advice নয়, Elora কখনো এটাকে legal advice হিসেবে দেবে না।

### ৬. Front-Desk Quick Card (Docs, এক পাতা)
1. ৫ লাইন — যেগুলো মানলে বেশিরভাগ no-show ঠেকে।
2. Reception desk-এ রাখার মতো এক পাতা।

### শেষ ধাপ
- পুরো kit একবার read-through — ভুল, বানানো clinical wording, ভুল
  Talvenor বানান আছে কি না দেখা।
- PIMS replace করার দাবি করা যাবে না — kit PIMS-এর পাশে কাজ করে (76.5%
  practice ইতিমধ্যে PIMS ব্যবহার করে — AVMA 2025)।

## Output format

- ৬ অংশের DRAFT (Sheets/Docs link বা file) + এক পাতার build note: কোন অংশে
  কী আছে, Gate 1 যাচাই পাস কি না, sample test-এর ফলাফল।
- Output-এর মাথায় লেখা থাকবে: DRAFT / READY / TESTING / LIVE-এর মধ্যে
  আসল status — কখনো বানানো status নয়।

## Gate

- Build শুরু করতে Boss-এর `ok` লাগে।
- Gate 0 পাস না হওয়া পর্যন্ত কোনো অংশ বানানো যাবে না — Chief-এর
  `kit_build` শুধু blueprint ফেরত দেয়।

## Honest limits

- **Gate 0 BLOCKED:** kit-এর কোনো অংশ এখনো বানানো হয়নি — শুধু blueprint
  আছে। Build order Week 2 (Gate 0-র পরে)।
- Cadence-এর vet accuracy (Gate 1) এখনো যাচাই হয়নি — AAHA/PetDesk source
  পড়া বাকি।
- $49 price unproven — কোনো verified sale নেই। $10K/mo verdict: kit একা
  ৬–১২ মাসে দেবে না; credible $300–$1,000/mo (৬–২০ sale/mo), Gate 2 পাস
  করলে। Wedge (১/২০ buyer → $1,109/mo receptionist) UNTESTED।
- Dental/medical (patient-health) কখনো target নয় — এটা animal care।
- **BOSS INPUT REQUIRED:** Gate 0-র ফলাফল (Lemon Squeezy test) — Boss
  ছাড়া কেউ দিতে পারে না।
