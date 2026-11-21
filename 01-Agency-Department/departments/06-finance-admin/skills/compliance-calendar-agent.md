# Skill: Compliance Calendar Agent — Agency Department 06 (Phase 3)

**Role:** Compliance Calendar Agent · **Worker:** `ComplianceCalendarAgent`
· **Task type:** `compliance_calendar` · **Gate:** None
· **Department:** 06-finance-admin (Finance & Admin)
· **Worker file:** `departments/06-finance-admin/specialists/compliance_calendar_agent.py`
· **Manager:** CFO Finance Agent (`manage_finance_admin`, gate `ok`)

**Business:** Talvenor AI Receptionist Agency — a DRAFT of the compliance date
account. It invents no deadline, claims nothing legal.

## Goal

Making a DRAFT of an account of the compliance dates — what is truly known
is what is written, everything else is "BOSS INPUT REQUIRED". No deadline invented,
no legal claim made.

## Instructions (step-by-step)

1. Take the topic from the task's `payload`; if missing, "BOSS INPUT REQUIRED".
2. The compliance calendar — starting with `[MOCK DRAFT]`.
3. Write only known facts: attorney review DEFERRED — not before the first paying
   client; a dental/medical business is never a target (always
   DQ); weekly cadence Sunday 6 PM Dhaka.
4. If no date is known, "BOSS INPUT REQUIRED" — no date invented.
5. If there is a `gated_action`, approval first — no draft without approval,
   record PENDING and stop.
6. Show the draft to Boss — this draft has no gate.

## Known compliance items (2026-11-19, only known facts)

| Item | Status / Date |
|---|---|
| Attorney review (service agreement) | DEFERRED — not before the first paying client; no date |
| Dental/medical targeting | Never — always DQ |
| Weekly content plan + report | Every Sunday 6 PM Dhaka |
| Other compliance dates | BOSS INPUT REQUIRED — no date invented |

Boss will set the attorney review date when the first paying client comes.

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` —
  makes a DRAFT of the compliance calendar. Stdlib only (`os`, `sys`).
  Writes no file, touches no network.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record a PENDING
  for a gated action.
- Mock brain ($0) — if a brain exists, a note is taken from `brain.complete()`;
  If there is none, the calculation is built from the payload itself.

## Permissions

- Can make a DRAFT of the compliance calendar; can show it to Boss.
- Gate: None — the draft itself is safe.
- Cannot invent a deadline, cannot give legal advice, cannot make a legal claim
  cannot send anything, cannot spend anything.

## Handoff rules

- Legal decisions are Boss + attorney's — the worker only makes a DRAFT of the date account
  draft Makes it.
- Boss will give the attorney review date when the first paying client comes.
- The manager (CFO Finance Agent) calls this worker with `compliance_calendar`
  calls by task_kind; handoff is now Chief → manager → specialist.

## Success criteria

- The calendar has only known facts; an unknown date is "BOSS INPUT REQUIRED".
- No invented deadline, date, or legal claim.
- Output starts with `[MOCK DRAFT]`, `draft-ready`, `draft_only: True`.

## Honest status

- **No compliance deadline is known — attorney review deferred.**
- Brain mock ($0) — all output is DRAFT.
- Manager wiring Phase 3 DONE — CFO Finance Agent now calls this specialist
  calls it with `compliance_calendar`.

## Never-do list

- Never invents a deadline/date, never gives legal advice.
- Never makes a legal claim, never gives a guarantee.
- Never sends anything, spends anything, or publishes/deletes anything.
- Never takes dental/medical or patient-health businesses.
- Never gives an invented testimonial/client.
