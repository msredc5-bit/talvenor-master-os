# BUSINESS-02 — E-commerce & Digital Product OS (Commerce Wrapper)

**তারিখ:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, Boss-এর review-এর জন্য
**Source:** Boss-এর পাঠানো brief `~/workspace/briefs/unified-business-os-2026-11-19.md` §3 (as-is সংরক্ষিত, design হিসেবে adopt করা হয়নি — নিচে audit করা হয়েছে)
**Points at:** `02-Digital-Product-Department/` (আসল digital-product কাজ) + dropshipping research file
**এই ফাইলের নিয়ম:** শুধু wrapper — নতুন code নয়, নতুন store নয়, কিছু live নয়। Brief-এর ৫টি division-কে সৎ status দিয়ে লেখা হয়েছে; যা live বলে দাবি করা হয়েছিল তার বেশিরভাগই live নয়।

## Brief-এর audit (যা ভুল ছিল, ঠিক করা হয়েছে)

| Brief-এ যা ছিল | সত্য অবস্থা |
|---|---|
| Commerce-র নিজস্ব "Commerce Brain" | **ভুল।** তিন ব্যবসার আলাদা live brain নেই। **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN। Products Chief আছেন, আলাদা live brain নয়। |
| ৫টি division-এর Specialist Agent-রা (প্রতিটি division-এ ৭–১১ জন agent) | **বানানো হয়নি।** কোনো division-এ agent worker নেই — শুধু Vet Kit-এর blueprint + research ফাইল আছে। |
| Amazon / Shopify / Etsy — চালু division হিসেবে | **ভুল।** নিচের table দেখুন — Amazon GATED, Shopify PARKED (Boss-এর direct project), Etsy CLOSED। |
| Brief-এর ৩টি ছবি (external diagram) | **ব্যবহার করা হয়নি** — external diagram, এই wrapper-এ reference-ও নেই। |

## ৫টি Division — সৎ Status

| Division | Status | যা আসল (What is real) | Next step |
|---|---|---|---|
| Amazon | **GATED** | কিছু নেই — কোনো account নেই, কোনো store নেই, কোনো worker নেই। | ৫টি live client + $5K MRR হলে তবেই খোলা যাবে। তার আগে কিছু বানানো হবে না। |
| Shopify | **PARKED — Boss-এর direct project** | Store draft only (2026-10-21-এ খোলা single-product dropshipping project)। Agent-run division নয় — Boss নিজে চালান। | Boss-এর সিদ্ধান্তে — agent-রা এতে হাত দেয় না। |
| Etsy | **CLOSED** | কিছু নেই — Bangladesh থেকে Etsy বন্ধ (verified 2026-11-12)। | কখনো live হিসেবে বানানো হবে না। Etsy-তে list করা যাবে না। |
| Dropshipping | **RESEARCH-ONLY** | Research ফাইল মাত্র: `~/workspace/research_notes/dropshipping-product-intelligence-2026-10-27.md` (MODE E report, 2026-10-27)। কোনো store বানানো হয়নি, কোনো supplier contact হয়নি, কোনো spend হয়নি। | নিচে research-এর সারাংশ দেখুন — validation ছাড়া এগোনো নয়। |
| Digital Products | **BLOCKED on Gate 0** | Vet No-Show Recovery Kit $49 — **blueprint মাত্র** (`02-Digital-Product-Department/kit-outline.md`, ৬ অংশ, ০/৬ বানানো)। PA vet list 39/100। Sale 0। | Gate 0 — Lemon Squeezy signup test (Boss-এর ~15-min step)। নিচে দেখুন। |

## Dropshipping — research ফাইলে আসলে যা আছে (এর বেশি কিছু নয়)

Source: `~/workspace/research_notes/dropshipping-product-intelligence-2026-10-27.md` — শুধু এই ফাইলে যা লেখা আছে তাই; এর বাইরে কোনো product/price যোগ করা হয়নি।

