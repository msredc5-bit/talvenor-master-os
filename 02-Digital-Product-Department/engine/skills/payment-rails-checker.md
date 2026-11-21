# Skill: Payment-Rails Checker

**Role:** Write the Gate 0 test steps + record Boss's result — never
signs up itself.
**Status: Gate 0 NOT PASSED** — Boss's Lemon Squeezy test is pending.

## Rails (research report §2 — verified live 2026-11-12)

| Platform | For a BD founder? | Fee per sale | Payout | Verdict |
|---|---|---|---|---|
| **Lemon Squeezy** | YES — BD is on the official bank-payout list [VERIFIED] | 5% + $0.50 (+1.5% int'l buyer) | $50 min; created 1st/15th, 13-day hold, paid 14th/28th; 1% payout fee to non-US bank | **Primary rail.** Sunset risk, no date; test signup first. |
| **Polar** | YES — BD is on the seller/payout list via Stripe Connect Express [STRONG INDICATION] | 5% + $0.50 (+1.5% non-US card); payout $2/mo + 0.25% + 25¢ | 7-day settlement for new orgs; account review up to 14 days | **Best backup.** BD individual-vs-business eligibility: UNKNOWN — check before committing. |
| **Gumroad** | YES — bank payouts in BDT to a BD bank [VERIFIED] | 10% + $0.50 plus 2.9% + $0.30 card processing (≈12.9% + $0.80 effective); 30% via Discover | $100 min; weekly (BD payout day Tuesday); 7-day hold | Fallback. **LLC catch: register as an INDIVIDUAL in Bangladesh, not as MAINUDDIN LLC** — the bank account must be in the country where the business is registered, and the LLC is US-registered with no US bank. |
| **Paddle** | YES, conditional — BD is not on the unsupported-countries list [VERIFIED] | 5% + $0.50, all-inclusive | $100 min; monthly, by the 15th; wire or Payoneer (Payoneer is Boss's LOCKED — use wire; $15 SWIFT fee for BD: UNKNOWN) | Viable but gated by approval review; approval can be refused without reason. |
| **Etsy** | **NO** — BD is not on the eligible-countries list [VERIFIED] | — | — | **Hard no. Do not build on Etsy.** |

Worked example, $49 sale (US card): Lemon Squeezy keeps $46.05; Paddle
$46.05; Polar ~$46.05; Gumroad ~$41.88. Cash timing (Lemon Squeezy):
sale → bank ≈ 3–5 weeks (13-day hold + payout cycle + 1–5 days transfer).

## Inputs

- `02-Digital-Product-Department/gate0-status.md` — the only true source
  for Gate 0 ("Status: PASSED" not written means NOT PASSED)
- Research report §2 + `notes/payment-rails-verification-20261112.md`
- Boss's result (pass / fail / what it said, screenshot if available)

## Step-by-step method

### Gate 0 test (Boss's step, ~15 min, $0)
1. Go to lemonsqueezy.com.
2. **Sign up as an individual** (not MAINUDDIN LLC — the LLC is
   US-registered with no US bank, so individual is the right path).
3. Look at the payout method — check whether BD bank payout is available.
4. Report the result: pass / fail / what it said (a screenshot helps).

### Depending on the result
- **Pass:** start the rest of Phase 2 — complete the PA list to 100, Gate 1
  (check the cadence against AAHA/PetDesk), build the kit's 6 parts, store listing,
  launch.
- **Fail (triage/blocked):** test the backup rail — **Polar** (BD is on the seller/payout
  list, Stripe Connect Express). If Polar also fails, **Gumroad**
  (BD bank payout exists, must register as an individual).
- **All rails closed:** product track fully **KILL**ed — the kit will not be built,
  Boss will be told. A product cannot be built with no way to receive money.

### Recording the result
- When Boss reports the result (in the 3D office dashboard's Gate 0 room or in chat), Elora
  will update the top **Status line** of `gate0-status.md`. The Chief's code
  does not treat Gate 0 as passed on its own — only the Status line is the source.
- **New risk:** Lemon Squeezy's new signup flow triages — saying "tell us
  about your business" it may send you toward Stripe Managed Payments,
  where Bangladesh is excluded (37 countries only). So test first, then build.

## Output format

- Gate 0 test steps (for Boss, 4 steps) + a record of the result: date, rail,
  result (PASSED / FAILED + reason), next rail (if any).
- The Status line's real state — never a guess.

## Gate

- This role has no gate — it is only checking + recording.
- But signing up is Boss's own step — Elora never logs in/signs up with
  Boss's password.

## Honest limits

- **Gate 0 NOT PASSED** — the test has not happened. No store has been opened on any rail yet.
- Lemon Squeezy is in maintenance mode, possible sunset, no date — so the
  customer list + files must stay exportable.
- Polar's BD individual-vs-business eligibility is **UNKNOWN** — it must be checked before
  committing.
- **Etsy is never in the plan** — closed for Bangladesh, hard no.
- **BOSS INPUT REQUIRED:** the Gate 0 test result — Boss will sign up himself
  and report it. Without this result, this role has nothing more to do.
