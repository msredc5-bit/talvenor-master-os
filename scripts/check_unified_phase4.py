#!/usr/bin/env python3
"""Unified Business OS Phase 4 check — AI Receptionist Delivery Engine
(buildable part only).

Verifies the Phase 4 buildable part (spec:
TALVENOR_MASTER_ARCHITECTURE.md, "PHASE 4 — AI RECEPTIONIST
DELIVERY ENGINE", buildable part only):
  1. Tenant schema: the machine-readable schema loads; the
     synthetic fictional tenant validates; each failure class is
     rejected (missing field -> CLIENT INPUT REQUIRED listing the
     field; dental/medical -> refused, hard DQ; bad phone; bad
     timezone; non-English language; emergency_redirect not True;
     greeting without {business_name}; unknown tier; bad state).
     Tier is the NAME only — no amount appears in the draft config
     or the tenant JSON.
  2. Vapi assistant config draft: structural (model gpt-4o-mini,
     voice Emma, transcriber nova-3, firstMessage, systemPrompt),
     draft_only + never_sent, never built from an invalid tenant.
  3. Deployment checklist: synthetic tenant — schema + Vapi pass,
     phone / test-calls / billing BLOCKED with exact missing inputs,
     3 gates missing, ready False; gates recorded (wrong word
     rejected) -> gates_missing empty but ready STILL False;
     invalid tenant -> schema + Vapi fail.
  4. QA-as-code: good synthetic script passes 8/8; each broken
     variant fails exactly its check (no disclosure, no life-safety,
     price quoted, no booking link, no transfer, no business name,
     no qualification); transfer-disabled tenant -> transfer check
     not applicable, still passes.
  5. Acceptance flow: happy path intake -> schema -> checklist ->
     qa -> boss_acceptance -> deploy (BLOCKED, status
     accepted_manual_deploy_pending); bad schema refuses at
     schema_check; bad QA refuses at qa; missing Boss "ok" refuses
     at boss_acceptance (wrong word rejected); record persists to
     TEMP and reloads; record is tasks-v1-shaped.
  6. No live deployment path: no network import (urllib / requests
     / socket / subprocess / http.client) and no urlopen in any of
     the 4 new modules; no gmail_send / n8n_trigger / live_tools
     reference; no "136" / "1189" digit sequence in any new file
     (the check_phase6 scope scan); no Bengali in any new file.
  7. The real store did not change in this run (tasks, approvals,
     memory, goals, usage_ledger, schedules, confirmations,
     leads.json, config.json all hash-identical; no agent_runs.json
     / audit.log / tool_calls.json created).

All store-touching steps use TEMP files/dirs (a TEMP approvals
file is passed nowhere here — no approval is requested; the
acceptance record is saved to a TEMP dir only). Stdlib only, no
network, no send, no publish, no spend, no delete.
Exit 0 = PASS.
"""

import importlib.util
import json
import os
import re
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
STORE_DIR = os.path.join(BASE, "store")

sys.path.insert(0, CEO_CORE_DIR)

CHECKS = []

