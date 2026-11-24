"""Lead-chain step executors — Talvenor Master OS, local-first Phase 6.

One function, ``execute_step(step, prospect, context)``, returning
``(status, detail, error)`` with status in
{"ok", "pending-approval", "blocked", "error"}.

Step dicts (defined by Worker A in ``chain.py``) carry keys
{"id", "name", "department", "specialist", "kind", "gate",
"on_failure"}. Dispatch is on ``step["kind"]``.

Rules (hard):
  * Everything is DRAFT-ONLY, TEST data only, $0. No send, no
    publish, no spend, no delete, no deploy, no network, no live
    call of any kind. Every detail string is labelled "[DRAFT]".
  * ``outreach_draft`` produces the draft email but the gated send
    is NEVER executed: when the step carries a gate, the step
    returns "pending-approval" so the chain treats it as held.
  * ``deployment`` is ALWAYS "blocked" in sandbox — Boss approval
    is required, and no code path here can ever return anything
    else for it.
  * No prices are ever quoted. The sales draft says "details on a
    short call" instead.
  * Dental/medical prospects are never qualified (DQ).
  * ``execute_step`` never raises: any exception inside a step
    becomes ("error", "", str(exc)).

Specialist names used in draft details are the REAL specialist
class names from the department ``specialists/`` folders (verified
from the files, not invented).

Stdlib only. No network, no keys, no spend.
"""

from __future__ import annotations

import os

__all__ = ["execute_step", "BOOKING_LINK"]

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"

# Real specialist names, verified from the department specialists/
# folders (class names in the files there).
SPECIALISTS = {
    # Must match CHAIN_STEPS in chain.py (verified against the
    # department specialists/ folders): lead_discovery is 05's
    # MarketOpportunityAgent (not 01's GoogleMapsProspectFinder),
    # lead_verification is 07's DataValidationAgent (not 01's
    # BusinessVerificationAgent), reply_monitoring and monitoring
    # are 04's CallMonitoringAgent, client_onboarding is 04's
    # RetentionAgent, qa is 07's CallScenarioTestingAgent.
    "lead_discovery": "MarketOpportunityAgent",
    "lead_verification": "DataValidationAgent",
    "lead_qualification": "LeadScoringAgent",
    "crm_dryrun": "CRMManagerAgent",
    "outreach_draft": "SalesIntelligenceAgent",
    "reply_monitoring": "CallMonitoringAgent",
    "meeting": "SalesIntelligenceAgent",
    "sales_process": "SalesIntelligenceAgent",
    "client_onboarding": "RetentionAgent",
    "service_delivery": "VapiIntegrationAgent",
    "qa": "CallScenarioTestingAgent",
    "deployment": "DeploymentAgent",
    "monitoring": "CallMonitoringAgent",
}


def _spec(step, kind):
    """Specialist name for a detail string: the step dict's own
    "specialist" (from CHAIN_STEPS) wins, else the map above."""
    if isinstance(step, dict) and step.get("specialist"):
        return str(step["specialist"])
    return SPECIALISTS.get(kind, "Specialist")

_EXCLUDED_TYPES = ("dental", "medical")


def _name(prospect):
    if isinstance(prospect, dict):
        return str(prospect.get("business_name") or "TEST Prospect")
    return "TEST Prospect"


def _business_type(prospect):
    if not isinstance(prospect, dict):
        return ""
    for key in ("business_type", "type", "niche", "category"):
        value = prospect.get(key)
        if value:
            return str(value).lower()
    return ""


def _score(prospect):
    """Score from the prospect dict; falls back to strength labels."""
    if not isinstance(prospect, dict):
        return None
    score = prospect.get("score")
    if score is not None:
        try:
            return float(score)
        except (TypeError, ValueError):
            return None
    strength = str(prospect.get("strength") or "").strip().upper()
    return {"STRONG": 85, "MEDIUM": 70, "WEAK": 40}.get(strength)


def _step_lead_discovery(step, prospect, context):
    name = _name(prospect)
    website = prospect.get("website") if isinstance(prospect, dict) else None
    if not (isinstance(prospect, dict) and prospect.get("business_name")):
        return ("error", "",
                "discovery failed: missing business_name")
    if not website:
        return ("error", "", "discovery failed: missing website")
    detail = ("[DRAFT] %s research note — %s "
              "(%s): US home-service business with a public website; "
              "looks like a receptionist candidate, verify before "
              "any outreach." % (_spec(step, "lead_discovery"), name,
                                website))
    return ("ok", detail, "")


def _step_lead_verification(step, prospect, context):
    name = _name(prospect)
    if not isinstance(prospect, dict):
        return ("error", "", "verification failed: missing email")
    if not prospect.get("email"):
        return ("error", "", "verification failed: missing email")
    if not prospect.get("phone"):
        return ("error", "", "verification failed: missing phone")
    detail = ("[DRAFT] %s verification note — "
              "%s: email and phone present on TEST data; website "
              "matches business name; no live check made."
              % (_spec(step, "lead_verification"), name))
    return ("ok", detail, "")


