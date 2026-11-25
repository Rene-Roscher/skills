#!/usr/bin/env python3
"""Measure how long comparable features took in this repository, from its commit history.

Usage:
  cycle_time.py --scope NAME [--scope NAME ...] [--repo DIR] [--since WHEN]
  cycle_time.py --grep REGEX [--repo DIR] [--since WHEN]
  cycle_time.py --path DIR [--repo DIR] [--since WHEN]
  cycle_time.py --all-scopes [--min-commits N] [--repo DIR] [--since WHEN]
  cycle_time.py ... --burst-gap DAYS
  cycle_time.py --self-test

A feature is the set of commits selected by a Conventional Commits scope ("feat(billing): ..."),
by a regular expression on the subject, or by a path. For each one the script prints:

  commits        number of commits
  first, last    author date of the first and the last commit
  calendar days  last minus first, both days included
  active days    days with at least one commit
  longest gap    longest run of days without a commit inside the span

A scope that names a product area ("billing") spans the whole project and is not one feature.
Isolate the feature with --grep, --path or --since, or pass --burst-gap DAYS: commits of one
selection that are separated by more than DAYS idle days are reported as separate bursts
("billing#1", "billing#2"), and a burst is the closer match for one piece of work.

What the numbers mean: calendar days is elapsed time and includes every wait. Active days is the
closest thing to days of attention that history holds. Neither is hours of work, and one commit
day can hold ten minutes or ten hours. Use the range across several comparable features, never
one feature, and say which features you compared.

Exit code 0 with results, 1 when nothing matched, 2 on a usage or git error.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import statistics
import subprocess
import sys
import tempfile

SCOPE = re.compile(r"^[a-z]+\(([^)]+)\)!?:")


def git_log(repo: str, since: str, path: str | None) -> list[tuple[dt.date, str]]:
    cmd = ["git", "-C", repo, "log", "--no-merges", "--date=short", "--pretty=%ad%x09%s"]
    if since:
        cmd.append("--since=" + since)
    if path:
        cmd += ["--", path]
    try:
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        print("git log failed: " + detail.strip(), file=sys.stderr)
        raise SystemExit(2)
    rows = []
    for line in out.splitlines():
        day, _, subject = line.partition("\t")
        try:
            rows.append((dt.date.fromisoformat(day), subject))
        except ValueError:
            continue
    return rows


def measure(days: list[dt.date]) -> dict:
    uniq = sorted(set(days))
    gaps = [(b - a).days - 1 for a, b in zip(uniq, uniq[1:])]
    return {
        "commits": len(days),
        "first": uniq[0],
        "last": uniq[-1],
        "calendar": (uniq[-1] - uniq[0]).days + 1,
        "active": len(uniq),
        "gap": max(gaps) if gaps else 0,
    }


def bursts(days: list[dt.date], gap: int) -> list[list[dt.date]]:
    out: list[list[dt.date]] = []
    for day in sorted(days):
        if out and (day - out[-1][-1]).days - 1 <= gap:
            out[-1].append(day)
        else:
            out.append([day])
    return out


def collect(rows, scopes, grep, all_scopes, min_commits, label, burst_gap=None) -> dict[str, dict]:
    groups: dict[str, list[dt.date]] = {}
    if grep:
        rx = re.compile(grep, re.IGNORECASE)
        hit = [d for d, s in rows if rx.search(s)]
        if hit:
            groups[label or grep] = hit
    elif scopes or all_scopes:
        wanted = {s.lower() for s in scopes}
        for day, subject in rows:
            m = SCOPE.match(subject)
            if not m:
                continue
            name = m.group(1).lower()
            if all_scopes or name in wanted:
                groups.setdefault(name, []).append(day)
    elif rows:
        groups[label or "path"] = [d for d, _ in rows]
    if burst_gap is not None:
        split: dict[str, list[dt.date]] = {}
        for name, days in groups.items():
            parts = bursts(days, burst_gap)
            for i, part in enumerate(parts, 1):
                split[name if len(parts) == 1 else f"{name}#{i}"] = part
        groups = split
    return {k: measure(v) for k, v in groups.items() if len(v) >= min_commits}


def report(result: dict[str, dict]) -> None:
    width = max(len(k) for k in result)
    print(f"{'feature':<{width}}  commits  first       last        calendar  active  longest gap")
    for name, r in sorted(result.items(), key=lambda kv: kv[1]["first"]):
        print(f"{name:<{width}}  {r['commits']:>7}  {r['first']}  {r['last']}  "
              f"{r['calendar']:>8}  {r['active']:>6}  {r['gap']:>11}")
    if len(result) >= 3:
        cal = sorted(r["calendar"] for r in result.values())
        act = sorted(r["active"] for r in result.values())
        print(f"\n{len(result)} features: calendar days {cal[0]} to {cal[-1]} (median "
              f"{statistics.median(cal):g}), active days {act[0]} to {act[-1]} (median "
              f"{statistics.median(act):g})")
    else:
        print("\nFewer than three features: too few for a range. Add comparable ones or report 'not measured'.")
    print("Calendar days include waits. Active days are days with a commit, not hours of work.")


def self_test() -> int:
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    ident = ["-c", "user.name=Test", "-c", "user.email=user@example.com", "-c", "commit.gpgsign=false"]
    commits = [
        ("2026-03-02", "feat(import): parse the upload"),
        ("2026-03-02", "test(import): reject an empty file"),
        ("2026-03-03", "fix(import): keep the header row"),
        ("2026-03-09", "feat(import): show the row count"),
        ("2026-03-04", "feat(export): stream the rows"),
        ("2026-03-05", "docs: describe the import"),
    ]
    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["git", "init", "-q", tmp], check=True, env=env)
        for day, subject in commits:
            stamp = day + "T12:00:00"
            subprocess.run(["git", "-C", tmp, *ident, "commit", "-q", "--allow-empty", "-m", subject],
                           check=True, env=dict(env, GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp))
        rows = git_log(tmp, "", None)
        got = collect(rows, ["import"], None, False, 1, None)["import"]
        want = {"commits": 4, "calendar": 8, "active": 3, "gap": 5}
        for key, value in want.items():
            if got[key] != value:
                print(f"self-test: import {key} = {got[key]}, expected {value}")
                failed += 1
        if set(collect(rows, [], None, True, 1, None)) != {"import", "export"}:
            print("self-test: --all-scopes should find import and export, and skip the unscoped commit")
            failed += 1
        if collect(rows, [], None, True, 2, None).keys() != {"import"}:
            print("self-test: --min-commits 2 should keep only import")
            failed += 1
        if collect(rows, [], "row", False, 1, None)["row"]["commits"] != 3:
            print("self-test: --grep row should match three subjects")
            failed += 1
        split = collect(rows, ["import"], None, False, 1, None, burst_gap=3)
        if set(split) != {"import#1", "import#2"} or split["import#1"]["calendar"] != 2:
            print("self-test: --burst-gap 3 should split import into a two-day burst and a later one")
            failed += 1
        if set(collect(rows, ["import"], None, False, 1, None, burst_gap=5)) != {"import"}:
            print("self-test: --burst-gap 5 should keep import in one piece")
            failed += 1
        if collect(rows, ["missing"], None, False, 1, None):
            print("self-test: an unknown scope should match nothing")
            failed += 1
    print("self-test: %s" % ("passed" if not failed else "%d failed" % failed))
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=".", help="repository to read (default: current directory)")
    ap.add_argument("--since", default="", help='git date limit, for example "180 days ago"')
    ap.add_argument("--scope", action="append", default=[], help="Conventional Commits scope; repeatable")
    ap.add_argument("--grep", help="regular expression on the commit subject, case-insensitive")
    ap.add_argument("--path", help="only commits that touch this path")
    ap.add_argument("--label", help="name to print for a --grep or --path selection")
    ap.add_argument("--all-scopes", action="store_true", help="one row per scope found in the history")
    ap.add_argument("--min-commits", type=int, default=1, help="drop features with fewer commits")
    ap.add_argument("--burst-gap", type=int, metavar="DAYS",
                    help="split a selection into bursts at more than DAYS idle days")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.scope or a.grep or a.path or a.all_scopes):
        ap.print_usage(sys.stderr)
        print("give --scope, --grep, --path or --all-scopes", file=sys.stderr)
        return 2
    rows = git_log(a.repo, a.since, a.path)
    result = collect(rows, a.scope, a.grep, a.all_scopes, a.min_commits, a.label, a.burst_gap)
    if not result:
        print("no commits matched; report the duration as 'not measured'")
        return 1
    report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
