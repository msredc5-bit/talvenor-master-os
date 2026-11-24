"""Phase 4 scheduler — real job definitions, created PAUSED, activation gated
(Talvenor Master OS, local-first Phase 4).

Built ON TOP of 00-CEO-Core/quiet_schedules.py — this module does NOT
duplicate ScheduleStore. It adds:

  * Real job definitions (daily / weekly / monthly Talvenor jobs, grounded
    in the repo's existing stores and weekly cadence) as data, plus
    job_definitions() / job_definition(job_id).
  * create_paused_jobs(store) — writes the definitions into a ScheduleStore
    with status "paused". Creating an ACTIVE job is out of scope: this
    function never writes status "active", and it REFUSES the real
    store/schedules.json unless the caller also passes a Boss approval
    covering scope "scheduler-create" (real-store creation is a Boss
    decision, not a code change).
  * activate_job(store, job_id, approval) — the ONLY activation path in
    this module. It refuses (raises ActivationRefused, never activates)
    unless given an explicit Boss approval record: approver "Boss"
    (or "Md Mainuddin"), decision "approved", a non-empty approval_id,
    and a scope naming this job ("scheduler-activation:<job_id>").
    Activation never happens as a side effect of creation, import, or a
    schedule run.
  * resume_job(store, job_id) — guarded resume: a job that was never
    Boss-activated stays paused (raises ActivationRefused). Pausing via
    ScheduleStore.pause stays available at any time.
  * should_run_job() / due_jobs() — a paused job is NEVER due, and an
    active-but-never-activated job (e.g. someone called the raw
    ScheduleStore.resume) is treated as paused. Active + activated jobs
    reuse quiet_schedules' should_run semantics (first run / changed /
    unchanged-quiet / one-run-at-a-time).

Every job's action is draft / report / watch ONLY. No job sends,
publishes, spends, deletes, deploys, uploads, books, pays, or orders
anything — validate_job_definitions() enforces this on the action field.

Rules:
  - $0. No live calls, no keys, no network. Stdlib only.
  - No writes to the real store/ except through the guarded,
    approval-checked path above. Tests use a TEMPORARY store dir only
    (same --store-dir pattern as scripts/run_quiet_schedules.py).
  - The 100-mail follow-up rule, the gate core, free_only_guard, and the
    Phase 3 runtime limits are untouched by this module.

Usage:
  store = ScheduleStore(schedules_path="/tmp/some-temp/schedules.json")
  out = create_paused_jobs(store)          # all records land "paused"
  due = due_jobs(store)                    # every paused job: due=False
  rec = activate_job(store, "weekly-ceo-report",
                     {"approval_id": "APR-...", "approver": "Boss",
                      "decision": "approved",
                      "scope": "scheduler-activation:weekly-ceo-report"})

Status: REAL (Phase 4, 2026-11-25) — definitions + gating logic; no job
has ever been activated in the real store, and none is active anywhere.
"""

import copy
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_CEO_CORE_DIR = os.path.dirname(_HERE)
_REPO_ROOT = os.path.dirname(_CEO_CORE_DIR)
if _CEO_CORE_DIR not in sys.path:
    sys.path.insert(0, _CEO_CORE_DIR)

from quiet_schedules import (  # noqa: E402
    DEFAULT_SCHEDULES_PATH,
    SCHEDULE_KINDS,
    ScheduleStore,
    file_state,
)
from control import ControlCorruptError, consult as _control_consult  # noqa: E402
# Phase 7 (Worker C): activation + due checks consult the control
# plane (store/control.json, next to the store's schedules.json).
# Paused / emergency-stopped / corrupt control file -> activation
# refused, no job due. No behaviour change while running (default).

# ---------------------------------------------------------------------------
# Job definitions
# ---------------------------------------------------------------------------

# Interval (minutes) each cadence means. Daily 1440, weekly 10080,
# monthly 43200 (30 days). The schedule expression is a descriptive
# cron-like string in Asia/Dhaka time ("minute hour day month weekday");
# no cron daemon exists yet — interval_minutes is what ScheduleStore
# enforces. The expressions are the intended fire times for whenever a
# Boss-approved runner is attached later.
CADENCE_INTERVAL_MINUTES = {
    "daily": 1440,
    "weekly": 10080,
    "monthly": 43200,
}

