# Provider Setup — Fitting Any LLM to the Brain (simple guide)

The brain is mock now. To go live, 3 things are needed — one provider's
key + choosing that provider in config + turning the brain "live". Never write
a key in any file — only in an environment variable.

## 1. The providers (8) — where to get the key, which env var

| Provider | Where to get the key | Env var | Default model |
|---|---|---|---|
| Meta (Muse Spark) | dev.meta.ai — your Muse Spark API key (the same key already registered in the Meta connector on the Muse VM; the connector cannot read it back, so take it from your Meta account) | META_API_KEY | muse-spark-1.3 |
| OpenAI (ChatGPT) | https://platform.openai.com/api-keys | OPENAI_API_KEY | gpt-4o |
| Claude (Anthropic) | https://console.anthropic.com/settings/keys | ANTHROPIC_API_KEY | claude-sonnet-4-5 |
| Gemini (Google) | https://aistudio.google.com/apikey | GEMINI_API_KEY | gemini-3.5-flash-lite |
| Kimi (Moonshot) | https://platform.moonshot.ai | MOONSHOT_API_KEY | kimi-k2.5 |
| Grok (xAI) | https://console.x.ai | XAI_API_KEY | grok-4 |
| OpenRouter (auto-router) | https://openrouter.ai/keys | OPENROUTER_API_KEY | openrouter/free |
| Ollama (local, no key) | No key — install Ollama on your PC, pull a model | OLLAMA_HOST (server address, default localhost) | qwen2.5-coder:1.5b |

## 2. Changing the model — one line in config

In `00-CEO-Core/config.json`, the `providers` section has a `models`
list for each provider. The first model is the default. To put in a model
of your own choice, two ways:

- By name in the chain: `"fallback_chain": ["openai:gpt-4o-mini", "meta", "mock"]`
- By changing only the provider: `"brain_provider": "gemini"` (then the default model runs)

Take a new model's name from the vendor's model list — with a wrong name, the
provider gives a "model not found" error and moves to the next provider, then mock.

## 3. OpenRouter — the whole system (step by step)

OpenRouter is one door — many models can run with one key.

**Step 1 — Account:** go to https://openrouter.ai and sign up with Google/GitHub
(free, no card needed).

**Step 2 — Create a key:** go to https://openrouter.ai/keys → "Create API Key"
→ give it a name (e.g. Talvenor) → copy the key. The key is shown only once —
if you lose it, you must create a new one.

**Step 3 — Put the key on the PC (not in a file):** open a terminal
on your PC and run this command (Windows PowerShell):

```
setx OPENROUTER_API_KEY "your-key-here"
```

Then close the terminal and open it again — the key will work in the new terminal.
(If on Mac/Linux: `export OPENROUTER_API_KEY="your-key-here"` — but that is only
for that terminal; to make it permanent, write it in `.bashrc`/`.zshrc`.)

**Step 4 — Choose a model:** config has two ways.

- `openrouter/free` (default) — auto-router: OpenRouter itself picks a fitting
  free model for each request. Boss does not need to remember a model name.
- By name — e.g. `nvidia/nemotron-3-ultra-550b-a55b:free`. Models ending in `:free`
  are free.

**Step 5 — Know the free limits:** on free models, 20 requests/min,
50 requests/day. Once you buy $10 lifetime credit, it becomes 1,000/day.
Limits are counted in requests, not tokens. Free models change (they come and go) —
so keep more than one provider in the fallback chain, e.g.
`["openrouter", "meta", "mock"]`.

## 4. Muse Spark — the production brain key (paid, PC only)

Muse Spark is **PAID / credit-based** (it bills Boss's Muse Spark
credit). It is a **PRODUCTION-brain option only** — never the dev
brain, never in the free-only allowlist (the dev guard rejects it),
never a fallback for a failed free model. The key slot
(`META_API_KEY`) was added 2026-11-25; on the Muse VM the provider
still uses the registered Meta connector instead, and the key is
never read back from it.

**Step 1 — Get the key:** from your Meta account at dev.meta.ai
(the Muse Spark API key — the same one behind the Meta connector
on the Muse VM).

**Step 2 — Put the key on the PC (not in a file):** open a terminal
on your PC and run this command (Windows PowerShell):

```
setx META_API_KEY "paste-key-here"
```

Then close the terminal and open it again — the key will work in the
new terminal. Never paste the key in chat, in a file, or in a `.env`.

**Step 3 — Direct curl test first** (in the same PowerShell window;
proves the key + the network reach the Meta API, before any office
code runs):

```
curl.exe -s https://api.meta.ai/v1/chat/completions -H "Authorization: Bearer $env:META_API_KEY" -H "Content-Type: application/json" -d '{"model":"muse-spark-1.3","messages":[{"role":"user","content":"Reply with the single word: ok"}],"max_completion_tokens":30}'
```

Expected: HTTP 200 with `"ok"` in the reply. 401 = bad key.
403 / timeout = the network or key path is blocked — note the
2026-11-20 probe from this VM failed with a tunnel 403, $0 spent,
key validity still unproven; the curl test on your PC is the real
proof, and there is no retry from this VM without your word.

