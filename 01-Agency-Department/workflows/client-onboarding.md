# Workflow 3 — Client Onboarding

**Department:** 04 Client Operations (+ 01 Sales & Growth — close থেকে handover)
**তারিখ:** 2026-11-19 | **Status:** READY — কিন্তু **কোনো real client-এ এখনো test হয়নি (paying client 0)।**

## Purpose (উদ্দেশ্য)

Demo call-এ "yes" বলা ব্যবসাকে 7 দিনের মধ্যে live receptionist-এ নিয়ে যাওয়া — intake থেকে configuration পর্যন্ত, Boss-এর `ok` প্রতিটা ধাপে।

## Owner roles

| Role | Dept | Status |
|---|---|---|
| Business Requirement Analyst (`ClientIntakeReceiver`) | 04 | EXISTING — intake নেয় |
| Client Onboarding Agent (`OnboardingAgent`) | 04 | EXISTING — onboarding pack draft |
| Client Configuration Agent (`ServiceDeliveryManager`) | 04 | EXISTING — configuration manage করে |
| SalesCloser | 01 | EXISTING — close prep, handover দেয় |
| SchedulerAssistant | 01 | EXISTING — booking link সাহায্য |

## সত্য অবস্থা

- **Paying client 0** — এই workflow এখনো কোনো real client-এ চলেনি। যা লেখা আছে তা READY plan, exercised নয়।
- **Onboarding term:** 7 দিনের মধ্যে live, না হলে build fee refund। **3-month minimum**, তারপর month-to-month, 30 days notice।
- **Pricing LOCKED, internal only** — onboarding-এ client-কে price বলা হয় শুধু Boss যেটা confirm করেছেন সেটা; prospect-কে outreach-এ কখনো quote নয়।

## Step-by-step

### ধাপ ১ — Intake (ClientIntakeReceiver)

1. Client-এর কাছ থেকে নিন:
   - **Business info form:** business name, address, service area, website
   - **Hours:** কখন খোলা, কখন বন্ধ, after-hours-এ কী হবে
   - **Services:** কী কী service দেয়, কোনটার booking নিতে হবে
   - **FAQs:** বারবার আসা প্রশ্ন + সঠিক উত্তর
   - **Emergency routing:** emergency call-এ কাকে, কোন number-এ পাঠাতে হবে
   - **Booking rules:** কখন booking নেওয়া যাবে, কতদিন আগে, কোন slot নয়
   - **Escalation:** কোন পরিস্থিতিতে মানুষের কাছে transfer করতে হবে
2. কিছু না পেলে **CLIENT INPUT REQUIRED** লিখুন — guess করবেন না।
3. **Gate:** intake পাঠাতে `send` লাগে।

### ধাপ ২ — Onboarding pack draft (OnboardingAgent)

1. Intake থেকে **onboarding pack**-এর draft বানান:
   - business info form (পূরণ করা)
   - hours/services summary
   - **transfer number** (call transfer যাবে যেখানে)
   - 7-day live term + 3-month minimum (লিখিত)
   - call flow-এর খসড়া (greet → intent → qualify → action → confirm → log → close)
2. Pack-এ কোনো invented client, testimonial, guarantee থাকবে না।
3. **Gate:** pack Boss-কে দেখাতে `ok` লাগে — Boss `ok` বললে তবেই পরের ধাপ।

### ধাপ ৩ — Configuration (ServiceDeliveryManager)

1. Boss-এর `ok`-র পর Vapi/Sophia stack-এ client-এর configuration বসান (Workflow 4 — receptionist-deployment দেখুন):
   - prompt + knowledge base (hours, services, FAQs)
   - call flow + escalation + emergency routing
   - transfer number + booking rules
2. Configuration-এ কোনো step নিজে থেকে বদলাবেন না — pack-এ যা আছে তাই।
3. **Gate:** configuration-এ `ok` লাগে।

### ধাপ ৪ — Go-live (7 দিনের মধ্যে)

1. QA 12-check পাস করলে (Workflow 4) Boss-এর `ok` নিয়ে go-live।
2. Go-live-র দিন client-কে জানান: receptionist live, transfer number active, booking link চালু।
3. **Term মনে রাখুন:** onboarding complete হওয়ার 7 দিনের মধ্যে live না হলে build fee refund।
4. **Gate:** go-live-তে Boss-এর `ok` (exact word) লাগে।

## Honest status

- Workflow **READY, untested** — 0 paying client, তাই intake থেকে go-live পর্যন্ত কোনো ধাপই real client-এ চলেনি।
- Worker আছে (Intake, Onboarding, Configuration) — কিন্তু সবই draft/plan level-এ; live run-এর প্রমাণ নেই।

## Missing inputs (যা নেই)

- **প্রথম paying client** — client ছাড়া intake শুরুই হয় না।
- Client-এর business info, hours, services, transfer number — সবই CLIENT INPUT REQUIRED।
- Boss-এর `ok` প্রতিটা ধাপে।
