# BUSINESS-03 — Content Creation Studio OS (Media Wrapper)

**তারিখ:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, Boss-এর review-এর জন্য
**Source:** Boss-এর পাঠানো brief `~/workspace/briefs/unified-business-os-2026-11-19.md` §4 (as-is সংরক্ষিত, design হিসেবে adopt করা হয়নি — নিচে audit করা হয়েছে)
**Points at:** `03-Content-Creation-Department/` (Master OS repo-র Content বিভাগ, Creator OS vendored)
**এই ফাইলের নিয়ম:** শুধু wrapper — নতুন code নয়, নতুন video নয়, কিছু publish নয়। Brief-এর ১০টি creative department-কে EXISTING section/agent-এর সাথে map করা হয়েছে; যা নেই তা সৎভাবে লেখা।

## Brief-এর audit (যা ভুল ছিল, ঠিক করা হয়েছে)

| Brief-এ যা ছিল | সত্য অবস্থা |
|---|---|
| Media-র নিজস্ব "Creative Brain" | **ভুল।** তিন ব্যবসার আলাদা live brain নেই। **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN। Content Chief আছেন, আলাদা live brain নয়। |
| ১০টি creative department, প্রতিটিতে ৪–৫ জন specialist agent | **বানানো হয়নি।** আসল structure: **৫টি section + ১০টি section agent + ৬টি vendored worker** (নিচে map দেখুন)। Brief-এর বেশিরভাগ agent role-এর worker নেই। |
| Idea-to-Publishing pipeline — ৯ ধাপ, চালু workflow হিসেবে | **ভুল।** আসল pipeline **১৩ stage: REAL 0 / MOCK 10 / BLOCKED 3** — কোনো stage-ই আসল finished output দেয় না (নিচে দেখুন)। |
| Brief-এর ছবি (external diagram) | **ব্যবহার করা হয়নি** — external diagram, এই wrapper-এ reference-ও নেই। |

## আসল Structure (Phase 3 + Phase 7)

- **৫টি section:** plan / produce / publish / analyze / growth
- **১০টি section agent** (যাচাইকৃত `.py` ফাইল): TopicResearcher, ContentPlanner, ScriptWriter, VisualProducer, CaptionWriter, PublishPrep, PerformanceTracker, PerformanceAnalyst, GrowthAgent, RepurposeAgent
- **৬টি vendored worker** (Creator OS, `03-Content-Creation-Department/engine/workers/` — upstream `~/workspace/creator-os-combined/` canonical, আর runtime dependency নয়)
- **Chief:** Content Chief REAL (Phase 3), ৬ worker ডাকেন (mock brain, $0, draft-only)

## ১০টি Creative Department — আসল Map

| # | Creative Dept (brief) | Mapped to (আসল section / agent) | Status |
|---|---|---|---|
| 01 | Strategy & Research | plan section — TopicResearcher, ContentPlanner | MOCK — topic draft বানায়, research worker-এর live run নেই |
| 02 | Script & Copywriting | produce section — ScriptWriter | MOCK — `[MOCK DRAFT]` scaffold; **VOICE.md DRAFT — Boss ঠিক না করা পর্যন্ত কোনো script final নয়** |
| 03 | Image & Graphic Design | produce section — VisualProducer | MOCK — visual plan / shot list / thumbnail idea মাত্র; আসল design file নয় |
| 04 | AI Video Production | produce section — VisualProducer + stage 4 | **BLOCKED** — stage 4 video: Chief শুধু production plan + missing-inputs list দেয়, video render করে না। Real footage / OBS recording নেই; AI video generation REGION-BLOCKED; Boss-এর PC GPU AMD Radeon integrated 496MB VRAM — FramePack/WanGP চলবে না |
| 05 | Audio & Voice Production | produce section — কোনো dedicated audio worker নেই | **GAP** — voiceover line script-এর ভেতরে থাকে মাত্র। Piper TTS voice loop-এ আছে (offline, $0), Creator OS-এর ভেতরে নয় |
| 06 | Social Media Management | publish section — CaptionWriter, PublishPrep | MOCK — **prep only, কখনো post করে না**। Publish শুধু Boss-এর "post it"-এ, main chat থেকে |
| 07 | SEO & Distribution | publish section — CaptionWriter (SEO part) + growth section — RepurposeAgent | MOCK — caption pack draft + repurpose draft; কোনো distribution worker নেই |
| 08 | Content QA | analyze section — PerformanceTracker, PerformanceAnalyst | MOCK — report template মাত্র; **কোনো published content নেই, তাই review করার মতো কিছু নেই** |
| 09 | Audience Growth & Community | growth section — GrowthAgent, RepurposeAgent | MOCK — growth plan draft; **shorts_made 0**, community-তে reply করার worker নেই |
| 10 | Analytics & Monetization | analyze section — PerformanceTracker (template), PerformanceAnalyst | MOCK — **metrics 0**; ToolPilot 0 subs, 0 videos, YPP পৌঁছায়নি |

