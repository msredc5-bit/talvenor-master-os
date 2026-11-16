# Skill: Kit Sales (NEW)

**Role (ভূমিকা):** যাচাই করা PA clinic-দের জন্য Vet Kit outreach email-এর DRAFT লেখা — শুধু DRAFT, পাঠানো নয়।
**Agent:** `sections/sales/agents/kit_sales.py` — `KitSalesAgent` (task kind `kit_sales`, section `sales`)
**Status: DRAFTS ONLY** — Gate 0 NOT PASSED, email channel PAUSED (2026-11-14 থেকে)। প্রতিটা output-এ prominent warning থাকে: "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go"।

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (প্রথম ৩০ buyer-এর জন্য launch price **$39**)। Format: Google Sheets + Google Docs + copy-paste script।
- **কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet। Corporate chain নয়, solo mobile vet নয়।
- **Pain (VERIFIED):** no-show rate **~11%** (AAHA) × গড় vet visit **~$200** (AVMA 2025) ≈ **~$50k–$150k/yr** ঝুঁকিতে থাকে একটা সাধারণ clinic-এর (labeled estimate)। US-এ **34,296** vet practice (Census 2023)।
- **Contact (real facts):** booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (Talvenor Demo, 15 min, New York Time); phone +1 (947) 223-0244; main email contact@talvenorai.agency।
- **Price flag:** $49 কোনো verified sale থেকে আসেনি — inference। Prospect-কে $49 quote করা যাবে না Boss confirm না করলে।

## Inputs

- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` (39 verified row, read-only) — শুধু এই list-এর clinic-দের জন্য draft।
- `02-Digital-Product-Department/kit-outline.md` — kit-এর ৬ অংশের নাম + pain arithmetic (draft-এর ভিত্তি)।
- Task payload-এ `clinic_name` (optional) — CSV-তে মিললে তবেই addressed draft; না মিললে generic template।
- Gate 0 status: `gate0-status.md` — এখন NOT PASSED।

## Step-by-step method

1. **Clinic যাচাই:** payload-এ `clinic_name` থাকলে CSV-তে খোঁজা। মিললে public email দেখা — email "Not publicly listed" হলে addressed email draft লেখা যাবে না (contact details বানানো যাবে না)।
2. **Clinic না বলা থাকলে:** CSV-এর প্রথম emailable row (public email আছে) ব্যবহার করা — এখন সেটা Indy Veterinary Care, Philadelphia (info@indyvetcare.com)।
3. **Draft লেখা (plain US English):** subject + body — pain (AAHA 11% × AVMA ~$200), kit-এর ৬ অংশের নাম, CTA (booking link + phone)। Price জায়গায় placeholder: "[Price — Boss confirms before sending. Do NOT quote a price to a prospect without Boss confirming.]" — $49 লেখা হয় না।
4. **Warning লাগানো:** output-এর মাথায় prominent "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go" + "Email channel PAUSED"।
5. **কোনো clinic-কে দুইবার মেইল করা যাবে না** (launch-এর সময়) — note-এ লেখা থাকে।

## Output format

- Warning + addressed draft (To: verified clinic, city, public email, source_url) অথবা generic template (placeholders সহ)।
- Status: `draft-ready` (draft-এর জন্য); `mark_sold` চাইলে `blocked-gate0`।
- Draft-এর মাথায় লেখা থাকবে: DRAFT ONLY — পাঠানো হয়নি।

## Tools used (টুল)

- Read-only file read: `pa-vet-list/pa-vet-clinics.csv` (verified clinic + public email + source_url)।
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — draft লেখায়, live call নয়।
- Gated কাজে ApprovalGateway (PENDING record) — `send` চাইলে worker চালানো হয় না, PENDING-এ আটকায়।
- কোনো live tool, network, বা file write নয়। মেইল পাঠানো এই skill-এর কাজ নয়।

## Gate

- পাঠাতে Boss-এর `send` লাগে — exact word ছাড়া কিছু পাঠানো হয় না।
- Email channel এখন PAUSED — SPF/DMARC DNS fix Boss-এর হাতে বাকি (2026-11-14 থেকে)।

## Honest limits

- **Gate 0 NOT PASSED** — kit বানানো হয়নি (0/6), sale 0। Draft launch-এর পরে ব্যবহারের জন্য।
- **PAUSED email** — draft লেখা যায়, পাঠানো যায় না।
- PA list 39/100 — 39-এর মধ্যে public email আছে 8টার; বাকিদের addressed email draft লেখা যায় না।
- কোনো clinic-র সাথে Talvenor-এর কোনো সম্পর্ক/চুক্তি নেই — এটা শুধু public তথ্যের list।
- $49 price unproven — কোনো verified sale নেই।

## যা কখনো করে না

- মেইল পাঠায় না; sale হিসেবে কিছু চিহ্নিত করে না।
- Prospect-কে $49 quote করে না Boss confirm না করলে।
- Contact details বানায় না; CSV-এর বাইরে কাউকে draft লেখে না; কোনো file লেখে না।
- কোনো client/testimonial/statistic বানায় না।

## Worked example (আসল repo fact দিয়ে)

- **Task:** `{"type": "kit_sales", "title": "Outreach draft", "payload": {"clinic_name": "Indy Veterinary Care"}}` → `KitSalesAgent.run()`।
- **Agent করে:** CSV-তে খোঁজে — Indy Veterinary Care, Philadelphia, public email info@indyvetcare.com, phone (215) 923-2300, source https://indyvetcare.com/ — verified (README spot-check)।
- **ফলাফল:** status `draft-ready`; output-এর মাথায় "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go" warning; তারপর addressed email DRAFT (subject "Missed appointments — a simple fix for Indy Veterinary Care?", pain AAHA 11% × AVMA ~$200, ৬ অংশের নাম, CTA booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 + phone +1 (947) 223-0244, price জায়গায় placeholder — $49 লেখা নেই)। পাঠানো হয়নি।
