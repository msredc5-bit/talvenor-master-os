# Product Section — Building the Vet Kit + QA

**Purpose:** Give the build order from the Vet No-Show Recovery Kit's blueprint and write a QA checklist DRAFT for the 6 parts — not building the kit itself (it cannot be built before Gate 0 passes).

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Kit Builder | `agents/kit_builder.py` (`KitBuilderAgent`, task `kit_build`) | `skills/kit-builder.md` | `ok` | Existing role — new file as a section agent |
| Kit QA | `agents/kit_qa.py` (`KitQAAgent`, task `kit_qa`) | `skills/kit-qa.md` | `ok` | **NEW** role (Phase 7) |

## How work flows

1. Main CEO Bot → Products Chief (`chief_of_staff_products.py`) → routing by task type.
2. `kit_build` — the Chief's existing ROUTING branch (returns the blueprint); section agent `KitBuilderAgent` gives the same blueprint summary + build order, and if Gate 0 is NOT PASSED, status is `blocked-gate0`.
3. `kit_qa` — the Chief's `SECTION_ROUTING` branch (Phase 7, new) → `KitQAAgent` → "NOT BUILT — nothing to QA yet" + per-part QA checklist DRAFT.
4. For gated work (`send` / `publish` / `spend` / `delete`), the agent is not run — a PENDING request is written to the ApprovalGateway.

## Gates

- Boss's `ok` is needed to start building / use the output.
- No part of the kit can be built until Gate 0 passes.

## Honest limits

- **Gate 0 NOT PASSED** — the Lemon Squeezy signup test is Boss's step, still pending.
- **Kit 0/6 built** — only the blueprint (`kit-outline.md`) exists; there is nothing to QA.
- **PA list 39/100, sale 0**, email **PAUSED** (since 2026-11-14).
- No agent writes a file, touches the network, or marks anything as sold/launched.
