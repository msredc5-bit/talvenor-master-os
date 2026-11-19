# Workflow 1 — Lead Generation

**Department:** 01 Sales & Growth (+ 05 Research & Strategy support)
**তারিখ:** 2026-11-19 | **Status:** LIVE (চলমান) — discovery + verification + qualification হাতে + worker-এ চলে; filing `leads-organized`-এ হয়।

## Purpose (উদ্দেশ্য)

US home-service ব্যবসা (plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet) খুঁজে বের করা, যাচাই করা, score করা, আর `leads-organized`-এ ফাইল করা — যাতে outreach-এ শুধু সেই shop-গুলো যায় যাদের receptionist দরকার বলে মনে হয়।

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Lead Research Agent (`ProspectResearcher`) | 01 | EXISTING — research notes বানায় |
| Google Maps Prospect Finder | 01 | ROLE-ONLY — discovery হাতে হয় |
| Business Verification Agent | 01 | ROLE-ONLY — যাচাই হাতে হয় |
| Lead Scoring Agent | 01 | ROLE-ONLY — scoring হাতে হয় |
| Niche Selection Agent | 05 | ROLE-ONLY |
| Competitor Research Agent | 05 | ROLE-ONLY |

## সত্য অবস্থা (2026-11-19)

- **Lead pool: 507 row** — Tier 1: 2, Tier 2: 505। ফাইল: `~/workspace/talvenor/leads-organized/` (state-wise folder: PA, TX, GA, FL, CA, NC, IL, MI, OH, NY)।
- **প্রথম মেইল 162** — PA 39, TX 15, GA 16, FL 54, CA 14, NC 5, IL 9, MI 5, OH 1, NY 4।
- **Email PAUSED 2026-11-14 থেকে** — নতুন lead-এ মেইল যাচ্ছে না, শুধু discovery/filing চলছে।

## Step-by-step

### ধাপ ১ — Discovery (খোঁজা)

1. **Google Maps / Google Search / directory** থেকে niche + state/city ধরে ব্যবসা খুঁজুন (যেমন: "plumbers in Dallas TX")।
2. **Apify / Places** দিয়ে list টানুন যেখানে সম্ভব — Apify actor-এর output CSV হিসেবে নিন।
3. প্রতিটা ব্যবসার নাম, শহর/state, website, phone নোট করুন। কিছু না পেলে **NOT_FOUND** লিখুন — কখনো বানাবেন না।
4. **Gate:** কোনো gate নেই — research পড়া/খোঁজার কাজ, send/publish নয়।

### ধাপ ২ — Verification (যাচাই)

1. **Website আছে কি?** খুলে দেখুন — সত্যিকারের service business কি না, service area কী, phone number website-এর সাথে মেলে কি না।
2. **Phone:** website/Google-এ দেওয়া number নোট করুন। নিজে থেকে number বানাবেন না।
3. **Contact:** owner-এর নাম / contact email শুধু সেটাই নিন যেটা website বা public listing-এ আছে। Email guess করা যাবে না।
4. **Dental/medical ব্যবসা কখনো target নয়** — দেখলেই DQ (disqualify), list-এ তুলবেন না।
5. **Gate:** কোনো gate নেই — যাচাইয়ের কাজ।

### ধাপ ৩ — Qualification / Scoring (SOP 11-signal scoring)

1. **11-signal** দিয়ে score করুন: website আছে, phone আছে, service area স্পষ্ট, owner/contact পাওয়া যায়, review/presence, receptionist দরকারের signal (যেমন missed-call-এর ইঙ্গিত, "call us" নির্ভরতা) ইত্যাদি।
2. **STRONG / MEDIUM / WEAK** দিন:
   - **STRONG → Tier 1** (সবচেয়ে ভালো — এখন pool-এ মাত্র 2)
   - **MEDIUM → Tier 2** (pool-এর বেশিরভাগ — 505)
   - **WEAK → Tier 4**
3. MEDIUM কখনো Tier 2-এর উপরে যায় না; WEAK Tier 4-এ থাকে।
4. **Gate:** কোনো gate নেই — scoring-এর কাজ।

### ধাপ ৪ — Filing (leads-organized-এ তোলা)

1. State-wise folder-এ সঠিক CSV-তে row যোগ করুন। একই ব্যবসা দুইবার তুলবেন না — আগে খুঁজে দেখুন।
2. প্রতিটা row-তে: business name, city/state, website, phone, contact (যদি পাওয়া যায়), tier, score signal, source, date।
3. **কখনো কোনো row delete করবেন না** — ভুল হলে status column-এ লিখুন (যেমন `dead` / `bounced` / `DQ`), row মুছবেন না।
4. **Gate:** filing-এ gate নেই, কিন্তু outreach-এ যাওয়ার আগে Boss-এর `ok` লাগে (Workflow 2 দেখুন)।

## Honest status

- Discovery + verification + qualification **চলছে, হাতে + `ProspectResearcher`-এর সাহায্যে** — কিন্তু Google Maps Finder, Verification, Scoring-এর কোনো worker code নেই (ROLE-ONLY)।
- Pool 507 row-র মধ্যে Tier 1 মাত্র 2 — বেশিরভাগ Tier 2।
- Dental/medical ব্যবসা কখনো target নয় — সবসময় DQ।

## Missing inputs (যা নেই)

- Google Maps Finder / Verification / Scoring worker — skill `.md` এখনো লেখা হয়নি।
- CRM live নয় (n8n Cloud Data Tables PLANNED) — filing এখন CSV-তেই হয়।
- কোনো lead-এর email/phone guess করা যাবে না — না পেলে NOT_FOUND।
