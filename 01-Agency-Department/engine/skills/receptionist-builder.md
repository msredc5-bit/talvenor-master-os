# Skill: Receptionist Builder — Agency (Phase 5)

**Role:** Receptionist Builder · **Worker:** `RetellBuilder` (boss-ceo, DEL)
· **Task type:** `receptionist_build` · **Gate:** `ok`
· **SOP basis:** agency-os SKILL 06-vapi-voice-agent (Vapi layer) +
05-agent-architecture

**Most important fact:** Even though the worker is named RetellBuilder, Talvenor's
live stack is **Vapi / Sophia** (Boss will not pay for Retell — 2026-10-26
decision). So this role's output is only a **DRAFT build plan** — never a live build.
Phone: +1 (947) 223-0244.

## Input

- `business` (default: Apex Plumbing), `trade` (default: plumbing).
- The client's real information: business hours, services, transfer number, emergency
  rules — without them, "BOSS INPUT REQUIRED", cannot be invented.

## Method (step-by-step)

1. Gather the client's information (from the onboarding pack) — hours, services,
   price list, transfer number, emergency flow.
2. Write a DRAFT of the agent prompt — flow: Greet → life-safety check → intent →
   qualify → action → confirm → log → close. With honest AI disclosure.
3. Write a DRAFT of the knowledge base — services, FAQ, hours; no invented pricing.
4. Write the recording script — the demo call's script, using a fictional AP- confirmation
   number (never inventing a real number), end_call only.
5. Keep emergency flow + callback handling + in-prompt schedule in the plan.
6. Show the plan to Boss — the live Vapi build is Boss / live stack's job, not this role's.

## Output format

```text
Client: [business] ([trade])
DRAFT BUILD PLAN (live stack: Vapi / Sophia — not Retell)
1. Agent prompt: [DRAFT text]
2. Knowledge base: [services, FAQ, hours]
3. Recording script: [demo call script]
4. Emergency flow + callback handling: [...]
5. Transfer number: [BOSS INPUT REQUIRED — cannot be written without the real number]
Gate: ok
```

## Gate

`ok` — the plan can only be used once Boss sees it and says "ok". A live build needs
Boss's separate decision.

## Honest limits

- Mock brain ($0) — plan DRAFT only, not a live agent.
- RetellBuilder is the engine's old name — Retell is not used live.
- Transfer number, business hours, price — without the client's real information
  they cannot be invented.
- Paying client 0 — no client's live receptionist has launched yet.
- Vapi's real config (GPT-4o-mini, Emma voice, Deepgram nova-3) can be written in the plan,
  but this role changes nothing in Vapi.
