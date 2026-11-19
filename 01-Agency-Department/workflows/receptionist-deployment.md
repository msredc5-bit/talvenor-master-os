# Workflow 4 — Receptionist Deployment

**Department:** 03 AI Engineering (+ 07 Quality & Security — QA, + 04 Client Operations — handover)
**তারিখ:** 2026-11-19 | **Status:** READY (plan level) — **কোনো client deployment এখনো হয়নি।**

## Purpose (উদ্দেশ্য)

একজন client-এর জন্য Talvenor AI receptionist (Vapi/Sophia stack) বানিয়ে, QA করে, Boss-এর approval নিয়ে live করা — আর live-এর পর call দেখা।

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Voice Agent Builder (`RetellBuilder`) | 03 | EXISTING — DRAFT plan only |
| Vapi Integration Agent | 03 | ROLE-ONLY — Vapi সংযোগের worker নেই |
| Conversation Designer | 03 | ROLE-ONLY |
| Prompt Engineering Agent | 03 | ROLE-ONLY |
| Testing & Debugging Agent (`QAEngineer`) | 03/07 | EXISTING — QA checklist (partial) |
| Deployment Agent | 03 | ROLE-ONLY — deployment manual + Boss approval |
| Call Monitoring Agent | 04 | ROLE-ONLY — live monitoring worker নেই |

## সত্য অবস্থা — LIVE STACK (ভুল করবেন না)

- **Live production voice: Vapi — Sophia, live receptionist, +1 (947) 223-0244**, org `1861a735`, GPT-4o-mini, Emma voice, Deepgram nova-3।
- **Sophia production receptionist — demo নয়।**
- **Retell DROPPED 2026-10-26 — কখনো production নয়।** `RetellBuilder` শুধু DRAFT plan বানায়; নাম দেখে ভুল করবেন না।
- **Demo = recorded 60-second demo video:** https://facebook.com/reel/2947321012290705/ — live Sophia-কে demo হিসেবে দেখাবেন না।
- **Ava demo rebuild pending** — Boss demo account আনলে rebuild হবে।
- **কোনো client deployment এখনো হয়নি।** নিচের সব ধাপ READY plan — real client-এ চলেনি।

## Step-by-step

### ধাপ ১ — Build plan DRAFT (RetellBuilder)

1. Client-এর onboarding pack (Workflow 3) পড়ুন — hours, services, FAQs, emergency routing, booking rules, escalation, transfer number।
2. `RetellBuilder` দিয়ে **receptionist build plan-এর DRAFT** বানান: agent flow, prompt-এর খসড়া, knowledge base-এর list, call flow।
3. মনে রাখুন: এটা **DRAFT plan ONLY** — live agent বানানো নয়, Vapi-তে কিছু deploy করা নয়।
4. **Gate:** plan Boss-কে দেখাতে `ok` লাগে।

### ধাপ ২ — Prompt + knowledge base + call flow

1. **Prompt:** Greet → life-safety check → intent → qualify → action → confirm → log → close। Honest AI disclosure থাকবে — receptionist নিজেকে AI বলবে।
2. **Knowledge base:** client-এর hours, services, FAQs, booking rules — শুধু client-এর দেওয়া তথ্য; কিছু বানানো যাবে না।
3. **Call flow:** booking নেওয়া, emergency-তে transfer, escalation-এ মানুষের কাছে পাঠানো।
4. **Gate:** Boss-এর `ok` ছাড়া পরের ধাপ নয়।

### ধাপ ৩ — QA: 12-check checklist (QAEngineer)

1. **QA = 12-check checklist** — প্রতিটা check পাস/ফেল লিখুন:
   - hook/greeting ঠিক আছে, AI disclosure আছে, life-safety redirect আছে
   - hours/services/FAQ সঠিক, booking rules মানে, transfer number সঠিক
   - escalation কাজ করে, emergency routing সঠিক
   - "Talvenor" বানান ঠিক, কোনো invented claim নেই, কোনো price/guarantee নেই
2. কোনো check ফেল করলে deployment নয় — fix করে আবার QA।
3. **Gate:** QA-তে gate নেই (checklist-এর কাজ), কিন্তু deploy-তে Boss-এর `ok` লাগে।

### ধাপ ৪ — Deployment (manual + founder approval)

1. Boss-এর **`ok`** নিন।
2. **Manual step:** Vapi-তে assistant configure করা, phone number সংযোগ, knowledge base বসানো — হাতে করা হয়; কোনো auto-deploy worker নেই।
3. Go-live-র পর test call করে দেখুন: receptionist ধরে, booking নেয়, transfer করে।
4. **Gate:** `ok` — Boss-এর exact word + manual step।

### ধাপ ৫ — Monitoring (ROLE-ONLY — worker নেই)

1. **Call Monitoring Agent ROLE-ONLY — live monitoring worker এখনো নেই।**
2. Live-এর পর call log / booking দেখা হাতে করতে হয় — কোনো automated monitoring নেই।
3. সমস্যা দেখলে ClientSuccessAgent-কে draft লিখতে বলুন (Workflow 5)।

## Honest status

- Build plan DRAFT worker আছে; Vapi integration, deployment, monitoring-এর কোনো worker নেই।
- **No client deployment has happened yet** — এই workflow-এর কোনো ধাপই real client-এ চলেনি।

## Missing inputs (যা নেই)

- প্রথম paying client + তার onboarding pack (CLIENT INPUT REQUIRED)।
- Vapi Integration / Deployment / Call Monitoring worker।
- Boss-এর `ok` প্রতিটা ধাপে + manual deployment step।
