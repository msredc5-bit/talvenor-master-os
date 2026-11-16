# n8n Wiring — বাইরের দুনিয়ার সাথে সংযোগ (Phase 4)

**সত্য অবস্থা (2026-11-16): দুইটা workflow-ই READY, কোনোটাই LIVE নয়।**
Import file তৈরি আছে, Boss-এর import + connect + test বাকি। কোনো
workflow এখনো একটা mail-ও পাঠায়নি, একটা call-ও করেনি।

## Host-এর সত্য কথা ($0)

- **এখনকার host = Muse runtime + 10-min bridge cron (`ceo-office-bridge`)।**
  এটাই $0-তে চলে — cron প্রতি ১০ মিনিটে office-এর queued task দেখে,
  draft/result বানায়, কখনো send/publish/spend/delete করে না।
- **২৪/৭ always-on server নেই।** সত্যিকারের server (VPS/Render/Railway
  বা নিজের PC-তে ২৪ ঘণ্টা চালু service) টাকা দিয়ে করতে হবে — পরে,
  Boss-এর সিদ্ধান্তে। n8n Cloud-ও Boss-এর নিজের account — Elora সেখানে
  কিছু import করতে পারে না, Boss-কে করতে হবে।

## Workflow 1 — Tier 2 Auto-send (Gmail + Google Sheets)

- **File:** `~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json`
  (আসল path-এ hyphen আছে: `talvenor-outreach`, `talvenor/outreach` নয়)
- **Guide:** `~/workspace/talvenor-outreach/n8n-auto-send-setup-guide.md`
- **নাম:** "Talvenor Tier 2 — Daily auto-send 18:00 Dhaka" · **8 node**
- **Flow:** Schedule 18:00 Dhaka → Read Queue (Google Sheet) → শুধু
  আজকের `ready` row → একটা একটা করে Gmail send (মাঝে 50 sec gap) →
  Sheet-এ `status=sent` + message ID + time লেখা।
- **Sheet:** "Talvenor Tier 2 Send Queue" —
  `1SZjkPZfpGjHUBIWp9-bnYVhKuFaxXAgC_wOMlpfv4MM`, tab Queue
  (send_date, idx, business_name, email, subject, body, status,
  message_id, sent_at_dhaka, notes)।
- **Status: READY · NOT LIVE** (`"active": false` — ফাইল থেকে যাচাই করা)।
- **Boss-এর বাকি step (৩টা, একবারই):**
  1. n8n Cloud → Workflows → Import from File → JSON select।
  2. "Send email" node-এ Gmail connect (msredc5@gmail.com) + "Read Queue"
     / "Mark sent" node-এ Google Sheets connect (একই account)।
  3. 1-mail test — নিজের inbox-এ (msredc5@gmail.com) test row পাঠিয়ে
     দেখা: From-এ **hello@talvenorai.agency** দেখায় কি না। না দেখালে
     "Send email" node-এর Options → Send From-এ hello@ alias select
     করতে হবে; না পেলে Elora-কে বলতে হবে। Test pass হলে TEST row মুছে
     workflow **Active** করতে হবে।
- **EMAIL PAUSE GATE (2026-11-14 থেকে):** এই workflow এখন চালানো যাবে
  না — Boss আগে ২টা DNS record (SPF edit + DMARC new) বসিয়ে "check
  koro" বলবেন, Elora dig-এ যাচাই করবে, তারপর seed test পাস হলে তবেই
  restart। DNS fix ছাড়া auto-send চালু করলে mail spam-এ যাবে / SPF fail
  করবে।
- **দুই system একসাথে চলবে না:** n8n LIVE হওয়ার পর main-chat-এ tap
  করে পাঠানো বন্ধ — নইলে একই prospect-কে double mail যাবে। Test pass
  হলে cron `tier2-daily-send-trigger` re-scope হবে — draft Sheet-এ
  লেখা, পাঠানো n8n-এর কাজ।
