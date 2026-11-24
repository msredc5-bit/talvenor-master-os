---
name: main-ceo-bot
description: "The Master OS brain — reads Boss's (or Jarvis's) task and sends it to the right"
---

# Skill: Main CEO Bot

**Role:** The Master OS brain — reads Boss's (or Jarvis's) task and sends it to the right
Chief of Staff, and holds gated work in approval.

## Inputs

- Task: `{business: agency | digital-product | content, title, detail, gated_action?}`
- Config: `00-CEO-Core/config.json`
- Approval record: `store/approvals.json` (via `human_approval_gateway.py`)

## Outputs

- Routing decision: which Chief, which status (`routed-stub` / `routed-pending-approval`)
- If the task is gated: an approval request (status `pending`) — nothing more

## Tools

- `main_ceo_bot.py` — router
- `human_approval_gateway.py` — approval record
- VENDORED engine (Phase 6): `01-Agency-Department/engine/workers/` (upstream `~/workspace/boss-ceo/` canonical)

## Skill-finder — when a new capability is needed

- Skill: `skills/skill-finder.md` — the search procedure (local first →
  skills.sh leaderboard → verify → shortlist → Boss confirm → adapt).
- Code: `00-CEO-Core/skill_finder.py` — local search + DRAFT proposal
  (`store/skill-proposals.json`). When a task of type `find_skill` arrives, the router
  goes here — not to a Chief.
- Searching is allowed; writing / installing a skill file is not — Boss's "ok" is needed.

## Gate — stops here

- If a gated action (send / publish / spend / delete) is present, the task does not move forward.
- approve() runs only on Boss's exact gate word. Wrong word = ValueError.
- There is no path to auto-approve — not even in the code.
- $0 spend cap — spending work does not happen without approval.

## Limits (Phase 0)

- The Chief modules are STUBs — routing happens, the real work does not yet.
- The full live day (`boss_run.py --live`) has not been approved by Boss — it cannot be run.