**Step 4 — Full adapter proof (only on your word):** the live
adapter runs only after you unlock the production brain
(`production_brain.unlocked` in `00-CEO-Core/config.json`) —
that unlock is your separate decision, never a dev change.
Note: `python scripts\check_live_brain.py --live` proves the
**Gemini free dev brain**, not Muse Spark — there is no
one-command Muse Spark probe; the curl test above plus an
unlocked adapter run is the proof.

## 5. Ollama — the local brain (qwen2.5-coder:1.5b on your PC, $0, no key)

Ollama is the local model server. There is no separate "model
adapter" — Ollama IS the adapter, and the model is the name.
Once the Ollama adapter is in, ANY model Ollama serves works the
same way — `qwen2.5-coder:1.5b`, `gemma4:12b`, or any other — just
by naming it. No key, no account, no billing; data never leaves
your PC. (gemma4:12b cannot run on an 8 GB PC — see the honest
limit below; it is not in the dev chain.)

**Step 1 — Install Ollama:** download from https://ollama.com and
install. Ollama starts by itself after install (or run
`ollama serve` in a terminal).

**Step 2 — Download the model:** in PowerShell:

```
ollama pull qwen2.5-coder:1.5b
```

That is ~1 GB and fits easily. Honest limit (verified 2026-11-26):
gemma4:12b needs ~9.5 GB of memory and this PC has 8 GB total — it
does NOT run at all (llama-server crashes, out of memory, verified
twice). Do not pull gemma4:12b.

**Step 3 — Let setup find it:** no JSON editing, no key:

```
python scripts\setup_brain.py
```

It checks the local Ollama server FIRST (before any cloud key),
lists the installed models, tests each one with a single tiny
call, and saves the first working one as the dev brain
(`ollama:qwen2.5-coder:1.5b`).

**Step 4 — Prove it live:**

```
python scripts\check_live_brain.py --live
```

PASS only if mode is `live` AND brain_kind is `development`.
This makes the LOCAL model the dev brain (test data only, $0) —
it does NOT touch the production brain, which stays locked.

**Step 5 — Switch models without editing JSON:** set
`BRAIN_PROVIDER` / `BRAIN_MODEL` (e.g.
`setx BRAIN_PROVIDER ollama` + `setx BRAIN_MODEL qwen2.5-coder:1.5b`),
then run the probe again. Or edit the dev chain entry
(`"ollama:<model>"`) — the free-only guard allows any Ollama model.

**If Ollama is not running:** the provider raises a clear error
("Ollama is not reachable ... start Ollama ... ollama pull ...")
and the dev chain falls through to Gemini/OpenRouter (if a key
is set) and then to a loud mock draft — never a silent fake.

## 6. Going live with the brain — the last step (only on Boss's word)

1. Put the key in an env var as above (Ollama needs no key — just
   install it and pull a model).
2. Find a working free model automatically (no JSON editing):
   `python scripts\setup_brain.py` — it checks the local Ollama
   server first, then asks the provider which free
   models exist, tests each one with a single tiny call, and saves the
   first working one into `00-CEO-Core/config.json`
   (development_brain only). Any free key works (Gemini or OpenRouter);
   paid keys are never picked for the dev brain.
3. In the terminal, run one small live probe with
   `python scripts\check_live_brain.py --live` — only if it succeeds is the brain live.
4. To switch the dev brain later without editing JSON, set
   `BRAIN_PROVIDER` / `BRAIN_MODEL` env vars (e.g.
   `setx BRAIN_PROVIDER openrouter`) and run the probe again. The
   free-only guard still applies: a paid provider or model is refused,
   never called.

## 7. True status (now)

- No provider's key has been given yet — Meta's key is also unproven
  (the 2026-11-20 probe got stuck on a tunnel 403). The Meta key slot
  now exists (`META_API_KEY` env var, added 2026-11-25), but no key
  value is on record anywhere, and no live call has been made from it.
- Ollama (local model) was added 2026-11-26 as the 8th provider:
  no key needed, adapter verified against a mock server on this VM
  (7/7) — the real proof happened on your PC 2026-11-26 04:13 Dhaka
  (qwen2.5-coder:1.5b, 1.9s; `ollama pull qwen2.5-coder:1.5b` →
  `setup_brain.py` → `check_live_brain.py --live`). gemma4:12b cannot
  run on this PC (OOM, verified twice) and was removed from the dev
  chain in F1.
- The brain is still mock, phase 11 / v0.9.0. No live call has happened, $0 spent.
- `scripts\setup_brain.py` (2026-11-25) finds a working free model
  automatically and saves it — no more hand-editing config.json for
  the dev brain. Google stopped serving gemini-2.5-flash-lite to new
  keys (HTTP 404); the current free default is gemini-3.5-flash-lite.
- If the brain is started without a key, the adapter does not silently pretend
  to be live — it writes the reason and gives a mock draft.
