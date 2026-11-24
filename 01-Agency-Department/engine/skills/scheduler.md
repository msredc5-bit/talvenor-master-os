---
name: scheduler
description: "Scheduler · Worker: SchedulerAssistant (boss-ceo, OPS)"
---

# Skill: Scheduler — Agency (Phase 5)

**Role:** Scheduler · **Worker:** `SchedulerAssistant` (boss-ceo, OPS)
· **Task type:** `schedule_help` · **Gate:** None
· **SOP basis:** agency-os SKILL 20-agency-operations

**Job:** Helping with scheduling — proposing slots + draft invite. Before Boss
confirms, nothing is sent.

## Input

- `what` (default: client demo call) — what the schedule is for.
- Boss's availability (without it, "BOSS INPUT REQUIRED").

## Method (step-by-step)

1. Decide what to schedule (demo call / onboarding call / follow-up).
2. Propose 3 slots — with Asia/Dhaka time + US-Eastern equivalent.
3. Write a draft invite — short, plain: what, when, where (booking link:
   https://calendar.app.google/WLoxBfnLGTdjK3LB8 — Talvenor Demo,
   15 min, New York Time).
4. Show it to Boss — the invite only goes once Boss confirms (Boss sends it himself).

## Output format

```text
What: [client demo call]
Slots (Asia/Dhaka + US-Eastern):
  1. [Dhaka time] = [US-Eastern time]
  2. ...
  3. ...
Draft invite:
[short text + booking link]
Gate: None (sending the invite needs Boss's confirm — a separate decision)
```

## Gate

No gate — slot + draft is itself safe. Sending the invite does not happen without Boss's
confirm.

## Honest limits

- Mock brain ($0) — slot + draft DRAFT only.
- Without seeing Boss's calendar, a slot cannot be claimed "free" — it is only a proposal;
  Boss confirms.
- The booking link's times are New York Time — no invite can be written in the wrong timezone.
