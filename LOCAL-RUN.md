# Talvenor Master OS — Running It Locally on Your PC

## What you need (once)

1. **Python 3.10+** — install from [python.org](https://www.python.org/downloads/). During install you **must tick "Add Python to PATH"**.
2. **The repo** — if you have Git: `git clone https://github.com/msredc5-bit/talvenor-master-os.git`. Without Git, from the GitHub page: **Code → Download ZIP** → unzip.
3. **Internet** — for the first clone + loading the 3D library (Three.js CDN). The office work (run_office.py, voice) runs without internet.

## Running it in 3 steps

### Step 1 — Opening the dashboard (3D)

In the repo folder, **double-click `run_local.bat`**. It will do this by itself:

1. `python scripts\sync_status.py` — refreshes the numbers from the real files (`dashboards\status.json`)
2. Starts a local server — `http://localhost:8765`
3. Opens the **3D Dashboard** in the browser

To stop: **Ctrl+C** in the bat's window.

### Step 2 — Talking with Jarvis (voice)

```bat
python scripts\jarvis_voice_loop.py
```

- Speak in Bengali, it answers in Bengali. English also works (`--lang en`).
- The first time, ~361 MB of models will download (Piper + Vosk/sherpa) — once only.
- **The truth:** the voice is real, but the brain is still **mock** — answers are DRAFT. Saying "send koro" aloud does no work, it only becomes **PENDING**.
- No mic test has happened yet — the first real mic test will be on your PC.

### Step 3 — Giving the office a job

```bat
python scripts\run_office.py --business agency --task caption_write --input "{\"title\": \"Caption for Monday reel\"}"
```

- `--business`: `agency` | `products` | `content`
- Gated work (send/publish/spend/delete) gets stuck in **PENDING** without your gate word — never runs by itself.
- To run work from the queue: `python scripts\run_office.py --drain-queue --max 2`

### Step 4 — Giving work to the queue with the taskboard (Phase 9)

```bat
python scripts\taskboard_server.py
```

- Open: **http://localhost:8766/** (a different port from the dashboard's 8765, both run together).
- The board only writes tasks to `store\tasks.json` (queued) — the bridge cron does the work (every 10 minutes, max 2/run, draft/result only — no send/publish/spend/delete).
- To stop: **Ctrl+C** in the taskboard's window.
- Details: `dashboards\TASKBOARD-README.md`.

### Step 5 — Giving the brain a key (optional — the dashboard works without one)

Without a key the brain stays **mock** (drafts only). Keys live in
Windows environment variables ONLY — never in a file, never in chat.
After `setx`, close the terminal and open a new one. Full guide:
`00-CEO-Core\PROVIDERS-SETUP.md`.

**Dev brain (FREE, $0) — Gemini:**

```bat
setx GEMINI_API_KEY "paste-key-here"
```

- Key from: https://aistudio.google.com/apikey (no card, no billing).
- Curl test first, then the proof command:

```bat
python scripts\check_live_brain.py --live
```

- PASS only if mode is `live` AND `brain_kind` is `development`.
  Without the key it prints the setup steps and exits without calling.

**Production brain (PAID, Muse Spark) — META_API_KEY:**

```bat
setx META_API_KEY "paste-key-here"
```

- Key from: dev.meta.ai (your Muse Spark API key — the same one
  behind the Meta connector on the Muse VM; the connector cannot
  read it back, so take it from your Meta account).
- It bills your Muse Spark credit — production brain ONLY, never
  the dev brain, never a fallback for a failed free model.
- Curl test first (this is the real proof — the 2026-11-20 probe
  from this VM failed with a tunnel 403, $0 spent, key unproven):

```bat
curl.exe -s https://api.meta.ai/v1/chat/completions -H "Authorization: Bearer $env:META_API_KEY" -H "Content-Type: application/json" -d '{"model":"muse-spark-1.3","messages":[{"role":"user","content":"Reply with the single word: ok"}],"max_completion_tokens":30}'
```

- The full adapter proof runs only after YOU unlock the production
  brain (`production_brain.unlocked` in `00-CEO-Core\config.json`) —
  that unlock is your separate decision, never a dev change.
  Note: `check_live_brain.py --live` proves the **Gemini dev brain**,
  not Muse Spark.

`run_local.bat` shows the key status at step [0/3] (set / not set —
it never prints a key value).

## How is the dashboard connected to Master OS?

```
Real files (config.json, store/, gate0-status.md, pipeline.md)
        ↓  python scripts\sync_status.py
dashboards\status.json  ← numbers come here (not hand-written)
        ↓  run_local.bat → local server (port 8765)
3D Dashboard (dashboard-3d.html)  ← shows the numbers + building colors here
```

- The dashboard only **shows** — `run_office.py` does the work. To refresh the numbers, run `sync_status.py` again, then press **🔄 Refresh numbers** in the dashboard.
- If `status.json` is not found, the dashboard shows the 2026-11-20 snapshot — that is written on it.

## What is NOT LIVE (the truth)

| Item | State |
|---|---|
| Brain | **mock** — thinking is DRAFT, the live brain has not been flipped on |
| Muse Spark key | **slot ready, not set** — `META_API_KEY` env var (PC) or connector (Muse VM); production brain locked; key validity UNPROVEN (2026-11-20 probe failed tunnel 403) |
| Gemini dev key | **slot ready, not set** — `GEMINI_API_KEY` env var (free tier); dev brain stays mock until the `--live` proof passes |
| Email outreach | **PAUSED** (since 2026-11-14) — the SPF/DMARC DNS fix is still in your hands |
| Paying client | **0** · first mail 163 |
| Gate 0 (Vet Kit) | **NOT PASSED** — the Lemon Squeezy test is your step |
| n8n workflows | **READY, NOT LIVE** — import + connect + test remaining |
| YouTube upload | **OFF** — needs "upload it" + credentials |
| 24/7 server | **None** — the office stops when the PC is off; keeping it running needs a paid server |
| PC limits | RAM 8 GB (~1.4 GB free), GPU 496 MB VRAM — Ollama large models / GPU video **will not run**; CPU-only small models (1–1.5B) only |

## If something goes wrong

- **"Python not found"** → Reinstall Python, ticking "Add Python to PATH".
- **"Port 8765 busy"** → Close the previous server window and run again.
- **No 3D, but numbers show** → Check the internet (Three.js CDN is needed); the numbers will still show correctly.
- **Mic does not work** → Windows Settings → Privacy → Microphone → allow Python/terminal.
- **"Module not found"** → Are you running from inside the repo folder? `run_local.bat` cds there itself.

## The files

- `run_local.bat` — one-click dashboard (also shows brain key status)
- `00-CEO-Core\PROVIDERS-SETUP.md` — key setup guide (all 7 providers: where the key comes from, `setx`, live-proof steps)
- `scripts\sync_status.py` — syncs the numbers (now also writes `status.json`)
- `dashboards\dashboard-3d.html` — 3D dashboard (this file)
- `dashboards\status.json` — real numbers (made by sync)
- `dashboards\status.html` — old 2D status page (made by sync)
- `scripts\run_office.py` — the office runner
- `scripts\taskboard_server.py` — taskboard (port 8766, writes to `store\tasks.json`; `run_local.bat` does not run it)
- `dashboards\taskboard.html` + `dashboards\TASKBOARD-README.md` — taskboard page + instructions
- `scripts\jarvis_voice_loop.py` — Jarvis voice loop
- `00-CEO-Core\VOICE-SETUP.md` — voice setup in detail
