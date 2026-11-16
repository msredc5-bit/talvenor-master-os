# Section: Plan (পরিকল্পনা)

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (Chief-এর ৬ worker routing-এর উপরে, বদলে নয়)

## উদ্দেশ্য (Purpose)

কী বানানো হবে, কখন বানানো হবে — সেটা ঠিক করা। Topic বাছা (stage 1-research)
আর weekly plan বানানো (stage 0b-plan + 10-next-plan) — এই section-এর কাজ।
Plan শুধু draft — Boss-এর "ok" ছাড়া কিছু চলে না।

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Topic Researcher | `agents/topic_researcher.py` (`TopicResearcherAgent`) | `TopicResearcher` (vendored) | `skills/topic-researcher.md` | ok | WRAPPED |
| Content Planner | `agents/content_planner.py` (`ContentPlannerAgent`) | Standalone (no worker — Chief-level role) | `skills/content-planner.md` | ok | WRAPPED* |

\* Content Planner-এর কোনো vendored worker নেই — Chief-level role, তাই Phase 7-এ
standalone agent হিসেবে বানানো হয়েছে (আগে শুধু `engine/skills/content-planner.md`
skill ছিল, agent ছিল না)।

## কাজের প্রবাহ (How work flows)

1. Boss / Main CEO Bot → Content Chief (`chief_of_staff_content.py`) → task type
   `content_plan` (TopicResearcher) বা `plan_weekly` (ContentPlannerAgent)।
2. `content_plan` → vendored TopicResearcher worker (mock brain, $0) → ৩টি topic draft।
3. `plan_weekly` → ContentPlannerAgent (standalone, brain.complete) → weekly plan
   DRAFT (pillar + format + platform + posting time)।
4. ফলাফল Main CEO Bot-এ ফেরে → Boss-এর "ok" বা edit — তারপরেই পরের section
   (produce) কাজ শুরু করে।

## Gate

- `ok` — plan / topic approval। Boss-এর exact word ছাড়া কোনো plan চলে না।

## সৎ সীমা (Honest limits)

- **১৩ stage: REAL 0 / MOCK 10 / BLOCKED 3** — plan section-এর stage গুলো MOCK।
- **Nov 16–22 Talvenor weekly plan (৫ post: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) 2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" এখনো বাকি।** কোনো plan-ই approved বলে দাবি করা হয় না।
- Mock brain — আসল trend data পড়ে না; score scaffold মাত্র।
- ToolPilot rhythm: ১ long/week (Sat 10 AM ET) + ২ Shorts/week (Wed + Fri 9 AM ET)।
- Upload OFF — এই section কিছু upload করে না।
