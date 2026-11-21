# Skill: Content Planner

**Role:** Content Planner — makes the Content Engine's weekly/monthly plan. Worker: **no worker — Chief-level role**. Method source: `youtube-skills/yt-plan/SKILL.md` + `scripts/loop_next.py` (stage 10-next-plan) + `../pipeline.md`.
**Chief task type:** — (Chief-level, no routed task type). **Stage:** 0b-plan + 10-next-plan.

## Input

- last week's report (if there is one — there is no report yet, videos 0)
- Boss's real hours — how many hours a week he will give (if not told, write in the plan "BOSS INPUT REQUIRED: hours per week")
- list of half-made content (what is half-built — e.g. Week 1 long video READY TO RECORD)
- niche / topic

## Method (step-by-step)

1. Ask for Boss's hours — the `yt-plan` method: before writing a plan, two questions — (1) how many hours are really there in the week, (2) what is half-made. Do not write a plan beyond the hours — a plan beyond capacity is a list of regrets.
2. Pick **one anchor** — the week's main video, it gets the most time, it goes on the day the channel's analytics say (no analytics — so take the ToolPilot rhythm: long Sat 10:00 AM ET = Sat 9:00 PM Dhaka).
3. Pick **one cheap one** — from what exists: a clip, a reaction, a follow-up to an earlier comment.
4. Set the ToolPilot rhythm — 1 long/week + 2 Shorts/week (Shorts: Wed + Fri 9:00 AM ET = 8:00 PM Dhaka).
5. Set the Talvenor weekly social plan — 5 posts: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn (LinkedIn = Boss posts himself).
6. For each post write: pillar + format + platform + best US Eastern posting time.
7. Next week's plan (stage 10, `loop_next.py`): read the previous report and write the next brief — if there is no report, write "no previous report (videos 0), so the next brief repeats the previous plan".
8. Label the output `[MOCK DRAFT]`. Do not invent any metric/claim.

## Output format

```
[MOCK DRAFT] — Weekly Plan (date: ...)
Boss's hours: ... | Half-made: ...
Anchor video: ... (day + time ET/Dhaka)
Shorts: ... | ...
Talvenor 5-post plan:
| Day | Pillar | Format | Platform | Best time (ET) |
| Mon | ... | Reel | ... | ... |
| Tue | ... | Carousel | ... | ... |
| Wed | ... | Image | ... | ... |
| Thu | ... | Carousel | ... | ... |
| Fri | ... | LinkedIn (Boss himself) | ... | ... |
Next-plan note: ...
```

## Gate

`ok` — no plan runs without Boss's "ok" or edits.

## Honest limits

- **Nov 16–22 Talvenor weekly plan (5 posts) was given 2026-11-15 18:00 — Boss's "ok" is still pending.** Nothing is posted until approved.
- Nothing was posted Nov 9–15 (the plan was not approved) — giving a plan does not mean posting happened.
- The Track 3 question (ToolPilot or a brand-new channel) is unanswered — no plan for a new channel will be made.
- There is no previous report (videos 0), so stage 10-next-plan cannot write a real brief yet.
