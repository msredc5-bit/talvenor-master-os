#!/usr/bin/env python3
"""Approve / reject gated actions — operator entry point (B2, 2026-11-21).

The command-line path to decide the ApprovalGateway's records: until
now, approvals could only be decided via the Python API. This script
only DECIDES — executing an approved live action is not its job
(BLOCKED: the execute-after-approval path does not exist in the repo; Boss does it himself).

Usage:
  python3 scripts/approve.py --list
  python3 scripts/approve.py --approve <id> --word send
  python3 scripts/approve.py --reject <id>
  python3 scripts/approve.py --list --approvals-path /tmp/approvals-test.json

--list is read-only: writes nothing (expired pending shows as "pending (expired)"
but is not marked). --approve requires a matching gate word
(the ApprovalGateway itself verifies it) and expired records are refused
(APPROVAL_TTL_MINUTES = 20). --reject needs no word.

--approvals-path defaults to the real store/approvals.json — tests must pass a TEMP path
Stdlib only. No network, no send, no publish, no spend,
no delete, no execute.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(ROOT, "00-CEO-Core")
DEFAULT_STORE_DIR = os.path.join(ROOT, "store")

sys.path.insert(0, CEO_CORE_DIR)

from human_approval_gateway import (  # noqa: E402
    APPROVAL_TTL_MINUTES, ApprovalGateway)


def _age_minutes(record):
    try:
        asked = datetime.fromisoformat(
            str(record.get("requested_at")).replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - asked).total_seconds() / 60.0
    except (TypeError, ValueError):
        return None


def _is_expired(record):
    age = _age_minutes(record)
    return (record.get("status") == "pending" and age is not None
            and age > APPROVAL_TTL_MINUTES)


def _show(record):
    status = record.get("status", "?")
    if _is_expired(record):
        status += " (expired — approve will refuse)"
    age = _age_minutes(record)
    return {
        "id": record.get("id"),
        "action": record.get("action"),
        "detail": record.get("detail"),
        "requested_by": record.get("requested_by"),
        "status": status,
        "requested_at": record.get("requested_at"),
        "age_minutes": round(age, 1) if age is not None else None,
        "decided_by": record.get("decided_by"),
        "decided_at": record.get("decided_at"),
        "gate_word": record.get("gate_word"),
    }


def list_approvals(approvals_path):
    """Show all records (read-only — nothing is written)."""
    gateway = ApprovalGateway(approvals_path=approvals_path)
    records = [_show(r) for r in gateway.records]
    pending = [r for r in records if r["status"].startswith("pending")]
    print(json.dumps(records, indent=2, ensure_ascii=False))
    print(f"\n{len(records)} approval(s), {len(pending)} pending "
          f"(TTL {APPROVAL_TTL_MINUTES} min). Decide with --approve ID "
          "--word <gate word> or --reject ID. Deciding only — the "
          "approved live action is NOT executed by this script.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Decide gated approvals (list / approve / reject). "
                    "Deciding only — never executes the approved action.")
    parser.add_argument("--list", action="store_true",
                        help="list all approval records (read-only)")
    parser.add_argument("--approve", default=None, metavar="ID",
                        help="approve this approval id (needs --word)")
    parser.add_argument("--reject", default=None, metavar="ID",
                        help="reject this approval id")
    parser.add_argument("--word", default=None,
                        help="gate word for --approve (e.g. send, 'post it', 'upload it')")
    parser.add_argument("--approvals-path",
                        default=os.path.join(DEFAULT_STORE_DIR, "approvals.json"),
                        help="approvals JSON path (default: store/approvals.json)")
    args = parser.parse_args(argv)

    if args.list:
        return list_approvals(args.approvals_path)

    if args.approve:
        if not args.word:
            parser.error("--approve needs --word <gate word>")
        gateway = ApprovalGateway(approvals_path=args.approvals_path)
        try:
            record = gateway.approve(args.approve, gate_word=args.word)
        except (KeyError, ValueError) as exc:
            print(f"approve: FAILED: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(_show(record), indent=2, ensure_ascii=False))
        print("Approved — the live action itself is NOT executed here. "
              "Boss runs it himself with his exact word.")
        return 0

    if args.reject:
        gateway = ApprovalGateway(approvals_path=args.approvals_path)
        try:
            record = gateway.reject(args.reject)
        except (KeyError, ValueError) as exc:
            print(f"reject: FAILED: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(_show(record), indent=2, ensure_ascii=False))
        return 0

    parser.error("nothing to do — use --list, --approve ID --word WORD, "
                 "or --reject ID")
    return 2


if __name__ == "__main__":
    sys.exit(main())