# Only these action kinds exist. Anything else is rejected by validation.
ALLOWED_ACTION_KINDS = ("watch", "report", "draft")

# Whole-word scan of the "action" field — a job action must never name a
# commit. ("never sends" style guard language lives in "description",
# which is not scanned, so the guard can be stated plainly.)
FORBIDDEN_ACTION_WORDS = (
    "send", "publish", "spend", "delete", "deploy", "upload",
    "book", "pay", "order", "cancel", "transfer",
)

_JOB_ID_NOTE_PREFIX = "scheduler-job-id: "
_ACTIVATED_NOTE_PREFIX = "activated-by: "

# The four Phase 4 scheduler jobs. Grounded in the repo:
#  - store/tasks.json is the task queue run_office.py drains;
#  - store/approvals.json is the approval gateway's record;
#  - the weekly CEO report + Sunday 6 PM Dhaka cadence are the standing
#    weekly workflow (MEMORY.md);
#  - store/usage_ledger.json is the $0 usage ledger.
_JOB_DEFINITIONS = (
    {
        "id": "daily-task-queue-drain-watch",
        "name": "Daily task-queue drain watch",
        "kind": "watch",
        "cadence": "daily",
        "schedule": "0 6 * * * Asia/Dhaka",
        "interval_minutes": 1440,
        "source": "store/tasks.json",
        "action": "watch",
        "task": "Watch the task queue: count queued vs done tasks and "
                "draft a short status note for the CEO report.",
        "description": "Daily 06:00 Dhaka watch over store/tasks.json. "
                       "Draft/report only — it never executes, sends, "
                       "publishes, spends, or deletes any task.",
    },
    {
        "id": "daily-approval-queue-watch",
        "name": "Daily approval-queue watch",
        "kind": "watch",
        "cadence": "daily",
        "schedule": "0 7 * * * Asia/Dhaka",
        "interval_minutes": 1440,
        "source": "store/approvals.json",
        "action": "watch",
        "task": "Watch pending approvals: count approvals awaiting a "
                "Boss decision and draft a count summary for Boss.",
        "description": "Daily 07:00 Dhaka watch over store/approvals.json. "
                       "Watch/report only — it never approves, rejects, "
                       "sends, or changes any approval.",
    },
    {
        "id": "weekly-ceo-report",
        "name": "Weekly CEO report (draft)",
        "kind": "recurring",
        "cadence": "weekly",
        "schedule": "0 18 * * 0 Asia/Dhaka",
        "interval_minutes": 10080,
        "source": "store/tasks.json",
        "action": "draft",
        "task": "Draft the weekly CEO report from the real store and "
                "audit records: what was queued, done, and is pending.",
        "description": "Weekly Sunday 18:00 Dhaka — the standing weekly "
                       "cadence. Draft only — the report is a draft for "
                       "Boss to read; it is never sent or published.",
    },
    {
        "id": "monthly-ledger-usage-summary",
        "name": "Monthly ledger & usage summary (draft)",
        "kind": "recurring",
        "cadence": "monthly",
        "schedule": "0 6 1 * * Asia/Dhaka",
        "interval_minutes": 43200,
        "source": "store/usage_ledger.json",
        "action": "report",
        "task": "Draft a monthly summary of the $0 usage ledger: calls, "
                "costs (all $0.00), and totals, as a report draft.",
        "description": "Monthly, 1st at 06:00 Dhaka, over "
                       "store/usage_ledger.json. Report only — it never "
                       "spends, changes the ledger, or sends anything.",
    },
)


def job_definitions():
    """All Phase 4 scheduler job definitions (deep copies — callers
    cannot mutate the module's table)."""
    return copy.deepcopy(list(_JOB_DEFINITIONS))


def job_definition(job_id):
    """One job definition by its stable id. Raises KeyError if unknown."""
    for job in _JOB_DEFINITIONS:
        if job["id"] == job_id:
            return copy.deepcopy(job)
    raise KeyError(f"No scheduler job with id {job_id!r}")


