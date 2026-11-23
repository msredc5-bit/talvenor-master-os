"""Agent tool permissions — enforced allowlist (Phase 1, Unified OS).

Source: 00-CEO-Core/agent-tool-assignments-DRAFT.md (2026-11-21 decision
draft). This module is the ENFORCED copy of that draft: the table below
is what tool_calling.call_tool() checks before any tool runs. If the
draft changes, this table changes with it — and
TALVENOR_PERMISSION_MATRIX.md is regenerated from this table
(scripts/generate_permission_matrix.py).

Rules (least privilege, from the draft):
  1. One Tool Gateway — one registry (tools.json, 9 tools), one Approval
     Gate. No agent has its own MCP server.
  2. A draft tool only for the drafter.
  3. No gated tool directly to anyone — gmail_send / n8n_trigger are not
     handed to any worker/manager/CEO. Only the Agency Chief of Staff may
     REQUEST them via the ApprovalGateway (gate-request only) — the
     request still goes through trust_check + the gateway, and nothing
     executes.
  4. No tool = work in worker code.
  5. Memory is not permission — no tool assignment is an approval.

Enforcement point: tool_calling.call_tool() resolves the requesting
agent from context (see resolve_agent) and denies with status
"denied-permission" when the agent may not use the tool. A call with
NO identified agent (the MCP server, engine wrappers, and the older
check scripts call without an agent) follows the legacy dispatcher
path and is allowed — the dispatcher cannot invent an agent for a
caller that did not name one. To be enforced, a caller must identify
its agent: context={"agent": "<agent key>"} (or a recognized
requested_by name).

Agent keys:
  - "main_ceo_bot" / "chief_of_staff_agency" (the two named agents)
  - "dept_sales" ... "dept_innovation" (the 8 department managers)
  - worker class names (OutreachDrafter, ProspectResearcher, ...)
  - anything else -> NO tools (deny).

Stdlib only. No network, no send, no publish, no spend.
"""

# The 9 tools in 00-CEO-Core/tools.json.
ALL_TOOLS = frozenset({
    "draft_email",
    "research_notes",
    "draft_caption",
    "draft_script",
    "kit_outline_read",
    "status_read",
    "booking_reply",
    "gmail_send",
    "n8n_trigger",
})

GATED_TOOLS = frozenset({"gmail_send", "n8n_trigger"})

# agent key -> allowed tools. An agent not listed here has NO tools.
AGENT_TOOLS = {
    # Main CEO Bot — status reads only. Writes no drafts, sends nothing.
    "main_ceo_bot": frozenset({"status_read"}),
    # Agency Chief of Staff — status reads + gated tools as GATE-REQUEST
    # ONLY (request via ApprovalGateway, never execute). Writes no drafts.
    "chief_of_staff_agency": frozenset({
        "status_read", "gmail_send", "n8n_trigger",
    }),
    # Department managers — status reads only (plan only, no tools).
    "dept_sales": frozenset({"status_read"}),
    "dept_marketing": frozenset({"status_read"}),
    "dept_engineering": frozenset({"status_read"}),
    "dept_operations": frozenset({"status_read"}),
    "dept_strategy": frozenset({"status_read"}),
    "dept_finance": frozenset({"status_read"}),
    "dept_quality": frozenset({"status_read"}),
    # Product Innovation manager — status reads + kit outline read
    # (the draft's "Product Innovation Manager" reads the kit outline).
    "dept_innovation": frozenset({"status_read", "kit_outline_read"}),
    # Workers — draft_email.
    "OutreachDrafter": frozenset({"draft_email"}),
    "FollowUpAgent": frozenset({"draft_email"}),
    # Workers — research_notes.
    "ProspectResearcher": frozenset({"research_notes"}),
    "BusinessVerificationAgent": frozenset({"research_notes"}),
    "LeadScoringAgent": frozenset({"research_notes"}),
    "SalesIntelligenceAgent": frozenset({"research_notes"}),
    "GoogleMapsProspectFinder": frozenset({"research_notes"}),
    "CompetitorResearchAgent": frozenset({"research_notes"}),
    "IndustryResearchAgent": frozenset({"research_notes"}),
    "PricingResearchAgent": frozenset({"research_notes"}),
    "NicheSelectionAgent": frozenset({"research_notes"}),
    "OfferDevelopmentAgent": frozenset({"research_notes"}),
    "MarketOpportunityAgent": frozenset({"research_notes"}),
    "BusinessIntelligenceAgent": frozenset({"research_notes"}),
    # Workers — draft_caption.
    "CaptionWriter": frozenset({"draft_caption"}),
    "SocialMediaAgent": frozenset({"draft_caption"}),
    # Workers — draft_script.
    "VideoProducer": frozenset({"draft_script"}),
    # Workers — status_read.
    "ReportCompiler": frozenset({"status_read"}),
    "SchedulerAssistant": frozenset({"status_read"}),
    "ClientReportingAgent": frozenset({"status_read"}),
    "AnalyticsAgent": frozenset({"status_read"}),
    "RevenueTrackingAgent": frozenset({"status_read"}),
    # Workers — booking_reply.
    "ReplyHandler": frozenset({"booking_reply"}),
}

# Gated tools an agent may only REQUEST (via the ApprovalGateway) —
# never execute. Only the Chief has any.
GATE_REQUEST_ONLY = {
    "chief_of_staff_agency": frozenset({"gmail_send", "n8n_trigger"}),
}

