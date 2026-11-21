# Sweep Audit — Digital Product (02) + Content Creation (03)

**Date:** 2026-11-21 · **Scope:** `02-Digital-Product-Department/` and
`03-Content-Creation-Department/` only · **Mode:** AUDIT ONLY — no repo files
built or edited (this report file excepted). $0, no keys, no live calls.

**Method:** file inventory, `grep` for TODO/FIXME/GAP/DRAFT/MOCK/STUB/BLOCKED,
read of both Chiefs, both `engine/tool_calling.py` + `tools.json`, both
`engine/STAFF.md`, `03-.../pipeline.md`, `gate0-status.md`,
`toolpilot-status.md`, all section agents, and `00-CEO-Core/tool_calling.py`
(handler registry). `python3 -m py_compile` on every `.py` in 02/03:
**ALL COMPILE OK**.

## Headline corrections to the task's background premises

1. **The "5 staff roles with skill files but no code workers" claim is now
   STALE.** Phase 7 (2026-11-17) built code workers for every role:
   - 02: **7/7 roles have workers** — the original 5 plus **Kit QA**
     (`sections/product/agents/kit_qa.py`) and **Kit Sales**
     (`sections/sales/agents/kit_sales.py`), both wired into
     `chief_of_staff_products.py` `SECTION_ROUTING` (`kit_qa`, `kit_sales`,
     `support_draft`).
   - 03: **10/10 section roles have agents** — 6 vendored workers in
     `engine/workers/src/creator_workers.py` plus 4 standalone section agents
     (Content Planner, Performance Analyst, Growth Agent, Repurpose Agent),
     all wired into `chief_of_staff_content.py` (`ROUTING` 6 + `SECTION_ROUTING` 4).
   - **Zero roles in 02/03 have a skill file but no code worker.**
2. **The real gap is different: 10 section agents exist but are ORPHANED —
   no dispatch path ever calls them** (see Doable §A). This is the biggest
   doable-without-LLM item in scope.
3. **The 4 roles named in the 2026-11-21 MEMORY.md update (Ad Campaign, CRM,
   Expense Tracking, Backup & Recovery — skill exists, no worker code) do NOT
   exist anywhere in 02/03** (grep: no matches except "Backup rail" =
   Polar payment rail in `gate0-status.md`). They belong to another
   department (presumably 01-Agency) — out of this audit's scope; parent
   should route them to the Agency sweep, not this one.

---

## DOABLE WITHOUT LLM API

### A. Orphaned section agents — wire them into the Chiefs (10 agents)

Every agent below compiles and implements `run(task, brain, gateway,
approvals_path)`, but a repo-wide grep shows each is referenced **only** in
`engine/STAFF.md` and its own section skill file — no `.py` ever imports or
routes to it. Suggested fix: add each to the Chief's `SECTION_ROUTING`
under a distinct task type (or route the existing in-Chief task types through
the section agent instead of the static in-Chief branch). Pure routing code,
mock brain, no LLM needed.

**02 — `02-Digital-Product-Department/chief_of_staff_products.py`:**
`ROUTING` handles `kit_build`, `clinic_research`, `gate0_check`,
`launch_prep` **in-Chief with static dicts** (lines ~355–405); the matching
section agents are never called:

| # | Orphaned agent | Skill file | What it should do when wired |
|---|---|---|---|
| A1 | `sections/product/agents/kit_builder.py` (`KitBuilderAgent`, 170 lines) | `sections/product/skills/kit-builder.md` | Return kit blueprint summary + 6-part build order; `blocked-gate0` until Gate 0 passes |
| A2 | `sections/research/agents/clinic_researcher.py` (`ClinicResearcherAgent`, 157 lines) | `sections/research/skills/clinic-researcher.md` | Report PA list status 39/100 + verification rules (official site first, chains excluded, "Not publicly listed" never invented) |
| A3 | `sections/launch/agents/launch_manager.py` (`LaunchManagerAgent`, 159 lines) | `sections/launch/skills/launch-manager.md` | Return launch checklist DRAFT; `blocked-gate0` until Gate 0 passes |
| A4 | `sections/finance/agents/payment_rails_checker.py` (`PaymentRailsCheckerAgent`, 170 lines) | `sections/finance/skills/payment-rails-checker.md` | Return Gate 0 test steps + record Boss's verbatim result (never writes PASSED itself) |

