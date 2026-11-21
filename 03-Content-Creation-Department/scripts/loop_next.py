#!/usr/bin/env python3
"""loop_next.py — deterministic next-brief generator (stage 10-next-plan, MOCK).

Method: youtube-skills/yt-plan/SKILL.md + sections/plan/skills/
content-planner.md — reads the previous report file if present and writes
the next run's brief; if there is no previous report, the brief repeats
the previous plan (video 0, so there is nothing to learn from yet).

    python3 scripts/loop_next.py
    python3 scripts/loop_next.py --report reports/week1.json --plan plans/week1.json
    python3 scripts/loop_next.py --report reports/week1.json --out briefs/week2.json
    python3 scripts/loop_next.py --self-test

Rules (honest, deterministic — no LLM, no network, no invented numbers):
  - A report file is read only if it exists and parses. JSON reports may
    carry best_video / worst_video / change (one concrete change) /
    metrics; Markdown reports are scanned for those same labelled lines.
  - The next brief NEVER invents a number, a result, or a verdict. Every
    line in it quotes the report file or says the value is missing.
  - No report -> the brief says so in the skill's own words:
    "No previous report (videos 0), so the next brief repeats the previous plan"
    and repeats the previous plan file if one was given.
  - The brief shape follows yt-plan: one anchor, one cheap one, three
    Shorts cut from the anchor — never seven uploads in a week.
"""

import argparse
import json
import os
import sys

NO_REPORT_LINE = ("No previous report (videos 0), so the next brief repeats the "
                  "previous plan")


def _read_report(path):
    """Parse a previous report (JSON or Markdown). Returns a dict with
    only the keys the file actually carried — missing keys stay absent,
    never defaulted to invented values."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    report = {"source": path}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        for key in ("best_video", "worst_video", "change", "videos",
                    "views", "subs"):
            if key in data:
                report[key] = data[key]
        return report
    # Markdown: look for the same labelled lines, verbatim.
    for line in raw.splitlines():
        stripped = line.strip()
        for key, label in (("best_video", "best"),
                           ("worst_video", "worst"),
                           ("change", "change")):
            if stripped.lower().startswith(label + ":") and key not in report:
                report[key] = stripped[len(label) + 1:].strip()
    return report


def build_brief(report=None, plan=None):
    """Deterministic next brief from a parsed report and/or a previous
    plan. Returns a dict (JSON-serialisable)."""
    brief = {"stage": "10-next-plan", "mock": True, "draft_only": True}
    if report is None:
        brief["note"] = NO_REPORT_LINE
        if plan:
            brief["repeat_plan"] = plan
            brief["anchor"] = (plan.get("anchor")
                               or "Previous plan's anchor — as written in the plan file")
            brief["cheap_one"] = (plan.get("cheap_one")
                                  or "Previous plan's cheap video")
            brief["shorts"] = plan.get("shorts") or []
        else:
            brief["anchor"] = "Previous plan's anchor (no plan file given)"
            brief["cheap_one"] = "Previous plan's cheap video"
            brief["shorts"] = []
        return brief
    brief["from_report"] = report.get("source")
    if report.get("best_video"):
        brief["anchor"] = ("Follow-up to the best video: %s — do again what worked, "
                           "in the same format." % report["best_video"])
    else:
        brief["anchor"] = "Best video unknown (not in the report) — the anchor is the previous plan."
    if report.get("worst_video"):
        brief["cheap_one"] = ("Fix for the worst video: %s — same topic, shorter, "
                              "with the hook changed." % report["worst_video"])
    else:
        brief["cheap_one"] = "Worst video unknown — the cheap video is the previous plan."
    if report.get("change"):
        brief["one_change"] = report["change"]
    else:
        brief["one_change"] = ("No one change for next week is written in the report — "
                               "no change is made up without a report.")
    brief["shorts"] = ["3 Shorts from the anchor — not written separately, cut from the anchor."]
    return brief


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def self_test():
    """Both branches, on temp files only: (1) no report -> the repeat
    line; (2) a report with best/worst/change -> the brief quotes them."""
    import tempfile

    tmp = tempfile.mkdtemp()
    brief = build_brief(report=None, plan=None)
    ok1 = brief.get("note") == NO_REPORT_LINE
    print(f"  [{'PASS' if ok1 else 'FAIL'}] no report -> repeat line")
    report_path = os.path.join(tmp, "report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"best_video": "Nano Banana 2 test",
                   "worst_video": "AI news roundup",
                   "change": "Confirm the title's promise in the hook in the first 5 seconds"},
                  f)
    report = _read_report(report_path)
    brief = build_brief(report=report, plan=None)
    ok2 = ("Nano Banana 2 test" in brief.get("anchor", "")
           and "AI news roundup" in brief.get("cheap_one", "")
           and "Confirm the title's promise in the hook" in brief.get("one_change", ""))
    print(f"  [{'PASS' if ok2 else 'FAIL'}] report -> brief quotes best/worst/change")
    return 0 if (ok1 and ok2) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Write the next run's brief from the previous report (MOCK).")
    parser.add_argument("--report", help="previous report file (JSON or Markdown)")
    parser.add_argument("--plan", help="previous plan/brief file (JSON)")
    parser.add_argument("--out", help="write the brief JSON here (default: stdout)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    report = None
    if args.report:
        if not os.path.isfile(args.report):
            print(f"error: report file not found: {args.report}", file=sys.stderr)
            return 1
        try:
            report = _read_report(args.report)
        except (OSError, ValueError) as exc:
            print(f"error: cannot read report: {exc}", file=sys.stderr)
            return 1
    plan = None
    if args.plan:
        if not os.path.isfile(args.plan):
            print(f"error: plan file not found: {args.plan}", file=sys.stderr)
            return 1
        try:
            plan = _load_json(args.plan)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"error: cannot read plan: {exc}", file=sys.stderr)
            return 1
    brief = build_brief(report=report, plan=plan)
    text = json.dumps(brief, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"brief written: {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
