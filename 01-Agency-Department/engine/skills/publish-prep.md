# Skill: Publish Prep — Agency (Phase 5)

**Role:** Publish Prep · **Worker:** `PublishPrep` (boss-ceo, MKT)
· **Task type:** `publish_prep` · **Gate:** `post it`
· **SOP basis:** agency-os SKILL 17-marketing + 2026-10-10 publishing lesson

**Job:** Preparing an approved post for publishing — only PREPARE, not publish.

## Input

- `count` (default: 2) — how many posts to prepare.
- Approved posts: final file + caption pack + platform + Boss's "ok".

## Method (step-by-step)

1. Assemble the pack for each post: final file (image/video) + caption +
   first comment + scheduled time (US Eastern).
2. Platform check: Facebook Page short post + one CTA; Instagram Reel /
   carousel / single image + caption hook; LinkedIn text-led + Boss's
   personal profile (not the company page).
3. Check that the file + caption + time match — if there is a wrong file or wrong caption,
   tell Boss; do not fix it yourself and move toward publishing.
4. Give the pack to Boss — publishing only from the main chat, when Boss says "post it",
   Boss does it himself.

## Output format

```text
Publish-ready pack (count: [n]):
  1. Platform: [...] | File: [...] | Time (US Eastern): [...]
     Caption: [...]
     First comment: [...]
Gate: post it — nothing is published without Boss's exact word.
```

## Gate

`post it` — Boss's exact word is needed.

## Honest limits

- **Detached auto-publish forbidden (2026-10-10 lesson):** `facebook-cli`
  / `instagram-cli` publish hangs from a cron worker — scheduled
  auto-publish does not exist in this system.
- This role never publishes — it only prepares. If it is not published, that must be
  said honestly; "posted" cannot be claimed.
- Mock brain ($0) — pack DRAFT; Boss verifies the final file exists.
