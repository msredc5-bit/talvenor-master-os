# BUSINESS-03 — Content Creation Studio OS (Media Wrapper)

**Date:** 2026-11-19 | **Status:** Wrapper doc — DRAFT, for Boss's review
**Source:** the brief Boss sent, `~/workspace/briefs/unified-business-os-2026-11-19.md` §4 (preserved as-is, not adopted as design — audited below)
**Points at:** `03-Content-Creation-Department/` (the Content division of the Master OS repo, Creator OS vendored)
**Rule of this file:** wrapper only — no new code, no new video, nothing published. The brief's 10 creative departments are mapped to EXISTING sections/agents; what does not exist is written honestly.

## Audit of the brief (what was wrong, fixed)

| What the brief said | True state |
|---|---|
| Media's own "Creative Brain" | **Wrong.** The three businesses have no separate live brains. **ONE brain: BrainFactory, mock default ($0)**; live MetaSpark UNPROVEN. There is a Content Chief, not a separate live brain. |
| 10 creative departments, 4–5 specialist agents each | **Not built.** Real structure: **5 sections + 10 section agents + 6 vendored workers** (see the map below). Most of the brief's agent roles have no worker. |
| Idea-to-Publishing pipeline — 9 steps, as a running workflow | **Wrong.** The real pipeline is **13 stages: REAL 0 / MOCK 10 / BLOCKED 3** — no stage gives a real finished output (see below). |
| The brief's image (external diagram) | **Not used** — external diagram, not even referenced in this wrapper. |

## Real structure (Phase 3 + Phase 7)

- **5 sections:** plan / produce / publish / analyze / growth
- **10 section agents** (verified `.py` files): TopicResearcher, ContentPlanner, ScriptWriter, VisualProducer, CaptionWriter, PublishPrep, PerformanceTracker, PerformanceAnalyst, GrowthAgent, RepurposeAgent
- **6 vendored workers** (Creator OS, `03-Content-Creation-Department/engine/workers/` — upstream `~/workspace/creator-os-combined/` canonical, no longer a runtime dependency)
- **Chief:** Content Chief REAL (Phase 3), calls 6 workers (mock brain, $0, draft-only)

## 10 Creative Departments — real map

| # | Creative Dept (brief) | Mapped to (real section / agent) | Status |
|---|---|---|---|
| 01 | Strategy & Research | plan section — TopicResearcher, ContentPlanner | MOCK — makes topic drafts, no live run of a research worker |
| 02 | Script & Copywriting | produce section — ScriptWriter | MOCK — `[MOCK DRAFT]` scaffold; **VOICE.md DRAFT — no script is final until Boss fixes it** |
| 03 | Image & Graphic Design | produce section — VisualProducer | MOCK — only a visual plan / shot list / thumbnail idea; not a real design file |
| 04 | AI Video Production | produce section — VisualProducer + stage 4 | **BLOCKED** — stage 4 video: the Chief only gives a production plan + missing-inputs list, does not render video. No real footage / OBS recording; AI video generation REGION-BLOCKED; Boss's PC GPU AMD Radeon integrated 496MB VRAM — FramePack/WanGP will not run |
| 05 | Audio & Voice Production | produce section — no dedicated audio worker | **GAP** — voiceover lines only sit inside scripts. Piper TTS is in the voice loop (offline, $0), not inside Creator OS |
| 06 | Social Media Management | publish section — CaptionWriter, PublishPrep | MOCK — **prep only, never posts**. Publishing only on Boss's "post it", from the main chat |
| 07 | SEO & Distribution | publish section — CaptionWriter (SEO part) + growth section — RepurposeAgent | MOCK — caption pack draft + repurpose draft; no distribution worker |
| 08 | Content QA | analyze section — PerformanceTracker, PerformanceAnalyst | MOCK — only a report template; **no published content exists, so there is nothing to review** |
| 09 | Audience Growth & Community | growth section — GrowthAgent, RepurposeAgent | MOCK — growth plan draft; **shorts_made 0**, no worker to reply in the community |
| 10 | Analytics & Monetization | analyze section — PerformanceTracker (template), PerformanceAnalyst | MOCK — **metrics 0**; ToolPilot 0 subs, 0 videos, YPP not reached |

## Idea-to-Publishing Pipeline — real 13 stages

Source: `03-Content-Creation-Department/pipeline.md` — **REAL 0 / MOCK 10 / BLOCKED 3**.

