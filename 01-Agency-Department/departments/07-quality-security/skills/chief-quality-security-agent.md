# Skill: Chief Quality Security Agent — Agency Department 07 (Phase 1)

**Role:** Chief Quality Security Agent · **Manager:** `ChiefQualitySecurityAgent`
· **Task type:** `manage_quality_security` · **Gate:** `ok`
· **Department:** 07-quality-security (Quality & Security)
· **Agent file:** `departments/07-quality-security/manager/chief_quality_security_agent.py`

**Business:** Talvenor AI Receptionist Agency — routing quality/security tasks to
the right specialist. The manager loads and runs 6 new specialists (Phase 3)
with importlib; for QAEngineer it builds a DRAFT of the delegation
plan. This manager itself runs no QA/security check.

## Goal

From the quality/security task Boss gave (receptionist QA, voice quality,
call scenario, workflow, data validation, security monitoring, access
control, backup & recovery, compliance review), pick the right specialist
— load and run the 6 new specialists, and for QAEngineer build a DRAFT of the
delegation plan (with the specialists' names, their file/skill,
gate, and honest status). The specialist's output DRAFT is the final word;
not execution, not running a check yourself.

## Instructions (step-by-step)

1. Look at the task's `task_kind` — whether it is in `DEPARTMENT_TASKS`.
2. If absent: `unknown-task` status — with a list of the department's known task kinds,
   ask Boss to give the correct task_kind. Run no worker.
3. If present: if it is one of the 7 specialists, load it with importlib
   and run it — return its result; if it is QAEngineer, write a DRAFT of the delegation
   plan — starting with `[MOCK DRAFT]`.
4. If QAEngineer, write: also shared with dept 03 Testing & Debugging;
   voice quality is only partly covered, no dedicated worker.
5. If Backup & Recovery, load and run the specialist (DRAFT plan only; restore test not done).
6. If `gated_action` is present, approval first — not even a draft without approval,
   record PENDING and stop.
7. Show the plan to Boss — using it needs Boss's "ok".

## Department task kinds

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `receptionist_qa` | QAEngineer | None | EXISTING |
| `voice_quality_testing` | QAEngineer (partial) | None | EXISTING |
| `call_scenario_testing` | Call Scenario Testing Agent | None | EXISTING |
| `workflow_testing` | Workflow Testing Agent | None | EXISTING |
| `data_validation` | Data Validation Agent | None | EXISTING |
| `security_monitoring` | Security Monitoring Agent | None | EXISTING |
| `access_control` | Access Control Agent | None | EXISTING |
| `backup_recovery` | Backup & Recovery Agent | `ok` | EXISTING |
| `compliance_review` | Compliance Review Agent | None | EXISTING |

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — loads and runs 7 specialists, and builds a delegation plan DRAFT for QAEngineer
  DRAFT. Stdlib only (`os`, `sys`, `importlib`). Writes no file,
  touches no network.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record PENDING
  for a gated action.
- Mock brain ($0) — if a brain is present, a note is taken from `brain.complete()`;
  if absent, the plan is built from the payload itself.

## Permissions

- Can build a DRAFT; can show the delegation plan to Boss.
- Gate word `ok` — using the plan needs Boss's "ok".
- Cannot run any QA/security check itself, cannot execute QAEngineer,
  cannot send/spend/publish/delete anything.

## Handoff rules

- Giving a task to a specialist in the plan is Boss's decision — the manager itself loads and runs 7 specialists; for QAEngineer it
  only builds a delegation plan, does not run it.
- When a QA task arrives, QAEngineer's verdict is not the final word — delivery needs
  Boss's ok.
- When a backup & recovery task arrives, load and run the specialist (DRAFT plan only; restore test not done — NOT VERIFIED).
- Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING;
  handoff now goes through the Chief (DEPARTMENT_ROUTING).

## Success criteria

- The right specialist + file/skill + gate + status — all four are in the plan.
- If task_kind is unknown, `unknown-task` + a list of the known kinds.
- Shared/partial — an honest note is in the plan, not hidden.
- No invented facts/statistics; if absent, "BOSS INPUT REQUIRED".
- No QAEngineer is executed, no check is run by itself.

## Honest status

- **Mapped staff 8** — QAEngineer (also shared with dept 03) + 7 specialists (6 from Phase 3 + Backup & Recovery 2026-11-21; all DRAFT only, gate None); voice quality partial; backup & recovery EXISTING — DRAFT plan only, restore test not done.
- **Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).**
- Brain mock ($0) — all output is DRAFT.
- Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.

## Never-do list

- Never runs any QA/security check itself; never executes QAEngineer
  (only builds a plan for it).
- Never sends anything, spends, or publishes/deletes.
- Never invents client facts/statistics.
- Never claims a backup exists — there is no backup system.
- Never takes dental/medical or patient-health business.
- Never gives any guarantee, never gives an invented testimonial/client.
