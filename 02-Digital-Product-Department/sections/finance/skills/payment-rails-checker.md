# Skill: Payment-Rails Checker

**Role (ভূমিকা):** Gate 0 test-এর ধাপগুলো লেখা আর Boss-এর ফলাফল record করা — Lemon Squeezy signup (individual, BD bank payout দেখা যায় কি না), ফেল হলে fallback order: **Polar** → **Gumroad** (individual হিসেবে, LLC নয়)।
**Agent:** `sections/finance/agents/payment_rails_checker.py` — `PaymentRailsCheckerAgent` (task kind `gate0_check`, section `finance`)
**Status: এই role-ই Gate 0 দেখে** — কিন্তু নিজে কখনো signup করে না, নিজে কখনো "PASSED" লেখে না।

## Product (locked facts)

- **Gate 0 কী:** Vet Kit বানানোর আগে প্রথমে যাচাই — Lemon Squeezy-তে Bangladesh থেকে individual হিসেবে signup + payout হয় কি না। নতুন signup-দের triage করা হয় — Stripe Managed Payments-এর দিকে পাঠাতে পারে, যেখানে Bangladesh বাদ। তাই আগে test, তারপর build।
- **Rail fees (research report §2, 2026-11-12):** Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80 effective, $100 min payout।
- **Kit price:** $49 one-time (প্রথম ৩০ buyer-এর জন্য launch $39)।

## Inputs

- `02-Digital-Product-Department/gate0-status.md` (একমাত্র সত্য উৎস — "Status: PASSED" লেখা না থাকলে NOT PASSED)।
- Task payload-এ `boss_result` (optional) — Boss-এর জানানো ফলাফল, শুধু Boss জানালে record হয়।
- Research report §2 (rails verification 2026-11-12)।

## Step-by-step method (Gate 0 test — Boss-এর step, ~15 min, $0)

1. **lemonsqueezy.com-এ যান।**
2. **Individual হিসেবে signup করুন** (MAINUDDIN LLC নয় — LLC US-registered, US bank নেই বলে individual-ই সঠিক পথ)।
3. **Payout method দেখুন** — BD bank payout দেখা যায় কি না।
4. **ফলাফল জানান:** পাস / ফেল / কী বলল (screenshot দিলে ভালো হয়)।
5. **ফেল (triage/blocked) হলে backup rail test — Polar** (BD seller/payout list-এ আছে, Stripe Connect Express)।
6. **Polar-ও না হলে Gumroad** (BD bank payout আছে, individual হিসেবে register করতে হবে)।
7. **সব rail বন্ধ হলে product track পুরো KILL** — kit বানানো হবে না, Boss-কে জানানো হবে। টাকা পাওয়ার উপায় ছাড়া product বানানো যাবে না।

## Output format

- Gate 0 test steps (৬ ধাপ) + rail fees + gate0-status.md থেকে পড়া current Status।
- Boss-এর ফলাফল থাকলে: verbatim quote হিসেবে record — "Boss-এর জানানো ফলাফল (record only — এই agent-এর verdict নয়)" + note যে এই agent নিজে PASSED লেখে না, gate0-status.md-এর Status লাইন বদলানো Boss-এর কথায় manual step।
- Boss-এর ফলাফল না থাকলে: "Boss-এর ফলাফল এখনো আসেনি — Boss test করে জানালে তবেই record হবে।"

## Tools used (টুল)

- Read-only file read: `gate0-status.md` (Status লাইন)।
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — test steps DRAFT লেখায়, live call নয়।
- Gated কাজে ApprovalGateway (PENDING record) — এই skill-এ gate নেই, শুধু যাচাই + record।
- কোনো live tool, network, signup, বা file write নয়।

## Gate

- কোনো gate নেই — এটা শুধু যাচাই + রেকর্ড।
- Signup Boss-এর নিজের step — agent কখনো নিজে signup করে না।

## Honest limits

- **Gate 0 NOT PASSED** — test হয়নি। Boss-এর ফলাফল ছাড়া কোনো verdict নেই।
- সব rail বন্ধ হলে product track KILL — এটা kill criteria, আগেই লেখা।
- Etsy Bangladesh-এর জন্য বন্ধ — কখনো plan-এ নেই (hard no)।

## যা কখনো করে না

- নিজে Lemon Squeezy / Polar / Gumroad-এ signup করে না।
- নিজে থেকে Gate 0 "PASSED" লেখে না — Boss-এর ফলাফল ছাড়া।
- Etsy plan-এ আনে না; কোনো file লেখে না।

## Worked example (আসল repo fact দিয়ে)

- **Task:** `{"type": "gate0_check", "title": "Gate 0 test steps"}` → `PaymentRailsCheckerAgent.run()`।
- **Agent করে:** `gate0-status.md` পড়ে — Status NOT PASSED (2026-11-16); ৬ ধাপের test steps + rail fees (Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80, $100 min payout) লেখে।
- **ফলাফল:** status `draft-ready`; output-এ "Boss-এর ফলাফল এখনো আসেনি" — কোনো verdict নেই। উদাহরণ input হিসেবে Boss যদি জানাতেন "Lemon Squeezy signup done, BD bank payout visible" (এটা উদাহরণ input, আসল ফলাফল নয়), agent তা verbatim quote হিসেবে record করত — নিজে "PASSED" লিখত না।