**03 — `03-Content-Creation-Department/chief_of_staff_content.py`:**
`ROUTING` (lines ~95–101) calls the **vendored** workers directly;
`SECTION_ROUTING` (lines ~107–112) covers only `plan_weekly`,
`performance_analyze`, `growth_research`, `repurpose_plan`. The 6
"WRAPPED" section agents are never called:

| # | Orphaned agent | Skill file | What it should do when wired |
|---|---|---|---|
| A5 | `sections/plan/agents/topic_researcher.py` (`TopicResearcherAgent`) | `sections/plan/skills/topic-researcher.md` | Wrap vendored `TopicResearcher` (3 topics + angle/fit/next-step) |
| A6 | `sections/produce/agents/script_writer.py` (`ScriptWriterAgent`) | `sections/produce/skills/script-writer.md` | Wrap vendored `ScriptWriter` (hook options + spoken script, VOICE.md DRAFT warning) |
| A7 | `sections/produce/agents/visual_producer.py` (`VisualProducerAgent`) | `sections/produce/skills/visual-producer.md` | Wrap vendored `VisualProducer` (shot list + thumbnail idea; `video_file=None`, stage 4 BLOCKED) |
| A8 | `sections/publish/agents/caption_writer.py` (`CaptionWriterAgent`) | `sections/publish/skills/caption-writer.md` | Wrap vendored `CaptionWriter` (platform caption + hashtag pack) |
| A9 | `sections/publish/agents/publish_prep.py` (`PublishPrepAgent`) | `sections/publish/skills/publish-prep.md` | Wrap vendored `PublishPrep` (checklist, `ready_to_publish: False`) |
| A10 | `sections/analyze/agents/performance_tracker.py` (`PerformanceTrackerAgent`) | `sections/analyze/skills/performance-tracker.md` | Wrap vendored `PerformanceTracker` (report template; metrics 0) |

Note: `03-.../engine/STAFF.md` Phase 7 table marks A5–A10 "WRAPPED" and
`02-.../engine/STAFF.md` says the 4 existing ROUTING types run "as before" — the wiring was deliberately left unchanged in Phase 7, which is
exactly why these 10 agents are dead code today. Wiring them is the
single largest completion in scope and needs no LLM.

### B. Pipeline helper scripts referenced by skills but absent from the repo (03)

`pipeline.md` stages and section skills name these tools, but `find` across
the whole repo returns **no such files** — only the vendored
`engine/workers/src/creator_workers.py` + `src/workers/base.py` exist
(`engine/workers/SOURCE.md` confirms no youtube-skills tool was vendored).
Each can be built as a **deterministic, rule-based mock** (fixed rubric +
Boss-supplied inputs, no LLM, no network):

