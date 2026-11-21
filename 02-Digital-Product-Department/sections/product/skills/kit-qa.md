# Skill: Kit QA (NEW)

**Role:** Write a QA checklist DRAFT for the Vet No-Show Recovery Kit's 6 parts — whether any part has been built, and if so, what must be checked.
**Agent:** `sections/product/agents/kit_qa.py` — `KitQAAgent` (task kind `kit_qa`, section `product`)
**Status: NOTHING TO QA YET** — none of the kit's 6 parts has been built (0/6). The agent returns: "NOT BUILT — nothing to QA yet" + a QA checklist DRAFT for each part.

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (launch price **$39** for the first 30 buyers). Format: Google Sheets + Google Docs + copy-paste script.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets. Not a corporate chain, not a solo mobile vet.
- **The kit's 6 parts (from kit-outline.md):** (1) Reminder Cadence Pack — T-72h / T-24h / T-2h SMS + email + call script; (2) Same-Day Rebooking Scripts — phone + in-person; (3) Waitlist-Fill SOP — one page; (4) No-Show Log + $ Tracker — Sheets, with formulas; (5) Deposit / No-Show Policy Template — with attorney-review note; (6) Front-Desk Quick Card — 5 lines, one page.

## Inputs

- `02-Digital-Product-Department/kit-outline.md` — blueprint (the only source, read-only); the 6 parts are described here.
- Gate 1 check: whether the cadence + script match AAHA/PetDesk guidance (after build).
- Gate 0 status: `gate0-status.md` — now NOT PASSED, so there is nothing to QA.

## Step-by-step method (checklist DRAFT — to be used after build)

### QA checks for each part
1. **Reminder Cadence Pack** — whether all three touches T-72h / T-24h / T-2h are present; whether [NAME] / [PET] / [TIME] fields exist; Gate 1: whether the cadence + script match AAHA/PetDesk guidance.
2. **Same-Day Rebooking Scripts** — whether both the phone + in-person scripts are in plain US English; whether filling the slot the same day is covered.
3. **Waitlist-Fill SOP** — whether it is one page; whether it says who to call first + in what order + the exact call script.
4. **No-Show Log + $ Tracker** — whether the formulas auto-total (test with sample numbers); whether it shows all three: the month's misses / estimated $ loss / recovery rate.
5. **Deposit / No-Show Policy Template** — whether "have your own attorney review before using" is written; whether it is not presented as legal advice.
6. **Front-Desk Quick Card** — whether it is 5 lines; whether it is one page; whether it is fit to keep at the desk.

### Global checks (all parts)
- Whether "Talvenor" is spelled correctly everywhere.
- Whether there is any invented client / testimonial / statistic.
- Whether there is any claim to replace a PIMS — the kit works alongside a PIMS (76.5% of practices already use a PIMS — AVMA 2025).
- Whether there is any claim of a verified $49 sale.
- Whether there is any plan to email a clinic twice.

## Output format

- At the top: "NOT BUILT — nothing to QA yet" (now).
- Then a per-part checklist DRAFT: each part — status NOT BUILT + checks.
- At the end, the verdict: no part has passed QA — nothing has been built at all. Checklist DRAFT only.
- The output will state the true status — never an invented "PASS".

## Tools used

- Read-only file read: `kit-outline.md` (description of the 6 parts).
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the checklist DRAFT, not a live call.
- ApprovalGateway for gated work (PENDING record).
- No live tool, network, or file write.

## Gate

- Boss's `ok` is needed to use the QA result.
- Real QA happens only after Gate 0 passes + build; now only the checklist DRAFT.

## Honest limits

- **0/6 built** — there is nothing to QA. This skill's real test has not happened yet.
- Gate 1 (cadence check against AAHA/PetDesk) has not happened yet.
- $49 price unproven — no verified sale.

## Never does this

- Claims any part passed (nothing has been built at all).
- Builds the kit; writes any file; invents a client/testimonial/statistic.
- Presents the policy template as legal advice.

## Worked example (with real repo facts)

- **Task:** `{"type": "kit_qa", "title": "QA the 6 kit parts"}` → `KitQAAgent.run()`.
- **Agent does:** reads `kit-outline.md` and takes the 6 parts' names; since no part is built, writes each one's status as NOT BUILT.
- **Result:** status `draft-ready`; the output has "NOT BUILT — nothing to QA yet" + a checklist DRAFT for the 6 parts (e.g. the Reminder Cadence Pack's Gate 1 check: match with AAHA/PetDesk guidance; the No-Show Log + $ Tracker's formula sample test). No part passed — the verdict is written truthfully.
