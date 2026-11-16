# Skill: Visual Producer

**Role:** Visual Producer — Produce section-এর visual plan বানানো। Agent: `VisualProducerAgent` (`sections/produce/agents/visual_producer.py`, task_kind `video_produce`, gate `ok`)। Worker: `VisualProducer` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `visual_produce`, gate `ok`)।
**Chief task type:** `video_produce`। **Stage:** 3-visual-pack (`youtube-skills/yt-package/title.py` — title + thumbnail একসাথে lint করা) + 4-video-র production plan — MOCK।

## Input

- topic, format (short video / long video)
- script (থাকলে)
- footage / voiceover line / GPU নাম (থাকলে)

## Method (step-by-step)

1. Visual plan বানাও — shot list, thumbnail idea, on-screen text (verbatim, ছোট, readable)।
2. Title + thumbnail একসাথে lint করো (`title.py`) — Week 1 উদাহরণ: title "Google's Nano Banana 2 Is Free - But Is It Good?" (48 chars, title lint 100/100), thumbnail text "5 EDITS TESTED"।
3. Stage 4-video-র production plan + missing-inputs checklist লেখো — ঠিক কী কী input বাকি (footage / voiceover line / GPU নাম)।
4. Real footage first — কোনো shot film করা না গেলে সেটা বলো, fake করো না।
5. Output-এ `[MOCK DRAFT]` লিখো। `video_file` সবসময় **None** — এই role video file বানায় না।

## Output format

```
[MOCK DRAFT] — Visual plan (topic: ... | format: ...)
Shot list:
1. ... (on-screen text: "...")
2. ...
Thumbnail idea: "..." (text: "...")
Stage 4 — missing inputs:
- footage — ...
- voiceover lines / script — ...
- Boss-এর PC GPU নাম — ...
video_file: None (Stage 4 BLOCKED — video render করা হয়নি)
```

## Gate

`ok` — Boss-এর "ok" ছাড়া visual plan ব্যবহার করা যাবে না।

## সৎ সীমা

- **Stage 4 BLOCKED** — real footage / OBS recording নেই, Boss-এর PC GPU-র নাম **2026-11-01 থেকে জানা যায়নি** (true AI video motion-এর জন্য লাগে), AI video generation এখানে **REGION-BLOCKED — retry করা হয় না**। Default stills + Ken Burns motion = সত্যিকারের motion নয়।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, Boss-এর OBS recording-এর ৫ test বাকি।
- কোনো shot film করা না গেলে সেটা বলতে হয়, fake করা যাবে না।
