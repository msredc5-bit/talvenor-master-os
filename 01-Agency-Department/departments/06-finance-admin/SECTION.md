# Department 06: Finance & Admin — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency-র টাকা আর কাগজপত্রের হিসাব —
paying client-এর invoice DRAFT, revenue/subscription tracking-এর ভাবনা,
আর দেখা যায় এমন number দিয়ে financial report। এই department payment
নেয় না, invoice issue করে না — manager শুধু task-কে specialist-এর
কাছে route করার DELEGATION PLAN-এর DRAFT বানায়।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। $0 spend cap — কোনো
খরচ নেই। Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
ফোন +1 (947) 223-0244।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| CFOFinanceAgent | `departments/06-finance-admin/manager/cfo_finance_agent.py` | `departments/06-finance-admin/skills/cfo-finance-agent.md` | `ok` |

Manager-এর কাজ: `manage_finance_admin` — task_kind দেখে specialist ঠিক
করা, delegation plan-এর DRAFT বানানো। Worker execute নয়, invoice issue
নয়, payment নয়। Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| BillingInvoiceAgent | `billing_invoice` | `sections/ops/agents/billing_invoice_agent.py` | `ok` | EXISTING |
| ReportCompiler | `report_compile` | `engine/workers/src/workers/admin.py` | None | EXISTING |

- **BillingInvoiceAgent** — invoice DRAFT, শুধু LOCKED pricing (2026-11-12)
  থেকে: Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build;
  Scale $1,672/mo + $1,997 build। Invoice শুধু paying client-এর জন্য,
  Boss-এর কথায়। Paying client 0 — confirm না হলে TEMPLATE only, NOT
  ISSUED। Prospect-কে কখনো দাম quote নয়, payment collect নয়।
- **ReportCompiler** — সাপ্তাহিক performance report: কী post হয়েছে, দেখা
  যায় এমন platform number দিয়ে best/worst, lead list, পরের সপ্তাহে কী
  বদলাবে। Number না থাকলে "নেই" — কখনো অনুমান বা বানানো metric নয়।

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Revenue Tracking Agent | ROLE-ONLY | Role definition only — revenue-র হিসাব রাখার ভাবনা; paying client 0, তাই track করার revenue এখনো নেই। |
| Expense Tracking Agent | GAP | $0 spend cap — কোনো expense নেই, তাই track করার কিছু নেই; worker-ও নেই, skill-ও নেই। |
| Invoice Management Agent | EXISTING | BillingInvoiceAgent-ই করে (`billing_invoice` / `invoice_management`, gate `ok`)। |
| Subscription Tracking Agent | ROLE-ONLY | Role definition only — subscription-র হিসাব; paying client 0, তাই track করার subscription এখনো নেই। |
| Financial Reporting Agent | EXISTING | ReportCompiler-ই করে (`report_compile` / `financial_reporting`, no gate) — visible metrics only। |
| Document Management Agent | ROLE-ONLY | Role definition only — Agency document সাজানো; worker নেই। |
| Compliance Calendar Agent | ROLE-ONLY | Role definition only — deadline/compliance তারিখের হিসাব; worker নেই। |

## Missing roles (worker নেই)

- Expense Tracking Agent — GAP ($0 spend cap, কোনো expense নেই)।
- Revenue Tracking, Subscription Tracking, Document Management, Compliance
  Calendar — ROLE-ONLY: role definition আছে, worker নেই, skill .md
  registry-তে এখনো বানানো হয়নি।

## Gate

- `ok` (CFOFinanceAgent, BillingInvoiceAgent): delegation plan / invoice
  ব্যবহার করতে Boss-এর "ok" লাগে।
- None (ReportCompiler): report নিজেই নিরাপদ।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। Delegation plan-ই শেষ কথা — execution নয়।
- LOCKED pricing (2026-11-12) internal only — prospect-কে কখনো দাম quote নয়।
- Payment collect নয় — কোনো payment link/charge নেই।
- কোনো metric/সংখ্যা অনুমান নয় — দেখা যায় এমন number ছাড়া report-এ "নেই"।
- $0 spend cap — কোনো খরচ নেই, কোনো expense track করার নেই।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
