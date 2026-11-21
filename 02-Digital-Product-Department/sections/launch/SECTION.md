# Launch Section — Launch Checklist DRAFT

**Purpose:** Build a DRAFT of the Vet Kit launch checklist — not the launch itself.

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Launch Manager | `agents/launch_manager.py` (`LaunchManagerAgent`, task `launch_prep`) | `skills/launch-manager.md` | `go` | Existing role — new file as a section agent |

## How work flows

1. Main CEO Bot → Products Chief → `launch_prep` (existing ROUTING branch).
2. Section agent `LaunchManagerAgent` gives a checklist DRAFT: Gate 0 → the kit's 6 parts → Gate 1 check → Lemon Squeezy listing + Gumroad backup → sales page (Boss review) → email 100 clinics at 25 a day (4 days) → write replies + sales in a sheet.
3. If Gate 0 is NOT PASSED, status is `blocked-gate0` — nothing is marked as launched.
4. If `mark_launched` / `mark_sold` is requested, both the Chief and the agent return `blocked-gate0`.

## Gates

- Boss's `go` is needed to move the launch forward.
- No launch can happen until Gate 0 passes.

## Honest limits

- **Gate 0 NOT PASSED** — no launch has happened.
- **Kit 0/6 built, PA list 39/100, sale 0**, email **PAUSED** (since 2026-11-14).
- No agent writes a file, sends mail, touches the network, or records a sale.
