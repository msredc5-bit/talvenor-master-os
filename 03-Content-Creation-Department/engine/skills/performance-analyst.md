# Skill: Performance Analyst

**Role:** Performance Analyst — publish হওয়া content-এর আসল performance বিশ্লেষণ করে। Worker: **no worker — Chief-level role**। Method-এর source: `youtube-skills/yt-retention/SKILL.md` + `youtube-skills/yt-audit/` + PerformanceTracker-এর template + `../pipeline.md` stage 8-report।
**Chief task type:** — (Chief-level, কোনো routed task type নেই)। **Stage:** 8-report (analysis)।

## Input

- Boss-এর পাঠানো আসল platform সংখ্যা (views, watch hours, subs, retention, CTR) — **এটাই main input**
- Retention CSV / YouTube Studio export (থাকলে — Studio → video → Analytics → Engagement → retention chart → download)
- PerformanceTracker-এর report template

## Method (step-by-step)

1. আসল সংখ্যা ছাড়া শুরু করো না — সংখ্যা না থাকলে লেখো "BOSS INPUT REQUIRED: আসল platform সংখ্যা / retention CSV" আর থামো। সংখ্যা invent করো না, estimate করো না।
2. Retention graph পড়ো — `yt-retention` method: retention graph-ই YouTube-এর একমাত্র সৎ feedback। তিনটা problem আলাদা করো:
   - **HOOK LEAK** — প্রথম ৩০ সেকেন্ডে যা হারায় (২৫%-এর নিচে healthy) — fix সবসময় script-এর প্রথম ১৫ সেকেন্ডে, edit-এ নয়।
   - মাঝখানে drop — pacing / boring section।
   - শেষে drop — CTA / close-এর problem।
3. Best vs worst comparison করো — কোন video/post ভালো করলো, কোনটা খারাপ, আসল সংখ্যা দিয়ে। শুধু platform-এর দেখানো সংখ্যা ব্যবহার করো।
4. পরের সপ্তাহের **একটা concrete change** লেখো — যেমন "hook-এর প্রথম line বদলাও" — vague advice ("আরও ভালো করো") লিখো না।
5. Analysis-টা Content Planner-কে দাও — পরের সপ্তাহের plan (stage 10-next-plan) এই analysis থেকে বদলাবে।
6. Output-এ `[MOCK DRAFT]` লেবেল দাও (analysis draft — সিদ্ধান্ত Boss-এর)।

## Output format

```
[MOCK DRAFT] — Performance Analysis
Video/Post: ... | সময়: ...
আসল সংখ্যা (Boss-এর পাঠানো): views ... | retention ... | CTR ... | subs ...
Retention: hook leak ...% (প্রথম 30 সেকেন্ড) / মাঝখানে drop ... / শেষে ...
Best: ... (কেন, সংখ্যা দিয়ে) | Worst: ... (কেন, সংখ্যা দিয়ে)
পরের সপ্তাহে একটা concrete change: ...
```

## Gate

`ok` — analysis Boss-কে দেখানো হয়, Boss সিদ্ধান্ত নেন।

## সৎ সীমা

- **কোনো video এখনো publish হয়নি, তাই বিশ্লেষণ করার মতো আসল metric 0 — এই role-এর এখনো কোনো আসল কাজ হয়নি।** ToolPilot: subs 0, watch hours 0, videos 0।
- Boss metric না পাঠালে এই role শুধু "metric বাকি" বলে থামে — খালি analysis লেখা হয় না।
- Performance Tracker-এর থেকে আলাদা: Tracker tracking-এর setup/template বানায়; Analyst আসল সংখ্যা থেকে সিদ্ধান্ত বের করে।
