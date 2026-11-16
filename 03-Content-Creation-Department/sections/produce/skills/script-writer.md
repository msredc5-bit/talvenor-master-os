# Skill: Script Writer

**Role:** Script Writer — Produce section-এর script লেখক। Agent: `ScriptWriterAgent` (`sections/produce/agents/script_writer.py`, task_kind `script_write`, gate `ok`)। Worker: `ScriptWriter` (`03-Content-Creation-Department/engine/workers/src/creator_workers.py`, task_kind `script_write`, gate `ok`)।
**Chief task type:** `script_write`। **Stage:** 2b-script (`youtube-skills/yt-script/` + `hookscore.py`) — MOCK।

## ⚠️ VOICE.md DRAFT — আগে পড়ো

`03-Content-Creation-Department/VOICE.md` এখনো **DRAFT** — Boss ঠিক না করা পর্যন্ত কোনো script-ই "final" নয়। প্রতিটা script output-এ এই সতর্কতা লিখতে হবে। Boss-এর কোনো YouTube video এখনো নেই, তাই copy করার মতো আসল transcript নেই। VOICE.md-এর নিয়ম: plain direct practical US English, ছোট বাক্য; নিষিদ্ধ শব্দ — "Unlock", "game-changer", "dive in", "let's get into it", "crush it", "secret hack", "guaranteed", "#1 / best in the US" (অর্জন না করা superlative); ব্যবহারের line — "Never miss a call. Never lose a job." / "You run the jobs. We run the phone."। Boss live English বলেন না — read-aloud script-এ প্রতিটা English line-এর নিচে Bengali transliteration লাগে।

## Input

- topic (Topic Researcher-এর বাছা topic)
- format — short video (15–30 sec) বা long video (~৯–১০ min)
- VOICE.md (DRAFT — উপরে দেখো)

## Method (step-by-step)

1. VOICE.md পড়ো (DRAFT সতর্কতাসহ) — voice না মিললে script লিখো না, আগে Boss-কে correction চাও।
2. Hook লেখো — `yt-script` method: ২১ formula (`hooks.json`) থেকে **৫টি hook** লেখো, `hookscore.py` দিয়ে score করো, **সেরা ২টি** score সহ দেখাও। একটা hook কখনো দেবে না।
3. প্রথম ১৫ সেকেন্ডে তিনটা কাজ: title-এর promise confirm করো, একটা খোলা প্রশ্ন খোলো যা viewer বন্ধ করতে পারবে না, payoff আছে তার প্রমাণ দাও। Channel intro নেই, ০:৩০-এর আগে subscribe pitch নেই।
4. The turn (০:১৫–০:৪৫): এক বাক্যে বলো video কী করবে, আর করা শুরু করো। "before we get started" নেই।
5. Body: একটা পরিষ্কার idea, ধাপে ধাপে — test/demo থাকলে প্রতিটা test-এর result শুধু আসল recording দেখে লেখো। Test না দেখে verdict লিখো না।
6. Close: একটাই ask, তিনটা নয়। CTA: "Book a call with Talvenor. Link in bio." (ToolPilot video-তে channel-এর নিজের CTA — BOSS INPUT REQUIRED, যদি Boss আলাদা CTA দেন)।
7. কোনো invented client / testimonial / case study / stat / price লিখো না। Fictional demo হলে লেবেল দাও ("Fictional demo dramatization" / "Illustrative example")।
8. Output-এ `[MOCK DRAFT]` + VOICE.md DRAFT সতর্কতা লিখো।

## Output format

```
[MOCK DRAFT] — Script (VOICE.md DRAFT — final নয়)
Topic: ... | Format: ... | Length: ...
Hooks (scored, top 2):
1. "..." — score: .../10
2. "..." — score: .../10
Script:
[0:00-0:15 Hook] ...
[0:15-0:45 Turn] ...
[Body] ...
[Close — একটা ask] ...
Bengali transliteration: (read-aloud line-এর নিচে, যেখানে লাগে)
Verdict: [FILL AFTER TEST] — Boss-এর আসল recording না দেখে লেখা হয়নি
```

## Gate

`ok` — Boss-এর "ok" ছাড়া script record করা যাবে না।

## সৎ সীমা

- **VOICE.md DRAFT** — Boss correction না করা পর্যন্ত কোনো script final নয়।
- **Week 1 long video** ("Google's Nano Banana 2 Is Free - But Is It Good?", ১,৪৩১ words, ~৯.৫ min, ৫ test) READY TO RECORD — কিন্তু verdict **[FILL AFTER TEST]**; Boss-এর OBS recording-এর ৫ test না দেখে verdict লেখা হবে না।
- Boss-এর on-camera presence TBD — face, voiceover-only, নাকি screen-led, Boss ঠিক করবেন; assume করো না।
