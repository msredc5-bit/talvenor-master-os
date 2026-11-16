# Talvenor Master OS — আসল সিস্টেম (Phase 5 — COMPLETE: Three Engines)

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
│   ├── tool_calling.py         # REAL (Phase 5 — ToolRegistry + dispatcher, 6 mock handler)
│   ├── jarvis_voice.py         # STUB (mic যুক্ত নয়)
│   ├── config.json             # REAL (locked facts)
│   └── CEO-README.md
├── 01-Agency-Department/   # REAL (Phase 1) — Chief 15 worker ডাকে, draft-only
│   └── engine/             # REAL (Phase 5) — 15 staff, 8 tool (5 mock / 3 gated), 15 skill
├── 02-Digital-Product-Department/  # REAL* (Phase 2) — Chief আসল কাজ করে, kit blueprint + PA list 39/100; launch/sale Gate 0-তে আটকে
│   └── engine/             # REAL* (Phase 5) — 5 staff, 8 tool (6 mock / 2 gated), 5 skill
├── 03-Content-Creation-Department/ # REAL (Phase 3) — Chief 6 Creator OS worker ডাকে, draft-only; 13 stage REAL 0 / MOCK 10 / BLOCKED 3; upload OFF
│   └── engine/             # REAL (Phase 5) — 8 staff, 8 tool (5 mock / 3 gated), 8 skill
├── store/                  # tasks.json, approvals.json, vault/
├── dashboards/             # status.html (sync_status.py দিয়ে বানানো — সংখ্যা আসল ফাইল থেকে) + engines.html (sync_engines.py দিয়ে বানানো) + n8n-wiring.md (২ workflow-র map, READY NOT LIVE)
├── skills/                 # ৪টা skill manual (CEO + ৩ Chief)
├── scripts/                # check_phase0..4.py + check_engines.py + sync_status.py + sync_engines.py
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
| Shared tool-calling core (`tool_calling.py`) | **REAL (Phase 5)** — registry + dispatcher; mock tool DRAFT ফেরত দেয়, gated tool PENDING-এ আটকায়, সব call log করে |
| Agency Engine (15 staff, 8 tool, 15 skill) | **REAL (Phase 5)** — draft-only, email PAUSED; send/publish/spend gated |
| Products Engine (5 staff, 8 tool, 5 skill) | **REAL* (Phase 5)** — launch/sale Gate 0-তে আটকে |
| Content Engine (8 staff, 8 tool, 8 skill) | **REAL (Phase 5)** — upload OFF, VOICE.md DRAFT, GPU নাম বাকি |
| Main CEO Bot router | **REAL** — task ঠিক Chief-এর দিকে পাঠায় |
| config.json | **REAL** — locked facts |
| Dashboard status.html | **REAL** — sync_status.py দিয়ে বানানো, সংখ্যা আসল ফাইল থেকে |
| n8n workflows (auto-send + callback) | **READY · NOT LIVE** — import file তৈরি, Boss-এর import + connect + test বাকি |
| Jarvis voice | **STUB** — mic যুক্ত নয় |
| Agency Chief of Staff | **REAL (Phase 1)** — 15 worker routing, draft-only, gated কাজ PENDING-এ আটকায় |
| Products Chief of Staff | **REAL* (Phase 2)** — ৪ task type routing, Gate 0 fail-closed, launch/sale আটকায় |
| Content Chief of Staff | **REAL (Phase 3)** — 6 Creator OS worker routing, draft-only, upload OFF-এ আটকায়, video file বানায় না |
| boss-ceo engine (15 worker) | **REUSED** — `~/workspace/boss-ceo/`, duplicate নয় |
| talvenor-office | **REUSED** — `~/workspace/talvenor-office/` |
| Creator OS (6 worker) | **REUSED** — `~/workspace/creator-os-combined/` |
| Jarvis concept/code | **REUSED** — `~/workspace/jarvis-ceo-os-concept/`, jarvis-os repo |

## Gate (আইন)

`ok` / `post it` / `upload it` / `send` / `go` — Boss-এর exact
word ছাড়া send/publish/spend/delete হবে না। Spend cap **$0**।

## সত্য অবস্থা (2026-11-16)

- Paying client: **0**
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
- **Phase 5 — Three Engines:** ✅ BUILT 2026-11-16 (shared tool-calling core + ৩ engine — Agency 15 staff / 8 tool / 15 skill, Products 5 / 8 / 5, Content 8 / 8 / 8; engines dashboard sync-এ চলে, check 45/45 PASS) — **সব Phase শেষ।**

## Dashboard sync চালানো

```bash
python3 ~/workspace/talvenor-master-os/scripts/sync_status.py
python3 ~/workspace/talvenor-master-os/scripts/check_phase4.py
```

sync চালালে `dashboards/status.html` আবার আসল ফাইল থেকে বানানো হয় —
হাতে সংখ্যা বদলালে sync-এ ফিরে যাবে। কোনো মান না পেলে "unknown"
লেখে, বানায় না।
