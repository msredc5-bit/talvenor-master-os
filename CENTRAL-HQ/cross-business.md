# Cross-Business Collaboration — Talvenor Unified OS

> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Core rule: one business can help another — but help does not mean sharing data. Each cross-business job is a separate internal project, tracked separately.

## 1. Who helps whom, and how

| Gives the service | Gets the service | What service |
|---|---|---|
| Content Studio (03 Media) | Agency (01) | Talvenor social post, Reel script, caption pack, ad creative — for the Agency's marketing |
| Content Studio (03 Media) | Commerce (02) | Vet Kit product creative, sales page copy draft, launch post draft |
| Agency AI Engineering (01) | Commerce (02) | Support automation (e.g. draft answers to Vet Kit buyers' common questions) — only on Boss's word |
| Central Research Intelligence | All three businesses | Market research from shared research notes (`~/workspace/research_notes/`) — the same source for everyone |

## 2. Rules for each cross-business job

1. **Track as an internal project:** work + cost (time/money — now a $0 spend cap, so time) are written separately for each project. So each business's real cost and profit can be understood separately.
2. **The receiving Chief's routing is needed:** the Chief of the business receiving the service must route the job. No cross-business job starts without the Chief knowing.
3. **A gated action needs Boss's gate word:** if the job includes send / publish / spend / delete, it does not happen without Boss's exact gate word (`ok` / `"post it"` / `send` / `go` / `"upload it"`) — not even cross-business.
4. **Share output, not data:** the business giving the service only gives the finished output (e.g. caption, creative, draft) — it does not read the other business's internal client data, orders, or financial records. Rule: `data-isolation.md`.
5. **DRAFT only until approval:** cross-business output is also a draft — no publish/send without Boss's `ok`.

## 3. Examples (all internal projects, never automatic)

### Example A — Talvenor social post (for the Agency)

- Content Studio makes a Reel script + caption draft → goes to the Agency Chief → on Boss's `ok`, PublishPrep runs → on Boss's `"post it"`, it is posted from the main chat.
- Status: parts of this flow are BUILT (ContentPlanner, CaptionWriter, VideoProducer, PublishPrep — all draft-only); posting is never automatic.

### Example B — Vet Kit product creative (for Commerce)

- Content Studio makes a Vet Kit creative draft → goes to the Products Chief → used on Boss's `ok`.
- Status: NOT STARTED — the kit work itself is BLOCKED because Gate 0 is NOT passed; creative work comes after Gate 0.

### Example C — Support automation (for Commerce)

- Agency AI Engineering makes a support automation draft for Commerce — only on Boss's word.
- Status: NOT STARTED — Boss's order remaining; no automation is live (n8n READY NOT LIVE).

## 4. What must not be done (NOT ALLOWED)

| Forbidden | Why |
|---|---|
| Silent cross-read (quietly reading another business's data) | Breaks data isolation — not without Boss's explicit permission. |
| Cross-business send (sending in another business's name from one business) | The send gate is Boss's — no business can send on another's behalf by itself. |
| Automatic data sharing (copying one business's client/order/finance records into another business) | Each business's records stay separate — `data-isolation.md` §3. |
| Cross-business publish (publishing one business's content on another business's channel) | The publish gate is Boss's `"post it"` — whoever owns the channel, it happens on Boss's word. |
| Hiding costs (charging a cross-business job's cost to one business's account) | Each project's cost is tracked separately — §2.1. |

## 5. Current state (true)

- No live example of cross-business work has happened yet — all examples above are written as DRAFT/plan.
- Parts of the flow for Content Studio helping the Agency are BUILT (draft-only); work to help Commerce is NOT STARTED (Gate 0 BLOCKED).
- No cross-business automation is live.
