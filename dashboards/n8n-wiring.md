# n8n Wiring — connection to the outside world (Phase 4)

**True state (2026-11-21): both workflows are READY, neither is LIVE.**
Import files are ready; Boss's import + connect + test remain. No
workflow has sent a single mail or made a single call yet.

## The truth about the host ($0)

- **The current host = Muse runtime + 10-min bridge cron (`master-os-3d-bridge`).**
  This is what runs at $0 — every 10 minutes the cron looks at the repo's store/tasks.json queued tasks,
  makes drafts/results, never sends/publishes/spends/deletes.
- **No 24/7 always-on server.** A real server (a VPS/Render/Railway
  or a service running 24 hours on your own PC) costs money — later,
  on Boss's decision. n8n Cloud is also Boss's own account — Elora cannot
  import anything there, Boss has to do it.

## Workflow 1 — Tier 2 Auto-send (Gmail + Google Sheets)

- **File:** `~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json`
  (the real path has a hyphen: `talvenor-outreach`, not `talvenor/outreach`)
- **Guide:** `~/workspace/talvenor-outreach/n8n-auto-send-setup-guide.md`
- **Name:** "Talvenor Tier 2 — Daily auto-send 18:00 Dhaka" · **8 nodes**
- **Flow:** Schedule 18:00 Dhaka → Read Queue (Google Sheet) → only
  today's `ready` rows → Gmail send one by one (50 sec gap between) →
  write `status=sent` + message ID + time in the Sheet.
- **Sheet:** "Talvenor Tier 2 Send Queue" —
  `1SZjkPZfpGjHUBIWp9-bnYVhKuFaxXAgC_wOMlpfv4MM`, tab Queue
  (send_date, idx, business_name, email, subject, body, status,
  message_id, sent_at_dhaka, notes).
- **Status: READY · NOT LIVE** (`"active": false` — verified from the file).
- **Boss's remaining steps (3, once only):**
  1. n8n Cloud → Workflows → Import from File → JSON select.
  2. Connect Gmail in the "Send email" node (msredc5@gmail.com) + connect Google Sheets in the "Read Queue"
     / "Mark sent" nodes (same account).
  3. 1-mail test — send a test row to your own inbox (msredc5@gmail.com) and
     check: does the From show **hello@talvenorai.agency**? If not,
     select the hello@ alias in the "Send email" node's Options → Send From;
     if it is not there, tell Elora. If the test passes, delete the TEST row and
     make the workflow **Active**.
- **EMAIL PAUSE GATE (since 2026-11-14):** this workflow must not be run now —
  Boss first sets 2 DNS records (SPF edit + new DMARC) and says "check
  koro"; Elora verifies with dig, and only after the seed test passes
  is there a restart. Starting auto-send without the DNS fix sends mail to spam / SPF
  will fail.
- **Two systems will not run together:** after n8n goes LIVE, tapping in the main chat
  to send stops — otherwise the same prospect gets a double mail. After the test passes
  (and after the email restart — the cron has been DISABLED since 2026-11-14,
  email PAUSED) the cron `tier2-daily-send-trigger` will be re-scoped — drafts
  are written in the Sheet, sending is n8n's job.
- **Safety net:** Elora does a Sent-check before every draft path
  (if already sent, it does not mark `ready` in the Sheet); everything is visible in the Sheet
  (what went, when, message ID); to stop it, just Deactivate in n8n and
  nothing goes the next day. With no tap, if a wrong draft goes, nobody will stop it —
  so it must not be made Active without a test.

## Workflow 2 — Callback (Website form → Vapi call)

- **File:** `~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json`
- **Guide:** `~/workspace/talvenor-callback/callback-setup-guide.md`
- **Name:** "Talvenor Callback - Website form to Vapi" · **3 nodes**
- **Flow:** Website form (name + phone + consent) → n8n webhook POST
  `talvenor-callback` → Vapi `POST /call` (assistant "Sophia — Talvenor
  Callback (Outbound)", ID `1587fd30-57e1-4aaf-9c93-39a0c39e450e`) →
  Sophia calls the visitor with a 2–3 minute pitch → demo booking
  invite. The form's consent line gives TCPA consent.
- **Status: READY · NOT LIVE** (`"active": false` — verified from the file).
- **Boss's remaining steps:**
  1. **Twilio number (~$1.15/mo) — BLOCKER, costs money.** The free Vapi
     number (+19472230244) cannot make outbound calls. Buy a US number in Twilio
     and import it into Vapi, then set `phoneNumberId`
     (currently written as `FILL_AFTER_TWILIO_IMPORT` in the workflow).
     To call Bangladesh, Bangladesh in Twilio Geo Permissions
     must be turned on.
  2. Import the workflow in n8n Cloud → Vapi Header-Auth credential
     ("Vapi API Key", `Authorization: Bearer <Vapi private key>`) →
     **Active** → Production webhook URL copy.
  3. If that URL is given to Elora, it goes into the website form's `CALLBACK_WEBHOOK_URL`
     (a one-line job).
  4. Test: submit the form with your own number — Sophia's call
     should come in 10–20 seconds. The call will be in English.
- **Cost (estimate):** one callback ≈ $0.25–0.40; on $5 free credit,
  ≈ 12–20 callbacks. Twilio number ~$1.15/mo + per-minute.
- **Form's state:** the website form (v6/v7) is only in Boss's private view —
  the public link still shows v5 (no form). Sharing was BLOCKED
  (external webhook POST). The hosting path is still Boss's decision: export
  and host on talvenorai.agency (recommended) or remove the POST.

## What will never happen (gate)

- No n8n workflow sends a mail/call by itself — only after Boss's import +
  Active + (for auto-send) DNS fix + seed test.
- No workflow bypasses Master OS's approval gateway —
  writing drafts is the Chief's job; sending/calling comes after Boss's gate word + this
  wiring's Active step.
- No workflow is claimed LIVE — as long as `active: false`,
  the dashboard will keep saying NOT LIVE (`scripts/sync_status.py` reads it from the file
  and writes it).

## Dashboard sync

`dashboards/status.html` is now made by `scripts/sync_status.py`
— the n8n workflow's `active` flag, Gate 0, PA list, pipeline counts,
store numbers are all read from the real files and written. Numbers cannot be changed by hand —
running sync brings back the real numbers.
