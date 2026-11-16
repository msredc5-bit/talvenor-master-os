# Skill: Content Planner

**Role:** Content Planner — Content Engine-এর weekly/monthly plan বানায়। Worker: **no worker — Chief-level role**। Method-এর source: `youtube-skills/yt-plan/SKILL.md` + `scripts/loop_next.py` (stage 10-next-plan) + `../pipeline.md`।
**Chief task type:** — (Chief-level, কোনো routed task type নেই)। **Stage:** 0b-plan + 10-next-plan।

## Input

- আগের সপ্তাহের report (থাকলে — এখনো কোনো report নেই, video 0)
- Boss-এর আসল ঘণ্টা — সপ্তাহে কত ঘণ্টা দেবেন (না জানালে plan-এ লেখো "BOSS INPUT REQUIRED: সপ্তাহে কত ঘণ্টা")
- half-made content-এর list (যা অর্ধেক তৈরি আছে — যেমন Week 1 long video READY TO RECORD)
- niche / topic

## Method (step-by-step)

1. Boss-এর ঘণ্টা জিজ্ঞেস করো — `yt-plan` method: plan লেখার আগে দুটো প্রশ্ন — (১) সপ্তাহে আসলে কত ঘণ্টা আছে, (২) কী কী অর্ধেক তৈরি আছে। ঘণ্টার বেশি plan লিখো না — capacity-র বাইরে plan = regret-এর list।
2. **One anchor** বাছো — সপ্তাহের main video, সবচেয়ে বেশি সময় পাবে, channel-এর analytics যে দিন বলে সে দিন যাবে (analytics নেই — তাই ToolPilot rhythm ধরো: long Sat 10:00 AM ET = Sat 9:00 PM Dhaka)।
3. **One cheap one** বাছো — যা আছে তা থেকে: clip, reaction, আগের comment-এর follow-up।
4. ToolPilot rhythm বসাও — ১ long/week + ২ Shorts/week (Shorts: Wed + Fri 9:00 AM ET = 8:00 PM Dhaka)।
5. Talvenor weekly social plan বসাও — ৫ post: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn (LinkedIn = Boss নিজে post করেন)।
6. প্রতিটা post-এ লেখো: pillar + format + platform + best US Eastern posting time।
7. পরের সপ্তাহের plan (stage 10, `loop_next.py`): আগের report পড়ে পরের brief লেখো — report না থাকলে লেখো "আগের report নেই (video 0), তাই পরের brief আগের plan-ই repeat করে"।
8. Output-এ `[MOCK DRAFT]` লেবেল দাও। কোনো metric/claim invent করো না।

## Output format

```
[MOCK DRAFT] — Weekly Plan (তারিখ: ...)
Boss-এর ঘণ্টা: ... | Half-made: ...
Anchor video: ... (দিন + সময় ET/Dhaka)
Shorts: ... | ...
Talvenor 5-post plan:
| দিন | Pillar | Format | Platform | Best time (ET) |
| Mon | ... | Reel | ... | ... |
| Tue | ... | Carousel | ... | ... |
| Wed | ... | Image | ... | ... |
| Thu | ... | Carousel | ... | ... |
| Fri | ... | LinkedIn (Boss নিজে) | ... | ... |
Next-plan note: ...
```

## Gate

`ok` — Boss-এর "ok" বা edit ছাড়া plan চলে না।

## সৎ সীমা

- **Nov 16–22 Talvenor weekly plan (৫ post) 2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" এখনো বাকি।** Approve না হলে কিছু post হয় না।
- Nov 9–15-এ কিছু post হয়নি (plan approve হয়নি) — plan দেওয়া মানেই post হওয়া নয়।
- Track 3 প্রশ্ন (ToolPilot নাকি brand-new channel) উত্তর হয়নি — নতুন channel-এর plan বানানো হবে না।
- আগের report নেই (video 0), তাই stage 10-next-plan এখনো আসল brief লিখতে পারে না।
