# Skill: Payment-Rails Checker

**Role:** Gate 0 test-এর ধাপ লেখা + Boss-এর ফলাফল রেকর্ড করা — নিজে কখনো
signup করে না।
**Status: Gate 0 NOT PASSED** — Boss-এর Lemon Squeezy test বাকি।

## Rails (research report §2 — verified live 2026-11-12)

| Platform | BD founder-এর জন্য? | Fee per sale | Payout | Verdict |
|---|---|---|---|---|
| **Lemon Squeezy** | YES — BD official bank-payout list-এ আছে [VERIFIED] | 5% + $0.50 (+1.5% int'l buyer) | $50 min; created 1st/15th, 13-day hold, paid 14th/28th; 1% payout fee to non-US bank | **Primary rail।** Sunset risk, no date; test signup first। |
| **Polar** | YES — BD seller/payout list-এ আছে via Stripe Connect Express [STRONG INDICATION] | 5% + $0.50 (+1.5% non-US card); payout $2/mo + 0.25% + 25¢ | 7-day settlement for new orgs; account review up to 14 days | **Best backup।** BD individual-vs-business eligibility: UNKNOWN — check before committing। |
| **Gumroad** | YES — bank payouts in BDT to a BD bank [VERIFIED] | 10% + $0.50 plus 2.9% + $0.30 card processing (≈12.9% + $0.80 effective); 30% via Discover | $100 min; weekly (BD payout day Tuesday); 7-day hold | Fallback। **LLC catch: register as an INDIVIDUAL in Bangladesh, not as MAINUDDIN LLC** — bank account যে country-তে business registered সেই country-তেই থাকতে হবে, আর LLC US-registered, US bank নেই। |
| **Paddle** | YES, conditional — BD unsupported-countries list-এ নেই [VERIFIED] | 5% + $0.50, all-inclusive | $100 min; monthly, by the 15th; wire or Payoneer (Payoneer Boss-এর LOCKED — wire ব্যবহার; $15 SWIFT fee for BD: UNKNOWN) | Viable but gated by approval review; approval can be refused without reason। |
| **Etsy** | **NO** — BD eligible-countries list-এ নেই [VERIFIED] | — | — | **Hard no। Do not build on Etsy।** |

Worked example, $49 sale (US card): Lemon Squeezy keeps $46.05; Paddle
$46.05; Polar ~$46.05; Gumroad ~$41.88। Cash timing (Lemon Squeezy):
sale → bank ≈ 3–5 weeks (13-day hold + payout cycle + 1–5 days transfer)।

## Inputs

- `02-Digital-Product-Department/gate0-status.md` — Gate 0-র একমাত্র সত্য
  উৎস ("Status: PASSED" লেখা না থাকলে NOT PASSED)
- Research report §2 + `notes/payment-rails-verification-20261112.md`
- Boss-এর ফলাফল (pass / fail / কী বলল, screenshot থাকলে ভালো)

## Step-by-step method

### Gate 0 test (Boss-এর step, ~15 min, $0)
1. lemonsqueezy.com-এ যান।
2. **Individual হিসেবে signup করুন** (MAINUDDIN LLC নয় — LLC
   US-registered, US bank নেই বলে individual-ই সঠিক পথ)।
3. Payout method দেখুন — BD bank payout দেখা যায় কি না।
4. ফলাফল জানান: পাস / ফেল / কী বলল (screenshot দিলে ভালো হয়)।

### ফলাফল অনুযায়ী
- **পাস:** Phase 2-র বাকি কাজ শুরু — PA list 100-এ পূর্ণ করা, Gate 1
  (cadence AAHA/PetDesk যাচাই), kit-এর ৬ অংশ বানানো, store listing,
  launch।
- **ফেল (triage/blocked):** Backup rail test — **Polar** (BD seller/payout
  list-এ আছে, Stripe Connect Express)। Polar-ও না হলে **Gumroad**
  (BD bank payout আছে, individual হিসেবে register করতে হবে)।
- **সব rail বন্ধ:** Product track পুরো **KILL** — kit বানানো হবে না,
  Boss-কে জানানো হবে। টাকা পাওয়ার উপায় ছাড়া product বানানো যাবে না।

### ফলাফল রেকর্ড করা
- Boss ফলাফল জানালে (3D office dashboard-এর Gate 0 ঘরে বা chat-এ) Elora
  `gate0-status.md`-এর উপরের **Status লাইন** আপডেট করবে। Chief-এর কোড
  নিজে থেকে Gate 0 পাস বলে ধরে না — শুধু Status লাইনটাই উৎস।
- **নতুন risk:** Lemon Squeezy-র নতুন signup flow triage করে — "tell us
  about your business" বলে Stripe Managed Payments-এর দিকে পাঠাতে পারে,
  যেখানে Bangladesh বাদ (37 country only)। তাই আগে test, তারপর build।

## Output format

- Gate 0 test steps (Boss-এর জন্য, ৪ ধাপ) + ফলাফলের রেকর্ড: তারিখ, rail,
  ফলাফল (PASSED / FAILED + কারণ), পরের rail (যদি থাকে)।
- Status লাইনের আসল অবস্থা — কখনো অনুমান নয়।

## Gate

- এই role-এ কোনো gate নেই — এটা শুধু যাচাই + রেকর্ড।
- কিন্তু signup করা Boss-এর নিজের step — Elora/Boss-এর পাসওয়ার্ড দিয়ে
  কখনো login/signup করে না।

## Honest limits

- **Gate 0 NOT PASSED** — test হয়নি। কোনো rail-এ এখনো store খোলা হয়নি।
- Lemon Squeezy maintenance mode-এ আছে, possible sunset, no date — তাই
  customer list + file exportable রাখতে হবে।
- Polar-এর BD individual-vs-business eligibility **UNKNOWN** — commit
  করার আগে check করতে হবে।
- **Etsy কখনো plan-এ নেই** — Bangladesh-এর জন্য বন্ধ, hard no।
- **BOSS INPUT REQUIRED:** Gate 0 test-এর ফলাফল — Boss নিজে signup করে
  জানাবেন। এই ফলাফল ছাড়া এই role-এর আর কিছু করার নেই।
