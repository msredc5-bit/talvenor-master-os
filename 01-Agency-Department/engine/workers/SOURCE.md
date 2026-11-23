# Vendored boss-ceo engine — source note

**Date vendored:** 2026-11-16 (Talvenor Master OS, Phase 6 — Agency Vendoring)

## Origin (canonical upstream)

- Local checkout: `~/workspace/boss-ceo`
- GitHub: `github.com/msredc5-bit/agency-ceo-os` (boss-ceo/)

`~/workspace/boss-ceo` stays the canonical upstream.
This directory is a **snapshot copy, not the upstream** — fixes and new
workers belong upstream first, then get re-vendored here.

## What was copied (copy only — upstream was not modified)

| Vendored file | Source file | Bytes |
|---|---|---|
| `src/__init__.py` | `src/__init__.py` (empty package marker) | 0 |
| `src/workers/__init__.py` | `src/workers/__init__.py` (empty package marker) | 0 |
| `src/workers/acquisition.py` | `src/workers/acquisition.py` — ProspectResearcher, OutreachDrafter, ReplyHandler, NegotiationCoach | 3774 |
| `src/workers/admin.py` | `src/workers/admin.py` — InboxTriager, ReportCompiler, SchedulerAssistant | 2108 |
| `src/workers/base.py` | `src/workers/base.py` — WorkerBase (imports `src.contracts.llm`, `src.contracts.models`, `src.contracts.worker`) | 2090 |
| `src/workers/delivery.py` | `src/workers/delivery.py` — OnboardingAgent, QAEngineer, RetellBuilder | 2675 |
| `src/workers/marketing.py` | `src/workers/marketing.py` — CaptionWriter, ContentPlanner, ObjectionSimulator, PublishPrep, VideoProducer | 4155 |
| `src/contracts/__init__.py` | `src/contracts/__init__.py` (empty package marker) | 0 |
| `src/contracts/llm.py` | `src/contracts/llm.py` — LLMProvider interface | 682 |
| `src/contracts/models.py` | `src/contracts/models.py` — Task, WorkerResult, DayReport, LedgerEntry, DivisionReport | 1540 |
| `src/contracts/worker.py` | `src/contracts/worker.py` — Worker interface | 503 |
| `src/contracts/ceo.py` | `src/contracts/ceo.py` — CEO interface (not imported by the workers; copied so the contracts package stays whole) | 624 |
| `src/contracts/division.py` | `src/contracts/division.py` — DivisionManager interface (not imported by the workers; copied so the contracts package stays whole) | 602 |
| `src/contracts/store.py` | `src/contracts/store.py` — Store interface (not imported by the workers; copied so the contracts package stays whole) | 742 |
| `src/mock/__init__.py` | `src/mock/__init__.py` (empty package marker) | 0 |
| `src/mock/provider.py` | `src/mock/provider.py` — MockLLMProvider (imports only `src.contracts.llm`; does NOT import `scenarios.py`) | 1424 |
| `src/live/__init__.py` | `src/live/__init__.py` (empty package marker) | 0 |
| `src/live/meta_provider.py` | `src/live/meta_provider.py` — MetaSparkProvider, the live brain (unwired by design — only the mock brain runs here) | 3702 |

Total: 18 files, 24,621 bytes. Verified byte-identical to upstream with
`diff -r` at vendoring time. No `__pycache__` / `*.pyc` files were copied.

## Added after vendoring (Phase 11, 2026-11-20 — live providers)

Six more live providers were added in `src/live/` (same pattern as
meta_provider — stdlib urllib, env-var auth, unwired by default):

| Vendored file | Provider | Bytes (2026-11-23) |
|---|---|---|
| `src/live/openai_provider.py` | OpenAI (gpt-4o) | 3966 |
| `src/live/anthropic_provider.py` | Claude (claude-sonnet-4-5) | 4303 |
| `src/live/gemini_provider.py` | Gemini (gemini-2.5-flash) | 4167 |
| `src/live/kimi_provider.py` | Kimi (kimi-k2.5) | 4141 |
| `src/live/grok_provider.py` | Grok (grok-4) | 4044 |
| `src/live/openrouter_provider.py` | OpenRouter (`openrouter/free`) | 4648 |

So `src/live/` now holds 7 providers (meta + these 6). The table above
still describes the 2026-11-16 vendoring exactly; this section is the
Phase 2 (2026-11-23) update, not a re-verification of the original copy.

## `__pycache__` note (Phase 2 correction)

"No `__pycache__` / `*.pyc` files were copied" was true at copy time.
`__pycache__` directories now exist throughout the vendored tree — they
were created by later test runs on this VM. They are gitignored build
artifacts, not source, and were never part of the vendored copy.

## What was NOT copied, and why

- `src/mock/scenarios.py` — nothing in the copied set imports it
  (`grep` over upstream `src/` finds zero references). It is test/demo
  data for the upstream repo only.
- `src/ceo/` (`boss_ceo.py`, `orchestrator.py`), `src/divisions/`
  (`manager.py`), `src/store/` (`db.py`, `schema.sql`) — no copied file
  imports any of them. The Chief talks to workers directly; the CEO
  orchestrator and the SQLite store are not part of the Agency office.
- `dynamic_credentials` — `src/live/meta_provider.py` imports it, but
  the module does NOT live inside boss-ceo. It lives at
  `/opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py`
  (the connector Secure Vault surrogate). Phase 2 (2026-11-23) changed
  how it is loaded: the old top-level `sys.path.insert` + import broke
  the module import on a plain checkout (Boss's PC), so the import is
  now LAZY — inside `complete()`, only when a live call actually runs.
  On the Muse VM the surrogate still resolves from that bin directory;
  on a machine without it, the live call fails with a clear error
  instead of the import failing. No key or credential path was invented,
  and no key appears anywhere in this repo. Note: the live provider is
  unwired here — the Chief only ever constructs `MockLLMProvider`.

## Import notes

- The copied files import only `src.*` (absolute) and relative
  (`from .models import ...`) names plus the stdlib (`re`, `hashlib`,
  `json`, `time`, `urllib.request`, `abc`, `dataclasses`, `datetime`).
  No `yaml` import anywhere in the copied set; `yaml` is importable in
  this environment anyway (`python3 -c "import yaml"` → PyYAML 6.0.1).
- No `src/store/db.py` dependency: the vendored workers never touch a
  database. Task logging goes through the Chief's own `_log_task`
  (JSON store under the repo's `store/`), unchanged by this vendoring.

## Why vendored

The Chief (`chief_of_staff_agency.py`) used to insert
`~/workspace/boss-ceo` on `sys.path`. The Agency office is now
self-contained: the Chief inserts this directory (`engine/workers/`)
instead, so `from src.contracts.models import ...`,
`from src.mock.provider import ...`, and
`from src.workers.<division> import ...` work with no path outside the
repo. The only remaining outside-department path insert is
`00-CEO-Core` (the shared approval gateway), which is inside this
repo. (Note: `00-CEO-Core/main_ceo_bot.py` used to carry a
`BOSS_CEO_ENGINE_PATH` constant pointing at the old checkout — it was
a comment-only reference that never inserted that path on `sys.path`,
and Phase 6 removed it entirely.)
