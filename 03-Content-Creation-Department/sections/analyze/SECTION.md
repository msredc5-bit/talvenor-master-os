# Section: Analyze (বিশ্লেষণ)

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (Chief-এর ৬ worker routing-এর উপরে, বদলে নয়)

## উদ্দেশ্য (Purpose)

Publish হওয়া content কেমন করল, সেটা জানা — report template/setup (stage
8-report) আর আসল সংখ্যার বিশ্লেষণ। দুটো আলাদা কাজ: Tracker setup বানায়,
Analyst আসল সংখ্যা থেকে সিদ্ধান্ত বের করে।

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Performance Tracker | `agents/performance_tracker.py` (`PerformanceTrackerAgent`) | `PerformanceTracker` (vendored) | `skills/performance-tracker.md` | ok | WRAPPED |
| Performance Analyst | `agents/performance_analyst.py` (`PerformanceAnalystAgent`) | Standalone (no worker — Chief-level role) | `skills/performance-analyst.md` | ok | WRAPPED* |

\* Performance Analyst-এর কোনো vendored worker নেই — Chief-level role, তাই Phase 7-এ
standalone agent হিসেবে বানানো হয়েছে (আগে শুধু `engine/skills/performance-analyst.md`
skill ছিল, agent ছিল না)।

## কাজের প্রবাহ (How work flows)

1. Boss / Main CEO Bot → Content Chief → task type `performance_track` বা
   `performance_analyze`।
2. `performance_track` → vendored PerformanceTracker worker (mock brain, $0) →
   report template DRAFT (metric-এর list + comparison format + একটা change)।
3. `performance_analyze` → PerformanceAnalystAgent (standalone) → Boss-এর পাঠানো
   আসল সংখ্যা থাকলে analysis DRAFT; সংখ্যা না থাকলে "no metrics yet — Boss's
   numbers needed" বলে থামে।
4. ফলাফল Main CEO Bot-এ ফেরে → Boss সিদ্ধান্ত নেন (gate "ok") → পরের plan-এ
   একটা concrete change যায় (stage 10-next-plan)।

## Gate

- `ok` — report template / analysis Boss-কে দেখানো হয়, Boss সিদ্ধান্ত নেন।

## সৎ সীমা (Honest limits)

- **Metrics 0** — কোনো video এখনো publish হয়নি (subs 0, hours 0, videos 0)।
  সংখ্যা কখনো estimate করা হয় না — শুধু Boss-এর পাঠানো আসল platform সংখ্যা
  ব্যবহার করা হয়।
- **Performance Analyst-এর এখনো কোনো আসল কাজ হয়নি** — বিশ্লেষণ করার মতো আসল
  metric 0; Boss metric না পাঠালে agent শুধু "metric বাকি" বলে থামে।
- Retention: প্রথম ৩০ সেকেন্ডে ২৫%-এর নিচে healthy (yt-retention) — CSV না
  থাকলে leak বানানো হয় না।
- Upload OFF — এই section কিছু upload করে না।
