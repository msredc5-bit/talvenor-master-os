# Finance Section — Gate 0 Payment Rails

**Purpose:** Write the Gate 0 test steps and record Boss's result — Lemon Squeezy signup (BD individual), and if it fails, Polar → Gumroad (individual, not LLC).

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Payment-Rails Checker | `agents/payment_rails_checker.py` (`PaymentRailsCheckerAgent`, task `gate0_check`) | `skills/payment-rails-checker.md` | — (none) | Existing role — new file as a section agent |

## How work flows

1. Main CEO Bot → Products Chief → `gate0_check` (existing ROUTING branch).
2. Section agent `PaymentRailsCheckerAgent` writes the test steps (6 steps) + rail fees (Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80, $100 min payout) + the current Status read from gate0-status.md.
3. Boss's result is recorded only when Boss reports it — as a verbatim quote, not this agent's verdict. The agent itself never writes "PASSED", never changes the Status line of gate0-status.md — it writes no file at all.
4. If all rails are closed, the product track is fully KILLed — Boss will be told.

## Gates

- No gate — this is only checking + recording.
- Signup is Boss's own step (~15 min, $0) — the agent never signs up itself.

## Honest limits

- **Gate 0 NOT PASSED** — the test has not happened; without Boss's result there is no verdict.
- **Kit 0/6 built, PA list 39/100, sale 0**.
- Etsy hard no — closed for Bangladesh, never in the plan.
- No agent signs up, writes a file, touches the network, or writes PASSED/FAILED on its own.
