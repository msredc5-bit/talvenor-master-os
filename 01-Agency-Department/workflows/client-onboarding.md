# Workflow 3 — Client Onboarding

**Department:** 04 Client Operations (+ 01 Sales & Growth — handover from close)
**Date:** 2026-11-19 | **Status:** READY — but **not tested on any real client yet (paying client 0).**

## Purpose

Taking a business that said "yes" on the demo call to a live receptionist within 7 days — from intake to configuration, with Boss's `ok` at every step.

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Business Requirement Analyst (`ClientIntakeReceiver`) | 04 | EXISTING — takes intake |
| Client Onboarding Agent (`OnboardingAgent`) | 04 | EXISTING — onboarding pack draft |
| Client Configuration Agent (`ServiceDeliveryManager`) | 04 | EXISTING — manages configuration |
| SalesCloser | 01 | EXISTING — close prep, hands over |
| SchedulerAssistant | 01 | EXISTING — booking link help |

## True status

- **Paying client 0** — this workflow has not run on any real client yet. What is written is a READY plan, not exercised.
- **Onboarding term:** live within 7 days, or the build fee is refunded. **3-month minimum**, then month-to-month, 30 days notice.
- **Pricing LOCKED, internal only** — in onboarding, the client is told a price only if Boss confirmed it; never quoted to a prospect in outreach.

## Step-by-step

### Step 1 — Intake (ClientIntakeReceiver)

1. Take from the client:
   - **Business info form:** business name, address, service area, website
   - **Hours:** when open, when closed, what happens after-hours
   - **Services:** which services it gives, which ones to take bookings for
   - **FAQs:** recurring questions + the right answers
   - **Emergency routing:** who an emergency call goes to, at which number
   - **Booking rules:** when bookings can be taken, how far ahead, which slots not
   - **Escalation:** in which situations to transfer to a human
2. If something is missing, write **CLIENT INPUT REQUIRED** — do not guess.
3. **Gate:** sending intake needs `send`.

### Step 2 — Onboarding pack draft (OnboardingAgent)

1. Build a draft of the **onboarding pack** from intake:
   - business info form (filled in)
   - hours/services summary
   - **transfer number** (where call transfer goes)
   - 7-day live term + 3-month minimum (written)
   - call flow draft (greet → intent → qualify → action → confirm → log → close)
2. The pack will have no invented client, testimonial, or guarantee.
3. **Gate:** showing the pack to Boss needs `ok` — only once Boss says `ok` does the next step happen.

### Step 3 — Configuration (ServiceDeliveryManager)

1. After Boss's `ok`, place the client's configuration on the Vapi/Sophia stack (see Workflow 4 — receptionist-deployment):
   - prompt + knowledge base (hours, services, FAQs)
   - call flow + escalation + emergency routing
   - transfer number + booking rules
2. Do not change any configuration step yourself — only what is in the pack.
3. **Gate:** configuration needs `ok`.

### Step 4 — Go-live (within 7 days)

1. If QA's 12 checks pass (Workflow 4), go live with Boss's `ok`.
2. On go-live day, tell the client: receptionist live, transfer number active, booking link on.
3. **Remember the term:** if not live within 7 days of onboarding completing, the build fee is refunded.
4. **Gate:** go-live needs Boss's `ok` (exact word).

## Honest status

- Workflow **READY, untested** — 0 paying clients, so no step from intake to go-live has run on a real client.
- Workers exist (Intake, Onboarding, Configuration) — but all are at draft/plan level; no proof of a live run.

## Missing inputs

- **First paying client** — without a client, intake never starts.
- The client's business info, hours, services, transfer number — all CLIENT INPUT REQUIRED.
- Boss's `ok` at every step.
