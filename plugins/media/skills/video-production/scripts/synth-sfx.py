#!/usr/bin/env python3
"""Synthesise sound effects instead of using samples or platform sounds: no licence questions, and every
parameter can be changed when a reviewer says it sounds wrong.

Subcommands (each writes a 48 kHz 16-bit stereo WAV and prints its checks):
  buzz OUT.wav [--pulses 2] [--motor-hz 150]
      A phone vibrating on a wooden desk. An eccentric-mass motor spins up, its case knocks the desk once per
      revolution, and each knock rings the desk's resonances (modal filters). No saturation or clipping: a
      clipped or tanh-driven buzz reads as a broken speaker.
  chime OUT.wav [--notes 987.77,1318.51]
      A short notification chime from FM bells, one note after the other. Your own motif, not a platform tone.
  bed OUT.wav [--seconds 12] [--resolve-at 6]
      A low, tense pad that resolves into a major chord at --resolve-at, for the turn of a story.

Checks printed for every file: peak in dBFS (must stay below 0), DC offset, and for buzz the share of energy
between 100 and 400 Hz (the body of a desk vibration; a thin or hissy buzz scores low).
Exit codes: 0 written and checks pass, 1 a check fails, 2 usage error.
Needs Python 3.9+ and numpy. No network access.
"""

from __future__ import annotations

import argparse
import sys
import wave

try:
    import numpy as np
except ImportError:  # pragma: no cover - reported to the user
    print("numpy is required (pip install numpy)", file=sys.stderr)
    sys.exit(2)

SR = 48000


def t_axis(seconds: float) -> np.ndarray:
    return np.arange(int(round(seconds * SR))) / SR


def resonator(x: np.ndarray, fc: float, q: float) -> np.ndarray:
    """Two-pole resonator at fc with quality q: one mode of a vibrating body."""
    w = 2 * np.pi * fc / SR
    r = np.exp(-w / (2 * q))
    b0, a1, a2 = 1 - r, -2 * r * np.cos(w), r * r
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    for i, v in enumerate(x):
        y0 = b0 * v - a1 * y1 - a2 * y2
        y[i] = y0
        y2, y1 = y1, y0
    return y


