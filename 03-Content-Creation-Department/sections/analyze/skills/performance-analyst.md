# Skill: Performance Analyst

**Role:** Performance Analyst — Analyze section-এর আসল সংখ্যার বিশ্লেষণ। Agent: `PerformanceAnalystAgent` (`sections/analyze/agents/performance_analyst.py`, task_kind `performance_analyze`, gate `ok`)। Worker: নেই — Chief-level role।
**Chief task type:** `performance_analyze` (Phase 7 — নতুন)। **Stage:** 8-report (analysis) — MOCK।
**Method-এর source:** `youtube-skills/yt-retention/SKILL.md` (retention graph — hook leak, প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy) + `youtube-skills/yt-audit/` + PerformanceTracker-এর template + `pipeline.md` stage 8-report।

## Input

- Boss-এর পাঠানো আসল platform সংখ্যা / retention CSV / YouTube Studio export

## Method (step-by-step)

1. Metric না থাকলে থামো — "no metrics yet — Boss's numbers needed" লেখো। সংখ্যা ছাড়া analysis লেখা হয় না।
2. আসল metric থাকলে retention graph পড়ো — কোথায় viewer ছাড়ে (hook leak?), প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy কি না।
3. কারণ লেখো — কেন ছাড়ে, শুধু কোথায় ছাড়ে তা নয়।
4. পরের video-তে ঠিক কী বদলাতে হবে — একটা concrete change লেখো।
5. সংখ্যা কখনো estimate/invent করো না — শুধু Boss-এর পাঠানো আসল সংখ্যা।
6. Output-এ `[MOCK DRAFT]` লিখো।

## Output format

```
[MOCK DRAFT] — Performance analysis (video: ...)
Real numbers used (Boss-এর পাঠানো):
- Views: ... | Retention (প্রথম ৩০ সেকেন্ড): ... | CTR: ... | Subs: ...
Where viewers drop off: ...
Why: ...
One concrete change for next week: ...
```

Metric না থাকলে:

```
no metrics yet — Boss's numbers needed
```

## Gate

`ok` — analysis Boss-কে দেখানো হয়, Boss সিদ্ধান্ত নেন।

## সৎ সীমা

- **কোনো video এখনো publish হয়নি, তাই বিশ্লেষণ করার মতো আসল metric 0 — এই role-এর এখনো কোনো আসল কাজ হয়নি।** Boss metric না পাঠালে role শুধু "metric বাকি" বলে থামে।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — এখনো record/upload হয়নি, তাই analysis-এর কিছু নেই।
- Performance Tracker-এর থেকে আলাদা: Tracker tracking-এর setup/template বানায়, Analyst আসল সংখ্যা থেকে সিদ্ধান্ত বের করে।
