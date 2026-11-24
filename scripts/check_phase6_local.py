#!/usr/bin/env python3
"""check_phase6_local.py — Local-first Phase 6 self-check for the
sandbox lead chain + run_office.py lead_chain wiring (Worker C).

What it checks (offline ONLY — no network, no live call, ever;
$0; real n8n is [NOT TESTED]; no live send/deploy anywhere):

  1. lead_chain package imports (ChainRunner, steps, fixtures,
     crm_dryrun) + the chain declares exactly the 13 steps in
     §10.C order (discovery -> verification -> qualification ->
     CRM dry-run -> outreach draft -> reply monitoring -> meeting
     -> sales -> onboarding -> service delivery -> QA ->
     deployment -> monitoring).
  2. All 3 TEST fixtures load, TEST data only (names contain
     TEST, any email on an .example domain, no real lead data).
  3. Happy-path chain on the STRONG fixture in a temp store:
     status partial (gated send held) or blocked (deployment),
     cost 0.0, draft outreach present, send never executed.
  4. Deployment step is always blocked (happy-path result).
  5. Failure fixture (missing email) -> verification error,
     chain failed, later steps skipped with a dependency reason,
     failure recorded in the chain state file.
  6. Duplicate re-run with the same idempotency key returns the
     stored result without re-execution.
  7. CRM dry-run returns the would-be payload, live False,
     nothing written anywhere live (real adapter health is
     NOT CONNECTED).
  8. Gate: a step carrying {"tool": "gmail_send", "action":
     "send"} returns pending-approval through the REAL Phase 3
     gate (WorkflowEngine + agent_runtime.gate).
  9. run_office.py --task lead_chain on a temp store dir
     end-to-end via the REAL CLI path (happy path), with the
     execution recorded in the temp tasks.json.
 10. Real store files unchanged (sha256 of store/tasks.json,
     store/approvals.json, store/leads.json before/after).

Stdlib only. Every temp store is a per-run
tempfile.mkdtemp() dir (never a fixed /tmp path — the Phase 5
check-7 isolation lesson). A check that cannot run because
the lead_chain package is not built yet is marked BLOCKED in
its output, never faked as a pass.

Run: python3 scripts/check_phase6_local.py
Exit 0 = no FAIL (BLOCKED checks are reported, not hidden).
"""

import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
STORE_DIR = os.path.join(BASE, "store")
RUNNER = os.path.join(BASE, "scripts", "run_office.py")

sys.path.insert(0, CEO_CORE_DIR)

# The 13 §10.C step kinds, in order (also the order of the
# handlers in lead_chain/steps.py).
EXPECTED_STEP_KINDS = [
    "lead_discovery", "lead_verification", "lead_qualification",
    "crm_dryrun", "outreach_draft", "reply_monitoring", "meeting",
    "sales_process", "client_onboarding", "service_delivery",
    "qa", "deployment", "monitoring",
]

results = []  # (name, status, detail); status in PASS / FAIL / BLOCKED


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def blocked(name, reason):
    results.append((name, "BLOCKED", reason))
    print(f"[BLOCKED] {name} — {reason}")


def _sha256_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _step_ids(step_list):
    """Normalise a declared step list (dicts or strings) to ids."""
    ids = []
    for item in step_list:
        if isinstance(item, dict):
            ids.append(str(item.get("id") or item.get("kind") or ""))
        else:
            ids.append(str(item))
    return ids


def _load_chain_module():
    """Import the lead_chain package's chain module + ChainRunner.

    Returns (module, ChainRunner class) or raises ImportError.
    Prefers the package export; falls back to lead_chain.chain.
    """
    try:
        import lead_chain  # noqa: PLC0415
        runner_cls = getattr(lead_chain, "ChainRunner", None)
        if runner_cls is not None:
            return lead_chain, runner_cls
    except ImportError:
        pass
    import lead_chain.chain as chain_mod  # noqa: PLC0415
    return chain_mod, chain_mod.ChainRunner


def _declared_step_ids(chain_mod, runner_cls):
    """The chain's declared step order, from wherever it lives."""
    for holder in (chain_mod, runner_cls):
        for attr in ("STEPS", "CHAIN_STEPS", "STEP_ORDER", "STEP_KINDS"):
            value = getattr(holder, attr, None)
            if isinstance(value, (list, tuple)) and value:
                return _step_ids(value)
    return None


