# Live-brain proof — Boss's PC, 2026-11-26

Recorded as a FACT in F1 (FOUNDER OS). This snapshot's brain stays
`mock` — Boss's PC config was NOT copied here.

## What happened

- **2026-11-26 04:13 Dhaka** — Boss flipped `00-CEO-Core/config.json`
  `"brain"` from `mock` to `development` himself, then ran
  `scripts/setup_brain.py`. It saved the dev brain as
  `ollama:qwen2.5-coder:1.5b` (local Ollama, $0, no key), chain
  [ollama:qwen2.5-coder:1.5b, ollama:gemma4:12b,
  gemini:gemini-3.5-flash-lite, openrouter:openrouter/free].
  Production brain untouched/locked.
- **`check_live_brain.py --live` PASS** — reply: "Talvenor Master OS
  is a personal CEO agent designed to assist solo founders in
  managing their businesses effectively." Latency **1.9s**, tokens
  **83/23/106**, mode `live`, brain_kind `development`.
- **Second probe PASS 06:03 Dhaka** — 2.7s, live 1.5B;
  `check_dev_brain` 13/13.
- **Earlier the same day (03:33 Dhaka)** — first-ever live-brain
  probe on his PC via Gemini: `gemini:gemini-3.5-flash-lite`, PASS
  in 1.7s, tokens 71/6/77.

## Source

Boss's screenshots (2026-11-26, verified in chat). No live API call
was made from this VM for this proof — the VM cannot reach
api.meta.ai (tunnel 403), and the proof ran on his PC.

## What changed since

- **F1 (2026-11-26):** gemma4:12b was removed from the dev fallback
  chain — it cannot run on an 8 GB PC (llama-server OOM crash,
  verified twice) and keeping it wasted a 5-minute timeout on every
  cold start. The chain recorded above is the chain AS PROBED
  (gemma4:12b was in it but never reached — qwen answered first).
  The current chain is [ollama:qwen2.5-coder:1.5b,
  gemini:gemini-3.5-flash-lite, openrouter:openrouter/free].
- The snapshot brain is still `mock`. Every brain claim must say
  which copy it describes: this snapshot, GitHub, or Boss's PC.
