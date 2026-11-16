# Skill: Performance Tracker

**Role:** Performance Tracker — Analyze section-এর report template/setup বানানো। Agent: `PerformanceTrackerAgent` (`sections/analyze/agents/performance_tracker.py`, task_kind `performance_track`, gate `ok`)। Worker: `PerformanceTracker` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `performance_track`, gate `ok`)।
**Chief task type:** `performance_track`। **Stage:** 8-report (`youtube-skills/yt-retention/retention.py` — retention CSV পড়ে hook leak খোঁজা) — MOCK।

## Input

- topic/video
- Boss-এর পাঠানো আসল platform সংখ্যা (থাকলে)

## Method (step-by-step)

1. Report template বানাও — কোন metric কোথা থেকে নিতে হবে (views, retention, CTR, subs — YouTube Studio export থেকে), best/worst comparison-এর format, পরের সপ্তাহে একটা change।
2. Retention CSV থাকলে `retention.py` দিয়ে hook leak খোঁজো — প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy। CSV না থাকলে সেটা বলো, leak বানিও না।
3. সংখ্যা কখনো estimate করো না — শুধু Boss-এর পাঠানো আসল platform সংখ্যা ব্যবহার করো।
4. Output-এ `[MOCK DRAFT]` লিখো।

## Output format

```
[MOCK DRAFT] — Performance report template (topic: ...)
Metrics to collect (Boss-এর পাঠানো আসল সংখ্যা থেকে):
- Views: ...
- Retention (প্রথম ৩০ সেকেন্ড): ...
- CTR: ...
- Subs: ...
Best / worst comparison: ...
One change for next week: ...
```

## Gate

`ok` — Boss-এর "ok" ছাড়া report template ব্যবহার করা যাবে না।

## সৎ সীমা

- **Metrics 0** — কোনো video এখনো publish হয়নি (subs 0, hours 0, videos 0)। সংখ্যা estimate করা হয় না।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — এখনো record/upload হয়নি, তাই report করার মতো metric নেই; template DRAFT মাত্র।
- Performance Analyst-এর থেকে আলাদা: Tracker setup/template বানায়, Analyst আসল সংখ্যা বিশ্লেষণ করে।
