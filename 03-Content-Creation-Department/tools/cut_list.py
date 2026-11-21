#!/usr/bin/env python3
"""cut_list.py — transcript-in, cut-list-out (stage 5-edit, MOCK).

Method: youtube-skills/yt-edit/deadair.py (DEAD / FILLER / REPEAT cuts
from a timestamped transcript) + chapter boundaries + Shorts moments —
all rule-based, deterministic, no LLM, no network. It prints an edit
decision list (EDL); it does NOT cut any file — the editor applies it.

    python3 tools/cut_list.py transcript.srt
    python3 tools/cut_list.py transcript.srt --floor 0.35 --json
    python3 tools/cut_list.py --self-test

What it finds:
  DEAD    gaps between spoken cues longer than the floor (default 0.45s)
  FILLER  cues that are only filler ("um", "so yeah", "basically")
  REPEAT  a sentence restarted — the second take of the same opening
  CHAPTER a boundary at a long pause (>= 2.0s) where the next cue opens a
          new point (discourse marker or a fresh sentence). The chapter
          label is the cue's own first words, quoted — never invented.
  SHORTS  30-second windows around the highest-scoring cues (concrete
          numbers/names, a question, direct address, a stake). Top 3,
          non-overlapping. A Shorts moment is a candidate, not a promise.

Input: .srt / .vtt / whisper .json (same loader as deadair.py).
Stdlib only — no network, no LLM, no media touched.
"""

import argparse
import json
import os
import re
import sys

FILLER_ONLY = re.compile(r"^[\s,.-]*((um+|uh+|er+|ah+|so|okay|ok|right|yeah|like|anyway|basically|"
                         r"actually|you know|i mean|let me see|hold on)[\s,.-]*)+$", re.I)
CHAPTER_MARKERS = re.compile(
    r"^(first|next|now|then|finally|second|third|step\s*\d+|number\s*\d+|"
    r"another|lastly|in the end)\b", re.I)
CONCRETE = re.compile(r"\b(\d[\d,.]*\s?(%|k|m|x)?|\$\d)\b")
QUESTION = re.compile(r"\?")
YOU = re.compile(r"\b(you|your|you're|youre)\b", re.I)
STAKE = re.compile(r"\b(lose|lost|wasting|waste|quit|fail|broke|cost|risk|stop|never|die|dead)\b", re.I)

CHAPTER_PAUSE = 2.0   # seconds — a pause this long can open a chapter
SHORTS_WINDOW = 30.0  # seconds per Shorts candidate window
SHORTS_TOP = 3


def parse_ts(text):
    text = text.strip().replace(",", ".")
    parts = text.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    return int(parts[0]) * 60 + float(parts[1])


def load(path):
    """Transcript file -> [(start, end, text), ...]. SRT/VTT/whisper JSON."""
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    if path.endswith(".json"):
        data = json.loads(raw)
        segs = data.get("segments", data if isinstance(data, list) else [])
        return [(float(s["start"]), float(s["end"]), (s.get("text") or "").strip())
                for s in segs]
    cues, cur = [], None
    for line in raw.splitlines():
        m = re.match(r"\s*(\d[\d:.,]+)\s*-->\s*(\d[\d:.,]+)", line)
        if m:
            cur = [parse_ts(m.group(1)), parse_ts(m.group(2)), []]
            cues.append(cur)
        elif cur is not None and line.strip() and not line.strip().isdigit():
            cur[2].append(line.strip())
    return [(a, b, " ".join(t)) for a, b, t in cues if t]


def _norm(text):
    return re.sub(r"[^a-z ]", "", text.lower()).split()


def find_cuts(cues, floor=0.45):
    """DEAD / FILLER / REPEAT cuts (deadair.py method)."""
    cuts = []
    for i, (start, end, text) in enumerate(cues):
        if FILLER_ONLY.match(text):
            cuts.append({"kind": "FILLER", "start": start, "end": end,
                         "why": text.strip()[:48]})
        if i:
            gap = start - cues[i - 1][1]
            if gap > floor:
                keep = floor / 2
                cuts.append({"kind": "DEAD",
                             "start": round(cues[i - 1][1] + keep, 3),
                             "end": round(start - keep, 3),
                             "why": f"{gap:.2f}s gap"})
        if text.strip() and not FILLER_ONLY.match(text):
            j = i - 1
            while j >= 0 and (FILLER_ONLY.match(cues[j][2])
                              or not cues[j][2].strip()):
                j -= 1
            if j >= 0:
                a1, b1 = _norm(cues[j][2])[:5], _norm(text)[:5]
                if len(a1) >= 3 and a1 == b1:
                    cuts.append({"kind": "REPEAT",
                                 "start": cues[j][0], "end": cues[j][1],
                                 "why": f'restart of "{" ".join(a1)}"'})
    cuts = [c for c in cuts if c["end"] > c["start"]]
    cuts.sort(key=lambda c: c["start"])
    return cuts


