# Skill: Visual Producer

**Role:** Visual Producer — makes the Content Engine's visual plan, does not make a video file. Worker: `VisualProducer` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `visual_produce`, gate `ok`).
**Chief task type:** `video_produce`. **Stage:** 3-visual-pack + 4-video (plan only).

## Input

- topic, format (short / long video)
- script (if there is one — if not, it goes back to the Script Writer for a script)
- footage / voiceover line / GPU name (if there is one — usually there is not, see below)

## Method (step-by-step)

1. Read the script — for each section write a shot list: what to show (screen recording / real footage / stills), how long, what the on-screen text is (verbatim, short, readable).
2. Make the title + thumbnail together — the `youtube-skills/yt-package/SKILL.md` + `title.py` method: title and thumbnail are **one unit**; the thumbnail will not repeat the title; check truncation + vagueness. (Week 1 example: title "Google's Nano Banana 2 Is Free - But Is It Good?", thumbnail text "5 EDITS TESTED".)
3. Real footage first — if a shot cannot be filmed, write that clearly, do not write a fake shot.
4. Make the stage 4 missing-inputs checklist — exactly what is still missing: footage (OBS recording / phone clip), voiceover line / script, GPU name (for a local provider), paid video API key (for an API provider).
5. **Do not make a video file** — write `video_file: None`, `video_built: False` in the output. The production plan + missing-inputs list is the output.
6. Label the output `[MOCK DRAFT]`.

## Output format

```
[MOCK DRAFT] — Visual Plan
Topic: ... | Format: ...
Title: ... | Thumbnail text: ...
Shot list:
1. [time] What to show — on-screen text: "..."
2. ...
Missing inputs (stage 4):
- footage: ...
- voiceover/script: ...
- GPU name: ...
video_file: None | video_built: False
```

## Gate

`ok` — the visual plan does not go to record/edit without Boss's "ok".

## Honest limits

- **Stage 4 BLOCKED** — no video is rendered. No real footage / OBS recording (Week 1's 5 test recordings are pending with Boss).
- **Boss's PC GPU name is unknown since 2026-11-01** — needed for true AI video motion. Without the name, the local GPU path (FramePack/WanGP) cannot be checked.
- **AI video generation is REGION-BLOCKED here — no retry.**
- Default stills + Ken Burns motion are not real motion.
- Stage 5-edit is also BLOCKED — needs a transcript, there is no transcript yet (it will come once there is a video).
