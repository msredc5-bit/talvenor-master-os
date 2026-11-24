#!/usr/bin/env python3
"""check_agent_runtime.py — Local-first Phase 3 self-check for the
bounded agent runtime (loop + context + subagents + delegation +
runner wiring + gate preservation + skill loading).

What it checks (offline ONLY — no network, no live call, ever; mock
brain only, $0):
  1. Loop: iteration cap enforced.
  2. Loop: wall-clock timeout enforced (0s budget, and after a slow step).
  3. Loop: cost limit $0 enforced — continue-step over cap, done-step
     over cap (coordinator fix a), negative cost -> error (fix a),
     non-numeric cost -> error; CostTracker.record never raises on a
     negative cost (no raising guard in record).
  4. Loop: a step that raises ends "error" and never crashes the caller.
  5. Context: child_context inherits the parent's deadline (fix b);
     child mutation leaves the parent untouched.
  6. Subagents: spawn ok; parallel results in input order; isolated
     child contexts; result-contract validation (good accepted, bad
     rejected); raising fn -> "error"; overrun -> "timeout".
  7. Delegation: decompose (steps list + single-step); execute
     completed (all ok, cost 0.0); execute partial + decompose failure
     -> "partial"/"error" dicts, never raises.
  8. Runner: delegation wiring (fix c) — run_task(delegate=True) with
     a steps list engages execute(); _coerce_result maps completed /
     partial / error (partial names the failed steps, output is the
     WHOLE delegation dict, iterations = len(steps)); a single-step
     task with delegate=True falls back to the mock loop.
  9. Gate preservation: gmail_send / n8n_trigger / send / publish /
     spend / delete -> pending-approval, never executed; draft tools
     and the "draft" verb allowed; unknown action fails closed;
     coordinator fix (d): {"tool": "draft_email", "action": "send"}
     is gated, while {"tool": "draft_email"} and {"action": "draft"}
     stay allowed.
 10. Skill loading via the finder through the runtime: skill_query
     "backup" loads backup-recovery-agent read-only.
 11. No live calls: source-scan of the agent_runtime package for
     forbidden network imports/calls (requests, urllib, http.client,
     socket); the mock step reports mock_brain + draft_only.
 12. Real store unchanged by this check run (store/*.json contents
     snapshotted before and after; the skill-finder execution log is
     redirected to os.devnull, so logs/ is never touched either).

Stdlib only. Run: python3 scripts/check_agent_runtime.py
"""

import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

results = []  # (name, status, detail); status in PASS / FAIL / SKIP / BLOCKED


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    results.append((name, status, detail))
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))


def skip(name, reason):
    results.append((name, "SKIP", reason))
    print(f"[SKIP] {name} — {reason}")


def blocked(name, reason):
    results.append((name, "BLOCKED", reason))
    print(f"[BLOCKED] {name} — {reason}")


def _snapshot_store():
    """Contents of the real store JSONs — this check's only job is to
    prove this run did not change them."""
    snap = {}
    store_dir = os.path.join(BASE, "store")
    for name in sorted(os.listdir(store_dir)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(store_dir, name), encoding="utf-8") as f:
                snap[name] = f.read()
        except OSError:
            snap[name] = None
    return snap


