"""Follow-up queue — structured follow-up tasks (Phase 3, Unified OS).

Builds follow-up task records in the Phase 1 task-orchestrator shape
(tasks-v1: id, status, business, type, title, payload, queued_at,
priority, depends_on, retries, max_retries, cancelled,
idempotency_key, last_error).

Boss's standing 100-mail rule (2026-11-10, mandatory): NO follow-up
for a state until that state has 100 first mails complete. The count
is read from the lead store (store/leads.json) — never hardcoded.
Today NO state is at 100 (PA 39, FL 54, GA 16, TX 15, CA 15, IL 9,
MI 5, NC 5, NY 4, OH 1; FL's ceiling is 99 unique leads, so FL can
never reach 100 from the current pool) — so build_followup_queue()
returns an EMPTY queue and one refusal per requested state, each with
its reason recorded.

Rules:
  - This module RETURNS records; it never writes to any store. The
    caller decides where to persist them (tests use TEMP dirs; the
    real store only ever gains follow-up tasks when Boss's rule is met
    AND the email restart has happened).
  - A lead is only eligible when: it was emailed, it carries NO
    blocking flag (BOUNCED_DEAD_ADDRESS, NEVER_REMAIL_DOUBLE_SENT,
    HELD_DO_NOT_CONTACT, HELD_LOW_CONFIDENCE, OTHER_CHANNEL_CONTACTED),
    and its state's first-mail count is >= 100.
  - Every record is a DRAFT task (status "queued", type "followup") —
    the follow-up itself is a draft; sending it needs Boss's "send"
    through the trust gate + ApprovalGateway. Email is PAUSED since
    2026-11-14.
  - Idempotency: idempotency_key = "followup:<lead-id>:<state>" — a
    second build for the same lead returns the same key, so the
    orchestrator's duplicate handling (Phase 1) can reject it.
  - Stdlib only. No network, no send, no publish, no spend.
"""

import hashlib
import os
import sys
from datetime import datetime, timezone

here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import lead_store  # noqa: E402

FOLLOWUP_THRESHOLD_PER_STATE = lead_store.FOLLOWUP_THRESHOLD_PER_STATE

BLOCKING_FLAGS = (
    "BOUNCED_DEAD_ADDRESS",
    "NEVER_REMAIL_DOUBLE_SENT",
    "HELD_DO_NOT_CONTACT",
    "HELD_LOW_CONFIDENCE",
    "OTHER_CHANNEL_CONTACTED",
)

QUEUE_TASK_TYPE = "followup"


def _task_id(lead_id, state):
    """Deterministic task id (stable across rebuilds)."""
    digest = hashlib.sha256(
        ("followup:%s:%s" % (lead_id, state)).encode("utf-8")).hexdigest()
    return "fu-" + digest[:12]


def eligible_leads_for_state(state, leads_path=None):
    """Emailed, unblocked leads in a state — the follow-up candidates.

    Returns (candidates, blocked) where blocked is a list of
    (lead_id, reason) for emailed leads that cannot be followed up.
    A state with no emailed leads returns ([], []).
    """
    state = (state or "").strip().upper()
    candidates = []
    blocked = []
    for lead in lead_store.leads(leads_path):
        if (lead.get("state") or "").strip().upper() != state:
            continue
        sent = lead.get("sent") or {}
        if sent.get("emailed") is not True:
            continue
        hit = [f for f in (lead.get("flags") or [])
               if f in BLOCKING_FLAGS]
        if hit:
            blocked.append((lead.get("id"), "blocking flag: "
                            + ", ".join(sorted(hit))))
        else:
            candidates.append(lead)
    return candidates, blocked


