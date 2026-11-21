# store/ — Live Queue + Live State (policy)

The files in this folder are **live state** — written here, read from here.
The push rule differs per file.

## Live queue — tracked, in the push plan

| File | Job | Push |
|---|---|---|
| `tasks.json` | Task queue — the taskboard + bridge cron write/read here. 2026-11-21: 1 done record (booking-link verification, 2026-11-20). | **Tracked** — in PUSH-PLAN-Phase-9-10.md; will also be in the next push plan. |
| `approvals.json` | ApprovalGateway records. | Live state — part of the queue like tasks.json; push only if it is in the push plan. |

## Live state — in no push plan yet

| File | Job | Push |
|---|---|---|
| `memory.json` | Owner memory — Boss's verbatim quote (central store + box). Rewritten often. | **In no push plan** — push only on Boss's word. |
| `MEMORY.md` | Export of `memory.json` (human-readable). | **In no push plan** — push only on Boss's word. |
| `schedules.json` | Quiet schedule seed (`taskboard-queue-watch`, paused). | **In no push plan** — push only on Boss's word. |
| `confirmations.json` | ConfirmationStore — run-once confirmation records. | **In no push plan** — push only on Boss's word. |
| `usage_ledger.json` | $0 usage ledger — mock is always $0.00. | **In no push plan** — push only on Boss's word. |

Even when a future file arrives (`skill-proposals.json` — skill-finder's DRAFT proposal,
not yet built), the same rule applies: live state, push only on Boss's word.

## Rules

- **`.gitignore` has not been changed** — pushes happen with an explicit manifest (snapshot-push),
  not via gitignore. So this policy is written in this README — not in `.gitignore`.
- Before pushing a live-state file, ask Boss — a snapshot is being taken,
  and that is a conscious decision.
- While running a check script, if another writer (bridge cron, sibling
  worker, voice loop) is active in this folder, the check may flake — see the
  2026-11-21 run-discipline note in BUILD-LOG.md.
- `vault/` — text files of the workers' real results (draft/plan/script/report);
  rules are in `store/vault/README.md`. The Vault is also in no push plan.
