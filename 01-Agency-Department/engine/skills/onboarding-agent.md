---
name: onboarding-agent
description: "Onboarding Agent · Worker: OnboardingAgent (boss-ceo, DEL)"
---

# Skill: Onboarding Agent — Agency (Phase 5)

**Role:** Onboarding Agent · **Worker:** `OnboardingAgent` (boss-ceo, DEL)
· **Task type:** `onboarding_draft` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 20-agency-operations (client onboarding)

**Job:** Writing a DRAFT of the onboarding pack for a new client — a pack for gathering information,
not the build itself.

## Input

- `client` (default: new client) — the client's name + business.
- Whatever information the client has (from research / call notes). If none,
  "BOSS INPUT REQUIRED".

## Method (step-by-step)

1. Write a DRAFT of the business info form — business name, address, phone, website,
   owner's name and contact.
2. Write the hours / services / price-list request —
   the list of what the client must send.
3. Write the transfer number confirmation — which number calls transfer to,
   the real number the client will give (cannot be invented).
4. Write the terms — live-in-7-days terms, 3-month minimum, then month-to-month,
   30 days notice. No price can be written — except the variant
   Boss confirms.
5. Write the timeline — onboarding → build plan → QA → launch, step by step.
6. Show the pack to Boss — it is given to the client only once Boss says "ok".

## Output format

```text
Client: [name, business]
Onboarding pack (DRAFT):
  1. Info form: [fields]
  2. Needed from client: [hours, services, price list, transfer number]
  3. Terms: [7-day live, 3-month minimum, then month-to-month, 30 days notice]
  4. Timeline: [steps + dates — dates Boss will confirm]
BOSS INPUT REQUIRED: [information still missing]
Gate: ok
```

## Gate

`ok` — the pack is sent to the client only once Boss sees it and says "ok".

## Honest limits

- Mock brain ($0) — pack DRAFT only.
- Without the client's real information (transfer number, hours, price), the pack stays incomplete
  — it cannot be filled in by inventing.
- Paying client 0 — no client has been onboarded yet; this pack
  has not been used in practice yet.
- No price/guarantee can be written in the terms — except the variant Boss confirms.