def fft_band(x: np.ndarray, lo: float | None, hi: float | None) -> np.ndarray:
    """Zero-phase band limit with soft edges (raised-cosine over one octave)."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= np.clip(np.log2(np.maximum(f, 1e-6) / (lo / 2)), 0, 1) ** 2
    if hi:
        g *= np.clip(np.log2((2 * hi) / np.maximum(f, 1e-6)), 0, 1) ** 2
    return np.fft.irfft(spec * g, len(x))


def room(x: np.ndarray, seconds: float, wet: float, seed: int = 5) -> np.ndarray:
    """Small synthetic room: exponentially decaying filtered noise as impulse response."""
    rng = np.random.default_rng(seed)
    t = t_axis(seconds)
    ir = fft_band(rng.standard_normal(len(t)), None, 6000) * np.exp(-6.9 * t / seconds) * np.minimum(1, t / 0.01)
    ir /= np.sqrt((ir ** 2).sum())
    n = len(x) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    tail = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n]
    out = tail * wet
    out[: len(x)] += x
    return out


def fm_bell(f: float, dur: float, ratio: float = 2.0, index: float = 1.3, decay: float = 0.4) -> np.ndarray:
    t = t_axis(dur)
    i = index * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * f * t + i * np.sin(2 * np.pi * f * ratio * t))
    return y * (1 - np.exp(-t / 0.0015)) * np.exp(-t / decay)


def buzz(pulses: int, motor_hz: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    dur, gap = 0.4, 0.15
    out = np.zeros(int((pulses * (dur + gap) + 0.4) * SR))
    for k in range(pulses):
        t = t_axis(dur)
        spin = np.minimum(1, t / 0.06)                                   # the motor spins up
        f = (motor_hz + 6 * np.sin(2 * np.pi * 3.1 * t)) * (0.75 + 0.25 * spin)
        ph = 2 * np.pi * np.cumsum(f) / SR
        knock = np.maximum(0, np.sin(ph)) ** 6                          # one knock per revolution
        exc = (knock - knock.mean()) * (1 + 0.15 * rng.standard_normal(len(t)))
        body = (resonator(exc, 210, 6) + 0.7 * resonator(exc, 330, 7)    # desk modes
                + 0.25 * resonator(exc, 1150, 14) + 0.08 * resonator(exc, 2400, 18))  # case rattle, damped
        hum = 0.25 * np.sin(ph) + 0.08 * np.sin(2 * ph)
        env = np.minimum(1, t / 0.025) * np.minimum(1, (dur - t) / 0.05)
        p = (body * 6 + hum) * env * spin
        i = int(k * (dur + gap) * SR)
        out[i: i + len(p)] += p
    out = fft_band(out, 70, 4000)
    return room(out, 0.5, 0.1)


def chime(notes: list[float]) -> np.ndarray:
    out = np.zeros(int((0.09 * len(notes) + 1.0) * SR))
    for k, f in enumerate(notes):
        b = fm_bell(f, 0.9, decay=0.35 + 0.1 * k)
        i = int(k * 0.09 * SR)
        out[i: i + len(b)] += b * (0.8 if k == 0 else 1.0)
    return room(out, 0.9, 0.2)


def pad(freqs: list[float], dur: float, harmonics: int, attack: float, release: float, seed: int) -> np.ndarray:
    """Detuned band-limited saws; brightness set by how many harmonics are kept (no filter needed)."""
    rng = np.random.default_rng(seed)
    t = t_axis(dur)
    y = np.zeros_like(t)
    for f in freqs:
        for d in (-0.005, 0.0, 0.005):
            ph0 = rng.uniform(0, 2 * np.pi)
            for k in range(1, harmonics + 1):
                if f * k > 8000:
                    break
                y += np.sin(2 * np.pi * f * (1 + d) * k * t + k * ph0) / k ** 1.3
    env = np.minimum(1, t / attack) * np.clip((dur - t) / release, 0, 1)
    return y * env * (1 + 0.06 * np.sin(2 * np.pi * 0.35 * t))


def bed(seconds: float, resolve_at: float) -> np.ndarray:
    tense_f = [82.41, 123.47, 185.0]              # a bare fifth plus a ninth: open, unresolved
    resolved_f = [164.81, 207.65, 246.94, 329.63]  # major triad an octave up: the release
    out = np.zeros(int(seconds * SR))
    tense = pad(tense_f, resolve_at + 0.6, 6, 0.8, 0.8, 1)
    t = t_axis(resolve_at)
    pulse = np.sin(2 * np.pi * 55 * t) * np.exp(-((t % 0.5) / 0.08)) * 0.4  # a slow heartbeat under the tension
    out[: len(tense)] += tense
    out[: len(pulse)] += fft_band(pulse, None, 300)
    res = pad(resolved_f, seconds - resolve_at, 14, 0.6, 2.0, 2)
    i = int(resolve_at * SR)
    out[i: i + len(res)] += res[: len(out) - i] * 0.9
    return room(out, 2.4, 0.25)


def write(path: str, x: np.ndarray, peak_db: float) -> np.ndarray:
    x = x - x.mean()
    x = x / (np.abs(x).max() + 1e-12) * 10 ** (peak_db / 20)
    st = np.stack([x, x], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    return x


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buzz")
    b.add_argument("out")
    b.add_argument("--pulses", type=int, default=2)
    b.add_argument("--motor-hz", type=float, default=150.0)
    b.add_argument("--seed", type=int, default=0)
    c = sub.add_parser("chime")
    c.add_argument("out")
    c.add_argument("--notes", default="987.77,1318.51")
    d = sub.add_parser("bed")
    d.add_argument("out")
    d.add_argument("--seconds", type=float, default=12.0)
    d.add_argument("--resolve-at", type=float, default=6.0)
    a = ap.parse_args()

    if a.cmd == "buzz":
        x = write(a.out, buzz(a.pulses, a.motor_hz, a.seed), -3.0)
    elif a.cmd == "chime":
        x = write(a.out, chime([float(v) for v in a.notes.split(",")]), -3.0)
    else:
        if not 0 < a.resolve_at < a.seconds:
            print("--resolve-at must lie inside --seconds", file=sys.stderr)
            return 2
        x = write(a.out, bed(a.seconds, a.resolve_at), -6.0)

    peak = 20 * np.log10(np.abs(x).max() + 1e-12)
    dc = float(x.mean())
    ok = peak < 0 and abs(dc) < 1e-3
    line = f"{a.out}: {len(x) / SR:.2f}s, peak {peak:.1f} dBFS, DC {dc:+.5f}"
    if a.cmd == "buzz":
        spec = np.abs(np.fft.rfft(x)) ** 2
        f = np.fft.rfftfreq(len(x), 1 / SR)
        share = spec[(f >= 100) & (f <= 400)].sum() / spec.sum()
        ok = ok and share >= 0.5
        line += f", energy 100-400 Hz {share:.0%} (want at least 50%)"
    print(line + ("  PASS" if ok else "  FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
