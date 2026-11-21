# PUSH PLAN — Phase 9 + Phase 10 (Talvenor Master OS)

**Status: READY — NOT PUSHED.** Push only on Boss's "push koro", in the main chat (Elora).
**Made:** 2026-11-20 ~21:55 Dhaka. **Repo:** msredc5-bit/talvenor-master-os, branch `main`.
**Remote head verified (read-only, list_commits):** `b649b9bd57c0de314de7a539b31d0ea94caf61a2` — matches the sync record's head ✅ (head commit: "Talvenor Master OS — Phase 8 review fixes (2/2)").
**Must be verified again at push time** — if the remote head changes, stop and rebuild this plan.

## What will be pushed — 33 files, 4 batches

- **NEW 12:** taskboard 3 + mcp 4 + live_tools 2 + live_brain 2 + PUSH-PLAN (this file).
- **MODIFIED 21:** tools.json, tool_calling.py, config.json, 11 check scripts (phase0/1/2/3/4/6/7, engines, departments, specialists, voice), README.md, dashboard-3d.html, status.json, status.html, store/tasks.json, brain.py, BUILD-LOG.md.
- **All files are UTF-8 text, verified.** No binary. No voice models/output (gitignored) or `__pycache__`.
- **Phase 9 + Phase 10 will be pushed together** — no need to separate them (the brain is still mock because Phase 10 did not touch brain.py/config, phase 9 — pushing will not make the brain live).
- **ZIP + folder tree rebuilt** (`~/workspace/talvenor-master-os-full-2026-11-20.zip` + `~/workspace/talvenor-master-os-folder-structure-2026-11-20.txt`) — with these 33 files.

## Batch 1/4 — Phase 9: taskboard + MCP + live tools (10 file, 9 NEW + 1 MOD)

Commit message: `Talvenor Master OS — Phase 9+10 (1/4): taskboard + MCP + live-ready tools`

1. `dashboards/taskboard.html` (NEW)
2. `scripts/taskboard_server.py` (NEW)
3. `dashboards/TASKBOARD-README.md` (NEW)
4. `00-CEO-Core/mcp/mcp_server.py` (NEW)
5. `00-CEO-Core/mcp/mcp_client.py` (NEW)
6. `00-CEO-Core/mcp/check_mcp.py` (NEW)
7. `00-CEO-Core/mcp/README.md` (NEW)
8. `00-CEO-Core/live_tools.py` (NEW)
9. `scripts/check_live_tools.py` (NEW)
10. `00-CEO-Core/tools.json` (MOD)

## Batch 2/4 — Phase 9: core + check scripts (10 files, all MOD)

Commit message: `Talvenor Master OS — Phase 9+10 (2/4): tool_calling + checks`

1. `00-CEO-Core/tool_calling.py`
2. `scripts/check_phase0.py`
3. `scripts/check_phase1.py`
4. `scripts/check_phase2.py`
5. `scripts/check_phase3.py`
6. `scripts/check_phase4.py`
7. `scripts/check_phase6.py`
8. `scripts/check_phase7.py`
9. `scripts/check_engines.py`
10. `scripts/check_departments.py`

## Batch 3/4 — Phase 9 remaining + Phase 10 live brain (10 files, 2 NEW + 8 MOD)

Commit message: `Talvenor Master OS — Phase 9+10 (3/4): status + live brain adapter`

1. `scripts/check_specialists.py`
2. `scripts/check_voice.py`
3. `00-CEO-Core/config.json`
4. `README.md`
5. `dashboards/dashboard-3d.html`
6. `dashboards/status.json`
7. `dashboards/status.html`
8. `store/tasks.json`
9. `00-CEO-Core/live_brain.py` (NEW — Phase 10)
10. `scripts/check_live_brain.py` (NEW — Phase 10)

## Batch 4/4 — Phase 10 remaining + log + this plan (3 files, 1 NEW + 2 MOD)

Commit message: `Talvenor Master OS — Phase 9+10 (4/4): brain wiring + BUILD-LOG + push plan`

1. `00-CEO-Core/brain.py`
2. `BUILD-LOG.md`
3. `PUSH-PLAN-Phase-9-10.md` (NEW — this file)

## Push rules (per snapshot-push.md)

1. Before each batch, verify remote head == sync-record head (list_commits, read-only).
2. Per batch: make a NUL-delimited manifest file outside the source dir (e.g. `/tmp/push-9-10-batch-N.txt`), then `github push-files` once.
3. After each batch, append an entry to `~/workspace/talvenor-master-os.muse-github-snapshot-sync.json`, then verify the remote head (new head == record head).
4. No binary files — all UTF-8 text. Do not send `__pycache__`.
5. If any batch fails, do not run the next batch — fix it first.
6. When all batches are done, tell Boss the new head.
