# Section: Ops — Agency (Phase 7)

**উদ্দেশ্য (purpose):** Office-র ভেতরের কাজ — সাপ্তাহিক report, আর paying
client-এর invoice DRAFT। এই section কিছু পাঠায় না, payment নেয় না —
শুধু হিসাব আর draft।

**সত্য অবস্থা (2026-11-16):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| ReportCompiler | `engine/workers/src/workers/admin.py` (`ReportCompiler`) | `engine/skills/report-compiler.md` | None | MAPPED |
| BillingInvoiceAgent | `sections/ops/agents/billing_invoice_agent.py` | `sections/ops/skills/billing-invoice-agent.md` | `ok` | NEW (Phase 7) |

## কাজের প্রবাহ (how work flows)

1. **ReportCompiler** — সাপ্তাহিক performance report: কী post হয়েছে, দেখা
   যায় এমন platform number দিয়ে best/worst, lead list (নাম/platform/message/
   next step), পরের সপ্তাহে কী বদলাবে। Number না থাকলে "নেই" বলে Boss-কে
   paste করতে বলে — কখনো অনুমান বা বানানো metric নয়।
2. **BillingInvoiceAgent** — paying client-এর invoice DRAFT, শুধু LOCKED
   pricing (2026-11-12) থেকে: Starter $547/mo + $597 build; Growth
   $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build। Invoice শুধু
   paying client-এর জন্য, Boss-এর কথায়। Paying client 0 — confirm না হলে
   TEMPLATE only, NOT ISSUED। Prospect-কে কখনো দাম quote নয়, payment
   collect নয়।

## Gate

- `ok` (BillingInvoiceAgent): invoice ব্যবহার করতে Boss-এর "ok" লাগে।
- None (ReportCompiler): report নিজেই নিরাপদ।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। কোনো metric/সংখ্যা অনুমান নয় —
  দেখা যায় এমন number ছাড়া report-এ "নেই"।
- LOCKED pricing ছাড়া কোনো দাম নেই; prospect-কে দাম বলা হয় না।
- Payment collect নয় — কোনো payment link/charge নেই।
- Paying client 0; প্রথম মেইল 162।