| # | Missing file (referenced in) | Stage | Suggested mock fix |
|---|---|---|---|
| B1 | `tools/niche_score.py` (pipeline.md `0a-niche`; `engine/skills/topic-researcher.md:14`) | 0a-niche | Deterministic 4-axis scorer (demand / competition gap / monetization / fresher-fit, 1–10 each) with a written rubric; scores only from Boss-supplied facts, never invented trend data |
| B2 | `tools/concept_score.py` (pipeline.md `2a-concept`; `sections/plan/skills/topic-researcher.md:16`) | 2a-concept | Deterministic concept scorer: 3–5 concepts, 1–10 with one-line reason per score from a fixed rubric |
| B3 | `hookscore.py` + `hooks.json` (pipeline.md `2b-script`; `engine/skills/script-writer.md:19`) | 2b-script | Static list of the 21 hook formulas as templates + deterministic hook scorer (length, promise-confirm, open question) — no LLM generation, scoring only |
| B4 | `yt-package/title.py` (pipeline.md `3-visual-pack`; `engine/STAFF.md` §3) | 3-visual-pack | Deterministic title/thumbnail linter: char count, keyword presence, thumbnail-text length — same rules already used manually for the Week 1 title (48 chars, lint 100/100) |
| B5 | `scripts/loop_next.py` (pipeline.md `10-next-plan`; `engine/skills/content-planner.md:21`) | 10-next-plan | Deterministic next-brief generator: reads previous report file if present, else emits "No previous report (videos 0), so the next brief repeats the previous plan" |
| B6 | `upload_youtube.py` (pipeline.md `9-upload`; `chief_of_staff_content.py:18,198`) | 9-upload | **Write the script only** (OAuth + resumable upload, `DEFAULT OFF`, refuses to run unless `YOUTUBE_UPLOAD_ENABLED=1` + "upload it"); execution/verification stays BLOCKED (see Blocked §B5) |

### C. `engine/tool_calling.py` stubs completable as mock/draft handlers

Both wrappers are thin forwarders to `00-CEO-Core/tool_calling.py`, whose
`HANDLERS` registry already implements all 7 mock handlers
(`draft_email`, `research_notes`, `draft_caption`, `draft_script`,
`kit_outline_read`, `status_read`, `booking_reply`) — verified in
`00-CEO-Core/tool_calling.py:266–273`. The gated stubs have `handler: null`
and correctly fail closed today. Two can gain honest mock handlers:

| # | Tool (`tools.json`) | Suggested fix (mock/draft only) |
|---|---|---|
| C1 | 02 `launch_kit` (`gated: publish`, status `stub`) — `02-Digital-Product-Department/engine/tools.json` | Add a mock handler returning the same launch-checklist DRAFT the Chief's `launch_prep` already returns (Gate 0, 6 kit parts, Gate 1, listings, sales page, 25/day mail plan) with `launch_blocked: true` — a draft checklist, never a launch |
| C2 | 03 `publish_post` (`gated: publish`, status `stub`) — `03-Content-Creation-Department/engine/tools.json` | Add a mock handler returning the PublishPrep checklist draft (`ready_to_publish: false`) for the given `post_id` — a prep checklist, never a publish |

### D. Deterministic metrics report (03, stage 8-report) — doable, no LLM

- **File:** `03-Content-Creation-Department/sections/analyze/agents/performance_analyst.py`
  (`PerformanceAnalystAgent`) + `sections/analyze/skills/performance-analyst.md`.
- **Missing:** the agent only drafts analysis prose; there is no code that
  **reads** Boss-pasted numbers. Suggested fix: a stdlib-only parser that
  takes a metrics file (CSV/JSON: views, retention, CTR, subs per video)
  and deterministically computes best/worst + the one concrete change —
  same "never estimate numbers" rule, just automated arithmetic. Blocked
  from real use until a video is published (metrics are 0), but the parser
  itself is buildable and testable now with sample data.

### E. Stage 5-edit as an input-driven mock (03)

- **File:** `03-Content-Creation-Department/pipeline.md` stage `5-edit`
  (yt-edit: deadair, chapters, shorts) — currently BLOCKED for lack of a
  transcript.
- **Suggested fix:** build a deterministic transcript-in → cut-list-out
  tool (deadair timestamps, chapter boundaries, shorts moments) that takes
  a transcript file as input. No LLM needed (rule-based timestamps); it
  simply has no real input until stage 4 produces a video. This matches
  the Repurpose Agent's existing pattern
  (`sections/growth/agents/repurpose_agent.py` already returns a
  repurpose PLAN without a transcript).

### F. Stage 4-video stills + Ken Burns mock render (03) — buildable, with a caveat

