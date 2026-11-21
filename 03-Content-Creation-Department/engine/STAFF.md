# Content Engine — Staff Roster (STAFF.md)

**Engine:** Content Creation Engine (Creator OS) — `03-Content-Creation-Department/engine/`
**Channel:** ToolPilot @ToolPilotai69 — AI Tools & Tutorials, faceless, US viewers
**Chief:** `../chief_of_staff_content.py` — REAL (Phase 3), 6 task types → 6 Creator OS workers
**Brain:** MockLLM (mock brain, $0) — all output `[MOCK DRAFT]`, DRAFT ONLY
**13 stages:** REAL **0** / MOCK **10** / BLOCKED **3** (stage 4 video, stage 5 edit, stage 9 upload)

**Rules (for everyone):** no staff member publishes, uploads, sends mail, spends, or deletes. Gate words come only from Boss's mouth — "ok" / "post it" / "upload it" / "send" / "go". No auto-approve. $0 spend cap. No invented client / stat / testimonial / price. Brand is Talvenor only.

---

## 1. Topic Researcher (TopicResearcher)

- **Worker:** `TopicResearcher` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `topic_research`, gate `ok`)
- **What it does:** takes the CEO's decision and picks 3 content topics for the niche + audience — each with its angle, why it fits, and what the next research step is. Stage 1-research + 0a-niche (`tools/niche_score.py`, 1–10 score on 4 axes) + 2a-concept (`tools/concept_score.py`, 3–5 concepts, 1–10 score).
- **Input:** niche (e.g. "AI Tools & Tutorials"), audience (US viewers), Boss's trend/topic if given.
- **Output:** 3 topic drafts — with angle + fit + next-research-step, labelled `[MOCK DRAFT]`.
- **Gate:** `ok` — no topic is final without Boss's "ok".
- **Honest limits:** Mock brain — it does not read real trend data; scores are a scaffold only. If the niche is known, stage 0a is skipped.

## 2. Script Writer (ScriptWriter)

- **Worker:** `ScriptWriter` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `script_write`, gate `ok`)
- **What it does:** turns the chosen topic into a script — hook in the first 2 seconds, one clear idea, simple CTA. Method: `youtube-skills/yt-script/` — write 5 hooks from 21 formulas, score them with `hookscore.py`, show the best 2; in the first 15 seconds confirm the title's promise + open one question + prove there is a payoff.
- **Input:** topic, format (short video / long video), VOICE.md.
- **Output:** Script draft — hook options (with scores) + full spoken script, `[MOCK DRAFT]`.
- **Gate:** `ok` — a script may not be used without Boss's "ok".
- **⚠️ Honest limits — VOICE.md DRAFT:** `03-Content-Creation-Department/VOICE.md` is still DRAFT — no script is "final" until Boss fixes it. Boss has no YouTube video yet, so there is no real transcript to copy from. Boss does not speak live English — read-aloud scripts need Bengali transliteration under each English line. Week 1 long video ("Google's Nano Banana 2 Is Free - But Is It Good?") is READY TO RECORD, but the verdict is **[FILL AFTER TEST]** — no verdict will be written until Boss's OBS recording of the 5 tests is seen.

## 3. Visual Producer (VisualProducer)

- **Worker:** `VisualProducer` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `visual_produce`, gate `ok`)
- **What it does:** makes a visual plan — shot list, thumbnail idea, on-screen text (verbatim, short, readable). Stage 3-visual-pack (`youtube-skills/yt-package/title.py` — title + thumbnail linted together) and the stage 4-video production plan + missing-inputs checklist.
- **Input:** topic, format, script (if there is one), footage / voiceover line / GPU name (if there is one).
- **Output:** Visual plan draft + stage 4 missing-inputs list. `video_file` is always **None** — this role does not make a video file.
- **Gate:** `ok`.
- **Honest limits:** Stage 4 **BLOCKED** — no real footage / OBS recording, Boss's PC GPU name **unknown since 2026-11-01** (needed for true AI video motion), AI video generation is **REGION-BLOCKED here — no retry**. Default stills + Ken Burns motion are not real motion. If a shot cannot be filmed, that must be said; nothing may be faked.

## 4. Caption Writer (CaptionWriter)