- **Safety net:** Elora প্রতিটা draft path-এর আগে Sent-check করে
  (আগে পাঠানো থাকলে Sheet-এ `ready` করে না); Sheet-এ সব দেখা যায়
  (কী গেল, কখন, message ID); বন্ধ করতে চাইলে n8n-এ Deactivate করলেই
  পরের দিন আর যাবে না। Tap না থাকায় ভুল draft গেলে কেউ থামাবে না —
  তাই test ছাড়া Active করা যাবে না।

## Workflow 2 — Callback (Website form → Vapi call)

- **File:** `~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json`
- **Guide:** `~/workspace/talvenor-callback/callback-setup-guide.md`
- **নাম:** "Talvenor Callback - Website form to Vapi" · **3 node**
- **Flow:** Website form (নাম + phone + consent) → n8n webhook POST
  `talvenor-callback` → Vapi `POST /call` (assistant "Sophia — Talvenor
  Callback (Outbound)", ID `1587fd30-57e1-4aaf-9c93-39a0c39e450e`) →
  Sophia visitor-কে ২–৩ মিনিটের pitch-এ call করে → demo booking-এর
  invite। Form-এর consent line TCPA consent দেয়।
- **Status: READY · NOT LIVE** (`"active": false` — ফাইল থেকে যাচাই করা)।
- **Boss-এর বাকি step:**
  1. **Twilio number (~$1.15/mo) — BLOCKER, টাকা লাগবে।** Free Vapi
     number (+19472230244) দিয়ে outbound call যায় না। Twilio-তে US
     number কিনে Vapi-তে import করতে হবে, তারপর `phoneNumberId`
     (এখন workflow-এ `FILL_AFTER_TWILIO_IMPORT` লেখা) বসাতে হবে।
     Bangladesh-এ call করতে Twilio Geo Permissions-এ Bangladesh on
     করতে হবে।
  2. n8n Cloud-এ workflow import → Vapi Header-Auth credential
     ("Vapi API Key", `Authorization: Bearer <Vapi private key>`) →
     **Active** → Production webhook URL copy।
  3. ওই URL Elora-কে দিলে website form-এর `CALLBACK_WEBHOOK_URL`-এ
     বসানো হবে (এক লাইনের কাজ)।
  4. Test: নিজের number দিয়ে form submit — ১০–২০ সেকেন্ডে Sophia-র
     call আসা উচিত। Call English-এ হবে।
- **খরচ (আন্দাজ):** একটা callback ≈ $0.25–0.40; $5 free credit-এ
  ≈ ১২–২০টা callback। Twilio number ~$1.15/mo + per-minute।
- **Form-এর অবস্থা:** website form (v6/v7) শুধু Boss-এর private view-এ
  আছে — public link এখনো v5 দেখায় (form নেই)। Share BLOCKED ছিল
  (external webhook POST)। Hosting পথ Boss-এর সিদ্ধান্ত বাকি: export
  করে talvenorai.agency-তে host করা (recommended) অথবা POST সরানো।

## কী কী কখনোই হবে না (gate)

- n8n workflow নিজে থেকে কোনো mail/call পাঠায় না — Boss-এর import +
  Active + (auto-send-এর ক্ষেত্রে) DNS fix + seed test-এর পরেই চলে।
- কোনো workflow-ই Master OS-এর approval gateway bypass করে না —
  draft লেখা Chief-এর কাজ, পাঠানো/কল করা Boss-এর gate word + এই
  wiring-এর Active step-এর পরে।
- কোনো workflow LIVE বলে দাবি করা হয় না — `active: false` যতদিন,
  dashboard-এ NOT LIVE-ই লেখা থাকবে (`scripts/sync_status.py` ফাইল
  থেকে পড়ে লেখে)।

## Dashboard sync

`dashboards/status.html` এখন `scripts/sync_status.py` দিয়ে বানানো হয়
— n8n workflow-এর `active` flag, Gate 0, PA list, pipeline গণনা,
store সংখ্যা সব আসল ফাইল থেকে পড়ে লেখা হয়। হাতে সংখ্যা বদলানো যাবে
না — sync চালালে আবার আসল সংখ্যাই ফিরে আসবে।
