# Skill: Sales Closer — Agency (Phase 7)

**Role:** Sales Closer · **Worker:** `SalesCloserAgent` (Phase 7, sell section)
· **Task type:** `sales_close` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 16-sales-outreach (call prep / objection handling)

**Business:** Talvenor AI Receptionist — a call-prep
pack + close checklist DRAFT for Boss's sales call. Boss takes the call himself — this agent only prepares.

## Input

- `prospect`: the prospect's name/profile (from research; without it, BOSS INPUT REQUIRED).
- `business`: the business name, `goal` (default: book the 15-min demo call).

## Method (step-by-step)

1. Take from the prospect's research — name, business, pain signal; without it,
   send it to ProspectResearcher first, no guessing.
2. Write the opening (60 seconds, plain US English): missed call = lost job,
   AI receptionist 24/7 answers, one CTA (15-min demo call).
3. Likely questions + answers: what it does (answers, qualifies, books), live stack
   Vapi/Sophia, booking link. If a price question comes, offer a short call —
   never quote a price in the prep.
4. Build the close checklist (DRAFT): confirm demo time, send the booking link,
   note the next step, hand it to OnboardingAgent if Boss says yes.
5. Show the pack to Boss — not calling, not closing, not contracting.

## Output format

```text
[MOCK DRAFT] Sales Call Prep — DRAFT ONLY
Prospect: [prospect] | Business: [business] | Goal: [goal]
Call-prep pack (DRAFT):
1. Opening (60 sec): [missed call = lost job; AI receptionist 24/7; 15-min demo call]
2. Likely Q&A: [real facts only — Vapi/Sophia, booking link; price -> short call offer]
3. Close checklist (DRAFT): [confirm demo time; send booking link; note next step]
4. Boss takes the call himself — this agent never calls, never closes.
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: ok — using the pack needs Boss's exact word.
```

## Gate

`ok` — Boss's exact word is needed. This agent does not call, does not close,
does not contract — it only builds the prep DRAFT.

## Honest limits

- Mock brain ($0) — output DRAFT. Boss takes the call himself.
- No price quote, no guarantee, no invented client /
  testimonial / statistic.
- Without information, "BOSS INPUT REQUIRED" — no invented prospect information.
- Never dental/medical/patient-health.

## Worked example (with real information)

Input: `prospect` = BOSS INPUT REQUIRED, `business` = BOSS INPUT REQUIRED,
`goal` = book the 15-min demo call.

Output: prep pack in the format above — opening has missed call = lost job,
CTA has the booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
phone +1 (947) 223-0244. No price anywhere, no close was made —
Boss will take the call; the pack is only a DRAFT.
