#!/usr/bin/env python3
"""Compare browser measurements with fixed thresholds.

Subcommands:
  contrast FG BG [--large | --non-text]   WCAG 2.2 contrast ratio of two colours
  check FILE [--require KINDS]            check a measurement JSON file ("-" reads stdin)
  self-test                               run the built-in test vectors

Thresholds (WCAG 2.2, https://www.w3.org/TR/WCAG22/):
  text contrast 4.5:1 (1.4.3), large-scale text and non-text UI 3:1 (1.4.3, 1.4.11),
  pointer targets 24 x 24 CSS px unless an exception applies (2.5.8).
Overflow and fit use a tolerance of 1 CSS px for subpixel rounding.

Exit codes: 0 all checks pass, 1 a check fails or cannot be decided, 2 usage or input error.
Python standard library only. No network access.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys

TEXT_MIN = 4.5
LARGE_MIN = 3.0
TARGET_MIN = 24.0
TOLERANCE_PX = 1.0
KINDS = ("overflow", "contrast", "targets", "fit")


class InputError(Exception):
    pass


def parse_colour(text: str) -> tuple[float, float, float, float]:
    """Return (r, g, b, a) with r, g, b in 0..255 and a in 0..1.

    Accepts hex (#rgb, #rgba, #rrggbb, #rrggbbaa) and rgb()/rgba() in comma or space syntax, which is how
    browsers serialize sRGB colours from getComputedStyle. Other colour spaces (oklch, lab, color()) must be
    normalized first, for example through a canvas readback in the browser.
    """
    s = text.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,8})", s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            raise InputError(f"bad hex colour: {text!r}")
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return float(r), float(g), float(b), a
    m = re.fullmatch(r"rgba?\((.*)\)", s)
    if not m:
        raise InputError(f"unsupported colour {text!r}: normalize to rgb()/rgba() first (see the measurement reference)")
    inner = m.group(1).strip()
    alpha = "1"
    if "/" in inner:
        inner, alpha = (p.strip() for p in inner.split("/", 1))
    parts = [p for p in re.split(r"[\s,]+", inner) if p]
    if len(parts) == 4:
        parts, alpha = parts[:3], parts[3]
    if len(parts) != 3:
        raise InputError(f"bad rgb colour: {text!r}")

    def channel(p: str) -> float:
        v = float(p[:-1]) * 2.55 if p.endswith("%") else float(p)
        return min(255.0, max(0.0, v))

    def alpha_value(p: str) -> float:
        v = float(p[:-1]) / 100 if p.endswith("%") else float(p)
        return min(1.0, max(0.0, v))

    try:
        r, g, b = (channel(p) for p in parts)
        a = alpha_value(alpha)
    except ValueError as e:
        raise InputError(f"bad rgb colour: {text!r}") from e
    return r, g, b, a


def composite(fg: tuple[float, float, float, float], bg: tuple[float, float, float, float]) -> tuple[float, float, float]:
    if bg[3] < 1.0:
        raise InputError("background is not opaque: composite the background layers first")
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))  # type: ignore[return-value]


def luminance(rgb: tuple[float, float, float]) -> float:
    def lin(c: float) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (lin(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg_text: str, bg_text: str) -> float:
    bg = parse_colour(bg_text)
    fg = composite(parse_colour(fg_text), bg)
    l1, l2 = luminance(fg), luminance(bg[:3])
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def shown(ratio: float) -> str:
    # Truncate, never round up: 4.497 must not print as 4.50.
    return f"{math.floor(ratio * 100) / 100:.2f}:1"


def check_contrast(item: dict) -> tuple[bool | None, str]:
    need = LARGE_MIN if item.get("large") or item.get("nonText") else TEXT_MIN
    if item.get("uncertain"):
        return None, f"cannot decide ({item['uncertain']}); take a pixel sample from the element screenshot"
    ratio = contrast_ratio(str(item["fg"]), str(item["bg"]))
    return ratio >= need, f"{shown(ratio)} (needs {need}:1)"


def check_overflow(item: dict) -> tuple[bool | None, str]:
    over = float(item["scrollWidth"]) - float(item["clientWidth"])
    clipped = float(item.get("clippedPx", 0))
    worst = max(over, clipped)
    return worst <= TOLERANCE_PX, f"overflow {worst:.0f}px (scroll {over:.0f}px, clipped {clipped:.0f}px; limit {TOLERANCE_PX:.0f}px)"


def check_target(item: dict) -> tuple[bool | None, str]:
    w, h = float(item["width"]), float(item["height"])
    size = f"{w:.1f}x{h:.1f}px (needs {TARGET_MIN:.0f}x{TARGET_MIN:.0f})"
    if w >= TARGET_MIN and h >= TARGET_MIN:
        return True, size
    if item.get("exception"):
        return True, f"{size}, exception: {item['exception']}"
    return False, size


def check_fit(item: dict, viewport: dict) -> tuple[bool | None, str]:
    limit = float(item.get("limit", viewport.get("height", 0)))
    if limit <= 0:
        raise InputError("fit item needs 'limit' or a viewport height")
    bottom = float(item["bottom"])
    return bottom <= limit + TOLERANCE_PX, f"bottom {bottom:.0f}px (limit {limit:.0f}px)"


def check_file(data, require: list[str]) -> int:
    pages = data if isinstance(data, list) else [data]
    if not pages:
        raise InputError("no measurements in input")
    failed = undecided = total = 0
    for page in pages:
        if not isinstance(page, dict):
            raise InputError("each measurement set must be a JSON object")
        vp = page.get("viewport") or {}
        where = f"{page.get('page', '?')} @{vp.get('width', '?')}x{vp.get('height', '?')}"
        for kind in KINDS:
            if kind not in page and kind not in require:
                continue
            items = page.get(kind) or []
            if not items:
                print(f"FAIL {kind} {where}: no element matched, so the check proves nothing")
                failed += 1
                continue
            for item in items:
                total += 1
                try:
                    if kind == "contrast":
                        ok, msg = check_contrast(item)
                    elif kind == "overflow":
                        ok, msg = check_overflow(item)
                    elif kind == "targets":
                        ok, msg = check_target(item)
                    else:
                        ok, msg = check_fit(item, vp)
                except (KeyError, TypeError, ValueError) as e:
                    raise InputError(f"{kind} item {item!r}: {e}") from e
                label = "PASS" if ok else ("UNDECIDED" if ok is None else "FAIL")
                failed += ok is False
                undecided += ok is None
                print(f"{label} {kind} {where} {item.get('selector', '?')}: {msg}")
    if total == 0 and failed == 0:
        raise InputError("no measurement items in input")
    print(f"{total} checked, {failed} failed, {undecided} undecided")
    return 1 if failed or undecided else 0


def self_test() -> int:
    cases = [
        (("#000000", "#fff"), 21.0),
        (("#fff", "#fff"), 1.0),
        (("#767676", "#ffffff"), 4.54),
        (("#777777", "#ffffff"), 4.47),
        (("rgb(118, 118, 118)", "rgb(255 255 255)"), 4.54),
        (("rgba(0, 0, 0, 0.5)", "#ffffff"), 3.97),
        (("rgb(0 0 0 / 50%)", "#fff"), 3.97),
    ]
    bad = 0
    for (fg, bg), want in cases:
        got = math.floor(contrast_ratio(fg, bg) * 100) / 100
        ok = abs(got - want) < 0.005
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} contrast {fg} on {bg} = {got:.2f} (expected {want:.2f})")
    checks = [
        (check_overflow({"scrollWidth": 1201, "clientWidth": 1200})[0], True),
        (check_overflow({"scrollWidth": 1200, "clientWidth": 1200, "clippedPx": 95})[0], False),
        (check_target({"width": 24, "height": 23.5})[0], False),
        (check_target({"width": 20, "height": 20, "exception": "inline link in a sentence"})[0], True),
        (check_fit({"bottom": 690}, {"height": 700})[0], True),
        (check_fit({"bottom": 760}, {"height": 700})[0], False),
        (check_contrast({"fg": "#6b7280", "bg": "#1f2937"})[0], False),
        (check_contrast({"fg": "#6b7280", "bg": "#1f2937", "large": True})[0], True),
        (check_contrast({"fg": "#000000", "bg": "#fff", "uncertain": "background image"})[0], None),
    ]
    for i, (got, want) in enumerate(checks, 1):
        ok = got is want
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} threshold case {i}: {got} (expected {want})")
    for colour in ("oklch(0.5 0.1 200)", "rgb(1, 2)", "#abcde"):
        try:
            parse_colour(colour)
            print(f"FAIL {colour!r} was accepted")
            bad += 1
        except InputError:
            print(f"ok   {colour!r} rejected")
    print("self-test passed" if not bad else f"self-test: {bad} failure(s)")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="measure-check.py", description=__doc__.split("\n\n")[0],
                                 epilog=__doc__.split("\n\n", 1)[1], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("contrast", help="contrast ratio of a foreground and an opaque background colour")
    c.add_argument("fg")
    c.add_argument("bg")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--large", action="store_true", help="large-scale text (3:1)")
    g.add_argument("--non-text", action="store_true", help="UI component or graphical object (3:1)")
    k = sub.add_parser("check", help="check a measurement JSON file against the thresholds")
    k.add_argument("file", help="path to the JSON file, or - for stdin")
    k.add_argument("--require", default="", help="comma-separated kinds that must be present and non-empty: "
                   + ", ".join(KINDS))
    sub.add_parser("self-test", help="run the built-in test vectors")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "self-test":
            return self_test()
        if args.cmd == "contrast":
            ok, msg = check_contrast({"fg": args.fg, "bg": args.bg, "large": args.large, "nonText": args.non_text})
            print(f"{'PASS' if ok else 'FAIL'} {msg}")
            return 0 if ok else 1
        require = [r.strip() for r in args.require.split(",") if r.strip()]
        unknown = [r for r in require if r not in KINDS]
        if unknown:
            raise InputError(f"unknown kind(s) in --require: {', '.join(unknown)}")
        fh = sys.stdin if args.file == "-" else open(args.file, encoding="utf-8")
        with fh:
            data = json.load(fh)
        return check_file(data, require)
    except (InputError, OSError, json.JSONDecodeError) as e:
        print(f"measure-check.py: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