- **Scope:** USA, Shopify dropshipping; 30 candidate review করা হয়েছে, 10 shortlist।
- **Top score:** Cat water fountain 84, electric spin scrubber 82, deshedding brush 81, cordless car vacuum 80, rechargeable motion-sensor lights 80।
- **Best low-budget candidate:** Lick mat / slow feeder (সবচেয়ে সস্তা sample, হালকা, ভাঙে না)।
- **Best evergreen candidate:** Modular drawer organisers।
- **Validation plan (ফাইলের নিজের কথা):** sample order + organic video আগে; live supplier quote + sample pass ছাড়া paid ad নয়, inventory কেনা নয়, delivery date promise নয়।
- **সীমা (ফাইলের নিজের স্বীকারোক্তি):** কোনো live marketplace/supplier data টানা হয়নি — Amazon, AliExpress, CJdropshipping, TikTok Creative Center, Meta Ad Library primary source হিসেবে access করা হয়নি; evidence second-hand roundup থেকে। কোনো sales volume, conversion rate, ad cost, বা supplier price fact হিসেবে claim করা হয়নি। Score মানে "validate first", "will sell" নয়।
- **কী নেই:** কোনো store, কোনো supplier quote, কোনো sample order, কোনো spend — কিছুই হয়নি।

## Digital Products — Vet No-Show Recovery Kit $49 (আসল product track)

Source: `02-Digital-Product-Department/kit-outline.md` + `gate0-status.md` (**Status line: NOT PASSED, 2026-11-16** — fail-closed)।

- **Kit:** $49 one-time (প্রথম ৩০ buyer-এর জন্য launch price $39, তারপর $49)। Format: Google Sheets + Google Docs + copy-paste script। কোড নেই, app নেই।
- **কার জন্য:** Independent US vet clinic, ১–৫ vet, buyer = front-desk / practice manager। Corporate chain নয়, solo mobile vet নয়।
- **৬ অংশ (০/৬ বানানো):** (1) Reminder Cadence Pack, (2) Same-Day Rebooking Scripts, (3) Waitlist-Fill SOP, (4) No-Show Log + $ Tracker, (5) Deposit / No-Show Policy Template (attorney-review note সহ — legal advice নয়), (6) Front-Desk Quick Card।
- **PA list:** 39/100 (যাচাই করা)।
- **Sale:** 0। Launch হয়নি।
- **$10K/mo verdict (সৎ):** kit একা ৬–১২ মাসে $10K/mo দেবে না। Credible: $300–$1,000/mo (৬–২০ sale/mo), Gate 2 পাস করলে। $10K/mo-র একমাত্র পথ wedge (২০ buyer-এর ১ জন $1,109/mo receptionist নিলে) — **UNTESTED**।

### Gate 0 — BLOCKED (Boss-এর step বাকি)

- **Gate 0 কী:** Lemon Squeezy-তে Bangladesh থেকে individual হিসেবে signup + payout হয় কি না — আগে test, তারপর build।
- **Boss-এর step (~15 min, $0):** lemonsqueezy.com-এ individual হিসেবে signup (MAINUDDIN LLC নয়), payout method দেখুন, ফলাফল জানান।
- **ফেল হলে:** Backup rail test — **Polar** (BD seller/payout list-এ আছে)। Polar-ও না হলে **Gumroad** (BD bank payout আছে, **individual হিসেবে** register করতে হবে — LLC নয়)।
- **সব rail বন্ধ হলে:** Product track পুরো **KILL** — kit বানানো হবে না।
- **Gate 0-র পরে (যদি পাস হয়):** PA list 100-এ পূর্ণ করা, Gate 1 (cadence AAHA/PetDesk যাচাই), kit-এর ৬ অংশ বানানো, store listing, launch।

## ৭টি Shared Department — আসল / Planned-এ Map

Brief §3-এর shared department-গুলো — কোনোটাই আলাদা live department নয়; নিচে আসল জিনিসের সাথে map করা হয়েছে।

