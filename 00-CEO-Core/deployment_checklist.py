"""Deployment checklist — evaluate only, never execute (Phase 4).

Walks a tenant from schema-valid to ready-to-deploy as explicit
checks. Every step is one of:
  - "pass"         — the check ran and passed.
  - "fail"         — the check ran and failed (detail says why).
  - "blocked"      — cannot pass today: a live service or a Boss step
                     outside this repo is missing. The step lists the
                     exact missing input; it is never faked as passed.
  - "gate_missing" — needs Boss's gate word; the gate has not been
                     recorded yet.

Steps that need Boss's word are marked GATE. The checklist only
EVALUATES and reports — it deploys nothing, calls nothing, spends
nothing. A tenant is "ready" only when every step passes. With
today's reality (0 paying clients, no imported phone number, no
live brain proof) a tenant can NEVER be ready — the blocked steps
say so honestly instead of being skipped.

Gate recording: record_gate(gates, step_id, word, by="Boss") stores
one gate decision in a plain dict the caller owns. Gate words are
the standing ones: greeting approval needs "ok", booking-link
verification needs "ok", go-live needs "go". A wrong word for a
step is rejected, not recorded.

Stdlib only. No network, no send, no publish, no spend.
"""

import os
import sys
from datetime import datetime, timezone

here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import tenant_schema  # noqa: E402

BOOKING_LINK = "https://calendar.app.google/WLoxBfnLGTdjK3LB8"

# step_id -> gate word Boss must say (None = no gate word needed).
GATE_WORDS = {
    "greeting_approved": "ok",
    "booking_link_verified": "ok",
    "go_live": "go",
}

STEP_DEFS = (
    ("schema_valid", "Tenant config validates against tenant-v1",
     False),
    ("vapi_config_drafted", "Vapi assistant config drafted "
     "(model gpt-4o-mini, voice Emma, transcriber nova-3)", False),
    ("phone_number_assigned", "Phone number assigned to the tenant",
     False),
    ("booking_link_verified", "Booking link verified live", True),
    ("greeting_approved", "Greeting script approved by Boss", True),
    ("test_calls_passed", "Test calls passed", False),
    ("billing_confirmed", "Billing confirmed for a paying client",
     False),
    ("go_live", "Go-live gate (Boss's word)", True),
)


def record_gate(gates, step_id, word, by="Boss"):
    """Record one Boss gate decision in the caller's gates dict.

    Returns (recorded, reason). A wrong word for the step, or an
    unknown step, is rejected — never recorded.
    """
    if gates is None:
        gates = {}
    expected = GATE_WORDS.get(step_id)
    if expected is None:
        return False, "step '" + step_id + "' takes no gate word"
    if (word or "").strip().lower() != expected:
        return False, ("step '" + step_id + "' needs Boss's word '"
                       + expected + "', got '" + str(word) + "'")
    gates[step_id] = {
        "word": expected,
        "by": by,
        "at": datetime.now(timezone.utc).isoformat(),
    }
    return True, "recorded"


def _step(step_id, title, status, detail, gate=False):
    return {
        "id": step_id,
        "title": title,
        "status": status,
        "detail": detail,
        "gate": gate,
    }


