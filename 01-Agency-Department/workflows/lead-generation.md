# Workflow 1 — Lead Generation

**Department:** 01 Sales & Growth (+ 05 Research & Strategy support)
**Date:** 2026-11-19 | **Status:** LIVE (ongoing) — discovery + verification + qualification run by hand + worker; filing happens in `leads-organized`.

## Purpose

Finding, verifying, scoring, and filing US home-service businesses (plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet) in `leads-organized` — so outreach only goes to the shops that seem to need a receptionist.

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Lead Research Agent (`ProspectResearcher`) | 01 | EXISTING — builds research notes |
| Google Maps Prospect Finder | 01 | EXISTING — `departments/01-sales-growth/specialists/google_maps_prospect_finder.py` (`maps_prospect_find`) — discovery plan DRAFT |
| Business Verification Agent | 01 | EXISTING — `departments/01-sales-growth/specialists/business_verification_agent.py` (`business_verify`) |
| Lead Scoring Agent | 01 | EXISTING — `departments/01-sales-growth/specialists/lead_scoring_agent.py` (`lead_score`; STRONG ≥80 → Tier 1, 60–79 → Tier 2, MEDIUM caps Tier 2, WEAK → Tier 4) |
| Niche Selection Agent | 05 | EXISTING — `departments/05-research-strategy/specialists/niche_selection_agent.py` (`niche_selection`) |
| Competitor Research Agent | 05 | EXISTING — `departments/05-research-strategy/specialists/competitor_research_agent.py` (`competitor_research`) |

## True status (2026-11-19)

- **Lead pool: 507 rows** — Tier 1: 2, Tier 2: 505. Files: `~/workspace/talvenor/leads-organized/` (state-wise folders: PA, TX, GA, FL, CA, NC, IL, MI, OH, NY).
- **First mail 162** — PA 39, TX 15, GA 16, FL 54, CA 14, NC 5, IL 9, MI 5, OH 1, NY 4.
- **Email PAUSED since 2026-11-14** — no mail goes to new leads, only discovery/filing continues.

## Step-by-step

### Step 1 — Discovery

1. Find businesses by niche + state/city from **Google Maps / Google Search / directory** (e.g. "plumbers in Dallas TX").
2. Pull lists with **Apify / Places** where possible — take the Apify actor's output as CSV.
3. Note each business's name, city/state, website, phone. If something is missing, write **NOT_FOUND** — never invent it.
4. **Gate:** no gate — research is reading/searching work, not send/publish.

### Step 2 — Verification

1. **Is there a website?** Open it and check — is it a real service business, what is the service area, does the phone number match the website.
2. **Phone:** note the number given on the website/Google. Do not invent a number yourself.
3. **Contact:** take the owner's name / contact email only if it is on the website or a public listing. Email cannot be guessed.
4. **A dental/medical business is never a target** — on seeing one, DQ (disqualify); do not put it on the list.
5. **Gate:** no gate — verification work.

### Step 3 — Qualification / Scoring (SOP 11-signal scoring)

1. Score with **11 signals**: website exists, phone exists, service area clear, owner/contact found, review/presence, signals that a receptionist is needed (e.g. hints of missed calls, "call us" reliance), etc.
2. Give **STRONG / MEDIUM / WEAK**:
   - **STRONG → Tier 1** (the best — only 2 in the pool now)
   - **MEDIUM → Tier 2** (most of the pool — 505)
   - **WEAK → Tier 4**
3. MEDIUM never goes above Tier 2; WEAK stays at Tier 4.
4. **Gate:** no gate — scoring work.

### Step 4 — Filing (putting into leads-organized)

1. Add the row to the right CSV in the state-wise folder. Do not file the same business twice — search first.
2. In every row: business name, city/state, website, phone, contact (if found), tier, score signal, source, date.
3. **Never delete any row** — if wrong, write it in the status column (e.g. `dead` / `bounced` / `DQ`); do not erase the row.
4. **Gate:** filing has no gate, but Boss's `ok` is needed before going to outreach (see Workflow 2).

## Honest status

- Discovery + verification + qualification **ongoing, workers' DRAFT output + hand verification** — worker code exists for Google Maps Finder, Verification, Scoring (EXISTING, Phase 3, 2026-11-19); workers build DRAFTs, filing is done by hand.
- Of the pool's 507 rows, Tier 1 is only 2 — most are Tier 2.
- A dental/medical business is never a target — always DQ.

## Missing inputs

- Google Maps Finder / Verification / Scoring worker + skill exist (EXISTING, Phase 3, 2026-11-19) — not a live Maps/API call, DRAFT plan only.
- CRM is not live (n8n Cloud Data Tables PLANNED) — filing still happens in CSV.
- No lead's email/phone can be guessed — if not found, NOT_FOUND.
