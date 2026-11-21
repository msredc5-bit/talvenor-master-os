#!/usr/bin/env python3
"""check_gate.py — Improvement Phase 1 self-check (trust gate as code).

Nod's systematic pattern (trust.ts + approvals.ts) in Python:
  1. trust_gate.py imports standalone, fast, no network
  2. GATE_WORD_FOR_ACTION matches human_approval_gateway's mapping
  3. Read/draft free — allow without owner words
  4. Unknown action -> ask (not deny, not allow)
  5. No owner words -> ask
  6. Over the spend cap ($0) -> deny
  7. Spend amount 0 / no amount -> not deny (ask)
  8. Dental/medical/patient-health -> deny
  9. Unverified quote -> deny
 10. Verified quote + coverage -> allow
 11. Verified quote, no gate word -> ask
 12. Verified quote, no material target -> ask
 13. gmail_send PAUSED -> ask (not deny), PAUSED note stays
 14. Email restart quote -> PAUSED note goes, allow if coverage
 15. Dispatcher: mock tool draft-ready (as before)
 16. Dispatcher: gated gmail_send/n8n_trigger, no context ->
     pending-approval x2, exactly 1 approval each, handler does not run
 17. Dispatcher: dental args -> blocked-trust, approval 0
 18. Dispatcher: spend $5 -> blocked-trust, approval 0
 19. Dispatcher: verified quote + coverage -> pending-approval
     (the gateway is final — trust allow does not mean execute), trust allow
 20. ConfirmationStore: create -> approve (wrong word forbidden) ->
     execute once -> re-execute forbidden; fail -> uncertain, re-run forbidden;
     a new confirmation for repeats; decline/expire; gateway link
 21. No secrets in trust_gate.py / tool_calling.py
 22. Real store unchanged by this check run

All checks run in TEMP files — the real store is only read, never written.
Stdlib only, no network, no spend, no send. Exit 0 = PASS.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def _snapshot_store():
    snap = {}
    store_dir = os.path.join(BASE, "store")
    for name in sorted(os.listdir(store_dir)):
        path = os.path.join(store_dir, name)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as f:
                    snap[name] = f.read()
            except OSError:
                snap[name] = None
    return snap


def main():
    store_before = _snapshot_store()
    tmp_dir = tempfile.mkdtemp()

    # 1. Imports standalone, fast, no network.
    try:
        t0 = time.time()
        proc = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, "
             f"{CEO_CORE_DIR!r}); import trust_gate; "
             "print('trust_gate import OK')"],
            capture_output=True, text=True, timeout=30, cwd=BASE)
        elapsed = time.time() - t0
        check("trust_gate.py imports standalone, fast, no network",
              proc.returncode == 0 and elapsed < 10,
              f"{elapsed:.2f}s, rc={proc.returncode}")
    except Exception as e:  # noqa: BLE001
        check("trust_gate.py imports standalone, fast, no network", False, str(e))

    try:
        from trust_gate import (  # noqa: PLC0415
            GATE_WORD_FOR_ACTION, ConfirmationStore, trust_check)
        from human_approval_gateway import (  # noqa: PLC0415
            GATE_WORD_FOR_ACTION as GW_GATE_WORDS, ApprovalGateway)

        # 2. Gate-word mirror in sync.
        check("gate-word table matches human_approval_gateway",
              GATE_WORD_FOR_ACTION == GW_GATE_WORDS,
              f"trust_gate={GATE_WORD_FOR_ACTION}")

        # 3. Read/draft free.
        free = all(trust_check(a, {})["decision"] == "allow"
                   for a in ("read", "draft", "status", "search", "list"))
        check("read/draft actions allow without owner words", free)

        # 4. Unknown action -> ask.
        check("unknown action -> ask (not allow, not deny)",
              trust_check("teleport", {})["decision"] == "ask")

        # 5. No owner words -> ask.
        check("no owner words -> ask",
              trust_check("send", {"to": "a@b.com"})["decision"] == "ask")

        # 6. Spend above $0 cap -> deny.
        check("spend above $0 cap -> deny",
              trust_check("spend", {"amount_usd": 5, "purpose": "ads"})["decision"] == "deny")

        # 7. Spend amount 0 / missing -> not deny.
        d0 = trust_check("spend", {"amount_usd": 0, "purpose": "x"})["decision"]
        dn = trust_check("spend", {"purpose": "x"})["decision"]
        check("spend $0 / no amount -> not deny",
              d0 != "deny" and dn != "deny", f"$0={d0}, missing={dn}")

        # 8. Excluded niches -> deny.
        deny_dental = trust_check("send", {"to": "x@dentalcare.com"})["decision"] == "deny"
        deny_medical = trust_check("publish", {"platform": "facebook", "caption": "medical clinic"})["decision"] == "deny"
        deny_ph = trust_check("send", {"to": "a@b.com", "subject": "patient-health"})["decision"] == "deny"
        check("dental/medical/patient-health -> deny",
              deny_dental and deny_medical and deny_ph)

        # 9. Unverified quote -> deny.
        d = trust_check("send", {"to": "a@b.com"},
                        owner_words=["Day 4 batch send"],
                        owner_source="Boss: Today is a holiday")
        check("unverified quote -> deny",
              d["decision"] == "deny" and "not found verbatim" in d["basis"][0])

        # 10. Verified quote + coverage -> allow.
        d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
                        owner_words=["Day 4 batch send — email a@b.com"],
                        owner_source="Boss (chat): Day 4 batch send — email a@b.com",
                        tool_name="gmail_send")
        check("verified quote + coverage -> allow",
              d["decision"] == "allow" and len(d["quotes_verified"]) == 1, str(d))

        # 11. Verified quote, no gate word -> ask.
        d = trust_check("send", {"to": "a@b.com"},
                        owner_words=["write an email to a@b.com"],
                        owner_source="Boss: write an email to a@b.com",
                        tool_name="gmail_send")
        check("verified quote without gate word -> ask",
              d["decision"] == "ask", str(d))

        # 12. Verified quote, no material target -> ask.
        d = trust_check("send", {"to": "someone@example.com"},
                        owner_words=["email send"],
                        owner_source="Boss: email send",
                        tool_name="gmail_send")
        check("verified quote without material target -> ask",
              d["decision"] == "ask", str(d))

        # 13. gmail_send PAUSED -> ask (not deny), PAUSED note stays.
        d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
                        tool_name="gmail_send")
        check("gmail_send while PAUSED -> ask (not deny), PAUSED noted",
              d["decision"] == "ask"
              and any("PAUSED" in b for b in d["basis"]), str(d))

        # 14. Email restart quote -> PAUSED note goes, allow if coverage.
        d = trust_check("send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
                        owner_words=["email restart — send an email to a@b.com"],
                        owner_source="Boss: email restart — send an email to a@b.com",
                        tool_name="gmail_send")
        check("email restart quote lifts PAUSED note, allow with coverage",
              d["decision"] == "allow"
              and not any("PAUSED" in b for b in d["basis"]), str(d))
    except Exception as e:  # noqa: BLE001
        for name in ("gate-word table matches human_approval_gateway",
                     "read/draft actions allow without owner words",
                     "unknown action -> ask (not allow, not deny)",
                     "no owner words -> ask",
                     "spend above $0 cap -> deny",
                     "spend $0 / no amount -> not deny",
                     "dental/medical/patient-health -> deny",
                     "unverified quote -> deny",
                     "verified quote + coverage -> allow",
                     "verified quote without gate word -> ask",
                     "verified quote without material target -> ask",
                     "gmail_send while PAUSED -> ask (not deny), PAUSED noted",
                     "email restart quote lifts PAUSED note, allow with coverage"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 15-19. Dispatcher wiring (TEMP paths, real tools.json read-only).
    try:
        import tool_calling  # noqa: PLC0415

        registry = tool_calling.ToolRegistry.load_from_json(
            os.path.join(CEO_CORE_DIR, "tools.json"))
        tmp_appr = os.path.join(tmp_dir, "approvals-test.json")
        tmp_log = os.path.join(tmp_dir, "tool_calls-test.json")
        tmp_ledger = os.path.join(tmp_dir, "usage_ledger-test.json")

        # 15. Mock tool — draft-ready, as before.
        r = tool_calling.call_tool(
            "draft_email", {"business_name": "ABC Plumbing", "topic": "missed calls"},
            registry=registry, approvals_path=tmp_appr, calls_log_path=tmp_log,
            ledger_path=tmp_ledger)
        check("dispatcher: mock tool still draft-ready",
              r["status"] == "draft-ready" and r["draft_only"] is True, str(r))

        # 16. Gated live tools, no context -> pending-approval x2, 1 approval each.
        gw = ApprovalGateway(approvals_path=tmp_appr)
        before = len(gw.records)
        results16 = [tool_calling.call_tool(
            t, a, registry=registry, approvals_path=tmp_appr,
            calls_log_path=tmp_log, ledger_path=tmp_ledger)
            for t, a in (("gmail_send", {"to": "t@example.com", "subject": "Hi", "body": "Hello"}),
                         ("n8n_trigger", {"payload": {"x": 1}}))]
        gw = ApprovalGateway(approvals_path=tmp_appr)
        check("dispatcher: gmail_send/n8n_trigger -> pending-approval x2, 1 approval each",
              all(x["status"] == "pending-approval" for x in results16)
              and all(x["trust"]["decision"] == "ask" for x in results16)
              and len(gw.records) - before == 2
              and "Nothing was executed" in results16[0]["note"],
              f"statuses={[x['status'] for x in results16]}, approvals+={len(gw.records) - before}")

        # 17. Dental args -> blocked-trust, approval 0.
        before = len(ApprovalGateway(approvals_path=tmp_appr).records)
        r = tool_calling.call_tool(
            "gmail_send", {"to": "care@dental.com", "subject": "Hi", "body": "x"},
            registry=registry, approvals_path=tmp_appr, calls_log_path=tmp_log,
            ledger_path=tmp_ledger)
        after = len(ApprovalGateway(approvals_path=tmp_appr).records)
        check("dispatcher: dental args -> blocked-trust, 0 approvals",
              r["status"] == "blocked-trust" and after == before, str(r))

        # 18. Spend $5 via engine stub tool -> blocked-trust, approval 0.
        import importlib.util  # noqa: PLC0415
        spec = importlib.util.spec_from_file_location(
            "engine_tool_calling_check",
            os.path.join(BASE, "01-Agency-Department", "engine", "tool_calling.py"))
        engine_tc = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine_tc)
        before = len(ApprovalGateway(approvals_path=tmp_appr).records)
        r = engine_tc.call("spend", {"amount_usd": 5, "purpose": "ads"},
                           approvals_path=tmp_appr, calls_log_path=tmp_log,
                           ledger_path=tmp_ledger)
        after = len(ApprovalGateway(approvals_path=tmp_appr).records)
        check("dispatcher: engine spend $5 -> blocked-trust, 0 approvals",
              r["status"] == "blocked-trust" and after == before, str(r))

        # 19. Verified quote + coverage -> pending-approval (gateway is final),
        # trust allow.
        r = tool_calling.call_tool(
            "gmail_send", {"to": "a@b.com", "subject": "Hi", "body": "x"},
            context={"owner_words": ["Day 4 batch send — email a@b.com"],
                     "owner_source": "Boss (chat): Day 4 batch send — email a@b.com"},
            registry=registry, approvals_path=tmp_appr, calls_log_path=tmp_log,
            ledger_path=tmp_ledger)
        check("dispatcher: verified quote -> pending-approval, trust allow",
              r["status"] == "pending-approval"
              and r["trust"]["decision"] == "allow"
              and r["approval"]["status"] == "pending", str(r))
    except Exception as e:  # noqa: BLE001
        for name in ("dispatcher: mock tool still draft-ready",
                     "dispatcher: gmail_send/n8n_trigger -> pending-approval x2, 1 approval each",
                     "dispatcher: dental args -> blocked-trust, 0 approvals",
                     "dispatcher: engine spend $5 -> blocked-trust, 0 approvals",
                     "dispatcher: verified quote -> pending-approval, trust allow"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 20. ConfirmationStore lifecycle (TEMP paths).
    try:
        from trust_gate import ConfirmationStore  # noqa: PLC0415

        tmp_conf = os.path.join(tmp_dir, "confirmations-test.json")
        tmp_appr2 = os.path.join(tmp_dir, "approvals2-test.json")
        store = ConfirmationStore(confirmations_path=tmp_conf,
                                  approvals_path=tmp_appr2)
        c = store.create("send", {"to": "a@b.com", "subject": "Hi"},
                         "Send the Day 4 batch?", "Main CEO Bot")
        ok_create = (c["status"] == "asked" and c["approval_id"]
                     and c["args_canonical"] == '{"subject": "Hi", "to": "a@b.com"}')
        try:
            store.approve(c["id"], gate_word="ok")
            ok_wrong = False
        except ValueError:
            ok_wrong = True
        store.approve(c["id"], gate_word="send")
        gw2 = ApprovalGateway(approvals_path=tmp_appr2)
        ok_linked = gw2.is_approved(c["approval_id"]) is True
        ran = []
        out = store.execute_once(c["id"], lambda a: ran.append(a) or "sent-ok")
        ok_exec = (out["status"] == "executed"
                   and ran == [{"subject": "Hi", "to": "a@b.com"}])
        try:
            store.execute_once(c["id"], lambda a: "again")
            ok_reexec = False
        except ValueError:
            ok_reexec = True
        # Fail -> uncertain, never re-run.
        c2 = store.create("send", {"to": "b@c.com"}, "Test?", "Main CEO Bot")
        store.approve(c2["id"], gate_word="send")
        def _boom(_args):
            raise RuntimeError("network down mid-send")
        try:
            store.execute_once(c2["id"], _boom)
            ok_fail = False
        except ValueError as exc:
            ok_fail = "UNCERTAIN" in str(exc)
        ok_uncertain = (store.get(c2["id"])["status"] == "uncertain")
        try:
            store.execute_once(c2["id"], lambda a: "retry")
            ok_no_retry = False
        except ValueError:
            ok_no_retry = True
        # Repeat needs a NEW confirmation.
        c3 = store.create("send", {"to": "a@b.com", "subject": "Hi"},
                          "Send the Day 4 batch again?", "Main CEO Bot")
        store.approve(c3["id"], gate_word="send")
        out3 = store.execute_once(c3["id"], lambda a: "sent-again")
        ok_repeat = out3["status"] == "executed" and c3["id"] != c["id"]
        # Decline / expire / unknown action.
        c4 = store.create("publish", {"platform": "facebook", "caption": "x", "asset": "y"},
                          "Shall I post?", "Main CEO Bot")
        store.decline(c4["id"])
        c5 = store.create("publish", {"platform": "facebook", "caption": "x", "asset": "y"},
                          "Shall I post?", "Main CEO Bot")
        store.expire(c5["id"])
        ok_de = (store.get(c4["id"])["status"] == "declined"
                 and store.get(c5["id"])["status"] == "expired")
        try:
            store.create("upload", {"file": "x.mp4"}, "Upload?", "Main CEO Bot")
            ok_unknown = False
        except ValueError:
            ok_unknown = True
        check("confirmation lifecycle: create/approve/execute-once/no-reexec",
              ok_create and ok_wrong and ok_linked and ok_exec and ok_reexec,
              f"create={ok_create} wrong={ok_wrong} linked={ok_linked} "
              f"exec={ok_exec} no-reexec={ok_reexec}")
        check("confirmation lifecycle: fail -> uncertain, never re-runs",
              ok_fail and ok_uncertain and ok_no_retry)
        check("confirmation lifecycle: repeat needs new confirmation; decline/expire; unknown action rejected",
              ok_repeat and ok_de and ok_unknown)
    except Exception as e:  # noqa: BLE001
        for name in ("confirmation lifecycle: create/approve/execute-once/no-reexec",
                     "confirmation lifecycle: fail -> uncertain, never re-runs",
                     "confirmation lifecycle: repeat needs new confirmation; decline/expire; unknown action rejected"):
            if not any(r[0] == name for r in results):
                check(name, False, str(e))

    # 21. No secrets in the new/changed files.
    try:
        secret_re = re.compile(
            r"hsurr:|sk-[A-Za-z0-9]|api_key\s*=|password\s*=|"
            r"Authorization.{0,20}Bearer [A-Za-z0-9]")
        bad = []
        for rel in ("00-CEO-Core/trust_gate.py", "00-CEO-Core/tool_calling.py",
                    "01-Agency-Department/engine/tool_calling.py"):
            path = os.path.join(BASE, rel)
            with open(path, encoding="utf-8") as f:
                for lineno, line in enumerate(f, 1):
                    if secret_re.search(line):
                        bad.append(f"{rel}:{lineno}")
        check("no secrets in trust_gate.py / tool_calling.py (core+engine)",
              not bad, "; ".join(bad[:5]) if bad else "clean")
    except Exception as e:  # noqa: BLE001
        check("no secrets in trust_gate.py / tool_calling.py (core+engine)",
              False, str(e))

    # 22. Real store unchanged by this check run.
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else "CHANGED")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_gate: ALL PASS (Improvement Phase 1 — trust gate as code).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
