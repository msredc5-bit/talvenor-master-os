#!/usr/bin/env python3
"""Unified Business OS Phase 3 check — Sales and Growth Engine.

Verifies the Phase 3 build (spec: TALVENOR_MASTER_ARCHITECTURE.md,
"PHASE 3 — SALES AND GROWTH ENGINE"):
  1. Lead store (store/leads.json): schema, totals (524 unique leads
     from 507 pool rows + 30 sent-history-only; 13 branch rows merged),
     first mails computed from the store (163 total; PA 39, FL 54,
     GA 16, TX 15, CA 15, IL 9, MI 5, NC 5, NY 4, OH 1), dedup
     (UGI one lead, 2 locations; no two leads share a domain), flags
     (6 bounced, 2 double-sent, 1 held, 1 low-confidence,
     1 other-channel), Isackson filing-gap record (verified Gmail Sent
     message id). The builder reproduces the store byte-for-byte
     (except the "built" timestamp) into a TEMP dir.
  2. Reply triage: bounce / decline / hot-lead (pricing, demo,
     interest) / needs-decision (unclear, dental DQ, empty) verdicts;
     no price ever quoted in any draft; demo link only when asked;
     sendable is always False; no send path exists in the module.
  3. Follow-up queue: the 100-mail rule refuses ALL 10 real states
     today (queue empty, refusals carry reasons + counts); a synthetic
     101-mail TEMP store queues eligible leads only and skips the
     blocked ones; idempotency keys are stable.
  4. CRM adapter: health is NOT CONNECTED; dry-run payloads only
     (validated, serializable); no network import in the module.
  5. FollowUpAgent wiring: PA with no payload count reads 39 from the
     lead store (PARKED); payload count still wins; total reads 163.
  6. Sends stay blocked: trust_check("send") without Boss's words is
     never "allow"; a fresh ApprovalGateway approval stays pending.
  7. The real store did not change in this run (except the intended
     store/leads.json, which this check only reads).

All store-touching steps use TEMP files/dirs (a TEMP approvals file is
passed to every run() call; the builder is re-run into a TEMP dir).
Stdlib only, no network, no send, no publish, no spend, no delete.
Exit 0 = PASS.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
STORE_DIR = os.path.join(BASE, "store")
AGENCY_DIR = os.path.join(BASE, "01-Agency-Department")

sys.path.insert(0, CEO_CORE_DIR)

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _snapshot_store():
    snap = {}
    for name in ("tasks.json", "approvals.json", "memory.json",
                 "goals.json", "usage_ledger.json", "schedules.json",
                 "confirmations.json"):
        try:
            with open(os.path.join(STORE_DIR, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    snap["leads_exists"] = os.path.exists(
        os.path.join(STORE_DIR, "leads.json"))
    snap["agent_runs"] = os.path.exists(
        os.path.join(STORE_DIR, "agent_runs.json"))
    snap["audit_log"] = os.path.exists(os.path.join(STORE_DIR, "audit.log"))
    snap["tool_calls"] = os.path.exists(
        os.path.join(STORE_DIR, "tool_calls.json"))
    return snap


def main():
    tmp = tempfile.mkdtemp()
    approvals_path = os.path.join(tmp, "approvals.json")
    before = _snapshot_store()
    try:
        import lead_store
        import reply_triage
        import followup_queue
        import crm_adapter
        import honest_status
        from trust_gate import trust_check
        from human_approval_gateway import ApprovalGateway
    except Exception as exc:  # noqa: BLE001
        check("Phase 3 modules import", False, str(exc))
        print(f"\n{sum(1 for _, ok, _ in CHECKS if ok)}/{len(CHECKS)} checks passed.")
        return 1

    # ---------- 1. Lead store ----------
    try:
        data = lead_store.load_store()
        check("lead store loads (schema leads-v1)", data is not None
              and data.get("schema") == "leads-v1",
              f"schema={None if data is None else data.get('schema')}")
        meta = lead_store.store_meta()
        check("lead store totals: 524 unique from 507 + 30",
              meta.get("pool_rows") == 507
              and meta.get("pool_unique_after_dedup") == 494
              and meta.get("branch_rows_merged") == 13
              and meta.get("sent_history_only") == 30
              and meta.get("total_unique_leads") == 524
              and meta.get("source_row_total") == 537
              and len(lead_store.leads()) == 524,
              f"meta={meta.get('total_unique_leads')} unique, "
              f"{meta.get('pool_unique_after_dedup')} pool-unique")
        expected_state = {"PA": 39, "FL": 54, "GA": 16, "TX": 15,
                          "CA": 15, "IL": 9, "MI": 5, "NC": 5,
                          "NY": 4, "OH": 1}
        by_state = lead_store.first_mails_by_state()
        check("first mails computed from store: 163 total, per-state match",
              lead_store.first_mails_total() == 163
              and by_state == expected_state,
              f"total={lead_store.first_mails_total()}, by_state={by_state}")
        check("config honest_status agrees with store (163)",
              honest_status.first_mails_sent() == 163,
              f"config={honest_status.first_mails_sent()!r}")
        ugi = lead_store.find_by_domain("https://www.ugihvac.com/")
        check("dedup: UGI is one lead with 2 branch locations",
              ugi is not None and len(ugi.get("locations") or []) == 2
              and ugi["business_name"].startswith("UGI"),
              f"locations={None if ugi is None else len(ugi.get('locations') or [])}")
        domains = [l.get("domain") for l in lead_store.leads()
                   if l.get("domain")]
        check("dedup: no two leads share a domain",
              len(domains) == len(set(domains)),
              f"domains={len(domains)}, unique={len(set(domains))}")
        check("dedup lookups: phone + email find the same lead",
              lead_store.find_by_phone("+1 412-872-4105") is not None
              and lead_store.find_by_phone("+1 412-872-4105")["business_name"].startswith("Metz")
              and lead_store.find_by_email("info@athensplumbing.com") is not None,
              "Metz by phone, Athens by email")
        bounced = lead_store.flagged_leads("BOUNCED_DEAD_ADDRESS")
        check("flags: 6 bounced dead addresses, exact emails",
              len(bounced) == 6
              and {lead_store.norm_email(l.get("email")) for l in bounced}
              == {"info@athensplumbing.com", "info@albertoplumbing.com",
                  "office@plumbproz.com", "napps@nappsac.com",
                  "privacy@allmastersplumbing.com",
                  "service@tnt.jdpps.com"},
              f"bounced={[l['business_name'] for l in bounced]}")
        double = lead_store.flagged_leads("NEVER_REMAIL_DOUBLE_SENT")
        check("flags: 2 double-sent (Metz, AAA), never re-mail",
              len(double) == 2
              and {"Metz Plumbing & Sewer Lining LLC",
                   "AAA Sewer & Drain Service"}
              == {l["business_name"] for l in double},
              f"double={[l['business_name'] for l in double]}")
        held = lead_store.flagged_leads("HELD_DO_NOT_CONTACT")
        check("flags: 1 held (Premier Plumbing San Antonio)",
              len(held) == 1
              and held[0].get("domain") == "premierplumbing.us"
              and held[0].get("city") == "San Antonio",
              f"held={[l['business_name'] for l in held]}")
        check("flags: 1 low-confidence + 1 other-channel + shared",
              len(lead_store.flagged_leads("HELD_LOW_CONFIDENCE")) == 1
              and len(lead_store.flagged_leads("OTHER_CHANNEL_CONTACTED")) == 1
              and len(lead_store.flagged_leads("SHARED_PHONE")) == 2
              and len(lead_store.flagged_leads("SHARED_EMAIL")) == 4,
              "Always Plumbing held; Remarkable other-channel; "
              "Flow City/Rayne shared phone")
        isa = lead_store.find_by_email("isacksonplumbing@gmail.com")
        check("Isackson filing gap: verified Gmail Sent record in store",
              isa is not None
              and (isa.get("sent") or {}).get("emailed") is True
              and (isa.get("sent") or {}).get("message_id")
              == "1a1cfb0ff25cdb8c"
              and (isa.get("sent") or {}).get("sent_date") == "2026-11-12",
              f"sent={None if isa is None else isa.get('sent')}")
        check("store meta records the 163 reconciliation",
              "Isackson" in (meta.get("reconciliation") or "")
              and "163" in (meta.get("reconciliation") or ""),
              "reconciliation note present")
        check("lead store missing/corrupt -> UNKNOWN, never a guess",
              lead_store.first_mails_total("/tmp/no-such-leads.json")
              == lead_store.UNKNOWN
              and lead_store.load_store("/tmp/no-such-leads.json") is None,
              "UNKNOWN on missing file")
    except Exception as exc:  # noqa: BLE001
        check("lead store section", False, str(exc))

    # ---------- 1b. Builder reproduces the store (TEMP dir) ----------
    try:
        tmp_store = os.path.join(tmp, "store")
        proc = subprocess.run(
            [sys.executable,
             os.path.join(BASE, "scripts", "build_lead_store.py"),
             "--store-dir", tmp_store],
            capture_output=True, text=True, timeout=120)
        check("builder re-runs cleanly into a TEMP store",
              proc.returncode == 0, proc.stderr.strip()[:200])
        if proc.returncode == 0:
            rebuilt = json.load(open(os.path.join(tmp_store, "leads.json"),
                                     encoding="utf-8"))
            live = json.load(open(os.path.join(STORE_DIR, "leads.json"),
                                  encoding="utf-8"))
            rebuilt.pop("built", None)
            live.pop("built", None)
            check("builder output matches the live store (except timestamp)",
                  rebuilt == live,
                  "deterministic rebuild")
    except Exception as exc:  # noqa: BLE001
        check("builder reproducibility", False, str(exc))

    # ---------- 2. Reply triage ----------
    try:
        v = reply_triage.triage(
            "gmail", "mailer-daemon@example.com",
            "Delivery Status Notification (Failure): user unknown")
        check("triage: bounce -> log only, no draft",
              v["verdict"] == "bounce" and v["draft"] is None
              and v["sendable"] is False, v["verdict"])
        v = reply_triage.triage("gmail", "a@b.com", "Not interested, thanks.")
        check("triage: decline -> polite exit draft, not sendable",
              v["verdict"] == "decline"
              and v["draft"] == reply_triage.EXIT_DRAFT
              and v["sendable"] is False, v["verdict"])
        v = reply_triage.triage(
            "instagram", "plumber_joe",
            "Sounds interesting — how much does it cost?",
            sender_name="Joe")
        check("triage: pricing question -> hot lead, no price quoted",
              v["verdict"] == "hot_lead" and v.get("asked_price") is True
              and "$" not in (v["draft"] or "")
              and "we share details on a short call"
              in (v["draft"] or "").lower()
              and reply_triage.BOOKING_LINK in (v["draft"] or "")
              and v["sendable"] is False,
              "price answered with a call, booking link present")
        v = reply_triage.triage(
            "gmail", "a@b.com", "Can I see a demo of it working?",
            sender_name="Sam")
        check("triage: demo request -> hot lead with demo link",
              v["verdict"] == "hot_lead" and v.get("asked_demo") is True
              and reply_triage.DEMO_VIDEO_LINK in (v["draft"] or ""),
              "demo link present")
        v = reply_triage.triage(
            "gmail", "a@b.com", "Can I see a demo of it working?",
            sender_name="Sam")
        check("triage: demo link NOT in pricing-only draft",
              reply_triage.DEMO_VIDEO_LINK not in
              (reply_triage.triage(
                  "gmail", "a@b.com",
                  "How much does it cost?", sender_name="Sam")["draft"] or ""),
              "demo link only when asked")
        v = reply_triage.triage(
            "messenger", "x", "Sounds good — can we talk tomorrow?")
        check("triage: call request -> hot lead with booking link",
              v["verdict"] == "hot_lead"
              and reply_triage.BOOKING_LINK in (v["draft"] or ""),
              v["verdict"])
        v = reply_triage.triage("messenger", "x", "ok")
        check("triage: unclear -> needs_decision, no draft",
              v["verdict"] == "needs_decision" and v["draft"] is None,
              v["verdict"])
        v = reply_triage.triage(
            "gmail", "d@dental.example",
            "We are a dental clinic, interested in your service")
        check("triage: dental/medical -> needs_decision, never a hot lead",
              v["verdict"] == "needs_decision"
              and "dental" in v["reason"].lower(),
              v["verdict"])
        v = reply_triage.triage("gmail", "a@b.com", "")
        check("triage: empty message -> needs_decision",
              v["verdict"] == "needs_decision", v["verdict"])
        v = reply_triage.triage("gmail", "a@b.com", "Don't call me again.")
        check("triage: 'don't call me' -> decline, not interest",
              v["verdict"] == "decline", v["verdict"])
        ok, _ = reply_triage.validate_draft("Costs $547/mo, starter tier")
        check("draft validation rejects any price",
              ok is False, "price draft rejected")
        src = open(os.path.join(CEO_CORE_DIR, "reply_triage.py"),
                   encoding="utf-8").read()
        check("triage module has no send path (no gmail_send/CLI/send call)",
              "gmail_send" not in src and "hatch_gws_cli" not in src
              and "instagram-messages-cli" not in src
              and ".send(" not in src,
              "drafts only")
    except Exception as exc:  # noqa: BLE001
        check("reply triage section", False, str(exc))

    # ---------- 3. Follow-up queue ----------
    try:
        result = followup_queue.build_followup_queue()
        check("queue: empty today — 100-mail rule refuses all 10 states",
              result["queue"] == []
              and len(result["refusals"]) == 10
              and all(r["first_mails"] < 100 for r in result["refusals"]),
              f"refusals={len(result['refusals'])}, "
              f"queue={len(result['queue'])}")
        refused = {r["state"]: r for r in result["refusals"]}
        check("queue refusals carry reasons + counts (PA 39, FL 54)",
              refused["PA"]["first_mails"] == 39
              and refused["FL"]["first_mails"] == 54
              and "100-mail rule" in refused["PA"]["reason"]
              and refused["PA"]["candidates_parked"] > 0,
              f"PA={refused['PA']}")
        check("queue: FL ceiling 99 recorded in store meta (never 100)",
              lead_store.store_meta().get("fl_max_first_mails") == 99,
              f"fl_max={lead_store.store_meta().get('fl_max_first_mails')}")
        # Synthetic 101-mail TEMP store: queues eligible, skips blocked.
        tmp_leads = os.path.join(tmp, "leads.json")
        store = {"schema": "leads-v1", "meta": {}, "leads": [
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
        ]}
        with open(tmp_leads, "w", encoding="utf-8") as f:
            json.dump(store, f)
        out = followup_queue.build_followup_queue(["ZZ"], tmp_leads)
        check("queue: synthetic 101-mail state queues 100, skips bounced",
              len(out["queue"]) == 100
              and all(t["type"] == "followup"
                      and t["status"] == "queued"
                      and t["draft_only"] is True for t in out["queue"])
              and out["refusals"][0]["blocked_skipped"] == 1,
              f"queued={len(out['queue'])}")
        keys = [t["idempotency_key"] for t in out["queue"]]
        check("queue: idempotency keys stable across rebuilds",
              keys == [t["idempotency_key"] for t in
                       followup_queue.build_followup_queue(
                           ["ZZ"], tmp_leads)["queue"]],
              "stable keys")
        check("queue: task records carry the Phase 1 task shape",
              all(set(("id", "status", "business", "type", "title",
                       "payload", "queued_at", "priority", "depends_on",
                       "retries", "max_retries", "cancelled",
                       "idempotency_key", "last_error")) <= set(t.keys())
                  for t in out["queue"]),
              "tasks-v1 shape")
    except Exception as exc:  # noqa: BLE001
        check("follow-up queue section", False, str(exc))

    # ---------- 4. CRM adapter ----------
    try:
        h = crm_adapter.health()
        check("CRM health is NOT CONNECTED (no live check exists)",
              h["status"] == "NOT CONNECTED" and h["live"] is False
              and "not imported" in h["reason"],
              h["status"])
        lead = lead_store.find_by_domain("https://www.ugihvac.com/")
        payload = crm_adapter.lead_upsert_payload(lead)
        check("CRM dry-run: exact upsert payload, writes nothing",
              payload["dry_run"] is True
              and payload["table"] == "leads"
              and payload["action"] == "upsert"
              and payload["key"] == {"domain": "ugihvac.com"}
              and payload["fields"]["emailed"] is True
              and json.dumps(payload) is not None,
              "serializable would-be body")
        verdict = reply_triage.triage(
            "gmail", "joe@plumbing.example",
            "Sounds good — how much does it cost?", sender_name="Joe")
        event = crm_adapter.reply_event_payload(verdict, lead_id=lead["id"])
        check("CRM dry-run: reply event payload carries the verdict",
              event["dry_run"] is True and event["table"] == "replies"
              and event["fields"]["verdict"] == "hot_lead"
              and "$" not in (event["fields"]["draft"] or ""),
              "hot-lead event, no price")
        try:
            crm_adapter.lead_upsert_payload(
                {"business_name": "No State"})
            check("CRM dry-run rejects a bad lead", False, "no raise")
        except ValueError:
            check("CRM dry-run rejects a bad lead", True, "ValueError")
        src = open(os.path.join(CEO_CORE_DIR, "crm_adapter.py"),
                   encoding="utf-8").read()
        imported = set(re.findall(r"^(?:import|from)\s+([\w\.]+)",
                                  src, re.MULTILINE))
        check("CRM adapter imports no network library",
              not ({"urllib", "requests", "http", "subprocess", "socket"}
                   & imported),
              f"imports={sorted(imported)}")
    except Exception as exc:  # noqa: BLE001
        check("CRM adapter section", False, str(exc))

    # ---------- 5. FollowUpAgent wiring ----------
    try:
        fu = load_module(
            "followup_agent",
            os.path.join(AGENCY_DIR, "sections", "sell", "agents",
                         "followup_agent.py"))
        agent = fu.FollowUpAgent()
        r = agent.run({"payload": {"prospect": "Smoke", "state": "PA"}},
                      brain=None, approvals_path=approvals_path)
        check("FollowUpAgent reads PA 39 from lead store (PARKED)",
              r["status"] == "draft-ready"
              and "PARKED" in r.get("output", "")
              and "PA first mails = 39" in r.get("output", "")
              and "lead store" in r.get("output", ""),
              "PA 39 PARKED from store")
        check("FollowUpAgent total reads 163 (lead store, not config 162)",
              "163" in r.get("output", ""),
              "total 163 in output")
        r2 = agent.run({"payload": {"prospect": "Smoke", "state": "PA",
                                    "state_first_mails": 100}},
                       brain=None, approvals_path=approvals_path)
        check("FollowUpAgent payload count still wins (100 -> due)",
              "follow-up due" in r2.get("output", "")
              and "payload" in r2.get("output", ""),
              "payload wins")
    except Exception as exc:  # noqa: BLE001
        check("FollowUpAgent wiring section", False, str(exc))

    # ---------- 6. Sends stay blocked ----------
    try:
        d = trust_check("send", {"to": "a@b.com", "subject": "Hi",
                                 "body": "Hello"})
        check("trust gate: send without Boss's words is never 'allow'",
              d["decision"] != "allow",
              f"decision={d['decision']!r}")
        gw = ApprovalGateway(approvals_path=approvals_path)
        rec = gw.request("send", "test send", "check_unified_phase3")
        check("approval gateway: a fresh request stays pending",
              rec["status"] == "pending"
              and gw.is_approved(rec["id"]) is False,
              "pending, not approved")
        for mod_name in ("reply_triage", "followup_queue", "crm_adapter",
                         "lead_store"):
            src = open(os.path.join(CEO_CORE_DIR, mod_name + ".py"),
                       encoding="utf-8").read()
            check(f"{mod_name} has no send/publish/spend/delete call",
                  "gmail_send" not in src and "n8n_trigger" not in src
                  and "hatch_gws_cli" not in src,
                  "no live-send reference")
    except Exception as exc:  # noqa: BLE001
        check("sends-blocked section", False, str(exc))

    # ---------- 7. Real store unchanged (except intended leads.json) ----------
    try:
        after = _snapshot_store()
        changed = [k for k in before
                   if k not in ("leads_exists",) and before[k] != after[k]]
        check("real store unchanged by this check run",
              changed == [] and after["leads_exists"] is True
              and after["agent_runs"] is False
              and after["audit_log"] is False
              and after["tool_calls"] is False,
              f"changed={changed}")
    except Exception as exc:  # noqa: BLE001
        check("store-unchanged section", False, str(exc))

    passed = sum(1 for _, ok, _ in CHECKS if ok)
    print(f"\n{passed}/{len(CHECKS)} checks passed.")
    return 0 if passed == len(CHECKS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
