# Section: Delivery — Agency (Phase 7)

**Purpose:** Building a paying client's receptionist (DRAFT plan),
QA, onboarding, delivery management, and client check-in — from demo to go-live
and beyond. Live stack Vapi/Sophia. This section never builds live, and never calls
any receptionist live without QA pass + Boss "ok".

**True status (2026-11-16):** Paying client 0. Email PAUSED (since 2026-11-14
). Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
Phone +1 (947) 223-0244.

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| RetellBuilder | `engine/workers/src/workers/delivery.py` (`RetellBuilder`) | `engine/skills/receptionist-builder.md` | `ok` | MAPPED |
| QAEngineer | `engine/workers/src/workers/delivery.py` (`QAEngineer`) | `engine/skills/qa-engineer.md` | None | MAPPED |
| OnboardingAgent | `engine/workers/src/workers/delivery.py` (`OnboardingAgent`) | `engine/skills/onboarding-agent.md` | `ok` | MAPPED |
| ServiceDeliveryManager | `sections/delivery/agents/service_delivery_manager.py` | `sections/delivery/skills/service-delivery-manager.md` | `ok` | NEW (Phase 7) |
| ClientSuccessAgent | `sections/delivery/agents/client_success_agent.py` | `sections/delivery/skills/client-success-agent.md` | `send` | NEW (Phase 7) |

## How work flows

1. **OnboardingAgent** — a new client's onboarding pack DRAFT (info form,
   hours/services, transfer number, live-in-7-days terms). Without information,
   "BOSS INPUT REQUIRED".
2. **RetellBuilder** — the receptionist's **DRAFT build plan** (agent prompt,
   knowledge base, recording script). Live stack Vapi/Sophia — Boss will not pay for Retell,
   so never a live build, only a plan.
3. **QAEngineer** — 12-check QA checklist, verdict READY or CHANGES.
   The verdict is not the final word — delivery needs Boss's ok.
4. **ServiceDeliveryManager** — delivery checklist + go-live verification
   step is DRAFT. Go-live only after QA pass + Boss "ok"; without them, no live claim.
5. **ClientSuccessAgent** — check-in draft + renewal-reminder draft.
   Paying client 0 — without client information, TEMPLATE only, sent to nobody.

## Gate

- `ok` (RetellBuilder, OnboardingAgent, ServiceDeliveryManager): plan/pack
  needs Boss's "ok" to use.
- `send` (ClientSuccessAgent): sending a check-in/renewal message needs Boss's "send"
  ; Boss sends it himself.
- None (QAEngineer): the checklist itself is safe.

## Honest limits

- Live stack Vapi/Sophia — RetellBuilder is only a DRAFT build plan, not a live build.
- No receptionist is live without QA pass + Boss "ok" — never a live claim.
- Paying client 0 — without client information, "BOSS INPUT REQUIRED".
- All output is DRAFT, mock brain ($0). No price quote, no guarantee,
  no invented client/testimonial/statistic.