def validate_job_definitions(definitions=None):
    """Fail-closed validation of the job table (or a caller-supplied one).

    Checks: ids unique and non-empty; kind in SCHEDULE_KINDS; cadence in
    {daily, weekly, monthly} with interval_minutes matching the cadence;
    action in ALLOWED_ACTION_KINDS; the action field names no commit
    verb. Returns True; raises ValueError on the first problem.
    """
    definitions = list(definitions) if definitions is not None \
        else list(_JOB_DEFINITIONS)
    seen = set()
    for job in definitions:
        job_id = job.get("id")
        if not job_id or not str(job_id).strip():
            raise ValueError("scheduler job id must be a non-empty string.")
        if job_id in seen:
            raise ValueError(f"duplicate scheduler job id {job_id!r}.")
        seen.add(job_id)
        if job.get("kind") not in SCHEDULE_KINDS:
            raise ValueError(
                f"job {job_id!r}: unknown kind {job.get('kind')!r}. "
                f"Allowed: {list(SCHEDULE_KINDS)}")
        cadence = job.get("cadence")
        if cadence not in CADENCE_INTERVAL_MINUTES:
            raise ValueError(
                f"job {job_id!r}: unknown cadence {cadence!r}. Allowed: "
                f"{sorted(CADENCE_INTERVAL_MINUTES)}")
        expected = CADENCE_INTERVAL_MINUTES[cadence]
        if int(job.get("interval_minutes", 0)) != expected:
            raise ValueError(
                f"job {job_id!r}: interval_minutes "
                f"{job.get('interval_minutes')!r} does not match cadence "
                f"{cadence!r} (expected {expected}).")
        if job.get("action") not in ALLOWED_ACTION_KINDS:
            raise ValueError(
                f"job {job_id!r}: unknown action {job.get('action')!r}. "
                f"Allowed: {list(ALLOWED_ACTION_KINDS)}")
        words = [w.strip(".,;:!?()").lower()
                 for w in str(job.get("action", "")).split()]
        bad = [w for w in words if w in FORBIDDEN_ACTION_WORDS]
        if bad:
            raise ValueError(
                f"job {job_id!r}: action names forbidden verb(s) {bad} — "
                "scheduler jobs are draft/report/watch only.")
        if not str(job.get("schedule", "")).strip():
            raise ValueError(f"job {job_id!r}: schedule must be non-empty.")
        if not str(job.get("source", "")).strip():
            raise ValueError(f"job {job_id!r}: source must be non-empty.")
    return True


# ---------------------------------------------------------------------------
# Approval gate — activation refuses without an explicit Boss approval
# ---------------------------------------------------------------------------

class ActivationRefused(Exception):
    """Raised when activation (or a guarded resume) is refused: no
    valid Boss approval was supplied. Nothing is activated."""


# Who may approve a scheduler activation. Only Boss.
APPROVERS = ("Boss", "Md Mainuddin")


def validate_approval(approval, scope):
    """Check an approval record against a required scope.

    approval must be a dict with:
      approval_id: non-empty string (the approval record id),
      approver: "Boss" (or "Md Mainuddin"),
      decision: exactly "approved",
      scope: exactly the required scope, or the required scope plus
        nothing else (equality — no substring matching).
    Returns (ok, reason). Never raises for a bad approval — callers
    decide (activate_job raises ActivationRefused on ok=False).
    """
    if approval is None:
        return False, "no approval supplied — activation refused"
    if not isinstance(approval, dict):
        return False, "approval must be a dict record — activation refused"
    approval_id = approval.get("approval_id")
    if not approval_id or not str(approval_id).strip():
        return False, "approval has no approval_id — activation refused"
    if approval.get("approver") not in APPROVERS:
        return False, (
            f"approver {approval.get('approver')!r} is not Boss — "
            "activation refused")
    if approval.get("decision") != "approved":
        return False, (
            f"decision is {approval.get('decision')!r}, not 'approved' — "
            "activation refused")
    if approval.get("scope") != scope:
        return False, (
            f"scope {approval.get('scope')!r} does not cover required "
            f"scope {scope!r} — activation refused")
    return True, "approved"


def _activation_scope(job_id):
    return f"scheduler-activation:{job_id}"


def _is_real_store(store):
    """True when this ScheduleStore points at the repo's real
    store/schedules.json."""
    try:
        return (os.path.realpath(store.schedules_path)
                == os.path.realpath(DEFAULT_SCHEDULES_PATH))
    except (AttributeError, TypeError, OSError):
        return False


