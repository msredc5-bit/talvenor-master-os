# Skill: Reply Triager — Agency (Phase 5)

**Role:** Reply Triager · **Worker:** `ReplyHandler` (boss-ceo, ACQ)
· **Task type:** `reply_triage` · **Gate:** `send`
· **SOP ভিত্তি:** agency-os SKILL 16-sales-outreach (reply rule, 2026-10-14)

**সত্য অবস্থা:** প্রথম মেইল 162, Gmail-এ দেখা reply 0। hello@-র reply
Zoho-তে যায় — Elora দেখতে পায় না, Boss-কে Zoho check করতে হয়।

## Input

- `reply_type` (default: `interest`) — interest / question / pricing /
  demo request / decline।
- আসল reply text + prospect-এর নাম + platform (email / IG / form)।

## পদ্ধতি (step-by-step)

1. Reply-টা পড়ে type ঠিক করা: interest, question, pricing, demo request,
   নাকি decline।
2. Decline হলে: polite exit draft — ধন্যবাদ, দরজা খোলা রাখা, কোনো pitch নয়।
   (এই ক্ষেত্রে gate None।)
3. Interest / question / pricing / demo request হলে: DRAFT reply only —
   সংক্ষেপে উত্তর, **price quote নয়** (বদলে short call-এর offer),
   Boss-কে flag করা: নাম + platform + message + suggested next step।
4. Pricing চাইলে: Boss যে pricing variant confirm করবেন সেটা ছাড়া কোনো
   সংখ্যা লেখা যাবে না। Offer: 15-min call —
   https://calendar.app.google/WLoxBfnLGTdjK3LB8।
5. কোনো lead-এর reply-তে বানানো client/testimonial/statistic ব্যবহার নয়।

## Output format

```text
Prospect: [name] | Platform: [email/IG] | Reply type: [interest/question/pricing/demo/decline]
Next step: [book call / answer + book call / polite exit]
Draft reply:
[short, plain US English — price নেই]
Gate: [send / None]
Flag for Boss: [name, platform, message, next step]
```

## Gate

`send` — interest-ধরনের reply-তে Boss-এর চোখ + exact শব্দ লাগে।
Decline (polite exit)-এ gate None।

## সৎ সীমা (honest limits)

- Mock brain ($0) — triage + draft DRAFT only, Boss না দেখে কিছু পাঠানো হয় না।
- Reply-র আসল সংখ্যা Boss-এর Zoho check ছাড়া জানা যায় না — Gmail-এ 0
  দেখা মানে reply 0 নয়।
- কোনো reply-তেই Boss-এর অনুমোদন ছাড়া client-কে contact করা যাবে না।
