# Content Engine — on one page (README.md)

**Engine:** Content Creation Engine (Creator OS) — ToolPilot @ToolPilotai69
**Channel:** AI Tools & Tutorials, faceless, US viewers
**Chief:** `../chief_of_staff_content.py` — REAL (Phase 3), 6 task types → 6 Creator OS workers (mock brain, $0)
**Source:** `03-Content-Creation-Department/engine/workers/` (VENDORED Phase 6; upstream `~/workspace/creator-os-combined/` stays canonical)

## Staff — 8 people

| # | Role | Worker |
|---|---|---|
| 1 | Topic Researcher | TopicResearcher |
| 2 | Script Writer | ScriptWriter |
| 3 | Visual Producer | VisualProducer |
| 4 | Caption Writer | CaptionWriter |
| 5 | Publish Prep | PublishPrep |
| 6 | Performance Tracker | PerformanceTracker |
| 7 | Content Planner | no worker — Chief-level role |
| 8 | Performance Analyst | no worker — Chief-level role |

Details: `STAFF.md`. One skill each: 8 files in `skills/`.

## Tools — 8 (`tools.json`)

- **Mock (5):** draft_script, draft_caption, draft_email, research_notes, status_read — DRAFT ONLY, has a handler.
- **Gated stub (3):** publish_post (publish), upload_video (publish), spend (spend) — handler `null`, held without approval, this engine never runs them.

Wrapper: `tool_calling.py` — forwards to the shared core (`00-CEO-Core/tool_calling.py`); `call(name, args)` and `list_tools()`.

## Status — 13 stages: REAL 0 / MOCK 10 / BLOCKED 3

- **REAL 0** — no stage gives a real finished output yet; all are draft mock scaffolds.
- **MOCK 10** — 0a-niche, 0b-plan, 1-research, 2a-concept, 2b-script, 3-visual-pack, 6-caption-seo, 7-publish-prep, 8-report, 10-next-plan.
- **BLOCKED 3** — stage 4-video (no footage/GPU), stage 5-edit (no transcript), stage 9-upload (DEFAULT OFF).

ToolPilot: video **0**, subs **0**, watch hours **0**. Week 1 long video READY TO RECORD, verdict **[FILL AFTER TEST]**.

## What is blocked, and on whom

| Blocked item | Depends on |
|---|---|
| Upload OFF | Boss's "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube credential (OAuth) — all three |
| VOICE.md DRAFT | Boss's correction — no script is final until it is fixed |
| GPU name | Boss's PC GPU name — unknown since 2026-11-01 (needed for true AI motion) |
| OBS recording | Boss's OBS recording of Week 1's 5 tests — verdict after that |
| Track 3 question | ToolPilot or a brand-new channel — Boss's answer pending (since 2026-11-12) |
| Weekly plan "ok" | Nov 16–22 Talvenor plan (5 posts) — given 2026-11-15 18:00, Boss's "ok" pending |

## Gate

"ok" = plan/asset approval; "post it" = publish; "upload it" = upload; "send" = send; "go" = move the phase forward. Nothing happens without Boss's exact word — no auto-approve. $0 spend cap. LinkedIn = Boss posts himself.

## Honest limits

- AI video generation is REGION-BLOCKED here — no retry.
- Captions are line-level, not word-level karaoke.
- Performance Analyst has had no real work yet — metrics 0.
- The old artifact page `creator-os-combined` is STALE (shows 8 stages, the real count is 13) — it will not be fixed unless Boss says so.
