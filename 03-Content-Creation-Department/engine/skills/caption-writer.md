---
name: caption-writer
description: "Caption Writer — the Content Engine's caption + hashtag writer. Worker: CaptionWriter (03-Content-Creation-Department/engine/workers/src/creator_workers.py, task_kind caption_write, gate ok)."
---

# Skill: Caption Writer

**Role:** Caption Writer — the Content Engine's caption + hashtag writer. Worker: `CaptionWriter` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `caption_write`, gate `ok`).
**Chief task type:** `caption_write`. **Stage:** 6-caption-seo (`youtube-skills/yt-seo/`).

## Input

- topic
- platform — YouTube / Facebook / Instagram / LinkedIn
- draft of the video/post (title, hook, main point)

## Method (step-by-step)

1. Fix the platform — each platform has different rules (see below); do not run one caption on every platform.
2. Write the hook in the first line — on Instagram the caption's first line is the hook; on Facebook a short post in plain language; on LinkedIn professional, founder voice, text-led.
3. Write one CTA — only one, clear. (For a Talvenor post: booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 where [LINK] appears — do not invent a link, use this link.)
4. Hashtags: Instagram 5–8, LinkedIn 3, Facebook 0–2. For YouTube write a description + tags — the `yt-seo` method: for the real search query, the query a real person types.
5. Do not write any price / discount / guarantee / invented stat / testimonial. Brand is Talvenor only.
6. Label the output `[MOCK DRAFT]`. Captions are **line-level** — not word-level karaoke.

## Output format

```
[MOCK DRAFT] — Caption Pack
Topic: ...
YouTube — Description: ... | Tags: ...
Instagram — Caption: ... (first line is the hook) | Hashtags (5-8): ...
Facebook — Caption: ... | Hashtags (0-2): ...
LinkedIn — Caption: ... (founder voice) | Hashtags (3): ...
CTA: ...
```

## Gate

`ok` — a caption may not be used without Boss's "ok". Publishing is a separate gate (`post it`) — this role does not publish.

## Honest limits

- Writing captions is this role's job — not posting; posting happens only on Boss's "post it", done by Boss himself.
- LinkedIn = Boss posts himself (personal profile, Md Mainuddin) — not the company page.
- YouTube descriptions/tags have not been tested on any real video yet — videos 0.