| # | Stage | Worker / Tool | State | What is still owed to Boss |
|---|---|---|---|---|
| 0a | Niche finder | yt-niche `niche_score.py` | MOCK | Nothing (not needed if the topic is known) |
| 0b | Plan | yt-plan (weekly plan) | MOCK | How many hours per week he will give — to be told |
| 1 | Research | TopicResearcher | MOCK | Nothing |
| 2a | Concept | `concept_score.py` (3–5 concepts, 1–10 score) | MOCK | Nothing |
| 2b | Script | ScriptWriter + hookscore.py | MOCK | **VOICE.md correction** — DRAFT, no script is final until Boss fixes it |
| 3 | Visual pack | VisualProducer + title.py | MOCK | Nothing |
| 4 | Video | Reel Factory (pluggable provider) | **BLOCKED** | **OBS recording / real footage** (Week 1's 5 tests), PC GPU name, or a paid video key (not in the $0 cap) |
| 5 | Edit | yt-edit (deadair, chapters, shorts) | **BLOCKED** | The video's transcript (comes once there is a video) |
| 6 | Caption + SEO | CaptionWriter + yt-seo | MOCK | Nothing |
| 7 | Publish prep | PublishPrep ONLY | MOCK | Boss's gate words: **"post it"** to post, **"upload it"** to upload |
| 8 | Report | PerformanceTracker + yt-retention | MOCK | No video published, so metrics 0 — Boss's real numbers, as sent by him, are needed |
| 9 | Upload | `upload_youtube.py` | **BLOCKED — DEFAULT OFF** | Boss's **"upload it"** + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth) — all three |
| 10 | Next plan | `loop_next.py` | MOCK | No report yet (videos 0) |

**Match with the brief's 9 steps:** Topic & Trend Research → stage 0a/1; Strategy & Planning → 0b/2a; Script & Storyboard → 2b; Image/Video/Audio Production → 3/4/5; Editing & Post Production → 5; Quality Check & Copyright Review → 8 (template only, no separate QA worker); Founder Approval → gate (Boss's ok at every stage); Publishing & Distribution → 7/9; Analytics & Monetization → 8/10.

**Honest limits:** Live-LLM brain unwired (only MockLLM runs; no key in any file, no network call). Captions are line-level — not word-level karaoke. Default stills + Ken Burns motion = not real motion.

## True state (Real Status Block — 2026-11-19)

Source: `03-Content-Creation-Department/toolpilot-status.md` (2026-11-16) + `pipeline.md`.

| Item | State |
|---|---|
| Channel | ToolPilot — https://www.youtube.com/@ToolPilotai69 (Channel ID: UCLGlqsDCLmcqis9pMCikC4Q), account sojibprodhan99@gmail.com |
| Niche | AI Tools & Tutorials — faceless, screen recording + AI voiceover, US viewers |
| Subscribers | **0** |
| Watch hours | **0** |
| Videos | **0** — no videos, monetization, or profile picture/banner yet |
| YPP bar | 1,000 subs + 4,000 hours, or 10M Shorts views (from 2027-02-01, new applications need 8,000 hours or 20M Shorts views) — not reached |
| Week 1 content | READY TO RECORD — Long video "Google's Nano Banana 2 Is Free - But Is It Good?" (full spoken script 1,431 words, ~9.5 min, 5 tests) + 2 Shorts; **verdict [FILL AFTER TEST]** — no verdict will be written without seeing Boss's real OBS recording |
| VOICE.md | **DRAFT** — Boss's correction remaining |
| Upload | **OFF** — needs Boss's "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own OAuth; no real YouTube upload verified yet |
| LinkedIn | **Boss posts himself** (personal profile) — no connector posts |
| Talvenor weekly social (Nov 16–22) | Plan (5 posts) given on 2026-11-15 at 18:00 — Boss's "ok" remaining; nothing approved, nothing posted |
| Track 3 question | **Boss's answer remaining** (since 2026-11-12): Track 3 = ToolPilot, or a brand-new channel? Until the answer comes, work assumes ToolPilot; no new channel is built |
| GPU | Boss's PC: AMD Radeon integrated, 496MB VRAM — FramePack/WanGP will not run; AI video generation REGION-BLOCKED |

## Cross-business work (what Media does for the others)

- Content Studio can make ad creatives / video drafts for the Agency — as an **internal project**, DRAFT-only; publishing only on Boss's "post it".
- Content Studio can make product creatives for the Digital Product — as an internal project; the Vet Kit is still a blueprint, so creative work has not started.
- Work and cost must be tracked as separate projects — but there is no billable work to track yet (all drafts, all $0).

## Next steps (on Boss's decision)

1. **VOICE.md correction** — Boss will fix it before the first script is final.
2. **Week 1 OBS recording** — 5 tests of Nano Banana 2 (Boss will record, then the verdict).
3. **Track 3 answer** — ToolPilot, or a brand-new channel?
4. **Upload OAuth + "upload it"** — before the first real upload.
5. **"ok" on the Nov 16–22 plan** — otherwise, whether the weekly cadence stops or continues is Boss's decision.

## What this wrapper does not do

- Renders no video, uploads no video, publishes no post.
- Calls no script final (while VOICE.md is DRAFT).
- Claims no view/subscriber/revenue numbers — all 0.
- Builds no new channel (until the Track 3 answer comes).
