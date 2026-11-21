# Section: Analyze

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (on top of the Chief's 6 worker routings, not replacing them)

## Purpose

Knowing how published content did — report template/setup (stage
8-report) and analysis of the real numbers. Two separate jobs: the Tracker makes the setup,
the Analyst draws decisions from the real numbers.

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Performance Tracker | `agents/performance_tracker.py` (`PerformanceTrackerAgent`) | `PerformanceTracker` (vendored) | `skills/performance-tracker.md` | ok | WRAPPED |
| Performance Analyst | `agents/performance_analyst.py` (`PerformanceAnalystAgent`) | Standalone (no worker — Chief-level role) | `skills/performance-analyst.md` | ok | WRAPPED* |

* Performance Analyst has no vendored worker — Chief-level role, so in Phase 7 it was made as a
standalone agent (before, there was only the `engine/skills/performance-analyst.md`
skill, no agent).

## How work flows

1. Boss / Main CEO Bot → Content Chief → task type `performance_track` or
   `performance_analyze`.
2. `performance_track` → vendored PerformanceTracker worker (mock brain, $0) →
   report template DRAFT (list of metrics + comparison format + one change).
3. `performance_analyze` → PerformanceAnalystAgent (standalone) → if Boss's
   real numbers are there, an analysis DRAFT; if not, it stops with "no metrics yet — Boss's
   numbers needed".
4. The result returns to the Main CEO Bot → Boss decides (gate "ok") → one
   concrete change goes into the next plan (stage 10-next-plan).

## Gate

- `ok` — the report template / analysis is shown to Boss, Boss decides.

## Honest limits

- **Metrics 0** — no video has been published yet (subs 0, hours 0, videos 0).
  Numbers are never estimated — only Boss's real platform numbers
  are used.
- **Performance Analyst has had no real work yet** — there is no real
  metric to analyze; if Boss does not send metrics, the agent just says "metrics pending" and stops.
- Retention: below 25% in the first 30 seconds is healthy (yt-retention) — without a CSV
  no leak is made up.
- Upload OFF — this section uploads nothing.