def _control_halted(store):
    """Control-plane consult for this store: the control file lives
    next to the store's schedules.json (store/control.json for the
    real store, <temp>/control.json for a temp store). Returns
    (halted, reason). A corrupt control file consults as halted
    (fail-closed) — activation / due never proceed on a corrupt
    file. A missing file consults as running (no state ever written)."""
    control_path = os.path.join(
        os.path.dirname(os.path.abspath(store.schedules_path)),
        "control.json")
    try:
        return _control_consult(control_path)
    except ControlCorruptError as exc:
        return True, f"control file corrupt: {exc}"


# ---------------------------------------------------------------------------
# Record lookup — definitions are found by the job-id marker in the note
# ---------------------------------------------------------------------------

def _note_for(job):
    return (
        f"{_JOB_ID_NOTE_PREFIX}{job['id']}; {job['description']} "
        "| status at creation: paused — activation needs a Boss approval "
        "(see workflow_engine/scheduler.activate_job)."
    )


def job_id_from_record(record):
    """The scheduler job id carried in a record's note, or None when
    the record is not a scheduler job (e.g. the pre-existing
    taskboard-queue-watch)."""
    note = (record or {}).get("note") or ""
    marker = _JOB_ID_NOTE_PREFIX
    if marker not in note:
        return None
    rest = note.split(marker, 1)[1]
    return rest.split(";", 1)[0].strip() or None


def is_activated(record):
    """True when the record carries an activation marker — i.e. a Boss
    approval was recorded by activate_job. A record with status
    "active" but no marker was never Boss-activated."""
    note = (record or {}).get("note") or ""
    return _ACTIVATED_NOTE_PREFIX in note


def _find_record(store, job_id_or_record_id):
    """Find a record by its ScheduleStore id first, then by scheduler
    job id (note marker). Raises KeyError when nothing matches and
    ValueError when the marker matches more than one record."""
    try:
        return store.get(job_id_or_record_id)
    except KeyError:
        pass
    matches = [r for r in store.list()
               if job_id_from_record(r) == job_id_or_record_id]
    if not matches:
        raise KeyError(
            f"No schedule with id or scheduler job id "
            f"{job_id_or_record_id!r}")
    if len(matches) > 1:
        raise ValueError(
            f"Ambiguous scheduler job id {job_id_or_record_id!r}: "
            f"{len(matches)} records carry it — refusing to choose.")
    return matches[0]


# ---------------------------------------------------------------------------
# Creation — PAUSED records only
# ---------------------------------------------------------------------------

def create_paused_jobs(store, approval=None):
    """Write the Phase 4 job definitions into a ScheduleStore as
    PAUSED records. Idempotent: a job already present (same job-id
    marker) is left untouched and reported under "existing".

    Real-store guard: when the store IS the repo's real
    store/schedules.json, a Boss approval covering scope
    "scheduler-create" is required — real-store creation is a Boss
    decision, not a code change. A temp store needs no approval
    (creation is paused and harmless there).

    Never creates an active job: every new record is written with
    status="paused" and verified paused after the write.
    Returns {"created": [records], "existing": [records]}.
    """
    validate_job_definitions()
    if _is_real_store(store):
        ok, reason = validate_approval(approval, "scheduler-create")
        if not ok:
            raise ActivationRefused(
                "refusing to create scheduler jobs in the REAL store: "
                + reason + " (real-store creation is a Boss decision)")
    created, existing = [], []
    present = {job_id_from_record(r) for r in store.list()}
    for job in _JOB_DEFINITIONS:
        if job["id"] in present:
            existing.append(_find_record(store, job["id"]))
            continue
        record = store.add(
            job["name"], kind=job["kind"], source=job["source"],
            interval_minutes=job["interval_minutes"],
            status="paused", note=_note_for(job))
        if record["status"] != "paused":
            raise RuntimeError(
                f"job {job['id']!r} was not created paused "
                f"(status={record['status']!r}) — refusing to continue")
        created.append(record)
    return {"created": created, "existing": existing}


# ---------------------------------------------------------------------------
# Activation — explicit Boss approval only, never a side effect
# ---------------------------------------------------------------------------

