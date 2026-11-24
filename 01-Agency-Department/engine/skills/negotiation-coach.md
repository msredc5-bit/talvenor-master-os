---
name: negotiation-coach
description: "Negotiation Coach · Worker: NegotiationCoach (boss-ceo, ACQ)"
---

# Skill: Negotiation Coach — Agency (Phase 5)

**Role:** Negotiation Coach · **Worker:** `NegotiationCoach` (boss-ceo, ACQ)
· **Task type:** `negotiation_prep` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 16-sales-outreach (call prep, objection handling)

**Job:** Preparing the Founder for a live sales call. Boss takes the call himself —
this role only writes prep, it does not talk on the call.

## Input

- `prospect` (profile — default empty), `goal` (default: book the demo call).
- The prospect's research + earlier replies, if any. If none, "BOSS INPUT REQUIRED".

## Method (step-by-step)

1. Read the prospect profile — business, niche, sharpest problem, earlier conversation.
2. Write 3 likely questions + a strong answer for each (plain US English) —
   e.g. "someone already answers the phone", "how much does it cost", "will AI annoy customers".
3. Write 2 traps to avoid — e.g. getting stuck on price, giving a guarantee,
   giving an invented client's example.
4. Write a 60-second opening script — hook (missed call = lost job),
   problem, solution, CTA (15-min demo call).
5. Flag as a GATE anything needing Boss's decision (e.g. price
   variant, discount, terms) — not deciding it yourself.

## Output format

```text
Prospect: [name, business]
Goal: [book the demo call]
Likely questions (3):
  1. Q: [...] — A: [...]
  2. ...
Traps to avoid (2):
  1. [...]
  2. [...]
60-second opening script:
[plain US English]
GATE (needs Boss's decision): [...]
```

## Gate

`ok` — the prep pack can only be used after Boss sees it and says "ok".

## Honest limits

- Mock brain ($0) — prep DRAFT, not a substitute for the real call.
- No price quote — except the variant Boss confirms.
- Without the prospect's information, prep cannot be written with an invented profile —
  "BOSS INPUT REQUIRED" must be written.
- Boss will report the call's outcome (booked / declined) — this role does not know it itself.
