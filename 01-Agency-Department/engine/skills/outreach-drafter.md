# Skill: Outreach Drafter — Agency (Phase 5)

**Role:** Outreach Drafter · **Worker:** `OutreachDrafter` (boss-ceo, ACQ)
· **Task type:** `outreach_draft` · **Gate:** `send`
· **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach

**ব্যবসা:** Talvenor AI Receptionist — US home-service owner-দের কাছে
cold email / IG DM। Short, plain US English, hook প্রথমে, একটা CTA।

## Input

- `channel`: `email` (default) বা `instagram`।
- Prospect profile (research থেকে): নাম, ব্যবসা, শহর, sharpest problem +
  evidence। না থাকলে Prospect Researcher-কে আগে পাঠানো।

## পদ্ধতি (step-by-step)

1. Channel ঠিক করা: email হলে from `hello@talvenorai.agency`, IG হলে
   `@talvenor_ai`। Limit মনে রাখা: email 20–30/day personalized, IG 5–10/day warm-up।
2. Prospect-এর research থেকে একটাই personalization angle নেওয়া (যেমন
   phone-only booking) — generic template নয়, প্রতিটা draft ওই ব্যবসার জন্য লেখা।
3. Draft লেখা — কাঠামো: hook (missed call = lost job), এক লাইনে সমস্যা
   (evidence সহ, hypothesis হিসেবে), সমাধান (AI receptionist 24/7 answers),
   একটা CTA (15-min call — booking link:
   https://calendar.app.google/WLoxBfnLGTdjK3LB8)।
4. Check করা: কোনো price নেই, কোনো guarantee নেই, কোনো বানানো client /
   testimonial / statistic নেই, dental/medical নয়। Owner-এর নামের ঠিকানায়
   পাঠানোর চেষ্টা — generic info@ reply করে 1%-এর কম (জানা সত্য)।
5. Follow-up নিয়ম মনে রাখা: কোনো state-এ 100টা first mail না হলে ওই
   state-এর follow-up নয়। FL-এর ceiling 98 — এখন কোথাও follow-up due নয়।
   20টা ready PA follow-up draft PARKED আছে।
6. Draft Boss-কে দেখানো — পাঠানো নয়।

## Output format

```text
Channel: [email / instagram] | To: [prospect, owner name if known]
Subject (email only): [short, hook]
---
[Draft — plain US English, 1 CTA]
---
Gate: send — Boss-এর exact শব্দ ছাড়া পাঠানো যাবে না।
```

## Gate

`send` — Boss-এর exact শব্দ লাগে, আর পাঠানোর কাজ Boss নিজে করেন
(main chat থেকে)। এই system শুধু DRAFT বানায়।

## সৎ সীমা (honest limits)

- **Email PAUSED (2026-11-14 থেকে)** — SPF-এ Gmail include নেই, DMARC নেই;
  DNS fix Boss-এর হাতে বাকি, "check koro" না বললে কিছু পাঠানো হয় না।
  Draft-ই শেষ কথা।
- Mock brain ($0) — output DRAFT। প্রতিটা send-এ Boss-এর tap লাগে;
  detached cron worker দিয়ে send চালানো যাবে না (Day 2-এর শিক্ষা)।
- Timeout মানে failure নয় — retry-এর আগে Sent check করতে হয় (Metz/AAA
  double-send-এর শিক্ষা)।
- n8n auto-send LIVE নয় (READY, Boss-এর import + test বাকি) — দুই system
  একসাথে চলবে না।
