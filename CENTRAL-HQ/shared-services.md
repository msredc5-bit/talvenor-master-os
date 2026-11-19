# Central HQ — Shared Services (আসল জিনিসের সাথে ম্যাপ)

> Status: DRAFT — Boss-এর অনুমোদনের অপেক্ষায়
> তারিখ: 2026-11-19
> উদ্দেশ্য: brief-এর 10টি shared department-এর প্রতিটি আসলে কী, কোথায় থাকে, আসল অবস্থা কী — সেটা লেখা। brief-এর নাম রাখা হয়েছে, ভেতরের দাবি বাস্তবতা দিয়ে ঠিক করা হয়েছে।

## Status-এর মানে

| Status | মানে |
|---|---|
| BUILT | ফাইল/code আছে, যাচাই করা হয়েছে। |
| READY NOT LIVE | তৈরি, কিন্তু live চালু নয় — Boss-এর step বা gate বাকি। |
| DRAFT | খসড়া — final নয়, Boss-এর review বাকি। |
| GAP | বানানো হয়নি। |
| NOT PASSED | Gate পাস হয়নি — এগোনো BLOCKED। |

---

## 1. Executive Management — Main CEO Bot + 3 Chiefs

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | Boss-এর নির্দেশে 3টি business-কে পরিচালনা: Main CEO Bot routing করে, 3 Chief (Agency / Products / Content) নিজ নিজ business-এর দৈনন্দিন সমন্বয় করে। |
| কোথায় থাকে | `00-CEO-Core/main_ceo_bot.py`, `00-CEO-Core/config.json` (hierarchy + businesses); Chiefs: `01-Agency-Department/` (Agency Chief), `02-Digital-Product-Department/chief_of_staff_products.py`, `03-Content-Creation-Department/chief_of_staff_content.py` |
| আসল অবস্থা | BUILT (mock brain)। Chief→manager wiring Phase 2 — NOT BUILT, Boss-এর `go` বাকি। কোনো Chief gated action নিজে execute করে না। |

## 2. Strategic Planning — config.json + BUILD-LOG

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | Business goal, priority, phase-এর সিদ্ধান্ত — config-এ লেখা থাকে, BUILD-LOG-এ কাজের ইতিহাস থাকে। |
| কোথায় থাকে | `00-CEO-Core/config.json` (businesses, phases, gates, spend cap $0); `BUILD-LOG.md` (repo root, 584 লাইন, 2026-11-19 পর্যন্ত) |
| আসল অবস্থা | BUILT। Planning-এর সিদ্ধান্ত Boss নেন — কোনো agent নিজে strategy বদলাতে পারে না। |

## 3. AI Infrastructure — BrainFactory (mock) + Vapi + Ollama CPU-only

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | Model routing ও reasoning-এর জায়গা: BrainFactory (mock default, $0), live MetaSpark path UNPROVEN; voice stack Vapi (Sophia live); local ছোট মডেলের জন্য Ollama CPU-only। |
| কোথায় থাকে | `00-CEO-Core/brain.py` (BrainFactory); `00-CEO-Core/tool_calling.py` + `tools.json`; voice: `00-CEO-Core/jarvis_voice.py`, `00-CEO-Core/voice/` (Piper TTS + Vosk en + sherpa-onnx bn) |
| আসল অবস্থা | BUILT (mock)। Live MetaSpark UNPROVEN — কোনো live call হয়নি। Boss-এর PC: AMD Ryzen 3 5300U, 8GB RAM, Radeon integrated 496MB VRAM — GPU video / GPU Ollama CLOSED; CPU-only ছোট মডেল (1–1.5B) মাত্র। |

## 4. Agent Management — Agent Registry (69 entry) + Phase 7 Section Agents

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | কোন agent/worker আছে, তার status কী, gate কী — registry-তে লেখা। Phase 7-এর section agent-রা 3 business-এর section-এ কাজ করে। |
| কোথায় থাকে | `01-Agency-Department/agents/agent-registry/registry.md` + `registry.json` (69 entry: EXISTING 22 / ROLE-ONLY 43 / GAP 4; 8 manager আলাদা তালিকায়); Phase 7 sections: `01-Agency-Department/sections/`, `02-Digital-Product-Department/sections/`, `03-Content-Creation-Department/sections/` |
| আসল অবস্থা | BUILT (Phase 1, DRAFT — Boss-এর review-এর জন্য)। Registry-র 43টি ROLE-ONLY — শুধু role-এর সংজ্ঞা, worker code নেই। |

