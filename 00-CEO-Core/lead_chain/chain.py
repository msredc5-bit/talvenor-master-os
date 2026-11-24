"""Lead chain — Talvenor Master OS, local-first Phase 6.

The §10.C lead chain from the Master Build Prompt (brief lines
561-647): Lead Discovery -> Verification -> Qualification -> CRM
(dry-run) -> Outreach (draft only) -> Reply Monitoring -> Meeting
-> Sales Process -> Client Onboarding -> Service Delivery -> QA
-> Deployment (ALWAYS BLOCKED) -> Monitoring.

A task is COMPLETED only after execution and verification succeed
(brief §10.C); here that means chain status "completed" only when
every step returns "ok".

Execution path (chosen per the Phase 6 task brief):
  * Most steps run through the Phase 4 WorkflowEngine
    (``00-CEO-Core/workflow_engine/engine.py``), so gate checks are
    the real Phase 3 gate (``agent_runtime/gate.py``). A gated step
    comes back "pending-approval" and NEVER executes.
  * Steps whose outcome depends on the prospect's own data — the
    engine's mock path always returns "ok", so it cannot express
    them — run directly via ``.steps.execute_step`` (Worker B):
    lead_discovery (needs a website), lead_verification (needs
    email/phone), lead_qualification (score / dental-medical DQ),
    crm_dryrun (real CRM-adapter dry-run validation). Each such
    step records ``executed_via`` and why it went direct.

Kind semantics (two consumers, one field):
  * ``CHAIN_STEPS[].kind`` is a Phase 4 MOCK_KIND (draft / research
    / report / qa / status / search / list / read / mock) — that is
    what the engine needs to gate-check the step as a draft verb.
  * ``.steps.execute_step`` dispatches on ``kind`` as the handler
    name, so when the runner calls it directly it passes a copy of
    the step with ``kind`` remapped to the step id. The remap is
    recorded on the step record (``executed_via``).

Failure routing (strict chain, ``on_failure == "stop"`` on every
step): a step returning "error" or "blocked" stops the chain;
later steps are recorded "skipped" with reason
``"dependency: <failed step id>"``. "pending-approval" (the gated
send held) does NOT stop the chain — the draft exists, the send is
held for Boss's exact gate word.

Chain status precedence: "failed" (any step error) > "blocked"
(deployment blocked — the expected sandbox outcome) > "partial"
(any step pending-approval, rest ok) > "completed" (every step ok).
A re-run with the same prospect id returns the stored record with
``"duplicate": True`` and status "duplicate" WITHOUT re-executing
any step (idempotency key = sha256("lead-chain-v1:" + prospect id)).

Persistence: the full chain record is written as JSON to
``<state_dir>/<idempotency_key>.json`` (atomic write via store_io
when importable, else temp-file + os.replace + fsync) and one
structured log line is appended to ``<state_dir>/chain_log.jsonl``.
``state_dir`` is ``store_dir/"chains"`` when a store dir is given,
else a fresh ``tempfile.mkdtemp()`` dir — NEVER the real store
path by default. ``store/leads.json`` is never read or written
here; fixtures are TEST data only.

Stdlib only. $0 (cost_usd is always 0.0). No send, no publish, no
spend, no delete, no deploy, no network, no live calls.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["CHAIN_STEPS", "ChainRunner", "run_lead_chain"]

CHAIN_VERSION = "lead-chain-v1"

# --- The 13 steps -------------------------------------------------------
# "specialist" is the REAL specialist class name, verified from the
# department specialists/ folders (not invented). Departments are
# the folder ids under 01-Agency-Department/departments/.
# "kind" is a Phase 4 MOCK_KIND (workflow_engine/engine.py MOCK_KINDS).
# "gate" is None except where a sub-step is gated; "on_failure" is
# "stop" on every step (strict chain).

CHAIN_STEPS: List[Dict[str, Any]] = [
    {"id": "lead_discovery", "name": "Lead Discovery",
     "department": "05-research-strategy",
     "specialist": "MarketOpportunityAgent", "kind": "research",
     "gate": None, "on_failure": "stop"},
    {"id": "lead_verification", "name": "Lead Verification",
     "department": "07-quality-security",
     "specialist": "DataValidationAgent", "kind": "qa",
     "gate": None, "on_failure": "stop"},
    {"id": "lead_qualification", "name": "Lead Qualification",
     "department": "01-sales-growth",
     "specialist": "LeadScoringAgent", "kind": "research",
     "gate": None, "on_failure": "stop"},
    {"id": "crm_dryrun", "name": "CRM Dry-Run",
     "department": "01-sales-growth",
     "specialist": "CRMManagerAgent", "kind": "draft",
     "gate": None, "on_failure": "stop"},
    {"id": "outreach_draft", "name": "Outreach Draft",
     "department": "01-sales-growth",
     "specialist": "SalesIntelligenceAgent", "kind": "draft",
     "gate": {"tool": "gmail_send", "action": "send"},
     "on_failure": "stop"},
    {"id": "reply_monitoring", "name": "Reply Monitoring",
     "department": "04-client-operations",
     "specialist": "CallMonitoringAgent", "kind": "status",
     "gate": None, "on_failure": "stop"},
    {"id": "meeting", "name": "Meeting",
     "department": "01-sales-growth",
     "specialist": "SalesIntelligenceAgent", "kind": "draft",
     "gate": None, "on_failure": "stop"},
    {"id": "sales_process", "name": "Sales Process",
     "department": "01-sales-growth",
     "specialist": "SalesIntelligenceAgent", "kind": "draft",
     "gate": None, "on_failure": "stop"},
    {"id": "client_onboarding", "name": "Client Onboarding",
     "department": "04-client-operations",
     "specialist": "RetentionAgent", "kind": "draft",
     "gate": None, "on_failure": "stop"},
    {"id": "service_delivery", "name": "Service Delivery",
     "department": "03-ai-engineering",
     "specialist": "VapiIntegrationAgent", "kind": "draft",
     "gate": None, "on_failure": "stop"},
    {"id": "qa", "name": "QA",
     "department": "07-quality-security",
     "specialist": "CallScenarioTestingAgent", "kind": "qa",
     "gate": None, "on_failure": "stop"},
    {"id": "deployment", "name": "Deployment",
     "department": "03-ai-engineering",
     "specialist": "DeploymentAgent", "kind": "draft",
     "gate": {"tool": "deploy", "action": "deploy"},
     "on_failure": "stop"},
    {"id": "monitoring", "name": "Monitoring",
     "department": "04-client-operations",
     "specialist": "CallMonitoringAgent", "kind": "status",
     "gate": None, "on_failure": "stop"},
]

# Steps whose outcome depends on the prospect's own data, which the
# engine's mock path cannot express (it always returns "ok").
# These run directly via .steps.execute_step instead of the engine.
DIRECT_STEPS = frozenset({
    "lead_discovery", "lead_verification", "lead_qualification",
    "crm_dryrun",
})

_STEP_STATUSES = ("ok", "pending-approval", "blocked", "error",
                  "skipped")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_ceo_core_on_path() -> str:
    """Put 00-CEO-Core on sys.path (same lazy pattern the department
    managers use) so workflow_engine / store_io / agent_runtime
    import. Returns the directory added."""
    ceo_core = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ceo_core not in sys.path:
        sys.path.insert(0, ceo_core)
    return ceo_core


def _load_engine():
    """Phase 4 WorkflowEngine, or None when it cannot be imported."""
    try:
        _ensure_ceo_core_on_path()
        from workflow_engine.engine import WorkflowEngine  # noqa: PLC0415
        return WorkflowEngine
    except ImportError:
        return None


def _load_store_io():
    """store_io module (atomic JSON writes), or None on any failure."""
    try:
        _ensure_ceo_core_on_path()
        import store_io  # noqa: PLC0415
        return store_io
    except ImportError:
        return None


def _load_execute_step():
    """Worker B's .steps.execute_step, or None when unavailable
    (e.g. steps.py not built yet in a parallel checkout)."""
    try:
        from .steps import execute_step  # noqa: PLC0415
        return execute_step
    except ImportError:
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            if here not in sys.path:
                sys.path.insert(0, here)
            from steps import execute_step  # noqa: PLC0415
            return execute_step
        except ImportError:
            return None


def _write_json_atomic(path, payload) -> None:
    """Atomic JSON write: store_io when importable, else temp file +
    os.replace + fsync (same guarantee, no dependency)."""
    store_io = _load_store_io()
    if store_io is not None:
        store_io.write_json_atomic(str(path), payload)
        return
    parent = os.path.dirname(os.path.abspath(str(path)))
    if parent:
        os.makedirs(parent, exist_ok=True)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    fd, tmp_path = tempfile.mkstemp(prefix=".chain-tmp-", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(path))
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _append_log_line(path, record) -> None:
    """Append one structured JSON log line (fsync; store_io when
    importable). Never raises — a logging failure must not break
    the chain result."""
    try:
        store_io = _load_store_io()
        if store_io is not None:
            store_io.append_json_line(str(path), record)
            return
        parent = os.path.dirname(os.path.abspath(str(path)))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception:  # noqa: BLE001 — logging is best-effort
        pass


def _execution_record(task_id, attempt, status, started_at,
                      finished_at, error=None):
    """One per-attempt execution record, reusing the Phase 4 queue
    shape: {attempt, task_id, started_at, finished_at, status,
    error, cost_usd}. attempt 0 means the step was never attempted
    (skipped). cost_usd is always 0.0."""
    return {
        "attempt": attempt,
        "task_id": task_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "status": status,
        "error": error,
        "cost_usd": 0.0,
    }


def _engine_step_dict(step, prospect, extra=None):
    """Build the Phase 4 engine step dict for one chain step. An
    explicit tool/action from the step's gate is passed verbatim
    so the real Phase 3 gate sees it; otherwise the MOCK_KIND is
    gate-checked as a draft verb."""
    eng = {
        "id": step["id"],
        "name": step["name"],
        "kind": step["kind"],
        "input": {
            "prospect_id": prospect.get("id"),
            "business_name": prospect.get("business_name"),
            "specialist": step["specialist"],
            "department": step["department"],
        },
    }
    if extra:
        eng.update(extra)
    gate = step.get("gate") or {}
    if gate.get("tool"):
        eng["tool"] = gate["tool"]
    if gate.get("action"):
        eng["action"] = gate["action"]
    return eng


class ChainRunner:
    """Runs the 13-step lead chain for one prospect, in sandbox.

    ``run(prospect, store_dir=None)`` returns the full chain
    record dict (see module docstring). Never raises on a step
    failure — step failures are recorded. Raises ValueError only
    on a bad prospect argument (not a dict, or no "id").
    """

    def __init__(self):
        self._engine_cls = None
        self._engine_tried = False
        self._execute_step = None
        self._execute_step_tried = False

    # -- lazy loaders (cached per runner) -------------------------------
    def _engine(self):
        if not self._engine_tried:
            self._engine_cls = _load_engine()
            self._engine_tried = True
        return self._engine_cls

    def _direct(self):
        if not self._execute_step_tried:
            self._execute_step = _load_execute_step()
            self._execute_step_tried = True
        return self._execute_step

    # -- per-step execution ----------------------------------------------
    def _run_via_engine(self, step, prospect, context):
        """One chain step through the Phase 4 WorkflowEngine.
        Returns (status, detail, error, executed_via)."""
        engine_cls = self._engine()
        if engine_cls is None:
            return ("error", "",
                    "workflow engine unavailable and no direct "
                    "executor ran this step",
                    "workflow-engine (unavailable)")
        try:
            result = engine_cls().execute(
                {"steps": [_engine_step_dict(step, prospect)]})
        except Exception as exc:  # noqa: BLE001 — engine failure is a step error
            return ("error", "",
                    "%s: %s" % (type(exc).__name__, exc),
                    "workflow-engine")
        steps_out = result.get("steps") or []
        if not steps_out:
            return ("error", "",
                    "workflow engine returned no step result",
                    "workflow-engine")
        out = steps_out[0]
        status = out.get("status")
        output = out.get("output") or {}
        evidence = "; ".join(str(e) for e in (out.get("evidence") or []))
        detail = ("[DRAFT] %s %s — engine mock step %s; no live "
                  "call. %s" % (step["specialist"], step["name"],
                                status, evidence)).strip()
        if status == "ok":
            return ("ok", detail, "", "workflow-engine")
        if status == "pending-approval":
            return ("pending-approval", detail,
                    str(out.get("error") or "held by gate: "
                        "pending-approval"),
                    "workflow-engine")
        return ("error", "",
                str(out.get("error") or "engine step error: %s" % status),
                "workflow-engine")

    def _run_outreach_via_engine(self, step, prospect, context):
        """Outreach as two engine sub-steps: the draft (mock, ok)
        and the send (gated — pending-approval, never executed).
        Returns (status, detail, error, executed_via)."""
        engine_cls = self._engine()
        if engine_cls is None:
            return ("error", "",
                    "workflow engine unavailable and no direct "
                    "executor ran this step",
                    "workflow-engine (unavailable)")
        draft_step = _engine_step_dict(dict(step, gate=None), prospect)
        draft_step["id"] = "outreach_draft"
        draft_step["name"] = "Outreach draft"
        send_step = _engine_step_dict(step, prospect)
        send_step["id"] = "outreach_send"
        send_step["name"] = "Outreach send (gated)"
        try:
            result = engine_cls().execute(
                {"steps": [draft_step, send_step]})
        except Exception as exc:  # noqa: BLE001 — engine failure is a step error
            return ("error", "",
                    "%s: %s" % (type(exc).__name__, exc),
                    "workflow-engine")
        steps_out = result.get("steps") or []
        if len(steps_out) < 2:
            return ("error", "",
                    "workflow engine returned no send sub-step result",
                    "workflow-engine")
        draft_out, send_out = steps_out[0], steps_out[1]
        detail = ("[DRAFT] %s outreach draft ready (engine mock "
                  "step ok); send sub-step %s — never executed."
                  % (step["specialist"], send_out.get("status")))
        if draft_out.get("status") != "ok":
            return ("error", "",
                    str(draft_out.get("error")
                        or "outreach draft sub-step failed"),
                    "workflow-engine (draft + gated send sub-steps)")
        if send_out.get("status") == "pending-approval":
            return ("pending-approval", detail,
                    "send held: gmail_send requires Boss approval",
                    "workflow-engine (draft + gated send sub-steps)")
        if send_out.get("status") == "ok":
            # The gate must never allow a send in sandbox. If the
            # engine ever says ok, the runner still holds the send.
            return ("pending-approval", detail,
                    "send held: gmail_send requires Boss approval "
                    "(engine returned ok; runner holds it anyway)",
                    "workflow-engine (draft + gated send sub-steps)")
        return ("error", "",
                str(send_out.get("error") or "outreach send sub-step "
                    "error"),
                "workflow-engine (draft + gated send sub-steps)")

    def _run_deployment_via_engine(self, step, prospect, context):
        """Deployment through the engine gate, then mapped to
        "blocked": deploy is NEVER allowed in sandbox, whatever
        the engine verdict is. Returns (status, detail, error,
        executed_via)."""
        status, detail, error, via = self._run_via_engine(
            step, prospect, context)
        if status == "error" and "unavailable" in (error or ""):
            return ("blocked", "",
                    "deployment is ALWAYS BLOCKED in sandbox — "
                    "deploy is never allowed (engine unavailable, "
                    "so no gate verdict was even consulted)",
                    via + " -> blocked")
        return ("blocked", "",
                "deployment is ALWAYS BLOCKED in sandbox — deploy "
                "is never allowed (engine gate verdict: %s)"
                % status,
                via + " -> blocked")

    def _run_via_direct(self, step, prospect, context):
        """One chain step directly via .steps.execute_step. The
        step copy remaps kind -> step id because .steps dispatches
        on kind as the handler name. Returns (status, detail,
        error, executed_via), or None when .steps is unavailable."""
        execute_step = self._direct()
        if execute_step is None:
            return None
        direct_step = dict(step)
        direct_step["kind"] = step["id"]
        try:
            status, detail, error = execute_step(
                direct_step, prospect, context)
        except Exception as exc:  # noqa: BLE001 — direct failure is a step error
            return ("error", "",
                    "%s: %s" % (type(exc).__name__, exc),
                    "steps.execute_step (kind remapped to step id "
                    "for dispatch)")
        if status not in ("ok", "pending-approval", "blocked",
                          "error"):
            return ("error", "",
                    "execute_step returned unknown status: %r"
                    % (status,),
                    "steps.execute_step (kind remapped to step id "
                    "for dispatch)")
        return (status, detail or "", error or "",
                "steps.execute_step (kind remapped to step id for "
                "dispatch; engine cannot express this "
                "data-dependent outcome)")

    def _run_one_step(self, step, prospect, context):
        """Dispatch one step to the engine or the direct executor.
        Returns (status, detail, error, executed_via). Never
        raises."""
        step_id = step["id"]
        if step_id == "outreach_draft":
            return self._run_outreach_via_engine(step, prospect,
                                                 context)
        if step_id == "deployment":
            return self._run_deployment_via_engine(step, prospect,
                                                   context)
        if step_id in DIRECT_STEPS:
            direct = self._run_via_direct(step, prospect, context)
            if direct is not None:
                return direct
            # .steps unavailable: fall back to the engine and say
            # so — the engine mock returns ok, so a data-dependent
            # failure (e.g. missing email) would NOT be caught.
            status, detail, error, via = self._run_via_engine(
                step, prospect, context)
            return (status, detail, error,
                    via + " (fallback: steps.py unavailable; "
                    "data-dependent outcome not expressible)")
        return self._run_via_engine(step, prospect, context)

    # -- chain run --------------------------------------------------------
    def run(self, prospect, store_dir=None):
        """Run the chain for one prospect dict. Returns the full
        chain record. See the module docstring for the record
        shape, statuses, and idempotency behaviour."""
        if not isinstance(prospect, dict):
            raise ValueError("prospect must be a dict, got %s"
                             % type(prospect).__name__)
        prospect_id = prospect.get("id")
        if not prospect_id:
            raise ValueError("prospect must carry a non-empty 'id'")

        key_material = "%s:%s" % (CHAIN_VERSION, prospect_id)
        idempotency_key = hashlib.sha256(
            key_material.encode("utf-8")).hexdigest()

        if store_dir is not None:
            state_dir = Path(store_dir) / "chains"
        else:
            state_dir = Path(tempfile.mkdtemp(prefix="lead-chain-"))
        state_dir.mkdir(parents=True, exist_ok=True)
        record_path = state_dir / ("%s.json" % idempotency_key)
        log_path = state_dir / "chain_log.jsonl"

        # Idempotency: a stored record for this key is returned as
        # a duplicate WITHOUT re-executing any step.
        if record_path.exists():
            try:
                with open(record_path, "r", encoding="utf-8") as f:
                    stored = json.load(f)
            except (OSError, ValueError):
                stored = None
            if isinstance(stored, dict) and stored.get(
                    "idempotency_key") == idempotency_key:
                duplicate = dict(stored)
                duplicate["duplicate"] = True
                duplicate["status"] = "duplicate"
                _append_log_line(log_path, {
                    "event": "duplicate",
                    "idempotency_key": idempotency_key,
                    "prospect_id": prospect_id,
                    "status": "duplicate",
                    "cost_usd": 0.0,
                    "at": _now_iso(),
                })
                return duplicate

        started_at = _now_iso()
        context = {
            "prospect": prospect,
            "idempotency_key": idempotency_key,
            "chain": CHAIN_VERSION,
            "replies": [],
        }
        steps_out: List[Dict[str, Any]] = []
        stopped_by: Optional[str] = None
        first_error: Optional[str] = None

        for step in CHAIN_STEPS:
            step_id = step["id"]
            task_id = "%s:%s" % (idempotency_key[:12], step_id)
            if stopped_by is not None:
                reason = "dependency: %s" % stopped_by
                stamp = _now_iso()
                steps_out.append({
                    "id": step_id,
                    "name": step["name"],
                    "department": step["department"],
                    "specialist": step["specialist"],
                    "status": "skipped",
                    "detail": "skipped: %s" % reason,
                    "reason": reason,
                    "error": "",
                    "attempt": 0,
                    "executed_via": "not executed — skipped",
                    "execution_record": _execution_record(
                        task_id, 0, "skipped", stamp, stamp, ""),
                })
                continue
            step_started = _now_iso()
            try:
                status, detail, error, via = self._run_one_step(
                    step, prospect, context)
            except Exception as exc:  # noqa: BLE001 — a step never breaks run()
                status, detail, error, via = (
                    "error", "", "%s: %s" % (type(exc).__name__, exc),
                    "runner (exception guard)")
            step_finished = _now_iso()
            if status not in _STEP_STATUSES:
                status, error = ("error",
                                 "unknown step status: %r" % (status,))
            steps_out.append({
                "id": step_id,
                "name": step["name"],
                "department": step["department"],
                "specialist": step["specialist"],
                "status": status,
                "detail": detail or "",
                "error": error or "",
                "attempt": 1,
                "executed_via": via,
                "execution_record": _execution_record(
                    task_id, 1, status, step_started, step_finished,
                    error or None),
            })
            if status in ("error", "blocked"):
                # Strict chain: stop here (on_failure == "stop").
                stopped_by = step_id
                if first_error is None:
                    first_error = error or ("step %s %s"
                                            % (step_id, status))

        finished_at = _now_iso()
        statuses = [s["status"] for s in steps_out]
        if "error" in statuses:
            chain_status = "failed"
        elif "blocked" in statuses:
            chain_status = "blocked"
        elif "pending-approval" in statuses:
            chain_status = "partial"
        else:
            chain_status = "completed"

        record = {
            "schema": CHAIN_VERSION,
            "idempotency_key": idempotency_key,
            "prospect_id": prospect_id,
            "prospect_business_name": prospect.get("business_name"),
            "status": chain_status,
            "duplicate": False,
            "steps": steps_out,
            "cost_usd": 0.0,
            "started_at": started_at,
            "finished_at": finished_at,
            "error": first_error,
            "stopped_by": stopped_by,
            "policy": {
                "retry_max_attempts": 1,
                "retry_policy": "no retry in sandbox; a failed or "
                                "blocked step stops the chain and "
                                "later steps are skipped (dead-letter "
                                "= this record)",
                "timeout_seconds": 300,
                "on_failure": "stop",
            },
            "engine": "Phase 4 WorkflowEngine (real Phase 3 gate) "
                      "for gate-checked steps; .steps.execute_step "
                      "for data-dependent steps the engine cannot "
                      "express",
        }
        _write_json_atomic(record_path, record)
        _append_log_line(log_path, {
            "event": "chain_run",
            "idempotency_key": idempotency_key,
            "prospect_id": prospect_id,
            "status": chain_status,
            "steps": statuses,
            "stopped_by": stopped_by,
            "cost_usd": 0.0,
            "at": finished_at,
        })
        return record


def run_lead_chain(prospect, store_dir=None):
    """One-shot helper: ``ChainRunner().run(prospect, store_dir)``."""
    return ChainRunner().run(prospect, store_dir=store_dir)


if __name__ == "__main__":
    # Self-test — TEST fixture (a) only, in-memory (fresh temp
    # state dir), no live calls. Expected sandbox outcome: the
    # chain is "blocked" at deployment (always blocked), the
    # outreach send is held pending-approval, monitoring is skipped
    # as a deployment dependency, everything else ok, $0.
    try:
        from .fixtures import STRONG_TIER1_PROSPECT  # noqa: PLC0415
    except ImportError:
        here = os.path.dirname(os.path.abspath(__file__))
        if here not in sys.path:
            sys.path.insert(0, here)
        from fixtures import STRONG_TIER1_PROSPECT  # noqa: PLC0415

    _tmp = tempfile.mkdtemp(prefix="lead-chain-selftest-")
    _record = run_lead_chain(STRONG_TIER1_PROSPECT, store_dir=_tmp)
    _by_id = {s["id"]: s for s in _record["steps"]}
    assert len(_record["steps"]) == 13, _record["steps"]
    assert _record["status"] == "blocked", _record["status"]
    assert _record["cost_usd"] == 0.0
    assert _by_id["outreach_draft"]["status"] == "pending-approval"
    assert _by_id["deployment"]["status"] == "blocked"
    assert _by_id["monitoring"]["status"] == "skipped"
    assert _by_id["monitoring"]["reason"] == "dependency: deployment"
    assert _by_id["lead_verification"]["status"] == "ok"
    # Idempotency: the same prospect in the same store dir is a
    # duplicate and executes nothing again.
    _again = run_lead_chain(STRONG_TIER1_PROSPECT, store_dir=_tmp)
    assert _again["status"] == "duplicate" and _again["duplicate"] is True
    assert _again["steps"] == _record["steps"]
    print("OK")
    print("chain: %s | steps: %s"
          % (_record["status"],
             ", ".join("%s=%s" % (s["id"], s["status"])
                       for s in _record["steps"])))
    print("duplicate re-run: %s (no step re-executed)"
          % _again["status"])
