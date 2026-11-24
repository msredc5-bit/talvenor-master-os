---
name: chief-strategy-agent
description: "Chief Strategy Agent · Manager: ChiefStrategyAgent"
---

# Skill: Chief Strategy Agent — Agency Department 05 (Phase 1)

**Role:** Chief Strategy Agent · **Manager:** `ChiefStrategyAgent`
· **Task type:** `manage_research_strategy` · **Gate:** `ok`
· **Department:** 05-research-strategy (Research & Strategy)
· **Agent file:** `departments/05-research-strategy/manager/chief_strategy_agent.py`

**Business:** Talvenor AI Receptionist Agency — strategy-level research
a DRAFT of the delegation plan for routing a task to the right specialist.
This manager does no research itself; it loads and runs the Phase 3 specialists with importlib (DRAFT only).

## Goal

From the strategy research task Boss gave (competitor, industry, pricing,
niche, offer, market, business intelligence), pick the right specialist
and make a small DRAFT of a delegation plan — with the specialist's name,
their file/skill, gate, and honest status. The plan is the final word; no execution.

## Instructions (step-by-step)

1. Look at the task's `task_kind` — whether it is in `DEPARTMENT_TASKS`.
2. If not: `unknown-task` status — with the department's known task kinds
   listed, asking Boss to give the correct task_kind. No worker is run.
3. If present: write a DRAFT of the delegation plan with the specialist, file/skill, gate, status
   — starting with `[MOCK DRAFT]`.
4. If a specialist, write their real file path + EXISTING status; if GAP, write it clearly.
5. If there is a `gated_action`, approval first — no draft without approval,
   record PENDING and stop.
6. Show the plan to Boss — Boss's "ok" is needed to use it.

## Department task kinds

| Task kind | Specialist | Gate | Status |
|---|---|---|---|
| `competitor_research` | Competitor Research Agent | none | EXISTING |
| `industry_research` | Industry Research Agent | none | EXISTING |
| `pricing_research` | Pricing Research Agent | none | EXISTING |
| `niche_selection` | Niche Selection Agent | none | EXISTING |
| `offer_development` | Offer Development Agent | none | EXISTING |
| `market_opportunity` | Market Opportunity Agent | none | EXISTING |
| `business_intelligence` | Business Intelligence Agent | none | EXISTING |

## Tools

- `run(task, brain=None, gateway=None, approvals_path=None)` — delegation
  makes a plan DRAFT. Stdlib only (`os`, `sys`). Writes no file,
  touches no network.
- ApprovalGateway (lazy import, `00-CEO-Core`) — to record a PENDING
  for a gated action.
- Mock brain ($0) — if a brain exists, a note is taken from `brain.complete()`;
  If there is none, the plan is built from the payload itself.

## Permissions

- Can make a DRAFT; can show the delegation plan to Boss.
- Gate word `ok` — Boss's "ok" is needed to use the plan.
- Cannot send, cannot spend, cannot execute an engine/section worker (except a Phase 3 specialist load+run),
  cannot publish/delete anything.

## Handoff rules

- Giving the plan's specialist the task is Boss's decision — the manager calls the Phase 3 specialists with importlib (DRAFT only).
- If a prospect-level research task comes in, do not route it — that is ProspectResearcher's
  (dept 01 Sales) job; tell Boss.
- Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING;
  handoff is now through the Chief (DEPARTMENT_ROUTING).

## Success criteria

- The right specialist + file/skill + gate + status — all four are in the plan.
- For an unknown task_kind, `unknown-task` + a list of known kinds.
- No invented information/prices/statistics; if not available, "BOSS INPUT REQUIRED".
- No engine/section worker execution, no sending, no spending.

## Honest status

- **Phase 3 DONE 2026-11-19** — all 7 specialists are EXISTING (with skill + worker code).
- **Paying client 0; first mail 163; Email PAUSED (since 2026-11-14).**
- Brain mock ($0) — all output is DRAFT.
- Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.

## Never-do list

- Never executes an engine/section worker, never researches itself.
- Never sends anything, spends anything, or publishes/deletes anything.
- Never invents client/competitor/price/statistic facts.
- Never quotes a price to a prospect; LOCKED pricing internal only.
- Never takes dental/medical or patient-health businesses.
- Never gives any guarantee, never gives an invented testimonial/client.