def find_chapters(cues):
    """Chapter boundaries: a pause >= CHAPTER_PAUSE where the next cue
    opens a new point. Title = the cue's own first words (quoted)."""
    chapters = [{"index": 0, "start": cues[0][0], "title": "Opening"}] \
        if cues else []
    for i in range(1, len(cues)):
        gap = cues[i][0] - cues[i - 1][1]
        text = cues[i][2].strip()
        prev_done = cues[i - 1][2].strip().endswith((".", "?", "!"))
        if gap >= CHAPTER_PAUSE and (CHAPTER_MARKERS.match(text) or prev_done):
            first_words = " ".join(text.split()[:6])
            chapters.append({"index": len(chapters), "start": round(cues[i][0], 3),
                             "title": f"Starts: \"{first_words}\""})
    return chapters


def _moment_score(text):
    score = 0
    score += 2 * len(CONCRETE.findall(text))
    score += 1 if QUESTION.search(text) else 0
    score += 1 if YOU.search(text) else 0
    score += 1 if STAKE.search(text) else 0
    return score


def find_shorts(cues, duration):
    """Top SHORTS_TOP non-overlapping 30s windows around the best cues."""
    scored = [(i, _moment_score(text)) for i, (_s, _e, text) in enumerate(cues)]
    scored = [(i, s) for i, s in scored if s >= 2]
    scored.sort(key=lambda item: -item[1])
    windows = []
    for i, score in scored:
        start = max(0.0, cues[i][0] - 15.0)
        end = min(duration, start + SHORTS_WINDOW)
        start = max(0.0, end - SHORTS_WINDOW)
        if any(not (end <= w["start"] or start >= w["end"]) for w in windows):
            continue
        windows.append({"start": round(start, 3), "end": round(end, 3),
                        "score": score,
                        "anchor": cues[i][2].strip()[:80]})
        if len(windows) >= SHORTS_TOP:
            break
    windows.sort(key=lambda w: w["start"])
    return windows


def build_cut_list(path, floor=0.45):
    """Full cut list for one transcript file."""
    cues = load(path)
    if not cues:
        raise ValueError("no cues found - is this an srt, vtt or whisper json?")
    duration = cues[-1][1]
    cuts = find_cuts(cues, floor=floor)
    removed = sum(c["end"] - c["start"] for c in cuts)
    return {
        "source": path,
        "duration": round(duration, 3),
        "cues": len(cues),
        "dead_air_floor": floor,
        "cuts": cuts,
        "removed": round(removed, 3),
        "out": round(duration - removed, 3),
        "chapters": find_chapters(cues),
        "shorts": find_shorts(cues, duration),
        "mock": True,
        "note": ("RULE-BASED cut list only — no LLM, no edit applied. "
                 "Apply the cuts in an editor; verify each chapter/shorts "
                 "label against the real footage."),
    }


def show(result):
    print(f"\n  {result['source']}   {result['duration']:.2f}s in, "
          f"{result['cues']} cues, dead-air floor {result['dead_air_floor']}s\n")
    for cut in result["cuts"]:
        print(f"    {cut['kind']:<7} {cut['start']:8.2f} -> {cut['end']:8.2f}   "
              f"{cut['end'] - cut['start']:5.2f}s   {cut['why']}")
    print(f"\n  {len(result['cuts'])} cuts, {result['removed']:.2f}s removed, "
          f"{result['out']:.2f}s out "
          f"({result['removed'] / result['duration'] * 100:.1f}% shorter)\n")
    print("  chapters:")
    for ch in result["chapters"]:
        print(f"    {ch['index']}. {ch['start']:8.2f}s   {ch['title']}")
    print("\n  shorts moments (candidates, 30s windows):")
    for w in result["shorts"]:
        print(f"    {w['start']:8.2f}s -> {w['end']:8.2f}s   score {w['score']}   "
              f"\"{w['anchor']}\"")
    print()


def self_test():
    """Sample transcript in a temp file: DEAD + FILLER + REPEAT + a
    chapter boundary + a Shorts moment must all be found."""
    import tempfile

    sample = """1
00:00:00,000 --> 00:00:03,000
Welcome back. Today we test Nano Banana 2.

2
00:00:03,500 --> 00:00:05,000
Um, uh, basically...

3
00:00:07,500 --> 00:00:10,000
97 percent of channels quit before video 30.

4
00:00:10,500 --> 00:00:13,000
97 percent of channels quit before video 30, here is what the other 3 percent do.

5
00:00:16,000 --> 00:00:19,000
Next, we run all five edits on screen.
"""
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "sample.srt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(sample)
    result = build_cut_list(path)
    kinds = {c["kind"] for c in result["cuts"]}
    checks = [
        ("DEAD cut found", "DEAD" in kinds),
        ("FILLER cut found", "FILLER" in kinds),
        ("REPEAT cut found", "REPEAT" in kinds),
        ("chapter boundary found", len(result["chapters"]) >= 2),
        ("shorts moment found", len(result["shorts"]) >= 1),
        ("out < duration", result["out"] < result["duration"]),
    ]
    bad = [label for label, ok in checks if not ok]
    for label, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    return 1 if bad else 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Transcript-in, cut-list-out (stage 5-edit, MOCK).")
    parser.add_argument("transcript", nargs="?",
                        help="transcript file (.srt, .vtt, whisper .json)")
    parser.add_argument("--floor", type=float, default=0.45,
                        help="dead-air floor in seconds (default 0.45)")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.transcript or not os.path.exists(args.transcript):
        print(__doc__)
        return 1
    try:
        result = build_cut_list(args.transcript, floor=args.floor)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=1, ensure_ascii=False))
    else:
        show(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
