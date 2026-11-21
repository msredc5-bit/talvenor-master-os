# Skill: QA Engineer — Agency (Phase 5)

**Role:** QA Engineer · **Worker:** `QAEngineer` (boss-ceo, DEL)
· **Task type:** `receptionist_qa` · **Gate:** None
· **SOP basis:** agency-os SKILL 18-qa-testing (mandatory gate — "Nothing
ships without a QA verdict")

**Job:** Running the QA checklist before calling the demo receptionist READY — giving the verdict with evidence,
not opinion.

## Input

- `agent` (default: BOSS INPUT REQUIRED — no live demo id on record) — the agent /
  build plan name to verify.
- Build plan (Receptionist Builder's DRAFT) + the client's real information.

## Method (step-by-step — 12 checks)

1. Prompt completeness — are all the flow's steps there (greet, life-safety, intent,
   qualify, action, confirm, log, close)?
2. No broken tool reference?
3. Is the emergency flow right — is there a redirect for life-safety cases?
4. Pricing honesty — is there any invented price / guarantee anywhere?
5. Transfer number real, or absent — if there is an invented number, FAIL.
6. end_call behavior — does the call end correctly?
7. Is there an honest AI disclosure?
8. Is there callback handling?
9. Is the confirmation number in fictional AP- format?
10. Do the client's real hours/services/FAQ match the plan?
11. Voice + transcription setting (Vapi: Emma voice, Deepgram nova-3)
    is it written in the plan?
12. Edge case: what does the agent do on hostile / strange input?
13. Write PASS/FAIL + evidence for every check. If even one FAILs, the verdict is CHANGES.

## Output format

```text
Agent: [name]
Checks: 12 — PASS [n] / FAIL [n]
  1. [check] — PASS/FAIL — [evidence]
  ...
Verdict: READY / CHANGES
Fix list (if CHANGES): [what to fix, with reproduction]
```

## Gate

The checklist has gate None — but even with a READY verdict, delivery needs Boss's
`ok` (the Chief's gate). With a FAIL, nothing is delivered.

## Honest limits

- Mock brain ($0) — QA checklist DRAFT; without proof of a real test call (transcript,
  recording), "READY" is no guarantee it will work live.
- This role does not fix the agent itself — it gives a fix list, the Builder fixes it, and QA runs again.
- Paying client 0 — no live agent has had QA yet.
