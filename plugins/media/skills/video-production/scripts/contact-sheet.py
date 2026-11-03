#!/usr/bin/env python3
"""Contact sheet or frame strip from a rendered video, with the safe zone drawn on every tile.

Each tile is one decoded frame of the video file (not a still from the editor), labelled with its frame number
and time. A rectangle marks the safe zone in source pixels, so text and UI that cross it are visible at a
glance. The script also reports the mean luma of each sampled frame and flags near-black ones: frame 0 is the
platform's default cover, and a black first frame is a blank thumbnail.

Usage:
  contact-sheet.py VIDEO OUT.png --times 0,1.5,3.2       explicit times in seconds
  contact-sheet.py VIDEO OUT.png --count 14              evenly spaced, first frame included (delivery strip)
Options:
  --cols N           tiles per row (default 4)
  --tile-width PX    width of one tile (default 360)
  --safe X0,Y0,X1,Y1 safe zone in source pixels, drawn in red (default: none)
  --strict           exit 1 when the first sampled frame is near-black or a time lies outside the video
Exit codes: 0 written, 1 a strict check failed, 2 usage or tool error.
Python standard library plus ffmpeg and ffprobe on PATH. No network access.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BLACK_LUMA = 20  # mean 8-bit luma at or below this counts as near-black


def run(args: list[str], capture: bool = False) -> bytes:
    res = subprocess.run(args, stdout=subprocess.PIPE if capture else subprocess.DEVNULL, stderr=subprocess.PIPE)
    if res.returncode != 0:
        sys.stderr.write(res.stderr.decode(errors="replace"))
        raise SystemExit(2)
    return res.stdout


def probe(video: str) -> tuple[int, int, float, float]:
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height,r_frame_rate:format=duration", "-of", "json", video], capture=True)
    d = json.loads(out)
    s = d["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    return int(s["width"]), int(s["height"]), num / den, float(d["format"]["duration"])


def mean_luma(video: str, t: float) -> float | None:
    raw = run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
               "-vf", "scale=32:32,format=gray", "-f", "rawvideo", "-"], capture=True)
    return sum(raw) / len(raw) if raw else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("out")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--times")
    g.add_argument("--count", type=int)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--tile-width", type=int, default=360)
    ap.add_argument("--safe")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"{tool} is required", file=sys.stderr)
            return 2
    if not Path(a.video).is_file():
        print(f"video not found: {a.video}", file=sys.stderr)
        return 2

    w, h, fps, dur = probe(a.video)
    last = max(0.0, dur - 3.0 / fps)  # the container duration can run past the last decodable frame
    if a.times:
        times = [float(x) for x in a.times.split(",") if x.strip()]
    else:
        n = max(1, a.count)
        times = [0.0] if n == 1 else [round(last * i / (n - 1), 3) for i in range(n)]
    outside = [t for t in times if t < 0 or t > dur]

    box = ""
    if a.safe:
        x0, y0, x1, y1 = (int(v) for v in a.safe.split(","))
        if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
            print(f"safe zone {a.safe} does not fit a {w}x{h} frame", file=sys.stderr)
            return 2
        thick = max(2, w // 270)
        box = f"drawbox=x={x0}:y={y0}:w={x1 - x0}:h={y1 - y0}:color=red@0.9:t={thick},"

    tw = a.tile_width
    fsize = max(12, tw // 16)
    report = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(times):
            tc = min(max(t, 0.0), last)
            label = Path(tmp) / f"label{i:03d}.txt"
            label.write_text(f"f{round(tc * fps)}  {tc:.2f}s")
            vf = (f"{box}scale={tw}:-2,"
                  f"drawtext=textfile={label}:x=8:y=8:fontsize={fsize}:fontcolor=yellow:box=1:boxcolor=black@0.6:boxborderw=4")
            run(["ffmpeg", "-v", "error", "-y", "-ss", f"{tc:.3f}", "-i", a.video, "-frames:v", "1", "-vf", vf,
                 str(Path(tmp) / f"tile{i:03d}.png")])
            luma = mean_luma(a.video, tc)
            if luma is None or not (Path(tmp) / f"tile{i:03d}.png").exists():
                print(f"no frame decoded at {tc:.3f}s", file=sys.stderr)
                return 2
            report.append((t, round(tc * fps), luma))
        cols = max(1, min(a.cols, len(times)))
        rows = (len(times) + cols - 1) // cols
        run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", str(Path(tmp) / "tile%03d.png"),
             "-vf", f"tile={cols}x{rows}:padding=6:margin=6:color=0x202020", "-frames:v", "1", a.out])

    print(f"{a.out}: {len(times)} frames from {w}x{h} @ {fps:.3f} fps, {dur:.2f}s")
    failed = False
    for t, f, luma in report:
        flag = "  near-black" if luma <= BLACK_LUMA else ""
        print(f"  t={t:7.3f}s  f{f:<6d} mean luma {luma:5.1f}{flag}")
    if report and report[0][0] == 0 and report[0][2] <= BLACK_LUMA:
        print("first frame is near-black: the default cover will be blank")
        failed = True
    if outside:
        print(f"times outside the video (0..{dur:.2f}s): {outside}")
        failed = True
    return 1 if (failed and a.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
