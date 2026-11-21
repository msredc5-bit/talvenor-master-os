# Skill: Launch Manager

**Role:** Build the Vet Kit launch checklist (DRAFT only) — Gate 0, the kit's 6 parts, Gate 1 check, store listing, sales page, emailing 100 clinics, writing replies + sales in a sheet.
**Agent:** `sections/launch/agents/launch_manager.py` — `LaunchManagerAgent` (task kind `launch_prep`, section `launch`)
**Status: BLOCKED** — Gate 0 NOT PASSED. No launch can happen; only a DRAFT checklist.

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (launch price **$39** for the first 30 buyers). Format: Google Sheets + Google Docs + copy-paste script.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets. Not a corporate chain, not a solo mobile vet.
- **Launch plan (kit-outline.md Week 0–4):** Week 0 Gate 0 → Week 1 validate + PA list 100 → Week 2 kit build → Week 3 store + sales page → Week 4 launch (25 emails/day to 100 clinics, 4 days).
- **Gate 2 (kill criteria):** at 100 emails, ≥2% reply rate AND ≥1 sale — if 0 replies at 100 emails, stop email, vet Facebook groups for 2 weeks; if still 0, KILL.

## Inputs

- `02-Digital-Product-Department/kit-outline.md` (Week 0–4 build plan + Gate 0–3 kill criteria)
- `02-Digital-Product-Department/gate0-status.md` (the only true source — unless "Status: PASSED" is written, it is NOT PASSED)
- PA list status: 39/100 (`pa-vet-list/pa-vet-clinics.csv`)

## Step-by-step method (checklist DRAFT)

1. **Gate 0 passed** (does the Lemon Squeezy store open?) — still NOT PASSED.
2. **The kit's 6 parts built** (Sheets + Docs + script) — not done yet (0/6).
3. **Cadence checked against AAHA/PetDesk guidance (Gate 1)** — not done yet.
4. **Lemon Squeezy listing + Gumroad backup listing** — not done yet.
5. **Sales page** — Boss will review before launch.
6. **Email 100 clinics, 25 a day (4 days)** — email channel is now PAUSED (since 2026-11-14).
7. **Write every reply + sale in a sheet** — sales are still 0.

## Output format

- Launch checklist DRAFT (7 steps) + Gate 0 status + kit 0/6 + PA 39/100 + sale 0.
- Status: `blocked-gate0` until Gate 0 passes — no launch has happened, and it cannot happen.

## Tools used

- Read-only file read: `kit-outline.md`, `gate0-status.md`, `pa-vet-list/pa-vet-clinics.csv`.
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the checklist DRAFT, not a live call.
- ApprovalGateway for gated work (PENDING record).
- No live tool, network, or file write. Sending mail is not this skill's job.

## Gate

- Boss's `go` is needed to move the launch forward.
- No launch can happen until Gate 0 passes — the agent only gives a DRAFT checklist; if `mark_launched` is requested, status `blocked-gate0` is returned and nothing is recorded as launched.

## Honest limits

- **Gate 0 BLOCKED** — no launch has happened. Email PAUSED — emailing 100 clinics has not started yet.
- Kit 0/6, PA list 39/100, sale 0.
- $10K/mo verdict: the kit alone will not deliver it in 6–12 months; credible $300–$1,000/mo (6–20 sales/mo), if Gate 2 passes. Wedge (1/20 buyers → $1,109/mo receptionist) UNTESTED.

## Never does this

- Launches; honors mark_launched / mark_sold; records a sale.
- Sends mail; writes any file; invents a client/testimonial/statistic.

## Worked example (with real repo facts)

- **Task:** `{"type": "launch_prep", "title": "Launch checklist"}` → `LaunchManagerAgent.run()`.
- **Agent does:** reads `gate0-status.md` — Status NOT PASSED; writes the checklist's 7 steps (Gate 0, 6 parts, Gate 1, two listings, sales page, 25×4 emails, reply/sale sheet).
- **Result:** status `blocked-gate0`; the output has the DRAFT checklist + "Gate 0: NOT PASSED. Kit built: 0/6. PA list: 39/100. Sale: 0." No launch has happened.
