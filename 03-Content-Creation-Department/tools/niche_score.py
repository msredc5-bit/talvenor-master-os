#!/usr/bin/env python3
"""niche_score.py — deterministic niche scorer (stage 0a-niche, MOCK).

Method: youtube-skills/yt-niche/SKILL.md — 4 axes, 1-10 total.
The tool scores ONLY the signals Boss supplies (0-100 each) — it does
NOT fetch the web, does NOT measure real demand, does NOT invent trend
data. Scores come from Boss-supplied facts, never from a guess.

    python3 tools/niche_score.py                    # mock samples
    python3 tools/niche_score.py --niches niches.json
    python3 tools/niche_score.py --niches niches.json --json

Input JSON: [{"name": "...", "demand": 78, "competition": 62,
"monetization": 74, "fresher_fit": 88, "notes": "..."}, ...]

Axes (weights from the skill):
  Demand          30%  Do people search and watch this?
  Competition gap 30%  Room to enter = 100 - competition. Lower
                       competition scores higher — a fresher cannot
                       out-shout an entrenched niche.
  Monetization    25%  Can it pay — products, services, sponsors?
  Fresher-fit     15%  Can a beginner start with $0 + a phone/PC?

Total is 1-10. 7+ STRONG, 5-6.9 WORKABLE, below 5 WEAK.
Stdlib only — no network, no LLM, no file writes (except --out).
"""

import argparse
import json
import os
import sys

WEIGHTS = {
    "demand": 0.30,
    "competition_gap": 0.30,
    "monetization": 0.25,
    "fresher_fit": 0.15,
}

# Mock samples — clearly labelled, only used when no input file is given.
# These are PLACEHOLDER signals for a dry run, not real measurements.
MOCK_SAMPLES = [
    {"name": "AI Tools & Tutorials (SAMPLE)",
     "demand": 82, "competition": 68, "monetization": 74,
     "fresher_fit": 90, "notes": "SAMPLE signals — not measured"},
    {"name": "Budget Phone Repairs (SAMPLE)",
     "demand": 64, "competition": 41, "monetization": 58,
     "fresher_fit": 78, "notes": "SAMPLE signals — not measured"},
]


def band(total):
    """1-10 total -> STRONG / WORKABLE / WEAK (skill bands)."""
    if total >= 7:
        return "STRONG"
    if total >= 5:
        return "WORKABLE"
    return "WEAK"


def score_niche(entry):
    """One candidate -> scored dict. Signals must be 0-100 numbers;
    missing/invalid signals raise ValueError (never silently scored)."""
    name = (entry.get("name") or "").strip()
    if not name:
        raise ValueError("niche entry needs a 'name'")
    signals = {}
    for key in ("demand", "competition", "monetization", "fresher_fit"):
        value = entry.get(key)
        if value is None or isinstance(value, bool) \
                or not isinstance(value, (int, float)):
            raise ValueError(
                f"niche {name!r}: signal {key!r} missing or not a number "
                "(0-100, Boss-supplied — never guessed)")
        if not 0 <= value <= 100:
            raise ValueError(
                f"niche {name!r}: signal {key!r}={value} out of range 0-100")
        signals[key] = float(value)
    gap = 100.0 - signals["competition"]
    axes = {
        "demand": signals["demand"],
        "competition_gap": gap,
        "monetization": signals["monetization"],
        "fresher_fit": signals["fresher_fit"],
    }
    total = round(sum(axes[k] * WEIGHTS[k] for k in axes) / 10.0, 1)
    return {
        "name": name,
        "axes": {k: round(v, 1) for k, v in axes.items()},
        "total": total,
        "band": band(total),
        "notes": entry.get("notes", ""),
    }


def rank(entries):
    """Score every candidate, best first. Invalid entries fail loudly."""
    scored = [score_niche(e) for e in entries]
    scored.sort(key=lambda r: -r["total"])
    return scored


def _load_niches(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path}: expected a non-empty JSON list of niches")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score niche candidates 1-10 on 4 axes (yt-niche, MOCK).")
    parser.add_argument("--niches", help="JSON file of candidates (see --help text)")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)
    if args.niches:
        entries = _load_niches(args.niches)
        source = args.niches
    else:
        entries = MOCK_SAMPLES
        source = "MOCK SAMPLES (not measured — pass --niches for real signals)"
    try:
        ranked = rank(entries)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(
            {"source": source, "ranked": ranked}, indent=1, ensure_ascii=False))
        return 0
    print(f"\n  niche scores — source: {source}\n")
    for row in ranked:
        axes = "  ".join(
            f"{k} {v:.0f}" for k, v in row["axes"].items())
        print(f"    {row['total']:4.1f}  {row['band']:<8}  {row['name']}")
        print(f"         {axes}")
        if row["notes"]:
            print(f"         {row['notes']}")
    if ranked:
        print(f"\n  top pick: {ranked[0]['name']}  ({ranked[0]['total']}, "
              f"{ranked[0]['band']})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
