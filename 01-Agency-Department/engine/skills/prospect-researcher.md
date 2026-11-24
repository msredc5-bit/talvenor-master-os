---
name: prospect-researcher
description: "Prospect Researcher · Worker: ProspectResearcher (boss-ceo, ACQ)"
---

# Skill: Prospect Researcher — Agency (Phase 5)

**Role:** Prospect Researcher · **Worker:** `ProspectResearcher` (boss-ceo, ACQ)
· **Task type:** `prospect_research` · **Gate:** None (research only, nothing is sent)
· **SOP basis:** agency-os SKILL 02-lead-generation + 03-lead-qualification +
SOP `prospect-qualification-talvenor.md` (v1, 2026-11-03)

**Business:** Talvenor AI Receptionist — US home-service SMB: plumbing, HVAC,
roofing, garage door, septic, tree, foundation/waterproofing, restoration,
pest, vet. Dental / medical / patient-health — DQ at once, never scored.

## Input

- `niche` (default: `plumbing`), `region` (default: `Texas`).
- Or a lead dataset (business_name, city, state, phone, website —
  low-confidence flag if fewer than 4 fields are present).

## Method (step-by-step)

1. Decide the target niche + region. If it is a legal lead, park it (gated until the 4th client).
2. Look up the business — website, Google Business profile, social bio. If any
   field is not found, write `NOT_FOUND` — never invent a phone/email/address.
3. Tick the 11 need signals on each lead's website (with a proof URL):
   (1) phone-only booking, (2) no online scheduler, (3) no live chat,
   (4) contact-form only, (5) 24/7/emergency claims but no evidence of an answering system,
   (6) owner is out in the field himself, (7) urgent service, (8) many services /
   large area, (9) team page has only technicians, (10) no booking in the social bio
   link, (11) Google profile call-only.
4. Count signals: 3+ = STRONG, 2 = MEDIUM, 0–1 = WEAK. Score on a 100-point rubric —
   0 points without proof, never an average or benefit of the doubt.
5. Tier rules: STRONG + 80–100 = Tier 1; STRONG + 60–79 = Tier 2;
   MEDIUM = Tier 2 at most; WEAK = Tier 4 (do not contact). One review
   never makes Tier 1 alone — website signals are also needed.
6. Disqualifier check (100% row): closed business / phone disconnected / already
   an AI receptionist client / franchise central call center / fewer than 3
   reviews + no website / do-not-contact list / dental-medical. On a hit, DQ,
   score 0, with the reason written.
7. Write a one-line problem for each lead: `Possible problem: [problem] —
   Evidence: [what was seen on the website]`. This is a hypothesis — it cannot be told to the prospect
   as a verified fact.
8. Write in the CRM (stage = `not_contacted`): score, tier, signal count, evidence
   URL, best channel, reason line.

## Output format

```text
Prospect: [business name] — [city, state]
Tier: [1/2/3/4/DQ] | Score: [0-100] | Signals: [n/11 STRONG/MEDIUM/WEAK]
Possible problem: [...] — Evidence: [URL]
Best channel: [email / IG DM / form (Boss himself) / park]
```

## Gate

No gate — research itself is safe. But if any outreach is written from this research,
that is the Outreach Drafter's job, gate `send`.

## Honest limits

- Mock brain ($0) — output DRAFT, not to be used without verification.
- During qualification, nobody can be called/messaged/formed — observation only.
- If the website is down, Tier 1 is forbidden; write "site down at time of scoring".
- A reviewer's name must never be copied; review text + date only.
- If the tier is low, tell Boss honestly — the tier cannot be raised to fill a quota.
