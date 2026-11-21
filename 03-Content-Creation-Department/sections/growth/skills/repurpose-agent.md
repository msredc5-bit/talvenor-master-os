# Skill: Repurpose Agent

**Role:** Repurpose Agent — long-video-to-shorts plan for the Growth section. Agent: `RepurposeAgent` (`sections/growth/agents/repurpose_agent.py`, task_kind `repurpose_plan`, gate `ok`). Worker: none — NEW role (Phase 7).
**Chief task type:** `repurpose_plan` (Phase 7 — new). **Stage:** shorts track of 5-edit (yt-edit — shorts) — BLOCKED (needs a transcript, there is no transcript yet).

## Input

- source video file/link (long video — if there is one)
- transcript (if there is one)

## Method (step-by-step)

1. If there is no source video, write a missing-inputs list — a plan can be made, a short cannot.
2. Mark the long video's moments — hook moment, best reveal, funniest fail — each with its hook + length + caption note.
3. Week 1 example (real): Long video "Google's Nano Banana 2 Is Free - But Is It Good?" (~9.5 min, 5 tests) — Short 1: Figurine edit moment; Short 2: Background test moment.
4. For each Short: hook (first 2 seconds), length (15–30 sec), caption note.
5. Do not claim any short was made — PLAN ONLY. Do not write any invented client / stat / testimonial / price.
6. Write `[MOCK DRAFT]` in the output.

## Output format

```
[MOCK DRAFT] — Long-video-to-shorts plan (source: ...)
Missing inputs:
- source video file/link — ...
- transcript — ...
Shorts plan:
1. Short — moment: ... | hook: "..." | length: ... sec | caption note: ...
2. Short — moment: ... | hook: "..." | length: ... sec | caption note: ...
Shorts made: 0 (PLAN ONLY)
```

## Gate

`ok` — the plan may not be used without Boss's "ok".

## Honest limits

- **There is no long video yet** — Week 1 long video ("Google's Nano Banana 2 Is Free - But Is It Good?") is READY TO RECORD, Boss's OBS recording is pending. So this role only makes a PLAN.
- **Stage 5-edit BLOCKED** — needs a transcript, there is no transcript yet.
- The moments in the Shorts plan are only a plan — no short has been rendered/edited/published.
