"""Control plane — pause / resume / emergency-stop (Phase 7, Worker C).

One small state file, store/control.json, schema "control-v1":

  {"schema": "control-v1", "paused": false, "emergency_stop": false,
   "state": "running",
   "reason": null, "set_by": null, "set_at": null,
   "history": [{"state": "paused", "reason": "...", "set_by": "Boss",
                "set_at": "..."}, ...],
   "history_dropped": 0}

"state" is a DERIVED label ("running" / "paused" / "emergency_stop",
emergency_stop wins over paused) recomputed from the two flags on
every load and every transition — the flags are the truth, the label
is only a convenience for readers (scripts/sync_status.py shows it
on the dashboard).

Rules (Boss's control plane — nothing here sends, publishes, spends,
deletes, deploys, or executes anything; it only decides whether the
drain and the scheduler may run):

  - The drain halts when `paused` OR `emergency_stop` is set; the
    scheduler refuses activation and reports no job due while either
    is set.
  - `resume` clears ONLY `paused`. If `emergency_stop` is set, resume
    REFUSES (raises ControlRefused) — it never silently clears an
    emergency stop.
  - `emergency_stop` clears ONLY via `clear_emergency_stop` with a
    non-empty reason (empty/blank reason raises ValueError).
  - Load semantics: a MISSING or UNREADABLE (OSError) file loads as
    the running state — never an exception. This is fail-open ONLY
    when no state was ever written. A file that EXISTS but holds
    corrupt JSON (or a non-dict / wrong-schema payload) raises
    ControlCorruptError — fail-CLOSED on corruption: callers halt
    and record the error instead of running blind.
  - Every transition appends to an append-only `history` list, capped
    at 100 entries. When the cap is hit the OLDEST entry is dropped
    and `history_dropped` is incremented — drops are counted, never
    silent.
  - Writes go through store_io.write_json_atomic (atomic temp +
    os.replace), so a concurrent reader never sees a half-written
    control file. Transitions use store_io.update_json (locked
    read-modify-write) so two writers cannot lose each other's
    transition.

Usage:
  state = ControlState()                    # store/control.json
  state.pause("Thanksgiving — hold the queue", set_by="Boss")
  state.is_halted()                         # True
  halted, reason = consult()                # (True, "paused: ...")
  state.resume("back to work", set_by="Boss")
  state.emergency_stop("stop everything", set_by="Boss")
  state.clear_emergency_stop("all clear", set_by="Boss")

Stdlib only. No network, no send, no publish, no spend, no delete.
"""

import json
import os
from datetime import datetime, timezone

try:
    from store_io import update_json, write_json_atomic
except ImportError:  # direct script run from another directory
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from store_io import update_json, write_json_atomic  # noqa: E402

_MASTER_OS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_STORE_DIR = os.path.join(_MASTER_OS_DIR, "store")
DEFAULT_CONTROL_PATH = os.path.join(_STORE_DIR, "control.json")

SCHEMA = "control-v1"
MAX_HISTORY = 100

# History "state" labels — one per transition kind.
STATE_PAUSED = "paused"
STATE_RESUMED = "resumed"
STATE_EMERGENCY_STOP = "emergency_stop"
STATE_EMERGENCY_STOP_CLEARED = "emergency_stop_cleared"


class ControlError(Exception):
    """Base class for control-plane errors."""


class ControlCorruptError(ControlError):
    """The control file exists but cannot be trusted (corrupt JSON, or
    a non-dict / wrong-schema payload). Fail-closed: callers must halt
    and record this error, never run as if the state were running."""


class ControlRefused(ControlError):
    """A transition was refused (e.g. resume while an emergency stop
    is set). Nothing changed."""


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _state_label(state):
    """Derived label from the flags: emergency_stop wins over paused."""
    if state.get("emergency_stop"):
        return STATE_EMERGENCY_STOP
    if state.get("paused"):
        return STATE_PAUSED
    return "running"


def _default_state():
    """The running state — what a missing/unreadable file loads as."""
    return {
        "schema": SCHEMA,
        "paused": False,
        "emergency_stop": False,
        "state": "running",
        "reason": None,
        "set_by": None,
        "set_at": None,
        "history": [],
        "history_dropped": 0,
    }


def _validate_state(data, path):
    """Fail-closed validation of a loaded payload. Returns the state
    dict (normalised with defaults for missing optional fields).
    Raises ControlCorruptError on anything untrustworthy."""
    if not isinstance(data, dict):
        raise ControlCorruptError(
            f"control file {path!r} is corrupt: top-level JSON is not "
            f"an object ({type(data).__name__}) — halting fail-closed")
    if data.get("schema") != SCHEMA:
        raise ControlCorruptError(
            f"control file {path!r} is corrupt: schema is "
            f"{data.get('schema')!r}, expected {SCHEMA!r} — halting "
            "fail-closed")
    state = _default_state()
    for key in ("paused", "emergency_stop"):
        value = data.get(key, False)
        if not isinstance(value, bool):
            raise ControlCorruptError(
                f"control file {path!r} is corrupt: {key!r} is not a "
                f"boolean ({value!r}) — halting fail-closed")
        state[key] = value
    for key in ("reason", "set_by", "set_at"):
        state[key] = data.get(key)
    history = data.get("history", [])
    if not isinstance(history, list):
        raise ControlCorruptError(
            f"control file {path!r} is corrupt: 'history' is not a list "
            "— halting fail-closed")
    state["history"] = history[-MAX_HISTORY:]
    dropped = data.get("history_dropped", 0)
    state["history_dropped"] = dropped if isinstance(dropped, int) else 0
    # Entries dropped by this normalisation are counted, never silent.
    if len(history) > MAX_HISTORY:
        state["history_dropped"] += len(history) - MAX_HISTORY
    # The label is derived from the flags, never trusted from disk.
    state["state"] = _state_label(state)
    return state