## Idea-to-Publishing Pipeline — আসল ১৩ Stage

Source: `03-Content-Creation-Department/pipeline.md` — **REAL 0 / MOCK 10 / BLOCKED 3**।

| # | Stage | Worker / Tool | অবস্থা | Boss-এর কাছে যা বাকি |
|---|---|---|---|---|
| 0a | Niche finder | yt-niche `niche_score.py` | MOCK | কিছু না (topic জানা থাকলে লাগে না) |
| 0b | Plan | yt-plan (weekly plan) | MOCK | সপ্তাহে কত ঘণ্টা দেবেন — জানানো |
| 1 | Research | TopicResearcher | MOCK | কিছু না |
| 2a | Concept | `concept_score.py` (৩–৫ concept, ১–১০ score) | MOCK | কিছু না |
| 2b | Script | ScriptWriter + hookscore.py | MOCK | **VOICE.md correction** — DRAFT, Boss ঠিক না করা পর্যন্ত কোনো script final নয় |
| 3 | Visual pack | VisualProducer + title.py | MOCK | কিছু না |
| 4 | Video | Reel Factory (pluggable provider) | **BLOCKED** | **OBS recording / real footage** (Week 1-এর ৫ test), PC GPU নাম, অথবা paid video key ($0 cap-এ নয়) |
| 5 | Edit | yt-edit (deadair, chapters, shorts) | **BLOCKED** | video-র transcript (video হলেই আসবে) |
| 6 | Caption + SEO | CaptionWriter + yt-seo | MOCK | কিছু না |
| 7 | Publish prep | PublishPrep ONLY | MOCK | Boss-এর gate word: post করতে **"post it"**, upload করতে **"upload it"** |
| 8 | Report | PerformanceTracker + yt-retention | MOCK | কোনো video publish হয়নি, তাই metric 0 — Boss-এর পাঠানো আসল সংখ্যা লাগবে |
| 9 | Upload | `upload_youtube.py` | **BLOCKED — DEFAULT OFF** | Boss-এর **"upload it"** + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth) — তিনটাই |
| 10 | Next plan | `loop_next.py` | MOCK | কোনো report নেই এখনো (video 0) |

**Brief-এর ৯ ধাপের সাথে মিল:** Topic & Trend Research → stage 0a/1; Strategy & Planning → 0b/2a; Script & Storyboard → 2b; Image/Video/Audio Production → 3/4/5; Editing & Post Production → 5; Quality Check & Copyright Review → 8 (template মাত্র, আলাদা QA worker নেই); Founder Approval → gate (সব stage-এ Boss-এর ok); Publishing & Distribution → 7/9; Analytics & Monetization → 8/10।

**সৎ সীমা:** Live-LLM brain unwired (MockLLM-ই চলে; কোনো key ফাইলে নেই, কোনো network call নেই)। Captions line-level — word-level karaoke নয়। Default stills + Ken Burns motion = সত্যিকারের motion নয়।

