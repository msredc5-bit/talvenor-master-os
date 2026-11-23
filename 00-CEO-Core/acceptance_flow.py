"""Tenant acceptance flow — structured, fail-closed (Phase 4).

One acceptance record walks a tenant through:
  intake -> schema_check -> checklist -> qa -> boss_acceptance
  -> deploy (ALWAYS BLOCKED).

Each advance() call completes the CURRENT stage and moves to the
next one — or refuses to move, with the reason recorded:
  - schema_check refuses when the tenant fails validation.
  - checklist refuses when the evaluable steps (schema valid, Vapi
    draft built) fail. Blocked steps (phone number, test calls,
    billing) and missing gates are RECORDED as outstanding — they
    do not fail the stage, because no tenant can clear them today.
  - qa refuses when the QA verdict is "fail".
  - boss_acceptance refuses until Boss's "ok" is recorded.
  - deploy ALWAYS refuses: live deployment is manual — Boss
    executes it himself. No deploy path exists anywhere in this
    repo, and this module contains none.

The record is tasks-v1-shaped (id, status, business, type, title,
payload, created_at) plus stage / steps / history. It lives in
memory; save_record()/load_record() persist it through store_io
(atomic + locked) to a caller-chosen path — tests use TEMP dirs,
never the real store.

Stdlib only. No network, no send, no publish, no spend.
"""

import os
import sys
from datetime import datetime, timezone

here = os.path.dirname(os.path.abspath(__file__))
if here not in sys.path:
    sys.path.insert(0, here)

import deployment_checklist  # noqa: E402
import tenant_qa  # noqa: E402
import tenant_schema  # noqa: E402

STAGES = (
    "intake",
    "schema_check",
    "checklist",
    "qa",
    "boss_acceptance",
    "deploy",
)

BOSS_ACCEPTANCE_WORD = "ok"


def _now():
    return datetime.now(timezone.utc).isoformat()


def new_acceptance(tenant_id):
    """Start a fresh acceptance record for one tenant."""
    record = {
        "id": "acc-" + str(tenant_id),
        "type": "tenant_acceptance",
        "business": "talvenor",
        "title": "Tenant acceptance — " + str(tenant_id),
        "payload": {"tenant_id": tenant_id},
        "stage": "intake",
        "status": "in_progress",
        "deploy": "BLOCKED",
        "created_at": _now(),
        "steps": {stage: {"status": "pending", "detail": "",
                          "at": None} for stage in STAGES},
        "history": [],
    }
    return record


def record_boss_acceptance(gates, word, by="Boss"):
    """Record Boss's acceptance ("ok") in the caller's gates dict.

    Returns (recorded, reason). Any other word is rejected.
    """
    if gates is None:
        gates = {}
    if (word or "").strip().lower() != BOSS_ACCEPTANCE_WORD:
        return False, ("boss acceptance needs Boss's word 'ok', got '"
                       + str(word) + "'")
    gates["boss_acceptance"] = {
        "word": BOSS_ACCEPTANCE_WORD,
        "by": by,
        "at": _now(),
    }
    return True, "recorded"


def _set_step(record, stage, status, detail):
    record["steps"][stage] = {
        "status": status,
        "detail": detail,
        "at": _now(),
    }
    record["history"].append({
        "stage": stage,
        "result": status,
        "detail": detail,
        "at": _now(),
    })


def advance(record, tenant=None, gates=None, script=None):
    """Try to complete the record's current stage and move on.

    Returns (record, moved, reason). moved is False whenever the
    stage refuses to complete — the record stays at that stage with
    the failure recorded. The deploy stage never moves.
    """
    gates = gates or {}
    stage = record.get("stage")

    if stage == "intake":
        if not isinstance(tenant, dict):
            _set_step(record, "intake", "failed",
                      "no tenant config given")
            return record, False, "intake needs a tenant config"
        if tenant.get("tenant_id") != record.get("payload", {}).get(
                "tenant_id"):
            _set_step(record, "intake", "failed",
                      "tenant_id does not match the record")
            return record, False, "tenant_id does not match the record"
        _set_step(record, "intake", "passed",
                  "tenant config received: " + str(tenant["tenant_id"]))
        record["stage"] = "schema_check"
        return record, True, "intake passed"

    if stage == "schema_check":
        if not isinstance(tenant, dict):
            _set_step(record, "schema_check", "failed",
                      "no tenant config given")
            return record, False, "schema_check needs a tenant config"
        result = tenant_schema.validate_tenant(tenant)
        if not result["valid"]:
            _set_step(record, "schema_check", "failed",
                      "; ".join(result["errors"][:3]))
            return record, False, "tenant config invalid"
        _set_step(record, "schema_check", "passed",
                  "tenant config validates against tenant-v1")
        record["stage"] = "checklist"
        return record, True, "schema_check passed"

    if stage == "checklist":
        if not isinstance(tenant, dict):
            _set_step(record, "checklist", "failed",
                      "no tenant config given")
            return record, False, "checklist needs a tenant config"
        report = deployment_checklist.evaluate_checklist(tenant, gates)
        by_id = {s["id"]: s for s in report["steps"]}
        evaluable_ok = (by_id["schema_valid"]["status"] == "pass"
                        and by_id["vapi_config_drafted"]["status"]
                        == "pass")
        detail = ("blocked: " + ", ".join(report["blocked_by"])
                  + "; gates outstanding: "
                  + ", ".join(report["gates_missing"])
                  if report["blocked_by"] or report["gates_missing"]
                  else "all checklist steps pass")
        if not evaluable_ok:
            _set_step(record, "checklist", "failed",
                      "; ".join(report["failed"]) or "evaluable step "
                      "failed")
            return record, False, "checklist evaluable step failed"
        _set_step(record, "checklist", "passed", detail)
        record["stage"] = "qa"
        return record, True, ("checklist passed (blocked + gate items "
                              "recorded as outstanding)")

    if stage == "qa":
        if not isinstance(tenant, dict) or script is None:
            _set_step(record, "qa", "failed",
                      "qa needs a tenant config and a call script")
            return record, False, "qa needs a tenant and a script"
        result = tenant_qa.run_qa(tenant, script)
        failed = [c["id"] for c in result["checks"]
                  if not c["passed"]]
        if result["verdict"] != "pass":
            _set_step(record, "qa", "failed",
                      "QA failed: " + ", ".join(failed))
            return record, False, "QA failed: " + ", ".join(failed)
        _set_step(record, "qa", "passed",
                  "QA passed " + str(len(result["checks"]))
                  + " checks on script " + str(result["script_id"]))
        record["stage"] = "boss_acceptance"
        return record, True, "qa passed"

    if stage == "boss_acceptance":
        gate = gates.get("boss_acceptance") or {}
        if gate.get("word") != BOSS_ACCEPTANCE_WORD:
            _set_step(record, "boss_acceptance", "gate_missing",
                      "Boss's 'ok' has not been recorded")
            return record, False, "boss acceptance needs Boss's 'ok'"
        _set_step(record, "boss_acceptance", "passed",
                  "Boss accepted with 'ok'")
        record["stage"] = "deploy"
        return record, True, "boss_acceptance passed"

    if stage == "deploy":
        _set_step(record, "deploy", "blocked",
                  "Live deployment is manual — Boss executes it "
                  "himself. No deploy path exists in this repo.")
        record["status"] = "accepted_manual_deploy_pending"
        return record, False, ("deploy is BLOCKED: live deployment is "
                               "manual, Boss executes it")

    _set_step(record, stage or "unknown", "failed",
              "unknown stage '" + str(stage) + "'")
    return record, False, "unknown stage '" + str(stage) + "'"


