# Digital Product Engine — STAFF.md (কর্মী তালিকা)

**Department:** 02-Digital-Product-Department — Vet No-Show Recovery Kit ($49 one-time)
**Chief:** Products Chief of Staff (`chief_of_staff_products.py` — REAL, Phase 2)
**Status (2026-11-16):** Gate 0 **NOT PASSED** — Lemon Squeezy signup test Boss-এর step, এখনো বাকি।
Kit-এর ৬ অংশ বানানো হয়নি, sale **0**, launch হয়নি। PA list **39/100**।

এই engine-এ ঠিক **৫ জন** staff। কেউ মেইল পাঠায় না, publish করে না, খরচ করে
না, delete করে না। Gated কাজ (send / publish / spend / delete) হলে Boss-এর
exact gate word (ok / "post it" / "upload it" / send / go) ছাড়া কিছু চলে না।

---

## 1. Kit Builder

**কী করে:** kit-outline.md-এর blueprint থেকে kit-এর ৬ অংশ বানায় — (1) Reminder
Cadence Pack (T-72h / T-24h / T-2h SMS + email + call script), (2) Same-Day
Rebooking Scripts, (3) Waitlist-Fill SOP (এক পাতা), (4) No-Show Log + $ Tracker
(Sheets, formula সহ), (5) Deposit / No-Show Policy Template (attorney-review
note সহ), (6) Front-Desk Quick Card (৫ লাইন, এক পাতা)। সব plain US English,
Google Sheets + Docs, $0।

**Inputs:** `kit-outline.md` (blueprint — একমাত্র উৎস), research report
`~/workspace/research_notes/digital-product-final-20261112/report.md` §4.1,
Gate 1 যাচাই (cadence AAHA/PetDesk guidance-এর সাথে মেলে কি না)।

**Outputs:** ৬ অংশের DRAFT (Sheets/Docs) — Gate 0 পাসের পরে। এখন শুধু blueprint
ফেরত দেয়, kit নিজে নয়।

**Gate:** build শুরু করতে Boss-এর `ok` লাগে; output ব্যবহার করতে `ok`।

**Gate 0 status:** **BLOCKED** — Gate 0 পাস না হওয়া পর্যন্ত kit-এর কোনো অংশ
বানানো যাবে না। Chief-এর `kit_build` শুধু blueprint ফেরত দেয়।

## 2. Clinic Researcher

**কী করে:** PA vet list-কে ১০০টি যাচাই করা independent clinic-এর দিকে বাড়ায়।
প্রতিটা নতুন clinic-এর নিজের official website (সবচেয়ে ভালো) অথবা directory
listing থেকে নাম + শহর + website + public email/phone যাচাই করে
`pa-vet-clinics.csv`-এ যোগ করে।

**Inputs:** `pa-vet-list/pa-vet-clinics.csv` (এখন 39 row), `pa-vet-list/README.md`
(যাচাইয়ের নিয়ম), Google Maps / directory listing (public তথ্য শুধু)।

**Outputs:** যাচাই করা নতুন row (CSV) + শহর ভাগ সারাংশ। কোনো clinic-কে মেইল/
ফোন করা হয় না — এটা শুধু list, outreach নয়।

**Gate:** কোনো gate নেই — list বানানো নিরাপদ কাজ। কিন্তু list থেকে কাউকে মেইল
করতে `send` gate লাগে, আর email channel এখন PAUSED (2026-11-14 থেকে)।

**Gate 0 status:** **NOT BLOCKED** — list বাড়ানো Gate 0-র বাইরে করা যায়, তবে
plan অনুযায়ী বাকি 61 clinic Gate 0-র পরে পূর্ণ করা হবে।

**যা কখনো করে না:** contact details বানায় না — public-এ না থাকলে "Not publicly
listed" লেখে। Chain বাদ দেয়: Banfield, VCA, Vetco/Petco, BluePearl, Thrive,
PetVet365, PetVet Care Centers network। Corporate chain ও solo mobile vet নয় —
target independent companion-animal clinic, ১–৫ vet।

## 3. Launch Manager

**কী করে:** launch-এর checklist বানায় (DRAFT only) — Gate 0, kit-এর ৬ অংশ,
Gate 1 যাচাই, Lemon Squeezy listing + Gumroad backup listing, sales page
(Boss review), 100 clinic-কে দিনে ২৫টা করে মেইল (৪ দিন), reply + sale sheet-এ
লেখা।

**Inputs:** `kit-outline.md` (Week 0–4 build plan + Gate 0–3 kill criteria),
`gate0-status.md`, PA list-এর অবস্থা (39/100), Chief-এর `launch_prep` output।

**Outputs:** Launch checklist DRAFT — launch নিজে নয়।

**Gate:** launch এগোতে Boss-এর `go` লাগে।

**Gate 0 status:** **BLOCKED** — launch করা যাবে না। Chief-এর `launch_prep`
শুধু DRAFT checklist দেয়; `mark_launched` চাইলে status `blocked-gate0` ফেরত
আসে, কিছুই launch হিসেবে লেখা হয় না।

## 4. Payment-Rails Checker

**কী করে:** Gate 0 test-এর ধাপগুলো লেখে আর Boss-এর ফলাফল রেকর্ড করে —
Lemon Squeezy signup (individual, BD bank payout দেখা যায় কি না), ফেল হলে
fallback order: **Polar** → **Gumroad** (individual হিসেবে, LLC নয়)। সব rail
বন্ধ হলে product track KILL — Boss-কে জানানো।

**Inputs:** `gate0-status.md` (একমাত্র সত্য উৎস — "Status: PASSED" লেখা না
থাকলে NOT PASSED), research report §2 (rails verification 2026-11-12):
Lemon Squeezy 5% + $0.50, $50 min payout; Polar 5% + $0.50; Gumroad ~12.9% +
$0.80 effective, $100 min payout।