| Shared Department (brief) | আসল Map | Status |
|---|---|---|
| Product Research HQ | Dropshipping research ফাইল (2026-10-27) + digital-product research report (2026-11-12, `~/workspace/research_notes/digital-product-final-20261112/report.md`) | RESEARCH-ONLY — ফাইল আছে, worker নেই |
| Marketing HQ | Agency Marketing dept (01-Agency-Department, dept 02) — internal project হিসেবে সার্ভ করে | EXISTING (Agency-র ভেতরে) — Commerce-র আলাদা marketing team নেই |
| Creative Production | Content dept (03-Content-Creation-Department) — internal project হিসেবে সার্ভ করে | EXISTING (Content-এর ভেতরে) — Commerce-র আলাদা creative team নেই |
| Customer Experience | Client Operations dept (01-Agency-Department, dept 04) | EXISTING — কিন্তু client 0, তাই সার্ভ করার মতো customer নেই |
| Finance HQ | CFO manager (Agency dept 06) + LOCKED pricing; revenue $0 | BUILT — track করার মতো revenue নেই |
| Analytics HQ | `dashboards/status.html` + ReportCompiler (visible metrics only — যা দেখা যায় তাই, কখনো estimate নয়) | BUILT — metric 0 (sale 0, store 0) |
| Compliance & Risk | Phase 1 governance + platform rules (নিচে দেখুন) | BUILT (নিয়ম হিসেবে) — enforce করার মতো live operation নেই |

## Compliance & Risk — Platform Rules (LOCKED)

- **Etsy CLOSED** (Bangladesh; verified 2026-11-12) — কখনো live হিসেবে বানানো হবে না, Etsy-তে list করা যাবে না।
- **Amazon GATED** — ৫টি live client + $5K MRR না হওয়া পর্যন্ত কিছু বানানো হবে না।
- **Shopify PARKED** — Boss-এর direct project; agent-রা store-এ হাত দেয় না।
- **কোনো agent listing / pricing / refund / account-sensitive কাজ Boss-এর approval ছাড়া করে না।**
- **Dental/medical কখনো target নয়** — সবসময় DQ।
- **কোনো invented sale, price, stat, testimonial নয়।** $49 price-এর কোনো verified sale আছে বলে দাবি করা যাবে না।

## সত্য অবস্থা (Real Status Block — 2026-11-19)

| জিনিস | অবস্থা |
|---|---|
| Amazon | GATED — account 0, store 0, worker 0 |
| Shopify | PARKED — Boss-এর direct project, store draft only |
| Etsy | CLOSED — Bangladesh, verified 2026-11-12 |
| Dropshipping | RESEARCH-ONLY — ফাইল আছে, store 0, spend $0 |
| Digital Products (Vet Kit) | BLOCKED on Gate 0 — blueprint আছে, kit 0/6, PA list 39/100, sale 0 |
| Revenue (Commerce) | $0 |
| Spend cap | $0 |
| Brain | ONE brain (mock, $0) — আলাদা Commerce Brain নেই |

## পরের ধাপ (Boss-এর সিদ্ধান্তে)

1. **Gate 0 test** — Lemon Squeezy signup (Boss-এর ~15-min step)। এটাই Commerce track-এর একমাত্র খোলা দরজা।
2. Gate 0 পাস হলে: PA list 100-এ পূর্ণ করা → Gate 1 → kit build → listing → launch (100 মেইল)।
3. Gate 0 ফেল হলে: Polar test → Gumroad test → সব বন্ধ হলে track KILL।
4. Amazon/Shopify/Etsy — Boss নতুন করে না বললে কিছু করা হবে না।

## যা এই wrapper করে না

- কোনো store বানায় না, কোনো listing করে না, কোনো supplier-কে contact করে না।
- কোনো দাম/অফার prospect-কে জানায় না, কোনো sale-র দাবি করে না।
- Etsy-কে live হিসেবে দেখায় না, Amazon-কে live হিসেবে দেখায় না।
