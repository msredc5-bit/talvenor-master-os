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
- Manager কোনো worker execute করে না, নিজে কিছু post করে না।
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

## Brief Roles → Mapping

| Brief role | Mapping | Note |
|---|---|---|
| Market Positioning Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Content Strategy Agent | EXISTING — ContentPlanner | `content_plan`, gate ok |
| Social Media Agent | ROLE-ONLY | PublishPrep শুধু prep করে, কখনো post করে না; social management হাতে করা |
| Ad Campaign Agent | **GAP** | Paid ads — $0 spend cap, planned নয়; কোনো worker/skill নেই |
| Copywriting Agent | EXISTING — CaptionWriter | `caption_write`, gate none |
| Video Creative Agent | EXISTING — VideoProducer | `video_produce`, gate ok |
| SEO Agent | ROLE-ONLY | কোনো worker code নেই; skill doc অনুযায়ী হাতে করা |
| Analytics Agent | ROLE-ONLY | কোনো worker code নেই; weekly reporting ReportCompiler-এর (Finance & Admin, dept 07) আওতায় |

## Missing Roles

- **Ad Campaign Agent — GAP।** Paid ads $0 spend cap-এর কারণে planned নয়; কোনো
  worker code বা skill নেই। Boss সিদ্ধান্ত না নিলে এই role তৈরি হবে না।
- ROLE-ONLY ৪টি role-এর (Market Positioning, Social Media, SEO, Analytics) কোনো worker code নেই; এগুলো skill doc-এর role হিসেবে থাকে।

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
