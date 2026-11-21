# 03 — AI Engineering Department

## Purpose

Keeping Talvenor's AI receptionist build engineering path in one place: solution
design, voice agent build (DRAFT plan only), conversation design, prompt
engineering, Vapi integration, calendar integration, n8n automation, QA, and
deployment plans. This department only makes plans and DRAFTs — it changes nothing in production,
deploys nothing.

## Manager

- **CTO AI Engineering Agent** — `CTOAIEngineeringAgent`, task_kind `manage_ai_engineering`, gate `ok`
- Manager file: `01-Agency-Department/departments/03-ai-engineering/manager/cto_ai_engineering_agent.py`
- Skill file: `01-Agency-Department/departments/03-ai-engineering/skills/cto-ai-engineering-agent.md`
- The manager loads and runs the Phase 3 specialists (DRAFT only), deploys nothing; it does not execute an engine/section old worker.
- Agency Chief wiring **Phase 2 DONE** — the Chief now calls this manager via DEPARTMENT_ROUTING.

## Mapped Existing Staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| RetellBuilder | `receptionist_build` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | ok | EXISTING — DRAFT plan ONLY |
| QAEngineer | `receptionist_qa` | `01-Agency-Department/engine/workers/src/workers/delivery.py` | none | EXISTING — shared with dept 07, partial (QA checklist) |

Note: RetellBuilder's worker task_kind is `receptionist_build` in `delivery.py`
(changed from `retell_build` on 2026-11-21 — to match the routing key);
this department's delegation key is `receptionist_build`. RetellBuilder **DRAFT plan
only** — the live production stack is **Vapi/Sophia**, not Retell. QAEngineer is shared with dept 07
(Quality & Security); QA checklist only, not a full testing worker.

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| AI Solution Architect | EXISTING — `departments/03-ai-engineering/specialists/ai_solution_architect.py` | `solution_architect`, gate none — solution design DRAFT plan only; no live build |
| Voice Agent Builder | EXISTING — RetellBuilder | `receptionist_build`, gate ok — DRAFT plan only; live stack Vapi/Sophia |
| Conversation Designer | EXISTING — `departments/03-ai-engineering/specialists/conversation_designer.py` | `conversation_design`, gate none — an 8-step call-flow DRAFT, with honest AI disclosure |
| Prompt Engineering Agent | EXISTING — `departments/03-ai-engineering/specialists/prompt_engineering_agent.py` | `prompt_engineering`, gate none — prompt DRAFT + tuning notes (GPT-4o-mini, temp 0.2); does not change the live prompt |
| Vapi Integration Agent | EXISTING — `departments/03-ai-engineering/specialists/vapi_integration_agent.py` | `vapi_integration`, gate none — Vapi integration DRAFT plan; the brief's integration role name was corrected — the live provider is Vapi |
| CRM Integration Agent | EXISTING — `departments/03-ai-engineering/specialists/crm_integration_agent.py` | `crm_integration`, gate ok — CRM integration DRAFT plan; CRM (n8n Data Tables) PLANNED, not live |
| Calendar Integration Agent | EXISTING — `departments/03-ai-engineering/specialists/calendar_integration_agent.py` | `calendar_integration`, gate none — booking-link integration DRAFT (Google Calendar Appointment Schedule, 15 min, New York Time); does not touch a live calendar |
| n8n Automation Engineer | EXISTING — `departments/03-ai-engineering/specialists/n8n_automation_engineer.py` | `n8n_automation`, gate none — n8n workflow DRAFT notes; workflows READY, not LIVE |
| Testing & Debugging Agent | EXISTING — QAEngineer (partial) | `receptionist_qa`, QA checklist; shared with dept 07 |
| Deployment Agent | EXISTING — `departments/03-ai-engineering/specialists/deployment_agent.py` | `deployment`, gate none — deployment plan DRAFT ONLY; Boss's ok + manual steps are needed, no worker deploys |

## Missing Roles

- No missing role — CRM Integration Agent built on 2026-11-21 (skill + worker EXISTING).
- In Phase 3, 7 roles were built (AI Solution Architect, Conversation
  Designer, Prompt Engineering, Vapi Integration, Calendar Integration,
  n8n Automation, Deployment) — all EXISTING, with skill + worker.

## Honest Status

- **LIVE production voice: Vapi — Sophia, live receptionist, +1 (947) 223-0244**,
  org 1861a735, GPT-4o-mini, Emma voice, Deepgram nova-3. Sophia is no demo agent;
  Ava was a demo (deleted; rebuild pending, in a separate demo account).
- **Retell DROPPED 2026-10-26** — Retell is never production; RetellBuilder only
  DRAFT plan.
- **Paying clients: 0** — there is still no paying client.
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; all output is DRAFT.
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — this is the DB, no other database.
- **CRM: n8n Cloud Data Tables PLANNED, not live.**
- **Calendar: Google Calendar Appointment Schedule LIVE** — booking link
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 (15 min, New York Time).
- **n8n workflows READY, not LIVE.**
- **Deployment: Boss's ok + manual steps** — no worker deploys.
- **$0 spend cap** — nothing is spent.
- **Agency Chief wiring Phase 2 DONE** — the Chief now calls this department's manager via DEPARTMENT_ROUTING.
- **Pricing LOCKED, internal only** — prices are never stated to a prospect.
- **No dental/medical ever** — dental/medical or patient-health businesses are not a target.
- Brand **Talvenor only**. No invented client, price, statistic, testimonial, or guarantee.
