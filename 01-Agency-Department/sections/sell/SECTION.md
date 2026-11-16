# Section: Sell — Agency (Phase 7)

**উদ্দেশ্য (purpose):** Prospect-কে প্রথম draft থেকে demo call-এর প্রস্তুতি
পর্যন্ত — outreach, reply, follow-up, objection check, negotiation prep,
আর call-এর close-এর প্রস্তুতি। এই section কিছু পাঠায় না, call করে না,
close করে না — শুধু DRAFT বানায়। Call Boss নিজে নেন।

**সত্য অবস্থা (2026-11-16):** Email PAUSED (2026-11-14 থেকে, DNS fix বাকি)।
Paying client 0। প্রথম মেইল 162 — কোনো state-ই 100-তে নেই, তাই কোনো
state-এর follow-up due নয় (20টা ready PA follow-up draft PARKED)।
Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
ফোন +1 (947) 223-0244।

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| OutreachDrafter | `engine/workers/src/workers/acquisition.py` (`OutreachDrafter`) | `engine/skills/outreach-drafter.md` | `send` | MAPPED |
| ReplyHandler | `engine/workers/src/workers/acquisition.py` (`ReplyHandler`) | `engine/skills/reply-triager.md` | `send` | MAPPED |
| NegotiationCoach | `engine/workers/src/workers/acquisition.py` (`NegotiationCoach`) | `engine/skills/negotiation-coach.md` | `ok` | MAPPED |
| ObjectionSimulator | `engine/workers/src/workers/marketing.py` (`ObjectionSimulator`) | `engine/skills/objection-simulator.md` | `ok` | MAPPED |
| SalesCloser | `sections/sell/agents/sales_closer.py` | `sections/sell/skills/sales-closer.md` | `ok` | NEW (Phase 7) |
| FollowUpAgent | `sections/sell/agents/followup_agent.py` | `sections/sell/skills/followup-agent.md` | `send` | NEW (Phase 7) |

## কাজের প্রবাহ (how work flows)

1. **OutreachDrafter** — cold email / IG DM draft (email 20–30/day, IG
   5–10/day warm-up)। Draft ONLY।
2. **ObjectionSimulator** — পাঠানোর আগে draft-কে সন্দেহপ্রবণ prospect সেজে
   পরীক্ষা (৫ objection + rebuttal angle)। REVIEW ONLY, কখনো পাঠানো হয় না।
3. **ReplyHandler** — prospect reply triage (interest / question / pricing /
   demo / decline) + draft reply; price quote নয়, short call-এর offer।
4. **FollowUpAgent** — follow-up draft ONLY। **100-mail নিয়ম:** কোনো state-এ
   100 first mail না হলে ওই state-এর follow-up নয় — এখন কোথাও due নয়।
5. **NegotiationCoach** — live call-এর prep (৩ Q&A, ২ trap, ৬০-sec opening)।
6. **SalesCloser** — call-prep pack + close checklist DRAFT। Call Boss নিজে
   নেন — এই agent কখনো call করে না, close করে না।

## Gate

- `send` (OutreachDrafter, ReplyHandler, FollowUpAgent): পাঠাতে Boss-এর
  "send" লাগে; পাঠানো Boss নিজে করেন।
- `ok` (NegotiationCoach, ObjectionSimulator, SalesCloser): pack/review
  ব্যবহার করতে Boss-এর "ok" লাগে।

## সৎ সীমা (honest limits)

- Email PAUSED (2026-11-14 থেকে) — draft-ই শেষ কথা।
- **100-mail নিয়ম (Boss 2026-11-10):** কোনো state 100 first mail না হলে
  follow-up নয়; মোট first mail 162, কোনো state 100-তে নেই।
- সব output DRAFT, mock brain ($0)। কোনো price quote নয়, কোনো guarantee নয়,
  কোনো বানানো client/testimonial/statistic নেই।
- Paying client 0। Dental/medical কখনো নয়।
