# Sales Section — Kit Outreach DRAFTs

**Purpose:** Write DRAFTs of Vet Kit outreach emails for verified PA clinics — DRAFTs only, never sent.

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Kit Sales | `agents/kit_sales.py` (`KitSalesAgent`, task `kit_sales`) | `skills/kit-sales.md` | `send` | **NEW** role (Phase 7) |

## How work flows

1. Main CEO Bot → Products Chief → `kit_sales` (the Chief's `SECTION_ROUTING` branch, Phase 7, new) → `KitSalesAgent`.
2. The agent takes a verified clinic from `pa-vet-clinics.csv` (read-only): if the payload has a `clinic_name`, it checks the CSV for a match; if not, it uses the first emailable row (one with a public email) — now Indy Veterinary Care, Philadelphia.
3. Writing the draft (plain US English): pain (AAHA ~11% × AVMA ~$200), the kit's 6 parts, CTA (booking link + phone). The price is a placeholder — $49 is not written unless Boss confirms.
4. A prominent warning at the top of every output: "DRAFT ONLY — Gate 0 NOT passed, do not send until Boss says go".
5. If a gated `send` is requested, the agent is not run — a PENDING request is written to the ApprovalGateway.

## Gates

- Boss's `send` is needed to send — nothing is sent without the exact word.
- The email channel is now **PAUSED** (since 2026-11-14 — the SPF/DMARC DNS fix is still in Boss's hands).

## Honest limits

- **Gate 0 NOT PASSED** — the kit has not been built (0/6), sale 0. Drafts are for use after launch.
- **PA list 39/100** — of the 39, 8 have a public email; if there is no public email ("Not publicly listed"), no addressed email draft can be written.
- No clinic can be emailed twice (at launch time).
- No agent sends mail, marks a sale, invents contact details, writes a file, or touches the network.
