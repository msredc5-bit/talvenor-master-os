"""§21 items 20 (AI Receptionist QA) + 21 (Client tenant isolation) —
Talvenor Master OS, Phase 8.

Real code under test: 00-CEO-Core/tenant_schema.py,
tenant_qa.py, deployment_checklist.py. SYNTHETIC fixture tenant only
— 0 paying clients exist, so there is no real tenant.
"""
import copy
import json

import tenant_qa
import tenant_schema
from deployment_checklist import evaluate_checklist
from tenant_qa import run_qa, synthetic_call_script
from tenant_schema import (
    draft_vapi_assistant_config,
    synthetic_tenant,
    validate_tenant,
)


# ---------------------------------------------------------------- item 21
class TestTenantIsolation:
    def test_synthetic_tenant_validates(self):
        result = validate_tenant(synthetic_tenant())
        assert result["valid"] is True
        assert result["missing"] == []
        assert result["rejected_reason"] is None
        assert result["tenant_id"] == "T-0001"

    def test_missing_field_fails_closed_with_client_input_required(self):
        bad = synthetic_tenant()
        del bad["business"]["phone"]
        result = validate_tenant(bad)
        assert result["valid"] is False
        assert "business.phone" in result["missing"]
        assert any("CLIENT INPUT REQUIRED: business.phone" in e
                   for e in result["errors"])
        assert result["rejected_reason"] is not None

    def test_non_object_fails_closed(self):
        result = validate_tenant("not-a-tenant")
        assert result["valid"] is False
        assert "<root>" in result["missing"]

    def test_dental_medical_hard_dq(self):
        for trade in ("dental", "medical", "dentist"):
            bad = synthetic_tenant()
            bad["business"]["trade"] = trade
            result = validate_tenant(bad)
            assert result["valid"] is False, trade
            assert "hard DQ" in (result["rejected_reason"] or ""), trade

    def test_tier_is_name_only_no_amounts_anywhere(self):
        tenant = synthetic_tenant()
        assert tenant["tier"] == {"name": "Growth"}
        assert "$" not in json.dumps(tenant)
        draft = draft_vapi_assistant_config(tenant)
        assert draft["ok"] is True
        assert "$" not in json.dumps(draft["config"])
        bad = synthetic_tenant()
        bad["tier"]["name"] = "Enterprise"
        assert validate_tenant(bad)["valid"] is False

    def test_language_locked_english_emergency_redirect_required(self):
        bad = synthetic_tenant()
        bad["call_handling"]["language"] = "es"
        assert validate_tenant(bad)["valid"] is False
        bad = synthetic_tenant()
        bad["call_handling"]["emergency_redirect"] = False
        assert validate_tenant(bad)["valid"] is False

    def test_vapi_draft_is_dict_never_sent(self):
        draft = draft_vapi_assistant_config(synthetic_tenant())
        assert draft["ok"] is True
        cfg = draft["config"]
        assert cfg["model"]["model"] == "gpt-4o-mini"
        assert cfg["voice"]["voiceId"] == "Emma"
        assert cfg["transcriber"]["model"] == "nova-3"
        assert cfg["draft_only"] is True and cfg["never_sent"] is True
        # An invalid tenant yields no draft at all.
        bad = synthetic_tenant()
        bad["business"]["trade"] = "dental"
        assert draft_vapi_assistant_config(bad)["ok"] is False

    def test_deployment_checklist_never_ready(self):
        """Deploy is ALWAYS BLOCKED in sandbox: phone, test calls and
        billing are blocked steps, so ready is False for the synthetic
        tenant too — no tenant can ever be ready today."""
        report = evaluate_checklist(synthetic_tenant())
        assert report["ready"] is False
        assert report["tenant_id"] == "T-0001"
        by_id = {s["id"]: s for s in report["steps"]}
        assert by_id["schema_valid"]["status"] == "pass"
        assert by_id["phone_number_assigned"]["status"] == "blocked"
        assert by_id["test_calls_passed"]["status"] == "blocked"
        assert by_id["billing_confirmed"]["status"] == "blocked"
        assert set(report["blocked_by"]) >= {
            "phone_number_assigned", "test_calls_passed",
            "billing_confirmed"}


