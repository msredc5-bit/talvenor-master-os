# Section: Publish

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (on top of the Chief's 6 worker routings, not replacing them)

## Purpose

Preparing finished content for publishing — caption + hashtag pack (stage
6-caption-seo) and the publish-prep checklist (stage 7-publish-prep). Publishing
is not this section's job — only preparation, and waiting for
Boss's gate word.

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Caption Writer | `agents/caption_writer.py` (`CaptionWriterAgent`) | `CaptionWriter` (vendored) | `skills/caption-writer.md` | ok | WRAPPED |
| Publish Prep | `agents/publish_prep.py` (`PublishPrepAgent`) | `PublishPrep` (vendored) | `skills/publish-prep.md` | post it | WRAPPED |

## How work flows

1. Boss / Main CEO Bot → Content Chief → task type `caption_write` or `publish_prep`.
2. `caption_write` → vendored CaptionWriter worker (mock brain, $0) → caption +
   hashtag pack DRAFT (Instagram 5–8, LinkedIn 3, Facebook 0–2).
3. `publish_prep` → vendored PublishPrep worker → final checklist DRAFT.
   `ready_to_publish` is always False.
4. The result returns to the Main CEO Bot → Boss's "post it" (for video upload, "upload it")
   — and Boss does the publish/upload himself.

## Gate

- `ok` — caption pack approval.
- **`post it`** — publish. **`upload it`** — video upload. Nothing is
  published/uploaded without Boss's exact word.

## Honest limits

- **Upload stage 9 DEFAULT OFF** — all three are needed: Boss's "upload it" +
  `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth). This engine
  never runs `upload_youtube.py`. No real YouTube upload has been verified yet.
- Captions are line-level — not word-level karaoke (a Creator OS limit).
- LinkedIn = Boss posts himself (personal profile).
- **13 stages: REAL 0 / MOCK 10 / BLOCKED 3** — the publish section's stages are MOCK,
  upload (stage 9) BLOCKED.
