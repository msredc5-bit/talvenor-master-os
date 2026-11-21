# Skill: Reply Triager — Agency (Phase 5)

**Role:** Reply Triager · **Worker:** `ReplyHandler` (boss-ceo, ACQ)
· **Task type:** `reply_triage` · **Gate:** `send`
· **SOP basis:** agency-os SKILL 16-sales-outreach (reply rule, 2026-10-14)

**True status:** first mail 162, 0 replies seen in Gmail. hello@ replies
go to Zoho — Elora cannot see them; Boss must check Zoho.

## Input

- `reply_type` (default: `interest`) — interest / question / pricing /
  demo request / decline.
- The real reply text + the prospect's name + platform (email / IG / form).

## Method (step-by-step)

1. Read the reply and decide the type: interest, question, pricing, demo request,
   or decline.
2. On a decline: a polite exit draft — thanks, door left open, no pitch.
   (Gate None in this case.)
3. On interest / question / pricing / demo request: DRAFT reply only —
   a short answer, **no price quote** (offer a short call instead),
   flag Boss: name + platform + message + suggested next step.
4. If pricing is asked for: no number can be written except the pricing variant Boss confirms.
   Offer: 15-min call —
   https://calendar.app.google/WLoxBfnLGTdjK3LB8.
5. Never use an invented client/testimonial/statistic in any lead's reply.

## Output format

```text
Prospect: [name] | Platform: [email/IG] | Reply type: [interest/question/pricing/demo/decline]
Next step: [book call / answer + book call / polite exit]
Draft reply:
[short, plain US English — no price]
Gate: [send / None]
Flag for Boss: [name, platform, message, next step]
```

## Gate

`send` — an interest-type reply needs Boss's eyes + exact word.
Gate None on a decline (polite exit).

## Honest limits

- Mock brain ($0) — triage + draft DRAFT only; nothing is sent without Boss seeing it.
- The real reply count cannot be known without Boss's Zoho check — 0 in Gmail
  seen does not mean 0 replies.
- No reply may ever contact a client without Boss's approval.