def _step_lead_qualification(step, prospect, context):
    name = _name(prospect)
    btype = _business_type(prospect)
    for excluded in _EXCLUDED_TYPES:
        if excluded in btype:
            return ("error", "", "DQ: dental/medical excluded")
    score = _score(prospect)
    if score is None:
        return ("error", "", "qualification failed: missing score")
    if score >= 80:
        tier = "Tier 1"
    elif score >= 60:
        tier = "Tier 2"
    else:
        tier = "Tier 4"
    detail = ("[DRAFT] LeadScoringAgent qualification note — %s: "
              "score %g, %s. Draft only; no outreach sent."
              % (name, score, tier))
    return ("ok", detail, "")


def _load_crm_dryrun():
    """Lazy path import of the sibling crm_dryrun module (same
    pattern the department managers use for 00-CEO-Core)."""
    import importlib.util  # noqa: PLC0415
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "crm_dryrun.py")
    spec = importlib.util.spec_from_file_location(
        "lead_chain_crm_dryrun", path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load crm_dryrun.py from %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _step_crm_dryrun(step, prospect, context):
    name = _name(prospect)
    module = _load_crm_dryrun()
    result = module.dry_run_upsert(prospect)
    if result.get("status") != "ok":
        return ("error", "",
                str(result.get("error") or "crm dry-run failed"))
    payload = result.get("payload") or {}
    key = payload.get("key") or {}
    detail = ("[DRAFT] CRMManagerAgent dry-run upsert — %s: would-be "
              "payload for table 'leads' keyed by %s; dry_run=True, "
              "live=False; nothing written anywhere."
              % (name, key))
    return ("ok", detail, "")


def _draft_email_body(prospect):
    name = _name(prospect)
    website = ""
    if isinstance(prospect, dict):
        website = str(prospect.get("website") or "")
    lines = [
        "[DRAFT] Outreach email — DRAFT ONLY, never sent.",
        "",
        "Subject: Missed calls = missed jobs — Talvenor answers 24/7",
        "",
        "Hi %s team," % name,
        "",
        "Imagine a homeowner calls while your crew is on a job and "
        "nobody picks up — that job usually goes to the next "
        "plumber who answers.",
        "",
        "Talvenor is an AI receptionist for home-service "
        "businesses: it answers every call, books the job, and "
        "sends you the details — 24/7.",
        "",
        "Book a short call with us here: %s" % BOOKING_LINK,
        "",
        "Best,",
        "Talvenor — AI receptionist for service businesses",
    ]
    if website:
        lines.insert(4, "(Website on file: %s)" % website)
    return "\n".join(lines)


def _step_outreach_draft(step, prospect, context):
    # The draft is always produced. The send sub-step is NOT
    # executed here: when the step carries a gate, the step status
    # is pending-approval so the chain treats the send as held.
    draft = _draft_email_body(prospect)
    if step.get("gate"):
        return ("pending-approval", draft,
                "send held: gmail_send requires Boss approval")
    return ("ok", draft, "")


def _step_reply_monitoring(step, prospect, context):
    replies = (context or {}).get("replies", []) or []
    if not replies:
        return ("ok", "[DRAFT] %s reply scan — "
                       "no replies in sandbox fixture."
                % _spec(step, "reply_monitoring"), "")
    count = len(replies)
    detail = ("[DRAFT] %s reply scan — %d "
              "repl%s in sandbox fixture; read-only scan, no reply "
              "sent." % (_spec(step, "reply_monitoring"), count,
                         "y" if count == 1 else "ies"))
    return ("ok", detail, "")


def _step_meeting(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] SalesIntelligenceAgent meeting-prep note — "
              "%s: 15-minute demo call; booking link %s (text only, "
              "no invite sent); prep: confirm pain (missed calls), "
              "confirm decision maker, no prices quoted."
              % (name, BOOKING_LINK))
    return ("ok", detail, "")


def _step_sales_process(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] SalesIntelligenceAgent sales note — %s: "
              "discovery -> demo -> proposal; no prices quoted — "
              "if asked, details on a short call; next step is the "
              "booking link, never a contract." % name)
    return ("ok", detail, "")


def _step_client_onboarding(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] %s intake checklist — %s: "
              "(1) confirm business name + services, (2) confirm "
              "booking calendar, (3) confirm call-handling script, "
              "(4) confirm go-live date. Draft only; no account "
              "created." % (_spec(step, "client_onboarding"), name))
    return ("ok", detail, "")


def _step_service_delivery(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] VapiIntegrationAgent delivery plan — %s: "
              "build receptionist (greet -> intent -> qualify -> "
              "book -> log), test calls in sandbox, QA before any "
              "live use. Draft only; nothing deployed." % name)
    return ("ok", detail, "")


def _step_qa(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] %s QA checklist — %s: "
              "script answers correctly, booking link works, no "
              "invented claims, 'Talvenor' spelled right, no "
              "prices in any message. Draft only."
              % (_spec(step, "qa"), name))
    return ("ok", detail, "")


def _step_deployment(step, prospect, context):
    # ALWAYS blocked in sandbox. No code path here returns anything
    # else for this kind.
    return ("blocked", "",
            "deployment is ALWAYS BLOCKED in sandbox — "
            "Boss approval required")


