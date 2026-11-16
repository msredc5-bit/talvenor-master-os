# Support Section — Buyer-Reply DRAFTs (Templates)

**Purpose (উদ্দেশ্য):** kit buyer-দের প্রশ্নের reply-এর DRAFT লেখা — delivery, tracker formula, script ব্যবহার, refund, policy template — plain US English, DRAFT only।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Support Drafter | `agents/support_drafter.py` (`SupportDrafterAgent`, task `support_draft`) | `skills/support-drafter.md` | `send` | Existing role — section agent হিসেবে নতুন file |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief → `support_draft` (Chief-এর `SECTION_ROUTING` branch, Phase 7, নতুন) → `SupportDrafterAgent`।
2. Buyer-এর আসল message (Boss forward করবেন) থাকলে তার reply DRAFT; না থাকলে topic-এর template (`delivery` | `tracker` | `script` | `refund` | `policy` | `general`) — kit-outline.md-এর ৬ অংশ থেকে।
3. Policy প্রশ্নে সবসময়: "have your own attorney review before using" — template legal advice নয়।
4. Refund প্রশ্নে কোনো refund promise নেই — refund policy এখনো ঠিক হয়নি (BOSS INPUT REQUIRED)।
5. প্রতিটা output-এ সৎ note: "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale."

## Gates (গেট)

- পাঠাতে Boss-এর `send` লাগে। DRAFT নিজেই নিরাপদ, কোনো gate নেই।

## Honest limits (সৎ সীমা)

- **Sale 0 — কোনো buyer নেই।** এই section-এর আসল test এখনো হয়নি; Gate 0 পাস + প্রথম sale-এর পরেই আসল buyer-reply কাজ শুরু হবে।
- **Gate 0 NOT PASSED, kit 0/6 built**, email **PAUSED** (2026-11-14 থেকে)।
- Refund policy এখনো ঠিক হয়নি — Boss-এর decision ছাড়া refund নিয়ে কিছু লেখা যাবে না।
- কোনো agent মেইল পাঠায় না, legal advice দেয় না, invented buyer-এর message আসল হিসেবে চালায় না, file লেখে না, network ছোঁয় না।