def _load_fixtures():
    """Load the TEST fixtures as {fixture_id: prospect dict}.

    Accepts a FIXTURES dict, a get_fixture(id) function, or
    module-level TEST_* dicts. Returns None when the fixtures
    module cannot be loaded.
    """
    import lead_chain.fixtures as fixtures  # noqa: PLC0415
    table = getattr(fixtures, "FIXTURES", None)
    if isinstance(table, dict) and table:
        return dict(table)
    get_fixture = getattr(fixtures, "get_fixture", None)
    ids = getattr(fixtures, "FIXTURE_IDS", None)
    if callable(get_fixture) and isinstance(ids, (list, tuple)):
        out = {}
        for fid in ids:
            out[str(fid)] = get_fixture(fid)
        return out
    out = {}
    for name in dir(fixtures):
        if name.startswith("TEST"):
            value = getattr(fixtures, name)
            if isinstance(value, dict):
                out[name] = value
    return out or None


def _pick_fixture(fixtures, want):
    """Pick the STRONG or the missing-email fixture from the table.

    want: "strong" or "no_email". Returns (fixture_id, prospect).
    """
    for fid, prospect in fixtures.items():
        fid_u = str(fid).upper()
        if want == "strong":
            if "STRONG" in fid_u:
                return fid, prospect
            if isinstance(prospect, dict):
                try:
                    if float(prospect.get("score") or 0) >= 80:
                        return fid, prospect
                except (TypeError, ValueError):
                    pass
                if str(prospect.get("tier") or "") == "Tier 1":
                    return fid, prospect
                if str(prospect.get("strength") or "").upper() \
                        == "STRONG":
                    return fid, prospect
        else:
            if any(tag in fid_u for tag in ("NO_EMAIL", "NOEMAIL",
                                            "MISSING", "NO_CONTACT",
                                            "NOCONTACT")):
                return fid, prospect
            if isinstance(prospect, dict) \
                    and not prospect.get("email"):
                return fid, prospect
    return None, None


def _run_chain(runner_cls, prospect, store_dir, idem_key=None):
    """Run ChainRunner once, honouring its idempotency interface.

    Passes idempotency_key as a run() kwarg when the signature
    accepts it; otherwise injects it into a copy of a dict
    prospect. Returns the ChainRunner result dict.
    """
    try:
        runner = runner_cls()
    except TypeError:
        runner = runner_cls(store_dir)
    run = runner.run
    kwargs = {}
    if idem_key is not None:
        try:
            params = inspect.signature(run).parameters
        except (TypeError, ValueError):
            params = {}
        if "idempotency_key" in params:
            kwargs["idempotency_key"] = idem_key
        elif isinstance(prospect, dict):
            prospect = dict(prospect)
            prospect.setdefault("idempotency_key", idem_key)
    try:
        result = run(prospect, store_dir, **kwargs)
    except TypeError:
        result = run(prospect, **kwargs)
    if not isinstance(result, dict):
        return {"status": "error",
                "error": "ChainRunner.run returned a non-dict result"}
    return result


def _steps_of(result):
    steps = result.get("steps") or result.get("step_results") or []
    return steps if isinstance(steps, list) else []


def _step_by_id(steps, step_id):
    for step in steps:
        if not isinstance(step, dict):
            continue
        if step.get("id") == step_id or step.get("kind") == step_id:
            return step
    return None


def _snapshot_dir(path):
    try:
        return sorted(os.listdir(path))
    except OSError:
        return []