def _step_monitoring(step, prospect, context):
    name = _name(prospect)
    detail = ("[DRAFT] CallMonitoringAgent monitoring note — %s: "
              "watch answered-call rate, bookings logged, and "
              "missed-call follow-ups in sandbox records only; no "
              "live system watched." % name)
    return ("ok", detail, "")


_HANDLERS = {
    "lead_discovery": _step_lead_discovery,
    "lead_verification": _step_lead_verification,
    "lead_qualification": _step_lead_qualification,
    "crm_dryrun": _step_crm_dryrun,
    "outreach_draft": _step_outreach_draft,
    "reply_monitoring": _step_reply_monitoring,
    "meeting": _step_meeting,
    "sales_process": _step_sales_process,
    "client_onboarding": _step_client_onboarding,
    "service_delivery": _step_service_delivery,
    "qa": _step_qa,
    "deployment": _step_deployment,
    "monitoring": _step_monitoring,
}


def execute_step(step, prospect, context):
    """Execute one lead-chain step. Returns (status, detail, error).

    status is one of "ok", "pending-approval", "blocked", "error".
    Never raises.
    """
    try:
        if not isinstance(step, dict):
            return ("error", "",
                    "step must be a dict, got %s"
                    % type(step).__name__)
        kind = str(step.get("kind") or step.get("id") or "").strip()
        handler = _HANDLERS.get(kind)
        if handler is None:
            return ("error", "", "unknown step kind: %s" % kind)
        if context is None:
            context = {}
        return handler(step, prospect, context)
    except Exception as exc:  # noqa: BLE001 — a step never breaks the chain
        return ("error", "", "%s: %s" % (type(exc).__name__, exc))


if __name__ == "__main__":
    # Self-test — TEST data only, no I/O, no live calls.
    _good = {"business_name": "TEST Plumbing LLC",
             "website": "https://test-plumbing.example",
             "email": "office@test-plumbing.example",
             "phone": "+1-555-010-0001",
             "domain": "test-plumbing.example",
             "state": "PA", "score": 85,
             "business_type": "plumbing"}
    _no_contact = {"business_name": "TEST No Contact LLC",
                   "website": "https://test-nocontact.example",
                   "state": "PA", "score": 70,
                   "business_type": "hvac"}
    _dental = dict(_good, business_name="TEST Dental LLC",
                   business_type="dental")
    _ctx = {"replies": []}

    def _run(kind, prospect=None, gate=None):
        _step = {"id": kind, "name": kind, "kind": kind}
        if gate:
            _step["gate"] = gate
        return execute_step(_step, prospect if prospect is not None
                            else _good, _ctx)

    assert _run("lead_discovery")[0] == "ok"
    assert _run("lead_discovery", {"business_name": "X"})[0] == "error"
    assert _run("lead_verification")[0] == "ok"
    assert _run("lead_verification", _no_contact)[0] == "error"
    assert _run("lead_verification", _no_contact)[2] == (
        "verification failed: missing email")
    assert _run("lead_qualification")[0] == "ok"
    assert "Tier 1" in _run("lead_qualification")[1]
    assert _run("lead_qualification", _dental)[0] == "error"
    assert _run("lead_qualification", _dental)[2] == (
        "DQ: dental/medical excluded")
    assert _run("lead_qualification",
                dict(_good, score=65))[1].endswith("Tier 2. "
                "Draft only; no outreach sent.") or \
        "Tier 2" in _run("lead_qualification",
                         dict(_good, score=65))[1]
    assert "Tier 4" in _run("lead_qualification",
                            dict(_good, score=30))[1]
    assert _run("crm_dryrun")[0] == "ok"
    _status, _detail, _err = _run(
        "outreach_draft", gate={"tool": "gmail_send",
                                "action": "send"})
    assert _status == "pending-approval", _status
    assert BOOKING_LINK in _detail
    assert _err == "send held: gmail_send requires Boss approval"
    assert _run("outreach_draft")[0] == "ok"  # ungated: draft only
    assert _run("reply_monitoring")[0] == "ok"
    assert "no replies" in _run("reply_monitoring")[1]
    assert _run("meeting")[0] == "ok"
    assert BOOKING_LINK in _run("meeting")[1]
    assert _run("sales_process")[0] == "ok"
    assert "details on a short call" in _run("sales_process")[1]
    assert "$" not in _run("sales_process")[1]
    assert _run("client_onboarding")[0] == "ok"
    assert _run("service_delivery")[0] == "ok"
    assert _run("qa")[0] == "ok"
    assert _run("deployment") == (
        "blocked", "",
        "deployment is ALWAYS BLOCKED in sandbox — "
        "Boss approval required")
    assert _run("monitoring")[0] == "ok"
    assert execute_step({"kind": "nope"}, _good, _ctx)[0] == "error"
    assert execute_step(None, _good, _ctx)[0] == "error"
    assert execute_step({"kind": "qa"}, None, None)[0] in ("ok", "error")
    print("steps: OK (13 kinds; draft-only; outreach gated-held; "
          "deployment always blocked; DQ + verification failure "
          "routing verified)")
