# Section: Sell — Agency (Phase 7)

**Purpose:** From the first draft to a prospect to preparing for the demo call
— outreach, reply, follow-up, objection check, negotiation prep,
and preparing to close the call. This section sends nothing, calls nobody,
closes nothing — it only builds DRAFTs. Boss takes the call himself.

**True status (2026-11-16):** Email PAUSED (since 2026-11-14, DNS fix pending).
Paying client 0. First mail 163 — no state is at 100, so no
state's follow-up is due (20 ready PA follow-up drafts PARKED).
Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
Phone +1 (947) 223-0244.

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| OutreachDrafter | `engine/workers/src/workers/acquisition.py` (`OutreachDrafter`) | `engine/skills/outreach-drafter.md` | `send` | MAPPED |
| ReplyHandler | `engine/workers/src/workers/acquisition.py` (`ReplyHandler`) | `engine/skills/reply-triager.md` | `send` | MAPPED |
| NegotiationCoach | `engine/workers/src/workers/acquisition.py` (`NegotiationCoach`) | `engine/skills/negotiation-coach.md` | `ok` | MAPPED |
| ObjectionSimulator | `engine/workers/src/workers/marketing.py` (`ObjectionSimulator`) | `engine/skills/objection-simulator.md` | `ok` | MAPPED |
| SalesCloser | `sections/sell/agents/sales_closer.py` | `sections/sell/skills/sales-closer.md` | `ok` | NEW (Phase 7) |
| FollowUpAgent | `sections/sell/agents/followup_agent.py` | `sections/sell/skills/followup-agent.md` | `send` | NEW (Phase 7) |

## How work flows

1. **OutreachDrafter** — cold email / IG DM draft (email 20–30/day, IG
   5–10/day warm-up). Draft ONLY.
2. **ObjectionSimulator** — testing the draft as a skeptical prospect before sending
   (5 objections + rebuttal angle). REVIEW ONLY, never sent.
3. **ReplyHandler** — prospect reply triage (interest / question / pricing /
   demo / decline) + draft reply; no price quote, offer of a short call.
4. **FollowUpAgent** — follow-up draft ONLY. **100-mail rule:** without
   100 first mails in a state, no follow-up for that state — due nowhere now.
5. **NegotiationCoach** — live call prep (3 Q&A, 2 traps, 60-sec opening).
6. **SalesCloser** — call-prep pack + close checklist DRAFT. Boss takes the call
   himself — this agent never calls, never closes.

## Gate

- `send` (OutreachDrafter, ReplyHandler, FollowUpAgent): sending needs Boss's
  "send"; Boss sends it himself.
- `ok` (NegotiationCoach, ObjectionSimulator, SalesCloser): pack/review
  needs Boss's "ok" to use.

## Honest limits

- Email PAUSED (since 2026-11-14) — the draft is the final word.
- **100-mail rule (Boss 2026-11-10):** without 100 first mails in a state,
  no follow-up; total first mail 163, no state is at 100.
- All output is DRAFT, mock brain ($0). No price quote, no guarantee,
  no invented client/testimonial/statistic.
- Paying client 0. Never dental/medical.
