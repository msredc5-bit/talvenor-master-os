# Workflow 4 — Receptionist Deployment

**Department:** 03 AI Engineering (+ 07 Quality & Security — QA, + 04 Client Operations — handover)
**Date:** 2026-11-19 | **Status:** READY (plan level) — **no client deployment has happened yet.**

## Purpose

Building a Talvenor AI receptionist (Vapi/Sophia stack) for one client, QA-ing it, taking it live with Boss's approval — and watching calls after go-live.

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Voice Agent Builder (`RetellBuilder`) | 03 | EXISTING — DRAFT plan only |
| Vapi Integration Agent | 03 | EXISTING — `departments/03-ai-engineering/specialists/vapi_integration_agent.py` (`vapi_integration`) — DRAFT plan only |
| Conversation Designer | 03 | EXISTING — `departments/03-ai-engineering/specialists/conversation_designer.py` (`conversation_design`) |
| Prompt Engineering Agent | 03 | EXISTING — `departments/03-ai-engineering/specialists/prompt_engineering_agent.py` (`prompt_engineering`) |
| Testing & Debugging Agent (`QAEngineer`) | 03/07 | EXISTING — QA checklist (partial) |
| Deployment Agent | 03 | EXISTING — `departments/03-ai-engineering/specialists/deployment_agent.py` (`deployment`) — deployment plan DRAFT only; manual step + Boss approval |
| Call Monitoring Agent | 04 | EXISTING — `departments/04-client-operations/specialists/call_monitoring.py` (`call_monitoring`) — monitoring checklist DRAFT only, never live monitoring |

## True status — LIVE STACK (do not get this wrong)

- **Live production voice: Vapi — Sophia, live receptionist, +1 (947) 223-0244**, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3.
- **Sophia is the production receptionist — not a demo.**
- **Retell DROPPED 2026-10-26 — never production.** `RetellBuilder` only builds a DRAFT plan; do not be misled by the name.
- **Demo = recorded 60-second demo video:** https://facebook.com/reel/2947321012290705/ — do not show live Sophia as a demo.
- **Ava demo rebuild pending** — it will be rebuilt once Boss brings a demo account.
- **No client deployment has happened yet.** All steps below are READY plans — they have not run on a real client.

## Step-by-step

### Step 1 — Build plan DRAFT (RetellBuilder)

1. Read the client's onboarding pack (Workflow 3) — hours, services, FAQs, emergency routing, booking rules, escalation, transfer number.
2. Build a **receptionist build plan DRAFT** with `RetellBuilder`: agent flow, prompt draft, knowledge base list, call flow.
3. Remember: this is **DRAFT plan ONLY** — not building a live agent, not deploying anything to Vapi.
4. **Gate:** showing the plan to Boss needs `ok`.

### Step 2 — Prompt + knowledge base + call flow

1. **Prompt:** Greet → life-safety check → intent → qualify → action → confirm → log → close. There will be an honest AI disclosure — the receptionist will call itself AI.
2. **Knowledge base:** the client's hours, services, FAQs, booking rules — only information the client gave; nothing can be invented.
3. **Call flow:** taking bookings, transfer in an emergency, sending to a human on escalation.
4. **Gate:** no next step without Boss's `ok`.

### Step 3 — QA: 12-check checklist (QAEngineer)

1. **QA = 12-check checklist** — write pass/fail for each check:
   - hook/greeting is right, AI disclosure exists, life-safety redirect exists
   - hours/services/FAQ are correct, booking rules are followed, transfer number is correct
   - escalation works, emergency routing is correct
   - "Talvenor" is spelled right, no invented claim, no price/guarantee
2. If any check fails, no deployment — fix it and QA again.
3. **Gate:** QA has no gate (checklist work), but deploy needs Boss's `ok`.

### Step 4 — Deployment (manual + founder approval)

1. Take Boss's **`ok`**.
2. **Manual step:** configuring the assistant in Vapi, connecting the phone number, placing the knowledge base — done by hand; there is no auto-deploy worker.
3. After go-live, test with a test call: the receptionist answers, takes bookings, transfers.
4. **Gate:** `ok` — Boss's exact word + manual step.

### Step 5 — Monitoring (a worker exists — checklist DRAFT only)

1. **A Call Monitoring Agent worker exists** (EXISTING, Phase 3, 2026-11-19) — it builds a monitoring checklist DRAFT; not live monitoring (there is no live call).
2. After go-live, call logs / bookings must be checked by hand — the worker only gives a checklist DRAFT; it does no automated live monitoring.
3. If you see a problem, ask ClientSuccessAgent to write a draft (Workflow 5).

## Honest status

- Build plan, Vapi integration, prompt/conversation design, deployment, and monitoring — workers exist for all of them (EXISTING); all build DRAFT plans/checklists, none does live deploy/monitoring.
- **No client deployment has happened yet** — no step of this workflow has run on a real client.

## Missing inputs

- First paying client + their onboarding pack (CLIENT INPUT REQUIRED).
- Vapi Integration / Deployment / Call Monitoring workers exist (EXISTING) — live deploy/monitoring needs the first paying client + Boss's ok + a manual step.
- Boss's `ok` at every step + manual deployment step.
