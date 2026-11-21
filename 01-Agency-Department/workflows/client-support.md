# Workflow 5 — Client Support

**Department:** 04 Client Operations (+ 06 Finance & Admin — billing/reporting)
**Date:** 2026-11-19 | **Status:** READY — but **0 clients, so unexercised (not run).**

## Purpose

Supporting a live client, invoicing, giving a monthly report, and keeping the client — all draft-first, Boss's gate on every send.

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Support Agent (`ClientSuccessAgent`) | 04 | EXISTING — support draft |
| Invoice Management Agent (`BillingInvoiceAgent`) | 06 | EXISTING — invoice (paying client only) |
| Financial Reporting Agent (`ReportCompiler`) | 06 | EXISTING — visible metrics only |
| Client Reporting Agent | 04 | EXISTING — `departments/04-client-operations/specialists/client_reporting.py` (`client_reporting`) |
| Retention Agent | 04 | EXISTING — `departments/04-client-operations/specialists/retention.py` (`retention`) |
| Renewal & Upsell Agent | 04 | EXISTING — `departments/04-client-operations/specialists/renewal_upsell.py` (`renewal_upsell`) |

## True status

- **Paying client 0** — this workflow has not run on any real client yet. READY but unexercised.
- **Billing LOCKED pricing, internal only** — the invoice has only what Boss confirmed; never quoted to a prospect.
- **Monthly reporting: visible metrics only** — only what can be seen; never an estimate/invent.

## Step-by-step

### Step 1 — Support draft (ClientSuccessAgent)

1. Read the client's problem/question (it comes from inbox triage).
2. Write a **support reply DRAFT** — plain US English, the problem's solution or the next step, one CTA.
3. Write no price, guarantee, or invented solution. If you do not know, **CLIENT INPUT REQUIRED** / ask Boss — no guessing.
4. **Gate:** sending a reply needs `send` — Boss's exact word. DRAFT only — it cannot be sent without the send gate.

### Step 2 — Billing / invoice (BillingInvoiceAgent)

1. **An invoice is only for a paying client, on Boss's word.** Client 0 — no invoice has been made yet.
2. In the invoice draft: tier, build fee, included minutes, month — per the LOCKED pricing Boss confirmed.
3. **Gate:** an invoice needs `ok` — Boss's exact word.

### Step 3 — Monthly reporting (ReportCompiler)

1. At month's end, build the report with **visible metrics only**:
   - how many calls came, how many bookings happened (if visible)
   - what is going well, what needs fixing
2. Without a metric, write **"waiting-for-metrics"** — never an estimate/invent.
3. **Gate:** report compiling has no gate — reading/writing work.

### Step 4 — Retention / renewal (workers exist — DRAFT plan only)

1. **Workers exist for Retention Agent, Renewal & Upsell Agent, and Client Reporting Agent** (EXISTING, Phase 3, 2026-11-19) — they build DRAFT plans, send nothing.
2. Client 0 — retention/renewal work has not started at all yet.
3. When a client comes: tell Boss before renewal, write a draft, send nothing without Boss's `ok`.

## Honest status

- Support draft worker exists, invoice worker exists, reporting worker exists — but **because of 0 clients, none has run on a real client**.
- Retention/renewal/reporting workers exist (EXISTING) — but because of 0 clients, none has run on a real client.

## Missing inputs

- **First paying client** — without a client, support/billing/reporting never starts.
- The client's call/booking metrics (no report without visible metrics).
- Retention/renewal workers exist (EXISTING); without a client, retention/renewal work never starts.
- Boss's `send` / `ok` at every outward step.
