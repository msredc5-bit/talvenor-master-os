# PUSH PLAN — Phase 9 + Phase 10 (Talvenor Master OS)

**Status: READY — NOT PUSHED.** Push শুধু Boss-এর "push koro"-তে, main chat-এ (Elora)।
**তৈরি:** 2026-11-20 ~21:55 Dhaka। **Repo:** msredc5-bit/talvenor-master-os, branch `main`।
**Remote head যাচাই (read-only, list_commits):** `b649b9bd57c0de314de7a539b31d0ea94caf61a2` — sync record-এর head-এর সাথে মিলে গেছে ✅ (head commit: "Talvenor Master OS — Phase 8 review fixes (2/2)")।
**Push-এর সময় আবার যাচাই করতে হবে** — remote head বদলে গেলে থামতে হবে, এই plan আবার বানাতে হবে।

## কী push হবে — 33 file, 4 batch

- **NEW 12:** taskboard 3 + mcp 4 + live_tools 2 + live_brain 2 + PUSH-PLAN (এই file)।
- **MODIFIED 21:** tools.json, tool_calling.py, config.json, check 11টা (phase0/1/2/3/4/6/7, engines, departments, specialists, voice), README.md, dashboard-3d.html, status.json, status.html, store/tasks.json, brain.py, BUILD-LOG.md।
- **সব file UTF-8 text, যাচাই করা।** Binary নেই। Voice model/output (gitignored) ও `__pycache__` নেই।
- **Phase 9 + Phase 10 একসাথে push হবে** — আলাদা করার দরকার নেই (Phase 10-এর brain.py/config ছোঁয়া হয়নি বলেই brain এখনো mock, phase 9 — push করলেও brain mock-ই থাকবে)।
- **ZIP + folder tree rebuild করা হয়েছে** (`~/workspace/talvenor-master-os-full-2026-11-20.zip` + `~/workspace/talvenor-master-os-folder-structure-2026-11-20.txt`) — এই 33 file-সহ।

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

## Batch 2/4 — Phase 9: core + check scripts (10 file, সব MOD)

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

## Batch 3/4 — Phase 9 বাকি + Phase 10 live brain (10 file, 2 NEW + 8 MOD)

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

## Batch 4/4 — Phase 10 বাকি + log + এই plan (3 file, 1 NEW + 2 MOD)

Commit message: `Talvenor Master OS — Phase 9+10 (4/4): brain wiring + BUILD-LOG + push plan`

1. `00-CEO-Core/brain.py`
2. `BUILD-LOG.md`
3. `PUSH-PLAN-Phase-9-10.md` (NEW — এই file)

## Push-এর নিয়ম (snapshot-push.md অনুযায়ী)

1. প্রতি batch-এর আগে remote head == sync-record head যাচাই করো (list_commits, read-only)।
2. প্রতি batch: NUL-delimited manifest file source dir-এর বাইরে বানাও (যেমন `/tmp/push-9-10-batch-N.txt`), তারপর `github push-files` একবার।
3. প্রতি batch-এর পরে `~/workspace/talvenor-master-os.muse-github-snapshot-sync.json`-এ entry append করো, তারপর remote head যাচাই করো (নতুন head == record head)।
4. Binary file নেই — সব UTF-8 text। `__pycache__` পাঠাবে না।
5. কোনো batch fail করলে পরের batch চালাবে না — আগে ঠিক করো।
6. সব batch শেষ হলে Boss-কে নতুন head জানাও।
