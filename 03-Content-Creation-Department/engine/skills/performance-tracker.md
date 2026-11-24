---
name: performance-tracker
description: "Performance Tracker — makes the Content Engine's tracking setup. Worker: PerformanceTracker (03-Content-Creation-Department/engine/workers/src/creator_workers.py, task_kind performance_track, gate"
---

# Skill: Performance Tracker

**Role:** Performance Tracker — makes the Content Engine's tracking setup. Worker: `PerformanceTracker` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `performance_track`, gate `ok`).
**Chief task type:** `performance_track`. **Stage:** 8-report (`youtube-skills/yt-retention/retention.py`).

## Input

- topic / video (published or about to be published)
- Boss's real platform numbers if sent (if not, the template itself is the output, no numbers will be invented)

## Method (step-by-step)

1. Write the tracking setup — which metric to take from which platform:
   - YouTube: views, watch hours, subs, retention, CTR
   - Facebook / Instagram / LinkedIn: reach, engagement, link click (what the platform actually shows)
2. Make a report template — best performer vs worst performer comparison format + a place for **one** change next week.
3. For retention: the `yt-retention` method — YouTube Studio → video → Analytics → Engagement → audience-retention chart → download ("Audience retention") CSV; run `retention.py retention.csv --duration 600` to find the hook leak. If there is no CSV, do not write retention analysis — write "BOSS INPUT REQUIRED: retention CSV".
4. Never estimate numbers — use only Boss's real platform numbers. If there are no numbers, leave the metric fields **0 / empty**, do not put made-up numbers in.
5. Label the output `[MOCK DRAFT]`. This is a template/setup — not analysis (analysis is Performance Analyst's job).

## Output format

```
[MOCK DRAFT] — Performance Report Template
Topic/Video: ...
Metrics to collect:
- YouTube: views / watch hours / subs / retention / CTR — Boss's numbers
- Facebook: ...
- Instagram: ...
- LinkedIn: ...
Best performer: ... (when real numbers arrive)
Worst performer: ... (when real numbers arrive)
One change for next week: ...
```

## Gate

`ok` — the template may not be used without Boss's "ok".

## Honest limits

- **No video has been published yet — metrics 0** (ToolPilot: subs 0, watch hours 0, videos 0). So right now this role can only give a template, not a report.
- Boss must send the retention CSV / Studio export — without an export there is no retention analysis.
- Different from Performance Analyst: the Tracker makes the setup/template; the Analyst analyzes the real numbers and draws decisions.
