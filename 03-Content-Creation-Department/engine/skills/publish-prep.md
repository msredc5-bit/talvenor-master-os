# Skill: Publish Prep

**Role:** Publish Prep — the Content Engine's publish-readiness checker. Worker: `PublishPrep` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `publish_prep`, gate `post it`).
**Chief task type:** `publish_prep`. **Stage:** 7-publish-prep.

## Input

- finished post/video draft (script + visual plan + caption pack)
- platform (Facebook / Instagram / LinkedIn / YouTube)
- best posting time (US Eastern — e.g. ToolPilot long: Sat 10:00 AM ET = Sat 9:00 PM Dhaka; Shorts: Wed + Fri 9:00 AM ET = 8:00 PM Dhaka)

## Method (step-by-step)

1. Run the final checklist — write tick / fail for each item:
   - [ ] Hook is in the first 2 seconds (Reel) / first 15 seconds (long video)
   - [ ] On-screen text is readable, verbatim, spelled right ("Talvenor" spelled right)
   - [ ] No invented claim / client / stat / price / guarantee
   - [ ] If it is a fictional demo, it is labelled ("Illustrative example")
   - [ ] Caption + hashtags follow the platform's rules
   - [ ] Platform + posting time are right
   - [ ] If LinkedIn: Boss will post himself (personal profile) — this engine will not post
2. If any item fails, write it and send the draft back — do not hide a fail and write "ready".
3. Even if all pass, write: `ready_to_publish: False` — because this role does not publish/upload, it only gives a checklist.
4. Label the output `[MOCK DRAFT]`.

## Output format

```
[MOCK DRAFT] — Publish Prep Checklist
Topic: ... | Platform: ... | Best time (US Eastern): ...
Checklist:
[ ] Hook — pass/fail: ...
[ ] Readable text — pass/fail: ...
[ ] No invented claims — pass/fail: ...
[ ] Caption/hashtags — pass/fail: ...
[ ] Platform + time — pass/fail: ...
ready_to_publish: False
Gate: "post it" (for upload, "upload it")
```

## Gate

**`post it`** (for video upload, **`upload it`**) — nothing is published/uploaded without Boss's exact word, and even with approval this engine does not publish/upload — Boss does it himself.

## Honest limits — Upload OFF

- Upload stage 9 is **DEFAULT OFF** — all three are needed: Boss's "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth). This engine never runs `upload_youtube.py`.
- No video may be called "live" until a real upload is verified — no real YouTube upload has been verified yet.
- This role can draft Talvenor weekly posts too, but publishing happens only on Boss's "post it".