def save_record(record, path):
    """Persist an acceptance record through store_io (atomic)."""
    import store_io
    store_io.write_json_atomic(path, record)
    return path


def load_record(path):
    """Load an acceptance record written by save_record()."""
    import store_io
    return store_io.read_json(path, default=None)


if __name__ == "__main__":
    # Self-test — pure functions, no real store, no network, no send.
    import tempfile
    tenant = tenant_schema.synthetic_tenant()
    script = tenant_qa.synthetic_call_script(tenant)
    record = new_acceptance("T-0001")
    assert record["stage"] == "intake"
    assert record["deploy"] == "BLOCKED"

    # Full happy path: intake -> schema -> checklist -> qa -> boss ->
    # deploy (blocked).
    record, moved, _ = advance(record, tenant=tenant)
    assert moved is True and record["stage"] == "schema_check"
    record, moved, _ = advance(record, tenant=tenant)
    assert moved is True and record["stage"] == "checklist"
    gates = {}
    record, moved, _ = advance(record, tenant=tenant, gates=gates)
    assert moved is True and record["stage"] == "qa"
    assert record["steps"]["checklist"]["status"] == "passed"
    record, moved, _ = advance(record, tenant=tenant, script=script)
    assert moved is True and record["stage"] == "boss_acceptance"
    record, moved, reason = advance(record, tenant=tenant, gates=gates)
    assert moved is False and "ok" in reason
    assert record["steps"]["boss_acceptance"]["status"] == "gate_missing"
    ok, _ = record_boss_acceptance(gates, "nope")
    assert ok is False
    ok, _ = record_boss_acceptance(gates, "ok")
    assert ok is True
    record, moved, _ = advance(record, tenant=tenant, gates=gates)
    assert moved is True and record["stage"] == "deploy"
    record, moved, reason = advance(record, tenant=tenant, gates=gates)
    assert moved is False and "BLOCKED" in reason
    assert record["steps"]["deploy"]["status"] == "blocked"
    assert record["status"] == "accepted_manual_deploy_pending"
    assert record["deploy"] == "BLOCKED"

    # Refusals: bad schema blocks at schema_check; bad QA blocks at qa.
    bad = tenant_schema.synthetic_tenant()
    bad["business"]["trade"] = "dental"
    r2 = new_acceptance("T-0001")
    advance(r2, tenant=bad)
    record2, moved, _ = advance(r2, tenant=bad)
    assert moved is False and r2["stage"] == "schema_check"
    assert r2["steps"]["schema_check"]["status"] == "failed"
    r3 = new_acceptance("T-0001")
    advance(r3, tenant=tenant)
    advance(r3, tenant=tenant)
    advance(r3, tenant=tenant, gates={})
    bad_script = tenant_qa.synthetic_call_script(tenant)
    bad_script["turns"][-1]["text"] += " The visit costs $99."
    record3, moved, reason = advance(r3, tenant=tenant,
                                     script=bad_script)
    assert moved is False and r3["stage"] == "qa"
    assert "no_price_quoted" in reason

    # Persistence round-trips through a TEMP file only.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "acc-T-0001.json")
        save_record(record, path)
        back = load_record(path)
        assert back["id"] == record["id"]
        assert back["stage"] == "deploy"
        assert back["status"] == "accepted_manual_deploy_pending"
    print("acceptance_flow: OK (happy path reaches deploy BLOCKED; "
          "bad schema and bad QA refuse to advance; TEMP persistence "
          "round-trips)")
