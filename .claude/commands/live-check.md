---
description: Prove the dev brain is live with the key on this PC
---

Prove the development brain is live. This is the ONE sanctioned live
proof, and it makes exactly one tiny call (max 30 tokens).

Steps (from the repo folder, in order):
1. `python scripts\setup_brain.py` — finds a working free model for
   whichever key is set (`GEMINI_API_KEY` or `OPENROUTER_API_KEY`) and
   saves it. If no key is set, it prints the setup steps: stop there
   and show them to Boss.
2. `python scripts\check_live_brain.py --live` — the proof.
3. Report in Bengali, short:
   - PASS: mode `live` + brain_kind `development` → the dev brain
     works. Say which provider and model won.
   - FAILED: show the `last_failure` line exactly. If it is a 404,
     the model is not served to this key — run step 1 again, it picks
     another model. Never edit `config.json` by hand for this.
4. Never flip the real config's `brain` flag to `live`, never touch
   `production_brain`. The production brain stays locked until Boss
   separately authorizes it.
