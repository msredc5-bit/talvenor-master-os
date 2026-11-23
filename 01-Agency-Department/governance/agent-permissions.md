# Agent Permissions — Per-Agent Permission Model

> Phase 1 — Foundation only
> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Related files: `office-charter.md`, `approval-policy.md`, `security-policy.md`

## 1. Core Principles

1. **Each agent's permission follows its role.** No action outside the role can be done.
2. **A mock-brain agent only drafts.** No live action can be executed with a mock brain.
3. **No agent holds a credential.** Password, API key, token — no agent has any of them. The key lives only in the connector Secure Vault, used transiently.
4. **A manager can plan/delegate, not execute.** A manager will not execute a gated action itself — it goes to ApprovalGateway as PENDING, to Boss.
5. **No auto-approve.** Having permission does not make an action happen — a gated action still needs Boss's gate word.

## 2. The four parts of a permission

Each agent's permission is understood through these four:

| Part | Meaning |
|-----|------|
| **Role** | What the agent is for — e.g. Sales Manager, Marketing Manager |
| **Allowed tools** | Which tools it can use — e.g. file read, draft write, research |
| **Allowed actions** | Which jobs it can do itself — e.g. research, draft, plan, delegate |
| **Forbidden actions** | Which jobs it can never do — e.g. send, publish, spend, delete, credential access |

## 3. Worker Agent — general rules

- **Allowed tools:** File read, draft write, research/search, creating internal notes.
- **Allowed actions:** Researching, creating drafts, writing internal reports, arranging its own section's plan.
- **Forbidden actions:**
  - Sending external email / DM / message
  - Publishing a social post
  - Spending money, paying, giving a refund
  - Deleting a file / record / repo
  - Deploying or changing a production Vapi agent
  - Seeing or using a credential, password, API key
  - Contacting a client directly
  - Quoting a price

## 4. Manager Agent — general rules

- **Allowed tools:** Delegating to worker agents, reviewing drafts, creating plans, writing internal reports.
- **Allowed actions:** Planning, delegating, creating and reviewing drafts, sending to Boss for approval.
- **Forbidden actions:**
  - Executing a gated action itself (send / publish / spend / delete / deploy)
  - Bypassing ApprovalGateway
  - Telling a worker to do a gated action
  - Accessing a credential
  - Changing or quoting pricing
  - Filing legal / tax

A manager's job is plan + delegate + draft — no more.

## 5. Permission table for the 8 manager agents

All managers' permission level is on the same basis: **plan + delegate + draft; gated action → ApprovalGateway PENDING**. No manager has a separate execute permission.

| # | Manager Agent | Department | Permission Level | What happens on a gated action |
|---|---------------|------------|------------------|------------------------|
| 01 | Sales Manager | 01 Sales & Growth | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 02 | Marketing Manager | 02 Marketing | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 03 | AI Engineering Manager | 03 AI Engineering | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 04 | Client Operations Manager | 04 Client Operations | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 05 | Research & Strategy Manager | 05 Research & Strategy | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 06 | Finance & Admin Manager | 06 Finance & Admin | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 07 | Quality & Security Manager | 07 Quality & Security | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |
| 08 | Product & Innovation Manager | 08 Product & Innovation | Plan + delegate + draft | ApprovalGateway PENDING → Boss's gate word is needed |

**Note:** Agency Chief wiring is DONE (Phase 2, 2026-11-19) — the Agency Chief
now calls all 8 department managers via DEPARTMENT_ROUTING in
`chief_of_staff_agency.py`. The old "not done yet" line was corrected in
Unified Business OS Phase 2 (2026-11-23).

## 6. Special limits

- **Sales Manager:** Can research leads, can draft emails — but cannot send email. Email outreach is now PAUSED (since 2026-11-14). Even when the pause lifts, sending needs Boss's gate word.
- **Marketing Manager:** Can draft posts — but cannot publish without "post it".
- **AI Engineering Manager:** Can draft a Vapi build plan — but cannot deploy or change the production agent (Sophia, live receptionist, +1 (947) 223-0244). Production deploy only with Boss's approval.
- **Finance & Admin Manager:** Can draft accounts — but cannot pay, refund, or spend. Spend cap $0.
- **Quality & Security Manager:** Can audit, can flag problems — but cannot change access or rotate a secret. Boss does that.
- **Product & Innovation Manager:** Can draft a Vet Kit idea — but cannot take any live step on the Vet Kit until Gate 0 passes.

## 7. What happens if a permission is broken

- If any agent tries to take an action outside its permission, that action will be blocked.
- The blocked action is recorded as PENDING in ApprovalGateway — in store/approvals.json.
- The agent will not try to bypass the block itself. A bypass attempt must be reported to the Quality & Security Manager.
- Changing a permission needs Boss's approval. No agent can raise its own permission itself.

## 8. Credential rules (summary)

- No agent has a password / API key / token.
- The key lives only in the connector Secure Vault.
- In an agent's tool call the key is used transiently — a key must never be written in a file, a prompt, or a GitHub repo.
- Details are in `security-policy.md`.
