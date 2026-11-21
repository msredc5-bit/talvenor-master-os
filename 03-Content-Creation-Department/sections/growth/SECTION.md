# Section: Growth

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (on top of the Chief's 6 worker routings, not replacing them)

## Purpose

Growing the channel — trend research + collab-outreach draft (Growth Agent) and
a plan to split a long video into Shorts (Repurpose Agent). Both are NEW roles in Phase 7 —
before, the engine had no staff/worker/skill for them.

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Growth Agent | `agents/growth_agent.py` (`GrowthAgent`) | Standalone (NEW — no worker) | `skills/growth-agent.md` | send | NEW |
| Repurpose Agent | `agents/repurpose_agent.py` (`RepurposeAgent`) | Standalone (NEW — no worker) | `skills/repurpose-agent.md` | ok | NEW |

## How work flows

1. Boss / Main CEO Bot → Content Chief → task type `growth_research` or
   `repurpose_plan` (Phase 7 — SECTION_ROUTING).
2. `growth_research` → GrowthAgent (standalone, brain.complete) → trend-research
   DRAFT + collab-outreach DRAFT. Sending outreach needs Boss's "send" — Boss
   sends it himself.
3. `repurpose_plan` → RepurposeAgent (standalone, brain.complete) →
   long-video-to-shorts plan DRAFT + missing-inputs list (source video file/link
   + transcript). PLAN ONLY — no short is made.
4. The result returns to the Main CEO Bot → Boss's gate word — only then do the plan/produce sections
   work.

## Gate

- `send` — sending collab-outreach (Growth Agent).
- `ok` — repurpose plan approval.

## Honest limits

- **No trend is invented** — mock brain output is a [MOCK DRAFT] scaffold;
  real trend data needs Boss's input.
- **No collab has happened yet, no outreach has been sent.**
- **There is no long video yet** — Week 1 long video ("Google's Nano Banana 2 Is
  Free - But Is It Good?") READY TO RECORD, Boss's OBS recording is pending. So
  the Repurpose Agent only makes a PLAN; stage 5-edit is BLOCKED (no transcript).
- **13 stages: REAL 0 / MOCK 10 / BLOCKED 3** — growth work is MOCK/plan only.
- Upload OFF — this section uploads nothing.
