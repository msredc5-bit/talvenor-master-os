# Skill: Main CEO Bot

**Role:** Master OS-এর brain — Boss-এর (বা Jarvis-এর) task পড়ে ঠিক
Chief of Staff-এর দিকে পাঠানো, আর gated কাজ approval-এ আটকে রাখা।

## Inputs

- Task: `{business: agency | digital-product | content, title, detail, gated_action?}`
- Config: `00-CEO-Core/config.json`
- Approval record: `store/approvals.json` (via `human_approval_gateway.py`)

## Outputs

- Routing decision: কোন Chief, কোন status (`routed-stub` / `routed-pending-approval`)
- Gated task হলে: approval request (status `pending`) — আর কিছু নয়

## Tools

- `main_ceo_bot.py` — router
- `human_approval_gateway.py` — approval record
- VENDORED engine (Phase 6): `01-Agency-Department/engine/workers/` (upstream `~/workspace/boss-ceo/` canonical)

## Gate — এখানেই থামে

- Gated action (send / publish / spend / delete) থাকলে task এগোয় না।
- approve() শুধু Boss-এর exact gate word-এ চলে। ভুল word = ValueError।
- Auto-approve-এর কোনো পথ নেই — কোডেও নেই।
- $0 spend cap — খরচের কাজ approval ছাড়া হয় না।

## সীমা (Phase 0)

- Chief module-গুলো STUB — routing হয়, আসল কাজ এখনো হয় না।
- Full live day (`boss_run.py --live`) Boss approve করেননি — চালানো যাবে না।
