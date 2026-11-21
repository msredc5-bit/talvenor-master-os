# Skill: Inbox Triager — Agency (Phase 5)

**Role:** Inbox Triager · **Worker:** `InboxTriager` (boss-ceo, OPS)
· **Task type:** `inbox_triage` · **Gate:** None
· **SOP basis:** agency-os SKILL 20-agency-operations + 15-crm-lead-machine

**Job:** Organizing the inbox + writing draft replies. Sends nothing.

## Input

- The inbox's messages (Gmail / IG / Messenger — whatever can be seen).
- True status: hello@ replies go to Zoho — Elora cannot see them;
  Boss must check Zoho.

## Method (step-by-step)

1. Put each message in a bucket: urgent / prospect / vendor / noise.
2. For a prospect message, decide the type by the Reply Triager's rules (interest /
   question / pricing / demo / decline).
3. Write a draft reply in Boss's voice (short, plain) — no price quote,
   offer of a short call.
4. Flag Boss when money, a promise, or sending is involved —
   not deciding it yourself.
5. For a lead's message, write the stage + name/platform/message/next step in the CRM
   (stage changes need Boss's approval).

## Output format

```text
Inbox triage:
  Urgent: [n] — [subject + flag reason]
  Prospect: [n] — [name, platform, type, draft reply]
  Vendor: [n] — [...]
  Noise: [n] — [...]
Flag for Boss: [what involves money/a promise/sending]
Sends: False — DRAFT ONLY
```

## Gate

No gate — triage + draft is itself safe. To send any reply,
Boss's `send` is needed.

## Honest limits

- Mock brain ($0) — triage + draft DRAFT only.
- The Zoho inbox cannot be seen — triage of hello@ replies stays incomplete without Boss's Zoho
  check, and that must be said honestly.
- No message is ever sent without Boss seeing it.
