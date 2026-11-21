# Approval Policy — Gate-Word System

> Phase 1 — Foundation only
> Status: DRAFT — awaiting Boss's approval
> Date: 2026-11-19
> Related files: `office-charter.md`, `agent-permissions.md`, `security-policy.md`

## 1. Core principles

- **Nothing is sent / published / spent / deleted without Boss's exact gate word.**
- **There is no auto-approve path anywhere.** No agent, manager, or system can approve by itself.
- Giving approval is Boss's job alone. ApprovalGateway only holds the request as PENDING — it does not approve.
- Approval records live in the JSON store — `store/approvals.json`.

## 2. Gate-Word System

| Gate Word | Meaning | What gets approved |
|-----------|------|---------------|
| **ok** | Plan / asset approval | Plan, draft, design, asset — once Boss sees it and says "ok", the plan is approved |
| **"post it"** | Publish | A social post can be published — once for one post |
| **send** | Send | Email / message can be sent — only the batch it was given for |
| **go** | Advance build phase | Moving to the next build phase is allowed |
| **"upload it"** | Upload video | A video can be uploaded |

**Rules:**

- The gate word must be exact. A near word is not approval.
- One gate word is for one job. "ok" does not publish, "post it" does not send.
- A gate word's scope is only what Boss said. One batch's send approval cannot send another batch.
- An approval card can expire — if it expires, it must go to Boss again; it cannot be retried by itself.

## 3. Approval Table (CORRECTED)

Another AI's brief had the approval table wrong. The table below is the correct one:

| Job | Approval Level | Current status |
|-----|---------------|----------------|
| Lead research | Autonomous | The agent can do it itself — research needs no gate |
| Internal report | Autonomous | The agent can write it itself — as a draft to show Boss |
| Draft email | Autonomous | A draft can be created — it cannot be sent |
| External email sending | Approval / Controlled policy | Boss's "send" gate word is needed — **and currently PAUSED (since 2026-11-14, SPF/DMARC DNS fix pending)** |
| CRM update | Restricted automation | CRM (n8n Cloud Data Tables) is not live yet — there is nothing to update. Once CRM is live, it runs under the restricted automation rule |
| Production agent deployment | Founder approval | Sophia (live receptionist) deploy / change — only with Boss's approval |
| Client pricing change | Founder approval | Pricing LOCKED — changing it needs Boss's decision; it cannot be quoted to a prospect |
| Refund / payment | Human approval | All money work needs Boss's approval; spend cap $0 |
| Legal / tax filing | Human professional review | Cannot be done without a lawyer / tax professional's review |
| Security / access change | Restricted approval | Access change, secret rotate — only Boss does it, under restricted approval |

## 4. Approval Flow — how it works

1. The agent creates a draft / plan.
2. The agent sends a request to ApprovalGateway — status PENDING.
3. The request is recorded in `store/approvals.json`.
4. Boss sees the request and gives a gate word — or does not.
5. Only once the gate word is received does the action execute. Without the gate word, no action happens.
6. After execution, the result is recorded — what was done, when, on whose approval.

**What must not be done:**

- Approving a PENDING request yourself
- Guessing or assuming Boss's gate word
- Doing another job with one approval
- Acting without approval, saying "I will tell Boss later"

## 5. Email PAUSED — special note

- Email outreach PAUSED since 2026-11-14. SPF has no Gmail include, DMARC is missing — the DNS fix is pending from Boss.
- While the pause stands, email will not go even if the "send" gate word is given — first the DNS fix must be verified, then Boss will say restart.
- First mails are now 162 — this number will not grow during the pause.
- Day 4 / Day 5 drafts are READY, unsent — they cannot be sent until a restart.

## 6. No Auto-Approve

- No agent's permission includes auto-approve.
- No workflow has an auto-approve step.
- No cron / trigger can approve by itself.
- "Boss is busy, so I approved it myself" — that is never valid.

## 7. Changing approvals

- Changing this approval policy needs Boss's approval.
- Pricing, gate word, approval level — no agent can change any of them itself.
