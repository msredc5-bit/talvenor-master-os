#!/usr/bin/env python3
"""stills_render.py — stills + Ken Burns MOCK render (stage 4-video, MOCK).

CPU-only FFmpeg path (libx264, no GPU flags): takes still images +
per-still durations and renders a slow zoom/pan (Ken Burns) video.
This is a PLACEHOLDER render so the pipeline runs end-to-end — it is
NOT a publishable video and NOT true motion:

  - Boss's standard is REAL footage only (pipeline.md stage 4-video,
    BLOCKED). Stills + Ken Burns motion are not real motion.
  - Every output is labelled MOCK in THREE places: the filename
    ("mock-..." prefix), a burned-in "MOCK PLACEHOLDER — NOT REAL
    FOOTAGE" caption on every frame, and file metadata.
  - No network, no LLM, no upload, no publish. CPU only.

    python3 tools/stills_render.py --images a.jpg b.jpg --durations 3 3 \\
        --out renders/mock-week1.mp4
    python3 tools/stills_render.py --plan plan.json --out renders/mock-week1.mp4
    python3 tools/stills_render.py --self-test   # temp stills + render

Plan JSON: {"width": 1280, "height": 720, "fps": 25, "stills":
[{"image": "a.jpg", "duration": 3, "zoom": "in"|"out"}, ...]}
Each still needs duration > 0. Missing image / missing ffmpeg -> a
clear error, never a fake output file.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

MOCK_LABEL = "MOCK PLACEHOLDER - NOT REAL FOOTAGE"
MOCK_PREFIX = "mock-"
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 25
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _find_font():
    for path in FONT_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


def _zoompan_filter(zoom, frames, width, height, fps):
    """Ken Burns zoompan for one still. zoom 'in' starts wide and pushes
    in; 'out' starts tight and pulls out."""
    if zoom == "out":
        zoom_expr = "if(eq(on\\,1)\\,1.5\\,max(zoom-0.001\\,1.0))"
    else:
        zoom_expr = "min(zoom+0.001\\,1.5)"
    return (
        f"scale={width * 2}:{height * 2},"
        f"zoompan=z='{zoom_expr}':d={frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"s={width}x{height}:fps={fps},setsar=1"
    )


def render(stills, out_path, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT,
           fps=DEFAULT_FPS):
    """Render the mock video. Returns the output path. Raises
    RuntimeError / FileNotFoundError on any problem — never writes a
    fake file."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError(
            "ffmpeg not found on this machine — no mock render possible. "
            "Install ffmpeg (CPU-only) and retry; nothing was rendered.")
    if not stills:
        raise ValueError("no stills given — nothing to render")
    for still in stills:
        if not os.path.isfile(still["image"]):
            raise FileNotFoundError(f"still image not found: {still['image']}")
        if float(still.get("duration", 0)) <= 0:
            raise ValueError(
                f"still {still['image']}: duration must be > 0")
    if os.path.basename(out_path).startswith(MOCK_PREFIX) is False:
        out_path = os.path.join(os.path.dirname(out_path),
                                MOCK_PREFIX + os.path.basename(out_path))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    tmp = tempfile.mkdtemp(prefix="stills_render_")
    try:
        inputs = []
        filters = []
        for i, still in enumerate(stills):
            frames = max(1, int(round(float(still["duration"]) * fps)))
            # Single image frame as input (NOT -loop): zoompan expands
            # this ONE frame into `frames` output frames. A looped input
            # would multiply every input frame by d (200s instead of 4s).
            inputs += ["-i", still["image"]]
            filters.append(
                f"[{i}:v]{_zoompan_filter(still.get('zoom', 'in'), frames, width, height, fps)}[v{i}]")
        concat_inputs = "".join(f"[v{i}]" for i in range(len(stills)))
        filters.append(f"{concat_inputs}concat=n={len(stills)}:v=1:a=0[concat]")
        font = _find_font()
        if font:
            filters.append(
                "[concat]drawtext=fontfile={font}:text='{label}':"
                "fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6:"
                "x=(w-text_w)/2:y=h-60[vout]".format(font=font, label=MOCK_LABEL))
            last = "[vout]"
        else:
            print("warning: no DejaVu font found — frame caption skipped; "
                  "filename + metadata still label this MOCK.",
                  file=sys.stderr)
            last = "[concat]"
        cmd = ([ffmpeg, "-y"] + inputs +
               ["-filter_complex", ";".join(filters),
                "-map", last, "-c:v", "libx264", "-preset", "veryfast",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-metadata", f"title={MOCK_LABEL}",
                "-metadata", f"comment={MOCK_LABEL} — stills + Ken Burns, "
                            "not real footage, not publishable",
                out_path])
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(
                "ffmpeg failed (no output written): "
                + proc.stderr.strip()[-500:])
        if not os.path.isfile(out_path):
            raise RuntimeError("ffmpeg exited 0 but wrote no file")
        return out_path
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _load_plan(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("stills"), list):
        raise ValueError(f"{path}: expected {{\"stills\": [...]}}")
    return data


