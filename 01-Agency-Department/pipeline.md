# Agency Pipeline — the real steps (Phase 1)

Talvenor AI Receptionist Agency — selling AI receptionists to US home-service businesses (plumbing,
HVAC, roofing, garage door, septic, tree, foundation, restoration,
pest, vet). MAIN business.

> **Every status in this file is true — nothing is written except verified numbers.**

## The steps

| # | Step | Who does it | Gate | True status (2026-11-16) |
|---|---|---|---|---|
| 1 | **Finding leads** — US home-service SMB, looking for missed-call signals | ProspectResearcher (ACQ) | None (research only) | Lead universe: **537 unique leads** (Tier 1/2 pool) — `~/workspace/talvenor/leads-organized/` |
| 2 | **Writing drafts** — cold email / IG DM, short, plain US English, 1 CTA | OutreachDrafter (ACQ) | `send` | The draft is the final word — not sending |
| 3 | **Boss's approval** — ok / send after seeing the draft | Boss | `ok` / `send` | Every send needs Boss's tap |
| 4 | **Sending** — email / IG DM | Boss himself (not this system) | `send` | **PAUSED — since 2026-11-14.** DNS fix (SPF + DMARC) is still in Boss's hands; nothing goes until he says "check koro" |
| 5 | **Follow-up** — writing again if no reply comes | OutreachDrafter (ACQ) | `send` | **Nobody's follow-up is due yet.** Rule: no follow-up in a state until 100 first mails in that state. FL's ceiling is 98 — so no follow-up is due anywhere. 20 ready PA follow-up drafts are PARKED |
| 6 | **Reply triage** — sorting interest / decline / question | ReplyHandler (ACQ) + InboxTriager (OPS) | `send` (on an interest reply) | **First mail 162, 0 replies seen in Gmail.** hello@ replies go to Zoho — Elora cannot see them; Boss must check Zoho |
| 7 | **Booking a call** — 15-min demo call | SchedulerAssistant (OPS) | None | Booking link: https://calendar.app.google/WLoxBfnLGTdjK3LB8 (New York Time) |
| 8 | **Building the receptionist** — Vapi Sophia | RetellBuilder = DRAFT plan only (DEL) | `ok` | Live stack **Vapi / Sophia** — phone +1 (947) 223-0244. Boss will not pay for Retell, so RetellBuilder only writes the plan, never builds live |
| 9 | **QA + launch** — checklist, onboarding | QAEngineer + OnboardingAgent (DEL) | `ok` | Paying client **0** — no client has launched yet |
| 10 | **Marketing** — 5 weekly posts, video, caption | ContentPlanner / VideoProducer / CaptionWriter / PublishPrep / ObjectionSimulator (MKT) | `ok` / `post it` | Nov 16–22 plan awaits Boss's "ok". Publish only on Boss's "post it" |

## Verified numbers (2026-11-16, read from files)

- Day 1 draft file: **25** drafts; Day 2: **25**; Day 3: **25** — sent
- Day 4 draft file: **25** READY, not sent
- Day 5 draft file: **25** READY, not sent
- Day 6 draft file: **25** READY, not sent
- First mails total: **162** (locked record — Day 1–3 + earlier batch)
- Paying client: **0**
- Demo video (60-second): https://facebook.com/reel/2947321012290705/

## What this pipeline never does

- It does not target dental / medical / patient-health businesses (hard DQ)
- It does not quote a price — except the variant Boss confirms
- It does not use invented clients / testimonials / statistics
- It does not try to send while email is PAUSED — the draft is the final word
- n8n auto-send is not LIVE (READY, Boss's import + test pending) — the two systems cannot run together

## Files

- Chief: `chief_of_staff_agency.py` (REAL, Phase 1)
- Worker: `sub_agents/README.md` (routing for 15 workers)
- Workflow: `workflows/README.md` (the true status of the email pause)
- Task log: `../store/tasks.json` · Approval: `../store/approvals.json`
