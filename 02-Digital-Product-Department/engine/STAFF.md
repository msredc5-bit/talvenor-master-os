# Digital Product Engine — STAFF.md (staff list)

**Department:** 02-Digital-Product-Department — Vet No-Show Recovery Kit ($49 one-time)
**Chief:** Products Chief of Staff (`chief_of_staff_products.py` — REAL, Phase 2)
**Status (2026-11-16):** Gate 0 **NOT PASSED** — the Lemon Squeezy signup test is Boss's step, still pending.
None of the kit's 6 parts has been built, sale **0**, no launch. PA list **39/100**.

This engine has exactly **7** staff. Nobody sends mail, publishes, spends,
or deletes. For gated work (send / publish / spend / delete), nothing runs
without Boss's exact gate word (ok / "post it" / "upload it" / send / go).

---

## 1. Kit Builder

**What they do:** builds the kit's 6 parts from the blueprint in kit-outline.md — (1) Reminder
Cadence Pack (T-72h / T-24h / T-2h SMS + email + call script), (2) Same-Day
Rebooking Scripts, (3) Waitlist-Fill SOP (one page), (4) No-Show Log + $ Tracker
(Sheets, with formulas), (5) Deposit / No-Show Policy Template (with attorney-review
note), (6) Front-Desk Quick Card (5 lines, one page). All plain US English,
Google Sheets + Docs, $0.

**Inputs:** `kit-outline.md` (blueprint — the only source), research report
`~/workspace/research_notes/digital-product-final-20261112/report.md` §4.1,
Gate 1 check (does the cadence match AAHA/PetDesk guidance).

**Outputs:** DRAFT of the 6 parts (Sheets/Docs) — after Gate 0 passes. Now it
only returns the blueprint, not the kit itself.

**Gate:** Boss's `ok` is needed to start building; `ok` to use the output.

**Gate 0 status:** **BLOCKED** — no part of the kit can be built until Gate 0
passes. The Chief's `kit_build` only returns the blueprint.

## 2. Clinic Researcher

**What they do:** grows the PA vet list toward 100 verified independent clinics.
For each new clinic, verifies name + city + website + public email/phone from
the clinic's own official website (best) or a directory listing and adds it to
`pa-vet-clinics.csv`.

**Inputs:** `pa-vet-list/pa-vet-clinics.csv` (39 rows now), `pa-vet-list/README.md`
(verification rules), Google Maps / directory listing (public information only).

**Outputs:** verified new rows (CSV) + city-breakdown summary. No clinic is emailed/
called — this is only a list, not outreach.

**Gate:** no gate — building a list is safe work. But emailing anyone from the list
needs the `send` gate, and the email channel is now PAUSED (since 2026-11-14).

**Gate 0 status:** **NOT BLOCKED** — the list can be grown outside Gate 0, but
per the plan the remaining 61 clinics will be completed after Gate 0.

**Never does this:** invents contact details — if it is not public, writes "Not publicly
listed". Excludes chains: Banfield, VCA, Vetco/Petco, BluePearl, Thrive,
PetVet365, PetVet Care Centers network. The target is an independent companion-animal
clinic with 1–5 vets, not a corporate chain or a solo mobile vet.

## 3. Launch Manager

**What they do:** builds the launch checklist (DRAFT only) — Gate 0, the kit's 6 parts,
Gate 1 check, Lemon Squeezy listing + Gumroad backup listing, sales page
(Boss review), emailing 100 clinics at 25 a day (4 days), writing replies + sales
in a sheet.

**Inputs:** `kit-outline.md` (Week 0–4 build plan + Gate 0–3 kill criteria),
`gate0-status.md`, PA list status (39/100), the Chief's `launch_prep` output.

**Outputs:** Launch checklist DRAFT — not the launch itself.

**Gate:** Boss's `go` is needed to move the launch forward.

**Gate 0 status:** **BLOCKED** — no launch can happen. The Chief's `launch_prep`
gives only a DRAFT checklist; if `mark_launched` is requested, status `blocked-gate0`
is returned and nothing is recorded as launched.

## 4. Payment-Rails Checker

**What they do:** writes the steps for the Gate 0 test and records Boss's result —
Lemon Squeezy signup (individual, checking whether BD bank payout is available); if it
fails, the fallback order is: **Polar** → **Gumroad** (as an individual, not an LLC). If all
rails are closed, the product track is KILLed — Boss is told.

**Inputs:** `gate0-status.md` (the only true source — unless "Status: PASSED" is
written, it is NOT PASSED), research report §2 (rails verification 2026-11-12):
Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% +
$0.80 effective, $100 min payout.

