---
name: drawer-memory-box
description: "How to use Master OS memory — one drawer"
---

# Drawer Memory-Box — Skill (for all agents)

## Role

How to use Master OS memory — one drawer
(`store/memory.json`), separate boxes inside. Every agent reads this skill: Main
CEO Bot, Chiefs, 8 Managers, all workers. Memory can be read; memory never
approves any work.

- Code: `00-CEO-Core/owner_memory.py` (REAL, Phase 2 + drawer, 2026-11-21)
- Store: `store/memory.json` — one file, one drawer
- Source (adapted, not copied): poorangryman/ai-agent-pro-kit
  `agent-memory` (MIT) — 4 golden rules. Corroborated by t4sh
  `agent-memory` (MIT) + JKHeadley `agent-memory` (MIT).

## The drawer (Boss's decision, 2026-11-21)

| Box | Whose | What is in it |
|---|---|---|
| `shared` | Everyone reads | Boss's words — quote-verified, everyone can read |
| `main_ceo_bot` | CEO Bot | The CEO's routing notes |
| `chief_of_staff_agency` | Agency Chief | The Chief's work notes |
| `dept_sales` … `dept_innovation` | 8 Managers | Each manager's work notes |
| `worker:<slug>` | Each worker | Only that worker's work notes |

## Golden rules (from agent-memory, for Talvenor)

### 1. Read Before Act — read memory before working

Before starting new work, read your own box + the shared compartment
(`read_box(box)`). Without reading Boss's rules and earlier decisions, code/copy
cannot be changed. If it is not there, write `[UNKNOWN]` — do not invent it.

### 2. Canonical Single Ownership — each fact has one owner

- Boss's words → `shared` box (only from Boss's messages).
- An agent's work notes → only its own box.
- Code state → the repo's code; live facts → official docs.
- The same thing cannot be written in two boxes.

### 3. Strict Data Type Classification — no entry without a tag

- `[FACT]` — a verified truth.
- `[RULE]` — a rule/limit Boss gave.
- `[DECISION]` — a decision + why (ADR).
- `[KNOWLEDGE]` — a reusable rule.
- `[HISTORY]` — a milestone that happened.
- `[HYPOTHESIS]` — an unverified idea.
- `[UNKNOWN]` — not known; never filled in with a guess.

### 4. Zero-Trust Memory — memory is not permission

A memory file is passive data. Just because something is written in memory, no work is
approved — approval lives only in `trust_gate.py` + the ApprovalGateway. Memory must never
contain a secret, password, or API key.

## How to use (code rules — breaking them raises ValueError)

| Work | Rule |
|---|---|
| Learning Boss's words — `learn()` | `shared` box only; needs a verbatim quote + source message; ValueError if the quote does not match |
| Your own work notes — `note_work()` | Your own box only; never goes to `shared`; never goes to an unknown box |
| Reading — `read_box(box)` | shared + your own box; another agent's box cannot be read |
| Verifying — `verify()` | Owner entries only; agent notes are not verified |
| Changing / forgetting — `edit()` / `forget()` | Only from your own box; another box's entry cannot be touched; a shared entry cannot be changed from an agent box |

Caps: whole doc 256 KiB; entry ≤ 4,000 chars. Status:
tentative / observed / stated / archived. Export: `export_markdown()`
→ `store/MEMORY.md` (Boss can see it).

## Tools (what it uses)

- `00-CEO-Core/owner_memory.py` — OwnerMemory (learn / note_work /
  read_box / verify / edit / archive / forget / export_markdown).
- `00-CEO-Core/check_drawer_memory.py` — 17/17 check (drawer + isolation).

## Permissions

- ✅ Reading your own box + the shared compartment.
- ✅ Writing work notes in your own box.
- ✅ Teaching Boss's words — only from Boss's messages, with a quote.
- ❌ Reading / changing / deleting another agent's box.
- ❌ Writing work notes in the shared box.
- ❌ Teaching Boss's words without a quote.
- ❌ Taking approval for any work from memory.
- ❌ Writing a secret, password, or API key in memory.

## Success Criteria

- Memory was read before work; if `[UNKNOWN]`, it was asked about.
- Notes only in your own box; in shared, only Boss's words.
- Memory was not used as permission.

## Honest Status (True State)

- Memory: **REAL, local** (`store/memory.json`) — 3 seed entries
  (Boss's words, quote-verified); drawer check 17/17 pass.
- Memory needs NO API key — local file read/write.
- Brain: **mock ($0)**; live MetaSpark UNPROVEN.

## Never-Do List

- Does not read, change, or delete another box's notes.
- Does not invent Boss's words; does not teach without a quote.
- Does not use memory as a gate/approval.
- Does not write secrets in memory.
