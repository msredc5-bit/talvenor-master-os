# Talvenor Master OS — আসল সিস্টেম (Phase 7 — COMPLETE: Full Offices / Sections)

**এটা কী:** Boss-এর ৩ ব্যবসার আসল operating system-এর folder। এটা
কোনো ছবি বা mock নয় — Phase 0-র skeleton + CEO Core + approval
gateway সত্যিই কাজ করে।

## ৩ ব্যবসা (শুধু এই ৩টাই — ১৩৬ নয়)

1. **Agency** — Talvenor AI Receptionist, US home-service ব্যবসার জন্য (MAIN)
2. **Digital Product** — Vet No-Show Recovery Kit, $49 one-time (Gate 0 বাকি)
3. **Content Creation Engine** — Creator OS / ToolPilot @ToolPilotai69

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
│   ├── brain.py                # REAL (Phase 6 — BrainFactory: mock default / live unwired-until-flipped)
│   ├── tool_calling.py         # REAL (Phase 5 — ToolRegistry + dispatcher, 6 mock handler)
│   ├── jarvis_voice.py         # REAL (2026-11-17 — Piper+Vosk/sherpa, offline, $0; একই 3 function)
│   ├── voice/                  # REAL (2026-11-17) — speak.py (Piper TTS), listen.py (Vosk en + sherpa-onnx bn), loop.py (শোনা → brain → বলা + gate); models/ + output/ git-এ যায় না
│   ├── VOICE-SETUP.md          # Windows setup guide (Bengali)
│   ├── config.json             # REAL (locked facts; brain: mock, phase 7, v0.7.0 + voice block)
│   └── CEO-README.md
├── 01-Agency-Department/   # REAL (Phase 1) — Chief 15 worker ডাকে, draft-only; worker-রা এখন ভিতরে vendored (Phase 6)
│   ├── engine/             # REAL (Phase 5) — 15 staff, 8 tool (5 mock / 3 gated), 15 skill
│   └── sections/           # REAL (Phase 7) — 5 section (receive/sell/delivery/marketing/ops), 6 নতুন agent + 6 skill, 15 mapped staff
├── 02-Digital-Product-Department/  # REAL* (Phase 2) — Chief আসল কাজ করে, kit blueprint + PA list 39/100; launch/sale Gate 0-তে আটকে
│   ├── engine/             # REAL* (Phase 5) — 5 staff, 8 tool (6 mock / 2 gated), 5 skill
│   └── sections/           # REAL* (Phase 7) — 6 section (product/research/launch/sales/support/finance), 7 agent + 7 skill; Gate 0 fail-closed
├── 03-Content-Creation-Department/ # REAL (Phase 3) — Chief 6 Creator OS worker ডাকে, draft-only; 13 stage REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; worker-রা এখন ভিতরে vendored (Phase 6)
│   ├── engine/             # REAL (Phase 5) — 8 staff, 8 tool (5 mock / 3 gated), 8 skill
│   └── sections/           # REAL (Phase 7) — 5 section (plan/produce/publish/analyze/growth), 10 agent + 10 skill; upload OFF
├── store/                  # tasks.json, approvals.json, vault/
├── dashboards/             # status.html (sync_status.py দিয়ে বানানো — সংখ্যা আসল ফাইল থেকে) + engines.html (sync_engines.py দিয়ে বানানো) + n8n-wiring.md (২ workflow-র map, READY NOT LIVE)
├── skills/                 # ৪টা skill manual (CEO + ৩ Chief)
├── scripts/                # check_phase0..4.py + check_engines.py + check_phase6.py + check_phase7.py + run_office.py (runner) + sync_status.py + sync_engines.py + voice_test.py + check_voice.py + jarvis_voice_loop.py
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
| BrainFactory (`brain.py`) | **REAL (Phase 6)** — config flag `brain: mock` (default, $0, draft-only) / `live` (unwired-until-flipped; live verification 2026-11-06-এ TIMEOUT, key path UNPROVEN, কোনো live call নেই) |
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
| Agency Chief of Staff | **REAL (Phase 1)** — 15 worker routing, draft-only, gated কাজ PENDING-এ আটকায় |
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

## সত্য অবস্থা (2026-11-16)

- Paying client: **0**
- Jarvis voice: **REAL (2026-11-17)** — Piper+Vosk/sherpa, offline, $0; প্রথম live mic test Boss-এর PC-তে বাকি
- Email: **PAUSED** (2026-11-14 থেকে) — SPF/DMARC DNS fix Boss-এর হাতে বাকি
- প্রথম মেইল: 162
- Vet Kit Gate 0: **NOT PASSED** — Lemon Squeezy test Boss-এর step
- n8n workflows: **READY · NOT LIVE** — auto-send (8 node) + callback (3 node)
- Host: **Muse runtime + 10-min bridge cron ($0)** — ২৪/৭ server নেই

## পরের Phase

- **Phase 1 — Agency:** ✅ BUILT 2026-11-16 (Chief REAL, 15 worker wired, check 11/11 PASS)।
- **Phase 2 — Digital Product:** ✅ BUILT 2026-11-16 *যতদূর Gate 0 যেতে দেয়* (Chief REAL, kit blueprint, PA list 39/100, check PASS) — kit build/sale/launch Gate 0-তে আটকে।
- **Phase 3 — Creator OS:** ✅ BUILT 2026-11-16 (Chief REAL, 6 worker wired, 13 stage REAL 0 / MOCK 10 / BLOCKED 3, upload OFF, check PASS)।
- **Phase 4 — n8n wiring:** ✅ BUILT 2026-11-16 (wiring doc + sync_status.py, ২ workflow READY NOT LIVE, dashboard sync-এ চলে, check 9/9 PASS)।
- **Phase 5 — Three Engines:** ✅ BUILT 2026-11-16 (shared tool-calling core + ৩ engine — Agency 15 staff / 8 tool / 15 skill, Products 5 / 8 / 5, Content 8 / 8 / 8; engines dashboard sync-এ চলে, check 45/45 PASS)।
- **Phase 6 — Full Complete Agent Offices:** ✅ BUILT 2026-11-16 (worker-রা ভিতরে vendored — Agency 18 file + Content 4 file + SOURCE.md; BrainFactory mock default / live unwired; `run_office.py` runner — এক command-এ office চলে, `--drain-queue --max 2`; 136 DROPPED, scope 3 ব্যবসা only; config phase 6 / v0.6.0; check 14/14 PASS)।
- **Phase 7 — Full Offices (Sections):** ✅ BUILT 2026-11-17 (১৬ section — Agency 5, Products 6, Content 5; ২৩ section agent + ২৩ section skill; Agency-র ১৫ worker mapped + ৬ নতুন agent, Products-এর ৭ agent (Gate 0 fail-closed — kit/sale কখনো লেখা হয় না), Content-এর ১০ agent (৬ wrapper + ২ chief-level + ২ নতুন; upload OFF); ৩ Chief-এ SECTION_ROUTING; config phase 7 / v0.7.0; check 18/18 PASS) — **সব Phase শেষ। মোট 138/138 PASS।**

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
