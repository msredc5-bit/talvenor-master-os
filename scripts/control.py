"""Operator CLI for the control plane — pause / resume /
emergency-stop / clear / status (Phase 8, Worker C).

Thin front end over 00-CEO-Core/control.py's ControlState — the
same pattern as scripts/approval_centre.py over the ApprovalGateway.
No control logic is duplicated here; every command calls the real
ControlState methods on the control file given by --control-path
(default: the repo store/control.json).

Usage:
  python3 scripts/control.py status [--control-path PATH]
  python3 scripts/control.py pause --reason "hold the queue" [--by Boss]
  python3 scripts/control.py resume --reason "back to work"
  python3 scripts/control.py emergency-stop --reason "stop everything"
  python3 scripts/control.py clear --reason "all clear"

Exit codes: 0 ok; 2 usage error; 3 corrupt control file (fail-closed
— nothing was changed); 4 transition refused (e.g. resume while an
emergency stop is set). Stdlib only. No network, no send, no publish,
no spend, no delete.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "00-CEO-Core"))

from control import (  # noqa: E402
    DEFAULT_CONTROL_PATH,
    ControlCorruptError,
    ControlRefused,
    ControlState,
)


def _print_state(state):
    print("state: %(state)s | paused: %(paused)s | "
          "emergency_stop: %(emergency_stop)s" % state)
    print("reason: %s | set_by: %s | set_at: %s" % (
        state.get("reason"), state.get("set_by"), state.get("set_at")))
    print("history entries: %d (dropped: %d)" % (
        len(state.get("history") or []), state.get("history_dropped", 0)))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Talvenor control plane: pause / resume / "
                    "emergency-stop / clear / status.")
    parser.add_argument("--control-path", default=None,
                        help="control file (default: store/control.json)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show the current control state")
    for name in ("pause", "resume", "emergency-stop", "clear"):
        p = sub.add_parser(name, help="%s the control plane" % name)
        p.add_argument("--reason", required=True,
                       help="reason recorded in history (required)")
        p.add_argument("--by", default="Boss",
                       help="who set it (default: Boss)")
    args = parser.parse_args(argv)
    state = ControlState(
        control_path=args.control_path or DEFAULT_CONTROL_PATH)
    try:
        if args.command == "status":
            _print_state(state.load())
            return 0
        if args.command == "pause":
            new = state.pause(args.reason, set_by=args.by)
        elif args.command == "resume":
            new = state.resume(args.reason, set_by=args.by)
        elif args.command == "emergency-stop":
            new = state.emergency_stop(args.reason, set_by=args.by)
        elif args.command == "clear":
            new = state.clear_emergency_stop(args.reason, set_by=args.by)
        else:  # pragma: no cover - argparse enforces the choices
            parser.error("unknown command %r" % args.command)
    except ControlCorruptError as exc:
        print("CORRUPT control file — halting fail-closed, nothing "
              "changed: %s" % exc, file=sys.stderr)
        return 3
    except ControlRefused as exc:
        print("REFUSED: %s" % exc, file=sys.stderr)
        return 4
    except ValueError as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        return 2
    _print_state(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
