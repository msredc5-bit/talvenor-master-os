# Talvenor Unified OS — Master Architecture Map

> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> উৎস: `~/workspace/briefs/unified-business-os-2026-11-19.md` (Boss-এর পাঠানো brief, অন্য AI-এর প্রস্তাব — verbatim সংরক্ষিত, design হিসেবে নেওয়া হয়নি) + `00-CEO-Core/config.json` (আসল সিস্টেম)
> নিয়ম: এই ফাইলের সাথে brief-এর বিরোধ হলে এই ফাইলের LOCKED FACTS-ই সঠিক।

## 1. Architecture এক নজরে

```
Boss (Md Mainuddin, Founder — MAINUDDIN LLC, Pennsylvania, USA)
  ↓  কথা বলেন / নির্দেশ দেন
Jarvis (voice interface — Main CEO Bot-এর ডাকনাম, আলাদা brain নয়)
  ↓
Main CEO Bot — Unified Master Brain (00-CEO-Core, BrainFactory, mock default, $0)
  ↓  3 জন Chief-এর কাছে routing
┌──────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ 01 Agency            │ 02 Commerce                  │ 03 Media                     │
│ Agency Chief         │ Products Chief               │ Content Chief                │
│ (MAIN business)      │ (Digital Product)            │ (Content Creation Engine)    │
└──────────────────────┴──────────────────────────────┴──────────────────────────────┘
  ↓                      ↓                              ↓
  workers / managers     kit blueprint + PA vet list    Creator OS workers (mock)
```

- **ONE brain, 3 Chief — 3টি আলাদা live brain নয়।** BrainFactory একটাই, `00-CEO-Core/`-তে। Live MetaSpark path UNPROVEN।
- **Jarvis = voice interface।** Piper TTS + Vosk (en) + sherpa-onnx (bn), offline, $0। Jarvis কথা শোনে ও বলে; বুদ্ধি Main CEO Bot-এর (mock)।
- **কোনো gated action (send / publish / spend / delete) Boss-এর exact gate word ছাড়া হয় না।** Gate word: `ok` / `"post it"` / `send` / `go` / `"upload it"`। কোনো auto-approve path নেই।

## 2. তিনটি Business OS — আসল অবস্থা

| # | Business OS | Department ফোল্ডার | Chief | আসল অবস্থা (2026-11-19) |
|---|---|---|---|---|
| 01 | AI Receptionist Agency (MAIN) | `01-Agency-Department/` | Agency Chief — REAL | Phase 1 BUILT: 8 department, 69 registry entry (EXISTING 22 / ROLE-ONLY 43 / GAP 4), 8 manager, 21 staff (15 worker + 6 section agent)। প্রথম মেইল 162, paying client 0, email PAUSED 2026-11-14 থেকে। |
| 02 | Digital Product (Vet No-Show Recovery Kit, $49 one-time) | `02-Digital-Product-Department/` | Products Chief — REAL | Gate 0 NOT passed (Lemon Squeezy signup test — Boss-এর step বাকি)। Kit 0/6 built, PA vet list 39/100, বিক্রি 0। |
| 03 | Content Creation Engine (Creator OS, ToolPilot @ToolPilotai69) | `03-Content-Creation-Department/` | Content Chief — REAL | Phase 3 BUILT: 6 Creator OS worker wired (mock brain, draft-only)। 13 stage: REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; VOICE.md DRAFT; ভিডিও 0। |

**সামগ্রিক সত্য:** paying client 0, revenue $0, spend cap $0।

## 3. Audit সংশোধন তালিকা (brief বনাম বাস্তবতা)

Brief-এর প্রতিটি ভুল এক লাইনে ঠিক করা হলো:

