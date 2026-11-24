---
name: niche-selection-agent
description: "Niche Selection Agent · Worker: NicheSelectionAgent"
---

# Skill: Niche Selection Agent — Agency Department 05 (Phase 3)

**Role:** Niche Selection Agent · **Worker:** `NicheSelectionAgent`
· **Task type:** `niche_selection` · **Gate:** none
· **Department:** 05-research-strategy (Research & Strategy)
· **Worker file:** `departments/05-research-strategy/specialists/niche_selection_agent.py`

**Business:** Talvenor AI Receptionist Agency — checking which niche to enter — dental/medical always DQ.

## Goal

Making a DRAFT of niche selection from the topic Boss gave — dental/medical always DQ, legal kept gated until the 4th client.

## Instructions (step-by-step)

1. Look at the task's `payload.topic` — if missing, "BOSS INPUT REQUIRED".
2. Check against the list of valid niches: plumbing, HVAC, roofing, garage door, septic, tree, foundation, restoration, pest, vet.
3. If dental/medical/patient-health, write DQ directly — never a target.
4. If legal, write GATED — not before the 4th client.
5. If there is a `gated_action`, approval first — no draft without approval, record PENDING and stop.

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — niche selection draft Makes it.
  Stdlib only (`os`, `sys`). Writes no file, touches no network.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record a PENDING
  for a gated action.
- Mock brain ($0) — if a brain exists, a note is taken from `brain.complete()`;
  If there is none, the draft is built from the payload itself.

## Permissions

- Can make a DRAFT; can show the draft to Boss.
- Gate: none — the draft itself is safe, there is no gate.
- Cannot send, cannot spend, cannot publish/delete.

## Handoff rules

- The draft is shown to Boss; using/sending it is Boss's decision.
- Manager Chief Strategy Agent (`manage_research_strategy`) loads this worker
  with importlib and runs it; handoff through the Chief
  (DEPARTMENT_ROUTING → manager → specialist).
- If there is unknown information, write "BOSS INPUT REQUIRED" in the draft — no guessing.

## Success criteria

- Dental/medical always DQ; legal written as gated.
- No niche was called final without Boss's decision.
- Output starts with `[MOCK DRAFT]`, DRAFT ONLY.

## Honest status

- **Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).**
- Brain mock ($0) — all output is DRAFT.
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.

## Never-do list

- Never targets dental/medical/patient-health.
- Never opens legal before the 4th client.
- Never sends anything, spends anything, or publishes/deletes anything.
- Never quotes a price to a prospect; LOCKED pricing internal only.
- Never gives any guarantee, never gives an invented testimonial/client.
