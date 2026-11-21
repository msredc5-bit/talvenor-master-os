# Task Board — Talvenor Master OS (Phase 9)

## What it is

A small local web page — from here, tasks can be given to Master OS's queue,
and the queue's state can be seen. The board itself runs no task —
it only writes to `store/tasks.json`. The bridge cron does the real work (every 10
minutes, max 2/run, draft/result only — never send/publish/spend/
delete).

## How to start

```bash
# This VM / Linux
python3 scripts/taskboard_server.py
# Open: http://localhost:8766/

# Boss's PC (Windows)
python scripts\taskboard_server.py
# Open: http://localhost:8766/
```

Port 8766 (run_local.bat's dashboard uses 8765 — a different port,
so both run together). Localhost only (127.0.0.1) — cannot be opened from
outside. Stop with Ctrl+C.

## Adding a task (How to add a task)

1. Open the board and write a Title (what to do).
2. Give a Type — `research`, `caption_write`, `script_write`,
   `outreach_draft`, `gate0_check` (snake_case).
3. Choose the Business — Agency / Digital Product / Content.
4. Press "Add to queue" — the task will become `queued` in `store/tasks.json`
   and show its id.

It can also be added via API:

```bash
curl -X POST http://localhost:8766/api/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "verify the Talvenor booking link is live",
       "type": "research", "business": "agency", "payload": {}}'
```

## What happens next

- The bridge cron (every 10 minutes) takes at most 2 tasks from the queue.
- For a research task it verifies the real information, for a draft task it makes a draft —
  writes the result into the task record and sets status `done`.
- Pressing Refresh on the board (or auto after 30 seconds) shows the new status.
  Status is also visible: Phase, clients, first mails, email,
  Gate 0 — comes from `dashboards/status.json`.
- Gated work (send/publish/spend/delete) will not run via the board — it
  becomes PENDING in the ApprovalGateway and needs Boss's gate word.

## API

- `GET /` — board page
- `GET /api/status` — dashboards/status.json
- `GET /api/tasks` — `{"records": [...]}` (store/tasks.json)
- `POST /api/tasks` — new queued task (201 + record, or 400 + error)
