# Tenant Acceptance Flow (Phase 4 buildable part)

One tenant (one receptionist client business) walks six stages.
Each stage either passes and moves on, or refuses to move — the
refusal and its reason are recorded on the acceptance record.

## Stages

1. **intake** — a tenant config is received. Refuses when the config
   is missing or its tenant_id does not match the record.
2. **schema_check** — `tenant_schema.validate_tenant()` must pass.
   Missing field → CLIENT INPUT REQUIRED (fields listed). Dental /
   medical / patient-health trade → refused (hard DQ). Bad phone,
   bad timezone, non-English language, emergency_redirect not True
   → rejected with a reason.
3. **checklist** — `deployment_checklist.evaluate_checklist()`. The
   stage passes when the two evaluable steps pass (schema valid,
   Vapi assistant config drafted). Blocked steps (phone number,
   test calls, billing) and missing gates are RECORDED as
   outstanding — they never fail the stage, because no tenant can
   clear them today.
4. **qa** — `tenant_qa.run_qa()` on a synthetic call script must
   pass all 8 checks (business named, AI disclosure, life-safety,
   qualification, booking confirmation + link, no price quoted, no
   invented claim, transfer offered when enabled).
5. **boss_acceptance** — needs Boss's word "ok", recorded with
   `record_boss_acceptance()`. Any other word is rejected.
6. **deploy** — ALWAYS BLOCKED. Live deployment is manual: Boss
   executes it himself. No deploy path exists anywhere in this repo.

## Blocked items (honest, not skipped)

- Phone number: Twilio number not imported — Boss's step.
- Test calls: need a live number and a proven live brain — neither
  exists yet.
- Billing: 0 paying clients. BillingInvoiceAgent refuses any invoice
  unless paying_client_confirmed is True.
- Go-live: needs Boss's "go" (recorded as a checklist gate).

## Gates

- Greeting script approved: Boss's "ok".
- Booking link verified live: Boss's "ok" (Boss checks it in a
  browser; code never fetches it).
- Boss acceptance: Boss's "ok".
- Go-live: Boss's "go".

## Fixtures

The only tenant and the only call scripts are SYNTHETIC and
fictional ("Example Plumbing Co.", Fictional City). There are 0
paying clients, so there is no real tenant. Never copy a real lead
from store/leads.json into a tenant fixture.

## Code

- `tenant_schema.py` + `tenant_schema.json` — schema + validator +
  Vapi assistant config draft (dict only, never sent).
- `deployment_checklist.py` — evaluate-only checklist.
- `tenant_qa.py` — QA-as-code over a call script.
- `acceptance_flow.py` — the record + advance() + TEMP persistence.
- `scripts/check_unified_phase4.py` — the check suite for all of it.
