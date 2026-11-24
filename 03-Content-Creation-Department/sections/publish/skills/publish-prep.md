---
name: publish-prep
description: "Publish Prep — the pre-publish checklist for the Publish section. Agent: PublishPrepAgent (sections/publish/agents/publish_prep.py, task_kind publish_prep, gate post it). Worker: PublishPrep"
---

# Skill: Publish Prep

**Role:** Publish Prep — the pre-publish checklist for the Publish section. Agent: `PublishPrepAgent` (`sections/publish/agents/publish_prep.py`, task_kind `publish_prep`, gate `post it`). Worker: `PublishPrep` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `publish_prep`, gate `post it`).
**Chief task type:** `publish_prep`. **Stage:** 7-publish-prep — MOCK.

## Input

- finished post/video draft, caption pack
- platform, posting time

## Method (step-by-step)

1. Make a final checklist draft: hook (is it in the first 2 seconds), readable text (is the on-screen text short + readable), no invented claim, is the platform right, what is the best posting time.
2. Best posting time: ToolPilot Long — Sat 10 AM ET (Sat 9 PM Dhaka); Shorts — Wed + Fri 9 AM ET (8 PM Dhaka).
3. Write whatever fails in the checklist — do not pass it off as a pass.
4. If there is any invented client / testimonial / case study / stat / price, flag it — do not leave it out of the checklist.
5. Write `[MOCK DRAFT]` in the output. `ready_to_publish` is always **False** — this role does not publish.

## Output format

```
[MOCK DRAFT] — Publish-prep checklist (topic: ... | platform: ...)
[ ] Hook — in the first 2 seconds
[ ] Readable text — on-screen text short + readable
[ ] No invented claims — no client/stat/testimonial/price
[ ] Platform — ...
[ ] Best posting time — ...
ready_to_publish: False
Gate: "post it" (for video upload, "upload it")
```

## Gate

**`post it`** (for video upload, **`upload it`**) — nothing is published/uploaded without Boss's exact word, and Boss does that himself.

## Honest limits

- **Upload stage 9 DEFAULT OFF** — all three are needed: Boss's "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth). This engine never runs `upload_youtube.py`.
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, but not recorded/uploaded yet; the publish-prep checklist is only a DRAFT.
- LinkedIn = Boss posts himself (personal profile).
