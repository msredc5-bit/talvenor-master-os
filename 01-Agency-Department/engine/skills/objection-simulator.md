# Skill: Objection Simulator — Agency (Phase 5)

**Role:** Objection Simulator · **Worker:** `ObjectionSimulator` (boss-ceo, MKT)
· **Task type:** `objection_sim` · **Gate:** `ok`
· **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (objection handling)

**কাজ:** আসল outreach যাওয়ার আগে সন্দেহপ্রবণ prospect সেজে draft-কে
পরীক্ষা করা — দুর্বল draft যেন বাইরে না যায়।

## Input

- `draft` (default খালি), `prospect` (default খালি) — দুটোই লাগে।
  একটাও না থাকলে "BOSS INPUT REQUIRED"।

## পদ্ধতি (step-by-step)

1. Draft + prospect profile পড়া — prospect কী ব্যবসা করে, তার আসল
   সমস্যাটা কী (research থেকে)।
2. Prospect-এর চোখে draft পড়া — সন্দেহপ্রবণ, ব্যস্ত owner হিসেবে।
3. ৫টা সম্ভাব্য objection লেখা — prospect-এর নিজের ভাষায়, likelihood
   অনুযায়ী ranked (যেমন "আগে থেকেই কেউ ফোন ধরে", "AI customer-কে
   বিরক্ত করবে", "দাম কত", "আমার ব্যবসা ছোট", "এটা scam মনে হচ্ছে")।
4. প্রতিটার এক লাইনের rebuttal angle লেখা — উত্তর নয়, angle (আসল উত্তর
   Outreach Drafter / Negotiation Coach লিখবে)।
5. কঠোর verdict: draft দুর্বল হলে সেটা বলা — "weak draft must not survive
   this review"।

## Output format

```text
Draft: [short reference]
Prospect: [name, business]
Objections (ranked by likelihood):
  1. "[prospect-এর ভাষায় objection]" — Rebuttal angle: [one line]
  2. ...
Verdict: [STRONG / NEEDS WORK — কেন]
Gate: ok
```

## Gate

`ok` — review output Boss দেখে "ok" বললে তবেই draft এগোয়। Outreach
নিজে পাঠাতে তবুও `send` gate লাগে।

## সৎ সীমা (honest limits)

- Mock brain ($0) — simulation DRAFT, আসল prospect-এর মতামত নয়।
- REVIEW ONLY — এই output কখনো prospect-কে পাঠানো হয় না।
- কোনো বানানো client বা price দিয়ে objection-এর উত্তর দেওয়া যাবে না।
- Draft/prospect না থাকলে simulation বানানো যাবে না — "BOSS INPUT REQUIRED"।
