# Department 07: Quality & Security — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency-র কাজের মান আর নিরাপত্তা —
receptionist-এর QA, call scenario / workflow / data যাচাই, security
monitoring, access control, backup, compliance review। এই department
কোনো check নিজে চালায় না — manager শুধু task-কে specialist-এর কাছে
route করার DELEGATION PLAN-এর DRAFT বানায়।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।
Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefQualitySecurityAgent | `departments/07-quality-security/manager/chief_quality_security_agent.py` | `departments/07-quality-security/skills/chief-quality-security-agent.md` | `ok` |

Manager-এর কাজ: `manage_quality_security` — task_kind দেখে specialist
ঠিক করা, delegation plan-এর DRAFT বানানো। Worker execute নয়, কোনো QA/
security check নিজে চালানো নয়। Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

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
| Call Scenario Testing Agent | ROLE-ONLY | Role definition only — call scenario test-এর ভাবনা; worker নেই। |
| Workflow Testing Agent | ROLE-ONLY | Role definition only — workflow test-এর ভাবনা; worker নেই। |
| Data Validation Agent | ROLE-ONLY | Role definition only — data যাচাইয়ের ভাবনা; worker নেই। |
| Security Monitoring Agent | ROLE-ONLY | Role definition only — security নজরদারির ভাবনা; worker নেই। |
| Access Control Agent | ROLE-ONLY | Role definition only — কে কী দেখতে/বদলাতে পারে, তার ভাবনা; worker নেই। |
| Backup & Recovery Agent | GAP | Repo-তে কোনো backup system নেই — worker-ও নেই, skill-ও নেই। |
| Compliance Review Agent | ROLE-ONLY | Role definition only — compliance review-এর ভাবনা; worker নেই। |

## Missing roles (worker নেই)

- Backup & Recovery Agent — GAP (repo-তে কোনো backup system নেই)।
- Call Scenario Testing, Workflow Testing, Data Validation, Security
  Monitoring, Access Control, Compliance Review — ROLE-ONLY: role
  definition আছে, worker নেই, skill .md registry-তে এখনো বানানো হয়নি।
- Voice Quality Testing — আংশিক আছে (QAEngineer), dedicated worker নেই।

## Gate

- `ok` (ChiefQualitySecurityAgent): delegation plan ব্যবহার করতে Boss-এর
  "ok" লাগে।
- None (QAEngineer): QA checklist নিজেই নিরাপদ — verdict-ই শেষ কথা নয়,
  delivery-তে Boss-এর ok লাগে।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। Delegation plan-ই শেষ কথা — কোনো
  QA/security check execute নয়।
- Backup system নেই — backup/recovery-র কিছু track করা হয় না।
- কোনো client তথ্য/পরিসংখ্যান বানানো নয় — না থাকলে "BOSS INPUT REQUIRED"।
- Dental/medical/patient-health কখনো target নয়।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
