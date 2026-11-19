# Workflow 5 — Client Support

**Department:** 04 Client Operations (+ 06 Finance & Admin — billing/reporting)
**তারিখ:** 2026-11-19 | **Status:** READY — কিন্তু **0 client, তাই unexercised (চালানো হয়নি)।**

## Purpose (উদ্দেশ্য)

Live client-কে support দেওয়া, invoice করা, মাসিক report দেওয়া, আর client-কে ধরে রাখা — সব draft-first, Boss-এর gate প্রতিটা send-এ।

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Support Agent (`ClientSuccessAgent`) | 04 | EXISTING — support draft |
| Invoice Management Agent (`BillingInvoiceAgent`) | 06 | EXISTING — invoice (paying client only) |
| Financial Reporting Agent (`ReportCompiler`) | 06 | EXISTING — visible metrics only |
| Client Reporting Agent | 04 | ROLE-ONLY |
| Retention Agent | 04 | ROLE-ONLY — worker নেই |
| Renewal & Upsell Agent | 04 | ROLE-ONLY — worker নেই |

## সত্য অবস্থা

- **Paying client 0** — এই workflow এখনো কোনো real client-এ চলেনি। READY কিন্তু unexercised।
- **Billing LOCKED pricing, internal only** — invoice-এ Boss যেটা confirm করেছেন সেটাই; prospect-কে কখনো quote নয়।
- **Monthly reporting: visible metrics only** — যা দেখা যায় তাই; কখনো estimate/invent নয়।

## Step-by-step

### ধাপ ১ — Support draft (ClientSuccessAgent)

1. Client-এর সমস্যা/প্রশ্ন পড়ুন (inbox triage থেকে আসে)।
2. **Support reply-এর DRAFT** লিখুন — plain US English, সমস্যার সমাধান বা পরের step, একটা CTA।
3. কোনো price, guarantee, invented সমাধান লিখবেন না। না জানলে **CLIENT INPUT REQUIRED** / Boss-কে জিজ্ঞেস করুন — guess নয়।
4. **Gate:** reply পাঠাতে `send` লাগে — Boss-এর exact word। DRAFT only — send gate ছাড়া পাঠানো যাবে না।

### ধাপ ২ — Billing / invoice (BillingInvoiceAgent)

1. **Invoice শুধু paying client-এর জন্য, Boss-এর কথায়।** Client 0 — এখনো কোনো invoice বানানো হয়নি।
2. Invoice draft-এ: tier, build fee, included minutes, month — Boss-এর confirm করা LOCKED pricing অনুযায়ী।
3. **Gate:** invoice-তে `ok` লাগে — Boss-এর exact word।

### ধাপ ৩ — Monthly reporting (ReportCompiler)

1. মাস শেষে **visible metrics only** দিয়ে report বানান:
   - কত call এসেছে, কত booking হয়েছে (যদি দেখা যায়)
   - কী ভালো চলছে, কী ঠিক করতে হবে
2. Metric না থাকলে **"waiting-for-metrics"** লিখুন — কখনো estimate/invent নয়।
3. **Gate:** report compile-এ gate নেই — পড়া/লেখার কাজ।

### ধাপ ৪ — Retention / renewal (ROLE-ONLY — worker নেই)

1. **Retention Agent ও Renewal & Upsell Agent ROLE-ONLY** — কোনো worker নেই।
2. Client 0 — retention/renewal-এর কাজ এখনো শুরুই হয়নি।
3. Client এলে: renewal-এর আগে Boss-কে জানান, draft লিখুন, Boss-এর `ok` ছাড়া কিছু পাঠাবেন না।

## Honest status

- Support draft worker আছে, invoice worker আছে, reporting worker আছে — কিন্তু **0 client বলে কোনোটাই real client-এ চলেনি**।
- Retention/renewal-এর কোনো worker নেই (ROLE-ONLY)।

## Missing inputs (যা নেই)

- **প্রথম paying client** — client ছাড়া support/billing/reporting শুরু হয় না।
- Client-এর call/booking metrics (visible metrics ছাড়া report হয় না)।
- Retention/renewal worker।
- Boss-এর `send` / `ok` প্রতিটা outward step-এ।
