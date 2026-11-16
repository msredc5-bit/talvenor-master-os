# Agency Pipeline — আসল ধাপ (Phase 1)

Talvenor AI Receptionist Agency — US home-service ব্যবসার (plumbing,
HVAC, roofing, garage door, septic, tree, foundation, restoration,
pest, vet) জন্য AI receptionist বিক্রি করা। MAIN ব্যবসা।

> **এই ফাইলের প্রতিটা অবস্থা সত্য — যাচাই করা সংখ্যা ছাড়া কিছু লেখা নেই।**

## ধাপগুলো

| # | ধাপ | কে করে | Gate | সত্য অবস্থা (2026-11-16) |
|---|---|---|---|---|
| 1 | **Lead খোঁজা** — US home-service SMB, missed-call signal দেখা | ProspectResearcher (ACQ) | নেই (research only) | Lead universe: **537 unique lead** (Tier 1/2 pool) — `~/workspace/talvenor/leads-organized/` |
| 2 | **Draft লেখা** — cold email / IG DM, short, plain US English, ১টা CTA | OutreachDrafter (ACQ) | `send` | Draft-ই শেষ কথা — পাঠানো নয় |
| 3 | **Boss-এর approval** — draft দেখে ok / send | Boss | `ok` / `send` | প্রতিটা send-এ Boss-এর tap লাগে |
| 4 | **পাঠানো** — email / IG DM | Boss নিজে (এই সিস্টেম নয়) | `send` | **PAUSED — 2026-11-14 থেকে।** DNS fix (SPF + DMARC) Boss-এর হাতে বাকি, "check koro" না বললে কিছু যাবে না |
| 5 | **Follow-up** — reply না এলে আবার লেখা | OutreachDrafter (ACQ) | `send` | **এখনো কারো follow-up due নয়।** নিয়ম: কোনো state-এ 100টা first mail না হলে follow-up নয়। FL-এর ceiling 98 — তাই কোথাও follow-up due নয়। 20টা ready PA follow-up draft PARKED আছে |
| 6 | **Reply triage** — interest / decline / question আলাদা করা | ReplyHandler (ACQ) + InboxTriager (OPS) | `send` (interest reply-তে) | **প্রথম মেইল 162টা, Gmail-এ দেখা reply 0।** hello@-র reply Zoho-তে যায় — Elora দেখতে পায় না, Boss-কে Zoho check করতে হয় |
| 7 | **Call বুক করা** — 15-min demo call | SchedulerAssistant (OPS) | নেই | Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (New York Time) |
| 8 | **Receptionist বানানো** — Vapi Sophia | RetellBuilder = DRAFT plan only (DEL) | `ok` | Live stack **Vapi / Sophia** — ফোন +1 (947) 223-0244। Boss Retell-এর জন্য টাকা দেবেন না, তাই RetellBuilder শুধু plan লেখে, live build করে না |
| 9 | **QA + চালু** — checklist, onboarding | QAEngineer + OnboardingAgent (DEL) | `ok` | Paying client **0** — এখনো কোনো client চালু হয়নি |
| 10 | **Marketing** — সাপ্তাহিক ৫ পোস্ট, video, caption | ContentPlanner / VideoProducer / CaptionWriter / PublishPrep / ObjectionSimulator (MKT) | `ok` / `post it` | Nov 16–22 plan Boss-এর "ok"-র অপেক্ষায়। Publish শুধু Boss-এর "post it"-এ |

## যাচাই করা সংখ্যা (2026-11-16, ফাইল থেকে পড়া)

- Day 1 draft file: **25** draft; Day 2: **25**; Day 3: **25** — পাঠানো হয়েছে
- Day 4 draft file: **25** READY, পাঠানো হয়নি
- Day 5 draft file: **25** READY, পাঠানো হয়নি
- Day 6 draft file: **25** READY, পাঠানো হয়নি
- প্রথম মেইল মোট: **162** (locked record — Day 1–3 + আগের batch)
- Paying client: **0**
- Demo video (60-second): https://facebook.com/reel/2947321012290705/

## যা এই pipeline কখনো করে না

- Dental / medical / patient-health ব্যবসা target করে না (hard DQ)
- Price quote করে না — Boss যে variant confirm করবেন সেটা ছাড়া
- বানানো client / testimonial / statistic ব্যবহার করে না
- Email PAUSED থাকতে send-এর চেষ্টা করে না — draft-ই শেষ কথা
- n8n auto-send LIVE নয় (READY, Boss-এর import + test বাকি) — দুই system একসাথে চলবে না

## ফাইল

- Chief: `chief_of_staff_agency.py` (REAL, Phase 1)
- Worker: `sub_agents/README.md` (15 worker-এর routing)
- Workflow: `workflows/README.md` (email pause-এর সত্য অবস্থা)
- Task log: `../store/tasks.json` · Approval: `../store/approvals.json`
