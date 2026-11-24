"""Approval centre — Phase 7 (Worker C).

The operator-facing front end for the ApprovalGateway
(00-CEO-Core/human_approval_gateway.py). This module NEVER writes
approvals.json directly — every decision goes through the gateway's
own methods (the gateway's _save is the only writer). Wrong gate
word, expired record, or already-decided record raises the gateway's
own error — never swallowed, never auto-retried.

Why a centre on top of scripts/approve.py (which already wraps the
gateway)? approve.py is a flag-style operator script (--list /
--approve ID --word WORD). The centre is the importable API the
Founder Dashboard + CEO report use (list_pending with age/expiry,
request_approval, decide) plus a thin subcommand CLI
(scripts/approval_centre.py: list / approve <id> <gate-word> /
reject <id>). No gateway logic is duplicated here — approve.py's
behaviour is preserved, this module just gives it a stable API.

API:
  centre = ApprovalCentre(approvals_path=None)   # default: real store
  centre.list_pending()        -> pending records with age/expiry
  centre.request_approval("send", "Day 4 batch", "OutreachDrafter")
  centre.decide(id, "approve", gate_word="send")   # decided_by="Boss"
  centre.decide(id, "reject")

Module-level helpers (same behaviour, explicit gateway):
  list_pending(gateway) -> [...]
  request_approval(action, detail, requested_by, gateway=None,
                   approvals_path=None)
  decide(approval_id, decision, gate_word=None, decided_by="Boss",
         gateway=None, approvals_path=None)

Approval decisions are Boss-only: decided_by defaults to "Boss".
Stdlib only. No network, no send, no publish, no spend, no delete.
"""

import os
from datetime import datetime, timezone

try:
    from human_approval_gateway import (  # noqa: E402
        APPROVAL_TTL_MINUTES,
        GATE_WORD_FOR_ACTION,
        ApprovalGateway,
    )
except ImportError:  # direct script run from another directory
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from human_approval_gateway import (  # noqa: E402
        APPROVAL_TTL_MINUTES,
        GATE_WORD_FOR_ACTION,
        ApprovalGateway,
    )

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_APPROVALS_PATH = os.path.join(_MASTER_OS_DIR, "store",
                                      "approvals.json")


def _age_minutes(record):
    """Minutes since the record was requested, or None when the
    timestamp cannot be read."""
    try:
        asked = datetime.fromisoformat(
            str(record.get("requested_at")).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - asked).total_seconds() / 60.0
    except (TypeError, ValueError):
        return None


def _enrich(record):
    """One gateway record + the centre's age/expiry view. Read-only —
    the record itself is never mutated."""
    age = _age_minutes(record)
    expired = (record.get("status") == "pending" and age is not None
               and age > APPROVAL_TTL_MINUTES)
    expires_in = (APPROVAL_TTL_MINUTES - age) if age is not None else None
    return {
        "id": record.get("id"),
        "action": record.get("action"),
        "detail": record.get("detail"),
        "requested_by": record.get("requested_by"),
        "status": record.get("status"),
        "requested_at": record.get("requested_at"),
        "age_minutes": round(age, 1) if age is not None else None,
        "expires_in_minutes": round(expires_in, 1)
        if expires_in is not None else None,
        "expired": expired,
        "ttl_minutes": APPROVAL_TTL_MINUTES,
        "allowed_gate_words": list(
            GATE_WORD_FOR_ACTION.get(record.get("action"), ())),
        "decided_by": record.get("decided_by"),
        "decided_at": record.get("decided_at"),
        "gate_word": record.get("gate_word"),
    }


def _gateway_or_default(gateway, approvals_path):
    if gateway is not None:
        return gateway
    return ApprovalGateway(
        approvals_path=approvals_path or DEFAULT_APPROVALS_PATH)


def list_pending(gateway):
    """Pending approvals via the REAL gateway (its pending() sweeps
    expired records first, through the gateway's own writer).
    Returns enriched records with age/expiry — see _enrich."""
    return [_enrich(r) for r in gateway.pending()]


