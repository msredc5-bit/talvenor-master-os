# CEO Core sweep audit — 2026-11-21

Scope: `00-CEO-Core/` only, plus `scripts/` and `store/` at repo root.
Audit only — nothing built, nothing edited except this file.
$0, no keys, no live calls.

NOT touched per task brief: `00-CEO-Core/owner_memory.py`,
`00-CEO-Core/check_drawer_memory.py`, `store/memory.json` contents,
any `MEMORY-STRUCTURE-DECISION` doc (another agent owns those).
`store/memory.json` / `store/tasks.json` were checked for structure
only (top-level keys + record counts), not read in detail.

Terminology warning: "Phase 4" means TWO different things in this repo.
Old Phase 4 = n8n wiring — BUILT (`dashboards/n8n-wiring.md`,
`scripts/sync_status.py`, `scripts/check_phase4.py` 9/9).
New "Phase 4 team factory" (bot-hq / Grok+Muse team factory) — see BLOCKED §1.

---

## DOABLE WITHOUT LLM API

### A. Unwired modules (nothing imports / calls them in production)

**A1. `00-CEO-Core/quiet_schedules.py` — no runner, no caller.**
Only `scripts/check_quiet_schedules.py` imports it. The one seeded
schedule in `store/schedules.json` is `taskboard-queue-watch`, kind
`watch`, status `paused`, interval 10 min, source `store/tasks.json` —
no runner attached. `BUILD-LOG.md:689` already lists "bridge quiet-schedule adoption" as NOT DONE.
Suggested fix: add `scripts/run_quiet_schedules.py` (stdlib runner:
`ScheduleStore` + `run_watch()` with `tasks_queue_state` +
a drain work_fn), plus a check that the runner runs; bridge-cron
adoption itself is BLOCKED §8 (bridge lives outside the repo).

**A2. `00-CEO-Core/live_tools.py` — handlers exist, nothing imports them.**
`LIVE_HANDLERS` (`gmail_send`, `n8n_trigger`) is imported by no
production file — only `scripts/check_live_tools.py`. `tool_calling.py`
mentions live tools in its docstring but never imports the module;
`HANDLERS` (line 266) holds only the 7 mock handlers. By design the
dispatcher always intercepts gated tools as `pending-approval` and
step 4b fail-closes any `live-ready` tool that reaches it, so there is
currently NO execution path at all — not even after Boss approves.
Suggested fix (mock-safe part): import `LIVE_HANDLERS` into
`tool_calling.py` and validate `live-ready` registrations against it
(registry currently validates only `mock` handlers, lines 325–333).
The actual execute-after-approval path is BLOCKED §3.

**A3. `00-CEO-Core/mcp/mcp_server.py` + `mcp_client.py` — no production consumer.**
Only `00-CEO-Core/mcp/check_mcp.py` (9 checks) exercises them. No
runner script, no entry in `scripts/run_office.py`, no daemon, no
external MCP server connected (`00-CEO-Core/mcp/README.md` says
"NOT CONNECTED — per Boss's decision"). The server is runnable
(`python3 00-CEO-Core/mcp/mcp_server.py`, stdio) but nothing starts it.
Suggested fix: add a small `scripts/run_mcp_server.py` entry point (or
document the stdio command in `README.md` / `CEO-README.md`) and a
`check_mcp.py` run in the phase-check chain. Connecting a real external
MCP server is BLOCKED §4.
Note: `mcp_server.py` `tools/call` does NOT block the 2 live-ready
names — `registry.get("gmail_send")` succeeds and `call_tool` records a
real `pending-approval` in `store/approvals.json` by default (env
`TALVENOR_MCP_APPROVALS` unset). Intended (gate holds, nothing
executes), but there is no MCP-side refusal for gated names.

**A4. `00-CEO-Core/voice/loop.py` `handle_voice_text()` — bypasses the CEO Bot.**
The voice path calls `BrainFactory.get_brain(department)` +
`brain.complete(heard)` directly and speaks the raw mock text. It never
goes through `main_ceo_bot.route_task()`, so a voice request never
reaches a Chief, never reads `owner_memory`, never calls a tool, and
never writes a routing note. `jarvis_voice.py` itself is fine (entry is
`scripts/jarvis_voice_loop.py`), but the brain call is a dead-end draft.
Suggested fix: in `handle_voice_text()`, when heard text parses as a
task (or on a "task" prefix/keyword), route via
`main_ceo_bot.route_task()` and speak the routed result; keep
free-form chat on `brain.complete()`.