## 5. Memory Management — store/ + vault/ (central) + per-department ফোল্ডার

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | কেন্দ্রীয় task/approval record + shared vault; প্রতিটি department-এর নিজের ফোল্ডারে তার নিজের record। |
| কোথায় থাকে | Central: `store/tasks.json`, `store/approvals.json`, `store/vault/README.md`; Agency: `01-Agency-Department/`; Commerce: `02-Digital-Product-Department/`; Media: `03-Content-Creation-Department/` |
| আসল অবস্থা | BUILT (JSON store files)। আলাদা database নেই। কোনো business অন্য business-এর record পড়ে না — নিয়ম `data-isolation.md`-এ। |

## 6. Automation Engineering — n8n workflows READY NOT LIVE + run_office.py

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | Cross-business workflow-এর জায়গা: n8n wiring doc + office runner। |
| কোথায় থাকে | `dashboards/n8n-wiring.md` (wiring doc); `scripts/run_office.py` (runner — Main CEO Bot দিয়ে route করে, ApprovalGateway দিয়ে gate করে); `scripts/sync_status.py` |
| আসল অবস্থা | READY NOT LIVE — n8n workflow Boss-এর import + test বাকি। Runner mock brain দিয়ে চলে; gated action voice-এ শুধু PENDING হয়, execute হয় না। |

## 7. Finance Intelligence — আসল সংখ্যা (কোনো estimate নয়)

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | তিনটি business-এর একত্রিত আর্থিক ছবি — শুধু যা সত্যি তাই। |
| কোথায় থাকে | `00-CEO-Core/config.json` (honest_status); Agency finance: `01-Agency-Department/sections/ops/agents/billing_invoice_agent.py` (invoice — paying client ছাড়া বানানো হয় না); reporting: `ReportCompiler` (`01-Agency-Department/engine/workers/src/workers/admin.py`) |
| আসল অবস্থা | BUILT (reporting draft-only)। আসল সংখ্যা: paying client 0, revenue $0, spend cap $0, প্রথম মেইল 162, Vet Kit বিক্রি 0। Pricing LOCKED (internal only): Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build — prospect-কে কখনো quote নয়। |

## 8. Security & Governance — Agency governance (4 ফাইল) + Gates

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | Access, approval, audit — governance-এর ভিত্তি। |
| কোথায় থাকে | `01-Agency-Department/governance/office-charter.md`, `approval-policy.md`, `security-policy.md`, `agent-permissions.md`; gate: `00-CEO-Core/human_approval_gateway.py` |
| আসল অবস্থা | BUILT (Phase 1 foundation, DRAFT)। Gate ON: send / publish / spend / delete — Boss-এর exact word ছাড়া কিছু হয় না, কোনো auto-approve path নেই। এই governance এখন Agency-র; Commerce/Media-র জন্য আলাদা governance এখনো বানানো হয়নি — GAP। |

## 9. Performance Analytics — dashboards/status.html + ReportCompiler

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | কী হয়েছে, কী ভালো/খারাপ চলছে — শুধু যা দেখা যায় তাই। |
| কোথায় থাকে | `dashboards/status.html` (sync: `scripts/sync_status.py`); `ReportCompiler` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`report_compile`) |
| আসল অবস্থা | BUILT (status view — live dashboard নয়)। ReportCompiler visible metrics only — কখনো estimate/invent নয়। Platform-এর আসল number দেখা না গেলে Boss-কে paste করতে বলা হয়। |

## 10. Research Intelligence — ~/workspace/research_notes/ (shared, read-only source)

| বিষয় | বিবরণ |
|---|---|
| আসলে কী | তিনটি business-এর জন্য shared market research — এক জায়গা থেকে পড়া হয়, কেউ নিজের মতো বদলায় না। |
| কোথায় থাকে | `~/workspace/research_notes/` (repo-র বাইরে, shared, read-only source হিসেবে ব্যবহার) |
| আসল অবস্থা | BUILT (notes আছে)। Research থেকে পাওয়া তথ্য audit ছাড়া সিদ্ধান্তে নেওয়া হয় না — বাইরের research-এ ভুল brand/price/niche ঢুকতে পারে, তাই LOCKED FACTS-এর সাথে মিলিয়ে নিতে হয়। |

---

## যা এই shared services-এ নেই

- কোনো আলাদা live brain নেই (একটাই BrainFactory, mock)।
- কোনো live CRM নেই (n8n Data Tables PLANNED)।
- কোনো live automation নেই (n8n READY NOT LIVE)।
- কোনো paid ad / paid tool নেই (spend cap $0)।
