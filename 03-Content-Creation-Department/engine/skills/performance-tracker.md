# Skill: Performance Tracker

**Role:** Performance Tracker — Content Engine-এর tracking setup বানায়। Worker: `PerformanceTracker` (`~/workspace/creator-os-combined/src/creator_workers.py`, task_kind `performance_track`, gate `ok`)।
**Chief task type:** `performance_track`। **Stage:** 8-report (`youtube-skills/yt-retention/retention.py`)।

## Input

- topic / video (publish হওয়া বা হতে যাওয়া)
- Boss-এর পাঠানো আসল platform সংখ্যা (থাকলে — না থাকলে template-ই output, সংখ্যা invent করা হবে না)

## Method (step-by-step)

1. Tracking setup লেখো — কোন platform থেকে কোন metric নিতে হবে:
   - YouTube: views, watch hours, subs, retention, CTR
   - Facebook / Instagram / LinkedIn: reach, engagement, link click (যা platform আসলে দেখায়)
2. Report template বানাও — best performer vs worst performer-এর comparison format + পরের সপ্তাহে **একটা** change-এর জায়গা।
3. Retention-এর জন্য: `yt-retention` method — YouTube Studio → video → Analytics → Engagement → audience-retention chart → download ("Audience retention") CSV; `retention.py retention.csv --duration 600` দিয়ে hook leak খোঁজা। CSV না থাকলে retention analysis লিখো না — "BOSS INPUT REQUIRED: retention CSV" লেখো।
4. সংখ্যা কখনো estimate করো না — শুধু Boss-এর পাঠানো আসল platform সংখ্যা ব্যবহার করো। সংখ্যা না থাকলে metric-এর ঘর **0 / খালি** রাখো, বানানো সংখ্যা বসাবে না।
5. Output-এ `[MOCK DRAFT]` লেবেল দাও। এটা template/setup — analysis নয় (analysis Performance Analyst-এর কাজ)।

## Output format

```
[MOCK DRAFT] — Performance Report Template
Topic/Video: ...
Metrics to collect:
- YouTube: views / watch hours / subs / retention / CTR — Boss-এর পাঠানো সংখ্যা
- Facebook: ...
- Instagram: ...
- LinkedIn: ...
Best performer: ... (আসল সংখ্যা পেলে)
Worst performer: ... (আসল সংখ্যা পেলে)
One change for next week: ...
```

## Gate

`ok` — Boss-এর "ok" ছাড়া template ব্যবহার করা যাবে না।

## সৎ সীমা

- **কোনো video এখনো publish হয়নি — metric 0** (ToolPilot: subs 0, watch hours 0, videos 0)। তাই এখন এই role শুধু template দিতে পারে, report দিতে পারে না।
- Retention CSV / Studio export Boss-কে পাঠাতে হবে — export ছাড়া retention analysis হয় না।
- Performance Analyst-এর থেকে আলাদা: Tracker setup/template বানায়; Analyst আসল সংখ্যা বিশ্লেষণ করে সিদ্ধান্ত বের করে।
