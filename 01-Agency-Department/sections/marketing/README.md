# Marketing section — why agents/ + skills/ are empty

`sections/marketing/agents/` and `sections/marketing/skills/` are deliberately
empty — this is not missing work.

The marketing section's 4 staff (ContentPlanner, VideoProducer,
CaptionWriter, PublishPrep) are **MAPPED** — they come from the engine, with no section-local
agent/skill by design:

- Worker: `01-Agency-Department/engine/workers/src/workers/marketing.py`
- Skills: `01-Agency-Department/engine/skills/` (`content-planner.md`,
  `video-producer.md`, `caption-writer.md`, `publish-prep.md`)

Detailed roster: `SECTION.md`. In Phase 7, no NEW agent was added to the marketing section —
the 4 mapped staff are the whole roster.

(Note: 2026-11-21, completion sweep — so the next audit does not see the empty dirs
and think GAP again — that is why this README exists.)
