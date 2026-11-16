# Section: Receive — Agency (Phase 7)

**উদ্দেশ্য (purpose):** নতুন lead আসা থেকে research-এর হাতে দেওয়া পর্যন্ত —
lead গ্রহণ, inbox সাজানো, research, আর scheduling-এ সাহায্য। এই section
কিছু পাঠায় না, কাউকে call করে না — শুধু গ্রহণ আর সাজানো।

**সত্য অবস্থা (2026-11-16):** Email PAUSED (2026-11-14 থেকে, DNS fix বাকি)।
Paying client 0। প্রথম মেইল 162। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| ClientIntakeReceiver | `sections/receive/agents/client_intake_receiver.py` | `sections/receive/skills/client-intake-receiver.md` | `send` | NEW (Phase 7) |
| InboxTriager | `engine/workers/src/workers/admin.py` (`InboxTriager`) | `engine/skills/inbox-triager.md` | None | MAPPED |
| ProspectResearcher | `engine/workers/src/workers/acquisition.py` (`ProspectResearcher`) | `engine/skills/prospect-researcher.md` | None | MAPPED |
| SchedulerAssistant | `engine/workers/src/workers/admin.py` (`SchedulerAssistant`) | `engine/skills/scheduler.md` | None | MAPPED |

## কাজের প্রবাহ (how work flows)

1. **ClientIntakeReceiver** — নতুন lead এলে intake log + checklist DRAFT।
   তথ্য শুধু আসল source থেকে; না থাকলে "BOSS INPUT REQUIRED"।
2. **InboxTriager** — inbox সাজানো (urgent / prospect / vendor / noise) +
   draft reply; কিছু পাঠায় না।
3. **ProspectResearcher** — US home-service SMB research: owner, missed-call
   pain signal, tech gap, personalization angle। Dental/medical নয়।
4. **SchedulerAssistant** — ৩টা slot প্রস্তাব (Asia/Dhaka + US-Eastern) +
   draft invite; booking link আসলটা। Boss confirm করার আগে কিছু পাঠানো হয় না।

## Gate

- `send` (ClientIntakeReceiver): intake-সংক্রান্ত কিছু পাঠাতে Boss-এর
  "send" লাগে; পাঠানো Boss নিজে করেন।
- বাকি ৩ জনের gate None — ওদের draft নিজেই নিরাপদ।

## সৎ সীমা (honest limits)

- Email PAUSED (2026-11-14 থেকে) — draft-ই শেষ কথা, send-এর চেষ্টাও নয়।
- সব output DRAFT, mock brain ($0)। কোনো lead/client তথ্য বানানো হয় না।
- Paying client 0; প্রথম মেইল 162।
- কোনো price, guarantee, বানানো testimonial/statistic নেই।
