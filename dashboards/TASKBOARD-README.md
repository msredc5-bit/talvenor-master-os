# Task Board — Talvenor Master OS (Phase 9)

## এটা কী (What it is)

একটা ছোট local web page — এখান থেকে Master OS-এর queue-তে task দেওয়া
যায়, আর queue-র অবস্থা দেখা যায়। Board নিজে কোনো task চালায় না —
শুধু `store/tasks.json`-এ লেখে। আসল কাজ করে bridge cron (প্রতি ১০
মিনিট, সর্বোচ্চ ২টা/run, draft/result only — send/publish/spend/
delete কখনো নয়)।

## চালানো (How to start)

```bash
# এই VM / Linux
python3 scripts/taskboard_server.py
# খুলুন: http://localhost:8766/

# Boss-এর PC (Windows)
python scripts\taskboard_server.py
# খুলুন: http://localhost:8766/
```

Port 8766 (run_local.bat-এর dashboard 8765 ব্যবহার করে — আলাদা port,
যাতে দুইটা একসাথে চলে)। শুধু localhost (127.0.0.1) — বাইরে থেকে
খোলা যায় না। বন্ধ করতে Ctrl+C।

## Task দেওয়া (How to add a task)

1. Board খুলে Title লিখুন (কী করতে হবে)।
2. Type দিন — `research`, `caption_write`, `script_write`,
   `outreach_draft`, `gate0_check` (snake_case)।
3. Business বাছুন — Agency / Digital Product / Content।
4. "Queue-তে দাও" চাপুন — task-টা `store/tasks.json`-এ `queued`
   হয়ে যাবে, id দেখাবে।

API দিয়েও দেওয়া যায়:

```bash
curl -X POST http://localhost:8766/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "verify the Talvenor booking link is live",
       "type": "research", "business": "agency", "payload": {}}'
```

## তারপর কী হয় (What happens next)

- Bridge cron (প্রতি ১০ মিনিট) queue থেকে সর্বোচ্চ ২টা task নেয়।
- Research task হলে আসল তথ্য যাচাই করে, draft task হলে draft বানায় —
  ফলাফল task record-এ লিখে status `done` করে।
- Board-এ Refresh চাপলে (বা ৩০ সেকেন্ড পর auto) নতুন status দেখা
  যায়। Status-ও দেখা যায়: Phase, clients, first mails, email,
  Gate 0 — `dashboards/status.json` থেকে আসে।
- Gated কাজ (send/publish/spend/delete) board দিয়ে চলবে না — সেটা
  ApprovalGateway-এ PENDING হয়, Boss-এর gate word লাগে।

## API

- `GET /` — board page
- `GET /api/status` — dashboards/status.json
- `GET /api/tasks` — `{"records": [...]}` (store/tasks.json)
- `POST /api/tasks` — নতুন queued task (201 + record, বা 400 + error)
