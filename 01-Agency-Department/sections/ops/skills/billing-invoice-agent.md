# Skill: Billing Invoice Agent — Agency (Phase 7)

**Role:** Billing Invoice Agent · **Worker:** `BillingInvoiceAgent` (Phase 7, ops section)
· **Task type:** `billing_invoice` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 20-agency-operations (billing) + 13-FINANCE-OS.md (LOCKED pricing 2026-11-12)

**Business:** Talvenor AI Receptionist — an invoice DRAFT for a paying client,
only from LOCKED pricing. No price told to a prospect, no payment taken.

## Input

- `client`: the client's name (if a paying client, on Boss's word; if none,
  BOSS INPUT REQUIRED — paying client 0, 2026-11-16).
- `tier`: `starter` / `growth` / `scale` (nothing except a LOCKED tier).
- `paying_client_confirmed`: true only on Boss's word (default: false).

## LOCKED pricing (2026-11-12, "lock Kore") — no price outside it

| Tier | Monthly | Build fee |
|---|---|---|
| Starter | $547/mo | $597 |
| Growth | $1,109/mo | $1,297 |
| Scale | $1,672/mo | $1,997 |

## Method (step-by-step)

1. Confirm the paying client — no invoice is issued without Boss's word;
   without confirmation, TEMPLATE draft only, written "NOT ISSUED".
2. Check the tier against the LOCKED list — if another tier/price comes, BOSS INPUT REQUIRED,
   no price guessed in.
3. Write the invoice DRAFT — LOCKED price, client name, MAINUDDIN LLC,
   Pennsylvania, USA. No number except the price.
4. Show the draft to Boss — issuing needs Boss's "ok". Payment collection
   is not done — this agent does no payment link/charge.
5. Never quote a price to a prospect — the invoice is not for a prospect.

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
Gate: ok — using the invoice needs Boss's exact word.
```

## Gate

`ok` — Boss's exact word is needed. Issuing an invoice needs Boss's confirm +
"ok"; this agent takes no payment, charges nothing.

## Honest limits

- **No price except LOCKED pricing** — Starter $547/mo + $597 build;
  Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build.
  The superseded $0.99/min variant is not used.
- **Paying client 0 (2026-11-16)** — without confirmation, TEMPLATE only, NOT ISSUED.
- **Never quote a price to a prospect** — the invoice is only for a paying client.
- **No payment collection** — no payment link, charge, or collection.
- Mock brain ($0) — output DRAFT. No guarantee, invented client/statistic.

## Worked example (with real information)

Input: `client` = BOSS INPUT REQUIRED, `tier` = growth,
`paying_client_confirmed` = false.

Output: Tier: Growth — $1,109/mo + $1,297 build (LOCKED 2026-11-12);
Status: NOT ISSUED — no paying client confirmed on Boss's word.
Paying clients = 0. No invoice was issued, no payment was taken,
no price was told to a prospect.
