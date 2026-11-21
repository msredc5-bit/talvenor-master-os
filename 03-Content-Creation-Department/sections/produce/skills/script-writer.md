# Skill: Script Writer

**Role:** Script Writer — script writer for the Produce section. Agent: `ScriptWriterAgent` (`sections/produce/agents/script_writer.py`, task_kind `script_write`, gate `ok`). Worker: `ScriptWriter` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `script_write`, gate `ok`).
**Chief task type:** `script_write`. **Stage:** 2b-script (`youtube-skills/yt-script/` + `hookscore.py`) — MOCK.

## ⚠️ VOICE.md DRAFT — read first

`03-Content-Creation-Department/VOICE.md` is still **DRAFT** — no script is "final" until Boss fixes it. This warning must be written in every script output. Boss has no YouTube video yet, so there is no real transcript to copy from. VOICE.md rules: plain direct practical US English, short sentences; banned words — "Unlock", "game-changer", "dive in", "let's get into it", "crush it", "secret hack", "guaranteed", "#1 / best in the US" (superlatives not earned); lines to use — "Never miss a call. Never lose a job." / "You run the jobs. We run the phone.". Boss does not speak live English — read-aloud scripts need Bengali transliteration under each English line.

## Input

- topic (the topic Topic Researcher picked)
- format — short video (15–30 sec) or long video (~9–10 min)
- VOICE.md (DRAFT — see above)

## Method (step-by-step)

1. Read VOICE.md (with the DRAFT warning) — if the voice does not match, do not write the script; ask Boss for a correction first.
2. Write the hook — the `yt-script` method: from 21 formulas (`hooks.json`) write **5 hooks**, score them with `hookscore.py`, show the **best 2** with scores. Never give a single hook.
3. In the first 15 seconds do three things: confirm the title's promise, open a question the viewer cannot close, prove there is a payoff. No channel intro, no subscribe pitch before 0:30.
4. The turn (0:15–0:45): say in one sentence what the video will do, and start doing it. No "before we get started".
5. Body: one clear idea, step by step — if there is a test/demo, write each test's result only from the real recording. Do not write a verdict without seeing the test.
6. Close: one ask, not three. CTA: "Book a call with Talvenor. Link in bio." (In a ToolPilot video, the channel's own CTA — BOSS INPUT REQUIRED, if Boss gives a different CTA).
7. Do not write any invented client / testimonial / case study / stat / price. If it is a fictional demo, label it ("Fictional demo dramatization" / "Illustrative example").
8. Write `[MOCK DRAFT]` + the VOICE.md DRAFT warning in the output.

## Output format

```
[MOCK DRAFT] — Script (VOICE.md DRAFT — not final)
Topic: ... | Format: ... | Length: ...
Hooks (scored, top 2):
1. "..." — score: .../10
2. "..." — score: .../10
Script:
[0:00-0:15 Hook] ...
[0:15-0:45 Turn] ...
[Body] ...
[Close — one ask] ...
Bengali transliteration: (under the read-aloud line, where needed)
Verdict: [FILL AFTER TEST] — not written without seeing Boss's real recording
```

## Gate

`ok` — a script may not be recorded without Boss's "ok".

## Honest limits

- **VOICE.md DRAFT** — no script is final until Boss corrects it.
- **Week 1 long video** ("Google's Nano Banana 2 Is Free - But Is It Good?", 1,431 words, ~9.5 min, 5 tests) is READY TO RECORD — but the verdict is **[FILL AFTER TEST]**; no verdict will be written without seeing the 5 tests in Boss's OBS recording.
- Boss's on-camera presence is TBD — face, voiceover-only, or screen-led, Boss will decide; do not assume.