## সত্য অবস্থা (Real Status Block — 2026-11-19)

Source: `03-Content-Creation-Department/toolpilot-status.md` (2026-11-16) + `pipeline.md`।

| জিনিস | অবস্থা |
|---|---|
| Channel | ToolPilot — https://www.youtube.com/@ToolPilotai69 (Channel ID: UCLGlqsDCLmcqis9pMCikC4Q), account sojibprodhan99@gmail.com |
| Niche | AI Tools & Tutorials — faceless, screen recording + AI voiceover, US viewers |
| Subscribers | **0** |
| Watch hours | **0** |
| Videos | **0** — কোনো video, monetization, profile picture/banner এখনো নেই |
| YPP bar | 1,000 subs + 4,000 hours, অথবা 10M Shorts views (2027-02-01 থেকে নতুন আবেদনে 8,000 hours অথবা 20M Shorts views) — পৌঁছায়নি |
| Week 1 content | READY TO RECORD — Long video "Google's Nano Banana 2 Is Free - But Is It Good?" (full spoken script ১,৪৩১ words, ~৯.৫ min, ৫ test) + ২ Shorts; **verdict [FILL AFTER TEST]** — Boss-এর আসল OBS recording না দেখে verdict লেখা হবে না |
| VOICE.md | **DRAFT** — Boss-এর correction বাকি |
| Upload | **OFF** — needs Boss-এর "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের OAuth; কোনো real YouTube upload এখনো verify হয়নি |
| LinkedIn | **Boss নিজে post করেন** (personal profile) — কোনো connector post করে না |
| Talvenor weekly social (Nov 16–22) | Plan (৫ post) 2026-11-15 18:00-তে দেওয়া হয়েছে — Boss-এর "ok" বাকি; কিছু approve হয়নি, কিছু post হয়নি |
| Track 3 প্রশ্ন | **Boss-এর উত্তর বাকি** (2026-11-12 থেকে): Track 3 = ToolPilot, নাকি brand-new channel? উত্তর না আসা পর্যন্ত ToolPilot-ই ধরে কাজ, নতুন channel বানানো হয় না |
| GPU | Boss-এর PC: AMD Radeon integrated, 496MB VRAM — FramePack/WanGP চলবে না; AI video generation REGION-BLOCKED |

## Cross-Business কাজ (Media অন্যদের জন্য কী করে)

- Content Studio Agency-র জন্য ad creative / video draft বানাতে পারে — **internal project** হিসেবে, DRAFT-only; publish শুধু Boss-এর "post it"-এ।
- Content Studio Digital Product-এর জন্য product creative বানাতে পারে — internal project হিসেবে; Vet Kit এখনো blueprint, তাই creative-র কাজ শুরু হয়নি।
- কাজ ও খরচ আলাদা project হিসেবে track করতে হবে — কিন্তু এখনো track করার মতো billable কাজ নেই (সব draft, সব $0)।

## পরের ধাপ (Boss-এর সিদ্ধান্তে)

1. **VOICE.md correction** — প্রথম script final হওয়ার আগে Boss ঠিক করবেন।
2. **Week 1 OBS recording** — Nano Banana 2-র ৫ test (Boss রেকর্ড করবেন, তারপর verdict)।
3. **Track 3 উত্তর** — ToolPilot, নাকি brand-new channel?
4. **Upload OAuth + "upload it"** — প্রথম real upload-এর আগে।
5. **Nov 16–22 plan-এ "ok"** — না হলে weekly cadence থামবে কি চলবে, Boss-এর সিদ্ধান্ত।

## যা এই wrapper করে না

- কোনো video render করে না, কোনো video upload করে না, কোনো post publish করে না।
- কোনো script-কে final বলে না (VOICE.md DRAFT থাকতে)।
- কোনো view/subscriber/revenue সংখ্যার দাবি করে না — সব 0।
- কোনো নতুন channel বানায় না (Track 3 উত্তর না আসা পর্যন্ত)।
