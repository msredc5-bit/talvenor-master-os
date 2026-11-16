# Skill: Billing Invoice Agent — Agency (Phase 7)

**Role:** Billing Invoice Agent · **Worker:** `BillingInvoiceAgent` (Phase 7, ops section)
· **Task type:** `billing_invoice` · **Gate:** `ok`
· **SOP ভিত্তি:** agency-os SKILL 20-agency-operations (billing) + 13-FINANCE-OS.md (LOCKED pricing 2026-11-12)

**ব্যবসা:** Talvenor AI Receptionist — paying client-এর জন্য invoice-এর
DRAFT, শুধু LOCKED pricing থেকে। Prospect-কে দাম বলা নয়, payment নেওয়া নয়।

## Input

- `client`: client-এর নাম (paying client হলে, Boss-এর কথায়; না থাকলে
  BOSS INPUT REQUIRED — paying client 0, 2026-11-16)।
- `tier`: `starter` / `growth` / `scale` (LOCKED tier ছাড়া আর কিছু নয়)।
- `paying_client_confirmed`: true শুধু Boss-এর কথায় (default: false)।

## LOCKED pricing (2026-11-12, "lock Kore") — এর বাইরে কোনো দাম নয়

| Tier | Monthly | Build fee |
|---|---|---|
| Starter | $547/mo | $597 |
| Growth | $1,109/mo | $1,297 |
| Scale | $1,672/mo | $1,997 |

## পদ্ধতি (step-by-step)

1. Paying client confirm করা — Boss-এর কথা ছাড়া invoice issue নয়;
   confirm না হলে TEMPLATE draft only, "NOT ISSUED" লেখা।
2. Tier যাচাই করা LOCKED তালিকায় — অন্য tier/দাম এলে BOSS INPUT REQUIRED,
   অনুমান করে দাম বসানো নয়।
3. Invoice DRAFT লেখা — LOCKED দাম, client নাম, MAINUDDIN LLC,
   Pennsylvania, USA। দাম ছাড়া আর কোনো সংখ্যা নেই।
4. Draft Boss-কে দেখানো — issue করতে Boss-এর "ok" লাগে। Payment collect
   নয় — কোনো payment link/charge এই agent করে না।
5. Prospect-কে কখনো দাম quote নয় — invoice prospect-এর জন্য নয়।

## Output format

```text
[MOCK DRAFT] Invoice — DRAFT ONLY
Client: [client]
Tier: [Starter — $547/mo + $597 build | Growth — $1,109/mo + $1,297 build | Scale — $1,672/mo + $1,997 build] (LOCKED 2026-11-12)
Status: [NOT ISSUED — no paying client confirmed on Boss's word | DRAFT ready for Boss review]
Invoice (DRAFT): Talvenor AI Receptionist — MAINUDDIN LLC, Pennsylvania, USA. Amounts from LOCKED pricing only.
Never quote this to a prospect. Never collect payment from here.
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: ok — invoice ব্যবহার করতে Boss-এর exact শব্দ লাগবে।
```

## Gate

`ok` — Boss-এর exact শব্দ লাগে। Invoice issue করতে Boss-এর confirm +
"ok" লাগে; এই agent payment নেয় না, charge করে না।

## সৎ সীমা (honest limits)

- **LOCKED pricing ছাড়া কোনো দাম নেই** — Starter $547/mo + $597 build;
  Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build।
  Superseded $0.99/min variant ব্যবহার নয়।
- **Paying client 0 (2026-11-16)** — confirm না হলে TEMPLATE only, NOT ISSUED।
- **Prospect-কে কখনো দাম quote নয়** — invoice শুধু paying client-এর জন্য।
- **Payment collect নয়** — কোনো payment link, charge, বা collection নেই।
- Mock brain ($0) — output DRAFT। কোনো guarantee, বানানো client/statistic নেই।

## Worked example (আসল তথ্য দিয়ে)

Input: `client` = BOSS INPUT REQUIRED, `tier` = growth,
`paying_client_confirmed` = false।

Output: Tier: Growth — $1,109/mo + $1,297 build (LOCKED 2026-11-12);
Status: NOT ISSUED — no paying client confirmed on Boss's word।
Paying clients = 0। Invoice issue করা হয়নি, payment নেওয়া হয়নি,
prospect-কে দাম বলা হয়নি।
