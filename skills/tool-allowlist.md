---
name: tool-allowlist
description: "Enforcing per-agent tool allowlists in the Tool Gateway — which agent may run which"
---

# Tool-Allowlist Enforcement — Skill (for the Agency Chief of Staff)

## Role

Enforcing per-agent tool allowlists in the Tool Gateway — which agent may run which
tool, and where Boss's approval is needed for gated tools. This
skill is read by the Agency Chief of Staff (the Chief is the only funnel toward the gate).
Enforcement happens in code, not in prompts.

- Code: `00-CEO-Core/tools.json` (9 tool) + `tool_calling.py`
  (dispatcher) + `human_approval_gateway.py` + `trust_gate.py`
- Policy: `00-CEO-Core/agent-tool-assignments-DRAFT.md` (per-agent table)
- Source (adapted, not copied): frankxai/skills `tool-allowlist` (MIT) —
  default-deny, deny wins, least privilege per task. Secondary:
  braydos-h/BreachPilot `securing-agentic-ai-tool-invocation`
  (Apache-2.0) — allowlist + HITL + audit logging.

## Principles (unbreakable)

### 1. Default-deny — not in the allowlist means deny

An agent may only run the tools in its allowlist. Not in the list — deny.
Not a blocklist (a new tool would be allowed by default — that is insecure).

### 2. Deny wins — deny always beats allow

If the same tool has both deny + allow, deny wins. A narrow deny can sit inside a broad allow;
a narrow allow cannot sit inside a broad deny.

### 3. Least privilege per task — tools per task

Each task has its own allowlist. A review task has no deploy tool. Without a `why`
no allow rule may be kept — a rule with no written task need
must be deleted.

### 4. Enforce natively — the dispatcher, not the prompt

A prompt/skill tells an agent what to do — but the boundary is held by
the dispatcher (`tool_calling.py`). The dispatcher checks before a tool call;
a prompt's words are not the boundary.

## Enforcement procedure — before every tool call

The dispatcher checks in this order (one failure means deny):

1. **Allowlist check** — is the tool in this agent's allowlist?
   Missing → deny + report.
2. **Gated check** — if `gmail_send` / `n8n_trigger`: is there an approval record in the ApprovalGateway
   + Boss's exact gate word (`send`)?
   Missing → PENDING, stop.
3. **Argument check** — is there a secret (key/token/password) in the arguments?
   If so, deny.
4. **Audit log** — every call (allow/deny) goes to the log — who, which tool,
   when, why.

## The 9 tools + who gets what (from DRAFT policy)

| Tool | Type | Who gets it |
|---|---|---|
| `draft_email`, `research_notes`, `draft_caption`, `draft_script`, `booking_reply` | mock, draft-only | only the worker that writes drafts |
| `kit_outline_read`, `status_read` | mock, read-only | CEO, Chief, Manager, reader worker |
| `gmail_send`, `n8n_trigger` | **gated, live-ready** | nobody directly — only the Chief, requesting via the ApprovalGateway on Boss's `send` word; the dispatcher executes, not the agent |

The CEO only gets `status_read`. Managers only get `status_read`.
Workers get nothing except their own draft tools.

## Stop conditions — stop when you see them

- The agent has a tool but there is no policy file / the policy cannot be read.
- An allowed call surprises you — shrink the allow, add a deny,
  check whether the same gap exists anywhere else.
- A deny was bypassed (called with a different spelling) — put the boundary in the dispatcher,
  not in the prompt.

## Tools (what it uses)

- `00-CEO-Core/tool_calling.py` — dispatcher (enforcement point).
- `00-CEO-Core/tools.json` — one registry (9 tools).
- `00-CEO-Core/human_approval_gateway.py` — approval record.
- `00-CEO-Core/trust_gate.py` — quote-verified confirmation.

## Permissions

- ✅ Allowlist check + deny + audit log.
- ✅ Approval request for a gated tool (the Chief does it).
- ❌ Changing the allowlist yourself — changing it needs Boss's "ok", then
  separate wiring.
- ❌ Running a gated tool directly — the dispatcher executes it.
- ❌ Running a tool without a policy file.

## Success Criteria

- All 4 checks ran before every tool call.
- Unknown tool/agent → deny + report (no silent retry).
- Nothing happened on a gated tool without an approval record.

## Honest Status (True State)

- Tool Gateway: **ONE** — one registry, one MCP server, one
  Approval Gate. No per-agent MCP servers (Boss's decision: 8 GB PC
  + $0 rule).
- Policy: **DRAFT** — `agent-tool-assignments-DRAFT.md`; no code changed
  yet.
- Brain: **mock ($0)**; a gated tool never executes.

## Never-Do List

- Does not run a tool without an allowlist.
- Does not use memory as permission.
- Does not run a gated tool without approval.
- If a deny is bypassed, does not stay silent — reports it.
