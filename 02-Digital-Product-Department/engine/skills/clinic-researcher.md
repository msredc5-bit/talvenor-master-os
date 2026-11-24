---
name: clinic-researcher
description: "Grow the PA vet list toward 100 verified independent clinics."
---

# Skill: Clinic Researcher

**Role:** Grow the PA vet list toward 100 verified independent clinics.
**Status: REAL work, 39/100** (2026-11-16, verified) — the remaining 61 will
be completed after Gate 0.

## Target (locked facts)

- **Goal:** 100 independent vet clinics, Pennsylvania (starting with one state).
- **Have now:** 39 clinics — 39% of the goal. 61 remaining.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets. Not a corporate
  chain (they have a central system), not a solo mobile vet (too small).
- **City breakdown (39):** Philadelphia 8, York 5, Lancaster 4, Allentown /
  Bethlehem 4, Pittsburgh / Monroeville 3, Erie 3, Scranton / Wilkes-Barre 3,
  State College 3, Harrisburg 2, Norristown 2, Reading 1, Altoona 1.

## Inputs

- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` (39 rows —
  source, never overwritten, only verified rows added)
- `02-Digital-Product-Department/pa-vet-list/README.md` (verification rules)
- Public source: the clinic's own official website (best) or a
  directory listing (name + city + website/phone visible)

## Step-by-step method

1. **Pick a new city** (README plan): around Pittsburgh, around Harrisburg,
   Lehigh Valley, Bucks/Montgomery County, Pittsburgh suburbs,
   small Central PA towns.
2. **Find a clinic** and open its official website — check whether it is
   independent, note signals like family-run / woman-owned.
3. **Chain check — exclusion list:** Banfield, VCA, Vetco/Petco,
   BluePearl, Thrive, PetVet365, PetVet Care Centers network. If it is a chain,
   no row can be added.
4. **Fill the fields:** clinic_name, city, website, public_email, public_phone,
   source_url. If the email/phone is not public, write **"Not publicly listed"**
   — nothing is invented. Of the 39, 8 have an email.
5. **Spot-check:** compare the new row's website + phone against the official site
   (as Indy Veterinary Care and Love City Vet were verified in Phase 2).
6. **When 100 is reached, freeze the list** (the date will be written in the file) — then
   Gate 1 → kit build → launch.

## Output format

- Verified new rows (CSV) + summary: total row count, new cities, how many
  have an email / how many are "Not publicly listed".
- The output contains only verified information — no estimates.

## Gate

- Building the list has no gate — it is safe work.
- But emailing anyone from the list needs the `send` gate, and the email channel
  is now **PAUSED** (since 2026-11-14 — SPF/DMARC DNS fix pending). No
  clinic has been emailed, and none can be.

## Honest limits

- **39/100** — 61 remaining. Talvenor has no relationship/
  agreement with any clinic — this is only a list of public information.
- Contact details are never invented. If there is no email, "Not publicly
  listed" — that is a gap, it cannot be filled with a guess.
- No clinic can be emailed twice (at launch time).
- Dental/medical is never a target — a vet clinic is animal care, outside the
  patient-health exclusion.
- **BOSS INPUT REQUIRED:** whether he wants to focus on any new city/area —
  if he does not say so, work proceeds per the README plan.
