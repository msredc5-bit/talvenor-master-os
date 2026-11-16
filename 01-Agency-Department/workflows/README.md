# Agency — workflows

এই folder-এ Agency-র workflow (n8n / script) থাকবে। Phase 0-তে
এখানে কোনো workflow নেই — Phase 4 (n8n wiring)-এ আসবে।

## সত্য অবস্থা (2026-11-16)

- **Email পাঠানো PAUSED** — Boss-এর নির্দেশ 2026-11-14। কোনো মেইল
  যাবে না যতক্ষণ Boss DNS fix করে "check koro" না বলেন।
- **DNS fix বাকি:** SPF-এ `include:_spf.google.com` যোগ করা + নতুন
  `_dmarc` record — Boss-এর DNS panel-এর কাজ। ফাইল:
  `~/workspace/talvenor/outreach/dns-fix-copy-paste-2026-11-14.md`
- **প্রথম মেইল:** 162টা পাঠানো (Day 1–3), paying client 0।
- **Day 4/5/6 draft:** ২৫টা করে READY, পাঠানো হয়নি — pause উঠলে
  Boss যেটা বলবেন সেটা যাবে।
- **n8n auto-send:** READY, LIVE নয় — Boss-এর import + ১টা test
  মেইল বাকি। কখনো দুই system একসাথে চলবে না।

## Phase 1-এ এখানে যা আসবে

- Tier 2 send schedule-এর সাথে Chief-এর সংযোগ (draft -> approval -> send)
- Reply watcher-এর সাথে সংযোগ (reply এলে Chief-কে জানানো)
- কোনো workflow-ই Boss-এর gate word ছাড়া send/publish করবে না।
