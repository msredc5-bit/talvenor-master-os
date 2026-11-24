#!/usr/bin/env python3
"""Approval centre CLI — thin front end for 00-CEO-Core/approval_centre.py
(Phase 7, Worker C).

Deciding only — never executes the approved live action (Boss runs it
himself with his exact word). All decisions go through the
ApprovalGateway's own methods; this script never writes
approvals.json directly.

Usage:
  python3 scripts/approval_centre.py list
  python3 scripts/approval_centre.py approve <id> <gate-word>
  python3 scripts/approval_centre.py reject <id>
  python3 scripts/approval_centre.py list --approvals-path /tmp/approvals-test.json

--approvals-path defaults to the real store/approvals.json — tests
must pass a TEMP path. Stdlib only. No network, no send, no publish,
no spend, no delete, no execute.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
DEFAULT_STORE_DIR = os.path.join(ROOT, "store")

sys.path.insert(0, CEO_CORE_DIR)

from approval_centre import ApprovalCentre  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Approval centre (list / approve / reject). "
                    "Deciding only — never executes the approved action.")
    parser.add_argument("--approvals-path",
                        default=os.path.join(DEFAULT_STORE_DIR,
                                             "approvals.json"),
                        help="approvals JSON path (default: store/approvals.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    # --approvals-path works before AND after the subcommand: the
    # subparsers' copy uses SUPPRESS so it never clobbers a value
    # given before the subcommand.
    sub.add_parser("list", help="list pending approvals with age/expiry")
    p_approve = sub.add_parser("approve", help="approve one approval id")
    p_approve.add_argument("id", help="approval id")
    p_approve.add_argument("gate_word", help="gate word, e.g. send, 'post it'")
    p_reject = sub.add_parser("reject", help="reject one approval id")
    p_reject.add_argument("id", help="approval id")
    for p in (sub.choices["list"], p_approve, p_reject):
        p.add_argument("--approvals-path", default=argparse.SUPPRESS,
                       help="approvals JSON path")

    args = parser.parse_args(argv)
    centre = ApprovalCentre(approvals_path=args.approvals_path)

    if args.command == "list":
        pending = centre.list_pending()
        print(json.dumps(pending, indent=2, ensure_ascii=False))
        print(f"\n{len(pending)} pending approval(s). Decide with "
              "approve <id> <gate-word> or reject <id>. Deciding only — "
              "the approved live action is NOT executed by this script.")
        return 0

    try:
        if args.command == "approve":
            record = centre.decide(args.id, "approve",
                                   gate_word=args.gate_word)
        else:  # reject
            record = centre.decide(args.id, "reject")
    except (KeyError, ValueError) as exc:
        print(f"approval_centre: FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(record, indent=2, ensure_ascii=False))
    print("Decided — the live action itself is NOT executed here. "
          "Boss runs it himself with his exact word.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
