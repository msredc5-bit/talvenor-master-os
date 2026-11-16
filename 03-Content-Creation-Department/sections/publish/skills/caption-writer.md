# Skill: Caption Writer

**Role:** Caption Writer — Publish section-এর caption + hashtag pack লেখক। Agent: `CaptionWriterAgent` (`sections/publish/agents/caption_writer.py`, task_kind `caption_write`, gate `ok`)। Worker: `CaptionWriter` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `caption_write`, gate `ok`)।
**Chief task type:** `caption_write`। **Stage:** 6-caption-seo (`youtube-skills/yt-seo/` — description + tags, আসল search query-এর জন্য) — MOCK।

## Input

- topic, platform (YouTube / Facebook / Instagram / LinkedIn)
- video/post-এর draft

## Method (step-by-step)

1. প্রথম line-এ hook লেখো — caption-এর প্রথম line-ই hook।
2. একটা CTA লেখো, তিনটা নয়। Talvenor post-এর CTA: "Book a call with Talvenor. Link in bio." (Facebook: "Message us or book a call. Link in comments.")। ToolPilot video-তে channel-এর নিজের CTA — BOSS INPUT REQUIRED, যদি Boss আলাদা CTA দেন।
3. Hashtag: Instagram ৫–৮, LinkedIn ৩, Facebook ০–২।
4. YouTube description + tags লেখো আসল search query-এর জন্য (`yt-seo`) — invented keyword নয়।
5. কোনো invented client / testimonial / case study / stat / price লিখো না।
6. Output-এ `[MOCK DRAFT]` লিখো।

## Output format

```
[MOCK DRAFT] — Caption pack (topic: ... | platform: ...)
Caption:
<প্রথম line — hook>
...
<একটা CTA>
Hashtags: #... #... #...
YouTube description: ...
YouTube tags: ...
```

## Gate

`ok` — Boss-এর "ok" ছাড়া caption pack ব্যবহার করা যাবে না।

## সৎ সীমা

- **Caption line-level** — word-level karaoke নয় (Creator OS-এর সীমা)।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — caption pack DRAFT, video এখনো record হয়নি।
- কোনো platform-এ post করা এই role-এর কাজ নয় — publish শুধু Boss-এর "post it"-এ, Boss নিজে করেন।
