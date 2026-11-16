# Skill: Clinic Researcher

**Role:** PA vet list-কে ১০০টি যাচাই করা independent clinic-এর দিকে বাড়ানো।
**Status: REAL work, 39/100** (2026-11-16, যাচাই করা) — বাকি 61 Gate 0-র
পরে পূর্ণ করা হবে।

## Target (locked facts)

- **লক্ষ্য:** 100 independent vet clinic, Pennsylvania (এক state দিয়ে শুরু)।
- **এখন আছে:** 39 clinic — লক্ষ্যের 39%। বাকি 61।
- **কার জন্য:** Independent companion-animal vet clinic, ১–৫ vet। Corporate
  chain নয় (ওদের central system আছে), solo mobile vet নয় (খুব ছোট)।
- **শহর ভাগ (39):** Philadelphia 8, York 5, Lancaster 4, Allentown /
  Bethlehem 4, Pittsburgh / Monroeville 3, Erie 3, Scranton / Wilkes-Barre 3,
  State College 3, Harrisburg 2, Norristown 2, Reading 1, Altoona 1।

## Inputs

- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` (39 row —
  source, কখনো overwrite নয়, শুধু যাচাই করা row যোগ করা)
- `02-Digital-Product-Department/pa-vet-list/README.md` (যাচাইয়ের নিয়ম)
- Public source: clinic-এর নিজের official website (সবচেয়ে ভালো) অথবা
  directory listing (নাম + শহর + website/phone দেখা যায়)

## Step-by-step method

1. **নতুন শহর বাছাই** (README plan): Pittsburgh আশেপাশে, Harrisburg
   আশেপাশে, Lehigh Valley, Bucks/Montgomery County, Pittsburgh suburbs,
   Central PA ছোট শহর।
2. **একটা clinic খুঁজে** official website খুলে দেখা — independent কি না,
   family-run / woman-owned-এর মতো signal নোট করা।
3. **Chain check — বাদ দেওয়ার তালিকা:** Banfield, VCA, Vetco/Petco,
   BluePearl, Thrive, PetVet365, PetVet Care Centers network। Chain হলে
   row যোগ করা যাবে না।
4. **Field ভরা:** clinic_name, city, website, public_email, public_phone,
   source_url। Email/phone public-এ না থাকলে **"Not publicly listed"**
   লেখা — কিছু বানানো হয় না। 39-এর মধ্যে email আছে 8টার।
5. **Spot-check:** নতুন row-এর website + phone official site-এর সাথে
   মিলিয়ে দেখা (Phase 2-এ যেমন Indy Veterinary Care ও Love City Vet
   যাচাই করা হয়েছে)।
6. **100 পূর্ণ হলে list freeze** করা হবে (ফাইল-এ তারিখ লেখা হবে) — তারপর
   Gate 1 → kit build → launch।

## Output format

- যাচাই করা নতুন row (CSV) + সারাংশ: মোট row সংখ্যা, নতুন শহর, কয়টার
  email আছে / কয়টার "Not publicly listed"।
- Output-এ শুধু যাচাই করা তথ্য — অনুমান নয়।

## Gate

- List বানানোয় কোনো gate নেই — এটা নিরাপদ কাজ।
- কিন্তু list থেকে কাউকে মেইল করতে `send` gate লাগে, আর email channel
  এখন **PAUSED** (2026-11-14 থেকে — SPF/DMARC DNS fix pending)। কোনো
  clinic-কে মেইল করা হয়নি, করা যাবে না।

## Honest limits

- **39/100** — 61 বাকি। কোনো clinic-র সাথে Talvenor-এর কোনো সম্পর্ক/
  চুক্তি নেই — এটা শুধু public তথ্যের list।
- Contact details কখনো বানানো হয় না। Email না থাকলে "Not publicly
  listed" — এটা gap, এটা fill করা যাবে না অনুমান দিয়ে।
- কোনো clinic-কে দুইবার মেইল করা যাবে না (launch-এর সময়)।
- Dental/medical কখনো target নয় — vet clinic animal care, patient-health
  exclusion-এর বাইরে।
- **BOSS INPUT REQUIRED:** কোনো নতুন শহর/area-তে focus করতে চান কি না —
  না বললে README plan অনুযায়ী এগোনো হবে।
