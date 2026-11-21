# Section: Plan

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (on top of the Chief's 6 worker routings, not replacing them)

## Purpose

Deciding what to make and when to make it. Picking topics (stage 1-research)
and making the weekly plan (stage 0b-plan + 10-next-plan) — this section's work.
A plan is only a draft — nothing runs without Boss's "ok".

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Topic Researcher | `agents/topic_researcher.py` (`TopicResearcherAgent`) | `TopicResearcher` (vendored) | `skills/topic-researcher.md` | ok | WRAPPED |
| Content Planner | `agents/content_planner.py` (`ContentPlannerAgent`) | Standalone (no worker — Chief-level role) | `skills/content-planner.md` | ok | WRAPPED* |

* Content Planner has no vendored worker — Chief-level role, so in Phase 7 it was made as a
standalone agent (before, there was only the `engine/skills/content-planner.md`
skill, no agent).

## How work flows

1. Boss / Main CEO Bot → Content Chief (`chief_of_staff_content.py`) → task type
   `content_plan` (TopicResearcher) or `plan_weekly` (ContentPlannerAgent).
2. `content_plan` → vendored TopicResearcher worker (mock brain, $0) → 3 topic drafts.
3. `plan_weekly` → ContentPlannerAgent (standalone, brain.complete) → weekly plan
   DRAFT (pillar + format + platform + posting time).
4. The result returns to the Main CEO Bot → Boss's "ok" or edits — only then does the next section
   (produce) start work.

## Gate

- `ok` — plan / topic approval. No plan runs without Boss's exact word.

## Honest limits

- **13 stages: REAL 0 / MOCK 10 / BLOCKED 3** — the plan section's stages are MOCK.
- **Nov 16–22 Talvenor weekly plan (5 posts: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) was given 2026-11-15 18:00 — Boss's "ok" is still pending.** No plan is claimed to be approved.
- Mock brain — it does not read real trend data; scores are a scaffold only.
- ToolPilot rhythm: 1 long/week (Sat 10 AM ET) + 2 Shorts/week (Wed + Fri 9 AM ET).
- Upload OFF — this section uploads nothing.
