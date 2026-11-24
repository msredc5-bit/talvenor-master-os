---
name: payment-rails-checker
description: "Write the Gate 0 test steps and record Boss's result — Lemon Squeezy signup (individual, checking whether BD bank payout is available), and if it fails, the fallback order: Polar → Gumroad (as an"
---

# Skill: Payment-Rails Checker

**Role:** Write the Gate 0 test steps and record Boss's result — Lemon Squeezy signup (individual, checking whether BD bank payout is available), and if it fails, the fallback order: **Polar** → **Gumroad** (as an individual, not an LLC).
**Agent:** `sections/finance/agents/payment_rails_checker.py` — `PaymentRailsCheckerAgent` (task kind `gate0_check`, section `finance`)
**Status: this role watches Gate 0** — but never signs up itself, never writes "PASSED" itself.

## Product (locked facts)

- **What Gate 0 is:** before building the Vet Kit, first verify — whether signup + payout on Lemon Squeezy works from Bangladesh as an individual. New signups are triaged — they may be sent toward Stripe Managed Payments, where Bangladesh is excluded. So test first, then build.
- **Rail fees (research report §2, 2026-11-12):** Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80 effective, $100 min payout.
- **Kit price:** $49 one-time (launch $39 for the first 30 buyers).

## Inputs

- `02-Digital-Product-Department/gate0-status.md` (the only true source — unless "Status: PASSED" is written, it is NOT PASSED).
- Task payload `boss_result` (optional) — Boss's reported result, recorded only when Boss reports it.
- Research report §2 (rails verification 2026-11-12).

## Step-by-step method (Gate 0 test — Boss's step, ~15 min, $0)

1. **Go to lemonsqueezy.com.**
2. **Sign up as an individual** (not MAINUDDIN LLC — the LLC is US-registered with no US bank, so individual is the right path).
3. **Look at the payout method** — check whether BD bank payout is available.
4. **Report the result:** pass / fail / what it said (a screenshot helps).
5. **If it fails (triage/blocked), test the backup rail — Polar** (BD is on the seller/payout list, Stripe Connect Express).
6. **If Polar also fails, Gumroad** (BD bank payout exists, must register as an individual).
7. **If all rails are closed, the product track is fully KILLed** — the kit will not be built, Boss will be told. A product cannot be built with no way to receive money.

## Output format

- Gate 0 test steps (6 steps) + rail fees + the current Status read from gate0-status.md.
- If Boss's result exists: record it as a verbatim quote — "Result reported by Boss (record only — not this agent's verdict)" + a note that this agent never writes PASSED itself, and changing the Status line of gate0-status.md is a manual step on Boss's word.
- If Boss's result does not exist: "Boss's result has not arrived yet — it will be recorded only when Boss tests and reports it."

## Tools used

- Read-only file read: `gate0-status.md` (Status line).
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the test steps DRAFT, not a live call.
- ApprovalGateway for gated work (PENDING record) — this skill has no gate, only checking + recording.
- No live tool, network, signup, or file write.

## Gate

- No gate — this is only checking + recording.
- Signup is Boss's own step — the agent never signs up itself.

## Honest limits

- **Gate 0 NOT PASSED** — the test has not happened. Without Boss's result there is no verdict.
- If all rails are closed, the product track is KILLed — this is the kill criteria, written in advance.
- Etsy is closed for Bangladesh — never in the plan (hard no).

## Never does this

- Signs up on Lemon Squeezy / Polar / Gumroad itself.
- Writes Gate 0 "PASSED" on its own — without Boss's result.
- Brings Etsy into the plan; writes any file.

## Worked example (with real repo facts)

- **Task:** `{"type": "gate0_check", "title": "Gate 0 test steps"}` → `PaymentRailsCheckerAgent.run()`.
- **Agent does:** reads `gate0-status.md` — Status NOT PASSED (2026-11-16); writes the 6-step test steps + rail fees (Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80, $100 min payout).
- **Result:** status `draft-ready`; the output says "Boss's result has not arrived yet" — no verdict. If Boss had reported as example input "Lemon Squeezy signup done, BD bank payout visible" (this is example input, not the real result), the agent would record it as a verbatim quote — it would not write "PASSED" itself.
