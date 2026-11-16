# Skill: Receptionist Builder — Agency (Phase 5)

**Role:** Receptionist Builder · **Worker:** `RetellBuilder` (boss-ceo, DEL)
· **Task type:** `receptionist_build` · **Gate:** `ok`
· **SOP ভিত্তি:** agency-os SKILL 06-vapi-voice-agent (Vapi layer) +
05-agent-architecture

**সবচেয়ে গুরুত্বপূর্ণ সত্য:** Worker-এর নাম RetellBuilder হলেও Talvenor-এর
live stack **Vapi / Sophia** (Boss Retell-এর জন্য টাকা দেবেন না — 2026-10-26
সিদ্ধান্ত)। তাই এই role-এর output শুধু **DRAFT build plan** — কখনো live build নয়।
ফোন: +1 (947) 223-0244।

## Input

- `business` (default: Apex Plumbing), `trade` (default: plumbing)।
- Client-এর আসল তথ্য: business hours, services, transfer number, emergency
  নিয়ম — না থাকলে "BOSS INPUT REQUIRED", বানানো যাবে না।

## পদ্ধতি (step-by-step)

1. Client-এর তথ্য সংগ্রহ করা (onboarding pack থেকে) — hours, services,
   price list, transfer number, emergency flow।
2. Agent prompt-এর DRAFT লেখা — flow: Greet → life-safety check → intent →
   qualify → action → confirm → log → close। Honest AI disclosure সহ।
3. Knowledge base-এর DRAFT লেখা — services, FAQ, hours; কোনো বানানো pricing নয়।
4. Recording script লেখা — demo call-এর script, fictional AP- confirmation
   number ব্যবহার (আসল নম্বর বানানো নয়), end_call only।
5. Emergency flow + callback handling + in-prompt schedule plan-এ রাখা।
6. Plan Boss-কে দেখানো — live Vapi build Boss / live stack-এর কাজ, এই role নয়।

## Output format

```text
Client: [business] ([trade])
DRAFT BUILD PLAN (live stack: Vapi / Sophia — Retell নয়)
1. Agent prompt: [DRAFT text]
2. Knowledge base: [services, FAQ, hours]
3. Recording script: [demo call script]
4. Emergency flow + callback handling: [...]
5. Transfer number: [BOSS INPUT REQUIRED — আসল নম্বর ছাড়া লেখা যাবে না]
Gate: ok
```

## Gate

`ok` — Boss plan দেখে "ok" বললে তবেই plan ব্যবহার করা যায়। Live build-এ
Boss-এর আলাদা সিদ্ধান্ত লাগে।

## সৎ সীমা (honest limits)

- Mock brain ($0) — plan DRAFT only, live agent নয়।
- RetellBuilder নামটা engine-এর পুরোনো নাম — live-এ Retell ব্যবহার হয় না।
- Transfer number, business hours, price — client-এর আসল তথ্য ছাড়া
  বানানো যাবে না।
- Paying client 0 — এখনো কোনো client-এর live receptionist চালু হয়নি।
- Vapi-র আসল config (GPT-4o-mini, Emma voice, Deepgram nova-3) plan-এ
  লেখা যায়, কিন্তু এই role Vapi-তে কিছু বদলায় না।
