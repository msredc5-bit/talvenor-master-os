#!/usr/bin/env python3
"""generate_ceo_report.py — CLI for the Phase 7 CEO reporting generator.

Writes the daily / weekly / monthly Founder CEO report (Markdown +
JSON twin) to reports/ceo/<period>-<YYYY-MM-DD>.md (+ .json).

Read-only on the store: generation never writes to store/. Draft only —
the report is never sent or published. Stdlib only, no network, no
spend, no deployment, no job activation.

  python3 scripts/generate_ceo_report.py --period weekly
  python3 scripts/generate_ceo_report.py --period daily --out-dir reports/ceo

The output directory must stay inside the repo (an absolute out-dir
outside the repo is refused).
"""

import argparse
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CEO_CORE_DIR = os.path.join(BASE, "00-CEO-Core")
sys.path.insert(0, CEO_CORE_DIR)

from ceo_reporting import generate_report, render_markdown  # noqa: E402

DEFAULT_STORE_DIR = os.path.join(BASE, "store")
DEFAULT_OUT_DIR = os.path.join(BASE, "reports", "ceo")


def _inside_repo(path):
    """True when the resolved path is inside the repo root."""
    root = os.path.realpath(BASE)
    target = os.path.realpath(path)
    return target == root or target.startswith(root + os.sep)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate the Founder CEO report (draft, read-only).")
    parser.add_argument("--period", required=True,
                        choices=("daily", "weekly", "monthly"),
                        help="Report period (rolling window).")
    parser.add_argument("--store-dir", default=DEFAULT_STORE_DIR,
                        help="Store directory (default: repo store/).")
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR,
                        help="Output directory (default: reports/ceo/, "
                             "must stay inside the repo).")
    args = parser.parse_args(argv)

    if not _inside_repo(args.out_dir):
        parser.error("refusing to write outside the repo: %s"
                     % args.out_dir)
    os.makedirs(args.out_dir, exist_ok=True)

    report = generate_report(args.store_dir, args.period)
    date = report["window"]["end_utc"][:10]  # YYYY-MM-DD of the window end
    base_name = "%s-%s" % (args.period, date)
    md_path = os.path.join(args.out_dir, base_name + ".md")
    json_path = os.path.join(args.out_dir, base_name + ".json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(report))
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, sort_keys=True)
    print("ceo report (%s) -> %s" % (args.period, md_path))
    print("ceo report json -> %s" % json_path)
    tasks = report["tasks"]
    appr = report["approvals"]
    usage = report["usage"]
    print("tasks=%s in_window=%s approvals_pending=%s usage_calls=%s "
          "total_usd=%s" % (
              tasks.get("total"), tasks.get("in_window"),
              appr.get("pending"), usage.get("total_calls"),
              usage.get("total_usd")))
    return 0


if __name__ == "__main__":
    # Self-test — TEMP store + TEMP out-dir only, the real store and
    # reports/ceo/ are never touched.
    import tempfile
    from datetime import datetime, timezone

    tmp_dir = tempfile.mkdtemp()
    tmp_store = os.path.join(tmp_dir, "store")
    tmp_out = os.path.join(tmp_dir, "out")
    os.makedirs(tmp_store)
    with open(os.path.join(tmp_store, "tasks.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "tasks-v1", "records": [
            {"id": "t1", "status": "queued", "type": "research",
             "business": "agency",
             "queued_at": "2026-11-25T00:00:00+00:00"},
            {"id": "t2", "status": "done", "type": "draft",
             "business": "agency",
             "queued_at": "2026-11-25T01:00:00+00:00"},
        ]}, f)
    with open(os.path.join(tmp_store, "approvals.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "approvals-v1", "records": [
            {"id": "a1", "status": "pending", "action": "send_email",
             "detail": "test send",
             "requested_at": "2026-11-24T12:00:00+00:00"},
        ]}, f)
    with open(os.path.join(tmp_store, "usage_ledger.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "usage-ledger-v1", "monthly_cap_usd": 0.0,
                   "records": []}, f)
    with open(os.path.join(tmp_store, "memory.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "owner-memory-v1", "entries": [],
                   "boxes": []}, f)
    with open(os.path.join(tmp_store, "schedules.json"), "w",
              encoding="utf-8") as f:
        json.dump({"schema": "schedules-v1", "records": []}, f)
    # Refusal: an out-dir outside the repo must be rejected.
    try:
        main(["--period", "weekly", "--store-dir", tmp_store,
              "--out-dir", os.path.join(tmp_dir, "outside")])
        raise SystemExit("FAIL: out-dir outside the repo was not refused")
    except SystemExit as exc:
        assert exc.code == 2, exc.code  # argparse error exit
    # Happy path on the temp store (out-dir inside the repo? No — the
    # temp out-dir is outside the repo, so exercise generate_report +
    # render_markdown directly and check the files the CLI would write).
    fixed_end = datetime(2026, 11, 25, 12, 0, 0, tzinfo=timezone.utc)
    rep = generate_report(tmp_store, "weekly", end=fixed_end)
    assert rep["tasks"]["total"] == 2 and rep["approvals"]["pending"] == 1
    assert rep["tasks"]["by_status"] == {"done": 1, "queued": 1}
    os.makedirs(tmp_out, exist_ok=True)
    md_text = render_markdown(rep)
    with open(os.path.join(tmp_out, "weekly-2026-11-25.md"), "w",
              encoding="utf-8") as f:
        f.write(md_text)
    with open(os.path.join(tmp_out, "weekly-2026-11-25.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False, sort_keys=True)
    assert os.path.isfile(os.path.join(tmp_out, "weekly-2026-11-25.md"))
    assert "a1" in md_text
    print("generate_ceo_report: OK (outside-repo out-dir refused; temp "
          "store 2 tasks / 1 pending approval; md+json written)")
    sys.exit(main())
