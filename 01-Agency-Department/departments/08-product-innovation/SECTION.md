# Department 08: Product Innovation — Agency (Phase 1)

**Purpose:** Talvenor Agency service innovation — new AI
product/feature research, automation R&D, technology evaluation, product
improvement, and prototype ideas. The manager picks the right specialist worker from task_kind,
runs it and returns its DRAFT; the specialists only build
DRAFTs — no research/prototype is executed live.

**True status (2026-11-19):** Paying client 0. First mail 162. Email PAUSED
(since 2026-11-14, DNS fix pending). Brain mock ($0). Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.
**Phase 3 DONE (2026-11-19):** all 6 specialists are EXISTING — skill .md +
worker .py exist; no longer a GAP department.

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefInnovationAgent | `departments/08-product-innovation/manager/chief_innovation_agent.py` | `departments/08-product-innovation/skills/chief-innovation-agent.md` | `ok` |

The manager's job: `manage_product_innovation` — pick the specialist from task_kind,
run the specialist worker and return its DRAFT (if it does not load,
a DRAFT of the delegation plan, fallback). Chief wiring Phase 2 DONE —
Agency Chief now calls this manager through DEPARTMENT_ROUTING.

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| NewAIProductResearchAgent | `new_ai_product_research` | `departments/08-product-innovation/specialists/new_ai_product_research.py` | none | EXISTING |
| NewFeatureResearchAgent | `new_feature_research` | `departments/08-product-innovation/specialists/new_feature_research.py` | none | EXISTING |
| AutomationRDAgent | `automation_rd` | `departments/08-product-innovation/specialists/automation_rd.py` | none | EXISTING |
| TechnologyEvaluationAgent | `technology_evaluation` | `departments/08-product-innovation/specialists/technology_evaluation.py` | none | EXISTING |
| ProductImprovementAgent | `product_improvement` | `departments/08-product-innovation/specialists/product_improvement.py` | none | EXISTING |
| PrototypeBuilderAgent | `prototype_builder` | `departments/08-product-innovation/specialists/prototype_builder.py` | none | EXISTING |

All six brief roles are EXISTING — each has a skill .md (in `skills/`) + worker
.py (in `specialists/`). All are DRAFT only, mock brain ($0).

**Note:** the Vet No-Show Recovery Kit ($49) is not this department's — it is
02-Digital-Product-Department's. This department is only for Agency service
innovation — making the receptionist service better, new AI
features, new automation.

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| New AI Product Research Agent | EXISTING | `new_ai_product_research`, gate none — `specialists/new_ai_product_research.py`; skill `skills/new-ai-product-research-agent.md`. |
| New Feature Research Agent | EXISTING | `new_feature_research`, gate none — `specialists/new_feature_research.py`; skill `skills/new-feature-research-agent.md`. |
| Automation R&D Agent | EXISTING | `automation_rd`, gate none — `specialists/automation_rd.py`; skill `skills/automation-rd-agent.md`. |
| Technology Evaluation Agent | EXISTING | `technology_evaluation`, gate none — `specialists/technology_evaluation.py`; skill `skills/technology-evaluation-agent.md`. |
| Product Improvement Agent | EXISTING | `product_improvement`, gate none — `specialists/product_improvement.py`; skill `skills/product-improvement-agent.md`. |
| Prototype Builder Agent | EXISTING | `prototype_builder`, gate none — `specialists/prototype_builder.py`; skill `skills/prototype-builder-agent.md`. Only a DRAFT of the prototype plan — it does not build the prototype itself. |

## Missing roles (no worker)

No missing role — all six brief roles are EXISTING. This department has
no GAP role.

## Gate

- `ok` (ChiefInnovationAgent): using the manager output needs Boss's "ok".
- All 6 specialists have gate none — the draft itself is safe, no gate.

## Honest limits

- All output is DRAFT, mock brain ($0). The specialists only build DRAFTs —
  no research/prototype is executed live, no prototype is built.
- This department is Agency service innovation only — the Vet No-Show Recovery Kit
  ($49) is 02-Digital-Product-Department's, not this department's.
- No client/price/statistics are invented — if absent, "BOSS INPUT REQUIRED".
- $0 spend cap — no tool is bought, no spend.
- Dental/medical/patient-health is never a target.
- Chief wiring Phase 2 DONE — Agency Chief now calls this manager through DEPARTMENT_ROUTING.
- Paying client 0; first mail 162; Email PAUSED (since 2026-11-14).
- Live voice stack Vapi/Sophia — Sophia is a live receptionist, not a demo.
