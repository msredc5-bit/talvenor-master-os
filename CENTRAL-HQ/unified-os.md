# Talvenor Unified OS — Master Architecture Map

> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Source: `~/workspace/briefs/unified-business-os-2026-11-19.md` (the brief Boss sent, another AI's proposal — preserved verbatim, not taken as design) + `00-CEO-Core/config.json` (the real system)
> Rule: if the brief conflicts with this file, this file's LOCKED FACTS are correct.

## 1. Architecture at a glance

```
Boss (Md Mainuddin, Founder — MAINUDDIN LLC, Pennsylvania, USA)
  ↓  talks / gives orders
Jarvis (voice interface — the Main CEO Bot's nickname, not a separate brain)
  ↓
Main CEO Bot — Unified Master Brain (00-CEO-Core, BrainFactory, mock default, $0)
  ↓  routing to the 3 Chiefs
┌──────────────────────┬──────────────────────────────┬──────────────────────────────┐
│ 01 Agency            │ 02 Commerce                  │ 03 Media                     │
│ Agency Chief         │ Products Chief               │ Content Chief                │
│ (MAIN business)      │ (Digital Product)            │ (Content Creation Engine)    │
└──────────────────────┴──────────────────────────────┴──────────────────────────────┘
  ↓                      ↓                              ↓
  workers / managers     kit blueprint + PA vet list    Creator OS workers (mock)
```

- **ONE brain, 3 Chiefs — not 3 separate live brains.** BrainFactory is one only, in `00-CEO-Core/`. Live MetaSpark path UNPROVEN.
- **Jarvis = voice interface.** Piper TTS + Vosk (en) + sherpa-onnx (bn), offline, $0. Jarvis listens and speaks; the smarts belong to the Main CEO Bot (mock).
- **No gated action (send / publish / spend / delete) happens without Boss's exact gate word.** Gate words: `ok` / `"post it"` / `send` / `go` / `"upload it"`. No auto-approve path.

## 2. Three Business OS — real state

| # | Business OS | Department folder | Chief | Real state (2026-11-19) |
|---|---|---|---|---|
| 01 | AI Receptionist Agency (MAIN) | `01-Agency-Department/` | Agency Chief — REAL | Phase 1 BUILT: 8 departments, 69 registry entries (EXISTING 69, GAP 0 — Phase 3 + 2026-11-21 GAP-worker build), 8 managers, 21 staff (15 workers + 6 section agents). First mails 163, paying clients 0, email PAUSED since 2026-11-14. |
| 02 | Digital Product (Vet No-Show Recovery Kit, $49 one-time) | `02-Digital-Product-Department/` | Products Chief — REAL | Gate 0 NOT passed (Lemon Squeezy signup test — Boss's step remaining). Kit 0/6 built, PA vet list 39/100, sales 0. |
| 03 | Content Creation Engine (Creator OS, ToolPilot @ToolPilotai69) | `03-Content-Creation-Department/` | Content Chief — REAL | Phase 3 BUILT: 6 Creator OS workers wired (mock brain, draft-only). 13 stages: REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; VOICE.md DRAFT; videos 0. |

**Overall truth:** paying clients 0, revenue $0, spend cap $0.

## 3. Audit correction list (brief vs reality)

Each of the brief's errors fixed in one line:

| # | What the brief said | Reality (in one line) |
|---|---|---|
| 1 | Three separate Brains for three businesses | ONE brain — BrainFactory (`00-CEO-Core/`), mock default ($0); 3 Chiefs, no separate live brains. |
| 2 | Agency's own Agency CRM and Client Database | DB = JSON store files (`store/tasks.json`, `store/approvals.json`); CRM = n8n Cloud Data Tables, PLANNED, not live. |
| 3 | Voice agent with Retell in AI Engineering | Retell DROPPED 2026-10-26 — live stack Vapi (Sophia, live receptionist, +1 (947) 223-0244, org 1861a735, GPT-4o-mini, Emma voice, Deepgram nova-3). |
| 4 | Showing Sophia as a demo agent | Sophia is the LIVE receptionist — does no demo work; Ava was the demo agent, deleted, rebuild pending. |
| 5 | 5 divisions in Commerce OS (Amazon / Shopify / Etsy / Dropshipping / Digital Product) | Etsy CLOSED (closed from Bangladesh, verified 2026-11-12) — cannot be built as live; Amazon GATED (closed until 5 live clients + $5K MRR); Shopify is Boss's DIRECT parked project; the real digital product is the Vet Kit $49, Gate 0 NOT passed. |
| 6 | 10 departments in Media Studio, full pipeline up to publishing | 13 stages: REAL 0 / MOCK 10 / BLOCKED 3; upload OFF; VOICE.md DRAFT; 0 videos on ToolPilot. |
| 7 | Each business's own database schema and own database | No separate database — one JSON store; separation is by folder and policy, not by database. |
| 8 | The brief's 3 images (outside product/blog diagrams) | The images are from outside, not used, not even referenced. |
| 9 | Roadmap: Phase 01 Central HQ → Phase 09 Security & Testing | Master OS Phase 0–7 BUILT (2026-11-16–17); Phase 2 Chief→manager wiring DONE 2026-11-19 — see §5 below. |
| 10 | "First 1 Master Agent + 3 Managers, then grow" | This advice is right — followed: 21 staff + 8 managers in the Agency, 69 entries in the registry. |

## 4. Architecture rules (Central HQ + Data Isolation)

1. **One HQ only:** decisions, routing, approval, finance overview, dashboard — all central (`CENTRAL-HQ/` + `00-CEO-Core/`).
2. **Data isolation:** no business may read another business's client data, orders, or financial records without Boss's permission. Details: `data-isolation.md`.
3. **Shared service, separate records:** central services (research, content, automation) can help everyone, but work and cost are tracked as separate projects for each business. Details: `cross-business.md`.
4. **Adding a new business:** it is added as a new Business OS — the whole system is not rebuilt.
5. **No secret in a prompt/repo:** keys only via the connector Secure Vault — details: `data-isolation.md` §4.

## 5. What remains

| Work | State |
|---|---|
| Phase 2 — Chief→manager wiring (connecting the 8 Agency managers to the Agency Chief) | DONE 2026-11-19 — the Chief calls the 8 managers via DEPARTMENT_ROUTING (`01-Agency-Department/chief_of_staff_agency.py`; `scripts/check_departments.py` 21/21). |
| Commerce OS build order | Gate 0 first (Lemon Squeezy signup test — Boss's step). If Gate 0 does not pass, kit build / sales BLOCKED. |
| Media OS build order | Keep upload OFF; finalize VOICE.md from DRAFT; ToolPilot's first video after Boss's `ok` + `"upload it"`. |
| Unified CEO Dashboard | `dashboards/status.html` (sync_status.py) exists — not a live dashboard, a status view. Extra work on the Central HQ dashboard awaits Boss's decision. |
| n8n workflows | READY NOT LIVE — Boss's import + test remaining. |

## 6. Files in this folder

| File | Job |
|---|---|
| `unified-os.md` (this file) | Master architecture map + audit corrections |
| `shared-services.md` | The brief's 10 shared departments — mapped to the real things |
| `data-isolation.md` | DATA policy (policy only, no new data) |
| `cross-business.md` | Cross-business collaboration rules |

## 7. Never-Do List (for this layer)

- The brief's errors (Retell in production, separate live brains, separate databases, treating closed marketplaces as live) must never be written as truth.
- Client, testimonial, case study, review, statistic, price, guarantee — nothing may be invented.
- Dental/medical are never targets.
- No old brand name other than Talvenor may be used.
- No send / publish / spend / delete without Boss's exact gate word.
