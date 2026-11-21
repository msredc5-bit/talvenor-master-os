# Agency Engine — Talvenor AI Receptionist (Phase 5)

**Business:** Talvenor AI Receptionist Agency — an AI receptionist for US home-service businesses
(plumbing, HVAC, roofing, garage door, septic, tree, foundation,
restoration, pest, vet). Boss's first business, MAIN.
Dental / medical / patient-health — never a target.

## At a glance

| Item | Count |
|---|---|
| Staff (role) | **15** — vendored boss-ceo workers (Phase 6), inside |
| Tools | **8** — mock 5, gated (stub) 3 |
| Skills | **15** — one per role |
| Chief | `../chief_of_staff_agency.py` (REAL, Phase 1) — routing is the source of truth |

## Staff (15)

ACQ: Prospect Researcher, Outreach Drafter, Reply Triager, Negotiation Coach ·
DEL: Receptionist Builder (DRAFT plan only — live stack Vapi/Sophia),
QA Engineer, Onboarding Agent ·
MKT: Content Planner, Video Producer, Caption Writer, Publish Prep,
Objection Simulator ·
OPS: Inbox Triager, Report Compiler, Scheduler.

Details: `STAFF.md` — worker class, division, job, input per role,
output, gate word.

## Tools (8)

- **Mock (5)** — builds DRAFTs, sends/changes nothing:
  `draft_email`, `research_notes`, `draft_caption`, `draft_script`, `status_read`
- **Gated / stub (3)** — never executes, handler null:
  `send_email` (gated: send), `publish_post` (gated: publish),
  `spend` (gated: spend, cap $0)
- Registry: `tools.json` · Wrapper: `tool_calling.py` — shared core
  uses (`00-CEO-Core/tool_calling.py`)'s `ToolRegistry.load_from_json` +
  `call_tool`; it executes nothing itself.

**Intent (2026-11-21, Boss's one-gateway decision):** `tools.json`
deliberately covers only these 8 generic tools — none of the 43 Phase-3 specialists
or 6 section agents has a tool entry, by design. Specialists are reachable
not through the ToolRegistry/MCP path, but through Chief/manager routing
(`chief_of_staff_agency.py` ROUTING / SECTION_ROUTING /
DEPARTMENT_ROUTING). Workers get skill + the central
Tool Gateway — no per-agent MCP server. So do not take the 8-tool registry
as a gap; registering every worker as a tool is
not needed.

## Skills (15)

`skills/` — one `.md` per role: role, input, step-by-step method
(from worker + agency-os SOP), output format, gate, honest limits.
Where Boss's input is truly needed, "BOSS INPUT REQUIRED" is written —
never invented facts.

## Status: REAL / MOCK / BLOCKED

| Part | Status |
|---|---|
| Chief routing (15 workers) | **REAL** — calls the vendored engine |
| Worker brain | **MOCK** — MockLLMProvider, $0; all output is DRAFT |
| Draft writing (email/DM/caption/script/plan) | **MOCK** — draft-ready |
| Receptionist build | **DRAFT plan only** — RetellBuilder writes the plan; the live build on Vapi/Sophia is Boss's job |
| Email sending | **BLOCKED — PAUSED** |
| Publish / upload | **BLOCKED — gate** (`post it` / `upload it`) |
| Spend | **BLOCKED — cap $0** |

## What is blocked, and whose hands it is in

1. **Email PAUSED (since 2026-11-14)** — SPF has no Gmail include, DMARC
   is missing. Fix in Boss's DNS panel: add `include:_spf.google.com` to SPF,
   place the `_dmarc` TXT record (`p=none`). Then when Boss says "check koro",
   it will be checked again. Until then the draft is the final word — the Day 4/5/6 25+25+25 drafts are
   READY, not sent.
2. **Send / publish / spend / delete** — nothing happens without Boss's exact gate word
   (`send` / `post it` / `ok` / `upload it` / `go`);
   there is no auto-approve path. Boss himself does the sending/publishing.
3. **Paying client 0, first mail 162** — 0 replies seen in Gmail;
   hello@ replies go to Zoho; Boss must check Zoho.
4. **Follow-up** — none due anywhere (100-mail rule; FL ceiling 98).
   20 ready PA follow-up drafts are PARKED.
5. **Shared core** — `00-CEO-Core/tool_calling.py` is being built in a parallel build;
   this engine's wrapper cannot run without it
   (the file did not exist at build time — no live run has been verified).

## Rules (locked)

- Brand Talvenor only · no invented client/testimonial/statistic/price ·
  $0 spend cap · stdlib only, no network, no pip ·
  no send/publish/spend/delete · Booking:
  https://calendar.app.google/WLoxBfnLGTdjK3LB8 · Phone +1 (947) 223-0244.

## Files

- `STAFF.md` · `tools.json` · `tool_calling.py` · `README.md` (this file)
- `skills/` — 15 skill `.md` files
- Source (reference only, not copied): `../chief_of_staff_agency.py`,
  `../pipeline.md`, `01-Agency-Department/engine/workers/src/workers/` (vendored; upstream `~/workspace/boss-ceo/src/workers/`),
  `~/workspace/agency-os/` (20 skill + SOP).
