# Section: Receive — Agency (Phase 7)

**Purpose:** From a new lead arriving to handing it to research —
receiving leads, organizing the inbox, research, and helping with scheduling. This section
sends nothing, calls nobody — only receiving and organizing.

**True status (2026-11-16):** Email PAUSED (since 2026-11-14, DNS fix pending).
Paying client 0. First mail 163. Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| ClientIntakeReceiver | `sections/receive/agents/client_intake_receiver.py` | `sections/receive/skills/client-intake-receiver.md` | `send` | NEW (Phase 7) |
| InboxTriager | `engine/workers/src/workers/admin.py` (`InboxTriager`) | `engine/skills/inbox-triager.md` | None | MAPPED |
| ProspectResearcher | `engine/workers/src/workers/acquisition.py` (`ProspectResearcher`) | `engine/skills/prospect-researcher.md` | None | MAPPED |
| SchedulerAssistant | `engine/workers/src/workers/admin.py` (`SchedulerAssistant`) | `engine/skills/scheduler.md` | None | MAPPED |

## How work flows

1. **ClientIntakeReceiver** — intake log + checklist DRAFT when a new lead arrives.
   Information only from the real source; without it, "BOSS INPUT REQUIRED".
2. **InboxTriager** — organizing the inbox (urgent / prospect / vendor / noise) +
   draft reply; it sends nothing.
3. **ProspectResearcher** — US home-service SMB research: owner, missed-call
   pain signal, tech gap, personalization angle. No dental/medical.
4. **SchedulerAssistant** — proposing 3 slots (Asia/Dhaka + US-Eastern) +
   draft invite; the booking link is the real one. Nothing is sent before Boss confirms.

## Gate

- `send` (ClientIntakeReceiver): sending anything intake-related needs Boss's
  "send"; Boss sends it himself.
- The other 3 have gate None — their drafts are themselves safe.

## Honest limits

- Email PAUSED (since 2026-11-14) — the draft is the final word, not even an attempt to send.
- All output is DRAFT, mock brain ($0). No lead/client information is invented.
- Paying client 0; first mail 163.
- No price, guarantee, or invented testimonial/statistic.
