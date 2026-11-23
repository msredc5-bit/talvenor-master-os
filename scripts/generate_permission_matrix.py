#!/usr/bin/env python3
"""Regenerate TALVENOR_PERMISSION_MATRIX.md from the enforced table.

The enforced table lives in 00-CEO-Core/permissions.py (AGENT_TOOLS +
GATE_REQUEST_ONLY). This generator reads that table and writes the
matrix — never edit the matrix by hand. If the table changes, re-run:

  python3 scripts/generate_permission_matrix.py

Stdlib only. No network, no send, no publish, no spend.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
OUT = os.path.join(ROOT, "TALVENOR_PERMISSION_MATRIX.md")

sys.path.insert(0, CEO_CORE_DIR)

import permissions  # noqa: E402


def generate():
    tools = sorted(permissions.ALL_TOOLS)
    groups = [
        ("Main CEO Bot", ["main_ceo_bot"]),
        ("Chiefs of Staff", ["chief_of_staff_agency"]),
        ("Department managers", [
            "dept_sales", "dept_marketing", "dept_engineering",
            "dept_operations", "dept_strategy", "dept_finance",
            "dept_quality", "dept_innovation",
        ]),
        ("Workers — draft_email", ["OutreachDrafter", "FollowUpAgent"]),
        ("Workers — research_notes", [
            "ProspectResearcher", "BusinessVerificationAgent",
            "LeadScoringAgent", "SalesIntelligenceAgent",
            "GoogleMapsProspectFinder", "CompetitorResearchAgent",
            "IndustryResearchAgent", "PricingResearchAgent",
            "NicheSelectionAgent", "OfferDevelopmentAgent",
            "MarketOpportunityAgent", "BusinessIntelligenceAgent",
        ]),
        ("Workers — draft_caption", ["CaptionWriter", "SocialMediaAgent"]),
        ("Workers — draft_script", ["VideoProducer"]),
        ("Workers — status_read", [
            "ReportCompiler", "SchedulerAssistant",
            "ClientReportingAgent", "AnalyticsAgent",
            "RevenueTrackingAgent",
        ]),
        ("Workers — booking_reply", ["ReplyHandler"]),
    ]
    lines = [
        "# Talvenor Permission Matrix — agent to allowed tools",
        "",
        "**Generated** from the enforced table in "
        "`00-CEO-Core/permissions.py` by "
        "`scripts/generate_permission_matrix.py` — do not edit by hand; "
        "edit the table and re-run the generator.",
        "",
        "Enforced in `tool_calling.call_tool()`: a call that names an "
        "agent is denied with status `denied-permission` when the agent "
        "may not use the tool. A call with NO identified agent follows "
        "the legacy dispatcher path (the MCP server, engine wrappers, "
        "and older check scripts call without an agent).",
        "",
        "Legend: `✓` = allowed. `✓*` = gate-request only — the agent may "
        "only REQUEST the gated tool via the ApprovalGateway (trust_check "
        "+ gateway); it never executes. `—` = not allowed. An agent not "
        "listed here has **NO tools**.",
        "",
        "Source of the assignments: "
        "`00-CEO-Core/agent-tool-assignments-DRAFT.md` (2026-11-21). "
        "The table governs only the 9 core tools in `tools.json`; engine "
        "wrappers' own tools (`send_email` / `publish_post` / `spend`) "
        "are governed by their own registries and gates.",
        "",
    ]
    for group_name, agents in groups:
        lines.append(f"## {group_name}")
        lines.append("")
        header = "| Agent | " + " | ".join(f"`{t}`" for t in tools) + " |"
        lines.append(header)
        lines.append("|---|---|" + "---|" * (len(tools) - 1) + "---|")
        for agent in agents:
            allowed = permissions.allowed_tools(agent)
            cells = []
            for tool in tools:
                if tool in allowed:
                    mark = "✓*" if permissions.is_gate_request_only(
                        agent, tool) else "✓"
                else:
                    mark = "—"
                cells.append(mark)
            lines.append(f"| `{agent}` | " + " | ".join(cells) + " |")
        lines.append("")
    lines.append("## Unlisted agents")
    lines.append("")
    lines.append("Any agent not in the table above — including any new "
                 "worker, manager, or chief added later — has **NO tools**: "
                 "every core-tool call from it is denied. To grant a tool, "
                 "add the agent to `AGENT_TOOLS` in `permissions.py` and "
                 "regenerate this matrix.")
    lines.append("")
    return "\n".join(lines)


def main():
    text = generate()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"generate_permission_matrix: {len(permissions.AGENT_TOOLS)} "
          f"agents, {len(permissions.ALL_TOOLS)} tools -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
