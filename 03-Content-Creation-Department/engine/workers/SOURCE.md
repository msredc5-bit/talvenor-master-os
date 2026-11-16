# Vendored Creator OS workers — source note

**Date vendored:** 2026-11-16 (Talvenor Master OS, Phase 6 — Content Vendoring)

## Origin (canonical upstream)

- Local checkout: `~/workspace/creator-os-combined/`
- GitHub: `github.com/msredc5-bit/Creator-Studio`

`~/workspace/creator-os-combined` stays the canonical upstream.
This directory is a **snapshot copy, not the upstream** — fixes and new
workers belong upstream first, then get re-vendored here.

## What was copied (copy only — upstream was not modified)

| Vendored file | Source file | Bytes |
|---|---|---|
| `src/__init__.py` | `src/__init__.py` (empty package marker) | 0 |
| `src/creator_workers.py` | `src/creator_workers.py` — the 6 real workers: TopicResearcher, ScriptWriter, VisualProducer, CaptionWriter, PublishPrep, PerformanceTracker | 4828 |
| `src/workers/__init__.py` | `src/workers/__init__.py` (empty package marker) | 0 |
| `src/workers/base.py` | `src/workers/base.py` — WorkerBase, Task, WorkerResult, MockLLM, LLMProvider, LiveLLMProvider (unwired by design) | 7931 |

No extra modules were needed: `creator_workers.py` imports only
`src.workers.base`, and `base.py` imports only the stdlib (`os`, `re`,
`dataclasses`). No youtube-skills tool (e.g. `hookscore.py`) is imported
by the 6 workers' path, so none was copied. No `__pycache__` / `*.pyc`
files were copied.

`VOICE.md` (2116 bytes) was vendored separately at
`03-Content-Creation-Department/VOICE.md`, from
`youtube-skills/VOICE.md` upstream.

## Why vendored

The Chief (`chief_of_staff_content.py`) used to insert
`~/workspace/creator-os-combined` on `sys.path`. The Content office is
now self-contained: the Chief inserts this directory
(`engine/workers/`) instead, so `from src.creator_workers import ...`
and `from src.workers.base import ...` work with no path outside the
repo. The only remaining outside-repo path insert is `00-CEO-Core`
(the shared approval gateway), which is inside this repo.
