# Research Section — PA Vet Clinic List

**Purpose:** Grow the PA vet list toward 100 verified independent clinics — official website first, otherwise a directory listing; contact details are never invented.

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Clinic Researcher | `agents/clinic_researcher.py` (`ClinicResearcherAgent`, task `clinic_research`) | `skills/clinic-researcher.md` | — (none) | Existing role — new file as a section agent |

## How work flows

1. Main CEO Bot → Products Chief → `clinic_research` (existing ROUTING branch).
2. Section agent `ClinicResearcherAgent` reads `pa-vet-clinics.csv` (read-only) and reports the status: row count, city breakdown, how many have a public email; writes the verification rules (official website first, chains excluded, "Not publicly listed").
3. Plan for verifying new clinics: the README's city plan (around Pittsburgh, around Harrisburg, Lehigh Valley, Bucks/Montgomery, Pittsburgh suburbs, small Central PA towns).
4. This section emails/calls nobody — this is only a list, not outreach.

## Gates

- Building the list has no gate — it is safe work.
- But emailing anyone from the list needs Boss's `send`, and the email channel is now PAUSED.

## Honest limits

- **PA list 39/100** (verified, 2026-11-16) — the remaining 61 will be completed after Gate 0.
- Of the 39, 8 have a public email; the rest are "Not publicly listed".
- Chains excluded: Banfield, VCA, Vetco, BluePearl, Thrive, PetVet365, PetVet Care Centers network.
- **Gate 0 NOT PASSED, kit 0/6 built, sale 0** — the list can be grown outside Gate 0, but per the plan the remaining 61 come after Gate 0.
- No agent writes a file (no CSV overwrite), touches the network, or invents contact details.
