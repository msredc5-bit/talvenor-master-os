#!/usr/bin/env python3
"""Snapshot store/ to a timestamped backup dir (Phase 1, Unified OS).

  python3 scripts/backup_store.py [--out DIR] [--restore-test]

Default backup dir: <repo>/backups/store-<UTC timestamp>/ — backups/
is git-ignored, so a snapshot never lands on GitHub. --out overrides
the destination (use a TEMP dir in tests).

--restore-test restores the snapshot into a TEMP dir and verifies
every file is present and every .json parses — it never touches the
real store.

Stdlib only. No network, no send, no publish, no spend.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE_DIR = os.path.join(ROOT, "store")
DEFAULT_BACKUPS_DIR = os.path.join(ROOT, "backups")


def snapshot_name():
    return ("store-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))


def backup_store(store_dir=STORE_DIR, out=None):
    """Copies store_dir to a timestamped dir; returns the dest path."""
    dest = out or os.path.join(DEFAULT_BACKUPS_DIR, snapshot_name())
    if os.path.exists(dest):
        raise FileExistsError(f"backup dir already exists: {dest}")
    shutil.copytree(store_dir, dest)
    return dest


def list_files(root):
    out = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), root))
    return sorted(out)


def verify_backup(backup_dir):
    """Every file present + every .json parses. Returns (ok, detail)."""
    files = list_files(backup_dir)
    if not files:
        return False, "backup is empty"
    bad = []
    for rel in files:
        if rel.endswith(".json"):
            try:
                with open(os.path.join(backup_dir, rel),
                          encoding="utf-8") as f:
                    json.load(f)
            except (OSError, json.JSONDecodeError) as exc:
                bad.append(f"{rel}: {exc}")
    if bad:
        return False, "; ".join(bad)
    return True, f"{len(files)} files, all JSON parses"


def restore_test(backup_dir):
    """Restores the snapshot to a TEMP dir and verifies it there.
    Returns (ok, detail). Never touches the real store."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = os.path.join(tmp, "store")
        shutil.copytree(backup_dir, dest)
        ok, detail = verify_backup(dest)
        same = list_files(dest) == list_files(backup_dir)
        return ok and same, detail + ("; file list matches" if same
                                      else "; file list DIFFERS")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Snapshot store/ to a timestamped backup dir.")
    parser.add_argument("--out", default=None,
                        help="destination dir (default: backups/store-<timestamp>/)")
    parser.add_argument("--restore-test", action="store_true",
                        help="after backing up, restore to a TEMP dir and verify")
    args = parser.parse_args(argv)
    try:
        dest = backup_store(out=args.out)
    except (OSError, FileExistsError) as exc:
        print(f"backup_store: FAILED: {exc}", file=sys.stderr)
        return 1
    files = list_files(dest)
    print(f"backup_store: {len(files)} files -> {dest}")
    ok, detail = verify_backup(dest)
    print(f"backup_store: verify: {'OK' if ok else 'FAILED'} — {detail}")
    if not ok:
        return 1
    if args.restore_test:
        ok, detail = restore_test(dest)
        print(f"backup_store: restore-test: {'OK' if ok else 'FAILED'} — {detail}")
        return 0 if ok else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
