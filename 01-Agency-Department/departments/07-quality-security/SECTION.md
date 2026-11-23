# Department 07: Quality & Security — Agency (Phase 1)

**Purpose:** Talvenor Agency's work quality and security —
receptionist QA, call scenario / workflow / data checks, security
monitoring, access control, backup, compliance review. The manager loads and runs 6 new
specialists (DRAFT only); for QAEngineer it only builds a DRAFT of the DELEGATION PLAN
for routing the task to a specialist.

**True status (2026-11-19):** Paying client 0. First mail 163. Email PAUSED
(since 2026-11-14, DNS fix pending). Brain mock ($0). Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.
Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefQualitySecurityAgent | `departments/07-quality-security/manager/chief_quality_security_agent.py` | `departments/07-quality-security/skills/chief-quality-security-agent.md` | `ok` |

The manager's job: `manage_quality_security` — pick the specialist from task_kind
and load and run 6 new specialists; for QAEngineer, build a DRAFT of the
delegation plan. It never runs any QA/security check itself.
Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| QAEngineer | `receptionist_qa` | `engine/workers/src/workers/delivery.py` | None | EXISTING |

- **QAEngineer** — 12-check QA checklist before calling the demo receptionist READY:
  prompt completeness, no broken tool reference, emergency flow, pricing
  honesty, transfer number real-or-absent, end_call behavior. Verdict
  READY or CHANGES — delivery needs Boss's ok.
- **Shared:** QAEngineer is also shared with dept 03 Testing & Debugging —
  the same worker, mapped to two departments.

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Voice Quality Testing Agent | EXISTING (partial) | QAEngineer's 12-check checklist partly covers voice quality; no dedicated voice-quality worker. |
| Call Scenario Testing Agent | EXISTING | `departments/07-quality-security/specialists/call_scenario_testing_agent.py` — `call_scenario_testing`, gate None. Call-scenario test script DRAFT; never a live call. |
| Workflow Testing Agent | EXISTING | `departments/07-quality-security/specialists/workflow_testing_agent.py` — `workflow_testing`, gate None. Workflow test check-script DRAFT; never a live run. |
| Data Validation Agent | EXISTING | `departments/07-quality-security/specialists/data_validation_agent.py` — `data_validation`, gate None. Data validation DRAFT; invents no results. |
| Security Monitoring Agent | EXISTING | `departments/07-quality-security/specialists/security_monitoring_agent.py` — `security_monitoring`, gate None. Security monitoring checklist DRAFT; never live monitoring. |
| Access Control Agent | EXISTING | `departments/07-quality-security/specialists/access_control_agent.py` — `access_control`, gate None. Access-control DRAFT; changes no access. |
| Backup & Recovery Agent | EXISTING | `departments/07-quality-security/specialists/backup_recovery_agent.py` — `backup_recovery`, gate ok. Backup DRAFT plan + DR runbook only; restore test not done — NOT VERIFIED. |
| Compliance Review Agent | EXISTING | `departments/07-quality-security/specialists/compliance_review_agent.py` — `compliance_review`, gate None. Compliance review DRAFT; never legal advice. |

## Missing roles (no worker)

- Backup & Recovery Agent — built 2026-11-21 (skill + worker EXISTING).
- Voice Quality Testing — partly covered (QAEngineer), no dedicated worker.

Phase 3 (2026-11-19): 6 new specialists built — Call Scenario
Testing, Workflow Testing, Data Validation, Security Monitoring, Access
Control, Compliance Review — all EXISTING, DRAFT only, gate None.
The manager now loads and runs them with importlib; for QAEngineer it
builds a DRAFT of the delegation plan as before.

## Gate

- `ok` (ChiefQualitySecurityAgent): using the delegation plan needs Boss's
  "ok".
- None (QAEngineer): the QA checklist itself is safe — the verdict is not the final word,
  delivery needs Boss's ok.
- None (6 new specialists): the draft itself is safe — DRAFT only, no gate.

## Honest limits

- All output is DRAFT, mock brain ($0). The delegation plan is the final word — no
  QA/security check is executed.
- No backup system — nothing about backup/recovery is tracked.
- No client facts/statistics are invented — if absent, "BOSS INPUT REQUIRED".
- Dental/medical/patient-health is never a target.
- Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.
- Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.
