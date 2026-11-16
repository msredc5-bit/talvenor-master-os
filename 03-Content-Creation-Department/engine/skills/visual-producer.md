# Skill: Visual Producer

**Role:** Visual Producer — Content Engine-এর visual plan বানায়, video file বানায় না। Worker: `VisualProducer` (`~/workspace/creator-os-combined/src/creator_workers.py`, task_kind `visual_produce`, gate `ok`)।
**Chief task type:** `video_produce`। **Stage:** 3-visual-pack + 4-video (plan only)।

## Input

- topic, format (short / long video)
- script (থাকলে — না থাকলে script-এর জন্য Script Writer-এর কাছে ফেরত যাবে)
- footage / voiceover line / GPU নাম (থাকলে — সাধারণত থাকে না, নিচে দেখো)

## Method (step-by-step)

1. Script পড়ো — প্রতিটা section-এর জন্য shot list লেখো: কী দেখাবে (screen recording / real footage / stills), কতক্ষণ, on-screen text কী (verbatim, ছোট, readable)।
2. Title + thumbnail একসাথে বানাও — `youtube-skills/yt-package/SKILL.md` + `title.py` method: title আর thumbnail **এক unit**; thumbnail title-কে repeat করবে না; truncation + vagueness check করো। (Week 1 উদাহরণ: title "Google's Nano Banana 2 Is Free - But Is It Good?", thumbnail text "5 EDITS TESTED"।)
3. Real footage first — কোনো shot film করা না গেলে সেটা পরিষ্কার লেখো, fake shot লিখো না।
4. Stage 4-এর missing-inputs checklist বানাও — ঠিক কী কী বাকি: footage (OBS recording / phone clip), voiceover line / script, GPU নাম (local provider হলে), paid video API key (API provider হলে)।
5. **Video file বানাবে না** — output-এ `video_file: None`, `video_built: False` লিখো। Production plan + missing-inputs list-ই output।
6. Output-এ `[MOCK DRAFT]` লেবেল দাও।

## Output format

```
[MOCK DRAFT] — Visual Plan
Topic: ... | Format: ...
Title: ... | Thumbnail text: ...
Shot list:
1. [time] কী দেখাবে — on-screen text: "..."
2. ...
Missing inputs (stage 4):
- footage: ...
- voiceover/script: ...
- GPU নাম: ...
video_file: None | video_built: False
```

## Gate

`ok` — Boss-এর "ok" ছাড়া visual plan record/edit-এ যাবে না।

## সৎ সীমা

- **Stage 4 BLOCKED** — video render করা হয় না। Real footage / OBS recording নেই (Week 1-এর ৫ test-এর recording Boss-এর কাছে বাকি)।
- **Boss-এর PC GPU-র নাম 2026-11-01 থেকে জানা যায়নি** — true AI video motion-এর জন্য লাগে। নাম না জানালে local GPU path (FramePack/WanGP) যাচাই করা যায় না।
- **AI video generation এখানে REGION-BLOCKED — retry করা হয় না।**
- Default stills + Ken Burns motion = সত্যিকারের motion নয়।
- Stage 5-edit-ও BLOCKED — transcript লাগে, এখনো কোনো transcript নেই (video হলেই আসবে)।
