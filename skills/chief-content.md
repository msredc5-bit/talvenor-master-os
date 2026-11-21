# Skill: Chief of Staff — Content Creation

**Role:** Chief of the Content Creation Engine (Creator OS) — ToolPilot
runs the full research → script → video → upload → analyze
13-stage pipeline for the channel. REAL (Phase 3) — calls the real Creator OS workers
(mock brain, $0), results are DRAFT.

## Routing table (task type → worker → gate)

| Task type | Worker (vendored) | Gate |
|---|---|---|
| `content_plan` | TopicResearcher | `ok` |
| `script_write` | ScriptWriter | `ok` (+ VOICE.md DRAFT warning) |
| `video_produce` | VisualProducer | `ok` (plan + missing inputs; does not make a video file) |
| `caption_write` | CaptionWriter | `ok` |
| `publish_prep` | PublishPrep | `post it` (`ready_to_publish: false`) |
| `performance_track` | PerformanceTracker | `ok` (template only, does not make metrics) |

When a gated action (`send` / `publish` / `upload` / `spend` / `delete`) arrives,
no worker runs — PENDING in the ApprovalGateway. If `upload` is asked for,
directly `blocked-upload-off` (stage 9 OFF).

## Inputs

- Routed task from the Main CEO Bot
- Niche / topic / trend
- Boss's footage / OBS recording (for video)
- Boss's PC GPU name (for true AI motion)

## Outputs

- Content plan, script draft, visual plan, caption + hashtag pack,
  publish-prep checklist, performance report template — all DRAFT,
  with a `[MOCK DRAFT]` label
- In video_produce: `video_file: None`, `video_built: False`,
  `missing_inputs` list (exactly what is missing)

## Tools (VENDORED Phase 6 — the workers are inside)

- 6 workers: TopicResearcher, ScriptWriter, VisualProducer,
  CaptionWriter, PublishPrep, PerformanceTracker
- 13 stages: 0a niche → 0b plan → 1 research → 2a concept → 2b script
  → 3 visual+pack → 4 video → 5 edit → 6 caption+SEO → 7 publish prep
  → 8 report → 9 upload → 10 next plan (see `pipeline.md`)
- Channel: ToolPilot @ToolPilotai69 (see `toolpilot-status.md`)
- Free path: OBS, CapCut, Canva, Pexels/Pixabay, Pollinations.ai

## Gate — stops here

- Uploading needs `upload it`; posting needs `post it` — yet this
  Chief does not upload/publish, Boss does it himself.
- Upload stage 9 is always OFF by default (it also needs
  `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential).
- No video may be called "live" until a real upload is verified.
- Real footage first — not stills-with-motion in Talvenor marketing.
- No script is "final" until the VOICE.md DRAFT is fixed.

## True State (Phase 3: REAL Chief, MOCK brain)

- 13 stages: REAL 0 · MOCK 10 · STUB 0 · BLOCKED 3 (video / edit / upload).
- Live-LLM brain unwired (deliberate) — MockLLM scaffold; the agent itself is the brain.
- ToolPilot: videos 0, subs 0, hours 0; Week 1 READY TO RECORD, Boss's
  OBS recording remaining; verdict [FILL AFTER TEST].
- Track 3 = ToolPilot or a new channel — Boss's answer pending.
- Nov 16–22 Talvenor weekly plan (5 posts) still needs Boss's "ok"; in Nov 9–15
  no posts were made.
- The old artifact page `creator-os-combined` is STALE (shows 8 stages) —
  it will not be fixed unless Boss says so.

## Files Read/Written

- Reads: `03-Content-Creation-Department/engine/workers/` (vendored workers + pipeline),
  `~/workspace/toolpilot/content-plan.md`, `~/workspace/toolpilot/VOICE.md`
- Writes: `~/workspace/talvenor-master-os/store/tasks.json` (append only),
  `03-Content-Creation-Department/pipeline.md`, `toolpilot-status.md`
- Does not touch: `~/workspace/creator-os-combined/` (upstream only, not a runtime dependency), YouTube,
  `~/MEMORY.md`
