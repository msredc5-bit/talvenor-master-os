# Product Section — Vet Kit বানানো + QA

**Purpose (উদ্দেশ্য):** Vet No-Show Recovery Kit-এর blueprint থেকে build order দেওয়া আর ৬ অংশের QA checklist DRAFT লেখা — kit নিজে বানানো নয় (Gate 0 পাসের আগে বানানো যাবে না)।

## Staff roster (কর্মী তালিকা)

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Kit Builder | `agents/kit_builder.py` (`KitBuilderAgent`, task `kit_build`) | `skills/kit-builder.md` | `ok` | Existing role — section agent হিসেবে নতুন file |
| Kit QA | `agents/kit_qa.py` (`KitQAAgent`, task `kit_qa`) | `skills/kit-qa.md` | `ok` | **NEW** role (Phase 7) |

## How work flows (কাজের ধারা)

1. Main CEO Bot → Products Chief (`chief_of_staff_products.py`) → task type দেখে routing।
2. `kit_build` — Chief-এর existing ROUTING branch (blueprint ফেরত দেয়); section agent `KitBuilderAgent` একই blueprint সারাংশ + build order দেয়, Gate 0 NOT PASSED হলে status `blocked-gate0`।
3. `kit_qa` — Chief-এর `SECTION_ROUTING` branch (Phase 7, নতুন) → `KitQAAgent` → "NOT BUILT — nothing to QA yet" + per-part QA checklist DRAFT।
4. Gated কাজ (`send` / `publish` / `spend` / `delete`) হলে agent চালানো হয় না — ApprovalGateway-এ PENDING request লেখা হয়।

## Gates (গেট)

- Build শুরু করতে / output ব্যবহার করতে Boss-এর `ok` লাগে।
- Gate 0 পাস না হওয়া পর্যন্ত kit-এর কোনো অংশ বানানো যাবে না।

## Honest limits (সৎ সীমা)

- **Gate 0 NOT PASSED** — Lemon Squeezy signup test Boss-এর step, এখনো বাকি।
- **Kit 0/6 built** — শুধু blueprint (`kit-outline.md`) আছে; QA করার মতো কিছু নেই।
- **PA list 39/100, sale 0**, email **PAUSED** (2026-11-14 থেকে)।
- কোনো agent file লেখে না, network ছোঁয় না, sale/launch চিহ্নিত করে না।
