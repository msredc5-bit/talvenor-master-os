# Skill: Content Planner

**Role:** Content Planner — making the Plan section's weekly/monthly plan. Agent: `ContentPlannerAgent` (`sections/plan/agents/content_planner.py`, task_kind `plan_weekly`, gate `ok`). Worker: none — Chief-level role.
**Chief task type:** `plan_weekly` (Phase 7 — new). **Stage:** 0b-plan + 10-next-plan — MOCK.
**Method source:** `youtube-skills/yt-plan/SKILL.md` (weekly plan — anchor video + cheap video, asks for Boss's real hours) + `scripts/loop_next.py` (stage 10-next-plan — reads the previous report and writes the next brief) + `pipeline.md`.

## Input

- last week's report (if there is one)
- Boss's hours (how many hours a week he will give)
- list of half-made content, niche/topic

## Method (step-by-step)

1. Ask for Boss's real hours — do not make a plan without knowing the hours. Anchor video (long) + cheap video (Shorts) — keep both in the plan.
2. Take the ToolPilot rhythm: **1 long/week (Sat 10 AM ET = Sat 9 PM Dhaka) + 2 Shorts/week (Wed + Fri 9 AM ET = 8 PM Dhaka)**.
3. Keep the Talvenor weekly social (5 posts) in the same plan — Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn (LinkedIn = Boss posts himself, personal profile).
4. Make a table: pillar + format + platform + posting time.
5. If there is a previous report, read it and write the next brief (stage 10-next-plan) — if there is none, say so, do not make one up.
6. Do not invent any metric/claim inside a plan. Write `[MOCK DRAFT]` in the output.

## Output format

```
[MOCK DRAFT] — Weekly plan (week: ... | Boss's hours: ...)
| Day | Pillar | Format | Platform | Posting time |
| Mon | ... | Reel | ... | ... |
| Tue | ... | Carousel | ... | ... |
| Wed | ... | Short | YouTube | 9 AM ET / 8 PM Dhaka |
| Fri | ... | Short | YouTube | 9 AM ET / 8 PM Dhaka |
| Sat | ... | Long | YouTube | 10 AM ET / 9 PM Dhaka |
```

## Gate

`ok` — no plan runs without Boss's "ok" or edits.

## Honest limits

- **Nov 16–22 Talvenor weekly plan (5 posts: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) was given 2026-11-15 18:00 — Boss's "ok" is still pending.** Nothing was posted Nov 9–15 (the plan was not approved).
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, verdict [FILL AFTER TEST].
- No plan is claimed to be approved — everything is a draft until "ok" comes.
