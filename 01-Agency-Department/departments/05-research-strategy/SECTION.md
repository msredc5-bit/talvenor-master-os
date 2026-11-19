# Department 05: Research & Strategy — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency-র strategy-level research — প্রতিযোগী,
industry, pricing, niche, offer, আর market opportunity বোঝা, যাতে Agency
সঠিক niche আর সঠিক offer নিয়ে এগোয়। এই department কোনো research নিজে
করে না — manager শুধু task-কে specialist-এর কাছে route করার DELEGATION
PLAN-এর DRAFT বানায়।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefStrategyAgent | `departments/05-research-strategy/manager/chief_strategy_agent.py` | `departments/05-research-strategy/skills/chief-strategy-agent.md` | `ok` |

Manager-এর কাজ: `manage_research_strategy` — task_kind দেখে specialist
ঠিক করা, delegation plan-এর DRAFT বানানো। Worker execute নয়, research
নয়, পাঠানো নয়। Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| — none — | — | — | — | GAP department |

এই department-এ mapped existing staff নেই। Strategy-level research-এর
কোনো worker এখনো বানানো হয়নি।

**খেয়াল:** Prospect-level research আলাদা কাজ — সেটা করে
ProspectResearcher (dept 01 Sales, `prospect_research`, no gate)।
এই department prospect খোঁজে না; এটা strategy-level research-এর জন্য —
competitor, industry, pricing, niche, offer, market।

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Competitor Research Agent | ROLE-ONLY | Role definition only — প্রতিযোগী agency-র offer/pricing/positioning research; worker নেই, skill .md registry-তে এখনো বানানো হয়নি। |
| Industry Research Agent | ROLE-ONLY | Role definition only — home-service industry trend/চাহিদা research; worker নেই। |
| Pricing Research Agent | ROLE-ONLY | Role definition only — বাজারের দাম-কাঠামো research; LOCKED pricing (2026-11-12) বদলায় না, prospect-কে দাম quote নয়। |
| Niche Selection Agent | ROLE-ONLY | Role definition only — কোন niche-এ যাওয়া যায়, তা যাচাই; dental/medical/patient-health কখনো নয়। |
| Offer Development Agent | ROLE-ONLY | Role definition only — offer-এর DRAFT ভাবনা; কোনো guarantee/বানানো client নয়। |
| Market Opportunity Agent | ROLE-ONLY | Role definition only — নতুন market সুযোগ খোঁজা; worker নেই। |
| Business Intelligence Agent | ROLE-ONLY | Role definition only — research-গুলো এক জায়গায় সাজিয়ে Boss-কে সারাংশ; সংখ্যা বানায় না। |

## Missing roles (worker নেই)

সাতটা brief role-ই missing — Competitor Research, Industry Research,
Pricing Research, Niche Selection, Offer Development, Market Opportunity,
Business Intelligence। সব ROLE-ONLY: role definition আছে, worker নেই,
skill .md registry-তে এখনো বানানো হয়নি। Manager শুধু delegation plan-এর
DRAFT বানায়; কোনো research execute হয় না।

## Gate

- `ok` (ChiefStrategyAgent): delegation plan ব্যবহার করতে Boss-এর "ok" লাগে।
- Brief role-গুলোর gate `ok` — worker বানানো হলে output ব্যবহারে Boss-এর
  "ok" লাগবে।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। কোনো research execute নয় — plan-ই
  শেষ কথা।
- কোনো client/প্রতিযোগী/দাম/পরিসংখ্যান বানানো নয় — না থাকলে
  "BOSS INPUT REQUIRED"।
- LOCKED pricing (2026-11-12) internal only — prospect-কে কখনো দাম quote নয়।
- Dental/medical/patient-health কখনো target নয়।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
