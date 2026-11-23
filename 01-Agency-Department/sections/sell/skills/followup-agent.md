# Skill: Follow-up Agent — Agency (Phase 7)

**Role:** Follow-up Agent · **Worker:** `FollowUpAgent` (Phase 7, sell section)
· **Task type:** `followup_draft` · **Gate:** `send`
· **SOP basis:** agency-os SKILL 16-sales-outreach (follow-up rule 2026-11-10)

**Business:** Talvenor AI Receptionist — writing a follow-up DRAFT. Never sent.

## Input

- `prospect`: the prospect's name/business (from research; without it, BOSS INPUT REQUIRED).
- `state`: US state (e.g. PA, FL, TX).
- `state_first_mails`: that state's first-mail count (the real number; without it,
  BOSS INPUT REQUIRED — no guessing).

## Method (step-by-step)

1. **Check the 100-mail rule (first):** without 100 first mails
   complete in a state, no follow-up for that state. If `state_first_mails` is
   below 100, write "PARKED — follow-up not due" in the draft; without the number,
   BOSS INPUT REQUIRED, it cannot be called due.
2. Write the follow-up draft — short, plain US English, hook first, one CTA
   (15-min call — booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8).
3. Check: no price, no guarantee, no invented client /
   testimonial / statistic, no dental/medical.
4. Show the draft to Boss — not send it. Boss sends it himself, when he says "send".

## Output format

```text
[MOCK DRAFT] Follow-up — DRAFT ONLY
Prospect: [prospect] | State: [state]
100-mail rule check: [state] first mails = [count] (read from the [payload | lead store]; threshold 100) — [DUE | PARKED, follow-up not due yet]
Overall first mails (read live from the lead store when readable, else config.json honest_status): 163 — no state at 100 yet.
Follow-up draft (short, plain US English, 1 CTA):
"[Hi — quick follow-up. Missed calls still mean lost jobs, and our AI receptionist answers 24/7... Book here: https://calendar.app.google/WLoxBfnLGTdjK3LB8]"
Status: [DUE — draft ready for Boss review | PARKED — do NOT send]
Phone: +1 (947) 223-0244
---
Gate: send — nothing can be sent without Boss's exact word.
```

## Gate

`send` — Boss's exact word is needed, and Boss himself does the sending
(from the main chat). This system only builds DRAFTs, no auto-send.

## Honest limits

- **100-mail rule (Boss 2026-11-10, standing):** without 100 first mails in a state,
  no follow-up for that state. Current truth: total first mail 163,
  no state is at 100 — no state's follow-up is due now.
  (163 = 162 filed emailed.csv rows + 1 verified filing gap: Isackson
  Plumbing, CA, sent 2026-11-12, Gmail Sent message 1a1cfb0ff25cdb8c.)
  20 ready PA follow-up drafts are PARKED. FL's ceiling is 99 unique
  leads (2026-11-23 count; the 2026-11-10 figure of 98 was the Nov 10
  pool snapshot).
- **Email PAUSED (since 2026-11-14)** — SPF has no Gmail include, no DMARC;
  the DNS fix is still in Boss's hands. The draft is the final word.
- Mock brain ($0) — output DRAFT. A timeout does not mean failure — before retry,
  Sent must be checked (the Metz/AAA double-send lesson).
- n8n auto-send is not LIVE (READY, Boss's import + test pending).

## Worked example (with real information)

Input: `prospect` = BOSS INPUT REQUIRED, `state` = PA,
`state_first_mails` = 39 (real number, 2026-11-12 count — the old "37" in
this example was stale; PA `emailed.csv` holds 39 rows + header).

Output: 100-mail rule check — PA first mails = 39 (read from the lead
store; threshold 100) — PARKED, follow-up not due yet. Overall first
mails read live from the lead store (163) — no state at 100 yet.
The draft is written, but Status: PARKED — do NOT send. It was not sent,
the rule was not broken.