def request_approval(action, detail, requested_by, gateway=None,
                     approvals_path=None):
    """Ask for a new approval — straight through to gateway.request.
    The gateway validates the action and writes the record."""
    gw = _gateway_or_default(gateway, approvals_path)
    return gw.request(action, detail, requested_by)


def decide(approval_id, decision, gate_word=None, decided_by="Boss",
           gateway=None, approvals_path=None):
    """Decide one approval — straight through to the gateway.

    decision "approve" -> gateway.approve(approval_id, gate_word,
    decided_by); decision "reject" -> gateway.reject(approval_id,
    decided_by). Anything else raises ValueError. The gateway's own
    errors (wrong gate word, expired record, already decided, unknown
    id) propagate unchanged — never swallowed, never auto-retried.
    decided_by defaults to "Boss": approval decisions are Boss-only.
    """
    gw = _gateway_or_default(gateway, approvals_path)
    if decision == "approve":
        return gw.approve(approval_id, gate_word=gate_word,
                          decided_by=decided_by)
    if decision == "reject":
        return gw.reject(approval_id, decided_by=decided_by)
    raise ValueError(
        f"Unknown decision {decision!r}. Allowed: 'approve', 'reject'.")


class ApprovalCentre:
    """The approval centre bound to one approvals file (default: the
    real store/approvals.json). All reads/writes go through the
    ApprovalGateway — this class never touches approvals.json itself."""

    def __init__(self, approvals_path=None, gateway=None):
        if gateway is not None:
            self.gateway = gateway
        else:
            self.gateway = ApprovalGateway(
                approvals_path=approvals_path or DEFAULT_APPROVALS_PATH)
        self.approvals_path = self.gateway.approvals_path

    def list_pending(self):
        """Pending approvals with age/expiry (see list_pending)."""
        return list_pending(self.gateway)

    def list_all(self):
        """All records (pending + decided) with age/expiry."""
        return [_enrich(r) for r in self.gateway.records]

    def request_approval(self, action, detail, requested_by):
        """Ask for a new approval — gateway.request."""
        return self.gateway.request(action, detail, requested_by)

    def decide(self, approval_id, decision, gate_word=None,
               decided_by="Boss"):
        """Decide one approval — gateway.approve / gateway.reject."""
        return decide(approval_id, decision, gate_word=gate_word,
                      decided_by=decided_by, gateway=self.gateway)

    def approve(self, approval_id, gate_word, decided_by="Boss"):
        """Approve one approval — gateway.approve (gate word checked
        by the gateway)."""
        return self.gateway.approve(approval_id, gate_word=gate_word,
                                    decided_by=decided_by)

    def reject(self, approval_id, decided_by="Boss"):
        """Reject one approval — gateway.reject."""
        return self.gateway.reject(approval_id, decided_by=decided_by)


if __name__ == "__main__":
    # Manual check — TEMP file only, the real store is never touched.
    import tempfile

    tmp = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
    centre = ApprovalCentre(approvals_path=tmp)
    req = centre.request_approval("send", "test request", "check")
    assert req["status"] == "pending"
    pending = centre.list_pending()
    assert len(pending) == 1 and pending[0]["id"] == req["id"]
    assert pending[0]["age_minutes"] is not None
    assert pending[0]["expires_in_minutes"] is not None
    assert pending[0]["allowed_gate_words"] == ["send", "পাঠাও"]
    assert pending[0]["expired"] is False
    try:
        centre.decide(req["id"], "approve", gate_word="ok")
        raise SystemExit("FAIL: wrong gate word was accepted")
    except ValueError:
        pass
    try:
        centre.decide(req["id"], "maybe")
        raise SystemExit("FAIL: unknown decision was accepted")
    except ValueError:
        pass
    out = centre.decide(req["id"], "approve", gate_word="send")
    assert out["status"] == "approved" and out["decided_by"] == "Boss"
    assert centre.list_pending() == []
    req2 = centre.request_approval("publish", "test 2", "check")
    out2 = centre.decide(req2["id"], "reject")
    assert out2["status"] == "rejected"
    print("approval_centre: OK (request -> list_pending with age/expiry "
          "-> wrong word rejected -> send approved -> reject recorded; "
          "gateway is the only writer)")
