# Skill: Chief of Staff — Digital Product

**Role:** Chief of the Vet No-Show Recovery Kit ($49 one-time) — listing,
keeping the kit blueprint, drafting the launch checklist, watching Gate 0.
**Status: REAL (Phase 2)** — the Chief module does real work, but the kit
being built/sold/launched is stuck at Gate 0.

## Inputs

- Routed task from the Main CEO Bot
- Gate 0 result — `02-Digital-Product-Department/gate0-status.md`
  (the only source; NOT PASSED unless "Status: PASSED" is there)
- Kit blueprint — `02-Digital-Product-Department/kit-outline.md`
- PA vet list — `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv`
- Research report — `~/workspace/research_notes/digital-product-final-20261112/report.md`

## Outputs

- Kit blueprint (the design) — not the kit itself
- PA list summary — verified rows only
- Launch checklist DRAFT — not a launch
- Gate 0 status — read from gate0-status.md
- Sale / reply report — real numbers only (sale 0 now)

## Routing table (task type → work → gate)

| Task type | Work | Gate |
|---|---|---|
| `kit_build` | Returns the blueprint (kit-outline.md) — not building the kit | `ok` |
| `clinic_research` | PA list summary (row count, cities) | — |
| `gate0_check` | Gate 0's true state | — |
| `launch_prep` | Launch checklist DRAFT — not a launch | `go` |

## Gate — stops here

- **Until Gate 0 passes, the kit cannot be marked launched/sold
  ** — if `mark_launched` / `mark_sold` is asked for, status `blocked-gate0`.
- Sending email needs `send` — this Chief never sends mail.
- Price $49 (launch $39 for the first 30 buyers) — before quoting in public,
  Boss will confirm.
- Dental/medical (patient-health) are never a target — this is animal care.

## Tools (REUSED / rail)

- Lemon Squeezy (once Gate 0 passes) — backup: Polar, then Gumroad
  (individual). Etsy closed — not in the plan.
- Google Sheets / Docs (kit — to be built after Gate 0).
- PA list — 39/100 (2026-11-16, verified).

## True State (Phase 2, 2026-11-16)

- Gate 0 **NOT PASSED** — the Lemon Squeezy test is Boss's step.
- The kit's 6 parts have not been built — only the blueprint exists.
- PA list 39/100 — the remaining 61 after Gate 0.
- Sale 0. $10K/mo verdict: the kit alone will not deliver it (in 6–12 months, $300–$1,000/mo
  credible); wedge (1/20 buyers → receptionist) UNTESTED.
