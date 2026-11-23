"""CRM adapter — dry-run only (Phase 3, Unified OS).

The CRM is n8n Data Tables, fed by the Tier-2 auto-send workflow
(``~/workspace/talvenor-outreach/n8n-workflow-tier2-auto-send.json``,
active: false) and the Sheet queue
(``1SZjkPZfpGjHUBIWp9-bnYVhKuFaxXAgC_wOMlpfv4MM``). Neither is live:
the workflow is not imported, the Sheet is not connected, and no
credential for either exists in this repo.

This adapter therefore:
  - health() reports NOT CONNECTED until a real check passes. No real
    check exists yet, so health is NOT CONNECTED by construction.
  - Every write method is DRY-RUN: it validates the payload, builds
    the EXACT payload that WOULD be sent to the CRM, and returns it.
    It writes nothing anywhere — no Sheet call, no n8n call, no file,
    no network. There is no live code path in this module at all
    (no urllib, no requests, no subprocess).
  - A live adapter can only be added after: the n8n workflow is
    imported (Boss's step), the Sheet is connected, and a successful
    health check passes. Until then, any caller that needs a live
    write must fail loudly instead of pretending.

Payload shape (what WOULD be sent):
  {"table": "leads", "action": "upsert", "key": {"domain": ...},
   "fields": {...}} — one record per lead, keyed by domain (fallback
   phone). Reply events go to table "replies" with the triage verdict.

Stdlib only. No network, no send, no publish, no spend.
"""

import json
import os

WORKFLOW_FILE = ("~/workspace/talvenor-outreach/"
                 "n8n-workflow-tier2-auto-send.json")
SHEET_QUEUE_ID = "1SZjkPZfpGjHUBIWp9-bnYVhKuFaxXAgC_wOMlpfv4MM"

HEALTH_NOT_CONNECTED = "NOT CONNECTED"


def health():
    """CRM health — always NOT CONNECTED until a real check passes.

    Returns {"status": "NOT CONNECTED", "reason": ..., "live": False}.
    The reason names the concrete blockers (workflow not imported,
    Sheet not connected, no credential). There is no code path that
    can return a live status today.
    """
    return {
        "status": HEALTH_NOT_CONNECTED,
        "live": False,
        "reason": ("n8n workflow not imported (active: false); Sheet "
                   "queue %s not connected; no CRM credential in the "
                   "repo. Dry-run only." % SHEET_QUEUE_ID),
        "workflow": WORKFLOW_FILE,
        "sheet_queue_id": SHEET_QUEUE_ID,
    }


def _require_lead_shape(lead):
    if not isinstance(lead, dict):
        raise ValueError("lead must be a dict")
    for field in ("business_name", "state"):
        if not lead.get(field):
            raise ValueError("lead is missing %r" % field)
    if not (lead.get("domain") or lead.get("phone_norm")):
        raise ValueError("lead has neither domain nor phone — no CRM key")


def lead_upsert_payload(lead):
    """The exact payload that WOULD upsert one lead. Writes nothing.

    Returns {"dry_run": True, "table": "leads", "action": "upsert",
    "key": {...}, "fields": {...}}. Raises ValueError on a bad lead.
    """
    _require_lead_shape(lead)
    key = {}
    if lead.get("domain"):
        key["domain"] = lead["domain"]
    else:
        key["phone"] = lead.get("phone_norm")
    sent = lead.get("sent") or {}
    fields = {
        "business_name": lead.get("business_name"),
        "city": lead.get("city"),
        "state": lead.get("state"),
        "website": lead.get("website"),
        "email": lead.get("email"),
        "phone": lead.get("phone"),
        "score": lead.get("score"),
        "tier": lead.get("tier"),
        "source": lead.get("source"),
        "emailed": bool(sent.get("emailed")),
        "sent_date": sent.get("sent_date"),
        "flags": sorted(lead.get("flags") or []),
    }
    return {"dry_run": True, "table": "leads", "action": "upsert",
            "key": key, "fields": fields}


def reply_event_payload(triage_verdict, lead_id=None):
    """The exact payload that WOULD log one triaged reply. Writes nothing.

    triage_verdict is a reply_triage.triage() dict. Raises ValueError
    when the verdict is not a dict with a "verdict" key.
    """
    if not isinstance(triage_verdict, dict) or "verdict" not in triage_verdict:
        raise ValueError("triage_verdict must be a triage() dict")
    return {
        "dry_run": True,
        "table": "replies",
        "action": "insert",
        "key": {"lead_id": lead_id},
        "fields": {
            "channel": triage_verdict.get("channel"),
            "sender": triage_verdict.get("sender"),
            "verdict": triage_verdict.get("verdict"),
            "excerpt": triage_verdict.get("excerpt"),
            "draft": triage_verdict.get("draft"),
            "reason": triage_verdict.get("reason"),
        },
    }


def batch_upsert_payloads(leads):
    """Dry-run payloads for a list of leads (validates each)."""
    return [lead_upsert_payload(lead) for lead in leads]


if __name__ == "__main__":
    # Self-test — pure data shaping, no I/O at all.
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import lead_store
    import reply_triage

    h = health()
    assert h["status"] == "NOT CONNECTED" and h["live"] is False
    assert h["sheet_queue_id"] == SHEET_QUEUE_ID

    lead = lead_store.find_by_domain("https://www.ugihvac.com/")
    assert lead is not None
    payload = lead_upsert_payload(lead)
    assert payload["dry_run"] is True
    assert payload["table"] == "leads" and payload["action"] == "upsert"
    assert payload["key"] == {"domain": "ugihvac.com"}
    assert payload["fields"]["business_name"].startswith("UGI")
    assert payload["fields"]["emailed"] is True
    assert json.dumps(payload)  # serializable — it IS the would-be body

    verdict = reply_triage.triage(
        "gmail", "joe@plumbing.example",
        "Sounds good — how much does it cost?", sender_name="Joe")
    event = reply_event_payload(verdict, lead_id=lead["id"])
    assert event["dry_run"] is True and event["table"] == "replies"
    assert event["fields"]["verdict"] == "hot_lead"
    assert "$" not in (event["fields"]["draft"] or "")

    try:
        lead_upsert_payload({"business_name": "No State"})
        raise SystemExit("FAIL: bad lead did not raise")
    except ValueError:
        pass
    try:
        lead_upsert_payload({"business_name": "X", "state": "PA"})
        raise SystemExit("FAIL: keyless lead did not raise")
    except ValueError:
        pass
    try:
        reply_event_payload({"no": "verdict"})
        raise SystemExit("FAIL: bad verdict did not raise")
    except ValueError:
        pass
    # The module imports no network library at all.
    import re as _re
    import crm_adapter
    source = open(crm_adapter.__file__, encoding="utf-8").read()
    imported = set(_re.findall(r"^(?:import|from)\s+([\w\.]+)",
                               source, _re.MULTILINE))
    for banned in ("urllib", "requests", "http", "subprocess", "socket"):
        assert banned not in imported, banned
    print("crm_adapter: OK (health NOT CONNECTED; dry-run payloads only, "
          "validated, serializable; no network import)")