NEW_FILES = (
    "tenant_schema.py",
    "tenant_schema.json",
    "deployment_checklist.py",
    "tenant_qa.py",
    "acceptance_flow.py",
    "tenant-acceptance.md",
)


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" — {detail}" if detail else ""))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _snapshot_store():
    snap = {}
    for name in ("tasks.json", "approvals.json", "memory.json",
                 "goals.json", "usage_ledger.json", "schedules.json",
                 "confirmations.json", "leads.json"):
        try:
            with open(os.path.join(STORE_DIR, name),
                      encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    try:
        with open(os.path.join(CEO_CORE_DIR, "config.json"),
                  encoding="utf-8") as f:
            snap["config.json"] = f.read()
    except OSError:
        snap["config.json"] = None
    snap["agent_runs"] = os.path.exists(
        os.path.join(STORE_DIR, "agent_runs.json"))
    snap["audit_log"] = os.path.exists(
        os.path.join(STORE_DIR, "audit.log"))
    snap["tool_calls"] = os.path.exists(
        os.path.join(STORE_DIR, "tool_calls.json"))
    return snap


def _copy_tenant(tenant):
    return json.loads(json.dumps(tenant))


def main():
    before = _snapshot_store()
    try:
        import tenant_schema
        import deployment_checklist
        import tenant_qa
        import acceptance_flow
    except Exception as exc:  # noqa: BLE001
        check("Phase 4 modules import", False, str(exc))
        print(f"\n{sum(1 for _, ok, _ in CHECKS if ok)}/{len(CHECKS)}"
              " checks passed.")
        return 1

    tenant = tenant_schema.synthetic_tenant()
    script = tenant_qa.synthetic_call_script(tenant)

    # ---------- 1. Tenant schema ----------
    try:
        schema = tenant_schema.load_schema()
        check("schema file loads (tenant-v1)",
              schema.get("schema") == "tenant-v1"
              and "business" in schema
              and schema["tier"]["name_enum"] == ["Starter", "Growth",
                                                  "Scale"],
              "tenant-v1, tier names only")
        check("synthetic fixture is labelled fictional",
              tenant.get("synthetic") is True
              and tenant.get("fictional") is True
              and tenant["business"]["name"] == "Example Plumbing Co."
              and tenant["business"]["city"] == "Fictional City",
              "Example Plumbing Co., Fictional City")
        r = tenant_schema.validate_tenant(tenant)
        check("synthetic tenant validates",
              r["valid"] is True and r["missing"] == []
              and r["rejected_reason"] is None,
              f"errors={r['errors']}")
        bad = _copy_tenant(tenant)
        del bad["business"]["phone"]
        r = tenant_schema.validate_tenant(bad)
        check("missing field -> CLIENT INPUT REQUIRED (phone listed)",
              r["valid"] is False
              and "business.phone" in r["missing"]
              and any("CLIENT INPUT REQUIRED: business.phone" in e
                      for e in r["errors"]),
              f"missing={r['missing']}")
        bad = _copy_tenant(tenant)
        del bad["qualification"]
        r = tenant_schema.validate_tenant(bad)
        check("missing section -> CLIENT INPUT REQUIRED (qualification)",
              r["valid"] is False
              and "qualification" in r["missing"],
              f"missing={r['missing']}")
        for trade in ("dental", "medical", "clinic"):
            bad = _copy_tenant(tenant)
            bad["business"]["trade"] = trade
            r = tenant_schema.validate_tenant(bad)
            check(f"trade '{trade}' refused (hard DQ)",
                  r["valid"] is False
                  and "hard DQ" in (r["rejected_reason"] or ""),
                  f"reason={r['rejected_reason']}")
        bad = _copy_tenant(tenant)
        bad["business"]["phone"] = "not-a-phone"
        r = tenant_schema.validate_tenant(bad)
        check("bad phone rejected",
              r["valid"] is False
              and any("phone" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["business"]["timezone"] = "Mars/Olympus"
        r = tenant_schema.validate_tenant(bad)
        check("bad timezone rejected",
              r["valid"] is False
              and any("timezone" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["call_handling"]["language"] = "es"
        r = tenant_schema.validate_tenant(bad)
        check("non-English language rejected (locked: en only)",
              r["valid"] is False
              and any("English" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["call_handling"]["emergency_redirect"] = False
        r = tenant_schema.validate_tenant(bad)
        check("emergency_redirect False rejected",
              r["valid"] is False
              and any("emergency_redirect" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["call_handling"]["greeting_template"] = "Hello, how can I help?"
        r = tenant_schema.validate_tenant(bad)
        check("greeting without {business_name} rejected",
              r["valid"] is False
              and any("business_name" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["tier"]["name"] = "Platinum"
        r = tenant_schema.validate_tenant(bad)
        check("unknown tier rejected",
              r["valid"] is False
              and any("tier.name" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        bad = _copy_tenant(tenant)
        bad["business"]["state"] = "XX"
        r = tenant_schema.validate_tenant(bad)
        check("bad state rejected",
              r["valid"] is False
              and any("state" in e for e in r["errors"]),
              f"errors={r['errors'][:1]}")
        r = tenant_schema.validate_tenant("not a dict")
        check("non-dict config rejected",
              r["valid"] is False
              and r["rejected_reason"] is not None,
              f"errors={r['errors'][:1]}")
        check("tier name only: no amount in tenant JSON",
              "$" not in json.dumps(tenant),
              "no $ in synthetic tenant")
    except Exception as exc:  # noqa: BLE001
        check("tenant schema section", False, str(exc))

    # ---------- 2. Vapi assistant config draft ----------
    try:
        draft = tenant_schema.draft_vapi_assistant_config(tenant)
        check("Vapi draft builds from a valid tenant",
              draft["ok"] is True and draft["config"] is not None,
              "ok=True")
        cfg = draft["config"] or {}
        check("Vapi draft structure (model/voice/transcriber)",
              cfg.get("model", {}).get("model") == "gpt-4o-mini"
              and cfg.get("voice", {}).get("voiceId") == "Emma"
              and cfg.get("transcriber", {}).get("model") == "nova-3"
              and cfg.get("transcriber", {}).get("language") == "en"
              and bool(cfg.get("firstMessage"))
              and bool(cfg.get("systemPrompt")),
              "gpt-4o-mini / Emma / nova-3 / en")
        check("Vapi draft names the business in the greeting",
              "Example Plumbing Co." in (cfg.get("firstMessage") or ""),
              "business named")
        check("Vapi draft is draft-only, never sent",
              cfg.get("draft_only") is True
              and cfg.get("never_sent") is True,
              "draft_only + never_sent")
        check("Vapi draft contains no amount",
              "$" not in json.dumps(cfg),
              "no $ in draft config")
        bad = _copy_tenant(tenant)
        bad["business"]["trade"] = "dental"
        draft = tenant_schema.draft_vapi_assistant_config(bad)
        check("Vapi draft refused for an invalid tenant",
              draft["ok"] is False and draft["config"] is None,
              "ok=False, no config built")
    except Exception as exc:  # noqa: BLE001
        check("Vapi draft section", False, str(exc))

    # ---------- 3. Deployment checklist ----------
    try:
        report = deployment_checklist.evaluate_checklist(tenant)
        by_id = {s["id"]: s for s in report["steps"]}
        check("checklist: schema + Vapi steps pass",
              by_id["schema_valid"]["status"] == "pass"
              and by_id["vapi_config_drafted"]["status"] == "pass",
              "evaluable steps pass")
        check("checklist: phone / test-calls / billing BLOCKED",
              by_id["phone_number_assigned"]["status"] == "blocked"
              and by_id["test_calls_passed"]["status"] == "blocked"
              and by_id["billing_confirmed"]["status"] == "blocked",
              f"blocked={report['blocked_by']}")
        check("checklist: blocked steps name the missing input",
              "Twilio" in by_id["phone_number_assigned"]["detail"]
              and "live brain" in by_id["test_calls_passed"]["detail"]
              and "paying_client_confirmed"
              in by_id["billing_confirmed"]["detail"],
              "exact missing inputs listed")
        check("checklist: 3 gates missing, ready False",
              report["gates_missing"]
              == ["booking_link_verified", "greeting_approved",
                  "go_live"]
              and report["ready"] is False,
              f"gates_missing={report['gates_missing']}")
        gates = {}
        ok, _ = deployment_checklist.record_gate(
            gates, "greeting_approved", "nope")
        check("gate: wrong word rejected, not recorded",
              ok is False and "greeting_approved" not in gates,
              "wrong word refused")
        ok, _ = deployment_checklist.record_gate(
            gates, "greeting_approved", "ok")
        check("gate: greeting 'ok' recorded",
              ok is True and "greeting_approved" in gates,
              "recorded")
        ok, _ = deployment_checklist.record_gate(gates, "go_live", "ok")
        check("gate: go-live 'ok' rejected (needs 'go')",
              ok is False and "go_live" not in gates,
              "'go' required")
        ok, _ = deployment_checklist.record_gate(gates, "go_live", "go")
        ok2, _ = deployment_checklist.record_gate(
            gates, "booking_link_verified", "ok")
        check("gate: go-live 'go' + booking 'ok' recorded",
              ok is True and ok2 is True,
              "all 3 gates recorded")
        report = deployment_checklist.evaluate_checklist(tenant, gates)
        check("checklist: gates recorded but ready STILL False",
              report["gates_missing"] == []
              and report["ready"] is False
              and report["blocked_by"] == ["phone_number_assigned",
                                           "test_calls_passed",
                                           "billing_confirmed"],
              "blocked steps remain")
        bad = _copy_tenant(tenant)
        del bad["business"]["phone"]
        report = deployment_checklist.evaluate_checklist(bad)
        by_id = {s["id"]: s for s in report["steps"]}
        check("checklist: invalid tenant -> schema + Vapi fail",
              by_id["schema_valid"]["status"] == "fail"
              and by_id["vapi_config_drafted"]["status"] == "fail",
              "fail, fail")
    except Exception as exc:  # noqa: BLE001
        check("deployment checklist section", False, str(exc))

    # ---------- 4. QA-as-code ----------
    try:
        result = tenant_qa.run_qa(tenant, script)
        check("QA: good synthetic script passes 8/8",
              result["verdict"] == "pass"
              and len(result["checks"]) == 8
              and all(c["passed"] for c in result["checks"]),
              f"turns={result['turns_checked']}")
        check("QA: script is labelled synthetic",
              script.get("synthetic") is True,
              "synthetic fixture")

        def broken(mutate):
            s = json.loads(json.dumps(script))
            mutate(s)
            return tenant_qa.run_qa(tenant, s)

        def drop_disclosure(s):
            s["turns"] = [t for t in s["turns"]
                          if "AI receptionist" not in t["text"]
                          and "speaking with Talvenor" not in t["text"]]
            for t in s["turns"]:
                t["text"] = t["text"].replace(
                    " — this is Talvenor, the AI receptionist.",
                    " — this is Talvenor.")
        r = broken(drop_disclosure)
        check("QA fails: no AI disclosure",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "ai_disclosure_present"][0]["passed"]
              is False,
              "ai_disclosure_present fails")

        def drop_life_safety(s):
            s["turns"] = [t for t in s["turns"]
                          if "emergency" not in t["text"].lower()
                          and "911" not in t["text"]]
        r = broken(drop_life_safety)
        check("QA fails: no life-safety check",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "life_safety_present"][0]["passed"]
              is False,
              "life_safety_present fails")

        def quote_price(s):
            s["turns"][-1]["text"] += " The visit costs $99."
        r = broken(quote_price)
        check("QA fails: price quoted to the caller",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "no_price_quoted"][0]["passed"]
              is False,
              "no_price_quoted fails")

        def drop_booking_link(s):
            for t in s["turns"]:
                t["text"] = t["text"].replace(
                    tenant_qa.BOOKING_LINK, "")
        r = broken(drop_booking_link)
        check("QA fails: no booking link in confirmation",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "booking_confirmation"][0]["passed"]
              is False,
              "booking_confirmation fails")

        def drop_transfer(s):
            for t in s["turns"]:
                t["text"] = t["text"].replace(
                    " If you would rather speak to a person, I can "
                    "transfer you to the office.", "")
        r = broken(drop_transfer)
        check("QA fails: no transfer offered (enabled)",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "transfer_rule_present"][0]["passed"]
              is False,
              "transfer_rule_present fails")

        def drop_business_name(s):
            for t in s["turns"]:
                t["text"] = t["text"].replace(
                    "Example Plumbing Co.", "our shop")
        r = broken(drop_business_name)
        check("QA fails: greeting does not name the business",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "greeting_names_business"][0]["passed"]
              is False,
              "greeting_names_business fails")

        def drop_qualification(s):
            q = tenant["qualification"]["questions"][0]
            for t in s["turns"]:
                t["text"] = t["text"].replace(q, "")
        r = broken(drop_qualification)
        check("QA fails: no qualification question asked",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "qualification_present"][0]["passed"]
              is False,
              "qualification_present fails")

        def add_claim(s):
            s["turns"][-1]["text"] += (" We are the best in the state, "
                                       "guaranteed.")
        r = broken(add_claim)
        check("QA fails: invented guarantee claim",
              r["verdict"] == "fail"
              and [c for c in r["checks"]
                   if c["id"] == "no_invented_claims"][0]["passed"]
              is False,
              "no_invented_claims fails")

        no_transfer = _copy_tenant(tenant)
        no_transfer["escalation"]["transfer_enabled"] = False
        no_transfer["escalation"].pop("transfer_number", None)
        r = tenant_schema.validate_tenant(no_transfer)
        check("transfer-disabled tenant still validates",
              r["valid"] is True,
              f"errors={r['errors']}")
        r = tenant_qa.run_qa(no_transfer, script)
        t_check = [c for c in r["checks"]
                   if c["id"] == "transfer_rule_present"][0]
        check("QA: transfer check not applicable when disabled",
              t_check["passed"] is True
              and "not applicable" in t_check["detail"],
              "passes as not-applicable")
    except Exception as exc:  # noqa: BLE001
        check("QA section", False, str(exc))

    # ---------- 5. Acceptance flow ----------
    try:
        record = acceptance_flow.new_acceptance("T-0001")
        check("acceptance record starts at intake, deploy BLOCKED",
              record["stage"] == "intake"
              and record["deploy"] == "BLOCKED"
              and record["type"] == "tenant_acceptance"
              and record["payload"]["tenant_id"] == "T-0001",
              "tasks-v1-shaped, deploy BLOCKED")
        record, moved, _ = acceptance_flow.advance(
            record, tenant=tenant)
        check("acceptance: intake passes",
              moved is True and record["stage"] == "schema_check",
              "-> schema_check")
        record, moved, _ = acceptance_flow.advance(
            record, tenant=tenant)
        check("acceptance: schema_check passes",
              moved is True and record["stage"] == "checklist",
              "-> checklist")
        gates = {}
        record, moved, _ = acceptance_flow.advance(
            record, tenant=tenant, gates=gates)
        check("acceptance: checklist passes (blocked recorded)",
              moved is True and record["stage"] == "qa"
              and record["steps"]["checklist"]["status"] == "passed"
              and "blocked" in record["steps"]["checklist"]["detail"],
              "-> qa, blocked items recorded")
        record, moved, _ = acceptance_flow.advance(
            record, tenant=tenant, script=script)
        check("acceptance: qa passes",
              moved is True and record["stage"] == "boss_acceptance",
              "-> boss_acceptance")
        record, moved, reason = acceptance_flow.advance(
            record, tenant=tenant, gates=gates)
        check("acceptance: missing Boss ok refuses",
              moved is False and "ok" in reason
              and record["stage"] == "boss_acceptance"
              and record["steps"]["boss_acceptance"]["status"]
              == "gate_missing",
              "refused, gate_missing")
        ok, _ = acceptance_flow.record_boss_acceptance(gates, "nope")
        check("acceptance: wrong word rejected for Boss ok",
              ok is False and "boss_acceptance" not in gates,
              "wrong word refused")
        ok, _ = acceptance_flow.record_boss_acceptance(gates, "ok")
        check("acceptance: Boss ok recorded",
              ok is True and "boss_acceptance" in gates,
              "recorded")
        record, moved, _ = acceptance_flow.advance(
            record, tenant=tenant, gates=gates)
        check("acceptance: boss_acceptance passes -> deploy stage",
              moved is True and record["stage"] == "deploy",
              "-> deploy")
        record, moved, reason = acceptance_flow.advance(
            record, tenant=tenant, gates=gates)
        check("acceptance: deploy ALWAYS blocked",
              moved is False and "BLOCKED" in reason
              and record["steps"]["deploy"]["status"] == "blocked"
              and record["status"]
              == "accepted_manual_deploy_pending",
              "deploy blocked, manual only")
        bad = _copy_tenant(tenant)
        bad["business"]["trade"] = "dental"
        r2 = acceptance_flow.new_acceptance("T-0001")
        acceptance_flow.advance(r2, tenant=bad)
        _, moved, _ = acceptance_flow.advance(r2, tenant=bad)
        check("acceptance: bad schema refuses at schema_check",
              moved is False and r2["stage"] == "schema_check"
              and r2["steps"]["schema_check"]["status"] == "failed",
              "refused, stays at schema_check")
        r3 = acceptance_flow.new_acceptance("T-0001")
        acceptance_flow.advance(r3, tenant=tenant)
        acceptance_flow.advance(r3, tenant=tenant)
        acceptance_flow.advance(r3, tenant=tenant, gates={})
        bad_script = json.loads(json.dumps(script))
        bad_script["turns"][-1]["text"] += " The visit costs $99."
        _, moved, reason = acceptance_flow.advance(
            r3, tenant=tenant, script=bad_script)
        check("acceptance: failed QA refuses at qa",
              moved is False and r3["stage"] == "qa"
              and "no_price_quoted" in reason,
              "refused, stays at qa")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "acc-T-0001.json")
            acceptance_flow.save_record(record, path)
            back = acceptance_flow.load_record(path)
            check("acceptance: record persists to TEMP + reloads",
                  back is not None and back["id"] == record["id"]
                  and back["stage"] == "deploy"
                  and back["status"]
                  == "accepted_manual_deploy_pending",
                  "TEMP round-trip")
    except Exception as exc:  # noqa: BLE001
        check("acceptance flow section", False, str(exc))

    # ---------- 6. No live deployment path ----------
    try:
        banned_import = re.compile(
            r"^\s*(import|from)\s+(urllib|requests|socket|subprocess"
            r"|http\.client)\b", re.MULTILINE)
        for mod_name in ("tenant_schema", "deployment_checklist",
                         "tenant_qa", "acceptance_flow"):
            src = open(os.path.join(CEO_CORE_DIR, mod_name + ".py"),
                       encoding="utf-8").read()
            check(f"{mod_name}: no network import, no live-send ref",
                  banned_import.search(src) is None
                  and "urlopen(" not in src
                  and "gmail_send" not in src
                  and "n8n_trigger" not in src
                  and "live_tools" not in src
                  and "hatch_gws_cli" not in src,
                  "no live path")
        bn = re.compile(r"[\u0980-\u09FF]")
        for fname in NEW_FILES:
            path = os.path.join(CEO_CORE_DIR, fname)
            text = open(path, encoding="utf-8").read()
            check(f"{fname}: no 136-scope digits, no Bengali",
                  "136" not in text and "1189" not in text
                  and "1,189" not in text
                  and bn.search(text) is None,
                  "clean")
    except Exception as exc:  # noqa: BLE001
        check("no-live-deployment-path section", False, str(exc))

    # ---------- 7. Real store unchanged ----------
    try:
        after = _snapshot_store()
        changed = [k for k in before if before[k] != after[k]]
        check("real store unchanged by this check run",
              changed == [] and after["agent_runs"] is False
              and after["audit_log"] is False
              and after["tool_calls"] is False,
              f"changed={changed}")
        check("lead store still 524 leads / 163 first mails",
              json.loads(after["leads.json"])["meta"]
              ["total_unique_leads"] == 524
              and json.loads(after["leads.json"])["meta"]
              ["first_mails_total"] == 163,
              "524 / 163 intact")
    except Exception as exc:  # noqa: BLE001
        check("store-unchanged section", False, str(exc))

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"\n{passed}/{len(CHECKS)} checks passed.")
    return 0 if passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
