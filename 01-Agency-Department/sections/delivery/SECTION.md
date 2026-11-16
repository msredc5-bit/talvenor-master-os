# Section: Delivery — Agency (Phase 7)

**উদ্দেশ্য (purpose):** Paying client-এর receptionist বানানো (DRAFT plan),
QA, onboarding, delivery পরিচালনা, আর client check-in — demo থেকে go-live
পর্যন্ত। Live stack Vapi/Sophia। এই section কখনো live build করে না, আর
QA pass + Boss "ok" ছাড়া কোনো receptionist live বলে না।

**সত্য অবস্থা (2026-11-16):** Paying client 0। Email PAUSED (2026-11-14
থেকে)। Booking: https://calendar.app.google/WLoxBfnLGTdjK3LB8 ·
ফোন +1 (947) 223-0244।

## Staff roster

| Staff | Agent file / vendored worker | Skill file | Gate | Status |
|---|---|---|---|---|
| RetellBuilder | `engine/workers/src/workers/delivery.py` (`RetellBuilder`) | `engine/skills/receptionist-builder.md` | `ok` | MAPPED |
| QAEngineer | `engine/workers/src/workers/delivery.py` (`QAEngineer`) | `engine/skills/qa-engineer.md` | None | MAPPED |
| OnboardingAgent | `engine/workers/src/workers/delivery.py` (`OnboardingAgent`) | `engine/skills/onboarding-agent.md` | `ok` | MAPPED |
| ServiceDeliveryManager | `sections/delivery/agents/service_delivery_manager.py` | `sections/delivery/skills/service-delivery-manager.md` | `ok` | NEW (Phase 7) |
| ClientSuccessAgent | `sections/delivery/agents/client_success_agent.py` | `sections/delivery/skills/client-success-agent.md` | `send` | NEW (Phase 7) |

## কাজের প্রবাহ (how work flows)

1. **OnboardingAgent** — নতুন client-এর onboarding pack DRAFT (info form,
   hours/services, transfer number, ৭ দিনে live-এর শর্ত)। তথ্য না থাকলে
   "BOSS INPUT REQUIRED"।
2. **RetellBuilder** — receptionist-এর **DRAFT build plan** (agent prompt,
   knowledge base, recording script)। Live stack Vapi/Sophia — Boss Retell-এর
   জন্য টাকা দেবেন না, তাই কখনো live build নয়, শুধু plan।
3. **QAEngineer** — ১২-check QA checklist, verdict READY বা CHANGES।
   Verdict-ই শেষ কথা নয় — delivery-তে Boss-এর ok লাগে।
4. **ServiceDeliveryManager** — delivery checklist + go-live verification
   ধাপ DRAFT। Go-live শুধু QA pass + Boss "ok"-এর পরে; ছাড়া live দাবি নয়।
5. **ClientSuccessAgent** — check-in draft + renewal-reminder draft।
   Paying client 0 — client তথ্য না থাকলে TEMPLATE only, কাউকে পাঠানো নয়।

## Gate

- `ok` (RetellBuilder, OnboardingAgent, ServiceDeliveryManager): plan/pack
  ব্যবহার করতে Boss-এর "ok" লাগে।
- `send` (ClientSuccessAgent): check-in/renewal বার্তা পাঠাতে Boss-এর "send"
  লাগে; পাঠানো Boss নিজে করেন।
- None (QAEngineer): checklist নিজেই নিরাপদ।

## সৎ সীমা (honest limits)

- Live stack Vapi/Sophia — RetellBuilder শুধু DRAFT build plan, live build নয়।
- QA pass + Boss "ok" ছাড়া কোনো receptionist live নয় — কখনো live দাবি নয়।
- Paying client 0 — client তথ্য না থাকলে "BOSS INPUT REQUIRED"।
- সব output DRAFT, mock brain ($0)। কোনো price quote নয়, কোনো guarantee নয়,
  কোনো বানানো client/testimonial/statistic নেই।
