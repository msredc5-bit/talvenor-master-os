# Skill: QA Engineer — Agency (Phase 5)

**Role:** QA Engineer · **Worker:** `QAEngineer` (boss-ceo, DEL)
· **Task type:** `receptionist_qa` · **Gate:** None
· **SOP ভিত্তি:** agency-os SKILL 18-qa-testing (mandatory gate — "Nothing
ships without a QA verdict")

**কাজ:** Demo receptionist READY বলার আগে QA checklist চালানো — প্রমাণ
দিয়ে verdict দেওয়া, মতামত দিয়ে নয়।

## Input

- `agent` (default: ava-apex-plumbing-demo) — যাচাই করতে হবে এমন agent /
  build plan-এর নাম।
- Build plan (Receptionist Builder-এর DRAFT) + client-এর আসল তথ্য।

## পদ্ধতি (step-by-step — ১২টা check)

1. Prompt completeness — flow-র সব ধাপ আছে কি (greet, life-safety, intent,
   qualify, action, confirm, log, close)?
2. ভাঙা tool reference নেই তো?
3. Emergency flow ঠিক আছে কি — life-safety ক্ষেত্রে redirect আছে?
4. Pricing honesty — কোথাও বানানো price / guarantee নেই তো?
5. Transfer number আসল, নাকি অনুপস্থিত — বানানো নম্বর থাকলে FAIL।
6. end_call behavior — সঠিকভাবে call শেষ হয়?
7. Honest AI disclosure আছে কি?
8. Callback handling আছে কি?
9. Confirmation number fictional AP- format-এ কি?
10. Client-এর আসল hours/services/FAQ plan-এর সাথে মেলে কি?
11. Voice + transcription setting (Vapi: Emma voice, Deepgram nova-3)
    plan-এ লেখা আছে কি?
12. Edge case: hostile / অদ্ভুত input-এ agent কী করে?
13. প্রতিটা check-এ PASS/FAIL + প্রমাণ লেখা। একটাও FAIL থাকলে verdict CHANGES।

## Output format

```text
Agent: [name]
Checks: 12 — PASS [n] / FAIL [n]
  1. [check] — PASS/FAIL — [evidence]
  ...
Verdict: READY / CHANGES
Fix list (CHANGES হলে): [কী ঠিক করতে হবে, reproduction সহ]
```

## Gate

Checklist-এ gate None — কিন্তু verdict READY হলেও delivery-তে Boss-এর
`ok` লাগে (Chief-এর gate)। FAIL থাকলে কিছু delivery নয়।

## সৎ সীমা (honest limits)

- Mock brain ($0) — QA checklist DRAFT; আসল test call-এর প্রমাণ (transcript,
  recording) ছাড়া "READY" মানে live-এ কাজ করবে তার গ্যারান্টি নয়।
- এই role নিজে agent fix করে না — fix list দেয়, Builder ঠিক করে, আবার QA হয়।
- Paying client 0 — এখনো কোনো live agent-এর QA হয়নি।
