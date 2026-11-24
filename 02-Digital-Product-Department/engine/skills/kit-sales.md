---
name: kit-sales
description: "Write DRAFTs of Vet Kit outreach emails for verified PA clinics — DRAFTs only, never sent."
---

# Skill: Kit Sales (NEW)

**Role:** Write DRAFTs of Vet Kit outreach emails for verified PA clinics — DRAFTs only, never sent.
**Agent:** `sections/sales/agents/kit_sales.py` — `KitSalesAgent` (task kind `kit_sales`, section `sales`)
**Status: DRAFTS ONLY** — Gate 0 NOT PASSED, email channel PAUSED (since 2026-11-14). Every output carries a prominent warning: "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go".

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (launch price **$39** for the first 30 buyers). Format: Google Sheets + Google Docs + copy-paste script.
- **For whom:** Independent companion-animal vet clinic, 1–5 vets. Not a corporate chain, not a solo mobile vet.
- **Pain (VERIFIED):** no-show rate **~11%** (AAHA) × average vet visit **~$200** (AVMA 2025) ≈ **~$50k–$150k/yr** at risk for a typical clinic (labeled estimate). **34,296** vet practices in the US (Census 2023).
- **Contact (real facts):** booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 (Talvenor Demo, 15 min, New York Time); phone +1 (947) 223-0244; main email contact@talvenorai.agency.
- **Price flag:** $49 does not come from any verified sale — an inference. $49 cannot be quoted to a prospect unless Boss confirms.

## Inputs

- `02-Digital-Product-Department/pa-vet-list/pa-vet-clinics.csv` (39 verified rows, read-only) — drafts only for clinics on this list.
- `02-Digital-Product-Department/kit-outline.md` — the kit's 6 parts + pain arithmetic (the basis of the draft).
- Task payload `clinic_name` (optional) — an addressed draft only if it matches the CSV; otherwise a generic template.
- Gate 0 status: `gate0-status.md` — now NOT PASSED.

## Step-by-step method

1. **Verify the clinic:** if the payload has a `clinic_name`, search the CSV. If it matches, look at the public email — if the email is "Not publicly listed", no addressed email draft can be written (contact details cannot be invented).
2. **If no clinic is given:** use the CSV's first emailable row (one with a public email) — now that is Indy Veterinary Care, Philadelphia (info@indyvetcare.com).
3. **Write the draft (plain US English):** subject + body — pain (AAHA 11% × AVMA ~$200), the kit's 6 parts, CTA (booking link + phone). Price is a placeholder: "[Price — Boss confirms before sending. Do NOT quote a price to a prospect without Boss confirming.]" — $49 is not written.
4. **Attach the warning:** a prominent "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go" + "Email channel PAUSED" at the top of the output.
5. **No clinic can be emailed twice** (at launch time) — written in the note.

## Output format

- Warning + addressed draft (To: verified clinic, city, public email, source_url) or generic template (with placeholders).
- Status: `draft-ready` (for the draft); `blocked-gate0` if `mark_sold` is requested.
- The top of the draft will say: DRAFT ONLY — not sent.

## Tools used

- Read-only file read: `pa-vet-list/pa-vet-clinics.csv` (verified clinic + public email + source_url).
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the draft, not a live call.
- ApprovalGateway for gated work (PENDING record) — if `send` is requested the worker is not run, it is held at PENDING.
- No live tool, network, or file write. Sending mail is not this skill's job.

## Gate

- Boss's `send` is needed to send — nothing is sent without the exact word.
- The email channel is now PAUSED — the SPF/DMARC DNS fix is still in Boss's hands (since 2026-11-14).

## Honest limits

- **Gate 0 NOT PASSED** — the kit has not been built (0/6), sale 0. Drafts are for use after launch.
- **PAUSED email** — drafts can be written, nothing can be sent.
- PA list 39/100 — of the 39, 8 have a public email; the rest cannot get an addressed email draft.
- Talvenor has no relationship/agreement with any clinic — this is only a list of public information.
- $49 price unproven — no verified sale.

## Never does this

- Sends mail; marks anything as a sale.
- Quotes $49 to a prospect unless Boss confirms.
- Invents contact details; writes a draft for anyone outside the CSV; writes any file.
- Invents any client/testimonial/statistic.

## Worked example (with real repo facts)

- **Task:** `{"type": "kit_sales", "title": "Outreach draft", "payload": {"clinic_name": "Indy Veterinary Care"}}` → `KitSalesAgent.run()`.
- **Agent does:** searches the CSV — Indy Veterinary Care, Philadelphia, public email info@indyvetcare.com, phone (215) 923-2300, source https://indyvetcare.com/ — verified (README spot-check).
- **Result:** status `draft-ready`; at the top of the output, the "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go" warning; then an addressed email DRAFT (subject "Missed appointments — a simple fix for Indy Veterinary Care?", pain AAHA 11% × AVMA ~$200, the 6 parts, CTA booking link https://calendar.app.google/WLoxBfnLGTdjK3LB8 + phone +1 (947) 223-0244, price as a placeholder — $49 is not written). Not sent.
