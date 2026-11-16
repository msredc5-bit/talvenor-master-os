# Launch Section — Launch Checklist DRAFT

**Purpose (উদ্দেশ্য):** Vet Kit launch-এর checklist DRAFT বানানো — launch নিজে করা নয়।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Launch Manager | `agents/launch_manager.py` (`LaunchManagerAgent`, task `launch_prep`) | `skills/launch-manager.md` | `go` | Existing role — section agent হিসেবে নতুন file |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief → `launch_prep` (existing ROUTING branch)।
2. Section agent `LaunchManagerAgent` checklist DRAFT দেয়: Gate 0 → kit-এর ৬ অংশ → Gate 1 যাচাই → Lemon Squeezy listing + Gumroad backup → sales page (Boss review) → 100 clinic-কে ২৫টা করে মেইল (৪ দিন) → reply + sale sheet-এ লেখা।
3. Gate 0 NOT PASSED হলে status `blocked-gate0` — launch হিসেবে কিছু চিহ্নিত হয় না।
4. `mark_launched` / `mark_sold` চাইলে Chief + agent দুজনেই `blocked-gate0` ফেরত দেয়।

## Gates (গেট)

- Launch এগোতে Boss-এর `go` লাগে।
- Gate 0 পাস না হওয়া পর্যন্ত launch করা যাবে না।

## Honest limits (সৎ সীমা)

- **Gate 0 NOT PASSED** — launch হয়নি।
- **Kit 0/6 built, PA list 39/100, sale 0**, email **PAUSED** (2026-11-14 থেকে)।
- কোনো agent file লেখে না, মেইল পাঠায় না, network ছোঁয় না, sale লেখে না।