def activate_job(store, job_id, approval=None):
    """Activate one scheduler job — ONLY with a valid Boss approval.

    approval must pass validate_approval() for scope
    "scheduler-activation:<job_id>". Without it (None, wrong approver,
    wrong decision, missing id, wrong scope) this raises
    ActivationRefused and the record stays exactly as it was — paused.
    Importing this module, creating jobs, or running a schedule never
    calls this function.

    On success the approval is recorded in the note
    ("activated-by: <approval_id>") BEFORE the status flips to active,
    so a job is never active without its activation marker. Returns the
    updated record. Activating an already-active + activated job is a
    no-op returning the record unchanged.

    Phase 7: refused while the control plane is halted (paused /
    emergency_stop / corrupt control file) — before the approval is
    even checked.
    """
    halted, halt_reason = _control_halted(store)
    if halted:
        raise ActivationRefused(
            f"activation of {job_id!r} refused: control plane halted "
            f"({halt_reason})")
    ok, reason = validate_approval(approval, _activation_scope(job_id))
    if not ok:
        raise ActivationRefused(
            f"activation of {job_id!r} refused: {reason}")
    record = _find_record(store, job_id)
    if record["status"] == "active" and is_activated(record):
        return record
    marker = (f"{_ACTIVATED_NOTE_PREFIX}{approval['approval_id']} "
              f"(approver: {approval['approver']})")
    new_note = (record.get("note") or "") + " | " + marker
    store.apply_correction(record["id"], note=new_note)
    updated = store.resume(record["id"])
    if updated["status"] != "active" or not is_activated(updated):
        raise RuntimeError(
            f"activation of {job_id!r} did not land active+marked "
            f"(status={updated['status']!r}) — check the store")
    return updated


def resume_job(store, job_id_or_record_id):
    """Guarded resume: only a job that was Boss-activated (activation
    marker in its note) may be resumed. A never-activated job stays
    paused — raises ActivationRefused. Use activate_job (with a Boss
    approval) for a never-activated job; use store.pause() to pause
    any job at any time (pausing is always safe)."""
    record = _find_record(store, job_id_or_record_id)
    if not is_activated(record):
        raise ActivationRefused(
            f"resume of {job_id_or_record_id!r} refused: job was never "
            "Boss-activated — it stays paused (use activate_job with a "
            "Boss approval)")
    return store.resume(record["id"])


def pause_job(store, job_id_or_record_id):
    """Pause a job (always allowed — pausing is safe). Activation
    marker is kept, so a Boss-activated job can be resumed later via
    resume_job."""
    record = _find_record(store, job_id_or_record_id)
    return store.pause(record["id"])


# ---------------------------------------------------------------------------
# Due checks — a paused job never fires
# ---------------------------------------------------------------------------

def _state_for_record(record):
    """Current observable state for a record: the hashable state of its
    source file, resolved against the repo root (same shape as
    quiet_schedules.file_state). A record with no source uses a
    constant marker, so it is due once, then quiet."""
    source = (record.get("source") or "").strip()
    if not source:
        return {"job": job_id_from_record(record) or record.get("id")}
    path = source if os.path.isabs(source) \
        else os.path.join(_REPO_ROOT, source)
    return file_state(path)


def should_run_job(store, job_id_or_record_id, current_state=None):
    """Whether one job should run now — (due, reason).

    Paused -> (False, "schedule is paused — skipped"), always.
    Active but never Boss-activated -> (False, treated as paused).
    Active + activated -> delegates to ScheduleStore.should_run, i.e.
    quiet_schedules semantics (first run / changed / unchanged-quiet /
    one-run-at-a-time / stale lock). Read-only: never mutates a record.
    """
    record = _find_record(store, job_id_or_record_id)
    # Phase 7: a halted control plane (paused / emergency_stop /
    # corrupt control file) means no job is due — before the paused /
    # activation checks below.
    halted, halt_reason = _control_halted(store)
    if halted:
        return False, f"control halted — skipped ({halt_reason})"
    if record["status"] != "active":
        return False, f"schedule is {record['status']} — skipped"
    if not is_activated(record):
        return False, ("active but never Boss-activated — treated as "
                       "paused")
    state = current_state if current_state is not None \
        else _state_for_record(record)
    return store.should_run(record["id"], state)


