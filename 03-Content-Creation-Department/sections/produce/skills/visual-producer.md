# Skill: Visual Producer

**Role:** Visual Producer — making the visual plan for the Produce section. Agent: `VisualProducerAgent` (`sections/produce/agents/visual_producer.py`, task_kind `video_produce`, gate `ok`). Worker: `VisualProducer` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `visual_produce`, gate `ok`).
**Chief task type:** `video_produce`. **Stage:** 3-visual-pack (`youtube-skills/yt-package/title.py` — title + thumbnail linted together) + 4-video production plan — MOCK.

## Input

- topic, format (short video / long video)
- script (if there is one)
- footage / voiceover line / GPU name (if there is one)

## Method (step-by-step)

1. Make a visual plan — shot list, thumbnail idea, on-screen text (verbatim, short, readable).
2. Lint the title + thumbnail together (`title.py`) — Week 1 example: title "Google's Nano Banana 2 Is Free - But Is It Good?" (48 chars, title lint 100/100), thumbnail text "5 EDITS TESTED".
3. Write the stage 4-video production plan + missing-inputs checklist — exactly which inputs are still missing (footage / voiceover line / GPU name).
4. Real footage first — if a shot cannot be filmed, say so; do not fake it.
5. Write `[MOCK DRAFT]` in the output. `video_file` is always **None** — this role does not make a video file.

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
- Boss's PC GPU name — ...
video_file: None (Stage 4 BLOCKED — no video rendered)
```

## Gate

`ok` — the visual plan may not be used without Boss's "ok".

## Honest limits

- **Stage 4 BLOCKED** — no real footage / OBS recording, Boss's PC GPU name **unknown since 2026-11-01** (needed for true AI video motion), AI video generation is **REGION-BLOCKED here — no retry**. Default stills + Ken Burns motion are not real motion.
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, 5 tests in Boss's OBS recording still pending.
- If a shot cannot be filmed, that must be said; it may not be faked.
