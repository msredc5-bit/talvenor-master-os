# Skill: Skill-Finder (the Main CEO Bot's skill for finding skills)

**Role:** When a new capability is needed for a task — one no agent's skill has —
find that skill. Searching is allowed; installing/adapting is not allowed without
Boss's "ok".

**Source (adapted, not copied):** cubicyyy/auto-research-skills —
`skill-finder` (MIT) + vercel-labs/skills — `find-skills` (MIT).
The method is theirs; the mechanism is ours (see below).

## Inputs

- Need: `{keywords, agent, why}` — for which agent, for what work the skill is needed
- Local registry: all the repo's `*/skills/*.md` (scanned yourself)
- Remote directories: skills.sh + the table below (names + licenses only, not code)

## Outputs

- If there is a local match: the skill's name + path (usable immediately)
- If there is no local match: a **DRAFT proposal** (`store/skill-proposals.json`) —
  candidate repo + skill + license + fit note + a question for Boss.
  A proposal does not mean install.

## Procedure — search steps (the order cannot be changed)

### 1. Local first — is it in your own repo?

Run `00-CEO-Core/skill_finder.py` — `find_skill_local(query)`.
If a keyword matches in the name + description, that is the answer. While a local skill exists,
do not search outside.

### 2. Leaderboard first — look at skills.sh

`find-skills`'s rule: the skills.sh leaderboard first — the most installed,
battle-tested skills sit on top. Then keyword search.

### 3. Verify quality — verify before recommending

Three signals, all three are needed:

| Signal | Preferred | Warning |
|---|---|---|
| Install count | 1,000+ | Below 100 |
| Source reputation | vercel-labs, anthropics, microsoft, openclaw | Unknown author |
| GitHub stars + license | look at stars, license must be MIT/Apache-2.0 | without a license it cannot be proposed |

If any one signal does not match, the candidate is rejected — it is not shown to Boss.

### 4. Shortlist — the best 3, show them to Boss

`skill-finder`'s rule: top 3–5, name + stars + one line on what it does.
**No install/adapt without confirm.** A big repo (hundreds of skills) cannot be brought
in whole — one skill must be chosen.

### 5. Vendor — keep it in the research dir, not in the repo

Once confirmed, the upstream repo may be cloned into `~/workspace/skill-research-2026-11-21/`
(research only). Upstream files never go
into the Master OS repo.

### 6. Adapt — not a copy, write it in your own words for Talvenor

- Talvenor facts only: Vapi/Sophia, Gmail hello@ (outreach, PAUSED),
  $0 cap, Approval Gate + gate words (ok/go/send), no dental/medical,
  no invented clients/prices, brain still mock.
- Paid execution excluded: no live ad spend, live CRM write, live API call —
  DRAFT plan + procedure.
- Windows: no symlink — the adapted file is copied.
- Source + license must be written in every adapted skill file.

## Remote sources (where to search)

| Source | License | What you get |
|---|---|---|
| skills.sh (directory) | per-skill | leaderboard + search |
| anthropics/skills | Apache-2.0 | docs/design/build skills |
| anthropics/knowledge-work-plugins | Apache-2.0 | sales/finance/marketing role skills |
| vercel-labs/skills | MIT | find-skills + web skills |
| adkit/ads-skills | MIT | Meta/Google ads strategy |
| superamped/ai-marketing-skills | MIT | ad analyzer, angles, creative |
| makash/godmode | MIT | backup, 126 engineering skills |
| poorangryman/ai-agent-pro-kit | MIT | agent-memory |
| frankxai/skills | MIT | tool-allowlist |
| braydos-h/BreachPilot | Apache-2.0 | tool-invocation security |
| openclaw/skills | MIT | expense-tracker, memory |
| cubicyyy/auto-research-skills | MIT | skill-finder (exact name) |

## Tools

- `00-CEO-Core/skill_finder.py` — local search + proposal draft + doctor
- `main_ceo_bot.py` — when a task of type `find_skill` arrives, it calls this skill
- `store/skill-proposals.json` — DRAFT proposals (not installs)

## Gate — stops here

- Searching is allowed; writing / installing a skill file is not — Boss's "ok" is needed.
- No skill without a license (not MIT/Apache-2.0) can be proposed.
- Paid skill/account, API key, live call — never.
- While a local skill exists, do not search outside.

## Limits

- Brain mock ($0) — this skill does not do online search itself; a human
  (Mira) searches, and results are verified by this procedure.
- The proposal stays DRAFT until Boss says "ok".
