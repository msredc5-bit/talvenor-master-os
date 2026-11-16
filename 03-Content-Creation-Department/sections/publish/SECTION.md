# Section: Publish (প্রকাশের প্রস্তুতি)

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (Chief-এর ৬ worker routing-এর উপরে, বদলে নয়)

## উদ্দেশ্য (Purpose)

তৈরি content-কে publish-এর জন্য সাজানো — caption + hashtag pack (stage
6-caption-seo) আর publish-prep checklist (stage 7-publish-prep)। Publish
করা এই section-এর কাজ নয় — শুধু প্রস্তুতি, আর Boss-এর gate word-এর জন্য
অপেক্ষা।

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Caption Writer | `agents/caption_writer.py` (`CaptionWriterAgent`) | `CaptionWriter` (vendored) | `skills/caption-writer.md` | ok | WRAPPED |
| Publish Prep | `agents/publish_prep.py` (`PublishPrepAgent`) | `PublishPrep` (vendored) | `skills/publish-prep.md` | post it | WRAPPED |

## কাজের প্রবাহ (How work flows)

1. Boss / Main CEO Bot → Content Chief → task type `caption_write` বা `publish_prep`।
2. `caption_write` → vendored CaptionWriter worker (mock brain, $0) → caption +
   hashtag pack DRAFT (Instagram ৫–৮, LinkedIn ৩, Facebook ০–২)।
3. `publish_prep` → vendored PublishPrep worker → final checklist DRAFT।
   `ready_to_publish` সবসময় False।
4. ফলাফল Main CEO Bot-এ ফেরে → Boss-এর "post it" (video upload-এর জন্য "upload it")
   — আর publish/upload Boss নিজে করেন।

## Gate

- `ok` — caption pack approval।
- **`post it`** — publish। **`upload it`** — video upload। Boss-এর exact word ছাড়া
  কিছু publish/upload হয় না।

## সৎ সীমা (Honest limits)

- **Upload stage 9 DEFAULT OFF** — লাগে তিনটাই: Boss-এর "upload it" +
  `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth)। এই engine
  কখনো `upload_youtube.py` চালায় না। কোনো real YouTube upload এখনো verify হয়নি।
- Caption line-level — word-level karaoke নয় (Creator OS-এর সীমা)।
- LinkedIn = Boss নিজে post করেন (personal profile)।
- **১৩ stage: REAL 0 / MOCK 10 / BLOCKED 3** — publish section-এর stage গুলো MOCK,
  upload (stage 9) BLOCKED।
