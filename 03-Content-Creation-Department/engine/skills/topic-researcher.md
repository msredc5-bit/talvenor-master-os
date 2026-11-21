# Skill: Topic Researcher

**Role:** Topic Researcher — the Content Engine's researcher. Worker: `TopicResearcher` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `topic_research`, gate `ok`).
**Chief task type:** `content_plan`. **Stage:** 1-research (+ 0a-niche, 2a-concept).

## Input

- niche — e.g. "AI Tools & Tutorials" (ToolPilot's niche, known)
- audience — e.g. US viewers (faceless, screen recording + AI voiceover)
- Boss's trend / topic if given (if not, this is not "BOSS INPUT REQUIRED" — the researcher picks topics himself, but Boss's trend comes first if there is one)

## Method (step-by-step)

1. Confirm the niche — ToolPilot's niche is fixed: AI Tools & Tutorials. To pick a new niche, use `youtube-skills/yt-niche/SKILL.md` + `tools/niche_score.py` — score 1–10 on 4 axes (demand, competition gap, monetization, fresher-fit) and rank. If the topic is known, stage 0a is skipped.
2. Write the audience in one line — who will watch, with what problem (e.g.: US viewer, wants to test a free AI tool).
3. Pick 3 topics — for each: angle (which side it is told from), why it fits this niche/audience, and what the next research step is (which test / which source to look at).
4. Score the concepts — the `tools/concept_score.py` method: 3–5 concepts, 1–10 score. Write the reason for the score in one line, do not invent scores — never give a score without a reason.
5. Do not invent any stat / result / source — if a fact is missing, write what input is needed ("BOSS INPUT REQUIRED" where Boss's input is really needed, e.g. a real test result).
6. Label the output `[MOCK DRAFT]` — mock brain ($0) scaffold.

## Output format

```
[MOCK DRAFT] — Topic Research
Niche: ...
Audience: ...
1. Topic: ... | Angle: ... | Why it fits: ... | Next research: ...
2. ...
3. ...
Concept scores: (concept — score/10 — reason)
Missing input: ... / none
```

## Gate

`ok` — no topic is final without Boss's "ok"; it does not go to script.

## Honest limits

- Mock brain — it does not read real trend data / YouTube search; scores are a scaffold only.
- No video has been published, so topics cannot be learned from an earlier video's performance — metrics 0.
- The Track 3 question (ToolPilot or a brand-new channel) is still unanswered — no topics for a new channel will be picked, work with ToolPilot.
