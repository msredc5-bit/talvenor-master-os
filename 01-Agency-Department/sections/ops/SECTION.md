# Section: Ops — Agency (Phase 7)

**Purpose:** The office's inside work — weekly report, and a paying
client's invoice DRAFT. This section sends nothing, takes no payment —
only accounts and drafts.

**True status (2026-11-16):** Paying client 0. First mail 162. Email PAUSED
(since 2026-11-14, DNS fix pending). Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| ReportCompiler | `engine/workers/src/workers/admin.py` (`ReportCompiler`) | `engine/skills/report-compiler.md` | None | MAPPED |
| BillingInvoiceAgent | `sections/ops/agents/billing_invoice_agent.py` | `sections/ops/skills/billing-invoice-agent.md` | `ok` | NEW (Phase 7) |

## How work flows

1. **ReportCompiler** — weekly performance report: what was posted, best/worst using
   platform numbers that can be seen, lead list (name/platform/message/
   next step), what changes next week. Without numbers, it says "none" and asks Boss to
   paste them — never a guess or invented metric.
2. **BillingInvoiceAgent** — a paying client's invoice DRAFT, only from LOCKED
   pricing (2026-11-12): Starter $547/mo + $597 build; Growth
   $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build. The invoice is only
   for a paying client, on Boss's word. Paying client 0 — without confirmation,
   TEMPLATE only, NOT ISSUED. Never quote a price to a prospect, never collect
   payment.

## Gate

- `ok` (BillingInvoiceAgent): using the invoice needs Boss's "ok".
- None (ReportCompiler): the report itself is safe.

## Honest limits

- All output is DRAFT, mock brain ($0). No metric/number is a guess —
  without a number that can be seen, the report says "none".
- There is no price except LOCKED pricing; no price is told to a prospect.
- No payment collection — no payment link/charge.
- Paying client 0; first mail 162.
