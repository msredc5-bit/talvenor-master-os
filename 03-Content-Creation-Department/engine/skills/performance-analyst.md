---
name: performance-analyst
description: "Performance Analyst — analyzes the real performance of published content. Worker: no worker — Chief-level role. Method source: youtube-skills/yt-retention/SKILL.md + youtube-skills/yt-audit/ +"
---

# Skill: Performance Analyst

**Role:** Performance Analyst — analyzes the real performance of published content. Worker: **no worker — Chief-level role**. Method source: `youtube-skills/yt-retention/SKILL.md` + `youtube-skills/yt-audit/` + PerformanceTracker's template + `../pipeline.md` stage 8-report.
**Chief task type:** — (Chief-level, no routed task type). **Stage:** 8-report (analysis).

## Input

- Boss's real platform numbers (views, watch hours, subs, retention, CTR) — **this is the main input**
- Retention CSV / YouTube Studio export (if there is one — Studio → video → Analytics → Engagement → retention chart → download)
- PerformanceTracker's report template

## Method (step-by-step)

1. Do not start without real numbers — if there are none, write "BOSS INPUT REQUIRED: real platform numbers / retention CSV" and stop. Do not invent or estimate numbers.
2. Read the retention graph — the `yt-retention` method: the retention graph is YouTube's only honest feedback. Separate three problems:
   - **HOOK LEAK** — what is lost in the first 30 seconds (below 25% is healthy) — the fix is always in the script's first 15 seconds, not in the edit.
   - Drop in the middle — pacing / boring section.
   - Drop at the end — CTA / close problem.
3. Do a best vs worst comparison — which video/post did well, which did badly, with real numbers. Use only the numbers the platform shows.
4. Write **one concrete change** for next week — e.g. "change the hook's first line" — do not write vague advice ("do better").
5. Give the analysis to the Content Planner — next week's plan (stage 10-next-plan) will change from this analysis.
6. Label the output `[MOCK DRAFT]` (analysis draft — the decision is Boss's).

## Output format

```
[MOCK DRAFT] — Performance Analysis
Video/Post: ... | Time: ...
Real numbers (Boss's): views ... | retention ... | CTR ... | subs ...
Retention: hook leak ...% (first 30 seconds) / middle drop ... / end ...
Best: ... (why, with numbers) | Worst: ... (why, with numbers)
One concrete change for next week: ...
```

## Gate

`ok` — the analysis is shown to Boss, Boss decides.

## Honest limits

- **No video has been published yet, so there is no real metric to analyze — this role has had no real work yet.** ToolPilot: subs 0, watch hours 0, videos 0.
- If Boss does not send metrics, this role just says "metrics pending" and stops — no empty analysis is written.
- Different from Performance Tracker: the Tracker makes the tracking setup/template; the Analyst draws decisions from the real numbers.
