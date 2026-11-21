# BUSINESS-02 — E-commerce & Digital Product OS (Commerce Wrapper)

**Date:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, for Boss's review
**Source:** the brief Boss sent, `~/workspace/briefs/unified-business-os-2026-11-19.md` §3 (preserved as-is, not adopted as design — audited below)
**Points at:** `02-Digital-Product-Department/` (the real digital-product work) + dropshipping research file
**Rule of this file:** wrapper only — no new code, no new store, nothing live. The brief's 5 divisions are written with honest status; most of what was claimed live is not live.

## Audit of the brief (what was wrong, fixed)

| What the brief said | True state |
|---|---|
| Commerce's own "Commerce Brain" | **Wrong.** The three businesses have no separate live brains. **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN. There is a Products Chief, not a separate live brain. |
| Specialist Agents of the 5 divisions (7–11 agents per division) | **Not built.** No division has an agent worker — only the Vet Kit blueprint + research files exist. |
| Amazon / Shopify / Etsy — as running divisions | **Wrong.** See the table below — Amazon GATED, Shopify PARKED (Boss's direct project), Etsy CLOSED. |
| The brief's 3 images (external diagrams) | **Not used** — external diagrams, not even referenced in this wrapper. |

## 5 Divisions — honest status

| Division | Status | What is real | Next step |
|---|---|---|---|
| Amazon | **GATED** | Nothing — no account, no store, no worker. | Only openable once there are 5 live clients + $5K MRR. Nothing will be built before that. |
| Shopify | **PARKED — Boss's direct project** | Store draft only (single-product dropshipping project opened 2026-10-21). Not an agent-run division — Boss runs it himself. | On Boss's decision — agents do not touch it. |
| Etsy | **CLOSED** | Nothing — Etsy is closed from Bangladesh (verified 2026-11-12). | Never to be built as live. Cannot list on Etsy. |
| Dropshipping | **RESEARCH-ONLY** | Research file only: `~/workspace/research_notes/dropshipping-product-intelligence-2026-10-27.md` (MODE E report, 2026-10-27). No store built, no supplier contacted, no spend. | See the research summary below — no moving forward without validation. |
| Digital Products | **BLOCKED on Gate 0** | Vet No-Show Recovery Kit $49 — **blueprint only** (`02-Digital-Product-Department/kit-outline.md`, 6 parts, 0/6 built). PA vet list 39/100. Sales 0. | Gate 0 — Lemon Squeezy signup test (Boss's ~15-min step). See below. |

## Dropshipping — what the research file actually has (nothing more)

Source: `~/workspace/research_notes/dropshipping-product-intelligence-2026-10-27.md` — only what is written in this file; no product/price added beyond it.

- **Scope:** USA, Shopify dropshipping; 30 candidates reviewed, 10 shortlisted.
- **Top score:** Cat water fountain 84, electric spin scrubber 82, deshedding brush 81, cordless car vacuum 80, rechargeable motion-sensor lights 80.
- **Best low-budget candidate:** Lick mat / slow feeder (cheapest sample, light, does not break).
- **Best evergreen candidate:** Modular drawer organisers.
- **Validation plan (the file's own words):** sample order + organic video first; no paid ads, no inventory purchase, no delivery date promise without a live supplier quote + sample pass.
- **Limits (the file's own admission):** no live marketplace/supplier data was pulled — Amazon, AliExpress, CJdropshipping, TikTok Creative Center, Meta Ad Library were not accessed as primary sources; evidence comes from second-hand roundups. No sales volume, conversion rate, ad cost, or supplier price is claimed as fact. A score means "validate first", not "will sell".
- **What does not exist:** no store, no supplier quote, no sample order, no spend — nothing happened.

## Digital Products — Vet No-Show Recovery Kit $49 (the real product track)

Source: `02-Digital-Product-Department/kit-outline.md` + `gate0-status.md` (**Status line: NOT PASSED, 2026-11-16** — fail-closed).

- **Kit:** $49 one-time (launch price $39 for the first 30 buyers, then $49). Format: Google Sheets + Google Docs + copy-paste scripts. No code, no app.
- **For whom:** Independent US vet clinics, 1–5 vets, buyer = front-desk / practice manager. Not corporate chains, not solo mobile vets.
- **6 parts (0/6 built):** (1) Reminder Cadence Pack, (2) Same-Day Rebooking Scripts, (3) Waitlist-Fill SOP, (4) No-Show Log + $ Tracker, (5) Deposit / No-Show Policy Template (with attorney-review note — not legal advice), (6) Front-Desk Quick Card.
- **PA list:** 39/100 (verified).
- **Sales:** 0. Not launched.
- **$10K/mo verdict (honest):** the kit alone will not give $10K/mo in 6–12 months. Credible: $300–$1,000/mo (6–20 sales/mo), if Gate 2 passes. The only path to $10K/mo is the wedge (1 in 20 buyers taking the $1,109/mo receptionist) — **UNTESTED**.

### Gate 0 — BLOCKED (Boss's step remaining)

- **What Gate 0 is:** whether signup + payout from Bangladesh as an individual works on Lemon Squeezy — test first, then build.
- **Boss's step (~15 min, $0):** sign up on lemonsqueezy.com as an individual (not MAINUDDIN LLC), check the payout method, report the result.
- **If it fails:** test the backup rail — **Polar** (on the BD seller/payout list). If Polar fails too, **Gumroad** (has BD bank payout, must register **as an individual** — not LLC).
- **If all rails are closed:** the product track is a full **KILL** — the kit will not be built.
- **After Gate 0 (if it passes):** complete the PA list to 100, Gate 1 (verify cadence AAHA/PetDesk), build the kit's 6 parts, store listing, launch.

## 7 Shared Departments — mapped to real / planned

The brief §3 shared departments — none is a separate live department; mapped to the real things below.

| Shared Department (brief) | Real map | Status |
|---|---|---|
| Product Research HQ | Dropshipping research file (2026-10-27) + digital-product research report (2026-11-12, `~/workspace/research_notes/digital-product-final-20261112/report.md`) | RESEARCH-ONLY — files exist, no worker |
| Marketing HQ | Agency Marketing dept (01-Agency-Department, dept 02) — serves as an internal project | EXISTING (inside Agency) — Commerce has no separate marketing team |
| Creative Production | Content dept (03-Content-Creation-Department) — serves as an internal project | EXISTING (inside Content) — Commerce has no separate creative team |
| Customer Experience | Client Operations dept (01-Agency-Department, dept 04) | EXISTING — but clients are 0, so there is no customer to serve |
| Finance HQ | CFO manager (Agency dept 06) + LOCKED pricing; revenue $0 | BUILT — no revenue to track |
| Analytics HQ | `dashboards/status.html` + ReportCompiler (visible metrics only — only what can be seen, never estimates) | BUILT — metrics 0 (sales 0, stores 0) |
| Compliance & Risk | Phase 1 governance + platform rules (see below) | BUILT (as rules) — no live operation to enforce on |

## Compliance & Risk — Platform Rules (LOCKED)

- **Etsy CLOSED** (Bangladesh; verified 2026-11-12) — never to be built as live, cannot list on Etsy.
- **Amazon GATED** — nothing built until 5 live clients + $5K MRR.
- **Shopify PARKED** — Boss's direct project; agents do not touch the store.
- **No agent does listing / pricing / refund / account-sensitive work without Boss's approval.**
- **Dental/medical is never a target** — always DQ.
- **No invented sales, prices, stats, or testimonials.** The $49 price must never be claimed to have a verified sale.

## True state (Real Status Block — 2026-11-19)

| Item | State |
|---|---|
| Amazon | GATED — account 0, store 0, worker 0 |
| Shopify | PARKED — Boss's direct project, store draft only |
| Etsy | CLOSED — Bangladesh, verified 2026-11-12 |
| Dropshipping | RESEARCH-ONLY — files exist, stores 0, spend $0 |
| Digital Products (Vet Kit) | BLOCKED on Gate 0 — blueprint exists, kit 0/6, PA list 39/100, sales 0 |
| Revenue (Commerce) | $0 |
| Spend cap | $0 |
| Brain | ONE brain (mock, $0) — no separate Commerce Brain |

## Next steps (on Boss's decision)

1. **Gate 0 test** — Lemon Squeezy signup (Boss's ~15-min step). This is the Commerce track's only open door.
2. If Gate 0 passes: complete the PA list to 100 → Gate 1 → kit build → listing → launch (100 mails).
3. If Gate 0 fails: Polar test → Gumroad test → if all are closed, track KILL.
4. Amazon/Shopify/Etsy — nothing will be done unless Boss says so again.

## What this wrapper does not do

- Builds no store, does no listing, contacts no supplier.
- Tells no price/offer to any prospect, claims no sale.
- Does not show Etsy as live, does not show Amazon as live.