**Outputs:** Gate 0 test steps + Boss-এর ফলাফলের রেকর্ড (gate0-status.md-এ
Status লাইন আপডেটের জন্য Boss-কে জানানো — Elora নিজে Status PASSED লেখে না
Boss-এর ফলাফল ছাড়া)।

**Gate:** কোনো gate নেই — এটা শুধু যাচাই + রেকর্ড।

**Gate 0 status:** **এই role-ই Gate 0 দেখে** — কিন্তু নিজে কখনো signup করে
না। Signup Boss-এর নিজের ~15-min step (lemonsqueezy.com, individual হিসেবে)।

**যা কখনো করে না:** নিজে Lemon Squeezy/Polar/Gumroad-এ signup করে না, Etsy
কখনো plan-এ আনে না (Bangladesh-এর জন্য বন্ধ — hard no)।

## 5. Support Drafter

**কী করে:** kit buyer-দের প্রশ্নের reply-এর DRAFT লেখে — delivery, file
খোলা, tracker formula, refund policy, "not legal advice" note — plain US
English, DRAFT only।

**Inputs:** buyer-এর আসল message (Boss forward করবেন), kit-এর ৬ অংশের
বিবরণ (kit-outline.md), research report §7.3 (support load ~10 min/buyer —
ASSUMPTION), refund policy (sales page-এ যা লেখা থাকবে — এখনো ঠিক হয়নি)।

**Outputs:** Reply DRAFT — পাঠানো নয়। Boss দেখে `send` বললে তবেই পাঠানো হয়।

**Gate:** পাঠাতে Boss-এর `send` লাগে।

**Gate 0 status:** **BLOCKED (কাজ নেই এখন)** — sale 0, তাই কোনো buyer নেই,
কোনো support প্রশ্নও নেই। Gate 0 পাস + প্রথম sale-এর পরেই এই role-এর কাজ
শুরু হবে।

**যা কখনো করে না:** locked $49 kit price-এর বাইরে কোনো price quote করে না;
prospect-কে $49-ও quote করে না Boss confirm না করলে। কোনো client/
testimonial/statistic বানায় না। Policy template-কে legal advice হিসেবে দেয়
না — সবসময় "have your own attorney review before using" লেখে।

---

## সত্য অবস্থা (2026-11-16)

| জিনিস | অবস্থা |
|---|---|
| Staff | 5 জন (এই ফাইল) |
| Gate 0 | NOT PASSED — Boss-এর Lemon Squeezy test বাকি |
| Kit-এর ৬ অংশ | কোনোটা বানানো হয়নি |
| PA list | 39 / 100 |
| Sale | 0 |
| Wedge (১/২০ buyer → $1,109/mo receptionist) | UNTESTED — অনুমান, fact নয় |

**Source ফাইল (কিছু copy/move করা হয়নি):** `chief_of_staff_products.py`,
`kit-outline.md`, `gate0-status.md`, `pa-vet-list/README.md` +
`pa-vet-clinics.csv`, `skills/chief-products.md`, `00-CEO-Core/config.json`,
`~/workspace/research_notes/digital-product-final-20261112/report.md`।

---

## Phase 7 — Section map (2026-11-17)

Phase 7-এ 5 staff-এর কাজ ৬টা section-এ সাজানো হয়েছে
(`02-Digital-Product-Department/sections/<section>/` — প্রতিটায়
`agents/` + `skills/` + `SECTION.md`)। নতুন staff **২ জন** (Kit QA,
Kit Sales) — মোট staff এখন **৭ জন**। Section agent-রা কোনো file লেখে
না, network ছোঁয় না, মেইল পাঠায় না, sale/launch চিহ্নিত করে না।

| Section | Staff | Agent file | Skill file | Gate | NEW / existing |
|---|---|---|---|---|---|
| product | Kit Builder | `sections/product/agents/kit_builder.py` | `sections/product/skills/kit-builder.md` | `ok` | existing role |
| product | Kit QA | `sections/product/agents/kit_qa.py` | `sections/product/skills/kit-qa.md` | `ok` | **NEW** |
| research | Clinic Researcher | `sections/research/agents/clinic_researcher.py` | `sections/research/skills/clinic-researcher.md` | — | existing role |
| launch | Launch Manager | `sections/launch/agents/launch_manager.py` | `sections/launch/skills/launch-manager.md` | `go` | existing role |
| sales | Kit Sales | `sections/sales/agents/kit_sales.py` | `sections/sales/skills/kit-sales.md` | `send` | **NEW** |
| support | Support Drafter | `sections/support/agents/support_drafter.py` | `sections/support/skills/support-drafter.md` | `send` | existing role |
| finance | Payment-Rails Checker | `sections/finance/agents/payment_rails_checker.py` | `sections/finance/skills/payment-rails-checker.md` | — | existing role |

Chief routing (Phase 7): আগের ৪ task type (`kit_build`,
`clinic_research`, `gate0_check`, `launch_prep`) আগের মতোই `ROUTING`-এ
চলে — কিছু বদলায়নি। ৩ নতুন type (`kit_sales`, `kit_qa`,
`support_draft`) Chief-এর `SECTION_ROUTING`-এ চলে — section agent
`importlib.util.spec_from_file_location` দিয়ে load করে, mock brain
(`BrainFactory.get_brain("agency")`) দিয়ে `run()` চালায়, `tasks.json`-এ
আগের মতো log করে।

**সত্য অবস্থা Phase 7-এর পরেও একই:** Gate 0 **NOT PASSED**, kit **0/6**
built, PA list **39/100**, sale **0**, email **PAUSED**। Section map
কোনো সত্য বদলায় না — শুধু কাজের সাজানো।