**A5. `00-CEO-Core/skill_finder.py` — wired to the router, dead-ended elsewhere.**
`main_ceo_bot.route_task({"type": "find_skill", ...})` works, but:
- `scripts/run_office.py` has no way to surface it (requires
  `--business`; `--task find_skill` would work only by accident of
  `route_task` checking `type` first) and the task-board form
  (`dashboards/taskboard.html` datalist) has no `find_skill` option.
- `propose_skill()` has no duplicate check — the same
  `candidate_repo` + `candidate_skill` can be appended repeatedly.
- `store/skill-proposals.json` does not exist yet (lazy-created on
  first proposal) and NOTHING reads proposals — no list/review command,
  no adapt step.
Suggested fix: add `find_skill` to the board datalist + a
`run_office.py` `--task find_skill` example; add dedup in
`propose_skill()`; add a `scripts/list_skill_proposals.py` (read-only).
Clone/adapt/install of a proposed skill is BLOCKED §5.

**A6. `00-CEO-Core/usage_ledger.py` — wired in code, never fed in production.**
`tool_calling._finish()` records a `$0` receipt only when
`ledger_path` is passed. NOBODY passes it in production:
`mcp/mcp_server.py` passes `approvals_path` + `calls_log_path` only;
`scripts/run_office.py` never calls `call_tool`; the three engine
wrappers (`01/02/03-*-Department/engine/tool_calling.py`) forward
`ledger_path=None` by default. Result: `store/usage_ledger.json` has
0 records. Likewise `check_in_required()` / `over_monthly_cap()` /
`task_total()` / `spend_report()` have no production callers (only
`scripts/check_memory_ledger.py` + the module's own `__main__`), and
the dashboard (`scripts/sync_status.py`) shows no ledger numbers.
Suggested fix: pass the real ledger path in `mcp_server.py` and in the
engine wrappers' defaults, and surface `monthly_total()` /
`total_calls` in `status.json` via `sync_status.py`.

**A7. `00-CEO-Core/live_brain.py` `build_provider_chain()` ignores `enabled`.**
`config.json` `providers.*.enabled` is read NOWHERE (no match in
`live_brain.py`, `brain.py`, or `scripts/check_providers.py`). The
chain is `["openrouter", "meta", "mock"]` while
`providers.openrouter.enabled` is `false` — if `brain` were flipped
to `live`, OpenRouter would still be tried first. The flag is
decorative today.
Suggested fix: in `build_provider_chain()`, skip chain entries whose
`providers[name].enabled` is `false` (mock-safe; changes nothing while
`brain` is `mock`).

**A8. `00-CEO-Core/brain.py` — `get_brain("digital-product")` raises ValueError.**
Only `agency` / `content` are handled. `02-Digital-Product-Department/chief_of_staff_products.py:289`
works around it with `BrainFactory.get_brain("agency")` — the Vet Kit
chief silently uses the agency mock/seed (`master-os-phase1`).
Suggested fix: add an explicit `"digital-product"` branch (own seed,
documented) or an explicit alias to agency with a comment.

### B. Router / gateway gaps

**B1. `00-CEO-Core/main_ceo_bot.py` — dead code + stale text.**
- The gated-action block after the three Chief branches (~lines
  255–270: `approval = None; action = task.get("gated_action") …`) is
  UNREACHABLE: unknown `business` raises earlier, and each of the
  three branches returns. The `ApprovalGateway` use at line 229 only
  exists in dead code.
- Stale comments: line 43 `# business key -> Chief of Staff module
  (Phase 0: stub modules)`; line 263 note `"Only Jarvis voice
  stays a STUB"` — `jarvis_voice.py` has been REAL since 2026-11-17.
- The `find_skill` branch (lines 138–160) does no memory read and
  writes no routing note, unlike the three business branches.
Suggested fix: delete the dead tail (or move its intent into the
Chiefs, where gated handling already lives); refresh the two comments;
add `context_for("main_ceo_bot")` + `_record_route_note()` to the
`find_skill` branch.

**B2. No operator entry point for approvals — approvals can be created but never decided.**
`ApprovalGateway.approve()` / `reject()` are called in production by
nobody: the only callers are check scripts and `__main__` self-tests.
There is no `scripts/approve.py`, no `--approve` flag on
`run_office.py`, and no approve button/endpoint on the task board.
A pending approval today can only be decided by an agent calling the
Python API directly.
Suggested fix: add `scripts/approve.py --list [--approve ID --word
send | --reject ID]` (read-only list + gate-word-checked decide,
TEMP-path friendly like the checks). Executing the approved live action
afterwards is BLOCKED §3, not this item.

**B3. No expiry anywhere — `"expired"` status is dead.**
`trust_gate.py` `CONFIRMATION_STATUSES` includes `"expired"`, but no
code ever sets it; `ApprovalGateway` records have no TTL and pending
approvals live forever. (Memory notes approval cards expire after
~20 min in the chat UI — that expiry is not implemented in this repo.)
Suggested fix: add a configurable TTL + a sweep/mark-expired step in
`ApprovalGateway` / `ConfirmationStore`, with `approve()` refusing
expired records. The TTL value itself needs Boss's word — use an
explicit constant so it is one decision, not a silent default.

**B4. `trust_gate.py` — email-pause note is gmail-only.**
The PAUSED note (lines ~277–286) attaches only when
`tool_name == "gmail_send"`. A `send` via `n8n_trigger` (also
`gated_action: "send"`) gets no pause note. Decision is still `ask`
without owner words, so this is a messaging gap, not a safety hole.
Suggested fix: attach the pause note for any `send` action while email
is PAUSED, or key it on the action rather than the tool name.

**B5. `"upload it"` gate word has no gated action.**
`config.json` `gates.words` defines `"upload it" = "upload a video"`,
but `GATED_ACTIONS` (`human_approval_gateway.py`) is only
`send / publish / spend / delete` — there is no `upload` action, so an
upload approval must be requested as `publish`.
Suggested fix: either add `"upload"` to `GATED_ACTIONS` +
`GATE_WORD_FOR_ACTION` + `trust_gate.py` mirrors, or remove
`"upload it"` from `config.json` words so the table matches the code.

### C. Task board (no check coverage at all)

**C1. `scripts/taskboard_server.py` is covered by NO check script.**
There is no `check_phase9.py` (Phase 9 is split across
`check_mcp.py` + `check_live_tools.py`, neither touches the server),
and no `check_phase5.py` / `check_phase8.py` either (Phase 5 is covered
by `check_engines.py`; Phase 8/agentic by `check_departments.py` +
`check_specialists.py`). The server has never been exercised by any
check — no test POSTs to `/api/tasks`, no test of `validate_task_body`.
Suggested fix: add `scripts/check_taskboard.py` (start server on an
ephemeral port in-process, POST valid/invalid bodies, GET `/api/tasks`,
verify the real `store/tasks.json` is untouched via TEMP paths — the
server hardcodes `TASKS_PATH` to the real store, so the check needs an
env override first; see C2).

**C2. `scripts/taskboard_server.py` hardcodes the real store.**
`TASKS_PATH` / `STATUS_PATH` / `BOARDPAGE_PATH` are module constants
from repo root — no env override (unlike `mcp_server.py`, which takes
`TALVENOR_MCP_APPROVALS` / `TALVENOR_MCP_CALLS_LOG`). Any test run
writes the real queue.
Suggested fix: honor `TALVENOR_TASKBOARD_TASKS` (and status/board
overrides) like the MCP server does.

**C3. `dashboards/taskboard.html` — board is queue-only, and thin.**
- No approvals view and no approve/reject control (see B2).
- Done tasks show no `result` (drain writes `result` + `drained_at`
  into the record; the table renders only title/type/business/status/
  queued_at).
- The new-task form always posts `payload: {}` — no payload input.
- Type datalist lacks `find_skill` (see A5).
- No cancel/delete of a queued task; no GET-single-task endpoint.
Suggested fix: render `result` (truncated) for `done`/`failed` rows,
add a payload textarea, add `find_skill` to the datalist, add
`DELETE /api/tasks/<id>` (queued-only) + a cancel button.

### D. Config / dashboard drift

**D1. `00-CEO-Core/config.json` — top-level fields stale; missing Phase 10 record.**
- `"phase": 9`, `"built": "2026-11-20"`, but `honest_status.phases`
  already records `phase_11_providers` + `improvement_p1/p2/p3`
  (2026-11-21). The top-level number lags the honest record by two
  phases.
- `honest_status.phases` has NO `phase_10_live_brain` key at all,
  although `brain.py`'s docstring says "see config.json
  honest_status.phases phase_10_live_brain" and `check_phase6.py:336`
  reads that key when `brain == "live"`. The 2026-11-20 ~01:44 live
  probe failure (tunnel 403, `api.meta.ai` unreachable, $0, key
  validity unproven) is recorded nowhere in config.
Suggested fix: bump `"phase"` to 11, update `"built"`, and add
`"phase_10_live_brain": "NOT PROVEN LIVE — probe 2026-11-20 01:44
failed (tunnel 403, api.meta.ai unreachable from this VM), $0 spent,
key validity UNPROVEN; brain stays mock"`.

**D2. `scripts/sync_status.py` — dashboard stops at Phase 7.**
`collect_status()` `phase_status` lists only `phase_0`–`phase_7`
(lines 307–315). `phase_9_connections`, `phase_11_providers`,
`agentic_phase_1/2/3`, `improvement_p1/p2/p3`, `unified_os` exist in
config but never reach `dashboards/status.json` / `status.html`.
The HTML footer hardcodes `Built: 2026-11-16 (Phase 0 + … + Phase 4
n8n wiring)` (line ~470) — every sync rewrites a stale date and a
stale phase list.
Suggested fix: build `phase_status` from all of
`honest_status.phases` (or at least add the missing keys + rows), and
use `config["built"]` / `config["version"]` for the footer date.
Minor: `read_voice_status()` STUB-branch fallback string
`"Jarvis voice (mic not connected)"` (line 126) is stale — mic is connected
via `voice/loop.py`; the current dashboard shows REAL, so this only
matters if voice ever regresses. (Note: `check_phase4.py` comment #5
claims the dashboard still shows that line — it does not anymore;
the comment itself is stale.)

**D3. `store/vault/` — promised, never written.**
`store/vault/README.md` says finished-task results land here as
`<date>-<business>-<short-title>.md`, first file from "Phase 1's first real task". Nothing in any `.py` file references `vault` except
`check_phase0.py:42` (asserts the README exists). `store/tasks.json`
already holds a `done` record, yet the vault is still empty (README
only). Suggested fix: add a small vault-write helper and call it from
`run_office.py` drain (and/or the Chiefs) when a task completes, or
decide the vault is manual and update the README to say so.

### E. Checks — nothing trivially passes, but there are weak spots

No `check()` call found is an unconditional pass: the `check("…",
True, …)` lines (`check_phase0.py:132,148`,
`check_engines.py:85`, `check_voice.py:118,169`,
`mcp/check_mcp.py:162`) all sit inside `try:` after real asserts, with
a matching `check(…, False, …)` in `except:` — reaching the line IS
the assertion. Weakest real checks:
- `scripts/check_phase4.py` #6: substring checks (`"Phase 4" in html
  and "BUILT" in html`) — could pass on unrelated text.
- `scripts/check_phase4.py` #5: greps `jarvis_voice.py` source for
  `"REAL"` / absence of `NotImplementedError` — source-text check, not
  a behavior check.
- `scripts/check_phase4.py` #4: reads workflow JSONs OUTSIDE the repo
  (`~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json`,
  `~/workspace/talvenor-callback/n8n-workflow-talvenor-callback.json`) —
  the check fails if Boss moves/renames those files, even though the
  repo itself is fine. Suggested fix: tolerate missing files with a
  SKIP (or record the dependency in the check's docstring).
- `scripts/check_phase0.py` #6 / `scripts/check_voice.py`: same
  source-grep pattern for voice REAL-ness (acceptable, but weaker than
  calling the functions — `check_voice.py` does also run
  `voice_test.py`).
- All `except ValueError: pass` / `except …: pass` hits in
  `main_ceo_bot.py`, `trust_gate.py`, `usage_ledger.py`,
  `quiet_schedules.py`, `human_approval_gateway.py`, `mcp_client.py`
  are inside `__main__` self-tests (negative-path assertions) — not
  gaps.

### F. Store structure (keys + counts only — contents not read in detail)

- `store/tasks.json`: `{schema, records}`, 1 record — `done`,
  type `research`, business `agency`. Schema fine.
- `store/memory.json`: `{schema, note, boxes, entries}`, 19 entries.
  (Contents not inspected — another agent owns memory structure.)
- `store/approvals.json`: 0 records. `store/confirmations.json`:
  0 records. `store/schedules.json`: 1 record (paused queue-watch,
  see A1). `store/usage_ledger.json`: 0 records (see A6).
- `store/skill-proposals.json`: DOES NOT EXIST (see A5).
- `store/tool_calls.json`: DOES NOT EXIST — nothing has logged a call
  through the default path yet (MCP server only writes it if actually
  run; checks use TEMP paths). Lazy creation is fine; its absence
  confirms no production tool call has been logged.
- `store/vault/`: README only, empty (see D3).

### G. Small items

- `00-CEO-Core/tool_calling.py` `_validate_args()`: unknown declared
  arg types and extra fields are silently ignored (documented as
  "schema bug, not a call failure"). Acceptable, but a strict-mode
  warning would catch schema drift.
- `tools.json`: 9 tools, 0 with `status: "stub"` — the `blocked-stub`
  path is only exercised by a synthetic stub in `check_engines.py`.
  No stub tool is currently registered, so nothing is waiting on a
  stub handler. The 7 mock handlers all exist in `HANDLERS`; the 2
  live-ready handlers exist in `LIVE_HANDLERS` (see A2).
- `00-CEO-Core/skill_finder.py` `REMOTE_SOURCES` is a static list of
  12 repos (names + licenses only) — no online verification by design
  (Mira does online search). Not a gap, noted for completeness.
- `trust_gate.py` `GATE_WORD_FOR_ACTION` duplicates
  `human_approval_gateway.py`'s table to avoid an import cycle;
  `check_gate.py` verifies the two stay in sync — that check exists
  and is a real check.

---

## BLOCKED

**1. Phase 4 TEAM FACTORY (new meaning) — no code, no checks, blocked on live brain + Boss's decision.**
What exists: only mentions. `README.md:201` — "Phase 4 team factory
blocked without a live brain"; `BUILD-LOG.md:689` — "Phase 4 team factory
— blocked without a live brain (needs bot-hq's real Hermes gateway)";
`MEMORY-STRUCTURE-DECISION-2026-11-21.md:142` lists live-brain proof as
the team-factory blocker. There is no factory module, no `spawn_team`
/ `build_team` handler, no team-spec schema, no `tools.json` entry, no
check. (Do not confuse with old Phase 4 n8n wiring, which is BUILT.)
What could be built in mock: a draft-only team-factory (team spec →
roster/role draft, no spawning, no live agents) — but Boss's
2026-11-21 order holds Phase 4 team factory until live-brain proof on
his PC, and the Grok+Muse combined-system deck is still pending his
decision (lock architecture vs prove live brain first). So even the
mock draft waits on Boss's word.
Reason: needs live LLM API (live brain proof) + Boss's decision.

**2. Live brain — flipping `brain` to `live`, or proving it.**
`brain.py` / `live_brain.py` construction is complete and 0-call safe,
but `complete()` has never succeeded: 2026-11-20 ~01:44 probe failed
(tunnel 403, `api.meta.ai` unreachable from this VM), $0 spent, key
validity still unproven. No further live retry without Boss's new word.
Reason: needs live LLM API + Boss's PC network + Boss's decision.

**3. Real execution of `gmail_send` / `n8n_trigger`.**
`live_tools.py` deliberately contains no `subprocess.run` / `urlopen`
call. Real sending additionally needs: Boss's exact gate word per send
(no auto-approve path exists by design); email restart — SPF/DMARC
DNS fix still not applied, sending PAUSED since 2026-11-14; and for
the callback workflow, Boss's Twilio number import + n8n webhook URL.
Reason: needs Boss's account/DNS steps + Boss's exact approval.

**4. Real external MCP server connection.**
`mcp/README.md`: "Live MCP server connection: NOT CONNECTED — per Boss's decision." The client can already speak stdio JSON-RPC to any
server; pointing it at a real one (and any credential it needs) is
Boss's call. Reason: needs Boss's decision (+ external account/key
if a server needs one).

**5. Skill-finder upstream clone + adapt/install of proposed skills.**
Boss's 2026-11-21 ~10:13 order: find the `skill-finder` skill/repo,
clone it, connect it to Main CEO Bot — local search + DRAFT proposal
(`skill_finder.py`, wired into `route_task`) is done, but the upstream
repos (`cubicyyy/auto-research-skills`, `vercel-labs/skills`, etc.)
are referenced only in the module docstring, not cloned into the repo;
and turning a proposal into an adapted skill file / install is
forbidden without Boss's "ok" (skill rules: draft-only, never verbatim,
adapt — never copy-paste). Reason: needs Boss's decision/approval.

**6. Voice — first real mic test + quality judgement.**
`jarvis_voice.py` / `voice/loop.py` are REAL and offline ($0), but mic/
speaker cannot be live-tested on this VM; Bengali Piper voice quality
is unjudged (no native listener has heard it) and Bengali STT accuracy
is unknown until Boss speaks to it on his PC. Reason: needs Boss
(his PC, his ears).

**7. Spend gate-word collision — `"go"` approves three things.**
`GATE_WORD_FOR_ACTION` (`human_approval_gateway.py`, mirrored in
`trust_gate.py`): `"spend": ("go",)`, `"delete": ("go",)`, while
`config.json` defines `"go"` as "advance a build phase". One word
currently authorises spending, deleting, and advancing a build phase.
Giving `spend` its own word (e.g. `"spend"`) would be a one-line code
change, but the gate words are Boss's recorded decisions — changing
them needs his word. Reason: needs Boss's decision.

**8. Quiet-schedule adoption by the bridge cron.**
The runner itself is doable (A1), but the bridge cron (every 10 min,
outside this repo) adopting `taskboard-queue-watch` is a scheduling/
ops decision for the parent agent / Boss. The seeded schedule stays
`paused` until then. Reason: needs parent/Boss decision (bridge lives
outside the repo).

**9. Vet Kit Gate 0 (Lemon Squeezy signup test) — out of CEO-Core scope, noted.**
`config.json` `businesses[2]` status: "Gate 0 NOT passed — Lemon
Squeezy signup test is Boss's step". Kit build/sale stays blocked.
Reason: needs Boss's account step (Lemon Squeezy signup).

**10. 4 GAP worker roles — out of CEO-Core scope, noted from the 2026-11-21 MEMORY.md update.**
Ad Campaign, CRM, Expense Tracking, Backup & Recovery — skill files
exist, worker code does not (registry 65/69 EXISTING, 4 GAP).
These live in `01-Agency-Department/`, not CEO Core, so they are
outside this audit's scope; listed here only because the
full-completion order now names them. Reason: department-scope build
work (doable in mock, but not CEO Core — needs the department agent /
Boss's prioritisation).

---

## Audit notes

- Files read in full: `brain.py`, `live_brain.py`, `live_tools.py`,
  `tool_calling.py`, `main_ceo_bot.py`, `trust_gate.py` (head +
  `trust_check` + store), `human_approval_gateway.py`,
  `usage_ledger.py`, `quiet_schedules.py` (head + `__main__`),
  `skill_finder.py`, `jarvis_voice.py`, `config.json`, `tools.json`,
  `mcp/mcp_server.py`, `mcp/mcp_client.py`, `mcp/check_mcp.py` (head),
  `mcp/README.md`, `voice/loop.py` (core), `scripts/run_office.py`,
  `scripts/taskboard_server.py`, `scripts/check_phase4.py`,
  `scripts/sync_status.py` (key sections), `dashboards/taskboard.html`,
  `store/vault/README.md`.
- Grep-verified: every `TODO`/`stub`/`pass` hit in scope is either a
  `__main__` self-test negative assertion or a deliberate design
  branch (`blocked-stub`, `blocked-trust`); no hidden unfinished
  handler was found in CEO Core.
- Import graph (production code only, checks excluded):
  - Wired: `brain` ← 3 Chiefs + `voice/loop`; `trust_gate` +
    `human_approval_gateway` ← `tool_calling`, `main_ceo_bot`, Chiefs;
    `usage_ledger` ← `tool_calling` (dormant, A6); `skill_finder` ←
    `main_ceo_bot` (find_skill branch); `main_ceo_bot` ←
    `run_office.py`; `jarvis_voice` ← `jarvis_voice_loop.py`.
  - Unwired: `quiet_schedules` (A1), `live_tools` (A2),
    `mcp_server`/`mcp_client` (A3). `live_brain` is wired but dormant
    (only constructed when `brain == "live"`).
- No file other than this report was written or edited.
