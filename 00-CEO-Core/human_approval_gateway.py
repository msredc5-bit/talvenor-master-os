"""Human Approval Gateway — REAL, working module (Phase 0).

The most important rule of the Talvenor Master OS is written in this file as code:
no gated work (send / publish / spend / delete) moves forward without Boss's exact gate word.
There is no auto-approve path — not even in the code.

Gate words (Boss's decision):
  ok       = plan / finished asset approval
  post it  = publish
  upload it = upload a video
  send     = send a message or email
  go       = advance a build phase

Usage:
  gw = ApprovalGateway()                       # reads store/approvals.json
  req = gw.request("send", "Day 4 batch - 25 emails", "OutreachDrafter")
  # If Boss says "send":
  gw.approve(req["id"], gate_word="send", decided_by="Boss")
  # If Boss says "no":
  gw.reject(req["id"], decided_by="Boss")
  gw.is_approved(req["id"])  # True only after approve()

Status: REAL (Phase 0). No mock — the decision is really written to approvals.json.
"""

import json
import os
import uuid
from datetime import datetime, timedelta, timezone

GATED_ACTIONS = ("send", "publish", "spend", "delete", "upload")

# Approval TTL — pending approvals expire after this many minutes.
# Recorded chat-card expiry is ~20 minutes (MEMORY.md: approval cards
# expire after about 20 minutes); the gateway mirrors that here so a
# pending approval cannot live forever. Expired records are refused
# by approve() and marked "expired" by sweep_expired().
APPROVAL_TTL_MINUTES = 20

# Gate word -> the action it approves
GATE_WORD_FOR_ACTION = {
    "send": ("send", "পাঠাও"),
    "publish": ("post it", "post all"),
    "spend": ("go",),          # spending needs separate explicit approval; "go" is only the word for advancing a phase
    "delete": ("go",),
    "upload": ("upload it",),
}

_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "store")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class ApprovalGateway:
    """Records approval for a gated action. No auto-approve."""

    def __init__(self, approvals_path=None):
        self.approvals_path = approvals_path or os.path.join(_STORE_DIR, "approvals.json")
        self._load()

    def _load(self):
        try:
            with open(self.approvals_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.records = data.get("records", []) if isinstance(data, dict) else []
        except (FileNotFoundError, json.JSONDecodeError):
            self.records = []

    def _save(self):
        payload = {
            "schema": "approvals-v1",
            "note": "Every gated action needs Boss's exact gate word. No auto-approve.",
            "records": self.records,
        }
        with open(self.approvals_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

    def request(self, action, detail, requested_by):
        """Ask for a new approval. Status always starts as 'pending'."""
        if action not in GATED_ACTIONS:
            raise ValueError(f"Unknown gated action: {action!r}. Allowed: {list(GATED_ACTIONS)}")
        record = {
            "id": uuid.uuid4().hex[:12],
            "action": action,
            "detail": detail,
            "requested_by": requested_by,
            "status": "pending",
            "requested_at": _now_iso(),
            "decided_by": None,
            "decided_at": None,
            "gate_word": None,
        }
        self.records.append(record)
        self._save()
        return dict(record)

    def approve(self, approval_id, gate_word, decided_by="Boss"):
        """When Boss approves — the gate word must match, otherwise ValueError.
        An expired record cannot be approved — sweep_expired() runs first,
        so an old pending expires on its own."""
        self.sweep_expired()
        record = self._find(approval_id)
        if record["status"] == "expired":
            raise ValueError(
                f"Approval {approval_id} expired (TTL "
                f"{APPROVAL_TTL_MINUTES} min) — ask Boss for a fresh approval.")
        if record["status"] != "pending":
            raise ValueError(f"Approval {approval_id} already decided: {record['status']}")
        allowed = GATE_WORD_FOR_ACTION[record["action"]]
        if gate_word not in allowed:
            raise ValueError(
                f"Gate word {gate_word!r} does not approve action {record['action']!r}. "
                f"Allowed: {list(allowed)}"
            )
        record["status"] = "approved"
        record["gate_word"] = gate_word
        record["decided_by"] = decided_by
        record["decided_at"] = _now_iso()
        self._save()
        return dict(record)

    def reject(self, approval_id, decided_by="Boss"):
        self.sweep_expired()
        record = self._find(approval_id)
        if record["status"] == "expired":
            raise ValueError(
                f"Approval {approval_id} already expired (TTL "
                f"{APPROVAL_TTL_MINUTES} min).")
        if record["status"] != "pending":
            raise ValueError(f"Approval {approval_id} already decided: {record['status']}")
        record["status"] = "rejected"
        record["decided_by"] = decided_by
        record["decided_at"] = _now_iso()
        self._save()
        return dict(record)

    def is_approved(self, approval_id):
        record = self._find(approval_id)
        return record["status"] == "approved"

    def pending(self):
        self.sweep_expired()
        return [dict(r) for r in self.records if r["status"] == "pending"]

    def sweep_expired(self):
        """Mark pending records past their TTL as "expired".

        TTL: APPROVAL_TTL_MINUTES from requested_at. Saves only if something
        changed; the file is not touched if nothing changed. Returns: the list
        of ids that expired."""
        now = datetime.now(timezone.utc)
        expired_ids = []
        for record in self.records:
            if record.get("status") != "pending":
                continue
            requested_at = record.get("requested_at")
            try:
                asked = datetime.fromisoformat(
                    str(requested_at).replace("Z", "+00:00"))
            except (TypeError, ValueError):
                continue  # if the timestamp cannot be read, it is not expired
            if now - asked > timedelta(minutes=APPROVAL_TTL_MINUTES):
                record["status"] = "expired"
                record["decided_at"] = now.isoformat()
                expired_ids.append(record["id"])
        if expired_ids:
            self._save()
        return expired_ids

    def _find(self, approval_id):
        for r in self.records:
            if r["id"] == approval_id:
                return r
        raise KeyError(f"No approval request with id {approval_id!r}")


if __name__ == "__main__":
    # Manual check: in-memory test, the real approvals.json is never touched.
    import tempfile

    tmp = os.path.join(tempfile.mkdtemp(), "approvals-test.json")
    gw = ApprovalGateway(approvals_path=tmp)
    req = gw.request("send", "test request", "check")
    assert gw.is_approved(req["id"]) is False
    try:
        gw.approve(req["id"], gate_word="ok")
        raise SystemExit("FAIL: wrong gate word was accepted")
    except ValueError:
        pass
    gw.approve(req["id"], gate_word="send")
    assert gw.is_approved(req["id"]) is True
    print("human_approval_gateway: OK (request -> wrong word rejected -> send approved)")