- **Worker:** `CaptionWriter` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `caption_write`, gate `ok`)
- **What it does:** writes a caption + hashtag pack per platform — hook in the first line, one CTA, hashtags (Instagram 5–8, LinkedIn 3, Facebook 0–2). Stage 6-caption-seo (`youtube-skills/yt-seo/` — description + tags, for real search queries).
- **Input:** topic, platform (YouTube / Facebook / Instagram / LinkedIn), draft of the video/post.
- **Output:** Caption pack draft — platform-wise caption + hashtag + CTA, `[MOCK DRAFT]`.
- **Gate:** `ok`.
- **Honest limits:** Captions are **line-level** — not word-level karaoke (a Creator OS limit). Posting on any platform is not this role's job.

## 5. Publish Prep (PublishPrep)

- **Worker:** `PublishPrep` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `publish_prep`, gate `post it`)
- **What it does:** prepares the post for publishing — final checklist: hook, readable text, no invented claim, platform, best posting time. Stage 7-publish-prep. It does not publish — it only gives a checklist draft.
- **Input:** finished post/video draft, caption pack, platform, posting time.
- **Output:** Publish-prep checklist draft, `ready_to_publish: False`.
- **Gate:** **`post it`** (for video upload, **`upload it`**) — nothing is published/uploaded without Boss's exact word, and even then Boss does it himself.
- **Honest limits:** Upload stage 9 is **DEFAULT OFF** — all three are needed: Boss's "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth). This engine never runs `upload_youtube.py`. LinkedIn = Boss posts himself (personal profile).

## 6. Performance Tracker (PerformanceTracker)

- **Worker:** `PerformanceTracker` — `03-Content-Creation-Department/engine/workers/src/creator_workers.py` (task_kind `performance_track`, gate `ok`)
- **What it does:** makes the **template/setup** for a performance report — which metric to take from where, best/worst comparison, one change for next week. Stage 8-report (`youtube-skills/yt-retention/retention.py` — reads a retention CSV to find the hook leak).
- **Input:** topic/video, Boss's real platform numbers if sent.
- **Output:** Report template draft — list of metrics + comparison format + one change, `[MOCK DRAFT]`.
- **Gate:** `ok`.
- **Honest limits:** no video has been published yet — metrics **0** (subs 0, hours 0, videos 0). Numbers are never estimated — only Boss's real platform numbers are used. Different from Performance Analyst: the Tracker makes the setup/template, the Analyst analyzes the real numbers.

## 7. Content Planner (ContentPlanner)