- **File:** `03-Content-Creation-Department/pipeline.md` stage `4-video`;
  `sections/produce/agents/visual_producer.py` (`video_file` always `None`).
- **Suggested fix:** a CPU-only FFmpeg stills + Ken Burns render path
  (the repo's own `local-reel-factory` / `local-auto-video` skills describe
  this pattern) can be vendored as a **mock** render so the pipeline runs
  end-to-end. **Caveat:** `pipeline.md` itself states this is not true
  motion, and Boss's standard is REAL footage only — so this unblocks a
  demo/placeholder render, not a publishable video. Real video stays
  BLOCKED (see Blocked §B4).

### G. Documentation sync fixes (no LLM, no code risk)

| # | File | Fix |
|---|---|---|
| G1 | `02-Digital-Product-Department/engine/STAFF.md:9` | Header still says "exactly **5** staff" while the Phase 7 table below it says 7 (Kit QA + Kit Sales added). Update header to 7. |
| G2 | `02-Digital-Product-Department/engine/skills/` (5 files) | Missing `kit-qa.md` and `kit-sales.md` — they exist only under `sections/product/skills/` and `sections/sales/skills/`. Copy/sync them into `engine/skills/` like the other 5, or delete the duplication and point `engine/skills/` at the section copies. |
| G3 | `03-Content-Creation-Department/engine/skills/` (8 files) | Missing `growth-agent.md` and `repurpose-agent.md` — they exist only under `sections/growth/skills/`. Same sync fix as G2. |
| G4 | `03-Content-Creation-Department/engine/STAFF.md` ("6 workers, 2 Chief-level roles") | Stale vs the Phase 7 table below it (10 agents). Update to 10. |
| G5 | `03-Content-Creation-Department/pipeline.md` "Honest limits" | Upstream artifact page `creator-os-combined` shows 8 stages vs the real 13 — `pipeline.md` says "won't be fixed unless Boss says so". It is a doc-only fix in the upstream checkout (`~/workspace/creator-os-combined/`), no LLM needed, but needs Boss's word per the file's own note. |

### H. PA vet list 39/100 — manual research task, no LLM needed (02)

- **Files:** `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv`
  (39 rows), `pa-vet-list/README.md`, `sections/research/agents/clinic_researcher.py`.
- **Missing:** 61 more verified independent PA clinics. The agent returns
  status drafts only; **adding rows is real web verification work**
  (official website first, chains excluded: Banfield, VCA, Vetco, BluePearl,
  Thrive, PetVet365; "Not publicly listed" when no public email). No LLM
  is required to do it — it is manual research, not a code gap. Per
  `gate0-status.md`, the remaining 61 are planned **after** Gate 0 passes,
  so this is sequenced behind Blocked §B1, not independently blocked.

---

## BLOCKED

Each item names the reason: **needs live LLM API / Boss's account / Boss's
decision**. Nothing here can be honestly completed in mock.

### B1. Gate 0 — Lemon Squeezy signup test (Boss's account + Boss's step) — 02
- **Files:** `02-Digital-Product-Department/gate0-status.md` (Status: NOT
  PASSED, 2026-11-16), `chief_of_staff_products.py` (`gate0_passed()`),
  `sections/product/agents/kit_builder.py`, `sections/launch/agents/launch_manager.py`.
- **Reason:** Boss's own ~15-min step at lemonsqueezy.com (individual
  signup, BD bank payout check). No code or LLM can do it — it is Boss's
  account and Boss's result. **Gates everything downstream:** kit 6 parts
  build, Gate 1 (cadence vs AAHA/PetDesk), store listings, launch, sales.
  Fallback order if it fails (Polar → Gumroad) also needs Boss's signup
  tests. If all rails fail, the product track is KILL per `gate0-status.md`.
- **Note:** the kit's 6 parts themselves need **no LLM** to build (static
  scripts/SOP/tracker templates) — they are blocked by this Boss decision,
  not by the lack of a live brain.

