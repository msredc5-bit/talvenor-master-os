# Section: Produce

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (on top of the Chief's 6 worker routings, not replacing them)

## Purpose

Turning a chosen topic into something ready to record — a script (stage 2b-script) and a
visual plan (stage 3-visual-pack + 4-video plan). Making a video file is not
this section's job — stage 4 is BLOCKED.

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Script Writer | `agents/script_writer.py` (`ScriptWriterAgent`) | `ScriptWriter` (vendored) | `skills/script-writer.md` | ok | WRAPPED |
| Visual Producer | `agents/visual_producer.py` (`VisualProducerAgent`) | `VisualProducer` (vendored) | `skills/visual-producer.md` | ok | WRAPPED |

## How work flows

1. Boss / Main CEO Bot → Content Chief → task type `script_write` or `video_produce`.
2. `script_write` → vendored ScriptWriter worker (mock brain, $0) → script draft —
   Every output carries the VOICE.md DRAFT warning.
3. `video_produce` → vendored VisualProducer worker → visual plan draft + stage 4
   missing-inputs list. `video_file` is always None.
4. The result returns to the Main CEO Bot → Boss's "ok" — only then does the publish section work.

## Gate

- `ok` — script / visual plan approval. Nothing may be used without Boss's exact word.

## Honest limits

- **VOICE.md DRAFT** — no script is "final" until Boss fixes it. Boss has no
  YouTube video yet, so there is no real transcript to copy from. Boss does not speak live English
  — read-aloud scripts need Bengali transliteration under each English line.
- **Stage 4 BLOCKED** — no real footage / OBS recording, Boss's PC GPU name unknown since 2026-11-01,
  AI video generation REGION-BLOCKED (no retry). Default stills
  + Ken Burns motion are not real motion. If a shot cannot be filmed, that must be said;
  it may not be faked.
- **Week 1 long video** ("Google's Nano Banana 2 Is Free - But Is It Good?", 1,431 words,
  ~9.5 min, 5 tests) READY TO RECORD — but the verdict is **[FILL AFTER TEST]**; no verdict will be written
  without seeing the 5 tests in Boss's OBS recording.
- Upload OFF — this section uploads nothing.
