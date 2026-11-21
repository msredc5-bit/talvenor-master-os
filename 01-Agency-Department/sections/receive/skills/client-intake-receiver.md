# Skill: Client Intake Receiver — Agency (Phase 7)

**Role:** Client Intake Receiver · **Worker:** `ClientIntakeReceiverAgent` (Phase 7, receive section)
· **Task type:** `client_intake` · **Gate:** `send`
· **SOP basis:** agency-os SKILL 02-lead-generation + SOP prospect-qualification-talvenor.md

**Business:** Talvenor AI Receptionist — taking a new lead's information when it arrives,
writing the intake log, and building an intake checklist DRAFT. No reply is sent.

## Input

- `business`: the business name (from the real source; without it, BOSS INPUT REQUIRED).
- `owner`: the owner's name, `trade`: plumbing / HVAC / roofing / garage door /
  septic / tree / foundation / restoration / pest / vet.
- `city`, `state`, `source` (where the lead came from), `contact`.

## Method (step-by-step)

1. Take the lead's information — only from the real source; a name/address/phone is never guessed.
2. Check whether the trade is within Talvenor's niche — if dental/medical/
   patient-health, it is not intake, it is excluded.
3. Write the intake log (in the returned draft): business, owner, trade, city,
   source, contact — for missing information, "BOSS INPUT REQUIRED".
4. Build the intake checklist (DRAFT): confirm information, check the niche,
   note the missed-call pain signal, hand it to ProspectResearcher for research.
5. No reply is sent — if a reply is needed, it is InboxTriager/OutreachDrafter's
   draft; nothing goes without Boss's "send".

## Output format

```text
[MOCK DRAFT] Client Intake — DRAFT ONLY
Lead: [business] | Owner: [owner] | Trade: [trade] | City: [city, state] | Source: [source] | Contact: [contact]
Intake checklist (DRAFT):
1. [confirm business + owner from a real source]
2. [niche check — Talvenor niche, not dental/medical]
3. [missed-call pain signal, if seen]
4. [hand to ProspectResearcher]
5. [no reply sent from intake]
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: send — sending anything intake-related needs Boss's exact word.
```

## Gate

`send` — Boss's exact word is needed, and Boss himself does the sending
(from the main chat). This system only builds DRAFTs.

## Honest limits

- Mock brain ($0) — output DRAFT. Intake itself sends nothing, calls nobody.
- Without information, "BOSS INPUT REQUIRED" — no invented client information.
- No price, guarantee, or invented client/testimonial/statistic.
- Never dental/medical/patient-health.

## Worked example (with real information)

Input: `business` = "BOSS INPUT REQUIRED" (new lead, name not confirmed yet),
`trade` = plumbing, `city` = Allentown, `state` = PA,
`source` = Facebook Page, `contact` = BOSS INPUT REQUIRED.

Output: intake log + checklist in the format above — name/contact has
"BOSS INPUT REQUIRED", booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8,
Phone +1 (947) 223-0244. No reply was sent, no information was invented.
