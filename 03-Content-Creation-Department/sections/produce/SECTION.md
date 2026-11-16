# Section: Produce (তৈরি)

**Department:** 03-Content-Creation-Department — Content Creation Engine (Creator OS)
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Phase:** 7 — Section agents + skills (Chief-এর ৬ worker routing-এর উপরে, বদলে নয়)

## উদ্দেশ্য (Purpose)

বাছা topic-কে record করার মতো জিনিসে বদলানো — script (stage 2b-script) আর
visual plan (stage 3-visual-pack + 4-video plan)। Video file বানানো এই
section-এর কাজ নয় — stage 4 BLOCKED।

## Staff roster

| Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|
| Script Writer | `agents/script_writer.py` (`ScriptWriterAgent`) | `ScriptWriter` (vendored) | `skills/script-writer.md` | ok | WRAPPED |
| Visual Producer | `agents/visual_producer.py` (`VisualProducerAgent`) | `VisualProducer` (vendored) | `skills/visual-producer.md` | ok | WRAPPED |

## কাজের প্রবাহ (How work flows)

1. Boss / Main CEO Bot → Content Chief → task type `script_write` বা `video_produce`।
2. `script_write` → vendored ScriptWriter worker (mock brain, $0) → script draft —
   প্রতিটা output-এ VOICE.md DRAFT সতর্কতা থাকে।
3. `video_produce` → vendored VisualProducer worker → visual plan draft + stage 4-এর
   missing-inputs list। `video_file` সবসময় None।
4. ফলাফল Main CEO Bot-এ ফেরে → Boss-এর "ok" — তারপরেই publish section কাজ করে।

## Gate

- `ok` — script / visual plan approval। Boss-এর exact word ছাড়া কিছু ব্যবহার করা যাবে না।

## সৎ সীমা (Honest limits)

- **VOICE.md DRAFT** — Boss ঠিক না করা পর্যন্ত কোনো script-ই "final" নয়। Boss-এর কোনো
  YouTube video এখনো নেই, তাই copy করার মতো আসল transcript নেই। Boss live English
  বলেন না — read-aloud script-এ প্রতিটা English line-এর নিচে Bengali transliteration লাগে।
- **Stage 4 BLOCKED** — real footage / OBS recording নেই, Boss-এর PC GPU-র নাম 2026-11-01
  থেকে জানা যায়নি, AI video generation REGION-BLOCKED (retry করা হয় না)। Default stills
  + Ken Burns motion = সত্যিকারের motion নয়। কোনো shot film করা না গেলে সেটা বলতে হয়,
  fake করা যাবে না।
- **Week 1 long video** ("Google's Nano Banana 2 Is Free - But Is It Good?", ১,৪৩১ words,
  ~৯.৫ min, ৫ test) READY TO RECORD — কিন্তু verdict **[FILL AFTER TEST]**; Boss-এর OBS
  recording-এর ৫ test না দেখে verdict লেখা হবে না।
- Upload OFF — এই section কিছু upload করে না।
