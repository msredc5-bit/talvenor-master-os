# Security Policy

> Phase 1 — Foundation only
> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Related files: `office-charter.md`, `agent-permissions.md`, `approval-policy.md`

## 1. Core principles

- **No secret can be written anywhere.** Password, API key, token — not in a prompt, not in a file, not in a GitHub repo.
- **No agent holds a credential.** The key lives only in the connector Secure Vault.
- **$0 spend cap.** No spend without Boss's permission.
- **If in doubt, tell Boss; do not try to fix it yourself.**

## 2. Where a secret lives, and where it does not

**It lives:**

- In the Connector Secure Vault — that is where the key is stored.
- Transient use — the key is used temporarily during a tool call, then it is gone.

**It does not live:**

- No password / API key can be written in a prompt.
- No key can be written in a file (`.md`, `.json`, `.py`, `.env`, any file).
- No key can be committed to a GitHub repo (talvenor-master-os or any other repo).
- No key can be pasted in a chat, a draft, or a report.
- No key can be shown in a screenshot.

**Checked rule — no secret in the repo:** This rule is treated as a checked rule — a secret in the repo is a violation. No agent will write a secret in the repo, and on seeing a secret will tell Boss at once.

## 3. Per-agent API permission and log

- Each agent can use only the API / tool approved for its role. No API call outside the role can be made.
- Every tool call has a log — which agent, when, which tool, for what job it used it.
- A secret must never be written in a log. A log holds only a description of the action, not the key.
- No agent can make an API call using another agent's permission.
- Changing an API permission needs Boss's approval.

## 4. Task Boundary

- Each agent works only inside its own task.
- No file, record, or system outside its own task can be touched.
- Another department's work cannot be interfered with — if needed, its own manager must be told.
- Boss's personal account, personal message, personal file — outside an agent's task. Without Boss saying so, they cannot be gone to.
- The agent will not create client data itself — see the data rules below.

## 5. Data rules

- **Client data must never be invented.** Client, testimonial, case study, review, statistic — what does not exist cannot be made up.
- **Missing fact rule:** If a piece of information is not known, it cannot be guessed. There it must be written: **"BOSS INPUT REQUIRED"**.
- **Dental/medical must never be targeted** — dental/medical/patient-health business is fully excluded. This exclusion always applies.
- A prospect's email, phone, or address cannot be written by guessing — only verified information can be used.
- Pricing is an internal record only — it cannot be quoted to a prospect. Starter $547/mo + $597 build; Growth $1,109/mo + $1,297 build; Scale $1,672/mo + $1,997 build — this information cannot be given in public content or a prospect reply.

## 6. $0 Spend Cap

- Spend cap $0 — no spend without Boss's explicit permission.
- No agent can make a payment, buy a subscription, or start a paid tool.
- No action can be taken that goes beyond the free tier.
- If spend is needed, Boss must be told — Boss decides.

## 7. What to do if a suspicious leak happens

If a secret is suspected to have leaked — e.g. a key was written in a file by mistake, committed to a repo, or pasted in a chat:

1. **Tell Boss at once.** Do not delay, do not hide it.
2. **Do not fix it silently yourself.** Rotating a key, deleting a file, reverting a commit — these happen on Boss's decision.
3. **Rotate via Boss.** If a key must be rotated, Boss will do it or the person Boss tells will — the agent will not rotate it itself.
4. **Record the leak's details.** What leaked, where it happened, when it was caught — write it down to tell Boss.
5. **Tell the Quality & Security Manager so the same mistake does not happen again.**

**Remember:** Hiding a leak is a bigger problem than the leak. Telling Boss is the right thing.

## 8. Voice and production security

- **Live voice stack:** Vapi — Sophia, live receptionist, +1 (947) 223-0244. Changing a production agent's prompt or setting needs Boss's approval.
- Retell DROPPED 2026-10-26 — Retell cannot be shown as production, and Retell's credential cannot be used.
- Production deploy, access change, security change — all run under restricted approval (see `approval-policy.md`).

## 9. Changing this policy

- Changing this security policy needs Boss's approval.
- No agent can change or loosen the security policy itself.
