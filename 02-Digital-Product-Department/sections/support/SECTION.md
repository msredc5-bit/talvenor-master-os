# Support Section — Buyer-Reply DRAFTs (Templates)

**Purpose:** Write DRAFT replies to kit buyers' questions — delivery, tracker formula, using a script, refund, policy template — plain US English, DRAFT only.

## Staff roster

| Staff | Agent file | Skill file | Gate | Status |
|---|---|---|---|---|
| Support Drafter | `agents/support_drafter.py` (`SupportDrafterAgent`, task `support_draft`) | `skills/support-drafter.md` | `send` | Existing role — new file as a section agent |

## How work flows

1. Main CEO Bot → Products Chief → `support_draft` (the Chief's `SECTION_ROUTING` branch, Phase 7, new) → `SupportDrafterAgent`.
2. If the buyer's real message is there (Boss will forward it), a reply DRAFT to it; if not, a template for the topic (`delivery` | `tracker` | `script` | `refund` | `policy` | `general`) — from the kit's 6 parts in kit-outline.md.
3. For a policy question, always: "have your own attorney review before using" — the template is not legal advice.
4. For a refund question, no refund promise — the refund policy is not decided yet (BOSS INPUT REQUIRED).
5. Every output has an honest note: "Sale 0 — no live buyers yet. This is a TEMPLATE until the first sale."

## Gates

- Boss's `send` is needed to send it. The DRAFT itself is safe, no gate.

## Honest limits

- **Sale 0 — no buyers.** This section's real test has not happened yet; real buyer-reply work starts only after Gate 0 passes + the first sale.
- **Gate 0 NOT PASSED, kit 0/6 built**, email **PAUSED** (since 2026-11-14).
- The refund policy is not decided yet — nothing about refunds can be written without Boss's decision.
- No agent sends mail, gives legal advice, passes an invented buyer's message off as real, writes a file, or touches the network.
