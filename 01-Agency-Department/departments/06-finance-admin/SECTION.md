# Department 06: Finance & Admin — Agency (Phase 1)

**Purpose:** Talvenor Agency's money and paperwork accounting —
a paying client's invoice DRAFT, thinking on revenue/subscription tracking,
and a financial report with visible numbers. This department takes no payment
and issues no invoice — the manager only
makes a DRAFT of the DELEGATION PLAN for routing the task to the specialist.

**Honest status (2026-11-19):** Paying client 0. First mail 163. Email PAUSED
(since 2026-11-14, DNS fix pending). Brain mock ($0). $0 spend cap — no
spending. Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
Phone +1 (947) 223-0244. (Live source for these numbers:
`00-CEO-Core/config.json` honest_status — the manager and the
Revenue/Subscription agents read it at run time, Phase 2.)

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| CFOFinanceAgent | `departments/06-finance-admin/manager/cfo_finance_agent.py` | `departments/06-finance-admin/skills/cfo-finance-agent.md` | `ok` |

The manager's job: `manage_finance_admin` — pick the specialist by task_kind.
For the 5 Phase 3 standalone specialists (Revenue, Expense, Subscription,
Document, Compliance) it loads and RUNS the specialist with importlib and
returns the specialist's DRAFT — that IS worker execution, DRAFT only.
For the section/engine old workers (BillingInvoiceAgent, ReportCompiler)
it makes a DRAFT of the delegation plan only — no execution, no invoice
issue, no payment. (Phase 2 correction: this doc used to say "No worker
execution" — that was wrong for the 5 specialists; the code always ran them.)

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| BillingInvoiceAgent | `billing_invoice` | `sections/ops/agents/billing_invoice_agent.py` | `ok` | EXISTING |
| ReportCompiler | `report_compile` | `engine/workers/src/workers/admin.py` | None | EXISTING |

- **BillingInvoiceAgent** — invoice DRAFT, only from the LOCKED pricing (2026-11-12)
  — Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build;
  Scale $1,672/mo + $1,997 build. An invoice is only for a paying client,
  on Boss's word. Paying client 0 — if not confirmed, TEMPLATE only, NOT
  ISSUED. Never quote a price to a prospect, never collect a payment.
- **ReportCompiler** — weekly performance report: what was posted, visible
  platform numbers for best/worst, lead list, what changes next week.
  If there is no number, "none" — never a guess or invented metric.

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Revenue Tracking Agent | EXISTING | `departments/06-finance-admin/specialists/revenue_tracking_agent.py` (`revenue_tracking`, gate None) — revenue $0, template only; paying client 0, so there is no revenue to track yet. |
| Expense Tracking Agent | EXISTING | `departments/06-finance-admin/specialists/expense_tracking_agent.py` (`expense_tracking`, gate None) — entry DRAFT + monthly report only; ledger empty ($0 spent); no spend approval. |
| Invoice Management Agent | EXISTING | BillingInvoiceAgent does it (`billing_invoice` / `invoice_management`, gate `ok`) — Phase 2: `invoice_management` is an alias of `billing_invoice` (one definition, resolved in the manager), not a second worker. |
| Subscription Tracking Agent | EXISTING | `departments/06-finance-admin/specialists/subscription_tracking_agent.py` (`subscription_tracking`, gate None) — Vapi free credit, paid total UNKNOWN (no source field — Phase 2, was "$0"); no subscription/cost invented. |
| Financial Reporting Agent | EXISTING | ReportCompiler does it (`report_compile` / `financial_reporting`, no gate) — Phase 2: `financial_reporting` is an alias of `report_compile` (one definition, resolved in the manager), not a second worker. |
| Document Management Agent | EXISTING | `departments/06-finance-admin/specialists/document_management_agent.py` (`document_management`, gate None) — organisation draft only; no file is written/moved. |
| Compliance Calendar Agent | EXISTING | `departments/06-finance-admin/specialists/compliance_calendar_agent.py` (`compliance_calendar`, gate None) — attorney review deferred; no deadline invented. |

## Missing roles (no worker)

- No missing role — Expense Tracking Agent built on 2026-11-21 (skill + worker EXISTING).

Phase 3 DONE (2026-11-19): Revenue Tracking, Subscription Tracking,
Document Management, Compliance Calendar — all 4 are EXISTING now
(specialist worker + skill .md exist, the CFO Finance Agent runs them).

## Gate

- `ok` (CFOFinanceAgent, BillingInvoiceAgent): delegation plan / invoice
  Boss's "ok" is needed to use it.
- None (ReportCompiler): the report itself is safe.

## Honest limits

- All output is DRAFT, mock brain ($0). For the section/engine old workers
  the delegation plan is the final word — no execution. The 5 Phase 3
  standalone specialists ARE run by the manager (DRAFT only) — see above.
- LOCKED pricing (2026-11-12) internal only — never quote a price to a prospect.
- No payment collection — no payment link/charge.
- No metric/number is a guess — without a visible number, the report says "none".
- $0 spend cap — no spending, no expense to track.
- Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.
- Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).
