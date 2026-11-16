# Section: Growth (বৃদ্ধি)

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (Chief-এর ৬ worker routing-এর উপরে, বদলে নয়)

## উদ্দেশ্য (Purpose)

Channel বড় করা — trend research + collab-outreach draft (Growth Agent) আর
long video-কে Shorts-এ ভাগ করার plan (Repurpose Agent)। দুটোই Phase 7-এ
NEW role — আগে engine-এ এদের কোনো staff/worker/skill ছিল না।

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Growth Agent | `agents/growth_agent.py` (`GrowthAgent`) | Standalone (NEW — no worker) | `skills/growth-agent.md` | send | NEW |
| Repurpose Agent | `agents/repurpose_agent.py` (`RepurposeAgent`) | Standalone (NEW — no worker) | `skills/repurpose-agent.md` | ok | NEW |

## কাজের প্রবাহ (How work flows)

1. Boss / Main CEO Bot → Content Chief → task type `growth_research` বা
   `repurpose_plan` (Phase 7 — SECTION_ROUTING)।
2. `growth_research` → GrowthAgent (standalone, brain.complete) → trend-research
   DRAFT + collab-outreach DRAFT। Outreach পাঠাতে Boss-এর "send" লাগে — পাঠানো
   Boss নিজে করেন।
3. `repurpose_plan` → RepurposeAgent (standalone, brain.complete) →
   long-video-to-shorts plan DRAFT + missing-inputs list (source video file/link
   + transcript)। PLAN ONLY — কোনো short বানানো হয় না।
4. ফলাফল Main CEO Bot-এ ফেরে → Boss-এর gate word — তারপরেই plan/produce section
   কাজ করে।

## Gate

- `send` — collab-outreach পাঠানো (Growth Agent)।
- `ok` — repurpose plan approval।

## সৎ সীমা (Honest limits)

- **কোনো trend invent করা হয় না** — mock brain output [MOCK DRAFT] scaffold;
  আসল trend data-র জন্য Boss-এর input লাগে।
- **কোনো collab এখনো হয়নি, কোনো outreach পাঠানো হয়নি।**
- **কোনো long video এখনো নেই** — Week 1 long video ("Google's Nano Banana 2 Is
  Free - But Is It Good?") READY TO RECORD, Boss-এর OBS recording বাকি। তাই
  Repurpose Agent শুধু PLAN বানায়; stage 5-edit BLOCKED (transcript নেই)।
- **১৩ stage: REAL 0 / MOCK 10 / BLOCKED 3** — growth কাজ MOCK/plan মাত্র।
- Upload OFF — এই section কিছু upload করে না।
