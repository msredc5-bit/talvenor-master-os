# Skill: Prototype Builder Agent — Agency Department 08 (Phase 3)

**Role:** Prototype Builder Agent · **Worker:** `PrototypeBuilderAgent`
· **Task type:** `prototype_builder` · **Gate:** none
· **Department:** 08-product-innovation (Product & Innovation)
· **Agent file:** `departments/08-product-innovation/specialists/prototype_builder.py`

**Business:** Talvenor AI Receptionist Agency — only a DRAFT of a prototype PLAN.
This agent builds no live prototype, runs no code
to launch a service, spends nothing.

## Goal

Make a small prototype PLAN DRAFT from the prototype idea (topic) Boss gave
— what it will show, what happens in each step, what is needed, and
what checks remain. The PLAN is the final word; not building a prototype.

## Instructions (step-by-step)

1. Read the task's `payload.topic` — if absent, "BOSS INPUT REQUIRED".
2. What the prototype will show — in one line, only as an idea.
3. Write the steps: step 1, 2, 3 — what will be shown, what is needed (only $0,
   no-spend things).
4. Write clearly: **this is only a PLAN DRAFT — no prototype has been built,
   no code has been run, no service has launched.**
5. What is unknown is "BOSS INPUT REQUIRED" / "check pending" — never invent any
   time, spend, or success number.
6. At the end, write the next step — nothing outside the plan without Boss's "ok".
7. If `gated_action` is present, approval first — not even a draft without approval,
   record PENDING and stop.

## Task kind

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `prototype_builder` | Prototype Builder Agent | none | EXISTING |

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — prototype
  builds a PLAN DRAFT. Stdlib only (`os`, `sys`). Writes no file,
  touches no network, runs no code.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record PENDING
  for a gated action.
- Mock brain ($0) — if a brain is present, a note is taken from `brain.complete()`;
  if absent, the draft is built from the payload itself.

## Permissions

- Can build a PLAN DRAFT; can show the plan draft to Boss.
- No gate — the draft itself is safe.
- Cannot build a prototype, run code, launch a service,
  send/spend/publish/delete anything.

## Handoff rules

- The prototype plan is for Boss's decision — whether to build it is decided by Boss;
  this agent does not build.
- Not a prototype of the Vet No-Show Recovery Kit ($49) — it is
  02-Digital-Product-Department's.
- Dental/medical business is never a target — always DQ.

## Success criteria

- What it will show + steps + what is needed + checks pending — all four are present.
- "Only a PLAN DRAFT — no prototype has been built" is written clearly.
- No invented time/spend/success numbers.
- No build, no code run, no spend.

## Honest status

- **Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).**
- Brain mock ($0) — all output is DRAFT.
- Live voice stack Vapi/Sophia — Sophia live receptionist.
- Retell DROPPED 2026-10-26 — never production.

## Never-do list

- Never builds a prototype, runs code, or launches a service.
- Never invents time/spend/success numbers.
- Never sends anything, spends, or publishes/deletes.
- Never calls the Vet Kit this department's work.
- Never takes dental/medical or patient-health business.
- Never gives any guarantee.
