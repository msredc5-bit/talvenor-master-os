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
- Manager কোনো worker execute করে না; শুধু delegation plan-এর DRAFT বানায়।
- Agency Chief wiring **Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।

## Mapped Existing Staff (5)

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| ClientIntakeReceiver | `client_intake` | `01-Agency-Department/sections/receive/agents/client_intake_receiver.py` | send | EXISTING |
| OnboardingAgent | `onboarding_draft` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | ok | EXISTING |
| ServiceDeliveryManager | `delivery_manage` | `01-Agency-Department/sections/delivery/agents/service_delivery_manager.py` | ok | EXISTING |
| ClientSuccessAgent | `client_success` | `01-Agency-Department/sections/delivery/agents/client_success_agent.py` | send | EXISTING |
| InboxTriager | `inbox_triage` | `01-Agency-Department/engine/workers/src/workers/admin.py` | none | EXISTING |

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Client Onboarding Agent | EXISTING — OnboardingAgent | `onboarding_draft`, gate ok |
| Business Requirement Analyst | EXISTING — ClientIntakeReceiver | `client_intake`, gate send — intake log + checklist DRAFT |
| Client Configuration Agent | EXISTING — ServiceDeliveryManager | `delivery_manage`, gate ok |
| Call Monitoring Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Client Reporting Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Support Agent | EXISTING — ClientSuccessAgent | `client_success`, gate send |
| Retention Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Renewal & Upsell Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা — কোনো upsell client-কে বলা হয় না যতক্ষণ Boss ok না দেন |

## Missing Roles

- এই department-এ কোনো GAP role নেই — brief-এর ৮টি role-ই EXISTING বা ROLE-ONLY হিসেবে covered।
- তবে ROLE-ONLY ৪টি role-এর (Call Monitoring, Client Reporting, Retention,
  Renewal & Upsell) কোনো worker code নেই; এগুলো skill doc-এর role হিসেবে থাকে।

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
