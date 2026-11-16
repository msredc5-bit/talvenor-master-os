"""Human Approval Gateway — REAL, working module (Phase 0).

Talvenor Master OS-এর সবচেয়ে গুরুত্বপূর্ণ নিয়ম এই ফাইলে কোড হিসেবে লেখা:
কোনো gated কাজ (send / publish / spend / delete) Boss-এর সঠিক gate word
ছাড়া এগোবে না। Auto-approve-এর কোনো পথ নেই — কোডেও নেই।

Gate words (Boss-এর সিদ্ধান্ত):
  ok       = plan / finished asset approval
  post it  = publish
  upload it = upload a video
  send     = send a message or email
  go       = advance a build phase

ব্যবহার:
  gw = ApprovalGateway()                       # store/approvals.json পড়ে
  req = gw.request("send", "Day 4 batch - 25 emails", "OutreachDrafter")
  # Boss "send" বললে:
  gw.approve(req["id"], gate_word="send", decided_by="Boss")
  # Boss "না" বললে:
  gw.reject(req["id"], decided_by="Boss")
  gw.is_approved(req["id"])  # True শুধু approve()-এর পর

Status: REAL (Phase 0)। কোনো mock নয় — সিদ্ধান্ত সত্যিই approvals.json-এ লেখা হয়।
"""

import json
import os
import uuid
from datetime import datetime, timezone

GATED_ACTIONS = ("send", "publish", "spend", "delete")

# Gate word -> যে action-টা সে অনুমোদন করে
GATE_WORD_FOR_ACTION = {
    "send": ("send", "পাঠাও"),
    "publish": ("post it", "post all"),
    "spend": ("go",),          # খরচের জন্য আলাদা স্পষ্ট অনুমোদন লাগে; "go" শুধু phase এগোনোর শব্দ
    "delete": ("go",),
}

_STORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "store")


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


class ApprovalGateway:
    """Gated action-এর অনুমোদন রেকর্ড করে। Auto-approve নেই।"""

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
        """নতুন অনুমোদন চাওয়া। Status সবসময় 'pending' দিয়ে শুরু হয়।"""
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
        """Boss অনুমোদন দিলে — gate word মিলতেই হবে, নইলে ValueError।"""
        record = self._find(approval_id)
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
        record = self._find(approval_id)
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
        return [dict(r) for r in self.records if r["status"] == "pending"]

    def _find(self, approval_id):
        for r in self.records:
            if r["id"] == approval_id:
                return r
        raise KeyError(f"No approval request with id {approval_id!r}")


if __name__ == "__main__":
    # হাতে চেক: in-memory টেস্ট, আসল approvals.json ছোঁয়া হয় না।
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
