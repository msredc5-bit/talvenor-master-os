# Skill: Topic Researcher

**Role:** Topic Researcher — Plan section-এর topic বাছাইকারী। Agent: `TopicResearcherAgent` (`sections/plan/agents/topic_researcher.py`, task_kind `content_plan`, gate `ok`)। Worker: `TopicResearcher` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `topic_research`, gate `ok`)।
**Chief task type:** `content_plan`। **Stage:** 1-research (+ 0a-niche, 2a-concept) — MOCK।

## Input

- niche (যেমন "AI Tools & Tutorials"), audience (US viewers)
- Boss-এর দেওয়া trend/topic থাকলে সেটা
- আগের সপ্তাহের report (থাকলে — stage 10-next-plan থেকে)

## Method (step-by-step)

1. Niche জানা থাকলে 0a-niche stage skip হয় — সরাসরি topic বাছো। Niche না থাকলে `tools/niche_score.py` (৪ axis-এ ১–১০ score) দিয়ে niche যাচাই করো।
2. CEO-র সিদ্ধান্ত নিয়ে niche + audience-এর জন্য **৩টি content topic** বাছো — প্রতিটার angle, কেন fit করে, আর পরের research step কী।
3. প্রতিটা topic-এর জন্য ৩–৫ concept লেখো, `concept_score.py` দিয়ে ১–১০ score করো (stage 2a-concept) — score scaffold মাত্র, আসল trend data নয়।
4. কোনো invented client / testimonial / case study / stat / price লিখো না।
5. Output-এ `[MOCK DRAFT]` লিখো — mock brain ($0), আসল trend data পড়া হয়নি।

## Output format

```
[MOCK DRAFT] — Topic research (niche: ... | audience: ...)
1. Topic: "..."
   Angle: ...
   কেন fit করে: ...
   পরের research step: ...
2. Topic: "..."
   ...
3. Topic: "..."
   ...
```

## Gate

`ok` — Boss-এর "ok" ছাড়া topic final নয়।

## সৎ সীমা

- **Mock brain** — আসল trend data পড়ে না; score scaffold মাত্র।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" (48 chars, title lint 100/100; thumbnail text "5 EDITS TESTED") — READY TO RECORD, verdict [FILL AFTER TEST]।
- Niche জানা থাকলে 0a stage skip হয়।
