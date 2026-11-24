"""§21 items 17 (Lead workflow) + 18 (Outreach sandbox) + 19 (Client
onboarding, as far as it is real) — Talvenor Master OS, Phase 8.

Real code under test: 00-CEO-Core/lead_chain/{chain,steps,crm_dryrun,
fixtures}.py. All runs use a tmp_path store; TEST fixtures only.
"""
import copy

import pytest

from lead_chain import ChainRunner, run_lead_chain
from lead_chain.fixtures import (
    MEDIUM_TIER2_PROSPECT,
    STRONG_TIER1_PROSPECT,
    WEAK_INCOMPLETE_PROSPECT,
)
from lead_chain.steps import BOOKING_LINK, execute_step


def _by_id(record):
    return {s["id"]: s for s in record["steps"]}


# ---------------------------------------------------------------- item 17
class TestLeadWorkflowHappyPath:
    def test_happy_path_blocked_at_deployment(self, tmp_path):
        """STRONG fixture: every step ok except the gated/outcome
        steps — outreach held pending-approval, deployment ALWAYS
        BLOCKED, monitoring skipped as its dependency. $0."""
        record = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        assert record["status"] == "blocked"
        assert record["cost_usd"] == 0.0
        assert len(record["steps"]) == 13
        by_id = _by_id(record)
        for step_id in ("lead_discovery", "lead_verification",
                        "lead_qualification", "crm_dryrun",
                        "reply_monitoring", "meeting", "sales_process",
                        "client_onboarding", "service_delivery", "qa"):
            assert by_id[step_id]["status"] == "ok", step_id
        assert by_id["outreach_draft"]["status"] == "pending-approval"
        assert by_id["deployment"]["status"] == "blocked"
        assert "ALWAYS BLOCKED" in by_id["deployment"]["error"]
        assert by_id["monitoring"]["status"] == "skipped"
        assert by_id["monitoring"]["reason"] == "dependency: deployment"
        assert record["stopped_by"] == "deployment"

    def test_medium_tier2_same_shape(self, tmp_path):
        record = run_lead_chain(
            copy.deepcopy(MEDIUM_TIER2_PROSPECT), store_dir=str(tmp_path))
        assert record["status"] == "blocked"
        assert "Tier 2" in _by_id(record)["lead_qualification"]["detail"]

    def test_chain_record_persisted_and_logged(self, tmp_path):
        record = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        chains_dir = tmp_path / "chains"
        assert (chains_dir / (record["idempotency_key"] + ".json")).exists()
        log_lines = (chains_dir / "chain_log.jsonl").read_text(
            encoding="utf-8").strip().splitlines()
        assert len(log_lines) == 1
        assert '"blocked"' in log_lines[0]
        assert all(s["execution_record"]["cost_usd"] == 0.0
                   for s in record["steps"])

    def test_failure_path_missing_email(self, tmp_path):
        """WEAK fixture (email MISSING): verification errors, the
        chain FAILS, every later step is skipped with the dependency
        reason — nothing after the failure executes."""
        record = run_lead_chain(
            copy.deepcopy(WEAK_INCOMPLETE_PROSPECT), store_dir=str(tmp_path))
        assert record["status"] == "failed"
        by_id = _by_id(record)
        assert by_id["lead_discovery"]["status"] == "ok"
        assert by_id["lead_verification"]["status"] == "error"
        assert by_id["lead_verification"]["error"] == (
            "verification failed: missing email")
        assert record["stopped_by"] == "lead_verification"
        for step_id in ("lead_qualification", "crm_dryrun",
                        "outreach_draft", "reply_monitoring", "meeting",
                        "sales_process", "client_onboarding",
                        "service_delivery", "qa", "deployment",
                        "monitoring"):
            assert by_id[step_id]["status"] == "skipped", step_id
            assert by_id[step_id]["reason"] == (
                "dependency: lead_verification"), step_id
            assert by_id[step_id]["attempt"] == 0, step_id

    def test_duplicate_rerun_executes_nothing(self, tmp_path):
        first = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        again = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        assert again["status"] == "duplicate"
        assert again["duplicate"] is True
        assert again["steps"] == first["steps"]
        assert again["idempotency_key"] == first["idempotency_key"]
        log_lines = (tmp_path / "chains" / "chain_log.jsonl").read_text(
            encoding="utf-8").strip().splitlines()
        assert len(log_lines) == 2  # run + duplicate marker, no re-run
        assert '"duplicate"' in log_lines[1]

    def test_bad_prospect_rejected_not_run(self, tmp_path):
        with pytest.raises(ValueError):
            run_lead_chain({"business_name": "No id"}, store_dir=str(tmp_path))
        with pytest.raises(ValueError):
            run_lead_chain("not-a-dict", store_dir=str(tmp_path))

    def test_dental_medical_dq(self):
        dental = copy.deepcopy(STRONG_TIER1_PROSPECT)
        dental["business_type"] = "dental"
        status, _detail, error = execute_step(
            {"id": "lead_qualification", "kind": "lead_qualification"},
            dental, {})
        assert status == "error"
        assert error == "DQ: dental/medical excluded"