def _append_history(state, label, reason, set_by):
    """Append one transition to the append-only history (capped at
    MAX_HISTORY; oldest dropped, drop counted). Returns the state."""
    entry = {
        "state": label,
        "reason": reason,
        "set_by": set_by,
        "set_at": _now_iso(),
    }
    history = list(state.get("history") or [])
    history.append(entry)
    dropped = state.get("history_dropped", 0) or 0
    if len(history) > MAX_HISTORY:
        excess = len(history) - MAX_HISTORY
        history = history[excess:]
        dropped += excess
    state["history"] = history
    state["history_dropped"] = dropped
    state["reason"] = reason
    state["set_by"] = set_by
    state["set_at"] = entry["set_at"]
    state["state"] = _state_label(state)
    return state


class ControlState:
    """The pause / resume / emergency-stop state for one control file
    (default: the repo's store/control.json)."""

    def __init__(self, control_path=None):
        self.control_path = control_path or DEFAULT_CONTROL_PATH

    # -- reading ------------------------------------------------------

    def load(self):
        """Load the state. Missing/unreadable file -> the running
        state (never an exception). Corrupt file -> ControlCorruptError
        (fail-closed)."""
        try:
            with open(self.control_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return _default_state()
        except OSError:
            # Unreadable (e.g. permissions) — fail-open to running ONLY
            # because no state could be read at all; documented in the
            # module docstring. A corrupt-but-readable file below is
            # the fail-closed case, not this one.
            return _default_state()
        except json.JSONDecodeError as exc:
            raise ControlCorruptError(
                f"control file {self.control_path!r} is corrupt JSON "
                f"({exc}) — halting fail-closed") from exc
        return _validate_state(data, self.control_path)

    def is_halted(self, state=None):
        """True when the drain/scheduler must halt (paused OR
        emergency_stop). Raises ControlCorruptError on a corrupt file
        (fail-closed) — a corrupt file never reads as 'running'."""
        state = state if state is not None else self.load()
        return bool(state.get("paused") or state.get("emergency_stop"))

    def halt_reason(self, state=None):
        """Human-readable halt reason, or None when running. Raises
        ControlCorruptError on a corrupt file."""
        state = state if state is not None else self.load()
        if state.get("emergency_stop"):
            return ("emergency_stop: "
                    + str(state.get("reason") or "no reason recorded"))
        if state.get("paused"):
            return ("paused: "
                    + str(state.get("reason") or "no reason recorded"))
        return None

    def status(self):
        """Current state dict (load semantics apply)."""
        return self.load()

    # -- writing ------------------------------------------------------

    def _save(self, state):
        write_json_atomic(self.control_path, state)
        return state

    def _transition(self, label, apply_fn, reason, set_by):
        """Locked read-modify-write of one transition. `apply_fn`
        mutates the loaded state dict (paused/emergency_stop flags);
        history + top-level reason/set_by/set_at are recorded here.
        Corrupt file -> ControlCorruptError (fail-closed, nothing
        written). Returns the new state dict."""
        def _apply(data):
            # update_json passes `default` when the file is missing;
            # a corrupt file raises JSONDecodeError before we get here.
            if data is None:
                state = _default_state()
            elif isinstance(data, dict) and data.get("schema") == SCHEMA:
                state = _validate_state(data, self.control_path)
            elif isinstance(data, dict) and "schema" not in data \
                    and not data:
                state = _default_state()
            else:
                raise ControlCorruptError(
                    f"control file {self.control_path!r} is corrupt "
                    "(schema mismatch) — refusing to write over it")
            apply_fn(state)
            return _append_history(state, label, reason, set_by)

        try:
            return update_json(self.control_path, _apply,
                               default=_default_state())
        except json.JSONDecodeError as exc:
            raise ControlCorruptError(
                f"control file {self.control_path!r} is corrupt JSON "
                f"({exc}) — halting fail-closed") from exc

    def pause(self, reason, set_by="Boss"):
        """Pause the drain + scheduler. Idempotent: pausing an already
        paused state still records the transition."""
        def _apply(state):
            state["paused"] = True

        return self._transition(STATE_PAUSED, _apply, reason, set_by)

    def resume(self, reason, set_by="Boss"):
        """Resume: clears ONLY `paused`. Refuses (ControlRefused) while
        an emergency stop is set — resume never silently clears it."""
        current = self.load()
        if current.get("emergency_stop"):
            raise ControlRefused(
                "resume refused: emergency_stop is set — clear it with "
                "clear_emergency_stop(reason) first; resume never "
                "clears an emergency stop")

        def _apply(state):
            state["paused"] = False

        return self._transition(STATE_RESUMED, _apply, reason, set_by)

    def emergency_stop(self, reason, set_by="Boss"):
        """Emergency stop: halts drain + scheduler until explicitly
        cleared. Does NOT touch `paused` (the two flags are
        independent — a stop survives a resume)."""
        def _apply(state):
            state["emergency_stop"] = True

        return self._transition(STATE_EMERGENCY_STOP, _apply, reason,
                                set_by)

    def clear_emergency_stop(self, reason, set_by="Boss"):
        """Clear an emergency stop. Requires a non-empty reason —
        an empty/blank reason raises ValueError and nothing changes."""
        if reason is None or not str(reason).strip():
            raise ValueError(
                "clear_emergency_stop needs a non-empty reason — "
                "refusing to clear the emergency stop without one")
        current = self.load()
        if not current.get("emergency_stop"):
            # Nothing to clear — still record the (no-op) transition so
            # the attempt is visible in history.
            def _noop(state):
                state["emergency_stop"] = False

            return self._transition(STATE_EMERGENCY_STOP_CLEARED, _noop,
                                    reason, set_by)

        def _apply(state):
            state["emergency_stop"] = False

        return self._transition(STATE_EMERGENCY_STOP_CLEARED, _apply,
                                reason, set_by)


def consult(control_path=None):
    """The drain/scheduler consult: (halted, reason).

    halted False + reason None  -> running, work may proceed.
    halted True + reason str    -> paused / emergency_stop: halt.
    Raises ControlCorruptError on a corrupt control file — the caller
    must treat that as halted (fail-closed) and record the error.
    A missing/unreadable file consults as running (fail-open only
    when no state was ever written — see the module docstring)."""
    state = ControlState(control_path=control_path)
    loaded = state.load()
    if state.is_halted(loaded):
        return True, state.halt_reason(loaded)
    return False, None


if __name__ == "__main__":
    # Manual check — TEMP file only, the real store is never touched.
    import tempfile

    tmp_dir = tempfile.mkdtemp()
    tmp_control = os.path.join(tmp_dir, "control.json")
    cs = ControlState(control_path=tmp_control)

    # 1. Missing file loads as running, never an exception.
    assert cs.is_halted() is False and cs.halt_reason() is None
    assert consult(tmp_control) == (False, None)

    # 2. Pause halts; resume restores running; the derived label tracks.
    cs.pause("hold the queue", set_by="Boss")
    assert cs.is_halted() is True
    assert cs.load()["state"] == "paused"
    assert consult(tmp_control)[0] is True
    cs.resume("back to work", set_by="Boss")
    assert cs.is_halted() is False
    assert cs.load()["state"] == "running"

    # 3. Emergency stop survives resume; resume refuses while it is set.
    cs.pause("hold", set_by="Boss")
    cs.emergency_stop("stop everything", set_by="Boss")
    assert cs.load()["state"] == "emergency_stop"
    try:
        cs.resume("try to resume", set_by="Boss")
        raise SystemExit("FAIL: resume cleared an emergency stop")
    except ControlRefused:
        pass
    assert cs.is_halted() is True
    assert cs.load()["emergency_stop"] is True
    # 4. Clearing needs a reason.
    for bad_reason in (None, "", "   "):
        try:
            cs.clear_emergency_stop(bad_reason, set_by="Boss")
            raise SystemExit("FAIL: empty reason cleared the stop")
        except ValueError:
            pass
    assert cs.load()["emergency_stop"] is True
    cs.clear_emergency_stop("all clear", set_by="Boss")
    assert cs.load()["emergency_stop"] is False
    # resume now clears the leftover pause.
    cs.resume("back to work", set_by="Boss")
    assert cs.is_halted() is False

    # 5. History is append-only, capped at 100, drops counted.
    for i in range(105):
        cs.pause(f"pause {i}", set_by="Boss")
    loaded = cs.load()
    assert len(loaded["history"]) == 100, len(loaded["history"])
    assert loaded["history_dropped"] >= 5, loaded["history_dropped"]
    assert loaded["history"][-1]["reason"] == "pause 104"

    # 6. Corrupt file halts fail-closed.
    with open(tmp_control, "w", encoding="utf-8") as f:
        f.write("{not json")
    try:
        cs.load()
        raise SystemExit("FAIL: corrupt control file loaded as running")
    except ControlCorruptError:
        pass
    try:
        consult(tmp_control)
        raise SystemExit("FAIL: corrupt control file consulted as running")
    except ControlCorruptError:
        pass

    print("control: OK (missing=running; pause halts; resume restores; "
          "emergency stop survives resume; clear needs a reason; "
          "history capped at 100 with drops counted; corrupt halts "
          "fail-closed)")
