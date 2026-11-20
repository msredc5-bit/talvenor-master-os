# Talvenor Master OS — আসল সিস্টেম (Phase 9 — COMPLETE: Taskboard + MCP + Live-Ready Tools)

**এটা কী:** Boss-এর ৩ ব্যবসার আসল operating system-এর folder। এটা
কোনো ছবি বা mock নয় — Phase 0-র skeleton + CEO Core + approval
gateway সত্যিই কাজ করে।

## ৩ ব্যবসা (শুধু এই ৩টাই — ১৩৬ নয়)

1. **Agency** — Talvenor AI Receptionist, US home-service ব্যবসার জন্য (MAIN)
2. **Digital Product** — Vet No-Show Recovery Kit, $49 one-time (Gate 0 বাকি)
3. **Content Creation Engine** — Creator OS / ToolPilot @ToolPilotai69

## Unified OS layer — Central HQ (2026-11-19)

একটাই HQ (00-CEO-Core: Main CEO Bot + Jarvis voice + Approval Gate + ONE mock
brain), তার নিচে ৩টা Business OS — আলাদা Chief, আলাদা department, আলাদা
data, কিন্তু CEO/Dashboard/Finance/Governance একটাই। নাম "TALVENOR UNIFIED OS"
শুধু architecture-layer-এর নাম (docs-এ) — repo-র নাম বদলায়নি, নতুন repo নয়।
- **CENTRAL-HQ/** — unified-os.md (master map + audit) + shared-services.md
  (১০ shared department → আসল জিনিস) + data-isolation.md (DATA policy:
  agency/commerce/media আলাদা, cross-read Boss-এর অনুমতি ছাড়া নয়) +
  cross-business.md (internal project নিয়ম) + BUSINESS-01-AGENCY.md +
  BUSINESS-02-COMMERCE.md + BUSINESS-03-MEDIA.md (wrapper docs, code নয়)
- **Commerce সত্য:** Amazon GATED (৫ client + $5K MRR না হওয়া পর্যন্ত), Etsy
  CLOSED (Bangladesh), Shopify PARKED (Boss-এর direct project), Dropshipping
  RESEARCH-ONLY, আসল digital product = Vet Kit $49 (Gate 0 NOT PASSED)
- **Dashboard:** status.html-এ নতুন "Unified OS — 3 Business OS" card
  (sync_status.py থেকে, সংখ্যা আসল ফাইল থেকে) — dashboard-3d.html ছোঁয়া হয়নি
- **বাকি:** Phase 3 specialists DONE 2026-11-19 (নিচে "Agentic Agency
  Office Phase 3" দেখুন); Commerce/Media OS-এর specialist build বাকি —
  Gate 0 / upload OFF / $0 cap যেমন আছে তেমনই

## Hierarchy (Boss-এর সংজ্ঞা, 2026-11-16)

1. **Conversation starts: Jarvis** — Boss Jarvis-এর সাথে কথা বলে।
2. **Jarvis যুক্ত থাকে super intelligent second brain-এর সাথে — Main CEO Bot।**
3. **Main CEO Bot সবকিছু maintain করে।** Second brain থেকে ৩টা system চলে:
   - Agency Office
   - Digital Product Business Office
   - Creator OS / Content Machine and Engine

Boss → Jarvis (voice) → Main CEO Bot (second brain) → ৩ Chief of Staff →
worker → ফলাফল ফিরে Main CEO Bot-এ → দরকার হলে Boss-এর অনুমোদন।

**Jarvis আর Main CEO Bot আলাদা** — Jarvis শুধু কথা শোনে/বলে (voice engine),
brain Main CEO Bot (second brain system)।

## Folder

```
talvenor-master-os/
├── 00-CEO-Core/            # brain + gate + config + shared tool-calling core
│   ├── main_ceo_bot.py         # REAL (router)
│   ├── human_approval_gateway.py  # REAL (approve/reject)
│   ├── brain.py                # REAL (Phase 6 + Phase 10 — BrainFactory: mock default / live via LiveBrainAdapter, loud mock fallback; live probe 2026-11-20 tunnel-403 BLOCKED, key unproven)
│   ├── tool_calling.py         # REAL (Phase 5 — ToolRegistry + dispatcher, 7 mock handler)
│   ├── tools.json              # REAL (7 tool-এর registry — booking_reply সহ)
│   ├── jarvis_voice.py         # REAL (2026-11-17 — Piper+Vosk/sherpa, offline, $0; একই 3 function)
│   ├── voice/                  # REAL (2026-11-17) — speak.py (Piper TTS), listen.py (Vosk en + sherpa-onnx bn), loop.py (শোনা → brain → বলা + gate); models/ + output/ git-এ যায় না
│   ├── VOICE-SETUP.md          # Windows setup guide (Bengali)
│   ├── config.json             # REAL (locked facts; brain: mock, phase 9, v0.9.0 + voice block)
│   └── CEO-README.md
├── 01-Agency-Department/   # REAL (Phase 1 + Agentic 1–3) — Chief 15 worker + 8 department manager + 43 specialist ডাকে, draft-only; worker-রা এখন ভিতরে vendored (Phase 6)
│   ├── chief_of_staff_agency.py  # REAL — ROUTING (15) + SECTION_ROUTING (6) + DEPARTMENT_ROUTING (8)
│   ├── pipeline.md             # 10 ধাপ + সৎ অবস্থা (mail 162, email PAUSED)
│   ├── governance/             # NEW (Agentic Phase 1) — office-charter.md + agent-permissions.md + approval-policy.md + security-policy.md
│   ├── departments/            # NEW (Agentic Phase 1–3) — 8 department (01-sales-growth … 08-product-innovation); প্রতিটায় SECTION.md + manager/ + skills/ + specialists/ (৪৩ worker .py)
│   ├── agents/agent-registry/  # NEW (Agentic Phase 1–3) — registry.md + registry.json (৬৯ entry: EXISTING ৬৫, GAP ৪)
│   ├── workflows/              # NEW (Agentic Phase 1) — 5 pipeline doc + README.md
│   ├── sub_agents/README.md    # sub-agent নোট
│   ├── engine/                 # REAL (Phase 5) — 15 staff, 8 tool (5 mock / 3 gated), 15 skill; workers/ (vendored boss-ceo engine, SOURCE.md + src/)
│   └── sections/               # REAL (Phase 7) — 5 section (receive/sell/delivery/marketing/ops), 6 নতুন agent + 6 skill, 15 mapped staff
├── 02-Digital-Product-Department/  # REAL* (Phase 2) — Chief আসল কাজ করে, kit blueprint + PA list 39/100; launch/sale Gate 0-তে আটকে
│   ├── chief_of_staff_products.py + README.md + kit-outline.md + gate0-status.md
│   ├── pa-vet-list/            # 39 verified PA vet clinic (goal 100)
│   ├── engine/                 # REAL* (Phase 5) — 5 staff, 8 tool (6 mock / 2 gated), 5 skill
│   └── sections/               # REAL* (Phase 7) — 6 section (product/research/launch/sales/support/finance), 7 agent + 7 skill; Gate 0 fail-closed
├── 03-Content-Creation-Department/ # REAL (Phase 3) — Chief 6 Creator OS worker ডাকে, draft-only; 13 stage REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; worker-রা এখন ভিতরে vendored (Phase 6)
│   ├── chief_of_staff_content.py + README.md + pipeline.md + VOICE.md (DRAFT) + toolpilot-status.md
│   ├── engine/                 # REAL (Phase 5) — 8 staff, 8 tool (5 mock / 3 gated), 8 skill; workers/ (vendored Creator OS, SOURCE.md + src/)
│   └── sections/               # REAL (Phase 7) — 5 section (plan/produce/publish/analyze/growth), 10 agent + 10 skill; upload OFF
├── CENTRAL-HQ/             # NEW (2026-11-19) — Unified OS layer, docs only (কোনো code নয়): unified-os.md + shared-services.md + data-isolation.md + cross-business.md + BUSINESS-01-AGENCY.md + BUSINESS-02-COMMERCE.md + BUSINESS-03-MEDIA.md
├── store/                  # tasks.json, approvals.json, vault/README.md (খালি — task 0, approval 0)
├── dashboards/             # status.html + status.json (sync_status.py দিয়ে বানানো — সংখ্যা আসল ফাইল থেকে) + engines.html (sync_engines.py দিয়ে বানানো) + dashboard-3d.html (3D dashboard, status.json পড়ে) + n8n-wiring.md (২ workflow-র map, READY NOT LIVE)
├── skills/                 # ৪টা skill manual (CEO + ৩ Chief)
├── scripts/                # check_phase0..4.py + check_engines.py + check_phase6.py + check_phase7.py + check_departments.py + check_specialists.py + run_office.py (runner) + sync_status.py + sync_engines.py + voice_test.py + check_voice.py + jarvis_voice_loop.py
├── .gitignore              # voice models/ + output/ push হয় না
├── LOCAL-RUN-BANGLA.md     # PC-তে চালানোর নির্দেশনা (Bengali) + run_local.bat (Windows)
├── README.md               # এই ফাইল
└── BUILD-LOG.md
```

## Phase 0 check চালানো

```bash
python3 ~/workspace/talvenor-master-os/scripts/check_phase0.py
```

সব PASS হলে Phase 0 ঠিক আছে।

## REAL vs STUB vs REUSED (সৎ টেবিল)

| জিনিস | অবস্থা |
|---|---|
| Approval gateway (approve/reject) | **REAL** — সত্যিই record করে, auto-approve নেই |
| BrainFactory (`brain.py`) | **REAL (Phase 6 + Phase 10)** — config flag `brain: mock` (default, $0, draft-only) / `live` (via `live_brain.py` LiveBrainAdapter, loud mock fallback; live verification 2026-11-06 TIMEOUT + 2026-11-20 tunnel-403, key path UNPROVEN, কোনো live call এখনো হয়নি) |
| Runner (`scripts/run_office.py`) | **REAL (Phase 6)** — এক command-এ office চালায় (Main CEO Bot → Chief → worker); gated কাজ PENDING-এ আটকায়; `--drain-queue --max 2` |
| Shared tool-calling core (`tool_calling.py`) | **REAL (Phase 5)** — registry + dispatcher; mock tool DRAFT ফেরত দেয়, gated tool PENDING-এ আটকায়, সব call log করে |
| Agency Engine (15 staff, 8 tool, 15 skill) | **REAL (Phase 5)** — draft-only, email PAUSED; send/publish/spend gated |
| Products Engine (5 staff, 8 tool, 5 skill) | **REAL* (Phase 5)** — launch/sale Gate 0-তে আটকে |
| Content Engine (8 staff, 8 tool, 8 skill) | **REAL (Phase 5)** — upload OFF, VOICE.md DRAFT, GPU নাম বাকি |
| Phase 7 sections (16 section, 23 agent, 23 skill) | **REAL** — draft-only, gated PENDING; Agency 5 section / 6 নতুন agent, Products 6 / 7 (Gate 0 fail-closed), Content 5 / 10 (upload OFF) |
| Main CEO Bot router | **REAL** — task ঠিক Chief-এর দিকে পাঠায় |
| config.json | **REAL** — locked facts |
| Dashboard status.html | **REAL** — sync_status.py দিয়ে বানানো, সংখ্যা আসল ফাইল থেকে |
| n8n workflows (auto-send + callback) | **READY · NOT LIVE** — import file তৈরি, Boss-এর import + connect + test বাকি |
| Jarvis voice | **REAL (2026-11-17)** — Piper TTS + Vosk (en) + sherpa-onnx (bn), offline, $0; mic যুক্ত; brain mock (voice Jarvis-কে বুদ্ধিমান বানায় না); gated কাজ voice-এ শুধু PENDING, execute নয় |
| Agency Chief of Staff | **REAL (Phase 1 + Agentic Phase 2 + 3)** — 15 worker + 8 department manager + 43 specialist routing (DEPARTMENT_ROUTING + manager→specialist importlib), draft-only, gated কাজ PENDING-এ আটকায় |
| Products Chief of Staff | **REAL* (Phase 2)** — ৪ task type routing, Gate 0 fail-closed, launch/sale আটকায় |
| Content Chief of Staff | **REAL (Phase 3)** — 6 Creator OS worker routing, draft-only, upload OFF-এ আটকায়, video file বানায় না |
| boss-ceo engine (15 worker) | **VENDORED (Phase 6)** — copy এখন `01-Agency-Department/engine/workers/`-এ ভিতরে; upstream `~/workspace/boss-ceo/` canonical থাকে, runtime dependency নয় |
| talvenor-office | **REUSED** — `~/workspace/talvenor-office/` (reference only) |
| Creator OS (6 worker) | **VENDORED (Phase 6)** — copy এখন `03-Content-Creation-Department/engine/workers/`-এ ভিতরে; upstream `~/workspace/creator-os-combined/` canonical থাকে, runtime dependency নয় |
| Jarvis concept/code | **REUSED** — `~/workspace/jarvis-ceo-os-concept/`, jarvis-os repo |
| 136 ব্যবসা / 1,189 worker | **DROPPED (Boss 2026-11-16)** — scope = 3 ব্যবসা only |

## Jarvis voice (REAL — 2026-11-17, phase নয়, voice addition)

- **বলা (TTS):** Piper, offline, $0। Bengali voice `bn_BD-google-medium` (Piper catalog-এর একমাত্র Bengali voice, CC-BY-SA-4.0) + English `en_US-lessac-medium` (Lessac licence — personal use OK, commercial-এর আগে licence দেখুন)।
- **শোনা (STT):** English Vosk `vosk-model-small-en-us-0.15` (40 MB, Apache-2.0); Bengali sherpa-onnx `vosk-model-small-streaming-bn` (~96 MB, Zipformer2, Apache-2.0, WER self-reported 17.9–32.9)। সত্য: classic Vosk-এর official list-এ কোনো Bengali model নেই — Bengali শোনে sherpa-onnx, Vosk নয়।
- **চালানো (Boss-এর PC, Windows):** `python scripts\jarvis_voice_loop.py` (default Bengali; `--lang en` English-এ)। Test: `python scripts\voice_test.py` (mic ছাড়া) + `python scripts\check_voice.py`। Setup: `00-CEO-Core/VOICE-SETUP.md`।
- **Verification (এই VM, 2026-11-17):** voice_test 7/7 PASS (en synth 71,724 B → Vosk "hello i am jarvis" exact; bn synth 82,988 B → sherpa "আমি জার্ফিস শুনছি" — "জার্ভিস"→"জার্ফিস" এক phoneme ভুল, WER-এর মধ্যেই); check_voice 13/14 (শুধু sounddevice FAIL — এই VM-এ PortAudio নেই, VM-only; Windows wheel-এ বান্ডেল থাকে)। Phase 0 8/8, Phase 7 18/18, মোট 138/138 — কোনো regression নেই।
- **সৎ সীমা:** Bengali voice-এর মান কেউ শোনেনি (Boss-ই প্রথম শুনবেন); Bengali STT-তে ভুল হবেই (ছোট model); brain mock — উত্তর MOCK-PLAN draft; live mic test শুধু Boss-এর PC-তে হবে (এই VM-এ PortAudio নেই); RAM টাইট (8 GB, ~1.4 GB free) — voice চালানোর সময় Chrome বন্ধ রাখুন।
- **Gate:** voice-এ "send"/"post it" বললে শুধু ApprovalGateway-এ PENDING লেখা হয়; execute হয় না। "upload it"/খরচ/delete voice-এ request করা যায় না।

## Gate (আইন)

`ok` / `post it` / `upload it` / `send` / `go` — Boss-এর exact
word ছাড়া send/publish/spend/delete হবে না। Spend cap **$0**।

## সত্য অবস্থা (2026-11-20)

- Paying client: **0**
- Jarvis voice: **REAL (2026-11-17)** — Piper+Vosk/sherpa, offline, $0; প্রথম live mic test Boss-এর PC-তে বাকি
- Email: **PAUSED** (2026-11-14 থেকে) — SPF/DMARC DNS fix Boss-এর হাতে বাকি
- প্রথম মেইল: 162
- Vet Kit Gate 0: **NOT PASSED** — Lemon Squeezy test Boss-এর step
- n8n workflows: **READY · NOT LIVE** — auto-send (8 node) + callback (3 node)
- Host: **Muse runtime + 10-min bridge cron `master-os-3d-bridge` ($0)** — ২৪/৭ server নেই। পুরনো ceo-office-dashboard + ceo-office-bridge 2026-11-20-এ delete — dashboard এখন একটাই, Talvenor Master OS 3D Dashboard।

## পরের Phase

- **Phase 1 — Agency:** ✅ BUILT 2026-11-16 (Chief REAL, 15 worker wired, check 11/11 PASS)।
- **Phase 2 — Digital Product:** ✅ BUILT 2026-11-16 *যতদূর Gate 0 যেতে দেয়* (Chief REAL, kit blueprint, PA list 39/100, check PASS) — kit build/sale/launch Gate 0-তে আটকে।
- **Phase 3 — Creator OS:** ✅ BUILT 2026-11-16 (Chief REAL, 6 worker wired, 13 stage REAL 0 / MOCK 10 / BLOCKED 3, upload OFF, check PASS)।
- **Phase 4 — n8n wiring:** ✅ BUILT 2026-11-16 (wiring doc + sync_status.py, ২ workflow READY NOT LIVE, dashboard sync-এ চলে, check 9/9 PASS)।
- **Phase 5 — Three Engines:** ✅ BUILT 2026-11-16 (shared tool-calling core + ৩ engine — Agency 15 staff / 8 tool / 15 skill, Products 5 / 8 / 5, Content 8 / 8 / 8; engines dashboard sync-এ চলে, check 45/45 PASS)।
- **Phase 6 — Full Complete Agent Offices:** ✅ BUILT 2026-11-16 (worker-রা ভিতরে vendored — Agency 18 file + Content 4 file + SOURCE.md; BrainFactory mock default / live unwired; `run_office.py` runner — এক command-এ office চলে, `--drain-queue --max 2`; 136 DROPPED, scope 3 ব্যবসা only; config phase 6 / v0.6.0; check 14/14 PASS)।
- **Phase 7 — Full Offices (Sections):** ✅ BUILT 2026-11-17 (১৬ section — Agency 5, Products 6, Content 5; ২৩ section agent + ২৩ section skill; Agency-র ১৫ worker mapped + ৬ নতুন agent, Products-এর ৭ agent (Gate 0 fail-closed — kit/sale কখনো লেখা হয় না), Content-এর ১০ agent (৬ wrapper + ২ chief-level + ২ নতুন; upload OFF); ৩ Chief-এ SECTION_ROUTING; config phase 7 / v0.7.0; check 18/18 PASS) — Phase 7 এখানেই শেষ নয়: তারপর Agentic Phase 1–3 + Unified OS (নিচে দেখুন)। মোট check এখন 200/200 (138 phases+engines + 21 departments + 41 specialists) + voice 13/14।
- **Agentic Agency Office Phase 1 — Foundation:** ✅ BUILT 2026-11-19 (Boss-এর order — আরেক AI-এর blueprint audit করে Agency office-এর সাথে combine; নতুন repo নয়, 01-Agency-Department-এর ভেতরেই): governance/ (charter, permissions, approval policy, security policy — ৪ file), departments/ (৮ department — Sales & Growth, Marketing, AI Engineering, Client Operations, Research & Strategy, Finance & Admin, Quality & Security, Product & Innovation; প্রতিটায় SECTION.md + manager .py + skill .md — ২৪ file), agents/agent-registry/ (registry.md + registry.json — ৬৯ entry: EXISTING ২২ role-entry = ২১ distinct worker, ROLE-ONLY ৪৩, GAP ৪; ৮ manager আলাদা তালিকায় EXISTING), workflows/ (৫ pipeline doc — lead-generation, sales-outreach, client-onboarding, receptionist-deployment, client-support)। ২১ existing staff map: Sales ৮, Marketing ৪, AI Eng ১, Client Ops ৫, Research ০ (GAP dept), Finance ২, Quality ১, Innovation ০ (GAP dept)। Audit সংশোধন: Retell production নয় — Vapi live (Sophia +19472230244); DB JSON store, PostgreSQL নয়; CRM n8n planned not live; Sophia live receptionist, demo নয়। ৮ manager live test PASS (TEMP store — draft-ready + unknown-task + pending-approval); সব check 138/138 + voice 13/14 PASS; sync byte-identical; store pristine। Agency Chief wiring **Phase 2 DONE 2026-11-19** — Chief এখন ৮ manager-কে DEPARTMENT_ROUTING দিয়ে ডাকে (নিচে "Agentic Agency Office Phase 2" দেখুন)। PUSHED 2026-11-19 ~23:40, head 162921aa (Boss-এর "finish everything + push"-এ, 55 file, 6 batch — Phase 1 + Phase 2 + Unified OS একসাথে)।
- **Agentic Agency Office Phase 2 — Executive wiring:** ✅ BUILT 2026-11-19 (Boss-এর order "যা বাকি আছে, সব কাজ শেষ করো" — Phase 1-এর ৮ manager-কে Agency Chief-এর সাথে যুক্ত করা): chief_of_staff_agency.py-তে নতুন DEPARTMENT_ROUTING — ৮ task type (dept_sales, dept_marketing, dept_engineering, dept_operations, dept_strategy, dept_finance, dept_quality, dept_innovation) → ৮ manager (ChiefGrowthAgent / MarketingDirectorAgent / CTOAIEngineeringAgent / COOClientOperationsAgent / ChiefStrategyAgent / CFOFinanceAgent / ChiefQualitySecurityAgent / ChiefInnovationAgent), gate সব `ok`, payload-এর task_kind → top-level translate (manager-রা task.get("task_kind") পড়ে), SECTION_ROUTING pattern-ই (importlib load + mock brain + tasks.json log), gated action → ApprovalGateway PENDING, unknown kind → "unknown-task"। ROUTING (১৫) ও SECTION_ROUTING (৬) অপরিবর্তিত। নতুন check script scripts/check_departments.py — ২১/২১ PASS (৮ manager load + ৮ route draft-ready [MOCK DRAFT] + ২ gated PENDING + ১ unknown-task + stale-claim grep clean + পুরনো check 138/138 + voice 13/14)। ২৫ file-এ stale wiring note ঠিক করা হয়েছে (৭৬ replacement + ৩ extra variant fix — "Chief এখনো call করে না" → "Chief এখন DEPARTMENT_ROUTING দিয়ে call করে")। PUSHED 2026-11-19 ~23:40, head 162921aa (Boss-এর "finish everything + push"-এ, 55 file, 6 batch)।
- **Agentic Agency Office Phase 3 — Specialists:** ✅ BUILT 2026-11-19 (Boss-এর order "go" — Phase 1-এর ৪৩ ROLE-ONLY role-কে আসল worker code হিসেবে বানানো): প্রতিটা role-এর skill .md প্রথমে লেখা, তারপর সেই skill থেকে worker .py (Phase 7 section-agent pattern — stdlib-only, Bengali docstring, run(task, brain, gateway, approvals_path), mock brain, DRAFT-labelled output, gated action → ApprovalGateway PENDING, কখনো execute নয়)। Per-dept: 01 Sales & Growth ৫ (Google Maps Prospect Finder, Business Verification, Lead Scoring, CRM Manager, Sales Intelligence), 02 Marketing ৪ (Market Positioning, Social Media, SEO, Analytics — worker file snake_case-এ rename করা হয়েছে), 03 AI Engineering ৭ (AI Solution Architect, Conversation Designer, Prompt Engineering, Vapi Integration — brief-এর Retell নাম corrected, Calendar Integration, n8n Automation, Deployment), 04 Client Operations ৪ (Call Monitoring, Client Reporting, Retention, Renewal & Upsell), 05 Research & Strategy ৭ (Competitor, Industry, Pricing, Niche Selection, Offer Development, Market Opportunity, Business Intelligence), 06 Finance & Admin ৪ (Revenue Tracking, Subscription Tracking, Document Management, Compliance Calendar), 07 Quality & Security ৬ (Call Scenario Testing, Workflow Testing, Data Validation, Security Monitoring, Access Control, Compliance Review), 08 Product & Innovation ৬ (New AI Product Research, New Feature Research, Automation R&D, Technology Evaluation, Product Improvement, Prototype Builder)। ৮ manager-ই নিজের specialist-দের importlib দিয়ে load করে চালায় (Chief→manager pattern-ই) — engine/section-এর পুরনো worker-দের plan-draft behavior অপরিবর্তিত, Chief-এর DEPARTMENT_ROUTING অপরিবর্তিত। Registry: ৬৯ entry — EXISTING ৬৫ (২২ role-entry + ৪৩ specialist = ৬৫ role-entry, ৬৪ distinct worker), ROLE-ONLY ০, GAP ৪ (Ad Campaign — $0 cap; CRM Integration — CRM live নয়; Expense Tracking — $0 spend; Backup & Recovery — backup system নেই) — GAP ৪-এর কোনো worker/skill বানানো হয়নি। নতুন check script scripts/check_specialists.py — ৪১/৪১ PASS (৪৩ load + ৪৩ draft-run + ৪৩ gated PENDING + ৮ manager route + ৮ manager gated + GAP + registry + stale-claim grep + forbidden terms + real store + পুরনো check 138/138 + check_departments 21/21)। Dept 02-র ৪ worker file snake_case-এ rename + ৬৮ stale-claim fix (manager .py/skill/SECTION.md — "কোনো worker execute করে না" → scoped সত্য: manager নতুন specialist চালায়, পুরনো engine/section worker চালায় না)। PUSHED 2026-11-20 ~00:21–01:19, head aab7dc03 (Boss-এর "push koro"-তে, 117 file, 12 batch)।
- **Old system delete + নতুন bridge (2026-11-20):** পুরনো `ceo-office-dashboard` artifact + `ceo-office-bridge` cron Boss-এর order-এ FULLY DELETE (backup `~/workspace/backups/ceo-office-dashboard-state-2026-11-20.json`); dashboard এখন একটাই — Talvenor Master OS 3D Dashboard (artifact `talvenor-master-os-3d-dashboard`)। নতুন bridge cron `master-os-3d-bridge` (প্রতি ১০ মিনিট) repo-র `store/tasks.json` queue পড়ে, আসল কাজ করে (সর্বোচ্চ ২/run, draft/result only — send/publish/spend/delete নয়), `dashboards/status.json` regenerate করে। Gate 0-র অবস্থা এখন chat-এ Elora-কে বললেই record হয় (dashboard-এ record করার পথ আর নেই)।

## Office চালানো (Phase 6 runner)

```bash
# একটা task (mock brain, draft-only) — আসল store-এ লেখে
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --business agency --task caption_write --input '{"title": "Caption pack", "platform": "instagram"}'

# Queue খালি করা (এক run-এ সর্বোচ্চ 2)
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --drain-queue --max 2

# Test — TEMP store-এ (আসল store ছোঁয় না)
python3 ~/workspace/talvenor-master-os/scripts/run_office.py --business content --task script_write --input '{}' --store-dir /tmp/store-test
```

Gated কাজ (send/publish/spend/delete) runner দিয়ে চলবে না — PENDING-এ
আটকাবে, Boss-এর gate word লাগবে। Brain `live` করতে হলে config.json-এ
`"brain": "live"` — শুধু Boss-এর কথায়, live verification-এর পরে।

## Dashboard sync চালানো

```bash
python3 ~/workspace/talvenor-master-os/scripts/sync_status.py
python3 ~/workspace/talvenor-master-os/scripts/check_phase4.py
```

sync চালালে `dashboards/status.html` আবার আসল ফাইল থেকে বানানো হয় —
হাতে সংখ্যা বদলালে sync-এ ফিরে যাবে। কোনো মান না পেলে "unknown"
লেখে, বানায় না।
