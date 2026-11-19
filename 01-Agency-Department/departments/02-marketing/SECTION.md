# 02 — Marketing Department

## উদ্দেশ্য (Purpose)

Talvenor-এর organic marketing এক জায়গায় রাখা: content plan, video produce,
caption write, আর publish prep। একই idea Facebook, Instagram, LinkedIn-এ
adapt করা — তিন platform-এ তিন আলাদা idea নয়। এই department শুধু plan আর
DRAFT বানায় — নিজে কিছু post করে না।

## Manager

- **Marketing Director Agent** — `MarketingDirectorAgent`, task_kind `manage_marketing`, gate `ok`
- Manager file: `01-Agency-Department/departments/02-marketing/manager/marketing_director_agent.py`
- Skill file: `01-Agency-Department/departments/02-marketing/skills/marketing-director-agent.md`
- Manager Phase 3 specialist-দের load করে চালায় (DRAFT only), নিজে কিছু post করে না; engine/section-এর পুরনো worker execute করে না।
- Agency Chief wiring **Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে call করে।

## Mapped Existing Staff (4)

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| ContentPlanner | `content_plan` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | ok | EXISTING |
| VideoProducer | `video_produce` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | ok | EXISTING |
| CaptionWriter | `caption_write` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | none | EXISTING |
| PublishPrep | `publish_prep` | `01-Agency-Department/engine/workers/src/workers/marketing.py` | post it | EXISTING |

Note: PublishPrep শুধু **prep** করে — কখনো post করে না। আসল publish Boss-এর
"post it" approval-এর পর হাতে করা হয়।

Phase 3 (2026-11-19) standalone specialists — আরও ৪ জন EXISTING:
Market Positioning Agent (`market_position`), Social Media Agent
(`social_manage`, planning draft only, NEVER posts), SEO Agent (`seo`),
Analytics Agent (`analytics`) — সবাই `departments/02-marketing/specialists/`
-এ, gate none, DRAFT only। Manager এদের importlib দিয়ে load করে।

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Market Positioning Agent | EXISTING — Market Positioning Agent | `market_position`, gate none | `departments/02-marketing/specialists/market_positioning_agent.py` |
| Content Strategy Agent | EXISTING — ContentPlanner | `content_plan`, gate ok |
| Social Media Agent | EXISTING — Social Media Agent | `social_manage`, gate none | `departments/02-marketing/specialists/social_media_agent.py` — planning draft only, NEVER posts; PublishPrep শুধু prep করে, কখনো post করে না |
| Ad Campaign Agent | **GAP** | Paid ads — $0 spend cap, planned নয়; কোনো worker/skill নেই |
| Copywriting Agent | EXISTING — CaptionWriter | `caption_write`, gate none |
| Video Creative Agent | EXISTING — VideoProducer | `video_produce`, gate ok |
| SEO Agent | EXISTING — SEO Agent | `seo`, gate none | `departments/02-marketing/specialists/seo_agent.py` |
| Analytics Agent | EXISTING — Analytics Agent | `analytics`, gate none | `departments/02-marketing/specialists/analytics_agent.py` — visible metrics only, কখনো estimate নয়; weekly reporting ReportCompiler-এর (Finance & Admin, dept 07) আওতায় |

## Missing Roles

- **Ad Campaign Agent — GAP।** Paid ads $0 spend cap-এর কারণে planned নয়; কোনো
  worker code বা skill নেই। Boss সিদ্ধান্ত না নিলে এই role তৈরি হবে না।

## Honest Status

- **Paying clients: 0** — এখনো কোনো paying client নেই।
- **Brain: mock ($0)** — live MetaSpark UNPROVEN; সব output DRAFT।
- **DB: JSON store files** (`store/tasks.json`, `store/approvals.json`) — এটাই DB, অন্য কোনো database নয়।
- **Publish gate "post it"** — Boss-এর exact word ছাড়া কিছু publish হয় না।
- **Paid ads: GAP** — $0 spend cap; কোনো ad spend নেই।
- **Weekly report** এই department-এর কাজ নয় — ReportCompiler (Finance & Admin) করে।
- **$0 spend cap** — কিছু খরচ করা হয় না।
- **Agency Chief wiring Phase 2 DONE** — Chief এখন DEPARTMENT_ROUTING দিয়ে এই department-এর manager-কে call করে।
- **Pricing LOCKED, internal only** — public content-এ কখনো দাম বলা হয় না।
- **No dental/medical ever** — dental/medical বা patient-health ব্যবসা target নয়।
- Brand **Talvenor only**। কোনো invented client, price, statistic, testimonial, guarantee নেই।
