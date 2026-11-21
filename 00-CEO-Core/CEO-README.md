# CEO Core — What It Does

**In simple terms:** This folder is the "head" of the Master OS. Boss talks to Jarvis
(voice), Jarvis passes it to the Main CEO Bot (brain), the Main CEO Bot decides which
business's Chief of Staff will do the work, and for gated work it does not move a
single step without Boss's approval.

## What's Inside

| File | Status | Job |
|---|---|---|
| `main_ceo_bot.py` | REAL (thin router) | Reads the task and routes it to the right Chief; gated work gets stuck at approval |
| `human_approval_gateway.py` | REAL (working) | send / publish / spend / delete / upload — nothing happens without approve()/reject(); no auto-approve; a pending approval expires in 20 minutes |
| `jarvis_voice.py` | STUB | Voice interface — not yet connected to a live mic |
| `config.json` | REAL | 3 businesses, gate ON, $0 cap, booking link, phone, email — all locked facts |
| `mcp/` | REAL (stdio server) | Shows 7 mock tools over MCP; run: `python3 scripts/run_mcp_server.py` |
| `CEO-README.md` | This file | — |

## Hierarchy (Boss's decision)

Boss → Jarvis (voice) → Main CEO Bot (brain) → 3 Chiefs of Staff →
specialized worker → the result comes back to the Main CEO Bot → Boss's
approval if needed.

**Jarvis and the Main CEO Bot are separate** — Jarvis only listens/speaks, the brain
is the Main CEO Bot. In Gemini's map they were together; that has been fixed.

## Gate (law)

- `ok` = plan/asset approval
- `post it` = publish
- `upload it` = video upload
- `send` / `পাঠাও` = send
- `go` = move to the next phase

Without a gate word there is no send/publish/spend/delete/upload — that
path was not even kept in the code.

## Running the MCP server

```bash
python3 scripts/run_mcp_server.py
```

stdio MCP server (JSON-RPC 2.0, no network) — shows 7 mock tools
(draft-only). Gated tools (gmail_send / n8n_trigger) are not
listed here; a gated call only writes a PENDING approval, it never executes.

## Where the real engine lives

A copy of the real engine for 15 workers is now inside this repo (`01-Agency-Department/engine/workers/`, vendored in Phase 6; upstream `~/workspace/boss-ceo/` stays canonical). This router calls workers from the inside copy.
