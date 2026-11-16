# Finance Section — Gate 0 Payment Rails

**Purpose (উদ্দেশ্য):** Gate 0 test-এর ধাপগুলো লেখা আর Boss-এর ফলাফল record করা — Lemon Squeezy signup (BD individual), ফেল হলে Polar → Gumroad (individual, LLC নয়)।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Payment-Rails Checker | `agents/payment_rails_checker.py` (`PaymentRailsCheckerAgent`, task `gate0_check`) | `skills/payment-rails-checker.md` | — (none) | Existing role — section agent হিসেবে নতুন file |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief → `gate0_check` (existing ROUTING branch)।
2. Section agent `PaymentRailsCheckerAgent` test steps লেখে (৬ ধাপ) + rail fees (Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% + $0.80, $100 min payout) + gate0-status.md থেকে পড়া current Status।
3. Boss-এর ফলাফল শুধু Boss জানালে record হয় — verbatim quote হিসেবে, এই agent-এর verdict নয়। Agent নিজে "PASSED" লেখে না, gate0-status.md-এর Status লাইন বদলায় না — কোনো file-ই লেখে না।
4. সব rail বন্ধ হলে product track পুরো KILL — Boss-কে জানানো হবে।

## Gates (গেট)

- কোনো gate নেই — এটা শুধু যাচাই + রেকর্ড।
- Signup Boss-এর নিজের step (~15 min, $0) — agent কখনো নিজে signup করে না।

## Honest limits (সৎ সীমা)

- **Gate 0 NOT PASSED** — test হয়নি; Boss-এর ফলাফল ছাড়া কোনো verdict নেই।
- **Kit 0/6 built, PA list 39/100, sale 0**।
- Etsy hard no — Bangladesh-এর জন্য বন্ধ, কখনো plan-এ নেই।
- কোনো agent signup করে না, file লেখে না, network ছোঁয় না, নিজে থেকে PASSED/FAILED লেখে না।
