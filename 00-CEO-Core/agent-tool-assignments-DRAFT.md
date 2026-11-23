# Agent Tool Assignments — DRAFT (a decision draft, not live wiring)

> **Status: DRAFT — 2026-11-21.** This is a decision draft. No code was
> changed — `tools.json` / `tool_calling.py` were not touched. To change any
> agent's tools, Boss's "ok" is needed, then wiring happens separately.
> The brain is still mock; a gated tool never executes.

## Rules (least privilege)

1. **One Tool Gateway** — one registry (`00-CEO-Core/tools.json`,
   9 tools), one MCP server (`00-CEO-Core/mcp/mcp_server.py`), one
   Approval Gate (`human_approval_gateway.py` + `trust_gate.py`). No agent
   has its own MCP server (Boss's decision: 8 GB PC + $0 rule).
2. **A draft tool only for the drafter** — the agent that writes a draft gets the draft tool.
3. **No gated tool directly to anyone** — `gmail_send` / `n8n_trigger` are not
   handed to any worker/manager/CEO. Only the Agency Chief of Staff
   can request via the ApprovalGateway, with Boss's exact gate word
   (`send`) — execution is still done by the dispatcher, not the agent.
4. **No tool = work in worker code** — work outside the 9 tools (e.g. monitoring
   calls, running QA tests) happens via the worker's own code + the manager's
   delegation plan; building a new tool for that is outside this draft.
5. **Memory is not permission** — no tool assignment is an approval;
   approval lives only at the gate.

## The 9 tools (00-CEO-Core/tools.json)

| Tool | Type | Job |
|---|---|---|
| `draft_email` | mock, draft-only | DRAFT of a cold email / follow-up |
| `research_notes` | mock, draft-only | DRAFT of prospect research notes |
| `draft_caption` | mock, draft-only | DRAFT of a caption + hashtag + CTA pack |
| `draft_script` | mock, draft-only | DRAFT of a Reel / video script outline |
| `kit_outline_read` | mock, read-only | Reading the kit outline file |
| `status_read` | mock, read-only | Reading the Agency's true status (first mails 163, clients 0, email PAUSED) |
| `booking_reply` | mock, draft-only | DRAFT of a one-line reply with the booking link |
| `gmail_send` | **gated, live-ready** | Sending a real email — never executes |
| `n8n_trigger` | **gated, live-ready** | Triggering an n8n webhook — never executes |

## Agent-level assignment

### Main CEO Bot — `main_ceo_bot`

| Tool | Why |
|---|---|
| `status_read` | Telling Boss the Agency's true status + routing to the right Chief |

Nothing else — the CEO writes no drafts, sends nothing. Gated tools: none.

### Agency Chief of Staff — `chief_of_staff_agency`

| Tool | Why |
|---|---|
| `status_read` | Telling the CEO the status + checking the status before delegating |
| `gmail_send` (gate-request only) | With Boss's exact `send` word, request via the ApprovalGateway — not execute |
| `n8n_trigger` (gate-request only) | With Boss's exact word, request via the ApprovalGateway — not execute |

The Chief writes no drafts itself — the workers write drafts. The Chief is the
only funnel towards the gate.

### Department Managers — 8 people (all under the same rule)

| Manager | Tool | Why |
|---|---|---|
| Sales (`dept_sales`) | `status_read` | Checking the status before building a delegation plan |
| Marketing (`dept_marketing`) | `status_read` | Same |
| AI Engineering (`dept_engineering`) | `status_read` | Same |
| Client Operations (`dept_operations`) | `status_read` | Same |
| Research & Strategy (`dept_strategy`) | `status_read` | Same |
| Finance & Admin (`dept_finance`) | `status_read` | Same |
| Quality & Security (`dept_quality`) | `status_read` | Same |
| Product Innovation (`dept_innovation`) | `status_read` | Same |

Managers only build a DRAFT of the delegation plan — they do not run a worker's
tool themselves. Gated tools: no manager has any.

## Worker / specialist-level assignment (by tool)

### `draft_email` — email draft (draft-only)

| Worker | Department | Why |
|---|---|---|
| OutreachDrafter (primary) | Sales | Writing cold-email drafts is its job |
| FollowUpAgent | Sales | Writes follow-up email drafts (following the 100-mail rule) |

### `research_notes` — research draft (draft-only)

| Worker | Department | Why |
|---|---|---|
| ProspectResearcher (primary) | Sales | Prospect research is its job |
| Business Verification Agent | Sales | Writes notes verifying a business |
| Lead Scoring Agent | Sales | Writes notes with the reasons for a lead score |
| Sales Intelligence Agent | Sales | Writes notes on sales signals |
| Google Maps Prospect Finder | Sales | Writes notes on prospects found from Maps |
| Competitor Research Agent | Research & Strategy | Writes competitor notes |
| Industry Research Agent | Research & Strategy | Writes industry notes |
| Pricing Research Agent | Research & Strategy | Writes pricing notes |
| Niche Selection Agent | Research & Strategy | Writes niche notes |
| Offer Development Agent | Research & Strategy | Writes offer notes |
| Market Opportunity Agent | Research & Strategy | Writes opportunity notes |
| Business Intelligence Agent | Research & Strategy | Writes BI notes |

### `draft_caption` — caption draft (draft-only)

| Worker | Department | Why |
|---|---|---|
| CaptionWriter (primary) | Marketing | Writing caption + hashtag + CTA packs is its job |
| Social Media Agent | Marketing | Writes caption drafts for social posts |

### `draft_script` — video script draft (draft-only)

| Worker | Department | Why |
|---|---|---|
| VideoProducer (primary) | Marketing | Writing Reel / video scripts + shot lists is its job |

### `kit_outline_read` — reading the kit outline (read-only)

| Worker | Department | Why |
|---|---|---|
| Product Innovation Manager | Product Innovation | Reads the kit outline for new product research |

Note: The kit belongs to the Digital Product department — from the Agency side it
can only be read, not changed.

### `status_read` — reading the status (read-only)

| Worker | Department | Why |
|---|---|---|
| ReportCompiler (primary) | Finance & Admin | Reads the status as input for building reports |
| SchedulerAssistant | Sales | Checks the status before scheduling |
| Client Reporting Agent | Client Operations | Reads the status for client reports |
| Analytics Agent | Marketing | Reads the status for analytics |
| Revenue Tracking Agent | Finance & Admin | Reads the status for revenue reports |

(The CEO, Chief, and 8 Managers also get `status_read` — see above.)

### `booking_reply` — booking reply draft (draft-only)

| Worker | Department | Why |
|---|---|---|
| ReplyHandler (primary) | Sales | Writing reply drafts with a booking link in a lead's name is its job |

### `gmail_send` (gated) — directly to nobody

| Who | How |
|---|---|
| Agency Chief of Staff | Request only via the ApprovalGateway, with Boss's exact `send` word |
| All workers / managers / CEO | **No** — nobody gets `gmail_send` directly |

### `n8n_trigger` (gated) — directly to nobody

| Who | How |
|---|---|
| Agency Chief of Staff | Request only via the ApprovalGateway, with Boss's exact word |
| n8n Automation Engineer | Can only build a DRAFT of the payload — cannot trigger |
| All workers / managers / CEO | **No** — nobody gets `n8n_trigger` directly |

## Gets no tool — works in worker code (42 people)

For these specialists' work, there is no action inside the 9 tools —
they work via the manager's delegation plan + their own worker code:

- Sales: NegotiationCoach, ObjectionSimulator, SalesCloser, CRM Manager Agent
- Marketing: ContentPlanner, PublishPrep, Market Positioning Agent, SEO Agent
- AI Engineering: RetellBuilder, QAEngineer, AI Solution Architect,
  Conversation Designer, Prompt Engineering Agent, Vapi Integration Agent,
  Calendar Integration Agent, n8n Automation Engineer, Deployment Agent
- Client Operations: ClientIntakeReceiver, OnboardingAgent,
  ServiceDeliveryManager, ClientSuccessAgent, InboxTriager,
  Call Monitoring Agent, Retention Agent, Renewal & Upsell Agent
- Finance & Admin: BillingInvoiceAgent, Subscription Tracking Agent,
  Document Management Agent, Compliance Calendar Agent
- Quality & Security: QAEngineer, Call Scenario Testing Agent,
  Workflow Testing Agent, Data Validation Agent, Security Monitoring Agent,
  Access Control Agent, Compliance Review Agent
- Product Innovation: New AI Product Research Agent, New Feature Research
  Agent, Automation R&D Agent, Technology Evaluation Agent,
  Product Improvement Agent, Prototype Builder Agent

GAP roles (4 people — no worker/skill, so no tool either): Ad Campaign Agent,
CRM Integration Agent, Expense Tracking Agent, Backup & Recovery Agent.

Note: QAEngineer is in the Quality registry in two rows (`QAEngineer` +
`QAEngineer (partial)`) — the same worker; counted once in this draft
(AI Engineering + Quality — it works in both departments).

## Tool gap — what is not in the 9 tools (not assigned in this draft)

There is no tool action for these — Boss's decision will be needed in future;
no new tool was built in this draft:

| Needed | Who needs it | Status |
|---|---|---|
| Calendar action (read/write) | SchedulerAssistant, Calendar Integration Agent | No calendar tool exists |
| Inbox-read action (Gmail / IG) | InboxTriager, ReplyHandler | No inbox-reading tool exists |
| Publish action | PublishPrep | Not in the core registry (see the divergence below) |
| Spend action | Finance (in future) | Not in the core registry; not needed now under the $0 cap |

## Divergence — the Agency engine's vendored copy (warning)

`01-Agency-Department/engine/tools.json` is **not** a copy of the core — it has
8 separate tools:

| Engine copy | Equivalent in the core copy |
|---|---|
| `draft_email`, `research_notes`, `draft_caption`, `draft_script`, `status_read` | Present under the same names |
| `send_email` (gated stub) | Named `gmail_send` in the core (gated, live-ready) |
| `publish_post` (gated stub) | **Not** in the core |
| `spend` (gated stub) | **Not** in the core |
| — | In the core but not in the engine: `kit_outline_read`, `booking_reply`, `gmail_send`, `n8n_trigger` |

Two names for the same job (`send_email` vs `gmail_send`) can cause confusion.
This draft rewires nothing — to fix it, there must be one registry
(the core's 9 names), and the engine must use it. That will not be done without
Boss's separate "ok".

## Decisions for Boss (for this draft)

1. Whether the assignment above is ok as policy (if yes, wiring is separate work).
2. Whether the engine copy's divergence must be brought into one registry.
3. Whether any of the tool gaps (calendar / inbox-read / publish) must be
   built now — otherwise those workers stay in worker code.