# ---------------------------------------------------------------- item 18
class TestOutreachSandbox:
    def test_draft_contains_booking_link_send_never_executed(self):
        step = {"id": "outreach_draft", "kind": "outreach_draft",
                "gate": {"tool": "gmail_send", "action": "send"}}
        status, detail, error = execute_step(
            step, copy.deepcopy(STRONG_TIER1_PROSPECT), {})
        assert status == "pending-approval"
        assert BOOKING_LINK in detail
        assert "[DRAFT]" in detail
        assert error == "send held: gmail_send requires Boss approval"

    def test_chain_outreach_send_is_held_not_sent(self, tmp_path):
        record = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        step = _by_id(record)["outreach_draft"]
        assert step["status"] == "pending-approval"
        assert "never executed" in step["detail"]
        assert "gmail_send" in step["error"]
        # No step in the whole record claims a send happened: the
        # only "sent" phrasings are "no outreach sent" (draft-only
        # labels) and "send held" (the gate). Nothing was sent.
        for s in record["steps"]:
            text = (s["detail"] + " " + s["error"]).lower()
            assert "sent to " not in text
            assert "email sent" not in text
            assert "send executed" not in text

    def test_crm_dryrun_writes_nothing(self):
        from lead_chain.crm_dryrun import dry_run_upsert, health
        assert health()["status"] == "NOT CONNECTED"
        result = dry_run_upsert(copy.deepcopy(STRONG_TIER1_PROSPECT))
        assert result["status"] == "ok"
        assert result["dry_run"] is True
        assert result["live"] is False
        assert result["payload"]["table"] == "leads"


# ---------------------------------------------------------------- item 19
class TestClientOnboarding:
    def test_onboarding_step_is_draft_checklist_routed_to_operations(self,
                                                                    tmp_path):
        """What is REAL: the chain's client_onboarding step is a
        DRAFT intake checklist routed to 04-client-operations /
        RetentionAgent. It creates NO account — the detail says so.
        There is no real onboarding flow behind the label; this test
        asserts the label/routing, not a live onboarding. NOTE: the
        chain routes client_onboarding through the Phase 4 engine
        mock, so the chain record's detail is the engine's mock text,
        not the checklist. The checklist content is asserted via the
        real step executor below; the chain asserts routing."""
        record = run_lead_chain(
            copy.deepcopy(STRONG_TIER1_PROSPECT), store_dir=str(tmp_path))
        step = _by_id(record)["client_onboarding"]
        assert step["status"] == "ok"
        assert step["department"] == "04-client-operations"
        assert step["specialist"] == "RetentionAgent"
        status, detail, _error = execute_step(
            {"id": "client_onboarding", "kind": "client_onboarding",
             "specialist": "RetentionAgent"},
            copy.deepcopy(STRONG_TIER1_PROSPECT), {})
        assert status == "ok"
        assert "intake checklist" in detail
        assert "no account created" in detail
        assert "Draft only" in detail

    def test_onboarding_never_runs_after_failure(self, tmp_path):
        record = run_lead_chain(
            copy.deepcopy(WEAK_INCOMPLETE_PROSPECT), store_dir=str(tmp_path))
        assert _by_id(record)["client_onboarding"]["status"] == "skipped"
