# Skill: Topic Researcher

**Role:** Topic Researcher — topic picker for the Plan section. Agent: `TopicResearcherAgent` (`sections/plan/agents/topic_researcher.py`, task_kind `content_plan`, gate `ok`). Worker: `TopicResearcher` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `topic_research`, gate `ok`).
**Chief task type:** `content_plan`. **Stage:** 1-research (+ 0a-niche, 2a-concept) — MOCK.

## Input

- niche (e.g. "AI Tools & Tutorials"), audience (US viewers)
- Boss's trend/topic if given
- last week's report (if there is one — from stage 10-next-plan)

## Method (step-by-step)

1. If the niche is known, stage 0a-niche is skipped — pick topics directly. If there is no niche, check the niche with `tools/niche_score.py` (1–10 score on 4 axes).
2. Take the CEO's decision and pick **3 content topics** for the niche + audience — each one's angle, why it fits, and what the next research step is.
3. For each topic write 3–5 concepts, score them 1–10 with `concept_score.py` (stage 2a-concept) — scores are a scaffold only, not real trend data.
4. Do not write any invented client / testimonial / case study / stat / price.
5. Write `[MOCK DRAFT]` in the output — mock brain ($0), no real trend data was read.

## Output format

```
[MOCK DRAFT] — Topic research (niche: ... | audience: ...)
1. Topic: "..."
   Angle: ...
   Why it fits: ...
   Next research step: ...
2. Topic: "..."
   ...
3. Topic: "..."
   ...
```

## Gate

`ok` — no topic is final without Boss's "ok".

## Honest limits

- **Mock brain** — it does not read real trend data; scores are a scaffold only.
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" (48 chars, title lint 100/100; thumbnail text "5 EDITS TESTED") — READY TO RECORD, verdict [FILL AFTER TEST].
- If the niche is known, stage 0a is skipped.