### B2. `sell_kit` — must stay a stub (real-world fact, not a mock) — 02
- **File:** `02-Digital-Product-Department/engine/tools.json`
  (`sell_kit`, `gated: spend`, `handler: null`).
- **Reason:** recording a sale asserts real revenue from a real buyer.
  A mock handler would fabricate sales (sale is 0, kit is 0/6 built).
  Completable only as a **Boss-confirmed-sale recorder**: gated `spend`,
  requires Boss's exact word + real payment proof, writes the record —
  and that path needs Gate 0 passed first (B1) plus a real buyer.

### B3. `spend` tool — must stay a stub ($0 cap) — 03
- **File:** `03-Content-Creation-Department/engine/tools.json`
  (`spend`, `gated: spend`, `handler: null`).
- **Reason:** $0 spend cap is a Boss order (2026-10-21 Maximum Autonomy
  L2). A mock spend handler would either fake spending or open a real
  spend path. Needs a Boss decision to fund a specific paid tool/API
  before any handler exists.

### B4. Stage 4-video — real video (Boss's footage / Boss's GPU / paid key) — 03
- **Files:** `03-Content-Creation-Department/pipeline.md` stage `4-video`
  (BLOCKED), `sections/produce/agents/visual_producer.py`,
  `toolpilot-status.md` (Week 1 READY TO RECORD).
