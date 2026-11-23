# Agency — workflows

This folder will hold the Agency's workflows (n8n / scripts). In Phase 0,
there is no workflow here — it comes in Phase 4 (n8n wiring).

## True status (2026-11-16)

- **Email sending PAUSED** — Boss's order, 2026-11-14. No mail
  will go until Boss fixes the DNS and says "check koro".
- **DNS fix pending:** adding `include:_spf.google.com` to SPF + a new
  `_dmarc` record — work for Boss's DNS panel. File:
  `~/workspace/talvenor/outreach/dns-fix-copy-paste-2026-11-14.md`
- **First mail:** 163 sent (Day 1–3), paying client 0.
- **Day 4/5/6 drafts:** 25 each READY, not sent — once the pause lifts,
  what Boss says goes.
- **n8n auto-send:** READY, not LIVE — Boss's import + 1 test
  mail pending. The two systems never run together.

## What comes here in Phase 1

- Chief's connection to the Tier 2 send schedule (draft -> approval -> send)
- Connection to the reply watcher (telling the Chief when a reply arrives)
- No workflow will send/publish without Boss's gate word.
