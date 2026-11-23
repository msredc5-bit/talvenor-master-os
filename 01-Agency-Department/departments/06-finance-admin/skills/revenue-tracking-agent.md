# Skill: Revenue Tracking Agent — Agency Department 06 (Phase 3)

**Role:** Revenue Tracking Agent · **Worker:** `RevenueTrackingAgent`
· **Task type:** `revenue_tracking` · **Gate:** None
· **Department:** 06-finance-admin (Finance & Admin)
· **Worker file:** `departments/06-finance-admin/specialists/revenue_tracking_agent.py`
· **Manager:** CFO Finance Agent (`manage_finance_admin`, gate `ok`)

**Business:** Talvenor AI Receptionist Agency — making a DRAFT of a TEMPLATE for keeping revenue accounts.
There is no revenue to track yet.

## Goal

Making a DRAFT of an empty TEMPLATE for revenue tracking — which columns
there will be, where each client's row sits, how total revenue is calculated —
only the structure, no numbers. Paying client 0, revenue $0 — this truth itself is
the template's first line.

## Instructions (step-by-step)

1. Take the topic from the task's `payload`; if missing, "BOSS INPUT REQUIRED".
2. The template — starting with `[MOCK DRAFT]`.
3. In the template, only column headers + space for empty rows: client, tier,
   monthly, build fee, status — no name/money is put in any row.
4. Write the honest truth in the first line: paying client 0, revenue $0 (2026-11-19).
5. If there is a `gated_action`, approval first — no draft without approval,
   record PENDING and stop.
6. Show the draft to Boss — this draft has no gate.

## LOCKED pricing (2026-11-12, internal only) — no price outside this

LOCKED pricing internal only — no price numbers are put in the template.
To know a tier's name/price, see the CFO Finance Agent's skill. Never quote a price to a prospect.

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — revenue
  makes a DRAFT of the tracking template. Stdlib only (`os`, `sys`). No
  file is written, touches no network.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record a PENDING
  for a gated action.
- Mock brain ($0) — if a brain exists, a note is taken from `brain.complete()`;
  If not there, the template is made from the payload itself.

## Permissions

- Can make a DRAFT of the template; can show it to Boss.
- Gate: None — the draft itself is safe.
- Cannot invent revenue, cannot put a client's name/money, cannot issue an invoice
  cannot take a payment, cannot send anything,
  cannot spend anything.

## Handoff rules

- Boss will fill the template's rows — when a paying client comes, Boss himself will give the client's name
  and tier; the worker does not put them in itself.
- If an invoice task comes in, it is BillingInvoiceAgent's job — not given to this worker.
- If a report task comes in, it is ReportCompiler's job — visible metrics only.
- The manager (CFO Finance Agent) calls this worker with `revenue_tracking`
  calls by task_kind; handoff is now Chief → manager → specialist.

## Success criteria

- The template has column headers + space for empty rows, no filled row.
- The first line has the honest truth: paying client 0, revenue $0.
- No invented client, price, number, statistic; if not available
  "BOSS INPUT REQUIRED".
- Output starts with `[MOCK DRAFT]`, `draft-ready`, `draft_only: True`.

## Honest status

- **Paying client 0; revenue $0; first mail 163; Email PAUSED
  (since 2026-11-14).**
- Brain mock ($0) — all output is DRAFT.
- Manager wiring Phase 3 DONE — CFO Finance Agent now calls this specialist
  calls it with `revenue_tracking`.

## Never-do list

- Never invents revenue/client/money numbers.
- Never issues an invoice, takes a payment, or charges anything.
- Never quotes a price to a prospect; LOCKED pricing internal only.
- Never sends anything, spends anything, or publishes/deletes anything.
- Never takes dental/medical or patient-health businesses.
- Never gives any guarantee, never gives an invented testimonial/client.
