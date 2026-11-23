# Digital Product Engine — README (one page)

**Department:** 02-Digital-Product-Department — Vet No-Show Recovery Kit
**Chief:** Products Chief of Staff (`chief_of_staff_products.py` — REAL, Phase 2)
**Status: REAL* / BLOCKED** — the engine is real, but building/selling/launching the kit is blocked at Gate 0.

## Product (locked facts)

- **Vet No-Show Recovery Kit — $49 one-time** (launch price $39 for the
  first 30 buyers). Google Sheets + Docs + copy-paste script. No code, no app.
- **For whom:** Independent US vet clinic (animal care — allowed;
  dental/medical-patient targeting EXCLUDED).
- **Pain:** no-show ~11% (AAHA) × average visit ~$200 (AVMA 2025) ≈ **$50k–$150k/yr**
  at risk for a typical clinic. 34,296 practices in the US.
- **The kit's 6 parts:** Reminder Cadence Pack (T-72h/T-24h/T-2h), Same-Day
  Rebooking Scripts, Waitlist-Fill SOP, No-Show Log + $ Tracker, Deposit/
  No-Show Policy Template (with attorney-review note), Front-Desk Quick Card.

## What this engine contains

| Item | Count |
|---|---|
| Staff (`STAFF.md`) | **7** — Kit Builder, Clinic Researcher, Launch Manager, Payment-Rails Checker, Support Drafter, Kit QA, Kit Sales |
| Tools (`tools.json`) | **8** — mock **6** (kit_outline_read, research_notes, draft_email, draft_caption, draft_script, status_read), gated stub **2** (launch_kit — publish, sell_kit — spend) |
| Skills (`skills/`) | **7** — one .md for each staff role (Kit QA + Kit Sales added after the first 5; the old "5" count was stale — corrected Phase 2) |
| Wrapper (`tool_calling.py`) | thin wrapper over the shared core (`00-CEO-Core/tool_calling.py`) — `call()` + `list_tools()` |

## What is blocked, and on whom

- **Gate 0 — NOT PASSED.** Lemon Squeezy signup test is Boss's own ~15-min
  step (lemonsqueezy.com, as an individual, checking whether BD bank payout
  is available). Until Boss reports the result, kit build / sale / launch are
  all BLOCKED. If it fails, the fallback order is: **Polar → Gumroad**
  (individual). If all rails are closed, the product track is KILLed entirely.
  **Etsy is never in the plan** (closed for Bangladesh).
- **PA vet list 39/100** — the remaining 61 clinics will be completed after
  Gate 0. No clinic has been emailed; email channel PAUSED (since 2026-11-14).
- **Sale 0.** Wedge (1/20 kit buyers → $1,109/mo receptionist) **UNTESTED** —
  an estimate, not a fact. $10K/mo verdict: the kit alone will not deliver it
  in 6–12 months; credible $300–$1,000/mo (6–20 sales/mo), if Gate 2 passes.

## Rules (always)

- Gated work (send / publish / spend / delete) — nothing runs without Boss's
  exact gate word (ok / "post it" / "upload it" / send / go). No auto-approve.
- $0 spend cap. No client/testimonial/statistic is invented. Brand =
  Talvenor only. No clinic is emailed.
- Source files: `chief_of_staff_products.py`, `kit-outline.md`,
  `gate0-status.md`, `pa-vet-list/` (README + CSV), `skills/chief-products.md`,
  `00-CEO-Core/config.json`,
  `~/workspace/research_notes/digital-product-final-20261112/report.md`.

## Files

- `STAFF.md` — 5 staff roles
- `tools.json` — 8-tool registry
- `skills/kit-builder.md`, `skills/clinic-researcher.md`,
  `skills/launch-manager.md`, `skills/payment-rails-checker.md`,
  `skills/support-drafter.md`
- `tool_calling.py` — thin wrapper
- `README.md` — this file
