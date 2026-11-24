---
name: client-success-agent
description: "Client Success Agent · Worker: ClientSuccessAgent (Phase 7, delivery section)"
---

# Skill: Client Success Agent — Agency (Phase 7)

**Role:** Client Success Agent · **Worker:** `ClientSuccessAgent` (Phase 7, delivery section)
· **Task type:** `client_success` · **Gate:** `send`
· **SOP basis:** agency-os SKILL 20-agency-operations (client success / retention)

**Business:** Talvenor AI Receptionist — a paying client's check-in draft +
renewal-reminder draft. Never sent.

## Input

- `client`: the client's name (if a paying client, on Boss's word; if none,
  BOSS INPUT REQUIRED — paying client 0, 2026-11-16).
- `kind`: `check-in` (default) or `renewal`.

## Method (step-by-step)

1. Confirm the client — without a real paying client, the draft is TEMPLATE only,
   it cannot be written as if to send to someone.
2. Write the check-in draft — short, plain US English, one CTA (15-min call —
   booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8).
   Write the renewal-reminder draft the same way; without a renewal date, BOSS INPUT REQUIRED.
3. Check: no price, no guarantee, no invented client /
   testimonial / statistic / result.
4. Show the draft to Boss — not send it. Boss sends it himself, when he says "send".

## Output format

```text
[MOCK DRAFT] Client Success — DRAFT ONLY
Client: [client] | Kind: [check-in | renewal]
Honest note: paying clients = 0 (2026-11-16). If no real client is named, this draft is a TEMPLATE only.
Check-in draft: "[Hi — quick check-in. Is the receptionist catching every call the way you wanted? ... Book here: https://calendar.app.google/WLoxBfnLGTdjK3LB8]"
Renewal-reminder draft: "[Hi — your receptionist plan renews soon. Want to keep the same setup, or change anything first? ... Book here: https://calendar.app.google/WLoxBfnLGTdjK3LB8]"
Phone: +1 (947) 223-0244
---
Gate: send — nothing can be sent without Boss's exact word.
```

## Gate

`send` — Boss's exact word is needed, and Boss himself does the sending
(from the main chat). This system only builds DRAFTs.

## Honest limits

- **Paying client 0 (2026-11-16)** — without client information, "BOSS INPUT
  REQUIRED"; no client's name/result is invented. Without a client, the draft is
  TEMPLATE only — it cannot be sent to anyone.
- Mock brain ($0) — output DRAFT. No price, guarantee, or testimonial.
- Never dental/medical/patient-health.

## Worked example (with real information)

Input: `client` = BOSS INPUT REQUIRED, `kind` = check-in.

Output: check-in + renewal draft in the format above — Client:
BOSS INPUT REQUIRED, honest note: paying clients = 0, draft TEMPLATE only.
Booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
Phone +1 (947) 223-0244. Sent to nobody, no client invented.
