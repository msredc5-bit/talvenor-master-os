# Department 05: Research & Strategy — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency-র strategy-level research — প্রতিযোগী,
industry, pricing, niche, offer, আর market opportunity বোঝা, যাতে Agency
সঠিক niche আর সঠিক offer নিয়ে এগোয়। Manager task-কে specialist-এর কাছে
delegate করে তার DRAFT ফেরত দেয় (Phase 3, 2026-11-19)।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefStrategyAgent | `departments/05-research-strategy/manager/chief_strategy_agent.py` | `departments/05-research-strategy/skills/chief-strategy-agent.md` | `ok` |

Manager-এর কাজ: `manage_research_strategy` — task_kind দেখে specialist
ঠিক করা, specialist-কে importlib দিয়ে load করে চালানো, তার DRAFT ফেরত
দেওয়া। task_kind না থাকলে ৭ specialist-এর overview draft। Chief wiring
Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
Phase 3 DONE (2026-11-19) — ৭ specialist-ই EXISTING।

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| CompetitorResearchAgent | `competitor_research` | `departments/05-research-strategy/specialists/competitor_research_agent.py` | none | EXISTING |
| IndustryResearchAgent | `industry_research` | `departments/05-research-strategy/specialists/industry_research_agent.py` | none | EXISTING |
| PricingResearchAgent | `pricing_research` | `departments/05-research-strategy/specialists/pricing_research_agent.py` | none | EXISTING |
| NicheSelectionAgent | `niche_selection` | `departments/05-research-strategy/specialists/niche_selection_agent.py` | none | EXISTING |
| OfferDevelopmentAgent | `offer_development` | `departments/05-research-strategy/specialists/offer_development_agent.py` | none | EXISTING |
| MarketOpportunityAgent | `market_opportunity` | `departments/05-research-strategy/specialists/market_opportunity_agent.py` | none | EXISTING |
| BusinessIntelligenceAgent | `business_intelligence` | `departments/05-research-strategy/specialists/business_intelligence_agent.py` | none | EXISTING |

৭ specialist-ই EXISTING (Phase 3, 2026-11-19) — প্রতিটার skill `.md` আছে
(`departments/05-research-strategy/skills/<role>.md`)। সব output DRAFT ONLY,
mock brain ($0)।

**খেয়াল:** Prospect-level research আলাদা কাজ — সেটা করে
ProspectResearcher (dept 01 Sales, `prospect_research`, no gate)।
এই department prospect খোঁজে না; এটা strategy-level research-এর জন্য —
competitor, industry, pricing, niche, offer, market।

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Competitor Research Agent | EXISTING | `specialists/competitor_research_agent.py` (`competitor_research`, gate none) — শুধু verified নাম (Smith.ai, Abby, Ruby, CallRail Voice Assist); skill `skills/competitor-research-agent.md`। |
| Industry Research Agent | EXISTING | `specialists/industry_research_agent.py` (`industry_research`, gate none) — প্রতিটা সংখ্যার source, না থাকলে UNVERIFIED; skill `skills/industry-research-agent.md`। |
| Pricing Research Agent | EXISTING | `specialists/pricing_research_agent.py` (`pricing_research`, gate none) — INTERNAL ONLY; LOCKED pricing বদলায় না, prospect-কে দাম quote নয়; skill `skills/pricing-research-agent.md`। |
| Niche Selection Agent | EXISTING | `specialists/niche_selection_agent.py` (`niche_selection`, gate none) — dental/medical সবসময় DQ, legal 4th client পর্যন্ত gated; skill `skills/niche-selection-agent.md`। |
| Offer Development Agent | EXISTING | `specialists/offer_development_agent.py` (`offer_development`, gate none) — কোনো guarantee নয়; skill `skills/offer-development-agent.md`। |
| Market Opportunity Agent | EXISTING | `specialists/market_opportunity_agent.py` (`market_opportunity`, gate none) — বানানো market size/stat নয়; skill `skills/market-opportunity-agent.md`। |
| Business Intelligence Agent | EXISTING | `specialists/business_intelligence_agent.py` (`business_intelligence`, gate none) — শুধু আসল সংখ্যা (client 0, first mail 162, email PAUSED, revenue $0); skill `skills/business-intelligence-agent.md`। |

## Missing roles (worker নেই)

কোনো missing role নেই — ৭টা brief role-ই EXISTING (Phase 3, 2026-11-19)।
এই department-এ কোনো GAP role নেই।

## Gate

- `ok` (ChiefStrategyAgent): manager-এর output ব্যবহার করতে Boss-এর "ok" লাগে।
- Brief role-গুলোর gate none — specialist draft নিজেই নিরাপদ, কোনো gate নেই।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। Manager specialist-কে load করে চালায়,
  specialist শুধু draft বানায় — কোনো পাঠানো/খরচ নয়।
- কোনো client/প্রতিযোগী/দাম/পরিসংখ্যান বানানো নয় — না থাকলে
  "BOSS INPUT REQUIRED"।
- LOCKED pricing (2026-11-12) internal only — prospect-কে কখনো দাম quote নয়।
- Dental/medical/patient-health কখনো target নয়।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
