# Content Creation — Pipeline (13 stages, honest map)

**Engine:** Creator OS — vendored copy `03-Content-Creation-Department/engine/workers/` (Phase 6; upstream `~/workspace/creator-os-combined/`)
**Channel:** ToolPilot @ToolPilotai69 (faceless, AI Tools & Tutorials)
**Chief:** `chief_of_staff_content.py` — REAL (Phase 3), calls 6 workers (mock brain, $0)

## 13 stages — status

| # | Stage | Worker / Tool | Status | What is still pending with Boss |
|---|---|---|---|---|
| `0a-niche` | Niche finder | yt-niche `niche_score.py` | **MOCK** — runs when there is no topic, skipped otherwise | nothing (this stage is not needed when the topic is known) |
| `0b-plan` | Plan | yt-plan (weekly plan) | **MOCK** — makes a plan from hours | tell us how many hours a week you will give |
| `1-research` | Research | TopicResearcher | **MOCK** — topic draft from the mock brain | nothing |
| `2a-concept` | Concept | `concept_score.py` (3–5 concepts, 1–10 score) | **MOCK** — score scaffold | nothing |
| `2b-script` | Script | ScriptWriter + hookscore.py | **MOCK** — `[MOCK DRAFT]` scaffold | **VOICE.md correction** — DRAFT, no script is final until Boss fixes it |
| `3-visual-pack` | Visual+Pack | VisualProducer + title.py | **MOCK** — shot list + thumbnail idea | nothing |
| `4-video` | Video | Reel Factory (pluggable provider) | **BLOCKED** — the Chief only gives a production plan + missing-inputs list; it does not render video | **OBS recording / real footage** (Week 1's 5 tests), **PC GPU name** (for true AI motion — unknown since 2026-11-01), or a paid video key (not under the $0 cap) |
| `5-edit` | Edit | yt-edit (deadair, chapters, shorts) | **BLOCKED** — needs a transcript, there is no transcript yet | the video's transcript (it will come once there is a video) |
| `6-caption-seo` | Caption+SEO | CaptionWriter + yt-seo | **MOCK** — caption pack draft | nothing |
| `7-publish-prep` | Publish prep | PublishPrep ONLY | **MOCK** — checklist draft, `ready_to_publish: false` | Boss's gate word: **"post it"** to post, **"upload it"** to upload |
| `8-report` | Report | PerformanceTracker + yt-retention | **MOCK** — report template; post-publish only | no video has been published, so metrics are 0 — Boss's real numbers will be needed |
| `9-upload` | Upload | `upload_youtube.py` | **BLOCKED** — **DEFAULT OFF** | Boss's **"upload it"** + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth) — all three |
| `10-next-plan` | Next plan | `loop_next.py` | **MOCK** — reads the previous report and writes the next brief | no report yet (videos 0) |

**Count:** REAL **0** · MOCK **10** · STUB **0** · BLOCKED **3** (stages 4, 5, 9).
REAL 0 is the truth — no stage gives a real finished output yet; everything is a
mock scaffold. The Chief's job: make drafts + hold things at the gate, not render video
or upload.

## Honest limits (not hidden)

- **Live-LLM brain unwired** — the standalone runner runs MockLLM only; the live
  provider is deliberately unwired (no key in any file, no network
  call). The Agent (Elora/Muse) is itself the brain — the agent writes the real text.
- **VOICE.md DRAFT** — `03-Content-Creation-Department/VOICE.md`.
- **True AI video motion** — impossible without Boss's PC GPU (name unknown) or a paid
  key. AI video generation is REGION-BLOCKED here — no retry.
  Default stills + Ken Burns motion are not real motion.
- **Captions are line-level** — not word-level karaoke.
- **Upload OFF** — no real YouTube upload has been verified yet.
- **The old artifact page `creator-os-combined` is STALE** — it shows 8 stages,
  the real count is 13. It will not be fixed unless Boss says so.

## Talvenor weekly social (Nov 16–22) — status

- Plan (5 posts: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri
  LinkedIn) **was given 2026-11-15 18:00 — Boss's "ok" is pending.**
  Nothing is approved, nothing is posted.
- Nov 9–15: **nothing was posted** (the Nov 9–15 plan was not approved).
- LinkedIn = Boss posts himself (personal profile).
- This Chief can also draft Talvenor's weekly posts (content_plan /
  caption_write), but publishing happens only on Boss's "post it".

## What is still pending with Boss (to unlock the rest of Phase 3)

1. **PC GPU name** — to tell whether FramePack/WanGP will run (pending since 2026-11-01).
2. **VOICE.md correction** — fix the DRAFT (before the first script).
3. **Week 1 OBS recording** — Nano Banana 2's 5 tests (verdict [FILL AFTER TEST]).
4. **Track 3 question** — ToolPilot, or a brand-new channel? No answer yet.
5. **Upload OAuth** — before the first real upload, Boss's own YouTube
   credential + "upload it".
6. **"ok" on the Nov 16–22 plan** — otherwise whether the weekly cadence stops or continues is also Boss's decision.