def self_test():
    """Render a 2-still mock video from ffmpeg-generated solid stills,
    all in a temp dir. Verifies the file exists, is labelled mock, and
    lasts ~4s."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("SKIP — ffmpeg not installed on this machine")
        return 0
    tmp = tempfile.mkdtemp(prefix="stills_selftest_")
    try:
        stills = []
        for i, color in enumerate(("navy", "teal")):
            path = os.path.join(tmp, f"still{i}.png")
            proc = subprocess.run(
                [ffmpeg, "-y", "-f", "lavfi", "-i",
                 f"color=c={color}:s=1280x720:d=1",
                 "-frames:v", "1", path],
                capture_output=True, text=True, timeout=60)
            assert proc.returncode == 0, proc.stderr[-300:]
            stills.append({"image": path, "duration": 2,
                           "zoom": "in" if i == 0 else "out"})
        out = os.path.join(tmp, "week1.mp4")
        rendered = render(stills, out)
        assert os.path.basename(rendered).startswith(MOCK_PREFIX), rendered
        assert os.path.getsize(rendered) > 1000, "output suspiciously small"
        probe = subprocess.run(
            [shutil.which("ffprobe") or "ffprobe", "-v", "error",
             "-show_entries", "format=duration", "-of", "csv=p=0", rendered],
            capture_output=True, text=True, timeout=60)
        duration = float(probe.stdout.strip())
        assert 3.5 <= duration <= 4.5, f"duration {duration}"
        print(f"  [PASS] mock render: {os.path.basename(rendered)}, "
              f"{duration:.1f}s, {os.path.getsize(rendered)} bytes")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Stills + Ken Burns MOCK render (stage 4, NOT publishable).")
    parser.add_argument("--images", nargs="+", help="still image files")
    parser.add_argument("--durations", nargs="+", type=float,
                        help="seconds per still (same count as --images)")
    parser.add_argument("--plan", help="plan JSON file")
    parser.add_argument("--out", help="output video path (mock- prefix added)")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.out:
        print("error: --out is required", file=sys.stderr)
        return 1
    if args.plan:
        try:
            plan = _load_plan(args.plan)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        stills = plan["stills"]
        width = plan.get("width", args.width)
        height = plan.get("height", args.height)
        fps = plan.get("fps", args.fps)
    elif args.images:
        if not args.durations or len(args.durations) != len(args.images):
            print("error: --durations must match --images one-to-one",
                  file=sys.stderr)
            return 1
        stills = [{"image": img, "duration": dur, "zoom": "in"}
                  for img, dur in zip(args.images, args.durations)]
        width, height, fps = args.width, args.height, args.fps
    else:
        print("error: give --plan or --images + --durations", file=sys.stderr)
        return 1
    try:
        rendered = render(stills, args.out, width=width, height=height, fps=fps)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"MOCK render written: {rendered}")
    print("MOCK PLACEHOLDER — NOT REAL FOOTAGE, not publishable. "
          "Boss's REAL-footage-only standard is unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
