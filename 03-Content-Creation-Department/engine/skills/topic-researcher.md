# Skill: Topic Researcher

**Role:** Topic Researcher — Content Engine-এর researcher। Worker: `TopicResearcher` (`~/workspace/creator-os-combined/src/creator_workers.py`, task_kind `topic_research`, gate `ok`)।
**Chief task type:** `content_plan`। **Stage:** 1-research (+ 0a-niche, 2a-concept)।

## Input

- niche — যেমন "AI Tools & Tutorials" (ToolPilot-এর niche, জানা আছে)
- audience — যেমন US viewers (faceless, screen recording + AI voiceover)
- Boss-এর দেওয়া trend / topic থাকলে সেটা (না থাকলে "BOSS INPUT REQUIRED" নয় — researcher নিজে topic বাছে, কিন্তু Boss-এর trend থাকলে সেটা আগে)

## Method (step-by-step)

1. Niche confirm করো — ToolPilot-এর niche fixed: AI Tools & Tutorials। নতুন niche বাছতে হলে `youtube-skills/yt-niche/SKILL.md` + `tools/niche_score.py` — ৪ axis (demand, competition gap, monetization, fresher-fit)-এ ১–১০ score করে rank করো। Topic জানা থাকলে 0a stage skip হয়।
2. Audience-কে এক লাইনে লেখো — কে দেখবে, কী problem নিয়ে দেখবে (যেমন: US viewer, free AI tool test করতে চায়)।
3. ৩টি topic বাছো — প্রতিটার জন্য: angle (কোন দিক থেকে বলা হবে), কেন এই niche/audience-এ fit করে, আর পরের research step কী (কী test / কী source দেখতে হবে)।
4. Concept score করো — `tools/concept_score.py` method: ৩–৫ concept, ১–১০ score। Score-এর কারণ এক লাইনে লেখো, score invent করো না — কারণ ছাড়া score দেবে না।
5. কোনো stat / result / source invent করো না — fact missing থাকলে লেখো কী input লাগবে ("BOSS INPUT REQUIRED" যেখানে Boss-এর input সত্যিই দরকার, যেমন আসল test result)।
6. Output-এ `[MOCK DRAFT]` লেবেল দাও — mock brain ($0) scaffold।

## Output format

```
[MOCK DRAFT] — Topic Research
Niche: ...
Audience: ...
1. Topic: ... | Angle: ... | কেন fit: ... | Next research: ...
2. ...
3. ...
Concept scores: (concept — score/10 — কারণ)
Missing input: ... / কিছু না
```

## Gate

`ok` — Boss-এর "ok" ছাড়া topic final নয়, script-এ যাবে না।

## সৎ সীমা

- Mock brain — আসল trend data / YouTube search পড়ে না; score scaffold মাত্র।
- কোনো video publish হয়নি, তাই আগের video-র performance থেকে topic শেখা যায় না — metric 0।
- Track 3 প্রশ্ন (ToolPilot নাকি brand-new channel) এখনো উত্তর হয়নি — নতুন channel-এর topic বাছা হবে না, ToolPilot-ই ধরে কাজ করো।
