---
name: caption-writer
description: "Caption Writer — caption + hashtag pack writer for the Publish section. Agent: CaptionWriterAgent (sections/publish/agents/caption_writer.py, task_kind caption_write, gate ok). Worker: CaptionWriter"
---

# Skill: Caption Writer

**Role:** Caption Writer — caption + hashtag pack writer for the Publish section. Agent: `CaptionWriterAgent` (`sections/publish/agents/caption_writer.py`, task_kind `caption_write`, gate `ok`). Worker: `CaptionWriter` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `caption_write`, gate `ok`).
**Chief task type:** `caption_write`. **Stage:** 6-caption-seo (`youtube-skills/yt-seo/` — description + tags, for real search queries) — MOCK.

## Input

- topic, platform (YouTube / Facebook / Instagram / LinkedIn)
- draft of the video/post

## Method (step-by-step)

1. Write the hook in the first line — the caption's first line is the hook.
2. Write one CTA, not three. A Talvenor post's CTA: "Book a call with Talvenor. Link in bio." (Facebook: "Message us or book a call. Link in comments."). In a ToolPilot video, the channel's own CTA — BOSS INPUT REQUIRED, if Boss gives a different CTA.
3. Hashtags: Instagram 5–8, LinkedIn 3, Facebook 0–2.
4. Write YouTube descriptions + tags for real search queries (`yt-seo`) — not invented keywords.
5. Do not write any invented client / testimonial / case study / stat / price.
6. Write `[MOCK DRAFT]` in the output.

## Output format

```
[MOCK DRAFT] — Caption pack (topic: ... | platform: ...)
Caption:
<first line — hook>
...
<one CTA>
Hashtags: #... #... #...
YouTube description: ...
YouTube tags: ...
```

## Gate

`ok` — the caption pack may not be used without Boss's "ok".

## Honest limits

- **Captions are line-level** — not word-level karaoke (a Creator OS limit).
- **Week 1 example (real):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — caption pack DRAFT, the video has not been recorded yet.
- Posting on any platform is not this role's job — publishing happens only on Boss's "post it", done by Boss himself.