def main():
    store_before = {
        name: _sha256_file(os.path.join(STORE_DIR, name))
        for name in ("tasks.json", "approvals.json", "leads.json")
    }

    chain_mod = None
    runner_cls = None
    fixtures = None
    try:
        chain_mod, runner_cls = _load_chain_module()
    except ImportError as exc:  # noqa: BLE001
        blocked("1. lead_chain package imports + 13 steps in "
                "§10.C order",
                "lead_chain not importable yet: %s" % exc)
        blocked("2. all 3 TEST fixtures load, no real lead data",
                "lead_chain.fixtures not importable yet")
        blocked("3. happy-path chain on STRONG fixture (temp "
                "store)", "ChainRunner not importable yet")
        blocked("4. deployment step always blocked",
                "ChainRunner not importable yet")
        blocked("5. failure fixture (missing email) -> "
                "verification error, chain failed, later steps "
                "skipped, failure recorded",
                "ChainRunner not importable yet")
        blocked("6. duplicate re-run with same idempotency key "
                "returns stored result",
                "ChainRunner not importable yet")
        blocked("9. run_office.py --task lead_chain end-to-end "
                "(temp store)", "ChainRunner not importable yet")
    else:
        # -- 1. Imports + 13 steps in §10.C order ------------------
        try:
            import lead_chain.steps as steps_mod  # noqa: PLC0415
            import lead_chain.crm_dryrun as crm_dryrun  # noqa: PLC0415
            declared = _declared_step_ids(chain_mod, runner_cls)
            ok = (declared == EXPECTED_STEP_KINDS)
            check("1. lead_chain imports + 13 steps in §10.C order",
                  ok,
                  "declared=%s" % (declared,)
                  if not ok else
                  "13 steps, order matches §10.C "
                  "(discovery..monitoring)")
        except Exception as exc:  # noqa: BLE001
            check("1. lead_chain imports + 13 steps in §10.C order",
                  False, f"{type(exc).__name__}: {exc}"[:160])

        # -- 2. All 3 TEST fixtures load, TEST data only -----------
        try:
            fixtures = _load_fixtures()
            problems = []
            if not isinstance(fixtures, dict) or not fixtures:
                problems.append("no fixtures loaded")
                fixtures = None
            else:
                if len(fixtures) != 3:
                    problems.append(f"{len(fixtures)} fixtures "
                                    "(want exactly 3)")
                for fid, prospect in fixtures.items():
                    if not isinstance(prospect, dict):
                        problems.append(f"{fid}: not a dict")
                        continue
                    pid = str(prospect.get("id") or "")
                    if not pid.startswith("TEST-"):
                        problems.append(f"{fid}: prospect id "
                                        f"{pid!r} is not TEST-")
                    name = str(prospect.get("business_name") or "")
                    if "TEST" not in name.upper():
                        problems.append(f"{fid}: business_name "
                                        f"{name!r} is not TEST-")
                    email = prospect.get("email")
                    if email is not None:
                        email = str(email)
                        if ".invalid" not in email \
                                and not email.endswith(".example"):
                            problems.append(
                                f"{fid}: email {email!r} is not a "
                                "clearly fake (.invalid/.example) "
                                "address")
                    website = str(prospect.get("website") or "")
                    if website and ".example" not in website:
                        problems.append(f"{fid}: website {website!r} "
                                        "is not .example")
                    phone = str(prospect.get("phone") or "")
                    if phone and "+1-555-01" not in phone:
                        problems.append(f"{fid}: phone {phone!r} is "
                                        "not a fictional +1-555-01xx "
                                        "number")
            check("2. all 3 TEST fixtures load, no real lead data",
                  not problems,
                  f"{len(fixtures)} fixtures: "
                  f"{sorted(fixtures)}"
                  if fixtures and not problems
                  else "; ".join(problems))
        except Exception as exc:  # noqa: BLE001
            check("2. all 3 TEST fixtures load, no real lead data",
                  False, f"{type(exc).__name__}: {exc}"[:160])

        # -- 3. Happy path on STRONG fixture (temp store) ----------
        happy_result = None
        happy_store = None
        try:
            strong_id, strong = _pick_fixture(fixtures or {},
                                              "strong")
            if strong is None:
                check("3. happy-path chain on STRONG fixture "
                      "(temp store)", False,
                      "no STRONG fixture found in "
                      f"{sorted((fixtures or {}))}")
            else:
                happy_store = tempfile.mkdtemp(prefix="check6-happy-")
                before = _snapshot_dir(happy_store)
                happy_result = _run_chain(runner_cls, strong,
                                          happy_store)
                steps = _steps_of(happy_result)
                outreach = _step_by_id(steps, "outreach_draft")
                detail = str((outreach or {}).get("detail") or "")
                executed = [s.get("id") for s in steps
                            if isinstance(s, dict)
                            and s.get("status") in ("executed", "sent")]
                ok = (
                    happy_result.get("status") in ("partial", "blocked")
                    and happy_result.get("cost_usd") == 0.0
                    and outreach is not None
                    and outreach.get("status") == "pending-approval"
                    and "[DRAFT]" in detail
                    and "draft" in detail.lower()
                    and "send" in detail.lower()
                    and not executed
                    and len(steps) == 13)
                check("3. happy-path chain on STRONG fixture "
                      "(temp store)",
                      ok,
                      f"fixture={strong_id}, "
                      f"status={happy_result.get('status')}, "
                      f"steps={len(steps)}, "
                      f"outreach={outreach.get('status') if outreach else None}, "
                      f"cost={happy_result.get('cost_usd')}, "
                      f"executed={executed}, "
                      f"new files={sorted(set(_snapshot_dir(happy_store)) - set(before))}")
        except Exception as exc:  # noqa: BLE001
            check("3. happy-path chain on STRONG fixture "
                  "(temp store)", False,
                  f"{type(exc).__name__}: {exc}"[:160])

        # -- 4. Deployment step always blocked ---------------------
        try:
            if happy_result is None:
                check("4. deployment step always blocked", False,
                      "no happy-path result (check 3 did not run)")
            else:
                deploy = _step_by_id(_steps_of(happy_result),
                                     "deployment")
                ok = (deploy is not None
                      and deploy.get("status") == "blocked")
                check("4. deployment step always blocked", ok,
                      f"deployment={deploy.get('status') if deploy else None}, "
                      f"error={str(deploy.get('error') or '')[:80] if deploy else 'no step'}")
        except Exception as exc:  # noqa: BLE001
            check("4. deployment step always blocked", False,
                  f"{type(exc).__name__}: {exc}"[:160])

        # -- 5. Failure fixture (missing email) --------------------
        try:
            fail_id, fail = _pick_fixture(fixtures or {}, "no_email")
            if fail is None:
                check("5. failure fixture (missing email) -> "
                      "verification error, chain failed, later "
                      "steps skipped, failure recorded", False,
                      "no missing-email fixture found in "
                      f"{sorted((fixtures or {}))}")
            else:
                fail_store = tempfile.mkdtemp(prefix="check6-fail-")
                before = _snapshot_dir(fail_store)
                result = _run_chain(runner_cls, fail, fail_store)
                steps = _steps_of(result)
                verify = _step_by_id(steps, "verification") \
                    or _step_by_id(steps, "lead_verification")
                ver_err = str((verify or {}).get("error") or "")
                ver_idx = next((i for i, s in enumerate(steps)
                                if isinstance(s, dict)
                                and s.get("id") in ("lead_verification",
                                                    "verification")),
                               None)
                later = steps[ver_idx + 1:] \
                    if ver_idx is not None else []
                skipped = [s for s in later
                           if isinstance(s, dict)
                           and s.get("status") == "skipped"]
                skipped_reasons = [
                    str(s.get("error") or s.get("detail") or "")
                    for s in skipped]
                new_entries = sorted(
                    set(_snapshot_dir(fail_store)) - set(before))
                state_records_failure = False
                state_detail = "no new state file"
                state_paths = []
                for entry in new_entries:
                    full = os.path.join(fail_store, entry)
                    if os.path.isdir(full):
                        for root, _dirs, files in os.walk(full):
                            for name in files:
                                state_paths.append(
                                    os.path.join(root, name))
                    else:
                        state_paths.append(full)
                for path in state_paths:
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                        if "failed" in text and "missing email" in text:
                            state_records_failure = True
                            state_detail = (
                                "state file %s records failure"
                                % os.path.relpath(path, fail_store))
                            break
                    except (OSError, UnicodeDecodeError):
                        continue
                ok = (
                    result.get("status") == "failed"
                    and verify is not None
                    and verify.get("status") == "error"
                    and "missing email" in ver_err
                    and later and len(skipped) == len(later)
                    and all(any(word in reason.lower()
                                for word in ("depend", "skip",
                                            "previous", "failed"))
                            for reason in skipped_reasons)
                    and state_records_failure)
                check("5. failure fixture (missing email) -> "
                      "verification error, chain failed, later "
                      "steps skipped, failure recorded",
                      ok,
                      f"fixture={fail_id}, "
                      f"status={result.get('status')}, "
                      f"verification={verify.get('status') if verify else None} "
                      f"({ver_err[:60]}), "
                      f"later skipped={len(skipped)}/{len(later)}, "
                      f"{state_detail}")
        except Exception as exc:  # noqa: BLE001
            check("5. failure fixture (missing email) -> "
                  "verification error, chain failed, later steps "
                  "skipped, failure recorded", False,
                  f"{type(exc).__name__}: {exc}"[:160])

        # -- 6. Duplicate re-run, same idempotency key -------------
        try:
            strong_id, strong = _pick_fixture(fixtures or {},
                                              "strong")
            if strong is None:
                check("6. duplicate re-run with same idempotency "
                      "key returns stored result", False,
                      "no STRONG fixture found")
            else:
                dup_store = tempfile.mkdtemp(prefix="check6-dup-")
                key = "check6-dup-TEST-STRONG-1"
                first = _run_chain(runner_cls, strong, dup_store,
                                   idem_key=key)
                before = _snapshot_dir(dup_store)
                second = _run_chain(runner_cls, strong, dup_store,
                                    idem_key=key)
                after = _snapshot_dir(dup_store)
                dup_flag = (second.get("duplicate") is True
                            or second.get("cached") is True
                            or second.get("stored_result") is True
                            or second.get("from_store") is True
                            or str(second.get("status") or "")
                            in ("duplicate", "cached"))
                same_steps = (_steps_of(first) == _steps_of(second))
                ok = (dup_flag
                      and second.get("status") == "duplicate"
                      and first.get("status") in ("partial", "blocked",
                                                  "completed")
                      and same_steps and before == after)
                check("6. duplicate re-run with same idempotency "
                      "key returns stored result",
                      ok,
                      f"key={key}, first={first.get('status')}, "
                      f"second={second.get('status')}, "
                      f"duplicate flag={dup_flag}, "
                      f"same steps={same_steps}, "
                      f"no new files={before == after}")
        except Exception as exc:  # noqa: BLE001
            check("6. duplicate re-run with same idempotency key "
                  "returns stored result", False,
                  f"{type(exc).__name__}: {exc}"[:160])

        # -- 9. run_office.py --task lead_chain end-to-end --------
        try:
            strong_id, strong = _pick_fixture(fixtures or {},
                                              "strong")
            if strong is None:
                check("9. run_office.py --task lead_chain "
                      "end-to-end (temp store)", False,
                      "no STRONG fixture found")
            else:
                cli_store = tempfile.mkdtemp(prefix="check6-cli-")
                proc = subprocess.run(
                    [sys.executable, RUNNER, "--business", "agency",
                     "--task", "lead_chain",
                     "--input", json.dumps(
                         {"prospect": strong_id, "execute": True}),
                     "--store-dir", cli_store],
                    capture_output=True, text=True, timeout=300,
                    cwd=BASE)
                result = json.loads(proc.stdout) \
                    if proc.returncode == 0 else {}
                chain_result = result.get("chain_result") or {}
                logged = []
                tasks_path = os.path.join(cli_store, "tasks.json")
                try:
                    with open(tasks_path, "r", encoding="utf-8") as f:
                        logged = json.load(f).get("records", [])
                except (OSError, json.JSONDecodeError):
                    logged = []
                lead_logged = [r for r in logged
                               if r.get("type") == "lead_chain"]
                ok = (
                    proc.returncode == 0
                    and result.get("status") in ("partial", "blocked")
                    and result.get("cost_usd") == 0.0
                    and result.get("routed_to", "").endswith(
                        "lead_chain.ChainRunner")
                    and chain_result.get("status") \
                    == result.get("status")
                    and len(lead_logged) == 1
                    and lead_logged[0].get("status")
                    == result.get("status"))
                check("9. run_office.py --task lead_chain "
                      "end-to-end (temp store)",
                      ok,
                      f"rc={proc.returncode}, "
                      f"status={result.get('status')}, "
                      f"cost={result.get('cost_usd')}, "
                      f"logged={len(lead_logged)} record(s), "
                      f"stderr={(proc.stderr or '').strip()[-120:]}")
        except Exception as exc:  # noqa: BLE001
            check("9. run_office.py --task lead_chain end-to-end "
                  "(temp store)", False,
                  f"{type(exc).__name__}: {exc}"[:160])

    # -- 7. CRM dry-run (independent of ChainRunner) ---------------
    try:
        from lead_chain.crm_dryrun import dry_run_upsert, health  # noqa: PLC0415
        h = health()
        prospect = {"business_name": "TEST Plumbing LLC",
                    "city": "Drexel Hill", "state": "PA",
                    "website": "https://test-plumbing.example",
                    "domain": "test-plumbing.example",
                    "email": "office@test-plumbing.example",
                    "phone": "+1-555-010-0001",
                    "score": 85, "tier": "Tier 1",
                    "source": "TEST fixture"}
        out = dry_run_upsert(prospect)
        payload = out.get("payload") or {}
        ok = (h.get("status") == "NOT CONNECTED"
              and h.get("live") is False
              and out.get("status") == "ok"
              and out.get("dry_run") is True
              and out.get("live") is False
              and payload.get("dry_run") is True
              and payload.get("table") == "leads"
              and payload.get("action") == "upsert"
              and payload.get("key") == {"domain": "test-plumbing.example"}
              and payload.get("fields", {}).get("business_name")
              == "TEST Plumbing LLC")
        check("7. CRM dry-run returns would-be payload, live "
              "False, nothing written anywhere live",
              ok,
              f"health={h.get('status')}, dry_run={out.get('dry_run')}, "
              f"live={out.get('live')}, table={payload.get('table')}, "
              f"key={payload.get('key')}")
    except ImportError as exc:  # noqa: BLE001
        blocked("7. CRM dry-run returns would-be payload, live "
                "False, nothing written anywhere live",
                "lead_chain.crm_dryrun not importable yet: %s" % exc)
    except Exception as exc:  # noqa: BLE001
        check("7. CRM dry-run returns would-be payload, live "
              "False, nothing written anywhere live", False,
              f"{type(exc).__name__}: {exc}"[:160])

    # -- 8. Gate: gmail_send/send -> pending-approval (real gate) --
    try:
        from workflow_engine.engine import WorkflowEngine  # noqa: PLC0415
        engine = WorkflowEngine()
        out = engine.execute({"steps": [
            {"id": "send", "kind": "send",
             "tool": "gmail_send", "action": "send"}]})
        steps = out.get("steps") or []
        step = steps[0] if steps else {}
        ok = (out.get("status") == "partial"
              and step.get("status") == "pending-approval"
              and out.get("cost_usd") == 0.0)
        check("8. gate: gmail_send/send returns pending-approval "
              "through the real gate, never executes",
              ok,
              f"engine={out.get('status')}, "
              f"step={step.get('status')}, cost={out.get('cost_usd')}, "
              f"error={str(out.get('error'))[:60]}")
    except Exception as exc:  # noqa: BLE001
        check("8. gate: gmail_send/send returns pending-approval "
              "through the real gate, never executes", False,
              f"{type(exc).__name__}: {exc}"[:160])

    # -- 10. Real store files unchanged -----------------------------
    try:
        store_after = {
            name: _sha256_file(os.path.join(STORE_DIR, name))
            for name in ("tasks.json", "approvals.json", "leads.json")
        }
        changed = [n for n in store_before
                   if store_before[n] != store_after[n]]
        check("10. real store files unchanged (sha256 tasks.json "
              "+ approvals.json + leads.json before/after)",
              not changed,
              "hashes match" if not changed
              else "CHANGED: " + ", ".join(changed))
    except Exception as exc:  # noqa: BLE001
        check("10. real store files unchanged (sha256 tasks.json "
              "+ approvals.json + leads.json before/after)", False,
              f"{type(exc).__name__}: {exc}"[:160])

    decided = [r for r in results if r[1] in ("PASS", "FAIL")]
    passed = sum(1 for r in decided if r[1] == "PASS")
    blocked_n = sum(1 for r in results if r[1] == "BLOCKED")
    print(f"\nPASS {passed}/{len(decided)} decided checks"
          + (f" ({blocked_n} BLOCKED)" if blocked_n else "")
          + ".")
    return 0 if passed == len(decided) else 1


if __name__ == "__main__":
    sys.exit(main())
