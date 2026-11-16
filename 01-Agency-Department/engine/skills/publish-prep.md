# Skill: Publish Prep — Agency (Phase 5)

**Role:** Publish Prep · **Worker:** `PublishPrep` (boss-ceo, MKT)
· **Task type:** `publish_prep` · **Gate:** `post it`
· **SOP ভিত্তি:** agency-os SKILL 17-marketing + 2026-10-10 publishing lesson

**কাজ:** Approved post publish-এর জন্য তৈরি করা — শুধু PREPARE, publish নয়।

## Input

- `count` (default: 2) — কতটা post তৈরি করতে হবে।
- Approved post-গুলো: final file + caption pack + platform + Boss-এর "ok"।

## পদ্ধতি (step-by-step)

1. প্রতিটা post-এর জন্য pack গোছানো: final file (image/video) + caption +
   first comment + scheduled time (US Eastern)।
2. Platform check: Facebook Page short post + একটা CTA; Instagram Reel /
   carousel / single image + caption hook; LinkedIn text-led + Boss-এর
   personal profile (company page নয়)।
3. File + caption + সময় মিলিয়ে দেখা — ভুল file বা ভুল caption থাকলে
   Boss-কে জানানো, নিজে ঠিক করে publish-এর দিকে এগোনো নয়।
4. Pack Boss-কে দেওয়া — publishing শুধু main chat থেকে, Boss "post it"
   বললে, Boss নিজে করেন।

## Output format

```text
Publish-ready pack (count: [n]):
  1. Platform: [...] | File: [...] | Time (US Eastern): [...]
     Caption: [...]
     First comment: [...]
Gate: post it — Boss-এর exact শব্দ ছাড়া কিছু publish হয় না।
```

## Gate

`post it` — Boss-এর exact শব্দ লাগে।

## সৎ সীমা (honest limits)

- **Detached auto-publish নিষিদ্ধ (2026-10-10 lesson):** `facebook-cli`
  / `instagram-cli` publish cron worker থেকে hang করে — scheduled
  auto-publish এই system-এ নেই।
- এই role কখনো publish করে না — শুধু তৈরি করে। Publish না হলে সেটা
  সৎভাবে বলতে হবে, "posted" দাবি করা যাবে না।
- Mock brain ($0) — pack DRAFT; final file-এর অস্তিত্ব Boss যাচাই করবেন।
