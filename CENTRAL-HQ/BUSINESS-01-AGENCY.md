# BUSINESS-01 — AI Receptionist Agency OS (Agency Wrapper)

**Date:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, for Boss's review
**Source:** the brief Boss sent, `~/workspace/briefs/unified-business-os-2026-11-19.md` §2 (preserved as-is, not adopted as design — audited below)
**Points at:** `01-Agency-Department/` (the Agency division of the Master OS repo)
**Rule of this file:** wrapper only — no new code, no new workers, nothing live. Point at what exists, write honestly about what does not.

## Audit of the brief (what was wrong, fixed)

| What the brief said | True state |
|---|---|
| AI Engineering: Retell | **Wrong.** Retell DROPPED 2026-10-26 — never production. Live voice stack **Vapi** — Sophia, live receptionist, +1 (947) 223-0244, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3. |
| Agency's own "Master Brain" | **Wrong.** The three businesses have no separate live brains. **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN. The Agency has a Chief (Agency Chief of Staff), not a separate live brain. |
| Agency's own Database | **Wrong.** DB = **JSON store files** (`store/tasks.json`, `store/approvals.json`). No separate database schema exists. |
| Agency CRM | **PLANNED, not live.** CRM = n8n Cloud Data Tables — not live yet. |

## 8 Departments (Phase 1, 2026-11-19)

Source: `01-Agency-Department/agents/agent-registry/registry.md` (69 entries: the brief's 62 roles + 7 existing workers outside the brief) + 8 `departments/*/SECTION.md` files.

| # | Department | Manager | Mapped existing staff | Status |
|---|---|---|---|---|
| 01 | Sales & Growth | Chief Growth Agent | 8 | EXISTING — manager + staff present; Chief wiring Phase 2 |
| 02 | Marketing | Marketing Director Agent | 4 | EXISTING — manager + staff present; Chief wiring Phase 2 |
| 03 | AI Engineering | CTO / AI Engineering Agent | 2 | EXISTING — manager + staff present; Chief wiring Phase 2 |
| 04 | Client Operations | COO / Client Operations Agent | 5 | EXISTING — manager + staff present; Chief wiring Phase 2 |
| 05 | Research & Strategy | Chief Strategy Agent | 7 | EXISTING — manager + 7 specialists present (Phase 3, 2026-11-19); Chief wiring Phase 2 DONE 2026-11-19 |
| 06 | Finance & Admin | CFO / Finance Agent | 2 | EXISTING — manager + staff present; Chief wiring Phase 2 |
| 07 | Quality & Security | Chief Quality & Security Agent | 1 | EXISTING — manager + staff present (QAEngineer, shared with dept 03); Chief wiring Phase 2 |
| 08 | Product & Innovation | Chief Innovation Agent | 6 | EXISTING — manager + 6 specialists present (Phase 3, 2026-11-19); Chief wiring Phase 2 DONE 2026-11-19 |

**Count:** 69 entries total — EXISTING 69, ROLE-ONLY 0, GAP 0 (4 GAP workers built on 2026-11-21). QAEngineer is counted in two departments (dept 03 + dept 07, same worker) — so **21** separate workers (15 engine workers + 6 section agents). All 8 managers are EXISTING (`.py` + skill files on disk), and **Chief wiring Phase 2 DONE 2026-11-19** — the Agency Chief calls the 8 managers via DEPARTMENT_ROUTING; managers are not standalone.

**GAP departments now 0:** the specialists of Research & Strategy (7 staff) and Product & Innovation (6 staff) were built in Phase 3 (2026-11-19) — these two departments were GAP before, not anymore.

## 5 Sections + 21 staff (Phase 7)

Source: `00-CEO-Core/config.json` (Phase 7) + registry.

| Section | Section agent (verified) | Gate |
|---|---|---|
| receive | ClientIntakeReceiver (`client_intake`) | `send` |
| sell | SalesCloser (`sales_close`), FollowUpAgent (`followup_draft`) | `ok` / `send` |
| delivery | ServiceDeliveryManager (`delivery_manage`), ClientSuccessAgent (`client_success`) | `ok` / `send` |
| marketing | Section exists; section agent file not verified in this task | — |
| ops | BillingInvoiceAgent (`billing_invoice`) | `ok` |

Plus the engine's **15 workers** (`01-Agency-Department/engine/workers/`) — **21 staff** total (15 workers + 6 section agents). All run on the mock brain ($0), DRAFT-only — nobody sends, posts, or deploys anything.

**FollowUpAgent — 100-mail rule: PARKED.** First mails in Pennsylvania: 37 — no follow-up in a state until 100 first mails in that state (Boss's 2026-11-10 rule).

## Agency's own Assets (brief §2 — with honest status)

| Asset (brief's name) | Real state | Status |
|---|---|---|
| Agency CRM | n8n Cloud Data Tables — **PLANNED, not live**. Without a CRM there is no CRM manager worker. | READY NOT LIVE |
| Client Database | Leads-organized filing + `store/` (JSON store files). No separate client database — paying clients 0. | BUILT (filing + store) |
| Agent Development Workspace | `01-Agency-Department/engine/workers/` — 15 workers vendored (`~/workspace/boss-ceo/` upstream, no longer a runtime dependency). | BUILT |
| Client Delivery Pipeline | `workflows/` — 5 workflow files. n8n workflows **READY, NOT LIVE** — Boss's import + test remaining. | READY NOT LIVE |
| Agency Finance Records | LOCKED pricing (internal only, 2026-11-12) + BillingInvoiceAgent — **invoices only for paying clients, on Boss's word**. Clients 0 — no invoice made yet. | BUILT (template only) |
| Agency Knowledge Base | `engine/skills/` + SOPs (Talvenor office SOPs). | BUILT |

**Pricing LOCKED, internal only (never quote to a prospect):** Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build.

**Live voice product:** Vapi — Sophia, live receptionist, +1 (947) 223-0244. Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (Talvenor Demo, 15 min, New York Time).

## True state (Real Status Block — 2026-11-19)

| Item | State |
|---|---|
| Email outreach | **PAUSED** — since 2026-11-14 (SPF/DMARC DNS fix still with Boss) |
| First mail | **163** |
| Paying client | **0** |
| Revenue | **$0** |
| Spend cap | **$0** |
| Brain | Mock default ($0); live MetaSpark UNPROVEN |
| GAP departments | 0 — Research & Strategy (7 staff) and Product & Innovation (6 staff) specialists built in Phase 3 |
| Chief wiring | **Phase 2 — DONE 2026-11-19**. The Agency Chief calls the 8 managers via DEPARTMENT_ROUTING |
| Dental/medical | Never a target — always DQ |
| Gates | ON — `ok` / `"post it"` / `send` / `go` / `"upload it"`; no send/publish/spend/delete without Boss's exact word |

## Next steps (on Boss's decision)

1. **Phase 2 — Chief wiring:** ✅ DONE 2026-11-19 — 8 managers connected to the Agency Chief via DEPARTMENT_ROUTING.
2. **Email restart:** once Boss applies the DNS fix (SPF + DMARC) and says "check koro" — only then think about the Day 4/Day 5 drafts (25 + 25, READY, unsent).
3. **GAP departments:** ✅ DONE — Research & Strategy and Product & Innovation workers built in Phase 3 (2026-11-19) + GAP build (2026-11-21); GAP departments now 0.
4. **First paying client:** the Agency's only real goal — clients from 0 to 1.

## What this wrapper does not do

- Builds no worker/manager, does no wiring.
- Contacts no client, sends no mail.
- Tells no price to any prospect, gives no guarantee, uses no invented client/testimonial/stat.
