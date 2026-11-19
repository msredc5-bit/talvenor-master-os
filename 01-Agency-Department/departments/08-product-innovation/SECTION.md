# Department 08: Product Innovation — Agency (Phase 1)

**উদ্দেশ্য (purpose):** Talvenor Agency service-এর innovation — নতুন AI
product/feature research, automation R&D, technology evaluation, product
improvement, আর prototype-এর ভাবনা। Manager task_kind দেখে সঠিক
specialist worker-কে চালিয়ে তার DRAFT ফেরত দেয়; specialist-রা শুধু
DRAFT বানায় — কোনো research/prototype live-এ execute হয় না।

**সত্য অবস্থা (2026-11-19):** Paying client 0। প্রথম মেইল 162। Email PAUSED
(2026-11-14 থেকে, DNS fix বাকি)। Brain mock ($0)। Booking:
https://calendar.app.google/WLoxBfnLGTdjK3LB8 · ফোন +1 (947) 223-0244।
**Phase 3 DONE (2026-11-19):** ৬ specialist-ই EXISTING — skill .md +
worker .py আছে; GAP department আর নয়।

## Manager

| Manager | Agent file | Skill file | Gate |
|---|---|---|---|
| ChiefInnovationAgent | `departments/08-product-innovation/manager/chief_innovation_agent.py` | `departments/08-product-innovation/skills/chief-innovation-agent.md` | `ok` |

Manager-এর কাজ: `manage_product_innovation` — task_kind দেখে specialist
ঠিক করা, specialist worker-কে চালিয়ে তার DRAFT ফেরত দেওয়া (load না
হলে delegation plan-এর DRAFT, fallback)। Chief wiring Phase 2 DONE —
Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।

## Mapped existing staff

| Worker | Task type | File path | Gate | Status |
|---|---|---|---|---|
| NewAIProductResearchAgent | `new_ai_product_research` | `departments/08-product-innovation/specialists/new_ai_product_research.py` | none | EXISTING |
| NewFeatureResearchAgent | `new_feature_research` | `departments/08-product-innovation/specialists/new_feature_research.py` | none | EXISTING |
| AutomationRDAgent | `automation_rd` | `departments/08-product-innovation/specialists/automation_rd.py` | none | EXISTING |
| TechnologyEvaluationAgent | `technology_evaluation` | `departments/08-product-innovation/specialists/technology_evaluation.py` | none | EXISTING |
| ProductImprovementAgent | `product_improvement` | `departments/08-product-innovation/specialists/product_improvement.py` | none | EXISTING |
| PrototypeBuilderAgent | `prototype_builder` | `departments/08-product-innovation/specialists/prototype_builder.py` | none | EXISTING |

ছয়টা brief role-ই EXISTING — প্রতিটার skill .md (`skills/`-এ) + worker
.py (`specialists/`-এ) আছে। সবাই DRAFT only, mock brain ($0)।

**খেয়াল:** Vet No-Show Recovery Kit ($49) এই department-এর নয় — সেটা
02-Digital-Product-Department-এর। এই department শুধু Agency service
innovation-এর জন্য — receptionist service-কে আরও ভালো করা, নতুন AI
feature, নতুন automation।

## Brief roles (role → status)

| Role | Status | Note |
|---|---|---|
| New AI Product Research Agent | EXISTING | `new_ai_product_research`, gate none — `specialists/new_ai_product_research.py`; skill `skills/new-ai-product-research-agent.md`। |
| New Feature Research Agent | EXISTING | `new_feature_research`, gate none — `specialists/new_feature_research.py`; skill `skills/new-feature-research-agent.md`। |
| Automation R&D Agent | EXISTING | `automation_rd`, gate none — `specialists/automation_rd.py`; skill `skills/automation-rd-agent.md`। |
| Technology Evaluation Agent | EXISTING | `technology_evaluation`, gate none — `specialists/technology_evaluation.py`; skill `skills/technology-evaluation-agent.md`। |
| Product Improvement Agent | EXISTING | `product_improvement`, gate none — `specialists/product_improvement.py`; skill `skills/product-improvement-agent.md`। |
| Prototype Builder Agent | EXISTING | `prototype_builder`, gate none — `specialists/prototype_builder.py`; skill `skills/prototype-builder-agent.md`। Prototype plan-এর DRAFT মাত্র — prototype নিজে বানায় না। |

## Missing roles (worker নেই)

কোনো missing role নেই — ছয়টা brief role-ই EXISTING। এই department-এ
কোনো GAP role নেই।

## Gate

- `ok` (ChiefInnovationAgent): manager output ব্যবহার করতে Boss-এর "ok" লাগে।
- ৬ specialist-এর gate none — draft নিজেই নিরাপদ, কোনো gate নেই।

## সৎ সীমা (honest limits)

- সব output DRAFT, mock brain ($0)। Specialist-রা শুধু DRAFT বানায় —
  কোনো research/prototype live-এ execute নয়, কোনো prototype বানানো নয়।
- এই department Agency service innovation only — Vet No-Show Recovery Kit
  ($49) 02-Digital-Product-Department-এর, এখানকার নয়।
- কোনো client/দাম/পরিসংখ্যান বানানো নয় — না থাকলে "BOSS INPUT REQUIRED"।
- $0 spend cap — কোনো tool কেনা নয়, কোনো খরচ নয়।
- Dental/medical/patient-health কখনো target নয়।
- Chief wiring Phase 2 DONE — Agency Chief এখন DEPARTMENT_ROUTING দিয়ে এই manager-কে ডাকে।
- Paying client 0; প্রথম মেইল 162; Email PAUSED (2026-11-14 থেকে)।
- Live voice stack Vapi/Sophia — Sophia live receptionist, demo নয়।
