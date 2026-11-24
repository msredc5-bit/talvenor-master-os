---
name: kit-builder
description: "Build the Vet No-Show Recovery Kit's 6 parts — from blueprint to the real kit."
---

# Skill: Kit Builder

**Role:** Build the Vet No-Show Recovery Kit's 6 parts — from blueprint to the real kit.
**Status: BLOCKED** — Gate 0 NOT PASSED. Now only the blueprint can be read, the kit
cannot be built.

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (launch price **$39** for the
  first 30 buyers, then $49). Format: Google Sheets + Google Docs
  + copy-paste script. No code, no app, nothing to install.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets, buyer =
  front-desk / practice manager. Not a corporate chain, not a solo mobile vet.
- **Pain (VERIFIED):** no-show rate **~11%** (AAHA) × average vet visit **~$200**
  (AVMA 2025) ≈ **~$50k–$150k/yr** at risk for a typical clinic
  (labeled estimate — 25 appointments/day × 11% × 250 days). **34,296**
  vet practices in the US (Census 2023). Real example: PAWS Clinic, 904 no-shows
  in 2025 (clinic Facebook post, 15 Jan 2026).
- **Price flag:** $49 does not come from any verified sale — it is an inference
  from a neighboring product's anchor ($49 Room Intake + Rounding SOP Pack). It
  will be tested at Gate 2.

## Inputs

- `02-Digital-Product-Department/kit-outline.md` — blueprint (the only source)
- Research report `~/workspace/research_notes/digital-product-final-20261112/report.md` §4.1 (exact description of the 6 parts), §4.2 (pain arithmetic)
- Gate 1 check: AAHA/PetDesk published guidance (the cadence + script must match it)
- Gate 0 status: `gate0-status.md` — no build starts unless it says "Status: PASSED"

## 6 parts — step-by-step method (after Gate 0, Week 2, 1 hour/day, $0)

### 1. Reminder Cadence Pack (Docs + script)
1. T-72h / T-24h / T-2h — SMS + email + phone-call script, copy-paste.
2. Every script must have [NAME] / [PET] / [TIME] fields.
3. **Gate 1:** the cadence + script must match AAHA/PetDesk's published guidance.
   If it does not match, fix it; if it still does not match, KILL or re-scope.

### 2. Same-Day Rebooking Scripts (Docs)
1. What the front desk says when a client no-shows or late-cancels — so that
   the slot is filled again the same day.
2. Phone script + in-person script, both in plain US English.

### 3. Waitlist-Fill SOP (Docs, one page)
1. Who to call first when a slot opens, in what order — with an exact call script.
2. A one-page procedure — can be posted at the front desk.

### 4. No-Show Log + $ Tracker (Sheets)
1. Log every no-show; formulas auto-total: how many appointments were missed
   this month, roughly how many $ were lost, what the recovery rate is.
2. Test the formulas with sample numbers (during build).
3. **This $ figure is the real point:** the clinic sees its loss with its own eyes.

### 5. Deposit / No-Show Policy Template (Docs)
1. A plain-words policy template a clinic can adopt.
2. It will say: **"have your own attorney review before using"** — this is
   not legal advice, and Elora never presents it as legal advice.

### 6. Front-Desk Quick Card (Docs, one page)
1. 5 lines — following them prevents most no-shows.
2. One page, to keep at the reception desk.

### Final step
- Read through the whole kit once — check for errors, invented clinical wording,
  or a misspelled "Talvenor".
- It cannot claim to replace a PIMS — the kit works alongside a PIMS (76.5%
  of practices already use a PIMS — AVMA 2025).

## Output format

- DRAFT of the 6 parts (Sheets/Docs link or file) + a one-page build note: what is in
  each part, whether the Gate 1 check passed, the sample test result.
- The top of the output will say the real status among DRAFT / READY / TESTING / LIVE —
  never an invented status.

## Gate

- Boss's `ok` is needed to start building.
- No part can be built until Gate 0 passes — the Chief's
  `kit_build` only returns the blueprint.

## Honest limits

- **Gate 0 BLOCKED:** no part of the kit has been built yet — only the blueprint
  exists. Build order is Week 2 (after Gate 0).
- The cadence's vet accuracy (Gate 1) has not been verified yet — reading the AAHA/PetDesk source
  is still pending.
- $49 price unproven — no verified sale. $10K/mo verdict: the kit alone
  will not deliver it in 6–12 months; credible $300–$1,000/mo (6–20 sales/mo), if Gate 2
  passes. Wedge (1/20 buyers → $1,109/mo receptionist) UNTESTED.
- Dental/medical (patient-health) is never a target — this is animal care.
- **BOSS INPUT REQUIRED:** the Gate 0 result (Lemon Squeezy test) — nobody but Boss
  can provide it.
