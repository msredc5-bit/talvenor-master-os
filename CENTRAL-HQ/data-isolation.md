# Data Isolation Policy — Talvenor Unified OS

> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> ধরন: POLICY ONLY — এই ফাইল কোনো নতুন data বানায় না, কোনো data move করে না, কোনো ফাইল বদলায় না। শুধু নিয়ম লেখা।
> ভিত্তি: brief-এর architecture rule — "একটি কেন্দ্রীয় HQ থাকবে, কিন্তু কোনো Business Unit অন্য Business Unit-এর ব্যক্তিগত Client Data, Orders বা Financial Records-এ অনুমতি ছাড়া প্রবেশ করতে পারবে না।"

## 1. DATA এলাকা — 4টি

| DATA এলাকা | ফোল্ডার / ফাইল | মালিক (কে পড়ে/লেখে) | ভেতরে কী থাকে |
|---|---|---|---|
| DATA/central | `store/tasks.json`, `store/approvals.json`, `store/vault/`, `00-CEO-Core/config.json` | HQ only (Main CEO Bot + Boss) | Task record, approval record, shared vault, system config |
| DATA/agency | `01-Agency-Department/` | Agency Chief only | Lead, prospect research, outreach draft, client intake, delivery, finance record |
| DATA/commerce | `02-Digital-Product-Department/` | Products Chief only | PA vet list (`pa-vet-list/pa-vet-clinics.csv`), kit blueprint (`kit-outline.md`), gate0-status (`gate0-status.md`) |
| DATA/media | `03-Content-Creation-Department/` | Content Chief only | Pipeline (`pipeline.md`), VOICE.md, ToolPilot status (`toolpilot-status.md`), Creator OS worker output |

## 2. পড়ার নিয়ম

1. **একটি business শুধু নিজের department + shared vault পড়ে।** Agency পড়ে `01-Agency-Department/` + `store/vault/`। Commerce পড়ে `02-Digital-Product-Department/` + `store/vault/`। Media পড়ে `03-Content-Creation-Department/` + `store/vault/`।
2. **HQ (Main CEO Bot) সব পড়তে পারে** — কারণ routing, approval ও reporting HQ-র কাজ। কিন্তু HQ-ও কোনো gated action নিজে execute করে না।
3. **Boss সব পড়তে পারেন** — Founder, চূড়ান্ত সিদ্ধান্তকারী।

## 3. Isolation নিয়ম (কঠোর)

| নিয়ম | বিবরণ |
|---|---|
| Client record আলাদা | Agency-র lead/client record শুধু Agency-র। Commerce বা Media তা পড়তে পারে না। |
| Financial record আলাদা | প্রতিটি business-এর revenue, expense, invoice record শুধু তার নিজের। একত্রিত ছবি শুধু HQ-র Finance Intelligence-এ (আসল সংখ্যা দিয়ে, `shared-services.md` §7)। |
| Order / sale record আলাদা | Commerce-র order/sale record শুধু Commerce-র। |
| অন্য business-এর data পড়তে হলে | Boss-এর explicit permission লাগবে — মৌখিক ইঙ্গিত নয়, স্পষ্ট অনুমতি। অনুমতি ছাড়া কোনো cross-read নয়। |
| Cross-business read হলে | তা internal project হিসেবে log করতে হবে — কোন business, কী পড়ল, কেন, Boss-এর কোন অনুমতিতে। Log ছাড়া cross-read নয়। |
| Shared vault-এ কী যায় | শুধু যা তিনটি business-এর সবার কাজে লাগে (যেমন booking link, brand line, gate word-এর নিয়ম)। কোনো client-এর ব্যক্তিগত তথ্য vault-এ নয়। |
| Research notes | `~/workspace/research_notes/` shared, read-only source — সবাই পড়তে পারে, কেউ বদলাতে পারে না। |

## 4. Secret নিয়ম

- **কোনো secret (API key, password, token) prompt-এ বা repo-তে লেখা যাবে না।**
- Key শুধু connector Secure Vault দিয়ে — transient ব্যবহার, কোথাও save নয়।
- কোনো agent credential ধরে রাখে না — বিস্তারিত `01-Agency-Department/governance/security-policy.md`-তে।
- Secret leak হলে Boss-কে জানাতে হবে — চাপা দেওয়া যাবে না।

## 5. লঙ্ঘন হলে কী হবে

- অনুমতি ছাড়া cross-read ধরা পড়লে কাজ থামবে, Boss-কে জানানো হবে, Boss সিদ্ধান্ত নেবেন।
- এই policy বদলাতে হলে Boss-এর অনুমোদন লাগবে। কোনো agent নিজে policy বদলাতে পারবে না।

## 6. বর্তমান অবস্থা (সত্য)

- Policy: DRAFT (এই ফাইল) — Boss-এর review বাকি।
- Enforcement: কোনো automated enforcement বানানো হয়নি — GAP। এখন নিয়ম মানে মানুষ + Main CEO Bot-এর routing; code দিয়ে আটকানোর ব্যবস্থা নেই।
- Client data-র পরিমাণ: Agency-তে paying client 0 — আলাদা করার মতো client record এখনো নেই; নিয়ম আগেই লেখা হলো যাতে client এলে ভুল না হয়।
