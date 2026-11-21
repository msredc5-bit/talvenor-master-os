# Skill: Support Drafter

**Role:** Write DRAFT replies to kit buyers' questions — DRAFT only, never sent.
**Agent:** `sections/support/agents/support_drafter.py` — `SupportDrafterAgent` (task kind `support_draft`, section `support`)
**Status: BLOCKED (no work now)** — sale 0, no buyers, no support questions either. This role's work starts only after Gate 0 passes + the first sale. Now the output is all templates.

## Product (locked facts)

- **Product:** Vet No-Show Recovery Kit, **$49 one-time** (launch price **$39** for the first 30 buyers). Format: Google Sheets + Google Docs + copy-paste script. Delivery: Lemon Squeezy download link (Gumroad backup).
- **The kit's 6 parts:** Reminder Cadence Pack (T-72h/T-24h/T-2h), Same-Day Rebooking Scripts, Waitlist-Fill SOP, No-Show Log + $ Tracker (Sheets), Deposit/No-Show Policy Template, Front-Desk Quick Card.
- **Support load (ASSUMPTION):** ~10 min/buyer — automatic delivery, email questions only → 20 sales/mo ≈ 3.3 hr/mo.

## Inputs

- The buyer's real message (Boss will forward it — Elora does not see the buyer's inbox); if there is none, a topic template.
- Topic: `delivery` | `tracker` | `script` | `refund` | `policy` | `general` (`topic` in the payload).
- `02-Digital-Product-Department/kit-outline.md` (description of the 6 parts).
- Refund policy (whatever will be written on the sales page — not decided yet; **BOSS INPUT REQUIRED**).
- Research report §7.3 (per-sale economics: on Lemon Squeezy a $49 sale nets $46.05; at a 3% refund ASSUMPTION, effective net $44.67).

## Step-by-step method

1. **Read the buyer's message** — what kind of question is it: (a) delivery/file opening, (b) tracker formula, (c) using a script, (d) refund, (e) a question about the policy template. If there is no real message, write the topic's template.
2. **Write the reply DRAFT** — plain US English, short, direct. Write the file/part names correctly (from kit-outline.md).
3. **If it is a policy question**, always write: "have your own attorney review before using" — the template is not legal advice.
4. **If it is a refund question**, write per the sales page's policy — if the policy is not decided, write in the DRAFT: **BOSS INPUT REQUIRED** (refund policy) — a policy cannot be invented by guessing; the draft only says the terms will be confirmed, with no refund promise.
5. **If it is a price question**, write only the locked $49 (launch $39 for the first 30 buyers) — no other price, discount, or guarantee can be written. $49 cannot be quoted to a prospect unless Boss confirms.
6. **Show the DRAFT to Boss** — it is only sent after Boss says `send`.

## Output format

- Reply DRAFT (plain US English) + an honest note: "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale. DRAFT ONLY — not sent."
- The top of the DRAFT will say: DRAFT — not sent.

## Tools used

- Read-only file read: `kit-outline.md` (description of the 6 parts).
- Mock brain draft (BrainFactory, config `brain: mock`, $0) — writes the reply DRAFT, not a live call.
- ApprovalGateway for gated work (PENDING record) — `send` is needed to send.
- No live tool, network, or file write. This skill does not see the buyer's inbox.

## Gate

- Boss's `send` is needed to send it. The DRAFT itself is safe, no gate.

## Honest limits

- **Sale 0 — no buyers.** This skill's real test has not happened yet.
- The refund policy is not decided yet — nothing about refunds can be written without Boss's decision.
- No client/testimonial/statistic can be invented. No reply can be written to an invented buyer's question — a DRAFT only when a real message arrives; a template if not.
- The policy template cannot be presented as legal advice.
- No price outside the locked $49 can be quoted; even $49 cannot be quoted to a prospect unless Boss confirms.
- **BOSS INPUT REQUIRED:** refund policy (for the sales page) + the first buyer's real message (DRAFT only when it arrives).

## Never does this

- Gives legal advice; invents a refund policy; passes an invented buyer's message off as real.
- Sends mail; writes any file.

## Worked example (with real repo facts)

- **Task:** `{"type": "support_draft", "title": "Tracker question template", "payload": {"topic": "tracker"}}` → `SupportDrafterAgent.run()`.
- **Agent does:** takes the No-Show Log + $ Tracker's description from kit-outline.md (log each no-show; formulas auto-total: the month's misses, estimated $ loss, recovery rate).
- **Result:** status `draft-ready`; at the top of the output, "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale. DRAFT ONLY — not sent." Then a plain US English reply DRAFT: log each no-show on its own row, formulas auto-total monthly misses / est. $ lost / recovery rate, check with sample numbers. Not sent.
