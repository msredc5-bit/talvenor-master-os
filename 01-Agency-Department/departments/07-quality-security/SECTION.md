# Department 07: Quality & Security — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency-র কাজের মান আর নিরাপত্তা —
receptionist-এর QA, call scenario / workflow / data যাচাই, security
monitoring, access control, backup, compliance review। Manager 6 নতুন
specialist-কে load করে চালায় (DRAFT only); QAEngineer-এর জন্য শুধু
task-কে specialist-এর কাছে route করার DELEGATION PLAN-এর DRAFT বানায়।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।
Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefQualitySecurityAgent | `departments/07-quality-security/manager/chief_quality_security_agent.py` | `departments/07-quality-security/skills/chief-quality-security-agent.md` | `ok` |

Manager-এর কাজ: `manage_quality_security` — task_kind দেখে specialist
ঠিক করা; 6 নতুন specialist-কে load করে চালানো, QAEngineer-এর জন্য
delegation plan-এর DRAFT বানানো। নিজে কোনো QA/security check চালানো
নয়। Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| QAEngineer | `receptionist_qa` | `engine/workers/src/workers/delivery.py` | None | EXISTING |

- **QAEngineer** — demo receptionist READY বলার আগে 12-check QA checklist:
  prompt completeness, ভাঙা tool reference নেই, emergency flow, pricing
  honesty, transfer number আসল-না-অনুপস্থিত, end_call behavior। Verdict
  READY অথবা CHANGES — delivery-তে Boss-এর ok লাগে।
- **Shared:** QAEngineer dept 03 Testing & Debugging-এর সঙ্গেও shared —
  একই worker, দুই department-এ map করা।

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Voice Quality Testing Agent | EXISTING (partial) | QAEngineer-এর 12-check checklist voice quality আংশিক cover করে; dedicated voice-quality worker নেই। |
| Call Scenario Testing Agent | EXISTING | `departments/07-quality-security/specialists/call_scenario_testing_agent.py` — `call_scenario_testing`, gate None। Call-scenario test script DRAFT; কখনো live call নয়। |
| Workflow Testing Agent | EXISTING | `departments/07-quality-security/specialists/workflow_testing_agent.py` — `workflow_testing`, gate None। Workflow test check-script DRAFT; কখনো live run নয়। |
| Data Validation Agent | EXISTING | `departments/07-quality-security/specialists/data_validation_agent.py` — `data_validation`, gate None। Data validation DRAFT; ফলাফল বানায় না। |
| Security Monitoring Agent | EXISTING | `departments/07-quality-security/specialists/security_monitoring_agent.py` — `security_monitoring`, gate None। Security monitoring checklist DRAFT; কখনো live monitoring নয়। |
| Access Control Agent | EXISTING | `departments/07-quality-security/specialists/access_control_agent.py` — `access_control`, gate None। Access-control DRAFT; কোনো access বদলায় না। |
| Backup & Recovery Agent | GAP | Repo-তে কোনো backup system নেই — worker-ও নেই, skill-ও নেই। |
| Compliance Review Agent | EXISTING | `departments/07-quality-security/specialists/compliance_review_agent.py` — `compliance_review`, gate None। Compliance review DRAFT; কখনো legal advice নয়। |

## Missing roles (worker নেই)

- Backup & Recovery Agent — GAP (repo-তে কোনো backup system নেই)।
- Voice Quality Testing — আংশিক আছে (QAEngineer), dedicated worker নেই।

Phase 3 (2026-11-19): 6 নতুন specialist বানানো হয়েছে — Call Scenario
Testing, Workflow Testing, Data Validation, Security Monitoring, Access
Control, Compliance Review — সবাই EXISTING, DRAFT only, gate None।
Manager এখন এদের importlib দিয়ে load করে চালায়; QAEngineer-এর জন্য
আগের মতো delegation plan-এর DRAFT বানায়।

## Gate

- `ok` (ChiefQualitySecurityAgent): delegation plan ব্যবহার করতে Boss-এর
  "ok" লাগে।
- None (QAEngineer): QA checklist নিজেই নিরাপদ — verdict-ই শেষ কথা নয়,
  delivery-তে Boss-এর ok লাগে।
- None (6 নতুন specialist): draft নিজেই নিরাপদ — DRAFT only, কোনো gate নেই।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। Delegation plan-ই শেষ কথা — কোনো
  QA/security check execute নয়।
- Backup system নেই — backup/recovery-র কিছু track করা হয় না।
- কোনো client তথ্য/পরিসংখ্যান বানানো নয় — না থাকলে "BOSS INPUT REQUIRED"।
- Dental/medical/patient-health কখনো target নয়।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
