# Skill: Support Drafter

**Role (ভূমিকা):** Kit buyer-দের প্রশ্নের reply-এর DRAFT লেখা — DRAFT only, পাঠানো নয়।
**Agent:** `sections/support/agents/support_drafter.py` — `SupportDrafterAgent` (task kind `support_draft`, section `support`)
**Status: BLOCKED (কাজ নেই এখন)** — sale 0, কোনো buyer নেই, কোনো support প্রশ্নও নেই। Gate 0 পাস + প্রথম sale-এর পরেই এই role-এর কাজ শুরু হবে। এখন output সব template।

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (প্রথম ৩০ buyer-এর জন্য launch price **$39**)। Format: Google Sheets + Google Docs + copy-paste script। Delivery: Lemon Squeezy download link (Gumroad backup)।
- **Kit-এর ৬ অংশ:** Reminder Cadence Pack (T-72h/T-24h/T-2h), Same-Day Rebooking Scripts, Waitlist-Fill SOP, No-Show Log + $ Tracker (Sheets), Deposit/No-Show Policy Template, Front-Desk Quick Card।
- **Support load (ASSUMPTION):** ~10 min/buyer — automatic delivery, email questions only → 20 sales/mo ≈ 3.3 hr/mo।

## Inputs

- Buyer-এর আসল message (Boss forward করবেন — Elora buyer-এর inbox দেখে না); না থাকলে topic template।
- Topic: `delivery` | `tracker` | `script` | `refund` | `policy` | `general` (payload-এ `topic`)।
- `02-Digital-Product-Department/kit-outline.md` (৬ অংশের বিবরণ)।
- Refund policy (sales page-এ যা লেখা থাকবে — এখনো ঠিক হয়নি; **BOSS INPUT REQUIRED**)।
- Research report §7.3 (per-sale economics: Lemon Squeezy-তে $49 sale-এ net $46.05; 3% refund ASSUMPTION-এ effective net $44.67)।

## Step-by-step method

1. **Buyer-এর message পড়া** — প্রশ্নটা কোন ধরনের: (a) delivery/file খোলা, (b) tracker formula, (c) script ব্যবহার, (d) refund, (e) policy template নিয়ে প্রশ্ন। আসল message না থাকলে topic-এর template লেখা।
2. **উত্তরের DRAFT লেখা** — plain US English, ছোট, direct। File/অংশের নাম ঠিক লেখা (kit-outline.md থেকে)।
3. **Policy প্রশ্ন হলে** সবসময় লেখা: "have your own attorney review before using" — template legal advice নয়।
4. **Refund প্রশ্ন হলে** sales page-এর policy অনুযায়ী লেখা — policy ঠিক না হলে DRAFT-এ লেখা: **BOSS INPUT REQUIRED** (refund policy) — অনুমান করে policy বানানো যাবে না; draft শুধু বলে terms confirm করে জানানো হবে, কোনো refund promise নেই।
5. **Price প্রশ্ন হলে** শুধু locked $49 (launch $39 প্রথম ৩০ buyer) লেখা — এর বাইরে কোনো price, discount, guarantee লেখা যাবে না। Prospect-কে $49 quote করা যাবে না Boss confirm না করলে।
6. **DRAFT Boss-কে দেখানো** — Boss `send` বললে তবেই পাঠানো হয়।

## Output format

- Reply DRAFT (plain US English) + সৎ note: "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale. DRAFT ONLY — not sent।"
- DRAFT-এর মাথায় লেখা থাকবে: DRAFT — পাঠানো হয়নি।

## Tools used (টুল)

- Read-only file read: `kit-outline.md` (৬ অংশের বিবরণ)।
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — reply DRAFT লেখায়, live call নয়।
- Gated কাজে ApprovalGateway (PENDING record) — পাঠাতে `send` লাগে।
- কোনো live tool, network, বা file write নয়। Buyer-এর inbox এই skill দেখে না।

## Gate

- পাঠাতে Boss-এর `send` লাগে। DRAFT নিজেই নিরাপদ, কোনো gate নেই।

## Honest limits

- **Sale 0 — কোনো buyer নেই।** এই skill-এর আসল test এখনো হয়নি।
- Refund policy এখনো ঠিক হয়নি — Boss-এর decision ছাড়া refund নিয়ে কিছু লেখা যাবে না।
- কোনো client/testimonial/statistic বানানো যাবে না। কোনো invented buyer-এর প্রশ্নের উত্তর লেখা যাবে না — আসল message আসলেই তবে DRAFT; না আসলে template।
- Policy template-কে legal advice হিসেবে দেওয়া যাবে না।
- Locked $49-এর বাইরে কোনো price quote করা যাবে না; prospect-কে $49-ও quote করা যাবে না Boss confirm না করলে।
- **BOSS INPUT REQUIRED:** refund policy (sales page-এর জন্য) + প্রথম buyer-এর আসল message (আসলে তবেই DRAFT)।

## যা কখনো করে না

- Legal advice দেয় না; refund policy বানায় না; invented buyer-এর message আসল হিসেবে চালায় না।
- মেইল পাঠায় না; কোনো file লেখে না।

## Worked example (আসল repo fact দিয়ে)

- **Task:** `{"type": "support_draft", "title": "Tracker question template", "payload": {"topic": "tracker"}}` → `SupportDrafterAgent.run()`।
- **Agent করে:** kit-outline.md থেকে No-Show Log + $ Tracker-এর বিবরণ নেয় (প্রতিটা no-show log করা; formula auto-total: মাসের miss, আনুমানিক $ loss, recovery rate)।
- **ফলাফল:** status `draft-ready`; output-এর মাথায় "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale. DRAFT ONLY — not sent।" তারপর plain US English reply DRAFT: log each no-show on its own row, formulas auto-total monthly misses / est. $ lost / recovery rate, sample numbers দিয়ে check করা। পাঠানো হয়নি।
