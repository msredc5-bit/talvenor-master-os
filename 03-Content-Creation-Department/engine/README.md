# Content Engine — এক পাতায় (README.md)

**Engine:** Content Creation Engine (Creator OS) — ToolPilot @ToolPilotai69
**Channel:** AI Tools & Tutorials, faceless, US viewers
**Chief:** `../chief_of_staff_content.py` — REAL (Phase 3), ৬ task type → ৬ Creator OS worker (mock brain, $0)
**Source:** `~/workspace/creator-os-combined/` (REUSED — copy/move করা হয়নি)

## Staff — ৮ জন

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

বিস্তারিত: `STAFF.md`। Skill একটা করে: `skills/`-এ ৮টি file।

## Tools — ৮টি (`tools.json`)

- **Mock (৫):** draft_script, draft_caption, draft_email, research_notes, status_read — DRAFT ONLY, handler আছে।
- **Gated stub (৩):** publish_post (publish), upload_video (publish), spend (spend) — handler `null`, approval ছাড়া আটকে থাকে, এই engine কখনো চালায় না।

Wrapper: `tool_calling.py` — shared core (`00-CEO-Core/tool_calling.py`)-এ forward করে; `call(name, args)` আর `list_tools()`।

## Status — ১৩ stage: REAL 0 / MOCK 10 / BLOCKED 3

- **REAL 0** — কোনো stage-ই এখনো আসল finished output দেয় না; সব draft mock scaffold।
- **MOCK 10** — 0a-niche, 0b-plan, 1-research, 2a-concept, 2b-script, 3-visual-pack, 6-caption-seo, 7-publish-prep, 8-report, 10-next-plan।
- **BLOCKED 3** — stage 4-video (footage/GPU নেই), stage 5-edit (transcript নেই), stage 9-upload (DEFAULT OFF)।

ToolPilot: video **0**, subs **0**, watch hours **0**। Week 1 long video READY TO RECORD, verdict **[FILL AFTER TEST]**।

## কী আটকে আছে, কার উপর

| আটকে থাকা | কার উপর |
|---|---|
| Upload OFF | Boss-এর "upload it" + `YOUTUBE_UPLOAD_ENABLED=1` + Boss-এর নিজের YouTube credential (OAuth) — তিনটাই |
| VOICE.md DRAFT | Boss-এর correction — ঠিক না হওয়া পর্যন্ত কোনো script final নয় |
| GPU-র নাম | Boss-এর PC GPU নাম — 2026-11-01 থেকে জানা যায়নি (true AI motion-এর জন্য) |
| OBS recording | Week 1-এর ৫ test-এর Boss-এর OBS recording — verdict তারপর |
| Track 3 প্রশ্ন | ToolPilot নাকি brand-new channel — Boss-এর উত্তর বাকি (2026-11-12 থেকে) |
| Weekly plan "ok" | Nov 16–22 Talvenor plan (৫ post) — 2026-11-15 18:00-তে দেওয়া, Boss-এর "ok" বাকি |

## Gate

"ok" = plan/asset approval; "post it" = publish; "upload it" = upload; "send" = send; "go" = phase এগোনো। Boss-এর exact word ছাড়া কিছু হয় না — কোনো auto-approve নেই। $0 spend cap। LinkedIn = Boss নিজে post করেন।

## সৎ সীমা

- AI video generation এখানে REGION-BLOCKED — retry করা হয় না।
- Caption line-level, word-level karaoke নয়।
- Performance Analyst-এর এখনো কোনো আসল কাজ হয়নি — metric 0।
- পুরনো artifact page `creator-os-combined` STALE (৮ stage দেখায়, আসল ১৩) — Boss না বললে ঠিক করা হবে না।