def evaluate_checklist(tenant, gates=None):
    """Evaluate the deployment checklist for one tenant.

    Returns {ready, steps, blocked_by, gates_missing, tenant_id}.
    Pure evaluation — reads the tenant, runs the schema validator,
    builds the Vapi draft in memory. Writes nothing, calls nothing.
    """
    gates = gates or {}
    steps = []
    result = tenant_schema.validate_tenant(tenant)
    tenant_id = tenant.get("tenant_id") if isinstance(tenant, dict) else None

    # 1. Schema valid.
    if result["valid"]:
        steps.append(_step("schema_valid", STEP_DEFS[0][1], "pass",
                           "tenant config validates against tenant-v1"))
    else:
        steps.append(_step("schema_valid", STEP_DEFS[0][1], "fail",
                           "; ".join(result["errors"][:3])))

    # 2. Vapi assistant config drafted (structural check only).
    if result["valid"]:
        draft = tenant_schema.draft_vapi_assistant_config(tenant)
        cfg = draft.get("config") or {}
        ok = (draft["ok"] is True
              and cfg.get("model", {}).get("model") == "gpt-4o-mini"
              and cfg.get("voice", {}).get("voiceId") == "Emma"
              and cfg.get("transcriber", {}).get("model") == "nova-3"
              and bool(cfg.get("firstMessage"))
              and bool(cfg.get("systemPrompt")))
        steps.append(_step(
            "vapi_config_drafted", STEP_DEFS[1][1],
            "pass" if ok else "fail",
            "draft built in memory, never sent"
            if ok else "draft failed structural check"))
    else:
        steps.append(_step("vapi_config_drafted", STEP_DEFS[1][1],
                           "fail",
                           "cannot draft from an invalid tenant config"))

    # 3. Phone number assigned — BLOCKED (Twilio import is Boss's step).
    steps.append(_step(
        "phone_number_assigned", STEP_DEFS[2][1], "blocked",
        "Twilio number not imported — Boss's step; no number can be "
        "assigned from code, and no number is provisioned here"))

    # 4. Booking link verified live — GATE (Boss checks it in a browser).
    link = None
    if isinstance(tenant, dict):
        link = (tenant.get("booking") or {}).get("calendar_link")
    if "booking_link_verified" in gates:
        steps.append(_step("booking_link_verified", STEP_DEFS[3][1],
                           "pass",
                           "Boss verified the link loads",
                           gate=True))
    elif isinstance(link, str) and link.startswith("https://"):
        steps.append(_step(
            "booking_link_verified", STEP_DEFS[3][1], "gate_missing",
            "link is a valid https URL but Boss has not verified it "
            "loads live yet — code never fetches it",
            gate=True))
    else:
        steps.append(_step("booking_link_verified", STEP_DEFS[3][1],
                           "fail",
                           "booking.calendar_link is missing or not an "
                           "https URL",
                           gate=True))

    # 5. Greeting approved — GATE.
    if "greeting_approved" in gates:
        steps.append(_step("greeting_approved", STEP_DEFS[4][1], "pass",
                           "Boss approved the greeting script",
                           gate=True))
    else:
        steps.append(_step("greeting_approved", STEP_DEFS[4][1],
                           "gate_missing",
                           "greeting script needs Boss's 'ok'",
                           gate=True))

    # 6. Test calls passed — BLOCKED (needs a live number + live brain).
    steps.append(_step(
        "test_calls_passed", STEP_DEFS[5][1], "blocked",
        "test calls need a live phone number and a proven live brain "
        "— neither exists yet; no test call is placed from code"))

    # 7. Billing confirmed — BLOCKED (0 paying clients).
    confirmed = False
    if isinstance(tenant, dict):
        confirmed = bool(
            (tenant.get("billing") or {}).get("paying_client_confirmed"))
    if confirmed:
        steps.append(_step("billing_confirmed", STEP_DEFS[6][1], "pass",
                           "paying client confirmed"))
    else:
        steps.append(_step(
            "billing_confirmed", STEP_DEFS[6][1], "blocked",
            "0 paying clients — BillingInvoiceAgent refuses any "
            "invoice unless paying_client_confirmed is True"))

    # 8. Go-live gate — GATE.
    if "go_live" in gates:
        steps.append(_step("go_live", STEP_DEFS[7][1], "pass",
                           "Boss said 'go'", gate=True))
    else:
        steps.append(_step("go_live", STEP_DEFS[7][1], "gate_missing",
                           "go-live needs Boss's 'go'", gate=True))

    ready = all(s["status"] == "pass" for s in steps)
    return {
        "ready": ready,
        "steps": steps,
        "blocked_by": [s["id"] for s in steps
                       if s["status"] == "blocked"],
        "gates_missing": [s["id"] for s in steps
                          if s["status"] == "gate_missing"],
        "failed": [s["id"] for s in steps if s["status"] == "fail"],
        "tenant_id": tenant_id,
    }


if __name__ == "__main__":
    # Self-test — pure evaluation, no store, no network, no send.
    tenant = tenant_schema.synthetic_tenant()
    report = evaluate_checklist(tenant)
    assert report["ready"] is False
    by_id = {s["id"]: s for s in report["steps"]}
    assert by_id["schema_valid"]["status"] == "pass"
    assert by_id["vapi_config_drafted"]["status"] == "pass"
    assert by_id["phone_number_assigned"]["status"] == "blocked"
    assert by_id["test_calls_passed"]["status"] == "blocked"
    assert by_id["billing_confirmed"]["status"] == "blocked"
    assert by_id["greeting_approved"]["status"] == "gate_missing"
    assert by_id["go_live"]["status"] == "gate_missing"
    assert report["blocked_by"] == ["phone_number_assigned",
                                    "test_calls_passed",
                                    "billing_confirmed"]
    gates = {}
    ok, _ = record_gate(gates, "greeting_approved", "nope")
    assert ok is False and "greeting_approved" not in gates
    ok, _ = record_gate(gates, "greeting_approved", "ok")
    assert ok is True
    ok, _ = record_gate(gates, "go_live", "ok")
    assert ok is False  # go-live needs "go", not "ok"
    ok, _ = record_gate(gates, "go_live", "go")
    assert ok is True
    ok, _ = record_gate(gates, "booking_link_verified", "ok")
    assert ok is True
    report = evaluate_checklist(tenant, gates)
    assert report["ready"] is False  # blocked steps remain
    assert report["gates_missing"] == []
    bad = tenant_schema.synthetic_tenant()
    del bad["business"]["phone"]
    report = evaluate_checklist(bad)
    assert report["steps"][0]["status"] == "fail"
    assert report["steps"][1]["status"] == "fail"
    print("deployment_checklist: OK (synthetic tenant: schema+vapi "
          "pass, phone/test-calls/billing blocked, gates missing "
          "until recorded; ready stays False)")
