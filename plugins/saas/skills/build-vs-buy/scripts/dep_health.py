#!/usr/bin/env python3
"""Read the health and reach of one package from public APIs and turn it into an admission verdict.

Sources (read-only, one request at a time): deps.dev API v3 (versions, publish dates, licenses,
advisories, OpenSSF Scorecard) and v3alpha (dependent counts), the npm registry and api.npmjs.org
download counts, the Packagist package API and Composer v2 metadata, the PyPI JSON API, OSV (advisories
for Packagist, which deps.dev does not cover) and the GitHub REST API. Python 3.10 or later, standard
library only.

Usage:
  dep_health.py npm express [--scope-lines 40] [--text]
  dep_health.py packagist laravel/framework
  dep_health.py pypi requests | go github.com/gorilla/mux | cargo serde
  dep_health.py --repo owner/name [--scope-lines 40]      GitHub signals only
  dep_health.py npm left-pad --repo owner/name             override the repository found in metadata
  dep_health.py --self-test                                offline, against built-in fixtures

GitHub token (optional, raises the rate limit from 60 to 5,000 requests an hour): GITHUB_TOKEN, else
the output of `gh auth token`. It is sent only to api.github.com, never printed and never written to
the output. --no-token skips it. DEP_HEALTH_CONTACT (an email address) is appended to the User-Agent,
as Packagist asks of API clients.

Verdicts:
  adopt            no blocker, active, wide reach
  adopt-with-adr   the owner decides and records the decision in an ADR (never decided by an agent)
  build-in-house   reach below the floors and the needed scope is small: write it in the project, or
                   copy the few lines needed where the license allows it, with attribution
  reject           archived, deprecated or abandoned, no license, or an advisory on the latest version

Exit codes:
  0  adopt
  1  any other verdict, or a failed self-test
  2  usage error, or the package does not exist in that registry
  3  no access: the registry or the network could not be reached. Nothing was judged; say so.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

TOOL = "build-vs-buy/dep_health.py 1.0"

# --- thresholds: the only place the numbers live -------------------------------------------------------
# kind "hard fact": a recorded state, no number involved. kind "cited": the number comes from the source.
# kind "practice, unverified": a working default with no citable source; change it in the project
# overlay if the owner sets other numbers.

GUIDE = "https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software (verified 2026-11)"
SCORECARD = "https://github.com/ossf/scorecard/blob/main/docs/checks.md (verified 2026-11)"
CHAOSS = "https://chaoss.community/kb/metric-contributor-absence-factor/ (verified 2026-11)"

THRESHOLDS = {
    "archived": {"value": True, "kind": "hard fact", "effect": "reject",
                 "source": SCORECARD + ": an archived project receives the lowest Maintained score"},
    "deprecated": {"value": True, "kind": "hard fact", "effect": "reject",
                   "source": "registry flag: deps.dev isDeprecated, npm deprecated, Packagist abandoned"},
    "license_missing": {"value": True, "kind": "hard fact", "effect": "reject",
                        "source": GUIDE + ": verify that every component has a license"},
    "advisory_on_latest": {"value": 1, "kind": "hard fact", "effect": "reject",
                           "source": "deps.dev advisoryKeys of the default version, or OSV query for it"},
    "release_max_days": {"value": 365, "kind": "cited", "effect": "adopt-with-adr",
                         "source": GUIDE + ": last release within the previous 12 months"},
    "activity_max_days": {"value": 365, "kind": "cited", "effect": "adopt-with-adr",
                          "source": GUIDE + ": significant activity within the previous 12 months"},
    "bus_factor_min": {"value": 2, "kind": "cited", "effect": "reach floor",
                       "source": GUIDE + ": more than one maintainer; measured as the " + CHAOSS},
    "downloads_month_min": {"value": {"npm": 50000, "packagist": 10000}, "kind": "practice, unverified",
                            "effect": "reach floor", "source": "no citable source found"},
    "dependents_min": {"value": 20, "kind": "practice, unverified", "effect": "reach floor",
                       "source": "no citable source found"},
    "stars_min": {"value": 100, "kind": "practice, unverified", "effect": "reach floor",
                  "source": "no citable source found"},
    "scope_lines_max": {"value": 300, "kind": "practice, unverified", "effect": "build-in-house",
                        "source": "owner rule: small scope plus low reach means write it in the project"},
}

DEPS = "https://api.deps.dev"
OSV = "https://api.osv.dev/v1/query"
GITHUB = "https://api.github.com"
DEPS_SYSTEMS = {"npm": "npm", "pypi": "pypi", "go": "go", "cargo": "cargo"}
DEPENDENTS_SYSTEMS = {"npm", "pypi", "cargo"}  # deps.dev: "currently available for npm, Cargo, Maven and PyPI"
ECOSYSTEMS = ["npm", "packagist", "pypi", "go", "cargo"]
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
GH_URL_RE = re.compile(r"github\.com[/:]([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:[/#?].*)?$", re.I)
NO_LICENSE = {"", "NONE", "UNLICENSED", "NOASSERTION", "NON-STANDARD", "UNKNOWN", "SEE LICENSE IN LICENSE"}

# SPDX ids by what copying a few lines into a closed-source product requires. Review-ready draft, not
# legal advice; the license text is the source (https://spdx.org/licenses/, verified 2026-11).
PERMISSIVE = {"MIT", "MIT-0", "ISC", "BSD-2-CLAUSE", "BSD-3-CLAUSE", "0BSD", "APACHE-2.0", "UNLICENSE", "ZLIB",
              "CC0-1.0", "BSL-1.0", "PYTHON-2.0", "PSF-2.0", "BLUEOAK-1.0.0", "X11"}
WEAK_COPYLEFT = {"MPL-2.0", "LGPL-2.1", "LGPL-2.1-ONLY", "LGPL-2.1-OR-LATER", "LGPL-3.0", "LGPL-3.0-ONLY",
                 "LGPL-3.0-OR-LATER", "EPL-1.0", "EPL-2.0", "CDDL-1.0"}


class UsageError(Exception):
    code = 2


class NoAccess(Exception):
    code = 3


class NotFound(Exception):
    pass


class SourceError(Exception):
    pass


# --- secrets ---------------------------------------------------------------------------------------------

_SECRETS: set[str] = set()
_REDACT_RES = [
    (re.compile(r"(?i)\b(authorization:?\s*(?:bearer|token)?)\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 [redacted]"),
    (re.compile(r"\b(?:gh[pousr]|github_pat)_[A-Za-z0-9_]{16,}"), "[redacted]"),
]


def register_secret(value: str | None) -> None:
    if value and len(value) >= 6:
        _SECRETS.add(value)


def redact(text: str) -> str:
    for s in sorted(_SECRETS, key=len, reverse=True):
        text = text.replace(s, "[redacted]")
    for rx, repl in _REDACT_RES:
        text = rx.sub(repl, text)
    return text


def github_token(use: bool) -> str | None:
    if not use:
        return None
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if not tok:
        try:
            out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=5)
            tok = out.stdout.strip() if out.returncode == 0 else ""
        except (OSError, subprocess.SubprocessError):
            tok = ""
    register_secret(tok)
    return tok or None


# --- HTTP ------------------------------------------------------------------------------------------------

def _urllib_transport(method: str, url: str, headers: dict, data: bytes | None, timeout: float):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https endpoints)
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:4000]


TRANSPORT = _urllib_transport


def http_json(url: str, *, token: str | None = None, body: dict | None = None, timeout: float = 20.0):
    contact = os.environ.get("DEP_HEALTH_CONTACT", "").strip()
    hdrs = {"User-Agent": TOOL + (f" (mailto={contact})" if contact else ""), "Accept": "application/json"}
    if url.startswith(GITHUB + "/"):
        hdrs["Accept"] = "application/vnd.github+json"
        if token:  # the token goes to api.github.com and nowhere else
            hdrs["Authorization"] = f"Bearer {token}"
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    try:
        status, raw = TRANSPORT("POST" if data else "GET", url, hdrs, data, timeout)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise NoAccess(redact(f"{url} not reachable: {getattr(e, 'reason', e)}"))
    text = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    if status == 404:
        raise NotFound(url)
    if status >= 400:
        raise SourceError(redact(f"HTTP {status}: {text[:200]}"))
    try:
        return json.loads(text) if text.strip() else {}
    except ValueError:
        raise SourceError(f"non-JSON response (HTTP {status})")


def enc(s: str) -> str:
    return urllib.parse.quote(s, safe="")


# --- collection ------------------------------------------------------------------------------------------

class Collector:
    """Holds every signal with its source URL and date, and every source call with its outcome."""

    def __init__(self, today: dt.date, token: str | None):
        self.today = today
        self.token = token
        self.signals: dict[str, dict] = {}
        self.sources: list[dict] = []

    def put(self, key: str, value, source: str, as_of: str | None = None) -> None:
        if value is None or key in self.signals:
            return
        self.signals[key] = {"value": value, "source": source, "as_of": as_of or self.today.isoformat()}

    def get(self, key: str):
        s = self.signals.get(key)
        return None if s is None else s["value"]

    def fetch(self, what: str, url: str, *, required: bool = False, body: dict | None = None):
        try:
            data = http_json(url, token=self.token, body=body)
        except NotFound:
            self.sources.append({"source": what, "url": url, "ok": False, "error": "not found (HTTP 404)"})
            if required:
                raise UsageError(f"{what}: not found at {url}")
            return None
        except (SourceError, NoAccess) as e:
            self.sources.append({"source": what, "url": url, "ok": False, "error": redact(str(e))})
            if required:
                raise NoAccess(redact(f"{what}: {e}"))
            return None
        self.sources.append({"source": what, "url": url, "ok": True})
        return data


def repo_from_url(url) -> str | None:
    if isinstance(url, dict):
        url = url.get("url")
    if not isinstance(url, str):
        return None
    m = GH_URL_RE.search(url.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def day(ts: str | None) -> str | None:
    return ts[:10] if isinstance(ts, str) and len(ts) >= 10 else None


def collect_depsdev(c: Collector, system: str, name: str) -> tuple[str | None, str | None]:
    base = f"{DEPS}/v3/systems/{system}/packages/{enc(name)}"
    pkg = c.fetch("deps.dev package", base, required=True) or {}
    versions = [v for v in pkg.get("versions", []) if isinstance(v, dict)]
    if not versions:
        raise UsageError(f"deps.dev lists no versions for {system} {name}")
    default = next((v for v in versions if v.get("isDefault")), None)
    dated = sorted((v for v in versions if v.get("publishedAt")), key=lambda v: v["publishedAt"])
    default = default or (dated[-1] if dated else versions[-1])
    version = default["versionKey"]["version"]
    if dated:
        newest = dated[-1]
        c.put("last_release", day(newest["publishedAt"]), base, day(newest["publishedAt"]))
        c.put("last_release_version", newest["versionKey"]["version"], base)
    if default.get("isDeprecated"):
        c.put("deprecated", default.get("deprecatedReason") or True, base)
    vurl = f"{base}/versions/{enc(version)}"
    ver = c.fetch("deps.dev version", vurl) or {}
    if "licenses" in ver:
        lic = [x for x in ver["licenses"] if x and x.strip().upper() not in NO_LICENSE]
        c.put("license", " AND ".join(lic) if lic else "", vurl)
    if "advisoryKeys" in ver:
        c.put("advisories", [a.get("id") for a in ver["advisoryKeys"]], vurl)
    repo = None
    for rel in ver.get("relatedProjects", []):
        if rel.get("relationType") == "SOURCE_REPO":
            pid = rel.get("projectKey", {}).get("id", "")
            if pid.startswith("github.com/"):
                repo = pid[len("github.com/"):]
                break
    if system in DEPENDENTS_SYSTEMS:
        durl = f"{DEPS}/v3alpha/systems/{system}/packages/{enc(name)}/versions/{enc(version)}:dependents"
        dep = c.fetch("deps.dev dependents", durl)
        if dep and int(dep.get("directDependentCount") or 0) > 0:
            c.put("dependents", int(dep["directDependentCount"]), durl)
        elif dep is not None:  # deps.dev cannot tell "no dependents" from "not computed" (seen for Cargo)
            c.put("dependents_reported_zero", True, durl)
    return version, repo


def collect_npm(c: Collector, name: str) -> tuple[str | None, str | None]:
    version, repo = collect_depsdev(c, "npm", name)
    lurl = f"https://registry.npmjs.org/{name.replace('/', '%2f')}/latest"
    man = c.fetch("npm registry", lurl) or {}
    if man.get("deprecated"):
        c.put("deprecated", man["deprecated"], lurl)
    if isinstance(man.get("maintainers"), list):
        c.put("registry_maintainers", len(man["maintainers"]), lurl)
    lic = man.get("license")
    if isinstance(lic, dict):
        lic = lic.get("type")
    if isinstance(lic, str):
        c.put("license", "" if lic.strip().upper() in NO_LICENSE else lic.strip(), lurl)
    repo = repo or repo_from_url(man.get("repository"))
    durl = f"https://api.npmjs.org/downloads/point/last-month/{name}"
    dl = c.fetch("npm downloads", durl)
    if dl and isinstance(dl.get("downloads"), int):
        c.put("downloads_month", dl["downloads"], durl, dl.get("end"))
    return version, repo


def collect_pypi(c: Collector, name: str) -> tuple[str | None, str | None]:
    version, repo = collect_depsdev(c, "pypi", name)
    purl = f"https://pypi.org/pypi/{enc(name)}/json"
    data = c.fetch("PyPI JSON", purl) or {}
    info = data.get("info") or {}
    lic = info.get("license_expression") or info.get("license")
    if isinstance(lic, str) and len(lic) <= 80:  # long values are a pasted license text, not an identifier
        c.put("license", "" if lic.strip().upper() in NO_LICENSE else lic.strip(), purl)
    if isinstance(data.get("vulnerabilities"), list):
        live = [v.get("id") for v in data["vulnerabilities"] if not v.get("withdrawn")]
        c.put("advisories", live, purl)
    for url in (info.get("project_urls") or {}).values():
        repo = repo or repo_from_url(url)
    return version, repo


def _p2_expand(entries: list[dict]) -> list[dict]:
    """Composer v2 minified metadata: each entry carries only what changed since the previous one."""
    out, cur = [], {}
    for e in entries:
        cur = dict(cur)
        for k, v in e.items():
            if v == "__unset":
                cur.pop(k, None)
            else:
                cur[k] = v
        out.append(cur)
    return out


def collect_packagist(c: Collector, name: str) -> tuple[str | None, str | None]:
    if not REPO_RE.match(name):
        raise UsageError("a Packagist name is vendor/package")
    vendor, pkg = name.split("/")
    jurl = f"https://packagist.org/packages/{enc(vendor)}/{enc(pkg)}.json"
    data = (c.fetch("Packagist package API", jurl, required=True) or {}).get("package") or {}
    dl = data.get("downloads") or {}
    if isinstance(dl.get("monthly"), int):
        c.put("downloads_month", dl["monthly"], jurl)
    for key in ("dependents", "suggesters", "favers"):
        if isinstance(data.get(key), int):
            c.put(key, data[key], jurl)
    if isinstance(data.get("github_stars"), int):
        c.put("stars_packagist", data["github_stars"], jurl)
    if isinstance(data.get("maintainers"), list):
        c.put("registry_maintainers", len(data["maintainers"]), jurl)
    if data.get("abandoned"):
        c.put("deprecated", f"abandoned: {data['abandoned']}", jurl)
    repo = repo_from_url(data.get("repository"))
    murl = f"https://repo.packagist.org/p2/{enc(vendor)}/{enc(pkg)}.json"
    meta = c.fetch("Packagist metadata", murl) or {}
    entries = _p2_expand((meta.get("packages") or {}).get(name) or [])
    stable = [e for e in entries if e.get("version") and not re.search(r"(?i)dev|alpha|beta|rc", e["version"])]
    latest = stable[0] if stable else (entries[0] if entries else None)
    version = None
    if latest:
        version = latest["version"].lstrip("v")
        times = sorted(e["time"] for e in stable if e.get("time"))
        if times:
            c.put("last_release", day(times[-1]), murl, day(times[-1]))
            c.put("last_release_version", latest["version"], murl)
        lic = latest.get("license")
        if isinstance(lic, list):  # Composer: an array of licenses is disjunctive ("or")
            ok = [x for x in lic if x.strip().upper() not in NO_LICENSE]
            c.put("license", " OR ".join(ok) if ok else "", murl)
        if latest.get("abandoned"):
            c.put("deprecated", f"abandoned: {latest['abandoned']}", murl)
    if version:
        res = c.fetch("OSV query", OSV, body={"version": version,
                                             "package": {"name": name, "ecosystem": "Packagist"}})
        if res is not None:
            c.put("advisories", [v.get("id") for v in res.get("vulns", []) if not v.get("withdrawn")],
                  f"{OSV} (Packagist {name} {version})")
    return version, repo


def bus_factor(contributors: list[dict]) -> int | None:
    """CHAOSS Contributor Absence Factor: fewest people who together hold half of all contributions."""
    counts = sorted((int(x.get("contributions") or 0) for x in contributors
                     if x.get("type") != "Bot" and not str(x.get("login", "")).endswith("[bot]")), reverse=True)
    total = sum(counts)
    if total <= 0:
        return None
    run = 0
    for i, n in enumerate(counts, 1):
        run += n
        if run * 2 >= total:
            return i
    return len(counts)


def collect_github(c: Collector, repo: str) -> None:
    rurl = f"{GITHUB}/repos/{repo}"
    data = c.fetch("GitHub repository", rurl)
    if not data:
        return
    c.put("archived", bool(data.get("archived") or data.get("disabled")), rurl)
    c.put("stars", data.get("stargazers_count"), rurl)
    c.put("last_push", day(data.get("pushed_at")), rurl, day(data.get("pushed_at")))
    lic = (data.get("license") or {}).get("spdx_id") if data.get("license") else ""
    c.put("license_repo", lic, rurl)
    curl = f"{rurl}/contributors?per_page=100"
    people = c.fetch("GitHub contributors", curl)
    if isinstance(people, list):
        c.put("contributors", f"{len(people)}+" if len(people) >= 100 else len(people), curl)
        c.put("bus_factor", bus_factor(people), curl + " (first 100, bots excluded)")
    purl = f"{DEPS}/v3/projects/{enc('github.com/' + repo)}"
    proj = c.fetch("deps.dev project (OpenSSF Scorecard)", purl) or {}
    sc = proj.get("scorecard") or {}
    if sc:
        c.put("scorecard_overall", sc.get("overallScore"), purl, day(sc.get("date")))
        for chk in sc.get("checks", []):
            if chk.get("name") == "Maintained":
                c.put("scorecard_maintained", chk.get("score"), purl, day(sc.get("date")))


# --- verdict ---------------------------------------------------------------------------------------------

def _license_terms(expr: str) -> list[list[str]]:
    """'MIT OR (Apache-2.0 AND BSD-3-Clause)' -> [['MIT'], ['APACHE-2.0', 'BSD-3-CLAUSE']] (OR of ANDs)."""
    expr = expr.replace("(", " ").replace(")", " ")
    return [[t.strip().upper().removesuffix("+") for t in re.split(r"\s+AND\s+", alt, flags=re.I) if t.strip()]
            for alt in re.split(r"\s+OR\s+|/", expr, flags=re.I) if alt.strip()]


def copy_terms(license_expr: str | None) -> dict:
    """What copying a few lines into the project requires. Review-ready draft, not legal advice."""
    if not license_expr:
        return {"permitted": False, "license": license_expr,
                "note": "No license grants no rights: do not copy. Write it fresh from the specification, "
                        "without the package source open."}
    rank = {"permissive": 0, "weak-copyleft": 1, "strong-copyleft": 2, "unknown": 3}

    def kind(i: str) -> str:
        if i in PERMISSIVE:
            return "permissive"
        if i in WEAK_COPYLEFT:
            return "weak-copyleft"
        if re.match(r"^A?GPL-", i):
            return "strong-copyleft"
        return "unknown"

    best = min((max((kind(i) for i in alt), key=rank.get) for alt in _license_terms(license_expr)),
               key=rank.get, default="unknown")
    if best == "permissive":
        apache = "APACHE-2.0" in license_expr.upper()
        return {"permitted": True, "license": license_expr,
                "note": "Copying the needed lines is permitted with attribution: keep the copyright line "
                        "and the license text next to the copied code"
                        + (", carry over the NOTICE file content and mark your changes." if apache else ".")}
    if best == "weak-copyleft":
        return {"permitted": False, "license": license_expr,
                "note": "Copied code stays under this license (file-level for MPL-2.0). Ask the owner before "
                        "copying; writing it fresh avoids the question."}
    if best == "strong-copyleft":
        return {"permitted": False, "license": license_expr,
                "note": "Copying would put the product under the same license. Do not copy; write it fresh."}
    return {"permitted": False, "unknown": True, "license": license_expr,
            "note": "License not recognised by this script. Read the license text before copying anything."}


def _age_days(iso: str | None, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat(iso)).days if iso else None
    except ValueError:
        return None


def evaluate(c: Collector, ecosystem: str | None, scope_lines: int | None) -> dict:
    t = {k: v["value"] for k, v in THRESHOLDS.items()}
    blockers, holds, notes = [], [], []

    def reason(bucket, code, detail, key, kind="unverified"):
        bucket.append({"code": code, "kind": THRESHOLDS[key]["kind"] if key else kind,
                       "detail": detail, "source": THRESHOLDS[key]["source"] if key else None})

    archived = c.get("archived")
    if archived:
        reason(blockers, "archived", "the source repository is archived", "archived")
    elif archived is None:
        reason(holds, "archived-unverified", "archived state not read (no GitHub repository or no access)", None)
    if c.get("deprecated"):
        reason(blockers, "deprecated", f"the registry marks it deprecated or abandoned: {c.get('deprecated')}",
               "deprecated")

    lic, lic_repo = c.get("license"), c.get("license_repo")
    effective = lic or (lic_repo if lic_repo and lic_repo.upper() not in NO_LICENSE else None)
    if lic is None and lic_repo is None:
        reason(holds, "license-unverified", "no license information could be read", None)
    elif not effective and (lic_repo or "").upper() == "NOASSERTION":
        reason(holds, "license-unrecognised", "a license file exists but its type is not recognised; read it",
               None)
    elif not effective:
        reason(blockers, "no-license", "no license in the registry metadata or the repository",
               "license_missing")

    adv = c.get("advisories")
    if adv:
        reason(blockers, "advisory", f"advisories affect the latest version: {', '.join(map(str, adv[:5]))}",
               "advisory_on_latest")
    elif adv is None and ecosystem:
        reason(holds, "advisories-unverified", "advisories for the latest version not read", None)

    for key, sig, label in (("release_max_days", "last_release", "release"),
                            ("activity_max_days", "last_push", "push to the repository")):
        age = _age_days(c.get(sig), c.today)
        if age is None:
            if sig == "last_release" and ecosystem:
                reason(holds, "release-unverified", "date of the last release not read", None)
            elif sig == "last_push" and archived is not None:
                reason(notes, "push-unverified", "date of the last push not read", None)
        elif age > t[key]:
            reason(holds, f"stale-{sig.replace('_', '-')}",
                   f"last {label} {c.get(sig)} is {age} days ago (limit {t[key]})", key)

    floors = []
    dl_floor = t["downloads_month_min"].get(ecosystem or "")
    stars = c.get("stars") if c.get("stars") is not None else c.get("stars_packagist")
    for key, value, floor, label in (
            ("downloads_month_min", c.get("downloads_month"), dl_floor, "downloads in the last month"),
            ("dependents_min", c.get("dependents"), t["dependents_min"], "direct dependents"),
            ("stars_min", stars, t["stars_min"], "GitHub stars"),
            ("bus_factor_min", c.get("bus_factor"), t["bus_factor_min"], "bus factor")):
        if floor is None:
            reason(notes, f"{key.removesuffix('_min')}-not-offered",
                   f"{label}: no official source for this ecosystem", None)
        elif value is None:
            reason(notes, f"{key.removesuffix('_min')}-unverified", f"{label}: not read", None)
        else:
            floors.append(value >= floor)
            if value < floor:
                reason(notes, f"below-{key.removesuffix('_min')}", f"{label} {value} below floor {floor}", key)
    below = floors.count(False)
    low_reach = bool(floors) and below * 2 > len(floors)
    if not floors:
        reason(holds, "reach-unverified", "no reach signal could be read", None)
    if low_reach:
        reason(holds, "low-reach", f"{below} of {len(floors)} reach signals are below their floor", None,
               "derived: more than half of the measured reach floors missed")

    small = scope_lines is not None and scope_lines <= t["scope_lines_max"]
    if blockers:
        verdict = "reject"
    elif low_reach and small:
        verdict = "build-in-house"
    elif holds:
        verdict = "adopt-with-adr"
        if low_reach and scope_lines is None:
            reason(holds, "scope-missing", "pass --scope-lines: low reach with a small scope means build in-house",
                   None, "input missing")
        elif low_reach:
            reason(holds, "scope-large", f"scope of {scope_lines} lines is above {t['scope_lines_max']}: "
                                         "the owner weighs writing it against depending on it", "scope_lines_max")
    else:
        verdict = "adopt"
    out = {"verdict": verdict, "reasons": blockers + holds, "notes": notes, "low_reach": low_reach}
    if verdict == "build-in-house" or small:
        out["copy"] = copy_terms(effective)
        if verdict == "reject" and small:
            out["copy"]["advice"] = "the scope is small: write the needed lines in the project"
    return out


# --- run -------------------------------------------------------------------------------------------------

COLLECTORS = {"npm": collect_npm, "pypi": collect_pypi, "packagist": collect_packagist}


def run(ecosystem: str | None, name: str | None, repo: str | None, scope_lines: int | None,
        token: str | None, today: dt.date | None = None) -> dict:
    if ecosystem and ecosystem not in ECOSYSTEMS:
        raise UsageError(f"ecosystem must be one of {', '.join(ECOSYSTEMS)}")
    if repo and not REPO_RE.match(repo):
        raise UsageError("--repo is owner/name")
    if not (ecosystem and name) and not repo:
        raise UsageError("give an ecosystem and a package name, or --repo owner/name")
    if scope_lines is not None and scope_lines < 0:
        raise UsageError("--scope-lines must be zero or more")
    c = Collector(today or dt.datetime.now(dt.timezone.utc).date(), token)
    version, found_repo = None, None
    if ecosystem:
        fn = COLLECTORS.get(ecosystem)
        if fn:
            version, found_repo = fn(c, name)
        else:
            version, found_repo = collect_depsdev(c, DEPS_SYSTEMS[ecosystem], name)
            if ecosystem == "go" and not found_repo:
                found_repo = repo_from_url(name)
    repo = repo or found_repo
    if repo:
        collect_github(c, repo)
    if not ecosystem and c.get("archived") is None:
        raise NoAccess("GitHub repository could not be read: " + "; ".join(
            s.get("error", "") for s in c.sources if not s["ok"]))
    result = evaluate(c, ecosystem, scope_lines)
    return {"tool": TOOL, "checked_at": c.today.isoformat(),
            "package": {"ecosystem": ecosystem, "name": name, "version": version}, "repo": repo,
            "scope_lines": scope_lines, **result, "exit": 0 if result["verdict"] == "adopt" else 1,
            "signals": c.signals, "sources": c.sources,
            "thresholds": {k: {kk: vv for kk, vv in v.items()} for k, v in THRESHOLDS.items()}}


def as_text(r: dict) -> str:
    p = r["package"]
    head = f"{p['ecosystem']} {p['name']} {p['version'] or ''}".strip() if p["ecosystem"] else r["repo"]
    lines = [f"{head}  (repo: {r['repo'] or 'none found'}, checked {r['checked_at']})", "", "Signals:"]
    for k, s in r["signals"].items():
        lines.append(f"  {k:22} {s['value']!s:24} {s['as_of']}  {s['source']}")
    lines += ["", f"Verdict: {r['verdict']}"]
    for x in r["reasons"]:
        lines.append(f"  - [{x['kind']}] {x['detail']}")
    if r["notes"]:
        lines.append("Notes:")
        lines += [f"  - [{x['kind']}] {x['detail']}" for x in r["notes"]]
    if "copy" in r:
        verdict = ("unknown, check the license" if r["copy"].get("unknown")
                   else "permitted" if r["copy"]["permitted"] else "not permitted")
        lines.append(f"Copying: {verdict} "
                     f"({r['copy']['license'] or 'no license'}). {r['copy']['note']}")
        if r["copy"].get("advice"):
            lines.append(f"  {r['copy']['advice']}")
    failed = [s for s in r["sources"] if not s["ok"]]
    if failed:
        lines.append("Sources not read:")
        lines += [f"  - {s['source']}: {s['error']}" for s in failed]
    return "\n".join(lines)


# --- self-test -------------------------------------------------------------------------------------------

class _FakeTransport:
    """Answers by URL prefix. A value is (status, payload) or an exception to raise."""

    def __init__(self, routes: dict):
        self.routes = routes
        self.calls: list[dict] = []

    def __call__(self, method, url, headers, data, timeout):
        self.calls.append({"method": method, "url": url, "headers": dict(headers)})
        for prefix in sorted(self.routes, key=len, reverse=True):
            if url.startswith(prefix):
                r = self.routes[prefix]
                if isinstance(r, Exception):
                    raise r
                status, payload = r
                return status, payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        return 404, b"{}"


def _npm_fixture(name, *, repo="example/" + "lib", license_="MIT", released="2026-10-01", deprecated=False,
                 advisories=(), dependents=5000, downloads=9_000_000, maintainers=4, stars=20000,
                 archived=False, pushed="2026-10-20", contributors=(400, 300, 200, 100), gh_license="MIT"):
    d = f"{DEPS}/v3/systems/npm/packages/{name}"
    gh = f"{GITHUB}/repos/{repo}"
    vk = {"system": "NPM", "name": name, "version": "2.0.0"}
    return {
        d: (200, {"packageKey": {"system": "NPM", "name": name},
                  "versions": [{"versionKey": dict(vk, version="1.0.0"), "publishedAt": "2020-01-01T00:00:00Z"},
                               {"versionKey": vk, "publishedAt": released + "T00:00:00Z", "isDefault": True,
                                "isDeprecated": deprecated, "deprecatedReason": "use another" if deprecated else ""}]}),
        f"{d}/versions/2.0.0": (200, {"versionKey": vk, "licenses": [license_] if license_ else [],
                                      "advisoryKeys": [{"id": a} for a in advisories],
                                      "relatedProjects": [{"projectKey": {"id": f"github.com/{repo}"},
                                                           "relationType": "SOURCE_REPO"}]}),
        f"{DEPS}/v3alpha/systems/npm/packages/{name}/versions/2.0.0:dependents":
            (200, {"dependentCount": dependents * 3, "directDependentCount": dependents}),
        f"https://registry.npmjs.org/{name}/latest": (200, {"license": license_ or None,
                                                             "maintainers": [{"name": f"m{i}"} for i in range(maintainers)]}),
        f"https://api.npmjs.org/downloads/point/last-month/{name}":
            (200, {"downloads": downloads, "start": "2026-10-04", "end": "2026-11-02", "package": name}),
        gh: (200, {"stargazers_count": stars, "archived": archived, "pushed_at": pushed + "T00:00:00Z",
                   "license": {"spdx_id": gh_license} if gh_license else None}),
        f"{gh}/contributors": (200, [{"login": f"u{i}", "type": "User", "contributions": n}
                                     for i, n in enumerate(contributors)]
                               + [{"login": "dependabot[bot]", "type": "Bot", "contributions": 5000}]),
        f"{DEPS}/v3/projects/": (200, {"scorecard": {"date": "2026-10-26T00:00:00Z", "overallScore": 7.1,
                                                      "checks": [{"name": "Maintained", "score": 10}]}}),
    }


def self_test() -> int:
    fails: list[str] = []
    check = lambda ok, msg: ok or fails.append(msg)  # noqa: E731
    today = dt.date(2026, 11, 4)
    saved = TRANSPORT

    def go(routes, eco="npm", name="pkg", repo=None, scope=None, token=None):
        fake = _FakeTransport(routes)
        globals()["TRANSPORT"] = fake
        return run(eco, name, repo, scope, token, today), fake

    try:
        # 1. a big, healthy package: adopt, exit 0, every signal carries a source and a date
        r, _ = go(_npm_fixture("big"), name="big")
        check(r["verdict"] == "adopt" and r["exit"] == 0, f"healthy: expected adopt, got {r['verdict']} {r['reasons']}")
        check(all(s["source"] and s["as_of"] for s in r["signals"].values()), "healthy: a signal lacks source/date")
        check(r["signals"]["bus_factor"]["value"] == 2, f"bus factor: expected 2 (bots excluded), "
                                                        f"got {r['signals'].get('bus_factor')}")
        check(r["signals"]["downloads_month"]["as_of"] == "2026-11-02", "downloads: as_of must be the period end")

        zero = _npm_fixture("zero", dependents=0, contributors=(900, 5))
        del zero["https://api.npmjs.org/downloads/point/last-month/zero"]
        r, _ = go(zero, name="zero")
        check(r["verdict"] == "adopt" and "dependents" not in r["signals"],
              f"deps.dev zero dependents must count as unverified, got {r['verdict']} {r['reasons']}")

        # 2. archived repository: reject, even with wide reach
        r, _ = go(_npm_fixture("old", archived=True), name="old")
        check(r["verdict"] == "reject" and any(x["code"] == "archived" for x in r["reasons"]),
              f"archived: expected reject/archived, got {r['verdict']} {r['reasons']}")

        # 3. tiny single-maintainer package, 20 lines needed: build in-house, MIT copy permitted
        tiny = _npm_fixture("tiny", stars=3, downloads=900, dependents=1, maintainers=1, contributors=(12,))
        r, _ = go(tiny, name="tiny", scope=20)
        check(r["verdict"] == "build-in-house" and r["exit"] == 1,
              f"tiny: expected build-in-house, got {r['verdict']} {r['reasons']}")
        check(r.get("copy", {}).get("permitted") is True and "attribution" in r["copy"]["note"],
              f"tiny: MIT must allow copying with attribution, got {r.get('copy')}")
        r, _ = go(tiny, name="tiny", scope=2000)
        check(r["verdict"] == "adopt-with-adr" and any(x["code"] == "scope-large" for x in r["reasons"]),
              f"tiny, big scope: expected adopt-with-adr/scope-large, got {r['verdict']}")
        r, _ = go(tiny, name="tiny")
        check(r["verdict"] == "adopt-with-adr" and any(x["code"] == "scope-missing" for x in r["reasons"]),
              f"tiny, no scope: expected adopt-with-adr/scope-missing, got {r['verdict']}")
        r, _ = go(_npm_fixture("one", contributors=(900, 5)), name="one")
        check(r["verdict"] == "adopt" and any(x["code"] == "below-bus_factor" for x in r["notes"]),
              f"one maintainer, wide reach: expected adopt with a bus-factor note, got {r['verdict']}")

        # 4. missing license: reject, and copying is not permitted
        r, _ = go(_npm_fixture("nolic", license_="", gh_license=None, stars=4, downloads=50, dependents=0),
                  name="nolic", scope=30)
        check(r["verdict"] == "reject" and any(x["code"] == "no-license" for x in r["reasons"]),
              f"no license: expected reject/no-license, got {r['verdict']} {r['reasons']}")
        check(r.get("copy", {}).get("permitted") is False, "no license: copying must not be permitted")
        r, _ = go(_npm_fixture("adv", advisories=("GHSA-test-0001",)), name="adv")
        check(r["verdict"] == "reject", f"advisory on latest: expected reject, got {r['verdict']}")
        r, _ = go(_npm_fixture("stale", released="2024-05-01"), name="stale")
        check(r["verdict"] == "adopt-with-adr" and any(x["code"] == "stale-last-release" for x in r["reasons"]),
              f"stale: expected adopt-with-adr/stale-last-release, got {r['verdict']}")

        # 5. network down: NoAccess, exit 3; GitHub rate limit alone: no adopt
        down = {"https://": urllib.error.URLError("network unreachable")}
        try:
            go(down, name="big")
            fails.append("network down: expected NoAccess")
        except NoAccess as e:
            check(e.code == 3, "network down: exit code must be 3")
        routes = _npm_fixture("big", repo="example/lim")
        routes[f"{GITHUB}/repos/example/lim"] = (403, {"message": "API rate limit exceeded"})
        r, _ = go(routes, name="big")
        check(r["verdict"] == "adopt-with-adr" and any(x["code"] == "archived-unverified" for x in r["reasons"]),
              f"GitHub refused: expected adopt-with-adr/archived-unverified, got {r['verdict']}")
        try:
            go({}, name="missing")
            fails.append("unknown package: expected UsageError")
        except UsageError as e:
            check(e.code == 2, "unknown package: exit code must be 2")

        # 6. token: sent only to api.github.com, redacted from errors, absent from the output
        tok = "gh" + "p_" + "FAKEtoken" + "0" * 27
        register_secret(tok)
        routes = _npm_fixture("big", repo="example/echo")
        routes[f"{GITHUB}/repos/example/echo/contributors"] = (500, f"bad header Authorization: Bearer {tok}".encode())
        r, fake = go(routes, name="big", token=tok)
        for call in fake.calls:
            sent = call["headers"].get("Authorization", "")
            check((tok in sent) == call["url"].startswith(GITHUB + "/"),
                  f"token must go to api.github.com only: {call['url']}")
        dumped = json.dumps(r) + as_text(r)
        check(tok not in dumped and "FAKEtoken" not in dumped, "token leaked into the output")
        check("[redacted]" in dumped, "the echoed token must appear as [redacted]")

        # 7. Packagist: downloads, dependents and favers from the package API, license from p2, OSV advisories
        pk = "https://packagist.org/packages/acme/http.json"
        p2 = "https://repo.packagist.org/p2/acme/http.json"
        routes = {pk: (200, {"package": {"downloads": {"monthly": 2_000_000}, "dependents": 900, "favers": 3000,
                                         "suggesters": 10, "github_stars": 2900, "maintainers": [{"name": "a"}],
                                         "repository": "https://github.com/acme/http"}}),
                  p2: (200, {"packages": {"acme/http": [  # minified: later entries inherit the license
                      {"version": "v4.0.0-RC1", "time": "2026-10-30T10:00:00+00:00", "license": ["MIT"]},
                      {"version": "v3.1.0", "time": "2026-09-30T10:00:00+00:00"},
                      {"version": "v3.0.0", "time": "2026-01-02T10:00:00+00:00"}]}}),
                  OSV: (200, {}), **{k.replace("example/lib", "acme/http"): v
                                     for k, v in _npm_fixture("x").items() if k.startswith(GITHUB)},
                  f"{DEPS}/v3/projects/": (200, {})}
        r, fake = go(routes, eco="packagist", name="acme/http")
        check(r["verdict"] == "adopt", f"packagist: expected adopt, got {r['verdict']} {r['reasons']}")
        check(r["signals"]["license"]["value"] == "MIT" and r["package"]["version"] == "3.1.0"
              and r["signals"]["last_release"]["value"] == "2026-09-30",
              f"packagist: license/version from p2, got {r['signals'].get('license')} {r['package']}")
        osv = [c for c in fake.calls if c["url"] == OSV]
        check(len(osv) == 1 and osv[0]["method"] == "POST", "packagist: one OSV POST for the latest version")

        # 8. license expressions
        check(copy_terms("MIT OR GPL-3.0-only")["permitted"] is True, "MIT OR GPL: the MIT branch permits copying")
        check(copy_terms("GPL-3.0-only")["permitted"] is False, "GPL: copying not permitted")
        check(copy_terms("WTFPL").get("unknown") is True and copy_terms("MIT").get("unknown") is None,
              "an unrecognised license is unknown, not forbidden")
        check(copy_terms("MIT AND GPL-2.0-or-later")["permitted"] is False, "MIT AND GPL: the strictest term wins")
        check("NOTICE" in copy_terms("Apache-2.0")["note"], "Apache-2.0: NOTICE must be named")
    except Exception as e:  # a crash is a failure, reported like one
        fails.append(f"unexpected {e.__class__.__name__}: {e}")
    finally:
        globals()["TRANSPORT"] = saved

    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("dep_health.py self-test: ok (healthy adopt, archived reject, tiny build-in-house, scope gates, "
          "bus factor, no-license reject, advisory, stale release, network down, GitHub refused, unknown "
          "package, token scope and redaction, Packagist, license expressions)")
    return 0


# --- CLI -------------------------------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Package health, reach and admission verdict.",
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("package", nargs="*", help="ECOSYSTEM NAME, for example: npm express")
    ap.add_argument("--repo", help="GitHub repository owner/name (overrides the one found in metadata)")
    ap.add_argument("--scope-lines", type=int, help="estimated lines the project needs from the package")
    ap.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    ap.add_argument("--no-token", action="store_true", help="do not use GITHUB_TOKEN or gh auth token")
    ap.add_argument("--self-test", action="store_true", help="run the offline self-test")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        if len(args.package) not in (0, 2):
            raise UsageError("give ECOSYSTEM NAME, for example: npm express")
        eco, name = (args.package + [None, None])[:2]
        r = run(eco.lower() if eco else None, name, args.repo, args.scope_lines, github_token(not args.no_token))
    except (UsageError, NoAccess) as e:
        print(json.dumps({"error": redact(str(e)), "exit": e.code}), file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    except Exception as e:  # no traceback: frames can hold the token
        print(json.dumps({"error": redact(f"unexpected {e.__class__.__name__}: {e}"), "exit": 3}), file=sys.stderr)
        return 3
    print(as_text(r) if args.text else json.dumps(r, indent=1, ensure_ascii=False))
    return r["exit"]


if __name__ == "__main__":
    sys.exit(main())
