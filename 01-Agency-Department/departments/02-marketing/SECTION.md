# 02 — Marketing Department

## Purpose

Talvenor's organic marketing in one place: content plan, video produce,
caption write, and publish prep. The same idea is adapted for Facebook, Instagram, LinkedIn —
not three different ideas on three platforms. This department only makes plans and
DRAFTs — it posts nothing itself.

## Manager

- **Marketing Director Agent** — `MarketingDirectorAgent`, task_kind `manage_marketing`, gate `ok`
- Manager file: `01-Agency-Department/departments/02-marketing/manager/marketing_director_agent.py`
- Skill file: `01-Agency-Department/departments/02-marketing/skills/marketing-director-agent.md`
- The manager loads and runs the Phase 3 specialists (DRAFT only), posts nothing itself; it does not execute the engine/section's old workers.
- Agency Chief wiring **Phase 2 DONE** — the Chief now calls this manager via DEPARTMENT_ROUTING.

## Mapped Existing Staff (4)

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| ContentPlanner | `content_plan` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | ok | EXISTING |
| VideoProducer | `video_produce` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | ok | EXISTING |
| CaptionWriter | `caption_write` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | none | EXISTING |
| PublishPrep | `publish_prep` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | post it | EXISTING |

Note: PublishPrep only does **prep** — it never posts. The real publish is done by Boss
after the "post it" approval, by hand.

Phase 3 (2026-11-19) standalone specialists — 4 more EXISTING:
Market Positioning Agent (`market_position`), Social Media Agent
(`social_manage`, planning draft only, NEVER posts), SEO Agent (`seo`),
Analytics Agent (`analytics`) — all in `departments/02-marketing/specialists/`
, gate none, DRAFT only. The manager loads them with importlib.

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Market Positioning Agent | EXISTING — Market Positioning Agent | `market_position`, gate none | `departments/02-marketing/specialists/market_positioning_agent.py` |
| Content Strategy Agent | EXISTING — ContentPlanner | `content_plan`, gate ok |
| Social Media Agent | EXISTING — Social Media Agent | `social_manage`, gate none | `departments/02-marketing/specialists/social_media_agent.py` — planning draft only, NEVER posts; PublishPrep only does prep, never posts |
| Ad Campaign Agent | EXISTING — Ad Campaign Agent | `ad_campaign`, gate ok | `departments/02-marketing/specialists/ad_campaign_agent.py` — paid ad DRAFT plan + analysis only, not a live ad, $0 spend cap |
| Copywriting Agent | EXISTING — CaptionWriter | `caption_write`, gate none |
| Video Creative Agent | EXISTING — VideoProducer | `video_produce`, gate ok |
| SEO Agent | EXISTING — SEO Agent | `seo`, gate none | `departments/02-marketing/specialists/seo_agent.py` |
| Analytics Agent | EXISTING — Analytics Agent | `analytics`, gate none | `departments/02-marketing/specialists/analytics_agent.py` — visible metrics only, never an estimate; weekly reporting is under ReportCompiler (Finance & Admin, dept 07) |

## Missing Roles

- No missing role — Ad Campaign Agent built on 2026-11-21 (skill + worker EXISTING).

## Honest Status

- **Paying clients: 0** — there is still no paying client.
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; all output is DRAFT.
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — this is the DB, no other database.
- **Publish gate "post it"** — nothing is published without Boss's exact word.
- **Paid ads: DRAFT plan only** — $0 spend cap; no ad spend, no live ad.
- **Weekly report** is not this department's work — ReportCompiler (Finance & Admin) does it.
- **$0 spend cap** — nothing is spent.
- **Agency Chief wiring Phase 2 DONE** — the Chief now calls this department's manager via DEPARTMENT_ROUTING.
- **Pricing LOCKED, internal only** — prices are never stated in public content.
- **No dental/medical ever** — dental/medical or patient-health businesses are not a target.
- Brand **Talvenor only**. No invented client, price, statistic, testimonial, or guarantee.
