# Skill: Outreach Drafter — Agency (Phase 5)

**Role:** Outreach Drafter · **Worker:** `OutreachDrafter` (boss-ceo, ACQ)
· **Task type:** `outreach_draft` · **Gate:** `send`
· **SOP basis:** agency-os SKILL 16-sales-outreach

**Business:** Talvenor AI Receptionist — cold email / IG DM to US home-service owners.
Short, plain US English, hook first, one CTA.

## Input

- `channel`: `email` (default) or `instagram`.
- Prospect profile (from research): name, business, city, sharpest problem +
  evidence. Without it, send it to the Prospect Researcher first.

## Method (step-by-step)

1. Decide the channel: if email, from `hello@talvenorai.agency`; if IG,
   `@talvenor_ai`. Remember the limits: email 20–30/day personalized, IG 5–10/day warm-up.
2. Take just one personalization angle from the prospect's research (e.g.
   phone-only booking) — not a generic template; every draft is written for that business.
3. Write the draft — structure: hook (missed call = lost job), the problem in one line
   (with evidence, as a hypothesis), the solution (AI receptionist 24/7 answers),
   one CTA (15-min call — booking link:
   https://calendar.app.google/WLoxBfnLGTdjK3LB8).
4. Check: no price, no guarantee, no invented client /
   testimonial / statistic, no dental/medical. Try sending to the owner's named address —
   generic info@ replies under 1% (known fact).
5. Remember the follow-up rule: if a state has not reached 100 first mails, no
   follow-up for that state. FL's ceiling is 98 — no follow-up is due anywhere now.
   20 ready PA follow-up drafts are PARKED.
6. Show the draft to Boss — not send it.

## Output format

```text
Channel: [email / instagram] | To: [prospect, owner name if known]
Subject (email only): [short, hook]
---
[Draft — plain US English, 1 CTA]
---
Gate: send — nothing can be sent without Boss's exact word.
```

## Gate

`send` — Boss's exact word is needed, and Boss himself does the sending
(from the main chat). This system only builds DRAFTs.

## Honest limits

- **Email PAUSED (since 2026-11-14)** — SPF has no Gmail include, no DMARC;
  the DNS fix is still in Boss's hands; nothing is sent until he says "check koro".
  The draft is the final word.
- Mock brain ($0) — output DRAFT. Every send needs Boss's tap;
  sending cannot run through a detached cron worker (the Day 2 lesson).
- A timeout does not mean failure — Sent must be checked before retry (the Metz/AAA
  double-send lesson).
- n8n auto-send is not LIVE (READY, Boss's import + test pending) — the two systems
  cannot run together.