| # | Brief-এ যা লেখা ছিল | বাস্তবতা (এক লাইনে) |
|---|---|---|
| 1 | তিনটি ব্যবসার জন্য তিনটি আলাদা Brain | ONE brain — BrainFactory (`00-CEO-Core/`), mock default ($0); 3 জন Chief, আলাদা live brain নয়। |
| 2 | Agency-র নিজস্ব Agency CRM ও Client Database | DB = JSON store files (`store/tasks.json`, `store/approvals.json`); CRM = n8n Cloud Data Tables, PLANNED, live নয়। |
| 3 | AI Engineering-এ Retell দিয়ে voice agent | Retell DROPPED 2026-10-26 — live stack Vapi (Sophia, live receptionist, +1 (947) 223-0244, org 1861a735, GPT-4o-mini, Emma voice, Deepgram nova-3)। |
| 4 | Sophia-কে demo agent হিসেবে দেখানো | Sophia LIVE receptionist — demo-র কাজ করে না; Ava ছিল demo agent, delete করা হয়েছে, rebuild pending। |
| 5 | Commerce OS-এ 5 division (Amazon / Shopify / Etsy / Dropshipping / Digital Product) | Etsy CLOSED (Bangladesh থেকে বন্ধ, verified 2026-11-12) — live হিসেবে বানানো যাবে না; Amazon GATED (5 live client + $5K MRR না হওয়া পর্যন্ত বন্ধ); Shopify Boss-এর DIRECT parked project; আসল digital product Vet Kit $49, Gate 0 NOT passed। |
| 6 | Media Studio-তে 10 department, publishing পর্যন্ত পূর্ণ pipeline | 13 stage: REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; VOICE.md DRAFT; ToolPilot-এ ভিডিও 0। |
| 7 | প্রতিটি business-এর আলাদা database schema ও আলাদা database | আলাদা database নেই — একটাই JSON store; আলাদা করা হয় ফোল্ডার ও policy দিয়ে, database দিয়ে নয়। |
| 8 | Brief-এর 3টি ছবি (বাইরের product/blog diagram) | ছবিগুলো বাইরের, ব্যবহার করা হয়নি, reference-ও দেওয়া হয়নি। |
| 9 | Roadmap: Phase 01 Central HQ → Phase 09 Security & Testing | Master OS Phase 0–7 BUILT (2026-11-16–17); Phase 2 Chief→manager wiring বাকি — নিচে §5 দেখুন। |
| 10 | "প্রথমে 1 Master Agent + 3 Manager, তারপর বাড়াও" | এই পরামর্শ ঠিক — মানা হয়েছে: Agency-তে 21 staff + 8 manager, registry-তে 69 entry। |

## 4. Architecture নিয়ম (Central HQ + Data Isolation)

1. **একটাই HQ:** সিদ্ধান্ত, routing, approval, finance overview, dashboard — সব কেন্দ্রীয় (`CENTRAL-HQ/` + `00-CEO-Core/`)।
2. **Data isolation:** কোনো business অন্য business-এর client data, order বা financial record Boss-এর অনুমতি ছাড়া পড়তে পারবে না। বিস্তারিত: `data-isolation.md`।
3. **Shared service, আলাদা record:** Central service (research, content, automation) সবাইকে সাহায্য করতে পারে, কিন্তু কাজ ও খরচ প্রতিটি business-এর জন্য আলাদা project হিসেবে track হয়। বিস্তারিত: `cross-business.md`।
4. **নতুন business যোগ:** নতুন Business OS হিসেবে যোগ হবে — পুরো সিস্টেম আবার বানানো যাবে না।
5. **কোনো secret prompt/repo-তে নয়:** key শুধু connector Secure Vault দিয়ে — বিস্তারিত: `data-isolation.md` §4।

## 5. যা বাকি আছে

| কাজ | অবস্থা |
|---|---|
| Phase 2 — Chief→manager wiring (8 Agency manager-কে Agency Chief-এর সাথে সংযোগ) | NOT BUILT — Boss-এর `go` বাকি। Manager-রা এখন standalone, DRAFT-only। |
| Commerce OS build order | Gate 0 আগে (Lemon Squeezy signup test — Boss-এর step)। Gate 0 pass না হলে kit build / sale BLOCKED। |
| Media OS build order | Upload OFF রাখা; VOICE.md DRAFT থেকে final করা; ToolPilot-এর প্রথম ভিডিও Boss-এর `ok` + `"upload it"`-এর পর। |
| Unified CEO Dashboard | `dashboards/status.html` (sync_status.py) আছে — live dashboard নয়, status view। Central HQ dashboard-এর বাড়তি কাজ Boss-এর সিদ্ধান্তের অপেক্ষায়। |
| n8n workflows | READY NOT LIVE — Boss-এর import + test বাকি। |

## 6. এই ফোল্ডারের ফাইল

| ফাইল | কাজ |
|---|---|
| `unified-os.md` (এই ফাইল) | Master architecture map + audit সংশোধন |
| `shared-services.md` | Brief-এর 10 shared department — আসল জিনিসের সাথে ম্যাপ |
| `data-isolation.md` | DATA policy (policy only, নতুন data নয়) |
| `cross-business.md` | Cross-business collaboration নিয়ম |

## 7. Never-Do List (এই layer-এর জন্য)

- Brief-এর ভুল (Retell production, আলাদা live brain, আলাদা database, বন্ধ marketplace-কে live ধরা) কখনো সত্য হিসেবে লেখা যাবে না।
- Client, testimonial, case study, review, statistic, price, guarantee — কিছুই invent করা যাবে না।
- Dental/medical কখনো target নয়।
- Brand Talvenor ছাড়া অন্য কোনো পুরনো brand name ব্যবহার করা যাবে না।
- Boss-এর exact gate word ছাড়া send / publish / spend / delete নয়।