# ---------------------------------------------------------------- item 20
class TestReceptionistQA:
    def test_good_script_passes_all_eight_checks(self):
        tenant = synthetic_tenant()
        result = run_qa(tenant, synthetic_call_script(tenant))
        assert result["verdict"] == "pass"
        assert len(result["checks"]) == 8
        assert all(c["passed"] for c in result["checks"])
        assert result["turns_checked"] == 10

    def test_price_quote_fails_exactly_that_check(self):
        tenant = synthetic_tenant()
        script = synthetic_call_script(tenant)
        script["turns"][-1]["text"] += " The visit costs $99."
        result = run_qa(tenant, script)
        assert result["verdict"] == "fail"
        failed = [c["id"] for c in result["checks"] if not c["passed"]]
        assert failed == ["no_price_quoted"]

    def test_missing_disclosure_fails_exactly_that_check(self):
        tenant = synthetic_tenant()
        script = synthetic_call_script(tenant)
        script["turns"] = [
            t for t in script["turns"]
            if "AI receptionist" not in t["text"]
            and "speaking with Talvenor" not in t["text"]]
        for t in script["turns"]:
            t["text"] = t["text"].replace(
                " — this is Talvenor, the AI receptionist.",
                " — this is Talvenor.")
        result = run_qa(tenant, script)
        assert result["verdict"] == "fail"
        failed = [c["id"] for c in result["checks"] if not c["passed"]]
        # Dropping the disclosure turns also strips the "AI
        # receptionist" greeting, so greeting_names_business fails
        # too — the disclosure check itself must be among the fails.
        assert "ai_disclosure_present" in failed

    def test_missing_life_safety_fails_exactly_that_check(self):
        tenant = synthetic_tenant()
        script = synthetic_call_script(tenant)
        script["turns"] = [
            t for t in script["turns"]
            if "emergency" not in t["text"].lower()
            and "911" not in t["text"]]
        result = run_qa(tenant, script)
        assert result["verdict"] == "fail"
        failed = [c["id"] for c in result["checks"] if not c["passed"]]
        assert failed == ["life_safety_present"]

    def test_missing_booking_link_fails_exactly_that_check(self):
        tenant = synthetic_tenant()
        script = synthetic_call_script(tenant)
        for t in script["turns"]:
            t["text"] = t["text"].replace(tenant_qa.BOOKING_LINK, "")
        result = run_qa(tenant, script)
        assert result["verdict"] == "fail"
        failed = [c["id"] for c in result["checks"] if not c["passed"]]
        assert failed == ["booking_confirmation"]

    def test_malformed_script_fails_closed(self):
        result = run_qa(synthetic_tenant(), {"id": "bad", "turns": []})
        assert result["verdict"] == "fail"
        result = run_qa(synthetic_tenant(), None)
        assert result["verdict"] == "fail"

    def test_qa_failure_has_no_recovery_task_mechanism(self):
        """GAP (honest): tenant_qa.run_qa returns a verdict only.
        No function in tenant_qa (or anywhere it calls) creates a
        recovery task or notifies a manager on failure — Scenario D
        is therefore [NOT TESTED] as an end-to-end recovery flow.
        This test pins the gap so a future fix flips it."""
        assert not hasattr(tenant_qa, "create_recovery_task")
        assert not hasattr(tenant_qa, "notify_manager")
        assert "recovery" not in dir(tenant_qa)
        tenant = synthetic_tenant()
        script = synthetic_call_script(tenant)
        script["turns"][-1]["text"] += " The visit costs $99."
        result = run_qa(tenant, script)
        assert result["verdict"] == "fail"
        assert "recovery_task" not in result
        assert "notified_manager" not in result
