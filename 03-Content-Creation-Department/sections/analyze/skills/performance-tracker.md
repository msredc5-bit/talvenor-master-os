---
name: performance-tracker
description: "Performance Tracker — making the report template/setup for the Analyze section. Agent: PerformanceTrackerAgent (sections/analyze/agents/performance_tracker.py, task_kind performance_track, gate ok)."
---

# Skill: Performance Tracker

**Role:** Performance Tracker — making the report template/setup for the Analyze section. Agent: `PerformanceTrackerAgent` (`sections/analyze/agents/performance_tracker.py`, task_kind `performance_track`, gate `ok`). Worker: `PerformanceTracker` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `performance_track`, gate `ok`).
**Chief task type:** `performance_track`. **Stage:** 8-report (`youtube-skills/yt-retention/retention.py` — reads a retention CSV to find the hook leak) — MOCK.

## Input

- topic/video
- Boss's real platform numbers if sent

## Method (step-by-step)

1. Make a report template — which metric to take from where (views, retention, CTR, subs — from a YouTube Studio export), best/worst comparison format, one change for next week.
2. If there is a retention CSV, find the hook leak with `retention.py` — below 25% in the first 30 seconds is healthy. If there is no CSV, say so; do not make up a leak.
3. Never estimate numbers — use only Boss's real platform numbers.
4. Write `[MOCK DRAFT]` in the output.

## Output format

```
[MOCK DRAFT] — Performance report template (topic: ...)
Metrics to collect (from Boss's real numbers):
- Views: ...
- Retention (first 30 seconds): ...
- CTR: ...
- Subs: ...
Best / worst comparison: ...
One change for next week: ...
```

## Gate

`ok` — the report template may not be used without Boss's "ok".

## Honest limits

- **Metrics 0** — no video has been published yet (subs 0, hours 0, videos 0). Numbers are not estimated.
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — not recorded/uploaded yet, so there is no metric to report; the template is only a DRAFT.
- Different from Performance Analyst: the Tracker makes the setup/template, the Analyst analyzes the real numbers.
