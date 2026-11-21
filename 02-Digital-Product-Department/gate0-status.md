# Gate 0 — Lemon Squeezy Signup Test

**Status: NOT PASSED (2026-11-16)**

## What Gate 0 is

Before building the Vet Kit, first verify: whether signup + payout on
Lemon Squeezy works from Bangladesh as an individual.
New signups are triaged — they may be sent toward Stripe Managed Payments,
where Bangladesh is excluded. So test first, then build.

## Boss's step (~15 min, $0)

1. Go to lemonsqueezy.com.
2. Sign up as an individual (not MAINUDDIN LLC — the LLC is US-registered,
   with no US bank, so individual is the right path).
3. Look at the payout method — check whether BD bank payout is available.
4. Report the result: pass / fail / what it said (a screenshot helps).

## Recording the result (Boss's job)

- **Tell Elora in chat** — when Boss reports the result, Elora will update this file + the Chief
  module's Gate 0 state. (The earlier dashboard artifact was deleted
  2026-11-20 — the 3D dashboard is static, nothing can be written there).
- Only if the top **Status line** of this file says PASSED will the Chief
  treat Gate 0 as passed — otherwise fail-closed: NOT PASSED. The Chief's code
  does not treat Gate 0 as passed on its own.

## Depending on the result

- **Pass:** start the rest of Phase 2 — complete the PA list to 100, Gate 1
  (check the cadence against AAHA/PetDesk), build the kit's 6 parts, store listing,
  launch.
- **Fail (triage/blocked):** test the backup rail — **Polar** (BD is on the seller/payout
  list, Stripe Connect Express). If Polar also fails, **Gumroad**
  (BD bank payout exists, must register as an individual).
- **All rails closed:** product track fully KILLed — the kit will not be built, Boss will
  be told. A product cannot be built with no way to receive money.

## True status (2026-11-16)

- Gate 0 NOT PASSED — the test has not happened.
- What could still be done in Phase 2 (outside Gate 0, honest work): the kit
  **blueprint** (`kit-outline.md` — the design, not the kit), PA list **39/100**
  (verified), Products Chief module REAL.
- The kit's 6 parts have not been built, sale 0, no launch — after Gate 0.
