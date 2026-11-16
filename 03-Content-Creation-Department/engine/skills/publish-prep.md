# Skill: Publish Prep

**Role:** Publish Prep — Content Engine-এর publish-প্রস্তুতি checker। Worker: `PublishPrep` (`~/workspace/creator-os-combined/src/creator_workers.py`, task_kind `publish_prep`, gate `post it`)।
**Chief task type:** `publish_prep`। **Stage:** 7-publish-prep।

## Input

- finished post/video draft (script + visual plan + caption pack)
- platform (Facebook / Instagram / LinkedIn / YouTube)
- best posting time (US Eastern — যেমন ToolPilot long: Sat 10:00 AM ET = Sat 9:00 PM Dhaka; Shorts: Wed + Fri 9:00 AM ET = 8:00 PM Dhaka)

## Method (step-by-step)

1. Final checklist চালাও — প্রতিটা item-এ tick / fail লেখো:
   - [ ] Hook প্রথম ২ সেকেন্ডে (Reel) / প্রথম ১৫ সেকেন্ডে (long video) আছে
   - [ ] On-screen text readable, verbatim, বানান ঠিক ("Talvenor" বানান ঠিক আছে)
   - [ ] কোনো invented claim / client / stat / price / guarantee নেই
   - [ ] Fictional demo হলে লেবেল আছে ("Illustrative example")
   - [ ] Caption + hashtag platform-এর নিয়মে আছে
   - [ ] Platform + posting time ঠিক আছে
   - [ ] LinkedIn হলে: Boss নিজে post করবেন (personal profile) — এই engine post করবে না
2. কোনো item fail হলে সেটা লেখো আর draft-টা ফেরত পাঠাও — fail লুকিয়ে "ready" লিখো না।
3. সব pass হলেও লেখো: `ready_to_publish: False` — কারণ publish/upload এই role করে না, শুধু checklist দেয়।
4. Output-এ `[MOCK DRAFT]` লেবেল দাও।

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
Gate: "post it" (upload হলে "upload it")
```

## Gate

**`post it`** (video upload-এর জন্য **`upload it`**) — Boss-এর exact word ছাড়া কিছু publish/upload হয় না, আর অনুমোদন থাকলেও এই engine publish/upload করে না — Boss নিজে করেন।

## সৎ সীমা — Upload OFF

- Upload stage 9 **DEFAULT OFF** — তিনটাই লাগে: Boss-এর "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth)। এই engine কখনো `upload_youtube.py` চালায় না।
- কোনো video "live" বলা যাবে না যতক্ষণ আসল upload verify না হয় — এখনো কোনো real YouTube upload verify হয়নি।
- Talvenor weekly post-ও এই role draft করতে পারে, কিন্তু publish শুধু Boss-এর "post it"-এ।
