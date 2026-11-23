# Talvenor Permission Matrix — agent to allowed tools

**Generated** from the enforced table in `00-CEO-Core/permissions.py` by `scripts/generate_permission_matrix.py` — do not edit by hand; edit the table and re-run the generator.

Enforced in `tool_calling.call_tool()`: a call that names an agent is denied with status `denied-permission` when the agent may not use the tool. A call with NO identified agent follows the legacy dispatcher path (the MCP server, engine wrappers, and older check scripts call without an agent).

Legend: `✓` = allowed. `✓*` = gate-request only — the agent may only REQUEST the gated tool via the ApprovalGateway (trust_check + gateway); it never executes. `—` = not allowed. An agent not listed here has **NO tools**.

Source of the assignments: `00-CEO-Core/agent-tool-assignments-DRAFT.md` (2026-11-21). The table governs only the 9 core tools in `tools.json`; engine wrappers' own tools (`send_email` / `publish_post` / `spend`) are governed by their own registries and gates.

## Main CEO Bot

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `main_ceo_bot` | — | — | — | — | — | — | — | — | ✓ |

## Chiefs of Staff

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `chief_of_staff_agency` | — | — | — | — | ✓* | — | ✓* | — | ✓ |

## Department managers

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `dept_sales` | — | — | — | — | — | — | — | — | ✓ |
| `dept_marketing` | — | — | — | — | — | — | — | — | ✓ |
| `dept_engineering` | — | — | — | — | — | — | — | — | ✓ |
| `dept_operations` | — | — | — | — | — | — | — | — | ✓ |
| `dept_strategy` | — | — | — | — | — | — | — | — | ✓ |
| `dept_finance` | — | — | — | — | — | — | — | — | ✓ |
| `dept_quality` | — | — | — | — | — | — | — | — | ✓ |
| `dept_innovation` | — | — | — | — | — | ✓ | — | — | ✓ |

## Workers — draft_email

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `OutreachDrafter` | — | — | ✓ | — | — | — | — | — | — |
| `FollowUpAgent` | — | — | ✓ | — | — | — | — | — | — |

## Workers — research_notes

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `ProspectResearcher` | — | — | — | — | — | — | — | ✓ | — |
| `BusinessVerificationAgent` | — | — | — | — | — | — | — | ✓ | — |
| `LeadScoringAgent` | — | — | — | — | — | — | — | ✓ | — |
| `SalesIntelligenceAgent` | — | — | — | — | — | — | — | ✓ | — |
| `GoogleMapsProspectFinder` | — | — | — | — | — | — | — | ✓ | — |
| `CompetitorResearchAgent` | — | — | — | — | — | — | — | ✓ | — |
| `IndustryResearchAgent` | — | — | — | — | — | — | — | ✓ | — |
| `PricingResearchAgent` | — | — | — | — | — | — | — | ✓ | — |
| `NicheSelectionAgent` | — | — | — | — | — | — | — | ✓ | — |
| `OfferDevelopmentAgent` | — | — | — | — | — | — | — | ✓ | — |
| `MarketOpportunityAgent` | — | — | — | — | — | — | — | ✓ | — |
| `BusinessIntelligenceAgent` | — | — | — | — | — | — | — | ✓ | — |

## Workers — draft_caption

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `CaptionWriter` | — | ✓ | — | — | — | — | — | — | — |
| `SocialMediaAgent` | — | ✓ | — | — | — | — | — | — | — |

## Workers — draft_script

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `VideoProducer` | — | — | — | ✓ | — | — | — | — | — |

## Workers — status_read

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `ReportCompiler` | — | — | — | — | — | — | — | — | ✓ |
| `SchedulerAssistant` | — | — | — | — | — | — | — | — | ✓ |
| `ClientReportingAgent` | — | — | — | — | — | — | — | — | ✓ |
| `AnalyticsAgent` | — | — | — | — | — | — | — | — | ✓ |
| `RevenueTrackingAgent` | — | — | — | — | — | — | — | — | ✓ |

## Workers — booking_reply

| Agent | `booking_reply` | `draft_caption` | `draft_email` | `draft_script` | `gmail_send` | `kit_outline_read` | `n8n_trigger` | `research_notes` | `status_read` |
|---|---|---|---|---|---|---|---|---|---|---|
| `ReplyHandler` | ✓ | — | — | — | — | — | — | — | — |

## Unlisted agents

Any agent not in the table above — including any new worker, manager, or chief added later — has **NO tools**: every core-tool call from it is denied. To grant a tool, add the agent to `AGENT_TOOLS` in `permissions.py` and regenerate this matrix.
