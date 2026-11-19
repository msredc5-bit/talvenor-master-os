# 04 — Client Operations Department

## উদ্দেশ্য (Purpose)

Client পাওয়ার পরের পুরো পথ এক জায়গায় রাখা: intake গ্রহণ, onboarding draft,
service delivery manage, client success, inbox triage, আর call monitoring /
reporting / retention / renewal-এর role-গুলো। এই department শুধু plan আর DRAFT
বানায় — কিছু পাঠায় না, কোনো live client-এর কাজ এখনো শুরু হয়নি।

## Manager

- **COO Client Operations Agent** — `COOClientOperationsAgent`, task_kind `manage_client_operations`, gate `ok`
- Manager file: `01-Agency-Department/departments/04-client-operations/manager/coo_client_operations_agent.py`
- Skill file: `01-Agency-Department/departments/04-client-operations/skills/coo-client-operations-agent.md`
- Manager delegation plan-এর DRAFT বানায় + Phase 3 specialist-দের load করে চালায় (DRAFT only); engine/section-এর পুরনো worker execute করে না।
- Agency Chief wiring **Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।

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
| Call Monitoring Agent | EXISTING — CallMonitoringAgent | `call_monitoring`, gate none — checklist DRAFT; live call দেখে না |
| Client Reporting Agent | EXISTING — ClientReportingAgent | `client_reporting`, gate none — report template + DRAFT; সংখ্যা না থাকলে BOSS INPUT REQUIRED |
| Support Agent | EXISTING — ClientSuccessAgent | `client_success`, gate send |
| Retention Agent | EXISTING — RetentionAgent | `retention`, gate none — retention plan DRAFT; paying client 0 |
| Renewal & Upsell Agent | EXISTING — RenewalUpsellAgent | `renewal_upsell`, gate none — renewal/upsell plan DRAFT; দাম quote নয়, Boss-এর ok ছাড়া client-কে upsell বলা হয় না |

## Missing Roles

- এই department-এ কোনো GAP role নেই — brief-এর ৮টি role-ই EXISTING
  হিসেবে covered।
- ROLE-ONLY role আর নেই — Call Monitoring, Client Reporting, Retention,
  Renewal & Upsell — ৪টিই Phase 3-এ worker code সহ EXISTING হয়েছে
  (2026-11-19)।

## Honest Status

- **Paying clients: 0** — এখনো কোনো live client নেই; intake/onboarding plan
  DRAFT হিসেবেই থাকে।
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; সব output DRAFT।
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — এটাই DB, অন্য কোনো database নয়।
- **CRM: n8n Cloud Data Tables PLANNED, not live।**
- **Calendar: Google Calendar Appointment Schedule LIVE** — booking link
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time)।
- **Live receptionist: Vapi/Sophia, +1 (947) 223-0244।**
- **$0 spend cap** — কিছু খরচ করা হয় না।
- **Agency Chief wiring Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই department-এর manager-কে call করে।
- **Pricing LOCKED, internal only** — client-কে দাম বলা হয় শুধু Boss-এর সিদ্ধান্তে,
  কখনো manager/worker-এর নিজের থেকে নয়।
- **No dental/medical ever** — dental/medical বা patient-health ব্যবসা নেওয়া হয় না।
- Brand **Talvenor only**। কোনো invented client, price, statistic, testimonial, guarantee নেই।