def due_jobs(store, states=None):
    """Which jobs in this store are due now.

    states: optional {record_id: current_state}; when absent, each
    record's state is read from its source file (read-only).
    Returns a list of {"job_id", "record_id", "name", "due", "reason"}
    for EVERY record in the store — including non-scheduler records
    (job_id None), which follow the same paused-never-due rule.
    A paused job is never due. Read-only: no record is mutated.
    """
    states = states or {}
    out = []
    # Phase 7: one consult for the whole store — a halted control
    # plane (paused / emergency_stop / corrupt control file) means
    # no job in this store is due.
    ctrl_halted, ctrl_reason = _control_halted(store)
    for record in store.list():
        job_id = job_id_from_record(record)
        if ctrl_halted:
            due, reason = False, \
                f"control halted — skipped ({ctrl_reason})"
        elif record["status"] != "active":
            due, reason = False, \
                f"schedule is {record['status']} — skipped"
        elif not is_activated(record):
            due, reason = False, ("active but never Boss-activated — "
                                  "treated as paused")
        else:
            state = states.get(record["id"])
            if state is None:
                state = _state_for_record(record)
            due, reason = store.should_run(record["id"], state)
        out.append({
            "job_id": job_id,
            "record_id": record["id"],
            "name": record["name"],
            "due": bool(due),
            "reason": reason,
        })
    return out


