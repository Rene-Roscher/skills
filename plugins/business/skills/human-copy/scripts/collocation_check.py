#!/usr/bin/env python3
"""Compare how often a flagged phrase and its natural alternative occur in the Google Books Ngram corpus.

Usage:
  collocation_check.py [--lang de|en] [--year 2019] [--timeout 15] PHRASE ALTERNATIVE [PHRASE ALTERNATIVE ...]
  collocation_check.py --self-test

Example:
  collocation_check.py --lang de "Entscheidung machen" "Entscheidung treffen"
  -> "Entscheidung machen" 1.38e-08 | "Entscheidung treffen" 1.92e-06 | 1 : 139 (de-2019, 2019)

How to read the ratio (a rule of thumb for this skill, not a published threshold):
  1 : 10 or rarer   the phrase is very likely a calque or an unusual combination; rewrite it
  1 : 3 to 1 : 10   weak; judge by register and context, prefer the alternative in UI and docs
  rarer than 1 : 3  not a calque; both are established, so do not flag it on frequency grounds

Limits: books, not UI text; corpus ends in 2019; at most five words per phrase; German verb-final order
means you compare infinitive forms ("Problem lösen"), not finite clauses. A phrase that is part of its
alternative ("den Link klicken" inside "auf den Link klicken") is counted inside it, so the ratio says nothing.

The network call is optional. Offline, or when the endpoint changes, the script prints "no verdict" and
exits 3; it never guesses. Exit codes: 0 checked, 2 usage error, 3 could not reach or parse the endpoint,
1 failed --self-test. Python 3.8 or later, standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://books.google.com/ngrams/json"
CORPUS = {"de": "de-2019", "en": "en-2019"}
FORBIDDEN = set(",+*/:()[]")  # Ngram query operators and separators


def fetch(url: str, timeout: float) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "collocation-check/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https endpoint)
        return resp.read().decode("utf-8")


def build_url(a: str, b: str, corpus: str, year: int) -> str:
    q = {"content": f"{a},{b}", "corpus": corpus, "year_start": year - 4, "year_end": year, "smoothing": 0}
    return ENDPOINT + "?" + urllib.parse.urlencode(q)


def validate(phrase: str) -> str | None:
    if not phrase.strip():
        return "empty phrase"
    if any(c in FORBIDDEN for c in phrase):
        return f"'{phrase}' contains one of {''.join(sorted(FORBIDDEN))}, which the Ngram query treats as an operator"
    if len(phrase.split()) > 5:
        return f"'{phrase}' has more than five words; the corpus stores at most 5-grams"
    return None


def ratio_text(x: float, y: float) -> str:
    if x == 0 and y == 0:
        return "neither phrase occurs; no verdict"
    if x == 0:
        return "phrase not found, alternative found: rewrite"
    if y == 0:
        return "alternative not found: check the alternative"
    if y >= x:
        return f"1 : {round(y / x)}"
    return f"{round(x / y, 1)} : 1"


def verdict(x: float, y: float) -> str:
    if x == 0 and y > 0:
        return "rewrite"
    if x == 0 or y == 0:
        return "no verdict"
    r = y / x
    if r >= 10:
        return "rewrite"
    if r >= 3:
        return "weak: judge by register"
    return "established: do not flag on frequency"


def check_pair(a: str, b: str, corpus: str, year: int, timeout: float, fetcher=fetch) -> tuple[str, int]:
    for p in (a, b):
        err = validate(p)
        if err:
            return f"usage: {err}", 2
    try:
        raw = fetcher(build_url(a, b, corpus, year), timeout)
        data = json.loads(raw)
        series = {item["ngram"]: item["timeseries"] for item in data}
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        return f'"{a}" | "{b}" | no verdict: endpoint not reachable ({e})', 3
    except (ValueError, KeyError, TypeError) as e:
        return f'"{a}" | "{b}" | no verdict: unexpected response ({e.__class__.__name__})', 3
    x = (series.get(a) or [0.0])[-1]
    y = (series.get(b) or [0.0])[-1]
    note = ""
    if a.lower() in b.lower() or b.lower() in a.lower():
        note = " | one phrase contains the other, so the ratio is meaningless"
    line = f'"{a}" {x:.3g} | "{b}" {y:.3g} | {ratio_text(x, y)} ({corpus}, {year}) | {verdict(x, y)}{note}'
    return line, 0


# --- self-test with a mocked endpoint -------------------------------------------------------------

def _mock(payload):
    def fetcher(url, timeout):
        if isinstance(payload, Exception):
            raise payload
        return payload
    return fetcher


def self_test() -> int:
    fails = []
    ok = json.dumps([
        {"ngram": "Entscheidung machen", "parent": "", "type": "NGRAM", "timeseries": [1.1e-08, 1.38e-08]},
        {"ngram": "Entscheidung treffen", "parent": "", "type": "NGRAM", "timeseries": [1.8e-06, 1.92e-06]},
    ])
    line, code = check_pair("Entscheidung machen", "Entscheidung treffen", "de-2019", 2019, 5, _mock(ok))
    if code != 0 or "1 : 139" not in line or "rewrite" not in line:
        fails.append(f"ratio not computed from the mocked series: {line}")
    est = json.dumps([
        {"ngram": "einmal mehr", "timeseries": [8.89e-06]},
        {"ngram": "wieder einmal", "timeseries": [1.75e-05]},
    ])
    line, code = check_pair("einmal mehr", "wieder einmal", "de-2019", 2019, 5, _mock(est))
    if "established" not in line:
        fails.append(f"1 : 2 must read as established: {line}")
    missing = json.dumps([{"ngram": "will receive an email", "timeseries": [7.16e-09]}])
    line, code = check_pair("will become an email", "will receive an email", "en-2019", 2019, 5, _mock(missing))
    if code != 0 or "phrase not found" not in line:
        fails.append(f"absent phrase must be reported, not crash: {line}")
    line, code = check_pair("a", "b", "en-2019", 2019, 5, _mock(urllib.error.URLError("offline")))
    if code != 3 or "no verdict" not in line:
        fails.append(f"offline must exit 3 with no verdict: {line}")
    line, code = check_pair("a", "b", "en-2019", 2019, 5, _mock("<html>blocked</html>"))
    if code != 3 or "unexpected response" not in line:
        fails.append(f"non-JSON response must exit 3: {line}")
    line, code = check_pair("a, b", "c", "en-2019", 2019, 5, _mock(ok))
    if code != 2:
        fails.append("a comma in a phrase must be a usage error")
    sub = json.dumps([{"ngram": "den Link klicken", "timeseries": [1e-08]},
                      {"ngram": "auf den Link klicken", "timeseries": [1e-08]}])
    line, code = check_pair("den Link klicken", "auf den Link klicken", "de-2019", 2019, 5, _mock(sub))
    if "meaningless" not in line:
        fails.append("substring pair must be marked")
    url = build_url("Problem lösen", "Problem angehen", "de-2019", 2019)
    if "corpus=de-2019" not in url or "smoothing=0" not in url or "year_end=2019" not in url:
        fails.append(f"query URL malformed: {url}")
    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("collocation_check self-test: ok (mocked endpoint: ratio, established, absent, offline, bad JSON, "
          "usage, substring, URL)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="collocation_check.py",
        description="Compare a flagged phrase with its alternative in the Google Books Ngram corpus (de-2019 or "
                    "en-2019) and print the frequency ratio. Network optional; offline prints no verdict.",
    )
    ap.add_argument("phrases", nargs="*", help="pairs: PHRASE ALTERNATIVE [PHRASE ALTERNATIVE ...]")
    ap.add_argument("--lang", choices=sorted(CORPUS), default="en", help="corpus language (default: en)")
    ap.add_argument("--year", type=int, default=2019, help="year to read, 1800 to 2019 (default: 2019)")
    ap.add_argument("--timeout", type=float, default=15.0, help="seconds per request (default: 15)")
    ap.add_argument("--self-test", action="store_true", help="run against a mocked endpoint and exit")
    args = ap.parse_args(argv)

    if args.self_test:
        return self_test()
    if not args.phrases or len(args.phrases) % 2:
        ap.print_usage(sys.stderr)
        print("collocation_check.py: give phrases in pairs: PHRASE ALTERNATIVE", file=sys.stderr)
        return 2
    if not 1804 <= args.year <= 2019:
        print("collocation_check.py: --year must be between 1804 and 2019", file=sys.stderr)
        return 2
    worst = 0
    for i in range(0, len(args.phrases), 2):
        line, code = check_pair(args.phrases[i], args.phrases[i + 1], CORPUS[args.lang], args.year, args.timeout)
        print(line, file=sys.stderr if code else sys.stdout)
        worst = max(worst, code)
        if code == 3:
            break  # the endpoint is down; do not hammer it
    return worst


if __name__ == "__main__":
    sys.exit(main())
