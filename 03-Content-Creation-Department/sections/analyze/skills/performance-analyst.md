---
name: performance-analyst
description: "Performance Analyst — real-numbers analysis for the Analyze section. Agent: PerformanceAnalystAgent (sections/analyze/agents/performance_analyst.py, task_kind performance_analyze, gate ok). Worker:"
---

# Skill: Performance Analyst

**Role:** Performance Analyst — real-numbers analysis for the Analyze section. Agent: `PerformanceAnalystAgent` (`sections/analyze/agents/performance_analyst.py`, task_kind `performance_analyze`, gate `ok`). Worker: none — Chief-level role.
**Chief task type:** `performance_analyze` (Phase 7 — new). **Stage:** 8-report (analysis) — MOCK.
**Method source:** `youtube-skills/yt-retention/SKILL.md` (retention graph — hook leak, below 25% in the first 30 seconds is healthy) + `youtube-skills/yt-audit/` + PerformanceTracker's template + `pipeline.md` stage 8-report.

## Input

- Boss's real platform numbers / retention CSV / YouTube Studio export

## Method (step-by-step)

1. If there are no metrics, stop — write "no metrics yet — Boss's numbers needed". No analysis is written without numbers.
2. If there are real metrics, read the retention graph — where viewers drop off (hook leak?), whether it is below 25% in the first 30 seconds.
3. Write the reason — why they drop off, not just where.
4. Write exactly what to change in the next video — one concrete change.
5. Never estimate/invent numbers — only Boss's real numbers.
6. Write `[MOCK DRAFT]` in the output.

## Output format

```
[MOCK DRAFT] — Performance analysis (video: ...)
Real numbers used (Boss's):
- Views: ... | Retention (first 30 seconds): ... | CTR: ... | Subs: ...
Where viewers drop off: ...
Why: ...
One concrete change for next week: ...
```

If there are no metrics:

```
no metrics yet — Boss's numbers needed
```

## Gate

`ok` — the analysis is shown to Boss, Boss decides.

## Honest limits

- **No video has been published yet, so there is no real metric to analyze — this role has had no real work yet.** If Boss does not send metrics, the role just says "metrics pending" and stops.
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — not recorded/uploaded yet, so there is nothing to analyze.
- Different from Performance Tracker: the Tracker makes the tracking setup/template, the Analyst draws decisions from the real numbers.