if __name__ == "__main__":
    # Self-test — TEMP store only; the real store is only read (hash
    # before/after) and never written. Stdlib only.
    import hashlib
    import json
    import tempfile

    def _real_store_sha():
        with open(DEFAULT_SCHEDULES_PATH, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    real_before = _real_store_sha()

    # 1. Definitions load and validate.
    jobs = job_definitions()
    assert len(jobs) == 4, jobs
    assert validate_job_definitions() is True
    assert [j["id"] for j in jobs] == [
        "daily-task-queue-drain-watch",
        "daily-approval-queue-watch",
        "weekly-ceo-report",
        "monthly-ledger-usage-summary",
    ]
    assert all(j["action"] in ALLOWED_ACTION_KINDS for j in jobs)
    try:
        job_definition("no-such-job")
        raise SystemExit("FAIL: unknown job id did not raise")
    except KeyError:
        pass
    bad = job_definitions()
    bad[0]["action"] = "send"
    try:
        validate_job_definitions(bad)
        raise SystemExit("FAIL: forbidden action 'send' passed validation")
    except ValueError:
        pass

    tmp_dir = tempfile.mkdtemp()
    tmp_sched = os.path.join(tmp_dir, "schedules.json")
    store = ScheduleStore(schedules_path=tmp_sched)

    # 2. Creation into a TEMP store lands every record paused.
    out = create_paused_jobs(store)
    assert len(out["created"]) == 4 and out["existing"] == [], out
    assert all(r["status"] == "paused" for r in store.list())
    assert all(job_id_from_record(r) is not None for r in store.list())
    # Idempotent: a second creation creates nothing, keeps the rest.
    out2 = create_paused_jobs(store)
    assert out2["created"] == [] and len(out2["existing"]) == 4, out2
    assert len(store.list()) == 4

    # 3. A paused job is never due.
    assert all(not d["due"] for d in due_jobs(store)), due_jobs(store)
    due, reason = should_run_job(store, "weekly-ceo-report",
                                 {"tasks": ["a"]})
    assert due is False and "paused" in reason, reason

    # 4. Activation without approval refuses — nothing changes.
    for bad_approval in (None, {}, {"approval_id": "APR-1"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "approved"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "approved",
                          "scope": "scheduler-activation:other-job"},
                         {"approval_id": "APR-1", "approver": "Someone",
                          "decision": "approved",
                          "scope": "scheduler-activation:weekly-ceo-report"},
                         {"approval_id": "APR-1", "approver": "Boss",
                          "decision": "pending",
                          "scope": "scheduler-activation:weekly-ceo-report"}):
        try:
            activate_job(store, "weekly-ceo-report", bad_approval)
            raise SystemExit(
                f"FAIL: activation without valid approval succeeded: "
                f"{bad_approval!r}")
        except ActivationRefused:
            pass
    rec = _find_record(store, "weekly-ceo-report")
    assert rec["status"] == "paused" and not is_activated(rec)

    # 5. Guarded resume of a never-activated job refuses, stays paused.
    try:
        resume_job(store, "weekly-ceo-report")
        raise SystemExit("FAIL: resume of never-activated job succeeded")
    except ActivationRefused:
        pass
    assert _find_record(store, "weekly-ceo-report")["status"] == "paused"

    # 6. Activation WITH a valid Boss approval works (temp store only).
    approval = {"approval_id": "APR-TEST-1", "approver": "Boss",
                "decision": "approved",
                "scope": "scheduler-activation:weekly-ceo-report"}
    rec = activate_job(store, "weekly-ceo-report", approval)
    assert rec["status"] == "active" and is_activated(rec), rec
    assert "APR-TEST-1" in rec["note"]
    # Re-activating is a no-op.
    assert activate_job(store, "weekly-ceo-report",
                        approval)["status"] == "active"
    # Now the activated job follows quiet_schedules semantics: first
    # run due, unchanged quiet, changed due again.
    due, reason = should_run_job(store, "weekly-ceo-report",
                                 {"tasks": ["a"]})
    assert due is True and reason.startswith("first run"), reason
    due, reason = should_run_job(store, "weekly-ceo-report",
                                 {"tasks": ["a"]})
    assert due is True and reason.startswith("first run"), reason
    store.begin_run(rec["id"])
    store.end_run(rec["id"], {"drafted": True},
                  current_state={"tasks": ["a"]})
    due, reason = should_run_job(store, "weekly-ceo-report",
                                 {"tasks": ["a"]})
    assert due is False and "quiet" in reason, reason
    due, reason = should_run_job(store, "weekly-ceo-report",
                                 {"tasks": ["a", "b"]})
    assert due is True and reason.startswith("changed"), reason
    # Pause keeps the marker; guarded resume works again afterwards.
    pause_job(store, "weekly-ceo-report")
    assert _find_record(store, "weekly-ceo-report")["status"] == "paused"
    assert all(not d["due"] for d in due_jobs(store)
               if d["job_id"] == "weekly-ceo-report")
    assert resume_job(store, "weekly-ceo-report")["status"] == "active"

    # 7. Raw ScheduleStore.resume bypass is caught by the due check:
    #    active but never Boss-activated is treated as paused.
    raw = _find_record(store, "daily-task-queue-drain-watch")
    store.resume(raw["id"])
    assert store.get(raw["id"])["status"] == "active"
    assert not is_activated(store.get(raw["id"]))
    due, reason = should_run_job(store, "daily-task-queue-drain-watch",
                                 {"tasks": ["a"]})
    assert due is False and "never Boss-activated" in reason, reason
    assert all(not d["due"] for d in due_jobs(store)
               if d["job_id"] == "daily-task-queue-drain-watch")

    # 8. Real-store creation without approval refuses.
    real_store = ScheduleStore()  # default path = real store
    try:
        create_paused_jobs(real_store)
        raise SystemExit("FAIL: real-store creation without approval "
                         "succeeded")
    except ActivationRefused:
        pass
    assert _real_store_sha() == real_before, "REAL STORE CHANGED"

    # 9. No live-call / secret surface in this module.
    # NOTE (Phase 8 fix): scan only the module body, not this
    # __main__ self-test block. The pre-Phase-7 scan read the whole
    # file, so every token listed in the tuple below tripped the scan
    # on its own literal — the self-test could never pass. The intent
    # is unchanged: production code must contain no live-call /
    # secret token. The "sk-" token is checked separately as a
    # key-like pattern (sk- + 20 or more alphanumerics): the bare
    # substring is a false positive — it occurs inside the legitimate
    # job id "daily-task-queue-drain-watch" ("ta[sk-]queue").
    import re as _re
    with open(os.path.abspath(__file__), encoding="utf-8") as f:
        src = f.read()
    src = src.split('if __name__ == "__main__":', 1)[0]
    for token in ("requests.", "urllib", "http.client", "socket.",
                  "api_key"):
        assert token not in src, f"forbidden token in source: {token}"
    assert not _re.search(r"sk-[A-Za-z0-9]{20,}", src), \
        "key-like 'sk-...' token in source"

    print("scheduler: OK (4 definitions validate; temp creation all "
          "paused + idempotent; paused never due; activation refuses "
          "without Boss approval; approval activates on temp store; "
          "guarded resume; raw-resume bypass caught as not due; "
          "real store untouched)")