def main():
    store_before = _snapshot_store()

    try:
        from agent_runtime import (  # noqa: PLC0415
            AgentRuntime, BoundedLoop, RuntimeContext, RuntimeLimits,
        )
        from agent_runtime import gate as runtime_gate  # noqa: PLC0415
        from agent_runtime.delegation import (  # noqa: PLC0415
            DelegationEngine, decompose_task,
        )
        from agent_runtime.subagents import (  # noqa: PLC0415
            SubagentManager, SubagentSpec, validate_result,
        )
        from agent_runtime.limits import CostTracker  # noqa: PLC0415
    except ImportError as e:  # noqa: BLE001
        check("agent_runtime imports", False, str(e))
        print("\n0/1 checks passed.")
        return 1

    # Redirect the skill-finder execution log to os.devnull so the
    # skill-loading check never touches logs/skill_executions.jsonl.
    try:
        import skill_finder as sf  # noqa: PLC0415
        sf.LOG_PATH = os.devnull
    except ImportError:
        sf = None

    def _ctx(limits=None, task=None):
        return RuntimeContext(task or {"id": "t"}, limits or RuntimeLimits())

    # 1. Iteration cap enforced.
    try:
        calls = {"n": 0}

        def _always_continue(ctx):
            calls["n"] += 1
            return {"status": "continue", "cost_usd": 0.0}

        # NOTE: BoundedLoop.run() enforces context.limits (the
        # context carries the limits; AgentRuntime always passes the
        # same limits to both), so the cap is set on the context.
        r = BoundedLoop().run(
            _always_continue, _ctx(RuntimeLimits(max_iterations=3)))
        ok = (r.status == "iteration_limit" and r.iterations == 3
              and calls["n"] == 3)
        check("loop: iteration cap enforced (3 continue steps)",
              ok, f"status={r.status}, iterations={r.iterations}, "
              f"calls={calls['n']}")
    except Exception as e:  # noqa: BLE001
        check("loop: iteration cap enforced (3 continue steps)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 2a. Wall-clock timeout enforced — zero budget.
    try:
        r = BoundedLoop().run(
            lambda ctx: {"status": "done", "cost_usd": 0.0},
            _ctx(RuntimeLimits(wall_clock_seconds=0.0)))
        ok = r.status == "timeout" and r.iterations == 0
        check("loop: wall-clock timeout enforced (0s budget)",
              ok, f"status={r.status}, iterations={r.iterations}")
    except Exception as e:  # noqa: BLE001
        check("loop: wall-clock timeout enforced (0s budget)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 2b. Wall-clock timeout enforced — after a slow step.
    try:
        def _slow(ctx):
            time.sleep(0.3)
            return {"status": "continue", "cost_usd": 0.0}

        r = BoundedLoop().run(
            _slow, _ctx(RuntimeLimits(wall_clock_seconds=0.1)))
        ok = r.status == "timeout" and r.iterations == 1
        check("loop: wall-clock timeout enforced (slow step overruns)",
              ok, f"status={r.status}, iterations={r.iterations}")
    except Exception as e:  # noqa: BLE001
        check("loop: wall-clock timeout enforced (slow step overruns)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 3a. Cost limit: continue-step over the $0 cap.
    try:
        def _costly_continue(ctx):
            return {"status": "continue", "cost_usd": 0.01}

        r = BoundedLoop().run(_costly_continue, _ctx())
        ok = r.status == "cost_limit" and r.cost_usd == 0.01
        check("loop: cost limit $0 enforced (continue-step over cap)",
              ok, f"status={r.status}, cost={r.cost_usd}")
    except Exception as e:  # noqa: BLE001
        check("loop: cost limit $0 enforced (continue-step over cap)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 3b. Cost limit: done-step over the $0 cap (fix a — must NOT complete).
    try:
        def _costly_done(ctx):
            return {"status": "done", "output": "finished",
                    "cost_usd": 0.01}

        r = BoundedLoop().run(_costly_done, _ctx())
        ok = r.status == "cost_limit" and r.cost_usd == 0.01
        check("loop: cost limit $0 enforced (done-step over cap, fix a)",
              ok, f"status={r.status}, cost={r.cost_usd}")
    except Exception as e:  # noqa: BLE001
        check("loop: cost limit $0 enforced (done-step over cap, fix a)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 3c. Negative cost -> error (fix a); record() itself never raises.
    try:
        tracker = CostTracker(0.0)
        recorded = tracker.record(-0.5)  # must NOT raise
        r = BoundedLoop().run(
            lambda ctx: {"status": "done", "cost_usd": -0.5}, _ctx())
        ok = (recorded == -0.5 and r.status == "error"
              and "negative" in (r.error or ""))
        check("loop: negative cost -> error; CostTracker.record never "
              "raises (fix a)",
              ok, f"recorded={recorded}, status={r.status}, "
              f"error={r.error}")
    except Exception as e:  # noqa: BLE001
        check("loop: negative cost -> error; CostTracker.record never "
              "raises (fix a)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 3d. Non-numeric cost -> error.
    try:
        r = BoundedLoop().run(
            lambda ctx: {"status": "done", "cost_usd": "abc"}, _ctx())
        ok = r.status == "error" and "numeric" in (r.error or "")
        check("loop: non-numeric cost -> error",
              ok, f"status={r.status}, error={r.error}")
    except Exception as e:  # noqa: BLE001
        check("loop: non-numeric cost -> error",
              False, f"{type(e).__name__}: {e}"[:160])

    # 4. A step that raises ends "error", caller survives.
    try:
        def _boom(ctx):
            raise RuntimeError("boom")

        r = BoundedLoop().run(_boom, _ctx())
        ok = r.status == "error" and "RuntimeError: boom" in (r.error or "")
        check("loop: raising step -> error, caller survives",
              ok, f"status={r.status}, error={r.error}")
    except Exception as e:  # noqa: BLE001
        check("loop: raising step -> error, caller survives",
              False, f"raised through: {type(e).__name__}: {e}"[:160])

    # 5a. Child inherits the parent's deadline (fix b).
    try:
        parent = RuntimeContext({"id": "p"},
                                RuntimeLimits(wall_clock_seconds=10.0))
        child = parent.child_context()
        # Capture each remaining value once: two live reads a moment
        # apart differ by microseconds, so compare with tolerance.
        cr = child.remaining_seconds()
        pr = parent.remaining_seconds()
        ok = (child.deadline == parent.deadline
              and cr <= pr + 0.05 and cr > 9.0)
        check("context: child inherits parent deadline (fix b)",
              ok, f"parent_deadline={parent.deadline:.3f}, "
              f"child_deadline={child.deadline:.3f}, "
              f"child_remaining={child.remaining_seconds():.3f}")
    except Exception as e:  # noqa: BLE001
        check("context: child inherits parent deadline (fix b)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 5b. Child mutation leaves the parent untouched.
    try:
        parent = _ctx(task={"id": "p", "x": 1})
        parent.log_step("seed", "ok", "before")
        child = parent.child_context()
        child.log_step("child", "ok", "mutated")
        child.cost_usd = 9.0
        child.task["x"] = 99
        ok = (len(parent.trace) == 1 and parent.cost_usd == 0.0
              and parent.task["x"] == 1 and len(child.trace) == 2)
        check("context: child mutation leaves parent untouched",
              ok, f"parent_trace={len(parent.trace)}, "
              f"parent_cost={parent.cost_usd}, parent_task_x="
              f"{parent.task['x']}, child_trace={len(child.trace)}")
    except Exception as e:  # noqa: BLE001
        check("context: child mutation leaves parent untouched",
              False, f"{type(e).__name__}: {e}"[:160])

    # 6a. Subagent spawn ok.
    try:
        def _good(child_ctx, data):
            return {"name": "a", "status": "ok", "output": f"got {data}",
                    "evidence": ["mock"], "cost_usd": 0.0}

        res = SubagentManager().spawn(
            SubagentSpec("a", _good, 5.0), "hello", _ctx())
        ok = res["status"] == "ok" and res["output"] == "got hello"
        check("subagent: spawn returns ok result",
              ok, f"status={res['status']}, output={res['output']}")
    except Exception as e:  # noqa: BLE001
        check("subagent: spawn returns ok result",
              False, f"{type(e).__name__}: {e}"[:160])

    # 6b. Parallel results in input order (slowest first).
    try:
        def _timed(child_ctx, data):
            time.sleep(data[1])
            return {"name": data[0], "status": "ok",
                    "output": data[0], "evidence": [], "cost_usd": 0.0}

        specs = [SubagentSpec(n, _timed, 5.0)
                 for n in ("first", "second", "third")]
        inputs = [("first", 0.3), ("second", 0.0), ("third", 0.1)]
        res = SubagentManager().run_parallel(specs, inputs, _ctx())
        ok = ([r["name"] for r in res] == ["first", "second", "third"]
              and all(r["status"] == "ok" for r in res))
        check("subagent: parallel results in input order",
              ok, f"order={[r['name'] for r in res]}")
    except Exception as e:  # noqa: BLE001
        check("subagent: parallel results in input order",
              False, f"{type(e).__name__}: {e}"[:160])

    # 6c. Subagent isolated contexts (parent untouched by child writes).
    try:
        def _mutator(child_ctx, data):
            child_ctx.log_step("child-write", "ok", data)
            child_ctx.cost_usd = 7.0
            child_ctx.task["x"] = 42
            return {"name": "m", "status": "ok", "output": "done",
                    "evidence": [], "cost_usd": 0.0}

        parent = _ctx(task={"id": "p", "x": 1})
        before_trace, before_cost = len(parent.trace), parent.cost_usd
        res = SubagentManager().spawn(
            SubagentSpec("m", _mutator, 5.0), "mark", parent)
        ok = (res["status"] == "ok" and len(parent.trace) == before_trace
              and parent.cost_usd == before_cost
              and parent.task["x"] == 1)
        check("subagent: isolated contexts (child writes leave parent "
              "untouched)",
              ok, f"status={res['status']}, parent_trace="
              f"{len(parent.trace)}, parent_cost={parent.cost_usd}")
    except Exception as e:  # noqa: BLE001
        check("subagent: isolated contexts (child writes leave parent "
              "untouched)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 6d. Result-contract validation: good accepted, bad rejected.
    try:
        good = {"name": "g", "status": "ok", "output": 1,
                "evidence": [], "cost_usd": 0.0}
        bad_cases = [
            {"status": "ok", "output": 1, "evidence": [],
             "cost_usd": 0.0},  # missing name
            dict(good, extra=1),  # extra key
            dict(good, status="weird"),  # bad status
            dict(good, evidence="nope"),  # evidence not a list
            dict(good, cost_usd="free"),  # cost not numeric
        ]
        rejected = 0
        for bad in bad_cases:
            try:
                validate_result(bad)
            except ValueError:
                rejected += 1
        ok = validate_result(good) is True and rejected == len(bad_cases)
        check("subagent: result-contract validation (good accepted, "
              "bad rejected)",
              ok, f"good={validate_result(good)}, "
              f"rejected={rejected}/{len(bad_cases)}")
    except Exception as e:  # noqa: BLE001
        check("subagent: result-contract validation (good accepted, "
              "bad rejected)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 6e. Subagent raising -> "error".
    try:
        def _raises(child_ctx, data):
            raise ValueError("subagent blew up")

        res = SubagentManager().spawn(
            SubagentSpec("r", _raises, 5.0), None, _ctx())
        ok = res["status"] == "error" and "ValueError" in str(res["output"])
        check("subagent: raising fn -> error result",
              ok, f"status={res['status']}, output={res['output']}")
    except Exception as e:  # noqa: BLE001
        check("subagent: raising fn -> error result",
              False, f"raised through: {type(e).__name__}: {e}"[:160])

    # 6f. Subagent overrun -> "timeout".
    try:
        def _slow_fn(child_ctx, data):
            time.sleep(1.0)
            return {"name": "s", "status": "ok", "output": "late",
                    "evidence": [], "cost_usd": 0.0}

        res = SubagentManager().spawn(
            SubagentSpec("s", _slow_fn, 0.1), None, _ctx())
        ok = res["status"] == "timeout"
        check("subagent: overrun -> timeout result",
              ok, f"status={res['status']}")
    except Exception as e:  # noqa: BLE001
        check("subagent: overrun -> timeout result",
              False, f"{type(e).__name__}: {e}"[:160])

    # 7a. Delegation decompose: steps list + single-step.
    try:
        listed = decompose_task({"steps": [{"name": "a"},
                                           {"name": "b", "kind": "x"}]})
        single = decompose_task({"id": "solo"})
        ok = ([s["name"] for s in listed] == ["a", "b"]
              and listed[1]["kind"] == "x"
              and len(single) == 1 and single[0]["name"] == "solo")
        check("delegation: decompose (steps list + single-step)",
              ok, f"listed={[s['name'] for s in listed]}, "
              f"single={[s['name'] for s in single]}")
    except Exception as e:  # noqa: BLE001
        check("delegation: decompose (steps list + single-step)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 7b. Delegation execute completed (all ok, cost 0.0).
    try:
        out = DelegationEngine().execute(
            {"id": "t", "steps": [{"name": "s1"}, {"name": "s2"}]}, _ctx())
        ok = (out["status"] == "completed" and len(out["steps"]) == 2
              and all(s["status"] == "ok" for s in out["steps"])
              and out["cost_usd"] == 0.0)
        check("delegation: execute completed (all steps ok, cost 0.0)",
              ok, f"status={out['status']}, steps={len(out['steps'])}, "
              f"cost={out['cost_usd']}")
    except Exception as e:  # noqa: BLE001
        check("delegation: execute completed (all steps ok, cost 0.0)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 7c. Delegation execute partial + decompose failure: never raises.
    try:
        class _StubManager:
            def run_parallel(self, specs, inputs, parent_context):
                return [
                    {"name": specs[0].name, "status": "ok",
                     "output": "fine", "evidence": [], "cost_usd": 0.0},
                    {"name": specs[1].name, "status": "error",
                     "output": "broke", "evidence": [], "cost_usd": 0.0},
                ]

        partial = DelegationEngine(manager=_StubManager()).execute(
            {"id": "t", "steps": [{"name": "good"}, {"name": "bad"}]},
            _ctx())
        bad_task = DelegationEngine().execute({"steps": "not-a-list"},
                                              _ctx())
        ok = (partial["status"] == "partial"
              and [s["status"] for s in partial["steps"]]
              == ["ok", "error"]
              and bad_task["status"] == "error"
              and bad_task["steps"] == [])
        check("delegation: execute partial + decompose failure, never "
              "raises",
              ok, f"partial={partial['status']}, "
              f"bad_task={bad_task['status']}")
    except Exception as e:  # noqa: BLE001
        check("delegation: execute partial + decompose failure, never "
              "raises",
              False, f"raised: {type(e).__name__}: {e}"[:160])

    # 8a. Runner delegation wiring (fix c): delegate=True engages execute().
    try:
        r = AgentRuntime().run_task(
            {"id": "rt", "steps": [{"name": "research"},
                                   {"name": "draft-caption"},
                                   {"name": "qa"}]},
            delegate=True)
        out = r.output or {}
        ok = (r.status == "completed" and r.iterations == 3
              and r.cost_usd == 0.0 and out.get("status") == "completed"
              and len(out.get("steps", [])) == 3
              and all(s["status"] == "ok" for s in out["steps"]))
        check("runner: delegation wiring — run_task(delegate=True) "
              "engages execute(), whole dict output (fix c)",
              ok, f"status={r.status}, iterations={r.iterations}, "
              f"cost={r.cost_usd}, steps={len(out.get('steps', []))}")
    except Exception as e:  # noqa: BLE001
        check("runner: delegation wiring — run_task(delegate=True) "
              "engages execute(), whole dict output (fix c)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 8b. _coerce_result maps completed / partial / error (fix c).
    try:
        ctx = _ctx()
        partial_in = {"status": "partial", "cost_usd": 0.0, "steps": [
            {"name": "good", "status": "ok", "output": "fine",
             "evidence": [], "cost_usd": 0.0},
            {"name": "broken-step", "status": "error", "output": "broke",
             "evidence": [], "cost_usd": 0.0},
        ]}
        err_in = {"status": "error", "cost_usd": 0.0, "steps": [
            {"name": "only", "status": "error", "output": "broke",
             "evidence": [], "cost_usd": 0.0}]}
        done_in = {"status": "completed", "cost_usd": 0.0, "steps": [
            {"name": "one", "status": "ok", "output": "fine",
             "evidence": [], "cost_usd": 0.0}]}
        p = AgentRuntime._coerce_result(partial_in, ctx)
        e = AgentRuntime._coerce_result(err_in, ctx)
        d = AgentRuntime._coerce_result(done_in, ctx)
        ok = (p.status == "error" and "broken-step" in (p.error or "")
              and p.output is partial_in and p.iterations == 2
              and e.status == "error" and e.output is err_in
              and e.iterations == 1
              and d.status == "completed" and d.output is done_in
              and d.iterations == 1)
        check("runner: _coerce_result maps partial->error (names failed "
              "step), error->error, completed->completed (fix c)",
              ok, f"partial={p.status}/{p.error}, error={e.status}, "
              f"completed={d.status}")
    except Exception as e:  # noqa: BLE001
        check("runner: _coerce_result maps partial->error (names failed "
              "step), error->error, completed->completed (fix c)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 8c. Single-step task with delegate=True falls back to the mock loop.
    try:
        r = AgentRuntime().run_task({"id": "single"}, delegate=True)
        out = r.output or {}
        ok = (r.status == "completed" and out.get("mock_brain") is True
              and out.get("draft_only") is True)
        check("runner: single-step + delegate=True falls back to mock "
              "loop",
              ok, f"status={r.status}, mock_brain={out.get('mock_brain')}")
    except Exception as e:  # noqa: BLE001
        check("runner: single-step + delegate=True falls back to mock "
              "loop",
              False, f"{type(e).__name__}: {e}"[:160])

    # 9a. Gate: gated actions -> pending-approval, never executed.
    try:
        gated = [{"tool": "gmail_send"}, {"tool": "n8n_trigger"},
                 {"action": "send"}, {"action": "publish"},
                 {"action": "spend"}, {"action": "delete"}]
        verdicts = [runtime_gate.enforce_gate(a) for a in gated]
        ok = all(v["allowed"] is False
                 and v["status"] == "pending-approval" for v in verdicts)
        check("gate: gmail_send/n8n_trigger/send/publish/spend/delete "
              "-> pending-approval",
              ok, f"gated={len(verdicts)}, all_pending="
              f"{all(v['status'] == 'pending-approval' for v in verdicts)}")
    except Exception as e:  # noqa: BLE001
        check("gate: gmail_send/n8n_trigger/send/publish/spend/delete "
              "-> pending-approval",
              False, f"{type(e).__name__}: {e}"[:160])

    # 9b. Gate: draft actions allowed.
    try:
        allowed = [{"tool": "draft_email"}, {"action": "draft"},
                   {"tool": "draft_caption"}]
        verdicts = [runtime_gate.enforce_gate(a) for a in allowed]
        ok = all(v["allowed"] is True and v["status"] == "allowed"
                 for v in verdicts)
        check("gate: draft_email / draft / draft_caption allowed",
              ok, f"verdicts={[v['status'] for v in verdicts]}")
    except Exception as e:  # noqa: BLE001
        check("gate: draft_email / draft / draft_caption allowed",
              False, f"{type(e).__name__}: {e}"[:160])

    # 9c. Gate: unknown action fails closed.
    try:
        v1 = runtime_gate.enforce_gate({"tool": "unknown_tool_xyz"})
        v2 = runtime_gate.enforce_gate({"action": "frobnosticate"})
        ok = (v1["allowed"] is False
              and v1["status"] == "pending-approval"
              and v2["allowed"] is False
              and v2["status"] == "pending-approval")
        check("gate: unknown tool/verb fails closed (gated)",
              ok, f"unknown_tool={v1['status']}, "
              f"unknown_verb={v2['status']}")
    except Exception as e:  # noqa: BLE001
        check("gate: unknown tool/verb fails closed (gated)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 9d. Gate fix (d): commit verb on an ungated tool is still gated.
    try:
        v_gated = runtime_gate.enforce_gate(
            {"tool": "draft_email", "action": "send"})
        v_tool = runtime_gate.enforce_gate({"tool": "draft_email"})
        v_verb = runtime_gate.enforce_gate({"action": "draft"})
        ok = (v_gated["allowed"] is False
              and v_gated["status"] == "pending-approval"
              and v_tool["allowed"] is True
              and v_verb["allowed"] is True)
        check("gate: draft_email+send gated, draft_email / draft allowed "
              "(fix d)",
              ok, f"draft_email+send={v_gated['status']}, "
              f"draft_email={v_tool['status']}, draft={v_verb['status']}")
    except Exception as e:  # noqa: BLE001
        check("gate: draft_email+send gated, draft_email / draft allowed "
              "(fix d)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 10. Skill loading via the finder through the runtime.
    try:
        if sf is None:
            skip("runtime: skill_query='backup' loads "
                 "backup-recovery-agent",
                 "skill_finder not importable in this run")
        else:
            r = AgentRuntime().run_task(
                {"id": "sk", "skill_query": "backup"})
            out = r.output or {}
            ok = (r.status == "completed"
                  and out.get("skill") == "backup-recovery-agent"
                  and out.get("skill_loaded") is True
                  and out.get("mock_brain") is True)
            check("runtime: skill_query='backup' loads "
                  "backup-recovery-agent (read-only)",
                  ok, f"status={r.status}, skill={out.get('skill')}, "
                  f"skill_loaded={out.get('skill_loaded')}")
    except Exception as e:  # noqa: BLE001
        check("runtime: skill_query='backup' loads "
              "backup-recovery-agent (read-only)",
              False, f"{type(e).__name__}: {e}"[:160])

    # 11. No live calls: source-scan + mock flags.
    try:
        forbidden = ("requests", "urllib", "http.client", "socket")
        hits = []
        pkg = os.path.join(CEO_CORE_DIR, "agent_runtime")
        for name in sorted(os.listdir(pkg)):
            if not name.endswith(".py"):
                continue
            with open(os.path.join(pkg, name), encoding="utf-8") as f:
                text = f.read()
            for token in forbidden:
                if token in text:
                    hits.append(f"{name}:{token}")
        r = AgentRuntime().run_task({"id": "mock-flag"})
        out = r.output or {}
        ok = (not hits and out.get("mock_brain") is True
              and out.get("draft_only") is True)
        check("no live calls: agent_runtime source-scan clean + mock "
              "step reports mock_brain/draft_only",
              ok, f"forbidden_hits={hits}, mock_brain="
              f"{out.get('mock_brain')}, draft_only={out.get('draft_only')}")
    except Exception as e:  # noqa: BLE001
        check("no live calls: agent_runtime source-scan clean + mock "
              "step reports mock_brain/draft_only",
              False, f"{type(e).__name__}: {e}"[:160])

    # 12. Real store unchanged by this check run.
    try:
        after = _snapshot_store()
        check("real store unchanged by this check run",
              after == store_before,
              "unchanged" if after == store_before else
              f"CHANGED: {[k for k in after if after.get(k) != store_before.get(k)]}")
    except Exception as e:  # noqa: BLE001
        check("real store unchanged by this check run", False, str(e))

    failed = [r for r in results if r[1] == "FAIL"]
    passed = [r for r in results if r[1] == "PASS"]
    skipped = [r for r in results if r[1] == "SKIP"]
    blocked_r = [r for r in results if r[1] == "BLOCKED"]
    decided = len(passed) + len(failed)
    print(f"\n{len(passed)}/{decided} checks passed "
          f"({len(skipped)} skipped, {len(blocked_r)} blocked).")
    if skipped:
        print("SKIPPED:", [r[0] for r in skipped])
    if blocked_r:
        print("BLOCKED:", [r[0] for r in blocked_r])
    if failed:
        print("FAILED:", [r[0] for r in failed])
        return 1
    print("check_agent_runtime: ALL DECIDED CHECKS PASS "
          "(offline — no live call made).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
