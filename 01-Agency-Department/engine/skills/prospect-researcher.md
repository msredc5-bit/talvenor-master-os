# Skill: Prospect Researcher — Agency (Phase 5)

**Role:** Prospect Researcher · **Worker:** `ProspectResearcher` (boss-ceo, ACQ)
· **Task type:** `prospect_research` · **Gate:** None (research only, কিছু পাঠানো হয় না)
· **SOP ভিত্তি:** agency-os SKILL 02-lead-generation + 03-lead-qualification +
SOP `prospect-qualification-talvenor.md` (v1, 2026-11-03)

**ব্যবসা:** Talvenor AI Receptionist — US home-service SMB: plumbing, HVAC,
roofing, garage door, septic, tree, foundation/waterproofing, restoration,
pest, vet। Dental / medical / patient-health — সঙ্গে সঙ্গে DQ, কখনো score নয়।

## Input

- `niche` (default: `plumbing`), `region` (default: `Texas`)।
- অথবা একটা lead dataset (business_name, city, state, phone, website —
  কমপক্ষে ৪টা field না থাকলে low-confidence flag)।

## পদ্ধতি (step-by-step)

1. Target niche + region ঠিক করা। Legal lead হলে park করা (4th client পর্যন্ত gated)।
2. ব্যবসা খোঁজা — website, Google Business profile, সোশ্যাল bio দেখা। কোনো
   field না পেলে `NOT_FOUND` লেখা — কখনো বানানো phone/email/address নয়।
3. প্রতিটা lead-এর website-এ ১১টা need signal টিক দেওয়া (প্রমাণের URL সহ):
   (1) phone-only booking, (2) online scheduler নেই, (3) live chat নেই,
   (4) contact-form only, (5) 24/7/emergency দাবি কিন্তু answering-system-এর
   প্রমাণ নেই, (6) owner নিজে field-এ, (7) urgent service, (8) অনেক service /
   বড় এলাকা, (9) team page-এ শুধু technician, (10) social bio-তে booking
   link নেই, (11) Google profile call-only।
4. Signal গোনা: 3+ = STRONG, 2 = MEDIUM, 0–1 = WEAK। ১০০ পয়েন্টের rubric-এ
   score করা — প্রমাণ ছাড়া ০ পয়েন্ট, কখনো average বা benefit of the doubt নয়।
5. Tier নিয়ম: STRONG + 80–100 = Tier 1; STRONG + 60–79 = Tier 2;
   MEDIUM = সর্বোচ্চ Tier 2; WEAK = Tier 4 (contact নয়)। একটা review
   কখনো একা Tier 1 বানায় না — website signal-ও লাগে।
6. Disqualifier check (১০০% row): বন্ধ ব্যবসা / ফোন disconnected / আগে
   থেকেই AI receptionist client / franchise central call center / ৩টার কম
   review + website নেই / do-not-contact list / dental-medical। Hit হলে DQ,
   score 0, কারণ লেখা।
7. প্রতিটা lead-এর এক লাইনের সমস্যা লেখা: `Possible problem: [সমস্যা] —
   Evidence: [website-এ যা দেখা গেছে]`। এটা hypothesis — prospect-কে
   verified fact হিসেবে বলা যাবে না।
8. CRM-এ লেখা (stage = `not_contacted`): score, tier, signal count, evidence
   URL, best channel, reason line।

## Output format

```text
Prospect: [business name] — [city, state]
Tier: [1/2/3/4/DQ] | Score: [0-100] | Signals: [n/11 STRONG/MEDIUM/WEAK]
Possible problem: [...] — Evidence: [URL]
Best channel: [email / IG DM / form (Boss নিজে) / park]
```

## Gate

কোনো gate নেই — research নিজেই নিরাপদ। কিন্তু এই research থেকে কোনো
outreach লেখা হলে সেটা Outreach Drafter-এর কাজ, gate `send`।

## সৎ সীমা (honest limits)

- Mock brain ($0) — output DRAFT, যাচাই ছাড়া ব্যবহার নয়।
- Qualification চলাকালীন কাউকে call/message/form করা যাবে না — শুধু observation।
- Website down থাকলে Tier 1 নিষিদ্ধ, "site down at time of scoring" লিখতে হবে।
- Reviewer-এর নাম কখনো copy করা যাবে না; review text + date only।
- Tier কম থাকলে সৎভাবে Boss-কে জানানো — quota পূরণের জন্য tier বাড়ানো যাবে না।
