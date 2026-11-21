# Skill: Clinic Researcher

**Role:** Grow the PA vet list toward 100 verified independent clinics.
**Agent:** `sections/research/agents/clinic_researcher.py` — `ClinicResearcherAgent` (task kind `clinic_research`, section `research`)
**Status: REAL work, 39/100** (2026-11-16, verified) — the remaining 61 will be completed after Gate 0.

## Target (locked facts)

- **Goal:** 100 independent vet clinics, Pennsylvania (starting with one state).
- **Have now:** 39 clinics — 39% of the goal. 61 remaining. Of the 39, 8 have a public email.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets. Not a corporate chain (they have a central system), not a solo mobile vet (too small).
- **City breakdown (39):** Philadelphia 8, York 5, Lancaster 4, Allentown / Bethlehem 4, Pittsburgh / Monroeville 3, Erie 3, Scranton / Wilkes-Barre 3, State College 3, Harrisburg 2, Norristown 2, Reading 1, Altoona 1.

## Inputs

- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` (39 rows — source, never overwritten, only verified rows added; this agent writes no file)
- `02-Digital-Product-Department/pa-vet-list/README.md` (verification rules)
- Public source: the clinic's own official website (best) or a directory listing (name + city + website/phone visible)

## Step-by-step method

1. **Pick a new city** (README plan): around Pittsburgh, around Harrisburg, Lehigh Valley, Bucks/Montgomery County, Pittsburgh suburbs, small Central PA towns.
2. **Find a clinic** and open its official website — check whether it is independent, note signals like family-run / woman-owned.
3. **Chain check — exclusion list:** Banfield, VCA, Vetco/Petco, BluePearl, Thrive, PetVet365, PetVet Care Centers network. If it is a chain, no row can be added.
4. **Fill the fields:** clinic_name, city, website, public_email, public_phone, source_url. If the email/phone is not public, write **"Not publicly listed"** — nothing is invented.
5. **Spot-check:** compare the new row's website + phone against the official site (as Indy Veterinary Care and Love City Vet were verified in Phase 2).
6. **When 100 is reached, freeze the list** (the date will be written in the file) — then Gate 1 → kit build → launch.

## Output format

- The verified list's status: total row count (39/100), city breakdown, how many have an email / how many are "Not publicly listed".
- The verification rules + the next-cities plan.
- The output contains only verified information — no estimates.

## Tools used

- Read-only file read: `pa-vet-list/pa-vet-clinics.csv`, `pa-vet-list/README.md`.
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the status DRAFT, not a live call.
- ApprovalGateway for gated work (PENDING record) — building the list has no gate.
- No live tool, network, or file write. Outreach (mail/phone) is not this skill's job.

## Gate

- Building the list has no gate — it is safe work.
- But emailing anyone from the list needs the `send` gate, and the email channel is now **PAUSED** (since 2026-11-14 — SPF/DMARC DNS fix pending). No clinic has been emailed, and none can be.

## Honest limits

- **39/100** — 61 remaining. Talvenor has no relationship/agreement with any clinic — this is only a list of public information.
- Contact details are never invented. If there is no email, "Not publicly listed" — that is a gap, it cannot be filled with a guess.
- No clinic can be emailed twice (at launch time).
- Dental/medical is never a target — a vet clinic is animal care, outside the patient-health exclusion.
- **BOSS INPUT REQUIRED:** whether he wants to focus on any new city/area — if he does not say so, work proceeds per the README plan.

## Never does this

- Invents contact details; brings a chain into the list.
- Emails/calls anyone (no outreach); overwrites the CSV — this agent writes no file.

## Worked example (with real repo facts)

- **Task:** `{"type": "clinic_research", "title": "PA list status"}` → `ClinicResearcherAgent.run()`.
- **Agent does:** reads `pa-vet-clinics.csv` — 39 rows, 8 have a public email; counts the city breakdown (Philadelphia 8, York 5, …).
- **Result:** status `draft-ready`; the output has the 39/100 status + the verification rules (official website first, chains excluded: Banfield, VCA, Vetco, BluePearl, Thrive, PetVet365; if there is no email, "Not publicly listed"). Spot-check examples (from the README): Indy Veterinary Care, Philadelphia — on the official site: independent, family-run, (215) 923-2300, info@indyvetcare.com; Love City Vet, Philadelphia — woman-owned, Northern Liberties, (215) 273-3335, NL@lovecityvet.com.
