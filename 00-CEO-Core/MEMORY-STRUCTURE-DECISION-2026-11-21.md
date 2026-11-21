# Memory System — Structure Decision (2026-11-21)

> **Boss's rule (voice call 2026-11-21 ~10:10 Dhaka):** the drawer layout was
> Mira's arrangement, from Boss's analogy. The memory's structure must be decided
> on **merit**, not from analogy, and then the memory system must be arranged in
> that structure and made **live** (wired + GitHub push). This file is that decision.

## The decision (in one line)

**One central store file (`store/memory.json`) — with separate boxes inside
(shared + each agent's own box).** In other words, the "drawer" shape stays,
but now it is not an analogy — it is the structure decided on the merits below.

## Why this structure — judged on merit

There were three options. Each was checked against Nod and bot-hq's RE
(with sources below).

### Option A — One central store + boxes inside (this is the one taken)

- **One owner → one memory doc.** Nod's lesson
  (`~/workspace/nod-reverse/reverse-engineering.md` §4, `memory.ts`):
  one owner's memory is one private JSON doc (256 KiB cap, 5 areas).
  Boss is one person — his words will stay in one place, never duplicated. If duplicated,
  one day the old/wrong copy becomes the "truth".
- **One repo, one PC (8 GB) → not 79 files.** bot-hq's per-bot
  files (`~/workspace/bot-hq-reverse/reverse-engineering.md` §5,
  `engine-memory.ts`) are for their separate Hermes homes — each bot
  really is a separate machine slice. Our agents are not separate homes; they are
  modules of one repo. 79 memory files for 79 agents means scattered truth,
  no single source — and Boss's shared words would have to be copied into every
  file, otherwise cross-file searching would be needed (which is really Option A
  built again, badly).
- **Box = per-agent isolation without scattering files.** In the shared compartment,
  only Boss's words (everyone reads, nobody can block them); each agent's
  work notes only in its own box (another box cannot read them — enforced
  in code). Boss's condition (2026-11-21 ~09:45) — that per-agent notes must not
  mix — is met this way, without adding files.
- **One file = one atomic save, one cap, one backup/export.**
  256 KiB cap, one `store/MEMORY.md` export — Boss can see everything in one file.

### Option B — Per-agent file (bot-hq style) — not taken

Each agent's own `MEMORY.md`/`USER.md`, `§`-separated entries.
The good side: an agent's notes are visible in a separate file, easy to delete.
But in this repo: agents are not separate homes; the shared Boss words cannot run
without duplication or cross-refs; the consistency of 79 files (which is latest?)
would have had to be built separately in code. Even in bot-hq, their `memories` SQLite table
sits legacy/unused — two sources means one of them dies.

### Option C — Hybrid (shared central + notes in per-agent files) — not taken

Owner words central, work notes in per-agent files. Looks nice, but
isolation splits across two mechanisms (code for shared, filesystem for notes),
a note's lifecycle (edit/archive/forget) needs two code paths, and export also
has to merge two sources. In a single-file design, `read_box()`/`list_own()` +
box-wise export give the same view — no merit in exchange for the complexity.

### Option D — Flat doc, no boxes (Nod's original) — not taken

One doc, 5 areas, no per-agent split. Simple, but it does not meet Boss's
condition — a worker's notes and Boss's words mix in one list,
separated only by area/slug. The box code already exists, 17/17 pass — there is
no gain in going back to D.

## What stayed as before (the good things)

- **Quote-verification:** memory learns only from Boss's own messages;
  if the quote is not verbatim in the source message, there is no entry (Nod §4).
- **Memory is context, NOT permission:** something being written in memory
  never approves any work — approval lives only in trust_gate + ApprovalGateway.
- **Isolation:** only Boss's words in shared; work notes only in one's own box;
  read/edit/forget from the wrong box is refused.
- **Visible + editable:** view / change / archive / forget;
  Markdown export (`store/MEMORY.md`).
- **Cap:** 256 KiB doc, entry ≤ 4,000 chars, 5 areas
  (about / preferences / people / routines / lessons), status
  tentative / observed / stated / archived.
- **3 seed entries verbatim, unchanged:** the Mira name, answering in Bengali,
  gate words (`store/memory.json`).

## What was newly added (gaps found in the merit review)

1. **Maintenance — repair (no-model, modelled on Nod's repair):**
   `OwnerMemory.maintenance_repair()` — archives tentative entries older than
   60 days (said once, never repeated); if the same
   (box, area, slug) has a duplicate, it archives the later one.
   No model is needed, no live call. Stated/observed entries
   are never auto-archived (they are confirmed/learned).
2. **Reflect — proposal only, never auto-write:**
   `OwnerMemory.validate_proposals()` — takes a candidate list and returns which
   ones pass quote-verify (ready to learn) and which are rejected — it writes
   nothing. The proposal is written by a future live brain / Mira;
   the server takes only quote-verified notes (Nod: "server keeps a
   note only if a cited owner message contains its quote verbatim").
3. **Compact context view:** `OwnerMemory.context_for(box)` — what attaches in
   CEO/Chief routing: shared entries + the box's own notes, in a small
   form (without source_message).
4. **Forget via the gate (Nod: forgetting wants a trust check):**
   `request_forget_owner_entry()` in the `Main CEO Bot` — creates a
   "delete" confirmation in the ConfirmationStore (gate word "go"); `forget_owner_entry()`
   runs only an approved confirmation via `execute_once()` — nothing is deleted
   without approval, on failure it is UNCERTAIN, never re-run.
5. **Reload guard (multi-instance safety):** every write
   (learn/note/edit/forget/repair) first reads fresh from disk — even if the CEO and
   the Chief hold separate instances of the same file, one person's save does not
   delete the other's note.

## Live wiring (what "live" means here)

- **Read path — always:** `Main CEO Bot.route_task()` reads memory on every route
  (`context_for("main_ceo_bot")`) and attaches it to the result as `memory`
  — the routing decision is made seeing Boss's words (name, language, gate
  words). The Agency Chief also reads `context_for("chief_of_staff_agency")` the same way
  in `handle_task()`.
- **Write path — owner words:** `Main CEO Bot.record_owner_message()` —
  teaches Boss's new words after quote-verifying them (learn). Nobody can teach
  except with Boss's words. This write path is called from the entry point of the
  live flow (when the Mira/chat layer gets Boss's words) — nothing is auto-learned
  from task text (task text is not Boss's verbatim message).
- **Write path — work notes:** `note_work()` runs on an explicit call
  (when a lesson is learned) — it is not auto-called from route/handle.
  Routing logs live in `store/tasks.json`; memory is for Boss's words +
  lessons. In the first design, a per-task routing note was written —
  a few check runs accumulated 573 notes in a test and broke `check_phase6`'s repo
  grep, so it was removed (2026-11-21 ~10:24, the lesson from that mistake:
  memory is not a log).
- **Write path — forgetting:** only with the gate's approval (no. 4 above).
- The brain is still **mock**, $0, with no key / live call. Memory is local
  file read/write — no API key needed.

## The files

- `00-CEO-Core/owner_memory.py` — memory code (maintenance + context
  + proposal validation + reload guard added; the old API unchanged).
  Reload guard: the CEO and Chief hold separate instances of the same file — so
  before every write, it reads fresh from disk; otherwise the last save would
  delete the earlier note.
- `00-CEO-Core/check_drawer_memory.py` — check script (the old 17 +
  new live-wiring/maintenance checks; all pass).
- `00-CEO-Core/main_ceo_bot.py` — CEO wiring (read + write + gated
  forget).
- `01-Agency-Department/chief_of_staff_agency.py` — Chief wiring
  (read only — context attached on every handle).
- `store/memory.json` — 3 seed entries, verbatim (this change did not alter
  the file — it is only being pushed).
- `store/MEMORY.md` — export, regenerated from the seeds.

## What is still left (needs Boss's decision)

- Live brain proof (Boss's PC network) — before the Phase 4 team factory.
  Even though memory is live, the brain is still mock.
- The Reflect proposer (candidates coming from the live brain / Mira) — now
  there is only a validator, not a proposer.