# Display names used as requested_by in the codebase -> agent key.
REQUESTED_BY_MAP = {
    "Main CEO Bot": "main_ceo_bot",
    "Agency Chief of Staff": "chief_of_staff_agency",
    "Chief of Staff": "chief_of_staff_agency",
}


def resolve_agent(context):
    """Identify the requesting agent from a call_tool context.

    Order: context["agent"] (explicit key) -> context["requested_by"]
    (display name, mapped) -> None (unidentified — legacy path).
    An explicit agent key that is not in the table is still returned
    (it resolves to NO tools); only a missing identification is None.
    """
    if not isinstance(context, dict):
        return None
    agent = context.get("agent")
    if isinstance(agent, str) and agent.strip():
        return agent.strip()
    requested_by = context.get("requested_by")
    if isinstance(requested_by, str) and requested_by.strip():
        name = requested_by.strip()
        if name in REQUESTED_BY_MAP:
            return REQUESTED_BY_MAP[name]
        if name in AGENT_TOOLS:
            return name
    return None


def allowed_tools(agent_key):
    """The tools an agent may use (empty set for an unknown agent)."""
    if not isinstance(agent_key, str):
        return frozenset()
    return AGENT_TOOLS.get(agent_key, frozenset())


def is_allowed(agent_key, tool_name):
    """Whether this agent may call this tool."""
    if tool_name not in ALL_TOOLS:
        return False
    return tool_name in allowed_tools(agent_key)


def is_gate_request_only(agent_key, tool_name):
    """Whether the agent may only REQUEST this gated tool (never execute)."""
    return tool_name in GATE_REQUEST_ONLY.get(agent_key, frozenset())


def check_permission(agent_key, tool_name):
    """(allowed, reason) — the reason names the agent, the tool, and the
    rule, so a denial is readable without looking the table up.

    The table governs only the 9 core tools. A tool that is not one of
    the 9 (e.g. an engine wrapper's send_email / publish_post / spend)
    is not governed here — it is allowed through to its own registry
    and gate. The engine/core tool-name divergence is a known issue
    (agent-tool-assignments-DRAFT.md) and is not rewired here.
    """
    if tool_name not in ALL_TOOLS:
        return True, (f"Tool {tool_name!r} is not one of the 9 core tools "
                      "— the permission table does not govern it.")
    if agent_key is None:
        return True, "No agent identified — legacy dispatcher path."
    allowed = is_allowed(agent_key, tool_name)
    if allowed:
        if is_gate_request_only(agent_key, tool_name):
            return True, (f"Agent {agent_key!r} may REQUEST gated tool "
                          f"{tool_name!r} via the ApprovalGateway only — "
                          "it never executes.")
        return True, f"Agent {agent_key!r} may use tool {tool_name!r}."
    return False, (f"Agent {agent_key!r} is not allowed to use tool "
                   f"{tool_name!r} (TALVENOR_PERMISSION_MATRIX.md — "
                   "no tool assignment for this agent).")


if __name__ == "__main__":
    # Self-test — no store touched.
    assert allowed_tools("main_ceo_bot") == frozenset({"status_read"})
    assert allowed_tools("chief_of_staff_agency") == frozenset(
        {"status_read", "gmail_send", "n8n_trigger"})
    assert allowed_tools("dept_sales") == frozenset({"status_read"})
    assert allowed_tools("OutreachDrafter") == frozenset({"draft_email"})
    assert allowed_tools("ReplyHandler") == frozenset({"booking_reply"})
    assert allowed_tools("NoSuchAgent") == frozenset()
    assert allowed_tools(None) == frozenset()
    assert is_allowed("OutreachDrafter", "draft_email") is True
    assert is_allowed("OutreachDrafter", "gmail_send") is False
    assert is_allowed("main_ceo_bot", "draft_email") is False
    assert is_allowed("chief_of_staff_agency", "gmail_send") is True
    assert is_gate_request_only("chief_of_staff_agency", "gmail_send") is True
    assert is_gate_request_only("OutreachDrafter", "gmail_send") is False
    assert resolve_agent({"agent": "OutreachDrafter"}) == "OutreachDrafter"
    assert resolve_agent({"requested_by": "Main CEO Bot"}) == "main_ceo_bot"
    assert resolve_agent({"requested_by": "OutreachDrafter"}) == "OutreachDrafter"
    assert resolve_agent({}) is None
    assert resolve_agent(None) is None
    ok, _ = check_permission("OutreachDrafter", "draft_email")
    assert ok is True
    ok, reason = check_permission("OutreachDrafter", "gmail_send")
    assert ok is False and "not allowed" in reason
    ok, _ = check_permission(None, "draft_email")
    assert ok is True  # unidentified -> legacy path
    ok, reason = check_permission("OutreachDrafter", "send_email")
    assert ok is True and "not one of the 9 core tools" in reason
    # Every tool in the table is a real tool; every gated tool is gated.
    for agent, tools in AGENT_TOOLS.items():
        assert tools <= ALL_TOOLS, (agent, tools)
    assert GATE_REQUEST_ONLY["chief_of_staff_agency"] <= GATED_TOOLS
    print("permissions: OK (table matches the DRAFT, Chief gate-request "
          "only, unknown agent has no tools)")
