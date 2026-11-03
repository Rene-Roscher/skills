#!/usr/bin/env python3
"""Measure what a listener would otherwise have to judge by ear.

Subcommands:
  voice-to-rest MIX --clip VOICE --at SECONDS [--clip VOICE --at SECONDS ...] [--min-db 4] [--search 0.5]
      For each voice clip, find it in the final mix near the given start time (cross-correlation), fit its gain
      by least squares and report voice energy over everything else in that stretch, in dB. Run it on the
      delivered file, after mastering: ducking, limiting and loudness normalisation all show up here.
  voicing AUDIO --from SECONDS --to SECONDS [--min-fraction 0.10] [--peak 6]
      Share of voiced frames in a stretch, from the cepstral peak in the 80-250 Hz pitch range. A word that came
      out whispered or unvoiced scores near zero; normally spoken words score well above it.

Inputs can be any file ffmpeg decodes (wav, mp3, mp4, mov). Audio is decoded to mono 16 kHz.
Exit codes: 0 every check passes, 1 a check fails, 2 usage or tool error.
Needs Python 3.9+, numpy and ffmpeg on PATH. No network access.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover - reported to the user
    print("numpy is required (pip install numpy)", file=sys.stderr)
    sys.exit(2)

SR = 16000


def load(path: str) -> np.ndarray:
    res = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode != 0 or not res.stdout:
        sys.stderr.write(res.stderr.decode(errors="replace") or f"no audio decoded from {path}\n")
        raise SystemExit(2)
    return np.frombuffer(res.stdout, dtype=np.float32).astype(np.float64)


def xcorr_valid(win: np.ndarray, clip: np.ndarray) -> np.ndarray:
    """Cross-correlation of clip against every full-overlap position in win (FFT, same result as np.correlate valid)."""
    n = len(win) + len(clip) - 1
    size = 1 << (n - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(win, size) * np.conj(np.fft.rfft(clip, size)), size)
    return c[: len(win) - len(clip) + 1]


def voice_to_rest(a: argparse.Namespace) -> int:
    if len(a.clip) != len(a.at):
        print("give one --at per --clip", file=sys.stderr)
        return 2
    mix = load(a.mix)
    worst = None
    for path, at in zip(a.clip, a.at):
        vo = load(path)
        lo = max(0, int((at - a.search) * SR))
        hi = min(len(mix), int((at + a.search) * SR) + len(vo))
        win = mix[lo:hi]
        if len(win) < len(vo) or not np.any(vo):
            print(f"{path}: clip does not fit the mix at {at:.2f}s (or is silent)", file=sys.stderr)
            return 2
        off = lo + int(np.argmax(xcorr_valid(win, vo)))
        seg = mix[off: off + len(vo)]
        g = float(seg @ vo / (vo @ vo))
        rest = seg - g * vo
        er = float(rest @ rest)
        db = 99.0 if er == 0 else 10 * np.log10(float((g * vo) @ (g * vo)) / er)
        worst = db if worst is None else min(worst, db)
        flag = "" if db >= a.min_db else f"  below {a.min_db:+.1f} dB"
        print(f"{path}: found at {off / SR:7.3f}s (asked {at:.3f}s), gain {g:5.3f}, voice-to-rest {db:+6.1f} dB{flag}")
    ok = worst is not None and worst >= a.min_db
    print(("PASS" if ok else "FAIL") + f": lowest voice-to-rest {worst:+.1f} dB, threshold {a.min_db:+.1f} dB")
    return 0 if ok else 1


def voicing(a: argparse.Namespace) -> int:
    x = load(a.audio)
    seg = x[int(a.start * SR): int(a.end * SR)]
    n_fft, hop = 1024, 160
    if len(seg) < n_fft:
        print("stretch is shorter than one analysis frame (64 ms)", file=sys.stderr)
        return 2
    win = np.hanning(n_fft)
    frames = np.lib.stride_tricks.sliding_window_view(seg, n_fft)[::hop] * win
    spec = np.abs(np.fft.rfft(frames, axis=1)) + 1e-9
    ceps = np.fft.irfft(np.log(spec), axis=1)
    q = np.arange(ceps.shape[1]) / SR
    band = (q > 1 / 250) & (q < 1 / 80)
    peak = ceps[:, band].max(axis=1) / (np.median(np.abs(ceps[:, band]), axis=1) + 1e-9)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    loud = rms > rms.max() * 0.05  # ignore silent frames inside the stretch
    voiced = int(((peak > a.peak) & loud).sum())
    total = int(loud.sum())
    frac = voiced / max(1, total)
    ok = frac >= a.min_fraction
    print(f"{a.audio} {a.start:.2f}-{a.end:.2f}s: voiced {voiced}/{total} frames = {frac:.0%} "
          f"(cepstral peak > {a.peak}); {'PASS' if ok else 'FAIL'} at minimum {a.min_fraction:.0%}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("voice-to-rest")
    v.add_argument("mix")
    v.add_argument("--clip", action="append", required=True)
    v.add_argument("--at", action="append", type=float, required=True)
    v.add_argument("--min-db", type=float, default=4.0)
    v.add_argument("--search", type=float, default=0.5, help="seconds searched either side of --at")
    s = sub.add_parser("voicing")
    s.add_argument("audio")
    s.add_argument("--from", dest="start", type=float, required=True)
    s.add_argument("--to", dest="end", type=float, required=True)
    s.add_argument("--min-fraction", type=float, default=0.10)
    s.add_argument("--peak", type=float, default=6.0)
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        print("ffmpeg is required", file=sys.stderr)
        return 2
    return voice_to_rest(a) if a.cmd == "voice-to-rest" else voicing(a)


if __name__ == "__main__":
    sys.exit(main())
