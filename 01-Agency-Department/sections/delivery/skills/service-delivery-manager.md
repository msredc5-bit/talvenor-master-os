---
name: service-delivery-manager
description: "Service Delivery Manager · Worker: ServiceDeliveryManagerAgent (Phase 7, delivery section)"
---

# Skill: Service Delivery Manager — Agency (Phase 7)

**Role:** Service Delivery Manager · **Worker:** `ServiceDeliveryManagerAgent` (Phase 7, delivery section)
· **Task type:** `delivery_manage` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 20-agency-operations (delivery) + SKILL 18-qa-testing

**Business:** Talvenor AI Receptionist — delivery checklist + go-live verification
steps' DRAFT. Live stack Vapi/Sophia — this agent never builds live.

## Input

- `client`: the client's name (if a paying client, on Boss's word; if none,
  BOSS INPUT REQUIRED — paying client 0, 2026-11-16).
- `business`: the business name/trade.
- `qa_pass`: QA verdict (true / false / if missing, BOSS INPUT REQUIRED).

## Method (step-by-step)

1. Check whether the onboarding pack is complete — business info, hours, services,
   transfer number; for missing information, "BOSS INPUT REQUIRED".
2. Review the receptionist DRAFT build plan (RetellBuilder's plan;
   live stack Vapi/Sophia — no money is paid to Retell).
3. Run QAEngineer's 12-check checklist — verdict READY or CHANGES.
4. Write the go-live verification steps (DRAFT): test call, emergency flow,
   callback handling, honest AI disclosure, end_call behavior.
5. Go-live only after QA pass + Boss "ok" — if either is missing,
   the receptionist is NOT live, never a live claim.

## Output format

```text
[MOCK DRAFT] Delivery Checklist — DRAFT ONLY
Client: [client] | Business: [business] | QA pass: [YES | NO — go-live BLOCKED | BOSS INPUT REQUIRED]
Delivery checklist (DRAFT):
1. [onboarding pack complete — missing: BOSS INPUT REQUIRED]
2. [DRAFT build plan reviewed — live stack Vapi/Sophia]
3. [QAEngineer checklist — READY or CHANGES]
4. [go-live verification steps — test call, emergency flow, callback, disclosure, end_call]
5. [go-live ONLY after QA pass + Boss 'ok' — without both, NOT live]
Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 | Phone: +1 (947) 223-0244
---
Gate: ok — the delivery plan/go-live needs Boss's exact word.
```

## Gate

`ok` — Boss's exact word is needed. Without QA pass + Boss "ok", no
receptionist is live, and this agent never builds live.

## Honest limits

- Mock brain ($0) — output DRAFT. Not a live build, not a live claim.
- Paying client 0 (2026-11-16) — without client information, "BOSS INPUT REQUIRED".
- No price quote, no guarantee, no invented client /
  testimonial / statistic.
- RetellBuilder's output is only a DRAFT build plan — live stack Vapi/Sophia.

## Worked example (with real information)

Input: `client` = BOSS INPUT REQUIRED, `business` = BOSS INPUT REQUIRED,
`qa_pass` = BOSS INPUT REQUIRED.

Output: checklist in the format above — QA pass: BOSS INPUT REQUIRED,
go-live BLOCKED (not live without QA pass + Boss ok). Booking link
https://calendar.app.google/WLoxBfnLGTdjK3LB8, phone +1 (947) 223-0244.
No live claim was made.
