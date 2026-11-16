# Content Creation — Pipeline (১৩ stage, সৎ map)

**Engine:** Creator OS — `~/workspace/creator-os-combined/` (REUSED, duplicate নয়)
**Channel:** ToolPilot @ToolPilotai69 (faceless, AI Tools & Tutorials)
**Chief:** `chief_of_staff_content.py` — REAL (Phase 3), ৬ worker ডাকে (mock brain, $0)

## ১৩ stage — অবস্থা

| # | Stage | Worker / Tool | অবস্থা | Boss-এর কাছে যা বাকি |
|---|---|---|---|---|
| `0a-niche` | Niche finder | yt-niche `niche_score.py` | **MOCK** — topic না থাকলে চলে, নইলে skip | কিছু না (topic জানা থাকলে এই stage লাগে না) |
| `0b-plan` | Plan | yt-plan (weekly plan) | **MOCK** — hours থেকে plan বানায় | সপ্তাহে কত ঘণ্টা দেবেন — জানানো |
| `1-research` | Research | TopicResearcher | **MOCK** — mock brain-এ topic draft | কিছু না |
| `2a-concept` | Concept | `concept_score.py` (৩–৫ concept, ১–১০ score) | **MOCK** — score scaffold | কিছু না |
| `2b-script` | Script | ScriptWriter + hookscore.py | **MOCK** — `[MOCK DRAFT]` scaffold | **VOICE.md correction** — DRAFT, Boss ঠিক না করা পর্যন্ত কোনো script final নয় |
| `3-visual-pack` | Visual+Pack | VisualProducer + title.py | **MOCK** — shot list + thumbnail idea | কিছু না |
| `4-video` | Video | Reel Factory (pluggable provider) | **BLOCKED** — Chief শুধু production plan + missing-inputs list দেয়; video render করে না | **OBS recording / real footage** (Week 1-এর ৫ test), **PC GPU নাম** (true AI motion-এর জন্য — 2026-11-01 থেকে জানা যায়নি), অথবা paid video key ($0 cap-এ নয়) |
| `5-edit` | Edit | yt-edit (deadair, chapters, shorts) | **BLOCKED** — transcript লাগে, এখনো কোনো transcript নেই | video-র transcript (video হলেই আসবে) |
| `6-caption-seo` | Caption+SEO | CaptionWriter + yt-seo | **MOCK** — caption pack draft | কিছু না |
| `7-publish-prep` | Publish prep | PublishPrep ONLY | **MOCK** — checklist draft, `ready_to_publish: false` | Boss-এর gate word: post করতে **"post it"**, upload করতে **"upload it"** |
| `8-report` | Report | PerformanceTracker + yt-retention | **MOCK** — report template; post-publish only | কোনো video publish হয়নি, তাই metric 0 — Boss-এর পাঠানো আসল সংখ্যা লাগবে |
| `9-upload` | Upload | `upload_youtube.py` | **BLOCKED** — **DEFAULT OFF** | Boss-এর **"upload it"** + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth) — তিনটাই |
| `10-next-plan` | Next plan | `loop_next.py` | **MOCK** — আগের report পড়ে পরের brief লেখে | কোনো report নেই এখনো (video 0) |

**গণনা:** REAL **0** · MOCK **10** · STUB **0** · BLOCKED **3** (stage 4, 5, 9)।
REAL 0-ই সত্য — কোনো stage-ই এখনো আসল finished output দেয় না; সব draft
mock scaffold। Chief-এর কাজ: draft বানানো + gate-এ আটকানো, video render
বা upload করা নয়।

## সৎ সীমা (লুকানো হয় না)

- **Live-LLM brain unwired** — standalone runner-এ MockLLM-ই চলে; live
  provider deliberate ভাবে unwired (কোনো key ফাইলে নেই, কোনো network
  call নেই)। Agent (Elora/Muse) নিজেই brain — আসল লেখা agent লেখে।
- **VOICE.md DRAFT** — `~/workspace/creator-os-combined/youtube-skills/VOICE.md`।
- **True AI video motion** — Boss-এর PC GPU (নাম জানা যায়নি) বা paid
  key ছাড়া হয় না। AI video generation এখানে REGION-BLOCKED — retry
  করা হয় না। Default stills + Ken Burns motion = সত্যিকারের motion নয়।
- **Captions line-level** — word-level karaoke নয়।
- **Upload OFF** — কোনো real YouTube upload এখনো verify হয়নি।
- **পুরনো artifact page `creator-os-combined` STALE** — ৮ stage দেখায়,
  আসল ১৩। Boss না বললে ঠিক করা হবে না।

## Talvenor weekly social (Nov 16–22) — অবস্থা

- Plan (৫ post: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri
  LinkedIn) **2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" বাকি।**
  কিছু approve হয়নি, কিছু post হয়নি।
- Nov 9–15: **কিছু post হয়নি** (Nov 9–15 plan approve হয়নি)।
- LinkedIn = Boss নিজে post করেন (personal profile)।
- এই Chief Talvenor-এর weekly post-ও draft করতে পারে (content_plan /
  caption_write), কিন্তু publish শুধু Boss-এর "post it"-এ।

## Boss-এর কাছে যা বাকি (Phase 3-র বাকিটা খুলতে)

1. **PC GPU-র নাম** — FramePack/WanGP চলবে কি না জানাতে (2026-11-01 থেকে বাকি)।
2. **VOICE.md correction** — DRAFT ঠিক করা (প্রথম script-এর আগে)।
3. **Week 1 OBS recording** — Nano Banana 2-র ৫ test (verdict [FILL AFTER TEST])।
4. **Track 3 প্রশ্ন** — ToolPilot, নাকি brand-new channel? উত্তর এখনো আসেনি।
5. **Upload OAuth** — প্রথম real upload-এর আগে Boss-এর নিজের YouTube
   credential + "upload it"।
6. **Nov 16–22 plan-এ "ok"** — না হলে weekly cadence থামবে কি চলবে, সেটাও Boss-এর সিদ্ধান্ত।