- **Reason:** Boss's standard is REAL footage only. Needs one of: Boss's
  OBS recording (Week 1's 5 Nano Banana 2 tests), Boss's PC GPU name
  (unknown since 2026-11-01 — decides whether FramePack/WanGP runs),
  or a paid video key (excluded by the $0 cap). AI video generation is
  REGION-BLOCKED here — retry is not an option. Mock stills+Ken Burns
  render is doable (Doable §F) but is not a publishable video.

### B5. Stage 9-upload — execution (Boss's account + Boss's word) — 03
- **Files:** `03-Content-Creation-Department/pipeline.md` stage `9-upload`
  (BLOCKED, DEFAULT OFF), `chief_of_staff_content.py` (`UPLOAD_STAGE`),
  `engine/tools.json` (`upload_video`, `gated: publish`, `handler: null`).
- **Reason:** needs all three — Boss's exact word "upload it" +
  `YOUTUBE_UPLOAD_ENABLED=1` + Boss's own YouTube OAuth credential
  (channel @ToolPilotai69, account sojibprodhan99@gmail.com). Writing the
  script is doable (Doable §B6); running it, and verifying a real upload,
  is not.

### B6. VOICE.md correction (Boss's decision/input) — 03
- **Files:** `03-Content-Creation-Department/VOICE.md` (DRAFT),
  `~/workspace/toolpilot/VOICE.md` (DRAFT), `toolpilot-status.md`.
- **Reason:** Boss must correct/approve the voice guide before any script
  is "final". No LLM can supply Boss's voice preferences, and there is no
  existing Boss YouTube video/transcript to copy from. Blocks script
  finality (stage `2b-script`), not script drafting.

### B7. Track 3 question — ToolPilot vs brand-new channel (Boss's decision) — 03
- **Files:** `03-Content-Creation-Department/toolpilot-status.md`
  ("Open question — Boss's answer pending (since 2026-11-12)"),
  `pipeline.md` ("What is pending with Boss" #4).
- **Reason:** Boss's decision only. The Chief deliberately keeps working
  on ToolPilot until told otherwise; no code or LLM resolves it.

### B8. Nov 16–22 Talvenor weekly plan "ok" (Boss's approval) — 03
- **Files:** `03-Content-Creation-Department/pipeline.md` (Talvenor weekly
  social), `engine/STAFF.md` §7.
- **Reason:** the 5-post plan was delivered 2026-11-15 18:00; Boss's "ok"
  is still pending, and Nov 9–15 also had zero posts for the same reason.
  Publishing needs "post it" per post. Not a code gap.

### B9. Week 1 verdict [FILL AFTER TEST] (Boss's recording) — 03
- **File:** `03-Content-Creation-Department/toolpilot-status.md`
  (long video "Google's Nano Banana 2 Is Free - But Is It Good?", 1,431
  words, ~9.5 min, 5 tests).
- **Reason:** the verdict can only be written after seeing Boss's actual
  OBS recording of the 5 tests. No LLM or mock can fill it honestly.

### B10. Real performance analysis (Boss's numbers; 0 videos published) — 03
- **Files:** `03-Content-Creation-Department/sections/analyze/agents/performance_analyst.py`,
  `engine/STAFF.md` §8, `toolpilot-status.md` (subs 0, hours 0, videos 0).
- **Reason:** analysis needs real platform metrics pasted by Boss
  (or a YouTube Studio / retention CSV export). With zero published
  videos there is nothing to analyze; numbers are never estimated. The
  deterministic parser is doable (Doable §D); real analysis is not.

### B11. Email channel PAUSED — kit outreach cannot send (Boss's DNS fix + restart) — 02
- **Files:** `02-Digital-Product-Department/sections/sales/agents/kit_sales.py`
  (WARNING: "Email channel PAUSED since 2026-11-14"),
  `engine/tools.json` (`draft_email` — draft only).
- **Reason:** sending is paused by Boss's 2026-11-14 order until the SPF /
  DMARC fixes are applied in Boss's DNS panel and he restarts it. Drafts
  are doable (mock); sending is Boss's step, not a code gap. Kit Sales
  drafts also must not quote the $49 price until Boss confirms it.

### B12. Support Drafter real work (needs a first sale) — 02
- **Files:** `02-Digital-Product-Department/sections/support/agents/support_drafter.py`,
  `engine/skills/support-drafter.md` ("Status: BLOCKED (no work right now)").
- **Reason:** sale 0, no buyers, no support questions exist. The worker
  exists and drafts correctly; real work starts after Gate 0 (B1) + first
  sale (B2). Refund policy is also "BOSS INPUT REQUIRED" in the skill —
  Boss must decide it before support drafts can answer refund questions.

### B13. True AI video motion (live LLM / paid key / GPU) — 03
- **File:** `03-Content-Creation-Department/pipeline.md` ("Honest limits").
- **Reason:** genuine AI motion needs either Boss's PC GPU (name unknown,
  B4) or a paid video-generation key ($0 cap). The mock brain cannot
  generate video, and the region block on AI video generation is not
  retryable from this VM.

---

## Summary counts

| Area | Finding |
|---|---|
| 02 roles with skill but no worker | **0** (7/7 have workers; premise stale) |
| 03 roles with skill but no worker | **0** (10/10 have agents; premise stale) |
| Orphaned section agents (code exists, never called) | **10** — 4 in 02, 6 in 03 (Doable §A) |
| Missing deterministic helper scripts (referenced, absent) | **6** — B1–B6 (Doable §B) |
| Tool stubs completable as mock/draft handlers | **2** — 02 `launch_kit`, 03 `publish_post` (Doable §C) |
| Other doable-without-LLM items | **5** — metrics parser (D), edit cut-list tool (E), stills render (F), doc sync G1–G5, PA list research (H) |
| Blocked items | **13** — B1–B13 above |
| Tools that must stay stubs | 02 `sell_kit` (B2), 03 `spend` (B3) |
| Out-of-scope flag | 4 MEMORY.md roles (Ad Campaign, CRM, Expense Tracking, Backup & Recovery) live outside 02/03 — route to the Agency sweep |

**Bottom line:** no staff role in 02/03 lacks a code worker. The remaining
completable work without an LLM API is (1) wiring 10 orphaned section
agents into the two Chiefs, (2) building 6 small deterministic helper
scripts, (3) two mock/draft tool handlers, plus doc sync and the metrics
parser. Everything else is genuinely blocked on Boss's Gate 0 test, Boss's
footage/approvals/decisions, or a real first sale / first published video.
