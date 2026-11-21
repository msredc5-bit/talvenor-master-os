# Central HQ — Shared Services (mapped to the real things)

> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Purpose: write what each of the brief's 10 shared departments really is, where it lives, and its real state. The brief's names are kept; the claims inside are corrected with reality.

## What the statuses mean

| Status | Means |
|---|---|
| BUILT | Files/code exist, verified. |
| READY NOT LIVE | Ready, but not live — Boss's step or gate remaining. |
| DRAFT | Draft — not final, Boss's review remaining. |
| GAP | Not built. |
| NOT PASSED | Gate not passed — moving forward BLOCKED. |

---

## 1. Executive Management — Main CEO Bot + 3 Chiefs

| Item | Details |
|---|---|
| What it really is | Running the 3 businesses on Boss's orders: the Main CEO Bot routes, and the 3 Chiefs (Agency / Products / Content) coordinate each business's day-to-day work. |
| Where it lives | `00-CEO-Core/main_ceo_bot.py`, `00-CEO-Core/config.json` (hierarchy + businesses); Chiefs: `01-Agency-Department/` (Agency Chief), `02-Digital-Product-Department/chief_of_staff_products.py`, `03-Content-Creation-Department/chief_of_staff_content.py` |
| Real state | BUILT (mock brain). Chief→manager wiring Phase 2 — DONE 2026-11-19 (Chiefs call the 8 managers via DEPARTMENT_ROUTING). No Chief executes a gated action itself. |

## 2. Strategic Planning — config.json + BUILD-LOG

| Item | Details |
|---|---|
| What it really is | Business goals, priorities, phase decisions — written in config, with work history in BUILD-LOG. |
| Where it lives | `00-CEO-Core/config.json` (businesses, phases, gates, spend cap $0); `BUILD-LOG.md` (repo root, 716 lines, up to 2026-11-21) |
| Real state | BUILT. Boss makes the planning decisions — no agent can change strategy by itself. |

## 3. AI Infrastructure — BrainFactory (mock) + Vapi + Ollama CPU-only

| Item | Details |
|---|---|
| What it really is | The place for model routing and reasoning: BrainFactory (mock default, $0), live MetaSpark path UNPROVEN; voice stack Vapi (Sophia live); Ollama CPU-only for small local models. |
| Where it lives | `00-CEO-Core/brain.py` (BrainFactory); `00-CEO-Core/tool_calling.py` + `tools.json`; voice: `00-CEO-Core/jarvis_voice.py`, `00-CEO-Core/voice/` (Piper TTS + Vosk en + sherpa-onnx bn) |
| Real state | BUILT (mock). Live MetaSpark UNPROVEN — no live call made. Boss's PC: AMD Ryzen 3 5300U, 8GB RAM, Radeon integrated 496MB VRAM — GPU video / GPU Ollama CLOSED; CPU-only small models (1–1.5B) only. |

## 4. Agent Management — Agent Registry (69 entry) + Phase 7 Section Agents

| Item | Details |
|---|---|
| What it really is | Which agents/workers exist, their status, their gates — written in the registry. Phase 7's section agents work in the 3 businesses' sections. |
| Where it lives | `01-Agency-Department/agents/agent-registry/registry.md` + `registry.json` (69 entries: EXISTING 69 / ROLE-ONLY 0 / GAP 0 — Phase 3 + 2026-11-21 GAP-worker build; 8 managers in a separate list); Phase 7 sections: `01-Agency-Department/sections/`, `02-Digital-Product-Department/sections/`, `03-Content-Creation-Department/sections/` |
| Real state | BUILT (Phase 1, DRAFT — for Boss's review). The registry's 43 ROLE-ONLY entries are now 0 — every role has worker code (43 Phase 3 specialists + 4 GAP workers, 2026-11-21). |

## 5. Memory Management — store/ + vault/ (central) + per-department folders

| Item | Details |
|---|---|
| What it really is | Central task/approval records + shared vault; each department's own records in its own folder. |
| Where it lives | Central: `store/tasks.json`, `store/approvals.json`, `store/vault/README.md`; Agency: `01-Agency-Department/`; Commerce: `02-Digital-Product-Department/`; Media: `03-Content-Creation-Department/` |
| Real state | BUILT (JSON store files). No separate database. No business reads another business's records — rules in `data-isolation.md`. |

## 6. Automation Engineering — n8n workflows READY NOT LIVE + run_office.py

| Item | Details |
|---|---|
| What it really is | The place for cross-business workflows: n8n wiring doc + office runner. |
| Where it lives | `dashboards/n8n-wiring.md` (wiring doc); `scripts/run_office.py` (runner — routes via Main CEO Bot, gates via ApprovalGateway); `scripts/sync_status.py` |
| Real state | READY NOT LIVE — n8n workflow import + test remaining for Boss. The runner runs on the mock brain; a gated action only becomes PENDING by voice, never executes. |

## 7. Finance Intelligence — real numbers (no estimates)

| Item | Details |
|---|---|
| What it really is | The combined financial picture of the three businesses — only what is true. |
| Where it lives | `00-CEO-Core/config.json` (honest_status); Agency finance: `01-Agency-Department/sections/ops/agents/billing_invoice_agent.py` (invoices — never made without a paying client); reporting: `ReportCompiler` (`01-Agency-Department/engine/workers/src/workers/admin.py`) |
| Real state | BUILT (reporting draft-only). Real numbers: paying clients 0, revenue $0, spend cap $0, first mails 162, Vet Kit sales 0. Pricing LOCKED (internal only): Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build — never quote to a prospect. |

## 8. Security & Governance — Agency governance (4 files) + Gates

| Item | Details |
|---|---|
| What it really is | Access, approval, audit — the foundation of governance. |
| Where it lives | `01-Agency-Department/governance/office-charter.md`, `approval-policy.md`, `security-policy.md`, `agent-permissions.md`; gate: `00-CEO-Core/human_approval_gateway.py` |
| Real state | BUILT (Phase 1 foundation, DRAFT). Gate ON: send / publish / spend / delete — nothing happens without Boss's exact word, no auto-approve path. This governance is the Agency's for now; separate governance for Commerce/Media is not built yet — GAP. |

## 9. Performance Analytics — dashboards/status.html + ReportCompiler

| Item | Details |
|---|---|
| What it really is | What happened, what is going well/badly — only what can be seen. |
| Where it lives | `dashboards/status.html` (sync: `scripts/sync_status.py`); `ReportCompiler` — `01-Agency-Department/engine/workers/src/workers/admin.py` (`report_compile`) |
| Real state | BUILT (status view — not a live dashboard). ReportCompiler uses visible metrics only — never estimates/invents. If a platform's real numbers cannot be seen, Boss is asked to paste them. |

## 10. Research Intelligence — ~/workspace/research_notes/ (shared, read-only source)

| Item | Details |
|---|---|
| What it really is | Shared market research for the three businesses — read from one place, nobody changes it their own way. |
| Where it lives | `~/workspace/research_notes/` (outside the repo, shared, used as a read-only source) |
| Real state | BUILT (notes exist). Information from research is not used in decisions without an audit — outside research can smuggle in a wrong brand/price/niche, so it must be checked against LOCKED FACTS. |

---

## What is not in these shared services

- No separate live brain (one BrainFactory, mock).
- No live CRM (n8n Data Tables PLANNED).
- No live automation (n8n READY NOT LIVE).
- No paid ads / paid tools (spend cap $0).
