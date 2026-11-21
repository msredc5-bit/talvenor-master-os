# Department 05: Research & Strategy — Agency (Phase 1)

**Purpose:** Talvenor Agency's strategy-level research — competitors,
industry, pricing, niche, offer, and market opportunity, so the Agency
moves ahead with the right niche and the right offer. The manager delegates the task to the specialist
and returns their DRAFT (Phase 3, 2026-11-19).

**Honest status (2026-11-19):** Paying client 0. First mail 162. Email PAUSED
(since 2026-11-14, DNS fix pending). Brain mock ($0). Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefStrategyAgent | `departments/05-research-strategy/manager/chief_strategy_agent.py` | `departments/05-research-strategy/skills/chief-strategy-agent.md` | `ok` |

The manager's job: `manage_research_strategy` — pick the specialist by task_kind
load and run the specialist with importlib, return their DRAFT.
If there is no task_kind, an overview draft of the 7 specialists. Chief wiring
Phase 2 DONE — the Agency Chief now calls this manager with DEPARTMENT_ROUTING.
Phase 3 DONE (2026-11-19) — all 7 specialists are EXISTING.

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

All 7 specialists are EXISTING (Phase 3, 2026-11-19) — each has a skill `.md`
(`departments/05-research-strategy/skills/<role>.md`). All output is DRAFT ONLY,
mock brain ($0).

**Note:** Prospect-level research is separate work — it is done by
ProspectResearcher (dept 01 Sales, `prospect_research`, no gate).
This department does not look for prospects; it is for strategy-level research —
competitor, industry, pricing, niche, offer, market.

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| Competitor Research Agent | EXISTING | `specialists/competitor_research_agent.py` (`competitor_research`, gate none) — only verified names (Smith.ai, Abby, Ruby, CallRail Voice Assist); skill `skills/competitor-research-agent.md`. |
| Industry Research Agent | EXISTING | `specialists/industry_research_agent.py` (`industry_research`, gate none) — a source for every number, UNVERIFIED if none; skill `skills/industry-research-agent.md`. |
| Pricing Research Agent | EXISTING | `specialists/pricing_research_agent.py` (`pricing_research`, gate none) — INTERNAL ONLY; does not change the LOCKED pricing, never quotes a price to a prospect; skill `skills/pricing-research-agent.md`. |
| Niche Selection Agent | EXISTING | `specialists/niche_selection_agent.py` (`niche_selection`, gate none) — dental/medical always DQ, legal gated until the 4th client; skill `skills/niche-selection-agent.md`. |
| Offer Development Agent | EXISTING | `specialists/offer_development_agent.py` (`offer_development`, gate none) — no guarantee; skill `skills/offer-development-agent.md`. |
| Market Opportunity Agent | EXISTING | `specialists/market_opportunity_agent.py` (`market_opportunity`, gate none) — no invented market size/stat; skill `skills/market-opportunity-agent.md`. |
| Business Intelligence Agent | EXISTING | `specialists/business_intelligence_agent.py` (`business_intelligence`, gate none) — only real numbers (client 0, first mail 162, email PAUSED, revenue $0); skill `skills/business-intelligence-agent.md`. |

## Missing roles (no worker)

No missing role — all 7 brief roles are EXISTING (Phase 3, 2026-11-19).
There is no GAP role in this department.

## Gate

- `ok` (ChiefStrategyAgent): Boss's "ok" is needed to use the manager's output.
- The brief roles have gate none — a specialist draft is safe on its own, no gate.

## Honest limits

- All output is DRAFT, mock brain ($0). The manager loads and runs the specialist,
  the specialist only makes a draft — no sending/spending.
- No invented client/competitor/price/statistic — if not available
  "BOSS INPUT REQUIRED".
- LOCKED pricing (2026-11-12) internal only — never quote a price to a prospect.
- Dental/medical/patient-health never a target.
- Chief wiring Phase 2 DONE — the Agency Chief now calls this manager via DEPARTMENT_ROUTING.
- Paying client 0; first mail 162; Email PAUSED (since 2026-11-14).
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.
