# Skill: Repurpose Agent

**Role:** Repurpose Agent — Growth section-এর long-video-to-shorts plan। Agent: `RepurposeAgent` (`sections/growth/agents/repurpose_agent.py`, task_kind `repurpose_plan`, gate `ok`)। Worker: নেই — NEW role (Phase 7)।
**Chief task type:** `repurpose_plan` (Phase 7 — নতুন)। **Stage:** 5-edit-এর shorts-ধারা (yt-edit — shorts) — BLOCKED (transcript লাগে, এখনো কোনো transcript নেই)।

## Input

- source video file/link (long video — থাকলে)
- transcript (থাকলে)

## Method (step-by-step)

1. Source video না থাকলে missing-inputs list লেখো — plan বানানো যাবে, short বানানো যাবে না।
2. Long video-র moment গুলো চিহ্নিত করো — hook moment, best reveal, funniest fail — প্রতিটার hook + length + caption note সহ।
3. Week 1 উদাহরণ (আসল): Long video "Google's Nano Banana 2 Is Free - But Is It Good?" (~৯.৫ min, ৫ test) — Short 1: Figurine edit moment; Short 2: Background test moment।
4. প্রতিটা Short-এর জন্য: hook (প্রথম ২ সেকেন্ড), length (১৫–৩০ sec), caption note।
5. কোনো short বানানো হয়েছে বলে দাবি করো না — PLAN ONLY। কোনো invented client / stat / testimonial / price লিখো না।
6. Output-এ `[MOCK DRAFT]` লিখো।

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

`ok` — Boss-এর "ok" ছাড়া plan ব্যবহার করা যাবে না।

## সৎ সীমা

- **কোনো long video এখনো নেই** — Week 1 long video ("Google's Nano Banana 2 Is Free - But Is It Good?") READY TO RECORD, Boss-এর OBS recording বাকি। তাই এই role শুধু PLAN বানায়।
- **Stage 5-edit BLOCKED** — transcript লাগে, এখনো কোনো transcript নেই।
- Shorts plan-এর moment গুলো শুধু plan — কোনো short render/edit/publish করা হয়নি।
