#!/usr/bin/env python3
"""concept_score.py — deterministic concept scorer (stage 2a-concept, MOCK).

Method: sections/plan/skills/topic-researcher.md + pipeline.md stage
2a-concept — 3-5 concepts, 1-10 score, one-line reason per score from a
fixed rubric. The tool scores ONLY the signals Boss supplies (0-100
each) — it does NOT fetch the web, does NOT measure real demand, does
NOT invent trend data. A score without a supplied signal is refused.

    python3 tools/concept_score.py                   # mock samples
    python3 tools/concept_score.py --concepts concepts.json
    python3 tools/concept_score.py --concepts concepts.json --json

Input JSON: [{"concept": "...", "clarity": 80, "fit": 74,
"payoff_proof": 65, "notes": "..."}, ...]  (3-5 entries expected)

Axes (fixed rubric):
  Clarity       40%  Can the idea be said in one line? (Boss-supplied)
  Fit           35%  Fits the niche + audience + channel voice?
  Payoff-proof  25%  Is the promised payoff shown/provable on screen?

Total is 1-10. 7+ STRONG, 5-6.9 WORKABLE, below 5 WEAK. Each score
carries a one-line reason taken from the fixed rubric band — a score
is never given without its reason.
Stdlib only — no network, no LLM, no file writes.
"""

import argparse
import json
import sys

WEIGHTS = {
    "clarity": 0.40,
    "fit": 0.35,
    "payoff_proof": 0.25,
}

# Fixed rubric — reason lines per axis band. The reason is chosen by the
# supplied signal, never written freehand.
REASONS = {
    "clarity": [
        (80, "one line, no explaining needed"),
        (60, "clear after one extra sentence"),
        (40, "needs untangling — two ideas in one"),
        (0, "cannot be said in one line yet"),
    ],
    "fit": [
        (80, "niche + audience + voice all match"),
        (60, "fits the niche, voice needs a check"),
        (40, "off-niche or off-audience — rethink the angle"),
        (0, "does not fit this channel"),
    ],
    "payoff_proof": [
        (80, "payoff can be shown on screen in 20 seconds"),
        (60, "payoff shown, but late in the video"),
        (40, "payoff is claimed, not shown"),
        (0, "no payoff to show — hook would be a summary"),
    ],
}

# Mock samples — clearly labelled, only used when no input file is given.
MOCK_SAMPLES = [
    {"concept": "Nano Banana 2 free test, 5 edits on screen (SAMPLE)",
     "clarity": 88, "fit": 84, "payoff_proof": 82,
     "notes": "SAMPLE signals — not measured"},
    {"concept": "AI tools news roundup (SAMPLE)",
     "clarity": 62, "fit": 58, "payoff_proof": 44,
     "notes": "SAMPLE signals — not measured"},
    {"concept": "My channel journey (SAMPLE)",
     "clarity": 45, "fit": 40, "payoff_proof": 30,
     "notes": "SAMPLE signals — not measured"},
]


def band(total):
    """1-10 total -> STRONG / WORKABLE / WEAK."""
    if total >= 7:
        return "STRONG"
    if total >= 5:
        return "WORKABLE"
    return "WEAK"


def _reason(axis, value):
    for floor, text in REASONS[axis]:
        if value >= floor:
            return text
    return REASONS[axis][-1][1]


def score_concept(entry):
    """One concept -> scored dict with a one-line reason per axis."""
    concept = (entry.get("concept") or "").strip()
    if not concept:
        raise ValueError("concept entry needs a 'concept'")
    signals = {}
    for key in ("clarity", "fit", "payoff_proof"):
        value = entry.get(key)
        if value is None or isinstance(value, bool) \
                or not isinstance(value, (int, float)):
            raise ValueError(
                f"concept {concept!r}: signal {key!r} missing or not a "
                "number (0-100, Boss-supplied — never guessed)")
        if not 0 <= value <= 100:
            raise ValueError(
                f"concept {concept!r}: signal {key!r}={value} out of range 0-100")
        signals[key] = float(value)
    total = round(sum(signals[k] * WEIGHTS[k] for k in signals) / 10.0, 1)
    return {
        "concept": concept,
        "axes": {k: round(v, 1) for k, v in signals.items()},
        "reasons": {k: _reason(k, v) for k, v in signals.items()},
        "total": total,
        "band": band(total),
        "notes": entry.get("notes", ""),
    }


def rank(entries):
    """Score every concept, best first. 3-5 expected; other counts are
    scored anyway but flagged (the skill wants 3-5)."""
    scored = [score_concept(e) for e in entries]
    scored.sort(key=lambda r: -r["total"])
    return scored


def _load_concepts(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list) or not data:
        raise ValueError(f"{path}: expected a non-empty JSON list of concepts")
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Score 3-5 video concepts 1-10 (stage 2a, MOCK).")
    parser.add_argument("--concepts", help="JSON file of concepts")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable output")
    args = parser.parse_args(argv)
    if args.concepts:
        entries = _load_concepts(args.concepts)
        source = args.concepts
    else:
        entries = MOCK_SAMPLES
        source = "MOCK SAMPLES (not measured — pass --concepts for real signals)"
    if len(entries) < 3 or len(entries) > 5:
        print(f"warning: expected 3-5 concepts, got {len(entries)}",
              file=sys.stderr)
    try:
        ranked = rank(entries)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(
            {"source": source, "ranked": ranked}, indent=1, ensure_ascii=False))
        return 0
    print(f"\n  concept scores — source: {source}\n")
    for row in ranked:
        print(f"    {row['total']:4.1f}  {row['band']:<8}  {row['concept']}")
        for axis in ("clarity", "fit", "payoff_proof"):
            print(f"         {axis:<12} {row['axes'][axis]:5.1f}  "
                  f"{row['reasons'][axis]}")
        if row["notes"]:
            print(f"         {row['notes']}")
    if ranked:
        print(f"\n  top pick: {ranked[0]['concept']}  ({ranked[0]['total']}, "
              f"{ranked[0]['band']})\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
