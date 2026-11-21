# 04 — Client Operations Department

## Purpose

Keeping the whole path after getting a client in one place: intake, onboarding draft,
service delivery management, client success, inbox triage, and call monitoring /
reporting / retention / renewal roles. This department only makes plans and DRAFTs
— it sends nothing, no live client's work has started yet.

## Manager

- **COO Client Operations Agent** — `COOClientOperationsAgent`, task_kind `manage_client_operations`, gate `ok`
- Manager file: `01-Agency-Department/departments/04-client-operations/manager/coo_client_operations_agent.py`
- Skill file: `01-Agency-Department/departments/04-client-operations/skills/coo-client-operations-agent.md`
- Manager makes a DRAFT of the delegation plan + loads and runs the Phase 3 specialists (DRAFT only); does not execute the engine/section's old workers.
- Agency Chief wiring **Phase 2 DONE** — the Chief now calls this manager via DEPARTMENT_ROUTING.

## Mapped Existing Staff (9)

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| ClientIntakeReceiver | `client_intake` | `01-Agency-Department/sections/receive/agents/client_intake_receiver.py` | send | EXISTING |
| OnboardingAgent | `onboarding_draft` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | ok | EXISTING |
| ServiceDeliveryManager | `delivery_manage` | `01-Agency-Department/sections/delivery/agents/service_delivery_manager.py` | ok | EXISTING |
| ClientSuccessAgent | `client_success` | `01-Agency-Department/sections/delivery/agents/client_success_agent.py` | send | EXISTING |
| InboxTriager | `inbox_triage` | `01-Agency-Department/engine/workers/src/workers/admin.py` | none | EXISTING |
| CallMonitoringAgent | `call_monitoring` | `01-Agency-Department/departments/04-client-operations/specialists/call_monitoring.py` | none | EXISTING |
| ClientReportingAgent | `client_reporting` | `01-Agency-Department/departments/04-client-operations/specialists/client_reporting.py` | none | EXISTING |
| RetentionAgent | `retention` | `01-Agency-Department/departments/04-client-operations/specialists/retention.py` | none | EXISTING |
| RenewalUpsellAgent | `renewal_upsell` | `01-Agency-Department/departments/04-client-operations/specialists/renewal_upsell.py` | none | EXISTING |

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Client Onboarding Agent | EXISTING — OnboardingAgent | `onboarding_draft`, gate ok |
| Business Requirement Analyst | EXISTING — ClientIntakeReceiver | `client_intake`, gate send — intake log + checklist DRAFT |
| Client Configuration Agent | EXISTING — ServiceDeliveryManager | `delivery_manage`, gate ok |
| Call Monitoring Agent | EXISTING — CallMonitoringAgent | `call_monitoring`, gate none — checklist DRAFT; does not watch live calls |
| Client Reporting Agent | EXISTING — ClientReportingAgent | `client_reporting`, gate none — report template + DRAFT; BOSS INPUT REQUIRED if there are no numbers |
| Support Agent | EXISTING — ClientSuccessAgent | `client_success`, gate send |
| Retention Agent | EXISTING — RetentionAgent | `retention`, gate none — retention plan DRAFT; paying client 0 |
| Renewal & Upsell Agent | EXISTING — RenewalUpsellAgent | `renewal_upsell`, gate none — renewal/upsell plan DRAFT; no price quote, no upsell told to a client without Boss's ok |

## Missing Roles

- There is no GAP role in this department — all 8 of the brief's roles are EXISTING
  covered.
- There is no ROLE-ONLY role left — Call Monitoring, Client Reporting, Retention,
  Renewal & Upsell — all 4 became EXISTING in Phase 3 with worker code
  (2026-11-19).

## Honest Status

- **Paying clients: 0** — there is still no live client; the intake/onboarding plan
  It stays as a DRAFT.
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; all output is DRAFT.
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — this is the DB, no other database.
- **CRM: n8n Cloud Data Tables PLANNED, not live.**
- **Calendar: Google Calendar Appointment Schedule LIVE** — booking link
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time).
- **Live receptionist: Vapi/Sophia, +1 (947) 223-0244.**
- **$0 spend cap** — nothing is spent.
- **Agency Chief wiring Phase 2 DONE** — the Chief now calls this department's manager via DEPARTMENT_ROUTING.
- **Pricing LOCKED, internal only** — a price is told to a client only by Boss's decision,
  never from the manager/worker itself.
- **No dental/medical ever** — no dental/medical or patient-health business is taken.
- Brand **Talvenor only**. No invented client, price, statistic, testimonial, or guarantee.