**Outputs:** Gate 0 test steps + a record of Boss's result (tells Boss to update the
Status line in gate0-status.md — Elora herself never writes Status PASSED
without Boss's result).

**Gate:** no gate — this is only checking + recording.

**Gate 0 status:** **this role watches Gate 0** — but never signs up itself.
Signup is Boss's own ~15-min step (lemonsqueezy.com, as an individual).

**Never does this:** signs up on Lemon Squeezy/Polar/Gumroad itself, never brings Etsy
into the plan (closed for Bangladesh — hard no).

## 5. Support Drafter

**What they do:** writes DRAFT replies to kit buyers' questions — delivery, opening
files, tracker formulas, refund policy, "not legal advice" note — plain US
English, DRAFT only.

**Inputs:** the buyer's real message (Boss will forward it), the kit's 6 parts
(kit-outline.md), research report §7.3 (support load ~10 min/buyer —
ASSUMPTION), refund policy (whatever will be written on the sales page — not
decided yet).

**Outputs:** Reply DRAFT — not sent. It is only sent after Boss reads it and says `send`.

**Gate:** Boss's `send` is needed to send it.

**Gate 0 status:** **BLOCKED (no work now)** — sales are 0, so there are no buyers,
and no support questions either. This role's work starts only after Gate 0 passes
+ the first sale.

**Never does this:** quotes any price outside the locked $49 kit price; does not
quote even $49 to a prospect unless Boss confirms. Invents no client/
testimonial/statistic. Does not present the policy template as legal advice —
always writes "have your own attorney review before using".

---

## True status (2026-11-16)

| Item | Status |
|---|---|
| Staff | 7 (this file) |
| Gate 0 | NOT PASSED — Boss's Lemon Squeezy test pending |
| The kit's 6 parts | None built |
| PA list | 39 / 100 |
| Sale | 0 |
| Wedge (1/20 buyers → $1,109/mo receptionist) | UNTESTED — an estimate, not a fact |

**Source files (nothing copied/moved):** `chief_of_staff_products.py`,
`kit-outline.md`, `gate0-status.md`, `pa-vet-list/README.md` +
`pa-vet-clinics.csv`, `skills/chief-products.md`, `00-CEO-Core/config.json`,
`~/workspace/research_notes/digital-product-final-20261112/report.md`.

---

## Phase 7 — Section map (2026-11-17)

In Phase 7, the 5 staff's work was arranged into 6 sections
(`02-Digital-Product-Department/sections/<section>/` — each with
`agents/` + `skills/` + `SECTION.md`). **2** new staff (Kit QA,
Kit Sales) — total staff now **7**. Section agents write no files,
touch no network, send no mail, and mark nothing as sold/launched.

| Section | Staff | Agent file | Skill file | Gate | NEW / existing |
|---|---|---|---|---|---|
| product | Kit Builder | `sections/product/agents/kit_builder.py` | `sections/product/skills/kit-builder.md` | `ok` | existing role |
| product | Kit QA | `sections/product/agents/kit_qa.py` | `sections/product/skills/kit-qa.md` | `ok` | **NEW** |
| research | Clinic Researcher | `sections/research/agents/clinic_researcher.py` | `sections/research/skills/clinic-researcher.md` | — | existing role |
| launch | Launch Manager | `sections/launch/agents/launch_manager.py` | `sections/launch/skills/launch-manager.md` | `go` | existing role |
| sales | Kit Sales | `sections/sales/agents/kit_sales.py` | `sections/sales/skills/kit-sales.md` | `send` | **NEW** |
| support | Support Drafter | `sections/support/agents/support_drafter.py` | `sections/support/skills/support-drafter.md` | `send` | existing role |
| finance | Payment-Rails Checker | `sections/finance/agents/payment_rails_checker.py` | `sections/finance/skills/payment-rails-checker.md` | — | existing role |

Chief routing (Phase 7 + sweep 2026-11-21): the earlier 4 task types (`kit_build`,
`clinic_research`, `gate0_check`, `launch_prep`) now run through a section agent
(`LEGACY_SECTION_ROUTING` — KitBuilder, ClinicResearcher,
LaunchManager, PaymentRailsChecker) — the Chief's outward contract
(status / output / handler / gate) stays as before. The 3 new types (`kit_sales`,
`kit_qa`, `support_draft`) run in the Chief's `SECTION_ROUTING` — the section agent
is loaded with `importlib.util.spec_from_file_location`, `run()` runs with a mock brain
(`BrainFactory.get_brain("agency")`), and logs to `tasks.json` as before.

**True status after Phase 7 is the same:** Gate 0 **NOT PASSED**, kit **0/6**
built, PA list **39/100**, sale **0**, email **PAUSED**. The section map
changes no fact — only how the work is arranged.