def build_followup_queue(states=None, leads_path=None):
    """Build the follow-up queue for the given states (default: all).

    Returns {"queue": [task records], "refusals": [refusal dicts]}.
    A refusal records: state, first_mails, threshold, reason, and (when
    the state IS at threshold) the blocked leads that were skipped.
    Today every state refuses — the queue is empty by rule, not by bug.
    """
    if states is None:
        states = sorted(lead_store.first_mails_by_state(leads_path).keys())
    queue = []
    refusals = []
    counts = lead_store.first_mails_by_state(leads_path)
    for state in states:
        state = (state or "").strip().upper()
        if not state:
            continue
        count = counts.get(state, 0)
        candidates, blocked = eligible_leads_for_state(state, leads_path)
        if count < FOLLOWUP_THRESHOLD_PER_STATE:
            refusals.append({
                "state": state,
                "first_mails": count,
                "threshold": FOLLOWUP_THRESHOLD_PER_STATE,
                "reason": ("100-mail rule: %s first mails = %d, below "
                           "threshold %d — no follow-up for this state"
                           % (state, count, FOLLOWUP_THRESHOLD_PER_STATE)),
                "candidates_parked": len(candidates),
                "blocked_skipped": len(blocked),
            })
            continue
        # At threshold: queue the eligible leads, record the blocked ones.
        for lead in candidates:
            lead_id = lead.get("id")
            queue.append({
                "id": _task_id(lead_id, state),
                "status": "queued",
                "business": "agency",
                "type": QUEUE_TASK_TYPE,
                "title": ("Follow-up draft for %s (%s)"
                          % (lead.get("business_name"), state)),
                "payload": {
                    "prospect": lead.get("business_name"),
                    "state": state,
                    "lead_id": lead_id,
                    "email": lead.get("email"),
                    "phone": lead.get("phone"),
                },
                "queued_at": datetime.now(timezone.utc).isoformat(),
                "priority": 5,
                "depends_on": [],
                "retries": 0,
                "max_retries": 3,
                "cancelled": False,
                "idempotency_key": "followup:%s:%s" % (lead_id, state),
                "last_error": None,
                "draft_only": True,
            })
        if blocked:
            refusals.append({
                "state": state,
                "first_mails": count,
                "threshold": FOLLOWUP_THRESHOLD_PER_STATE,
                "reason": ("%d emailed lead(s) skipped: blocking flag"
                           % len(blocked)),
                "candidates_parked": 0,
                "blocked_skipped": len(blocked),
                "blocked": [{"lead_id": lid, "reason": why}
                            for lid, why in blocked],
            })
    return {"queue": queue, "refusals": refusals}


if __name__ == "__main__":
    # Self-test — reads the real lead store, writes nothing.
    result = build_followup_queue()
    assert result["queue"] == [], result["queue"]
    refused = {r["state"]: r for r in result["refusals"]}
    assert refused["PA"]["first_mails"] == 39
    assert refused["FL"]["first_mails"] == 54
    assert refused["PA"]["candidates_parked"] > 0
    assert all(r["first_mails"] < 100 for r in result["refusals"])
    # Eligibility honours blocking flags: PA has 39 mailed, of which the
    # double-sent (Metz, AAA) are blocked, not candidates.
    cands, blocked = eligible_leads_for_state("PA")
    blocked_ids = {lid for lid, _ in blocked}
    assert len(blocked) >= 2, blocked
    assert len(cands) > 0
    assert not any(set(c.get("flags") or []) & set(BLOCKING_FLAGS)
                   for c in cands)
    # The two double-sent PA leads are among the blocked, never candidates.
    cand_ids = {c["id"] for c in cands}
    assert not (blocked_ids & cand_ids)
    # A synthetic store at threshold queues eligible leads only.
    import json
    import tempfile
    tmp = os.path.join(tempfile.mkdtemp(), "leads.json")
    store = {
        "schema": "leads-v1",
        "meta": {},
        "leads": [
            {"id": "L-0001", "business_name": "Test Plumbing",
             "state": "ZZ", "email": "a@test.example", "phone": "",
             "domain": "test.example", "phone_norm": "",
             "sent": {"emailed": True}, "flags": []},
            {"id": "L-0002", "business_name": "Bounced Plumbing",
             "state": "ZZ", "email": "b@test.example", "phone": "",
             "domain": "bounced.example", "phone_norm": "",
             "sent": {"emailed": True},
             "flags": ["BOUNCED_DEAD_ADDRESS"]},
        ] + [
            {"id": "L-%04d" % (10 + i), "business_name": "Filler %d" % i,
             "state": "ZZ", "email": "", "phone": "",
             "domain": "filler%d.example" % i, "phone_norm": "",
             "sent": {"emailed": True}, "flags": []}
            for i in range(99)
        ],
    }
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(store, f)
    # 101 mailed in ZZ (1 + 1 + 99) -> at threshold.
    assert lead_store.first_mails_for_state("ZZ", tmp) == 101
    out = build_followup_queue(["ZZ"], tmp)
    assert len(out["queue"]) == 100, len(out["queue"])
    assert out["queue"][0]["type"] == "followup"
    assert out["queue"][0]["draft_only"] is True
    assert out["queue"][0]["idempotency_key"].startswith("followup:L-")
    assert all(t["status"] == "queued" for t in out["queue"])
    assert out["queue"][0]["id"] == _task_id("L-0001", "ZZ")
    assert len(out["refusals"]) == 1  # the bounced lead, skipped
    assert out["refusals"][0]["blocked_skipped"] == 1
    # Idempotency: rebuilding gives the same keys.
    out2 = build_followup_queue(["ZZ"], tmp)
    assert [t["idempotency_key"] for t in out2["queue"]] == \
        [t["idempotency_key"] for t in out["queue"]]
    print("followup_queue: OK (100-mail rule refuses all 10 real states "
          "today; synthetic 101-mail state queues 100 eligible, skips "
          "the bounced lead; idempotency keys stable)")
