# Skill: Launch Manager

**Role (ভূমিকা):** Vet Kit launch-এর checklist বানানো (DRAFT only) — Gate 0, kit-এর ৬ অংশ, Gate 1 যাচাই, store listing, sales page, 100 clinic-কে মেইল, reply + sale sheet-এ লেখা।
**Agent:** `sections/launch/agents/launch_manager.py` — `LaunchManagerAgent` (task kind `launch_prep`, section `launch`)
**Status: BLOCKED** — Gate 0 NOT PASSED। Launch করা যাবে না; শুধু DRAFT checklist।

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (প্রথম ৩০ buyer-এর জন্য launch price **$39**)। Format: Google Sheets + Google Docs + copy-paste script।
- **কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet। Corporate chain নয়, solo mobile vet নয়।
- **Launch plan (kit-outline.md Week 0–4):** Week 0 Gate 0 → Week 1 validate + PA list 100 → Week 2 kit build → Week 3 store + sales page → Week 4 launch (দিনে ২৫ মেইল, 100 clinic-কে, ৪ দিন)।
- **Gate 2 (kill criteria):** 100 মেইলে ≥2% reply rate AND ≥1 sale — 100 মেইলে 0 reply হলে email বন্ধ, vet Facebook group ২ সপ্তাহ; তাও 0 হলে KILL।

## Inputs

- `02-Digital-Product-Department/kit-outline.md` (Week 0–4 build plan + Gate 0–3 kill criteria)
- `02-Digital-Product-Department/gate0-status.md` (একমাত্র সত্য উৎস — "Status: PASSED" না থাকলে NOT PASSED)
- PA list-এর অবস্থা: 39/100 (`pa-vet-list/pa-vet-clinics.csv`)

## Step-by-step method (checklist DRAFT)

1. **Gate 0 পাস** (Lemon Squeezy store খোলে কি না) — এখনো NOT PASSED।
2. **Kit-এর ৬ অংশ বানানো** (Sheets + Docs + script) — এখনো হয়নি (0/6)।
3. **Cadence AAHA/PetDesk guidance-এর সাথে যাচাই (Gate 1)** — এখনো হয়নি।
4. **Lemon Squeezy listing + Gumroad backup listing** — এখনো হয়নি।
5. **Sales page** — Boss review করবেন launch-এর আগে।
6. **100 clinic-কে ২৫টা করে মেইল (৪ দিন)** — email channel এখন PAUSED (2026-11-14 থেকে)।
7. **প্রতিটা reply + sale sheet-এ লেখা** — sale এখনো 0।

## Output format

- Launch checklist DRAFT (৭ ধাপ) + Gate 0 অবস্থা + kit 0/6 + PA 39/100 + sale 0।
- Status: Gate 0 পাস না হওয়া পর্যন্ত `blocked-gate0` — launch করা হয়নি, করা যাবে না।

## Tools used (টুল)

- Read-only file read: `kit-outline.md`, `gate0-status.md`, `pa-vet-list/pa-vet-clinics.csv`।
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — checklist DRAFT লেখায়, live call নয়।
- Gated কাজে ApprovalGateway (PENDING record)।
- কোনো live tool, network, বা file write নয়। মেইল পাঠানো এই skill-এর কাজ নয়।

## Gate

- Launch এগোতে Boss-এর `go` লাগে।
- Gate 0 পাস না হওয়া পর্যন্ত launch করা যাবে না — agent শুধু DRAFT checklist দেয়; `mark_launched` চাইলে status `blocked-gate0` ফেরত আসে, কিছুই launch হিসেবে লেখা হয় না।

## Honest limits

- **Gate 0 BLOCKED** — launch হয়নি। Email PAUSED — 100 clinic-কে মেইল এখনো শুরু হয়নি।
- Kit 0/6, PA list 39/100, sale 0।
- $10K/mo verdict: kit একা ৬–১২ মাসে দেবে না; credible $300–$1,000/mo (৬–২০ sale/mo), Gate 2 পাস করলে। Wedge (১/২০ buyer → $1,109/mo receptionist) UNTESTED।

## যা কখনো করে না

- Launch করে না; mark_launched / mark_sold মানে না; sale লেখে না।
- মেইল পাঠায় না; কোনো file লেখে না; client/testimonial/statistic বানায় না।

## Worked example (আসল repo fact দিয়ে)

- **Task:** `{"type": "launch_prep", "title": "Launch checklist"}` → `LaunchManagerAgent.run()`।
- **Agent করে:** `gate0-status.md` পড়ে — Status NOT PASSED; checklist-এর ৭ ধাপ লেখে (Gate 0, ৬ অংশ, Gate 1, দুটো listing, sales page, ২৫×৪ মেইল, reply/sale sheet)।
- **ফলাফল:** status `blocked-gate0`; output-এ DRAFT checklist + "Gate 0: NOT PASSED। Kit বানানো: 0/6। PA list: 39/100। Sale: 0।" Launch করা হয়নি।
