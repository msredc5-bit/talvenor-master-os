# Workflow 2 — Sales Outreach

**Department:** 01 Sales & Growth
**Date:** 2026-11-19 | **Status:** ⛔ PAUSED — draft only (since 2026-11-14, Boss's order).

## Purpose

Telling Tier 1/2 leads about the Talvenor AI receptionist with personalized email + Instagram DM, and taking bookings for a 15-min demo call — no price quote, no pressure.

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Email Outreach Agent (`OutreachDrafter`) | 01 | EXISTING — only writes drafts, never sends |
| Follow-up Agent (`FollowUpAgent`) | 01 | EXISTING — PARKED (100-mail rule) |
| ReplyHandler (`reply_triage`) | 01 | EXISTING — reply triage |
| SalesCloser / NegotiationCoach | 01 | EXISTING — close/negotiation prep (draft only) |
| SchedulerAssistant (`schedule_help`) | 01 | EXISTING — booking link help |

## True status (CURRENT STATE — PAUSED)

- **Email PAUSED since 2026-11-14.** Reason: DNS fix pending (SPF has no Gmail include, DMARC missing). Restart only once Boss fixes it in the DNS panel + says "check koro".
- **First mail 163** — PA 39, TX 15, GA 16, FL 54, CA 15, NC 5, IL 9, MI 5, OH 1, NY 4.
- **Day 4 / Day 5 / Day 6 drafts — 25 each READY, not sent.** Once the pause lifts, what Boss says goes.
- **Follow-up rule (standing, 2026-11-10):** no follow-up for a state until 100 first mails are complete in that state. No state is at 100 (FL ceiling 99 — it cannot reach 100). So follow-up is **PARKED**.
- **IG DM: 5–10/day** via `@talvenor_ai` — needs Boss's approval tap.
- **n8n auto-send READY, not LIVE** — Boss's import + 1 test mail pending.

## Step-by-step

### Step 1 — Writing drafts (OutreachDrafter)

1. Read the lead's research notes (business name, owner, pain signal, angle).
2. Write a **personalized email draft** — one idea, plain US English, one CTA: 15-min demo call.
3. **Demo = recorded 60-second demo video:** https://facebook.com/reel/2947321012290705/ — always say "60-second demo".
4. Sender: `hello@talvenorai.agency` (outreach address). `contact@talvenorai.agency` is never for cold outreach.
5. **Never quote a price** — pricing is internal only. If someone asks the price: share details on a short call, give the booking link.
6. **Gate:** a draft has no gate — writing a draft is not sending.

### Step 2 — Send (PAUSED — this step is closed now)

1. **Normal rule (without a pause):** 20–30 emails/day; nothing can be sent without Boss's exact gate word **`send`**.
2. **Now:** PAUSED. No mail will go. Day 4/5/6 drafts stay READY.
3. n8n auto-send is not LIVE — so no auto-send happens now either.
4. **Gate:** `send` — Boss's exact word. While the pause stands, even saying `send` cannot send until the DNS fix is verified.

### Step 3 — Instagram DM (5–10/day)

1. Find the lead's Instagram account; observe before sending a DM — never pitch in a comment.
2. Write a DM draft (OutreachDrafter, channel = instagram) — short, personal, one CTA.
3. **Gate:** no DM can be sent without Boss's approval tap.

### Step 4 — Follow-up (PARKED)

1. **100-mail rule:** follow-up for a state's leads only once 100 first mails are complete in that state.
2. No state is at 100 now — **so no follow-up**. PA has 39 first mails (2026-11-12 count — the old "37" in this step was stale; PA `emailed.csv` holds 39 rows + header, matching the §True-status count above).
3. A follow-up draft (`FollowUpAgent`) may be written, but it cannot be sent.
4. **Gate:** `send` — + the 100-mail rule fulfilled.

### Step 5 — Reply triage (ReplyHandler)

1. When a reply comes, triage it:
   - **Decline / not interested → polite exit** — no more follow-up, no argument.
   - **Interest / question / pricing / demo request → draft only** — write a reply draft, show Boss, send on Boss's word. Never a price — give the booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8
   - **Bounce / dead address →** write `bounced`/`dead` in the lead row, do not delete the row, do not mail again.
2. **Zoho gap:** replies to `hello@` go to Zoho — Elora cannot see them. **Boss must check and forward them himself.**
3. **Gate:** sending a reply needs `send` — Boss's exact word.

## Honest status

- Outreach **PAUSED** — draft writing continues, sending is stopped.
- Follow-up **PARKED** — stuck on the 100-mail rule.
- A reply triage worker exists, but Elora cannot see Zoho replies unless Boss forwards them.

## Missing inputs

- DNS fix (Boss's DNS panel): `include:_spf.google.com` in SPF + `_dmarc` record — no restart without it.
- Boss's "check koro" + word to restart.
- Zoho reply forwarding (Boss's job).
- n8n auto-send import + test (Boss's job).
