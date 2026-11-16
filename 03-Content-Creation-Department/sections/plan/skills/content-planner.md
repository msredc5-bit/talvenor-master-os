# Skill: Content Planner

**Role:** Content Planner — Plan section-এর weekly/monthly plan বানানো। Agent: `ContentPlannerAgent` (`sections/plan/agents/content_planner.py`, task_kind `plan_weekly`, gate `ok`)। Worker: নেই — Chief-level role।
**Chief task type:** `plan_weekly` (Phase 7 — নতুন)। **Stage:** 0b-plan + 10-next-plan — MOCK।
**Method-এর source:** `youtube-skills/yt-plan/SKILL.md` (সপ্তাহের plan — anchor video + cheap video, Boss-এর আসল ঘণ্টা জিজ্ঞেস করে) + `scripts/loop_next.py` (stage 10-next-plan — আগের report পড়ে পরের brief) + `pipeline.md`।

## Input

- আগের সপ্তাহের report (থাকলে)
- Boss-এর দেওয়া ঘণ্টা (সপ্তাহে কত ঘণ্টা দেবেন)
- half-made content-এর list, niche/topic

## Method (step-by-step)

1. Boss-এর আসল ঘণ্টা জিজ্ঞেস করো — ঘণ্টা না জেনে plan বানিও না। Anchor video (long) + cheap video (Shorts) — দুটোই plan-এ রাখো।
2. ToolPilot rhythm ধরো: **১ long/week (Sat 10 AM ET = Sat 9 PM Dhaka) + ২ Shorts/week (Wed + Fri 9 AM ET = 8 PM Dhaka)**।
3. Talvenor weekly social (৫ post) একই plan-এ রাখো — Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn (LinkedIn = Boss নিজে post করেন, personal profile)।
4. Table বানাও: pillar + format + platform + posting time।
5. আগের report থাকলে সেটা পড়ে পরের brief লেখো (stage 10-next-plan) — report না থাকলে সেটা বলো, বানিও না।
6. Plan-এর ভেতরে কোনো metric/claim invent করো না। Output-এ `[MOCK DRAFT]` লিখো।

## Output format

```
[MOCK DRAFT] — Weekly plan (week: ... | Boss-এর ঘণ্টা: ...)
| Day | Pillar | Format | Platform | Posting time |
| Mon | ... | Reel | ... | ... |
| Tue | ... | Carousel | ... | ... |
| Wed | ... | Short | YouTube | 9 AM ET / 8 PM Dhaka |
| Fri | ... | Short | YouTube | 9 AM ET / 8 PM Dhaka |
| Sat | ... | Long | YouTube | 10 AM ET / 9 PM Dhaka |
```

## Gate

`ok` — Boss-এর "ok" বা edit ছাড়া plan চলে না।

## সৎ সীমা

- **Nov 16–22 Talvenor weekly plan (৫ post: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) 2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" এখনো বাকি।** Nov 9–15-এ কিছু post হয়নি (plan approve হয়নি)।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, verdict [FILL AFTER TEST]।
- কোনো plan-ই approved বলে দাবি করা হয় না — "ok" না আসা পর্যন্ত সব draft।
