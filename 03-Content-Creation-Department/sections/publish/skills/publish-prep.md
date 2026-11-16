# Skill: Publish Prep

**Role:** Publish Prep — Publish section-এর publish-এর আগের checklist। Agent: `PublishPrepAgent` (`sections/publish/agents/publish_prep.py`, task_kind `publish_prep`, gate `post it`)। Worker: `PublishPrep` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `publish_prep`, gate `post it`)।
**Chief task type:** `publish_prep`। **Stage:** 7-publish-prep — MOCK।

## Input

- finished post/video draft, caption pack
- platform, posting time

## Method (step-by-step)

1. Final checklist draft বানাও: hook (প্রথম ২ সেকেন্ডে আছে কি), readable text (on-screen text ছোট + readable কি), কোনো invented claim নেই কি, platform ঠিক কি, best posting time কী।
2. Best posting time: ToolPilot Long — Sat 10 AM ET (Sat 9 PM Dhaka); Shorts — Wed + Fri 9 AM ET (8 PM Dhaka)।
3. Checklist-এ যা fail করে, সেটা লেখো — pass বলে চালিও না।
4. কোনো invented client / testimonial / case study / stat / price থাকলে সেটা flag করো — checklist থেকে বাদ দিও না।
5. Output-এ `[MOCK DRAFT]` লিখো। `ready_to_publish` সবসময় **False** — publish এই role করে না।

## Output format

```
[MOCK DRAFT] — Publish-prep checklist (topic: ... | platform: ...)
[ ] Hook — প্রথম ২ সেকেন্ডে আছে
[ ] Readable text — on-screen text ছোট + readable
[ ] No invented claims — client/stat/testimonial/price নেই
[ ] Platform — ...
[ ] Best posting time — ...
ready_to_publish: False
Gate: "post it" (video upload-এর জন্য "upload it")
```

## Gate

**`post it`** (video upload-এর জন্য **`upload it`**) — Boss-এর exact word ছাড়া কিছু publish/upload হয় না, আর সেটাও Boss নিজে করেন।

## সৎ সীমা

- **Upload stage 9 DEFAULT OFF** — লাগে তিনটাই: Boss-এর "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth)। এই engine কখনো `upload_youtube.py` চালায় না।
- **Week 1 উদাহরণ (আসল):** ToolPilot Week 1 long video — "Google's Nano Banana 2 Is Free - But Is It Good?" — READY TO RECORD, কিন্তু এখনো record/upload হয়নি; publish-prep checklist DRAFT মাত্র।
- LinkedIn = Boss নিজে post করেন (personal profile)।