- **Worker:** no worker — Chief-level role. Method source: `youtube-skills/yt-plan/SKILL.md` (weekly plan — anchor video + cheap video, asks for Boss's real hours) + `scripts/loop_next.py` (stage 10-next-plan — reads the previous report and writes the next brief) + `../pipeline.md`.
- **What it does:** makes a weekly / monthly content plan — what gets posted, when, in which order, per Boss's real capacity. The Talvenor weekly social plan (5 posts) and ToolPilot's rhythm (1 long/week + 2 Shorts/week) — both are this role's work.
- **Input:** last week's report (if there is one), Boss's hours, list of half-made content, niche/topic.
- **Output:** Weekly plan draft — table of pillar + format + platform + posting time, `[MOCK DRAFT]`.
- **Gate:** `ok` — no plan runs without Boss's "ok" or edits.
- **Honest limits:** **Nov 16–22 Talvenor weekly plan (5 posts: Mon Reel, Tue Carousel, Wed Image, Thu Carousel, Fri LinkedIn) was given 2026-11-15 18:00 — Boss's "ok" is still pending.** Nothing was posted Nov 9–15 (the plan was not approved). No metric/claim is invented inside a plan.

## 8. Performance Analyst (PerformanceAnalyst)

- **Worker:** no worker — Chief-level role. Method source: `youtube-skills/yt-retention/SKILL.md` (retention graph — hook leak, below 25% in the first 30 seconds is healthy) + `youtube-skills/yt-audit/` + PerformanceTracker's template + `../pipeline.md` stage 8-report.
- **What it does:** analyzes the real performance of **published** content — reads Boss's real metrics (views, retention, CTR, subs) and writes where viewers drop off, why they drop off, and exactly what to change in the next video.
- **Input:** Boss's real platform numbers / retention CSV / YouTube Studio export.
- **Output:** Analysis draft — where the leak is, why, and one concrete change for next week.
- **Gate:** `ok` — the analysis is shown to Boss, Boss decides.
- **Honest limits:** **No video has been published yet, so there is no real metric to analyze — this role has had no real work yet.** No analysis is written without numbers; if Boss does not send metrics, the role just says "metrics pending" and stops. Different from Performance Tracker: the Tracker makes the tracking setup/template, the Analyst draws decisions from the real numbers.

---

## Role → Chief task type map

| Staff | Chief task type | Worker |
|---|---|---|
| Topic Researcher | `content_plan` | TopicResearcher |
| Script Writer | `script_write` | ScriptWriter |
| Visual Producer | `video_produce` | VisualProducer |
| Caption Writer | `caption_write` | CaptionWriter |
| Publish Prep | `publish_prep` | PublishPrep |
| Performance Tracker | `performance_track` | PerformanceTracker |
| Content Planner | — (Chief-level) | no worker |
| Performance Analyst | — (Chief-level) | no worker |

**Staff count: 10.** Section agents for 10 people — 6 wrapped (Topic Researcher,
Script Writer, Visual Producer, Caption Writer, Publish Prep, Performance
Tracker) + 4 standalone (Content Planner, Performance Analyst, Growth Agent,
Repurpose Agent).

---

## Phase 7 — Section map (2026-11-17)

In Phase 7, one section agent + one section skill was made for each of the 8 staff —
`03-Content-Creation-Department/sections/<section>/`. In the 2026-11-21 sweep, the Chief's 6 worker
routings also go through section agents
(WRAPPED agents wrap the same vendored worker — the Chief's outward
contract stays as before); 4 new task types (`plan_weekly`,
`performance_analyze`, `growth_research`, `repurpose_plan`) go to section agents via the Chief's
`SECTION_ROUTING`. The truth of the 13 stages stays the same:
REAL **0** / MOCK **10** / BLOCKED **3**; upload OFF; VOICE.md DRAFT; metrics 0.

| Section | Staff | Agent file | Wrapped worker / Standalone | Skill file | Gate | Status |
|---|---|---|---|---|---|---|
| plan | Topic Researcher | `sections/plan/agents/topic_researcher.py` | `TopicResearcher` | `sections/plan/skills/topic-researcher.md` | ok | WRAPPED |
| plan | Content Planner | `sections/plan/agents/content_planner.py` | Standalone (Chief-level) | `sections/plan/skills/content-planner.md` | ok | WRAPPED* |
| produce | Script Writer | `sections/produce/agents/script_writer.py` | `ScriptWriter` | `sections/produce/skills/script-writer.md` | ok | WRAPPED |
| produce | Visual Producer | `sections/produce/agents/visual_producer.py` | `VisualProducer` | `sections/produce/skills/visual-producer.md` | ok | WRAPPED |
| publish | Caption Writer | `sections/publish/agents/caption_writer.py` | `CaptionWriter` | `sections/publish/skills/caption-writer.md` | ok | WRAPPED |
| publish | Publish Prep | `sections/publish/agents/publish_prep.py` | `PublishPrep` | `sections/publish/skills/publish-prep.md` | post it | WRAPPED |
| analyze | Performance Tracker | `sections/analyze/agents/performance_tracker.py` | `PerformanceTracker` | `sections/analyze/skills/performance-tracker.md` | ok | WRAPPED |
| analyze | Performance Analyst | `sections/analyze/agents/performance_analyst.py` | Standalone (Chief-level) | `sections/analyze/skills/performance-analyst.md` | ok | WRAPPED* |
| growth | Growth Agent | `sections/growth/agents/growth_agent.py` | Standalone (NEW) | `sections/growth/skills/growth-agent.md` | send | NEW |
| growth | Repurpose Agent | `sections/growth/agents/repurpose_agent.py` | Standalone (NEW) | `sections/growth/skills/repurpose-agent.md` | ok | NEW |

* Content Planner and Performance Analyst have no vendored worker — Chief-level
roles, so in Phase 7 they were made as standalone agents. Growth Agent and Repurpose
Agent are fully NEW roles — before, the engine had no staff/worker/skill for them.

**Section count: 5** (plan, produce, publish, analyze, growth) — **agent 10, skill 10.**
All agents are DRAFT ONLY (mock brain, $0), write no file, touch no network, and
do not publish/upload/send/spend/delete anything.
