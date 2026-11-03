#!/usr/bin/env python3
"""Read search and site performance from official APIs, store dated snapshots and compare them.

Sources: Google Search Console (Search Analytics, URL Inspection, sitemaps), Bing Webmaster Tools
(query and page stats) and the Plausible Stats API v2. Read-only. Python 3.10 or later, standard library
only; the Google service-account login signs its JWT with the `openssl` command-line tool.

Usage:
  measure.py gsc --site sc-domain:example.com [--days 28 | --start D --end D] [--dims page,query]
                 [--filter page:contains:/pricing] [--type web] [--data-state final] [--max-rows N]
  measure.py inspect --site sc-domain:example.com --url https://www.example.com/a [--url ...]
                 [--urls-file FILE] [--max 100]
  measure.py sitemaps --site sc-domain:example.com
  measure.py bing --site https://www.example.com/ [--method GetPageStats] [--days 28 | --start --end]
  measure.py plausible --site-id example.com [--metrics visitors,visits] [--dims visit:entry_page]
                 [--days 28 | --start --end | --range 28d] [--filter JSON]
  measure.py snapshot --label baseline [--gsc-site S] [--bing-site S] [--plausible-site S] [--days 28]
                 [--out docs/growth/snapshots]
  measure.py compare BEFORE.json AFTER.json [--by page|query] [--treated FILE --control FILE]
  measure.py compare --gsc-site S --before 2026-08-31:2026-09-27 --after 2026-10-05:2026-11-01
  measure.py window [--days 28] [--lag 3]
  measure.py --self-test

Credentials (never passed on the command line, never printed, never written to a snapshot):
  GSC_ACCESS_TOKEN              a ready OAuth access token with the webmasters.readonly scope, or
  GSC_SERVICE_ACCOUNT_FILE      service-account JSON key (default: CONFIG/gsc-service-account.json)
  BING_WEBMASTER_API_KEY        or BING_WEBMASTER_API_KEY_FILE (default: CONFIG/bing-api-key)
  PLAUSIBLE_API_KEY             or PLAUSIBLE_API_KEY_FILE (default: CONFIG/plausible-api-key)
  PLAUSIBLE_BASE_URL            for a self-hosted instance (default: https://plausible.io)
  CONFIG is $SEARCH_MEASUREMENT_CONFIG_DIR or ~/.config/search-measurement. Key files must be mode 600
  (no group or other bits) and must not sit inside a git work tree; otherwise the script refuses them.

Exit codes:
  0  done; JSON on stdout
  1  a check failed (self-test, or a snapshot that would contain a credential)
  2  usage error (arguments, dates, unreadable input file)
  3  no access: credentials missing, unsafe or rejected, openssl missing, or network unreachable.
     Nothing was measured; say so instead of guessing numbers.
  4  the API refused the request (quota, rate limit, bad request, server error)
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

TOOL = "search-measurement/measure.py 1.0"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_BASE = "https://www.googleapis.com/webmasters/v3"
INSPECT_URL = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
BING_BASE = "https://ssl.bing.com/webmaster/api.svc/json/"
PLAUSIBLE_DEFAULT = "https://plausible.io"

GSC_PAGE = 25000          # rowLimit maximum per Search Analytics request
GSC_LAG_DAYS = 3          # "typically available after 2-3 days"
JWT_MAX_LIFETIME = 3600   # Google: exp at most one hour after iat
INSPECT_PER_DAY = 2000    # URL Inspection quota per site per day
INSPECT_PER_MIN = 600     # URL Inspection quota per site per minute
PLAUSIBLE_PAGE = 10000    # default and page size of Plausible pagination
GSC_DIMS = {"query", "page", "country", "device", "searchAppearance", "date", "hour"}
GSC_TYPES = {"web", "image", "video", "news", "discover", "googleNews"}
GSC_OPERATORS = {"contains", "equals", "notContains", "notEquals", "includingRegex", "excludingRegex"}
BING_METHODS = {"GetQueryStats", "GetPageStats", "GetRankAndTrafficStats"}
MIN_CLAIM_DAYS = 28
DEFAULT_MIN_IMPRESSIONS = 100
POSITION_EPSILON = 0.1


class UsageError(Exception):
    code = 2


class NoAccess(Exception):
    code = 3


class ApiError(Exception):
    code = 4


class CheckFailed(Exception):
    code = 1


# --- secrets -----------------------------------------------------------------------------------------

_SECRETS: set[str] = set()
_REDACT_RES = [
    (re.compile(r'"private_key"\s*:\s*"(?:[^"\\]|\\.)*"'), '"private_key": "[redacted]"'),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S), "[redacted key]"),
    (re.compile(r"(?i)\b(apikey|api_key|access_token|assertion|refresh_token|client_secret)=[^&\s\"']+"),
     r"\1=[redacted]"),
    (re.compile(r'(?i)"(access_token|refresh_token|id_token|client_secret)"\s*:\s*"[^"]*"'), r'"\1": "[redacted]"'),
    (re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 [redacted]"),
    (re.compile(r"\bya29\.[A-Za-z0-9._-]+"), "[redacted]"),
]


def register_secret(value: str | None) -> None:
    """Remember a credential so every later message can be scrubbed of it."""
    if not value or len(value) < 6:
        return
    _SECRETS.add(value)
    _SECRETS.add(json.dumps(value)[1:-1])  # the JSON-escaped form, e.g. a PEM key with \n
    _SECRETS.add(urllib.parse.quote(value, safe=""))


def redact(text: str) -> str:
    for s in sorted(_SECRETS, key=len, reverse=True):
        if s:
            text = text.replace(s, "[redacted]")
    for rx, repl in _REDACT_RES:
        text = rx.sub(repl, text)
    return text


def contains_registered_secret(text: str) -> bool:
    return any(s and s in text for s in _SECRETS)


# --- dates -------------------------------------------------------------------------------------------

def pacific_today() -> dt.date:
    """Search Console dates are Pacific Time."""
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Los_Angeles")).date()
    except Exception:  # no tz database: UTC-8 is at most one hour off
        return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=8)).date()


def parse_date(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        raise UsageError(f"not a date (YYYY-MM-DD): {s!r}")


def lagged_window(days: int, lag: int = GSC_LAG_DAYS, today: dt.date | None = None) -> tuple[dt.date, dt.date]:
    """Window of `days` days that ends `lag` days before today, so final data is complete."""
    if days < 1:
        raise UsageError("--days must be at least 1")
    if lag < 0:
        raise UsageError("--lag must not be negative")
    today = today or pacific_today()
    end = today - dt.timedelta(days=lag)
    return end - dt.timedelta(days=days - 1), end


def prior_window(start: dt.date, end: dt.date, year_ago: bool = False) -> tuple[dt.date, dt.date]:
    """Same length, same weekdays: the directly preceding window, or 52 weeks earlier."""
    shift = dt.timedelta(days=364) if year_ago else (end - start + dt.timedelta(days=1))
    return start - shift, end - shift


def parse_span(s: str) -> tuple[dt.date, dt.date]:
    if ":" not in s:
        raise UsageError(f"window must be START:END, got {s!r}")
    a, b = s.split(":", 1)
    start, end = parse_date(a), parse_date(b)
    if end < start:
        raise UsageError(f"window ends before it starts: {s!r}")
    return start, end


def window_info(start: dt.date, end: dt.date, today: dt.date | None = None, lag: int = GSC_LAG_DAYS) -> dict:
    today = today or pacific_today()
    days = (end - start).days + 1
    return {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": days,
        "start_weekday": start.strftime("%a"),
        "whole_weeks": days % 7 == 0,
        "inside_lag": end > today - dt.timedelta(days=lag),
    }


def resolve_window(args) -> tuple[dt.date, dt.date]:
    if getattr(args, "start", None) or getattr(args, "end", None):
        if not (args.start and args.end):
            raise UsageError("give both --start and --end, or --days")
        start, end = parse_date(args.start), parse_date(args.end)
        if end < start:
            raise UsageError("--end is before --start")
        return start, end
    return lagged_window(args.days, args.lag)


# --- HTTP ----------------------------------------------------------------------------------------------

def _urllib_transport(method: str, url: str, headers: dict, data: bytes | None, timeout: float):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (fixed https endpoints)
            return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:4000]


TRANSPORT = _urllib_transport


def http_json(method: str, url: str, *, headers: dict | None = None, body: dict | None = None,
              form: dict | None = None, timeout: float = 60.0, what: str = "API") -> dict:
    hdrs = {"User-Agent": TOOL, "Accept": "application/json"}
    hdrs.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    elif form is not None:
        data = urllib.parse.urlencode(form).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    try:
        status, raw = TRANSPORT(method, url, hdrs, data, timeout)
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        raise NoAccess(redact(f"{what} not reachable: {getattr(e, 'reason', e)}"))
    text = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    if status in (401, 403):
        raise NoAccess(redact(f"{what} rejected the credentials or the account lacks access (HTTP {status}): "
                              f"{text[:300]}"))
    if status == 429:
        raise ApiError(redact(f"{what} quota or rate limit reached (HTTP 429): {text[:300]}"))
    if status >= 400:
        raise ApiError(redact(f"{what} returned HTTP {status}: {text[:300]}"))
    try:
        return json.loads(text) if text.strip() else {}
    except ValueError:
        raise ApiError(redact(f"{what} returned a non-JSON response (HTTP {status})"))


# --- credentials ------------------------------------------------------------------------------------

def config_dir() -> Path:
    return Path(os.environ.get("SEARCH_MEASUREMENT_CONFIG_DIR") or "~/.config/search-measurement").expanduser()


def state_dir() -> Path:
    return Path(os.environ.get("SEARCH_MEASUREMENT_STATE_DIR") or "~/.cache/search-measurement").expanduser()


def inside_git_worktree(path: Path) -> bool:
    for parent in path.resolve().parents:
        if (parent / ".git").exists():
            return True
    return False


def read_secret_file(path: Path) -> str:
    if not path.is_file():
        raise NoAccess(f"credential file not found: {path}")
    if os.name == "posix":
        mode = path.stat().st_mode & 0o777
        if mode & 0o077:
            raise NoAccess(f"refusing {path}: readable by group or others (mode {mode:o}); run: chmod 600 {path}")
    if inside_git_worktree(path):
        raise NoAccess(f"refusing {path}: it is inside a git work tree; move it outside the repository, "
                       f"for example to {config_dir()}")
    text = path.read_text(encoding="utf-8").strip()
    register_secret(text)
    return text


def secret_from(env_value: str, env_file: str, default_name: str, label: str) -> str:
    value = os.environ.get(env_value)
    if value:
        register_secret(value)
        return value
    path = Path(os.environ.get(env_file) or (config_dir() / default_name)).expanduser()
    if not path.exists():
        raise NoAccess(f"no {label} credential: set {env_value}, or put the key in {path} (mode 600) "
                       f"or point {env_file} to it")
    return read_secret_file(path)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def jwt_parts(client_email: str, now: int, key_id: str | None = None,
              scope: str = GSC_SCOPE, lifetime: int = JWT_MAX_LIFETIME) -> tuple[dict, dict]:
    if lifetime > JWT_MAX_LIFETIME or lifetime <= 0:
        raise UsageError("JWT lifetime must be between 1 and 3600 seconds")
    header = {"alg": "RS256", "typ": "JWT"}
    if key_id:
        header["kid"] = key_id
    claims = {"iss": client_email, "scope": scope, "aud": TOKEN_URL, "iat": now, "exp": now + lifetime}
    return header, claims


def signing_input(header: dict, claims: dict) -> bytes:
    enc = lambda o: b64url(json.dumps(o, separators=(",", ":")).encode())  # noqa: E731
    return f"{enc(header)}.{enc(claims)}".encode()


def sign_rs256(data: bytes, private_key_pem: str) -> str:
    """RS256 via openssl; the key goes through a pipe, never to disk or argv."""
    r, w = os.pipe()
    try:
        os.write(w, private_key_pem.encode())
        os.close(w)
        w = -1
        proc = subprocess.run(["openssl", "dgst", "-sha256", "-sign", f"/dev/fd/{r}"], input=data,
                              capture_output=True, pass_fds=(r,), timeout=30)
    except FileNotFoundError:
        raise NoAccess("openssl not found; install it or set GSC_ACCESS_TOKEN to a ready access token")
    finally:
        if w != -1:
            os.close(w)
        os.close(r)
    if proc.returncode != 0 or not proc.stdout:
        raise NoAccess(f"openssl could not sign the token request (exit {proc.returncode}); check the key file")
    return b64url(proc.stdout)


def gsc_token() -> str:
    tok = os.environ.get("GSC_ACCESS_TOKEN")
    if tok:
        register_secret(tok)
        return tok
    default = config_dir() / "gsc-service-account.json"
    path = Path(os.environ.get("GSC_SERVICE_ACCOUNT_FILE") or default).expanduser()
    if not path.exists():
        raise NoAccess(f"no Google credential: set GSC_ACCESS_TOKEN, or put a service-account key in {path} "
                       "(mode 600) or point GSC_SERVICE_ACCOUNT_FILE to it")
    try:
        info = json.loads(read_secret_file(path))
        email, key = info["client_email"], info["private_key"]
    except (ValueError, KeyError, TypeError):
        raise NoAccess(f"{path} is not a service-account JSON key (needs client_email and private_key)")
    register_secret(key)
    register_secret(info.get("private_key_id"))
    header, claims = jwt_parts(email, int(time.time()), info.get("private_key_id"))
    unsigned = signing_input(header, claims)
    assertion = unsigned.decode() + "." + sign_rs256(unsigned, key)
    register_secret(assertion)
    data = http_json("POST", TOKEN_URL, form={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                                              "assertion": assertion}, what="Google token endpoint")
    token = data.get("access_token")
    if not token:
        raise NoAccess("Google token endpoint returned no access token")
    register_secret(token)
    return token


# --- Search Console ----------------------------------------------------------------------------------

def parse_filters(specs: list[str]) -> list[dict]:
    out = []
    for spec in specs or []:
        parts = spec.split(":", 2)
        if len(parts) != 3:
            raise UsageError(f"filter must be dimension:operator:expression, got {spec!r}")
        dim, op, expr = parts
        if dim not in {"query", "page", "country", "device", "searchAppearance"}:
            raise UsageError(f"filter dimension {dim!r} not allowed")
        if op not in GSC_OPERATORS:
            raise UsageError(f"filter operator {op!r} not one of {sorted(GSC_OPERATORS)}")
        out.append({"dimension": dim, "operator": op, "expression": expr})
    return out


def gsc_query(site: str, start: dt.date, end: dt.date, dims: list[str], token: str, *, search_type: str = "web",
              filters: list[dict] | None = None, data_state: str = "final", max_rows: int = 0) -> dict:
    bad = [d for d in dims if d not in GSC_DIMS]
    if bad:
        raise UsageError(f"unknown dimension(s): {bad}")
    if search_type not in GSC_TYPES:
        raise UsageError(f"unknown search type {search_type!r}")
    url = f"{GSC_BASE}/sites/{urllib.parse.quote(site, safe='')}/searchAnalytics/query"
    rows: list[dict] = []
    calls, start_row, agg = 0, 0, None
    while True:
        limit = GSC_PAGE if not max_rows else min(GSC_PAGE, max_rows - len(rows))
        if limit <= 0:
            break
        body = {"startDate": start.isoformat(), "endDate": end.isoformat(), "dimensions": dims,
                "type": search_type, "dataState": data_state, "rowLimit": limit, "startRow": start_row}
        if filters:
            body["dimensionFilterGroups"] = [{"groupType": "and", "filters": filters}]
        data = http_json("POST", url, headers={"Authorization": f"Bearer {token}"}, body=body,
                         what="Search Console")
        calls += 1
        agg = data.get("responseAggregationType", agg)
        batch = data.get("rows") or []
        for r in batch:
            row = dict(zip(dims, r.get("keys", [])))
            row.update(clicks=r.get("clicks", 0), impressions=r.get("impressions", 0),
                       ctr=r.get("ctr", 0.0), position=r.get("position", 0.0))
            rows.append(row)
        if len(batch) < limit:
            break
        start_row += len(batch)
    return {"rows": rows, "calls": calls, "aggregation": agg,
            "params": {"site": site, "start": start.isoformat(), "end": end.isoformat(), "dimensions": dims,
                       "type": search_type, "dataState": data_state, "filters": filters or []}}


def url_in_property(url: str, site: str) -> bool:
    if site.startswith("sc-domain:"):
        host = (urllib.parse.urlsplit(url).hostname or "").lower()
        dom = site.split(":", 1)[1].lower()
        return host == dom or host.endswith("." + dom)
    return url.startswith(site)


def _ledger_load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def inspect_urls(site: str, urls: list[str], token: str, *, max_n: int = 100, sleep=time.sleep,
                 ledger_path: Path | None = None, today: dt.date | None = None) -> dict:
    if max_n < 1 or max_n > INSPECT_PER_DAY:
        raise UsageError(f"--max must be between 1 and {INSPECT_PER_DAY}")
    outside = [u for u in urls if not url_in_property(u, site)]
    if outside:
        raise UsageError(f"{len(outside)} URL(s) are outside the property {site}, e.g. {outside[0]}")
    ledger_path = ledger_path or (state_dir() / "inspect-usage.json")
    day = (today or pacific_today()).isoformat()
    ledger = _ledger_load(ledger_path)
    used = int(ledger.get(site, {}).get(day, 0))
    budget = min(max_n, INSPECT_PER_DAY - used)
    if budget <= 0:
        raise ApiError(f"URL Inspection daily quota for {site} used up by this tool today ({used} of "
                       f"{INSPECT_PER_DAY}); try again after midnight Pacific Time")
    interval = 60.0 / INSPECT_PER_MIN + 0.01
    results, done, stopped = [], 0, None
    for i, u in enumerate(urls[:budget]):
        if i:
            sleep(interval)
        try:
            data = http_json("POST", INSPECT_URL, headers={"Authorization": f"Bearer {token}"},
                             body={"inspectionUrl": u, "siteUrl": site}, what="URL Inspection")
        except ApiError as e:
            stopped = str(e)
            break
        done += 1
        st = (data.get("inspectionResult") or {}).get("indexStatusResult") or {}
        g, uc = st.get("googleCanonical"), st.get("userCanonical")
        results.append({
            "url": u, "verdict": st.get("verdict"), "coverageState": st.get("coverageState"),
            "indexingState": st.get("indexingState"), "robotsTxtState": st.get("robotsTxtState"),
            "pageFetchState": st.get("pageFetchState"), "lastCrawlTime": st.get("lastCrawlTime"),
            "googleCanonical": g, "userCanonical": uc, "crawledAs": st.get("crawledAs"),
            "canonical_mismatch": bool(g and uc and g != uc),
        })
    ledger.setdefault(site, {})[day] = used + done
    ledger[site] = {k: v for k, v in ledger[site].items() if k >= (dt.date.fromisoformat(day)
                                                                   - dt.timedelta(days=7)).isoformat()}
    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        ledger_path.write_text(json.dumps(ledger, indent=1), encoding="utf-8")
    except OSError:
        pass
    return {"site": site, "inspected": done, "not_inspected": urls[done:], "quota_used_today": used + done,
            "quota_per_day": INSPECT_PER_DAY, "stopped": stopped, "results": results}


def gsc_sitemaps(site: str, token: str) -> dict:
    url = f"{GSC_BASE}/sites/{urllib.parse.quote(site, safe='')}/sitemaps"
    data = http_json("GET", url, headers={"Authorization": f"Bearer {token}"}, what="Search Console sitemaps")
    out = []
    for s in data.get("sitemap") or []:
        out.append({k: s.get(k) for k in ("path", "type", "isSitemapsIndex", "isPending", "lastSubmitted",
                                          "lastDownloaded", "errors", "warnings")}
                   | {"submitted": sum(int(c.get("submitted") or 0) for c in s.get("contents") or [])})
    return {"site": site, "sitemaps": out,
            "note": "contents[].indexed is deprecated by Google; read indexing from URL Inspection"}


# --- Bing ----------------------------------------------------------------------------------------------

_MS_DATE = re.compile(r"/Date\((-?\d+)([+-]\d{4})?\)/")


def bing_date(value: str) -> str:
    m = _MS_DATE.fullmatch(value or "")
    if not m:
        return value
    ms, off = int(m.group(1)), m.group(2) or "+0000"
    sign = -1 if off[0] == "-" else 1
    tz = dt.timezone(sign * dt.timedelta(hours=int(off[1:3]), minutes=int(off[3:5])))
    return dt.datetime.fromtimestamp(ms / 1000, tz).date().isoformat()


def bing_stats(site: str, method: str, key: str, start: dt.date | None = None, end: dt.date | None = None) -> dict:
    if method not in BING_METHODS:
        raise UsageError(f"--method must be one of {sorted(BING_METHODS)}")
    url = BING_BASE + method + "?" + urllib.parse.urlencode({"siteUrl": site, "apikey": key})
    try:
        data = http_json("GET", url, what="Bing Webmaster API")
    except ApiError as e:
        if "InvalidApiKey" in str(e):
            raise NoAccess("Bing Webmaster API rejected the API key")
        raise
    rows = []
    for item in data.get("d") or []:
        day = bing_date(item.get("Date", ""))
        if start and end and not (start.isoformat() <= day <= end.isoformat()):
            continue
        rows.append({"date": day, "key": item.get("Query"), "clicks": item.get("Clicks", 0),
                     "impressions": item.get("Impressions", 0),
                     "avg_impression_position": item.get("AvgImpressionPosition"),
                     "avg_click_position": item.get("AvgClickPosition")})
    return {"rows": rows, "params": {"site": site, "method": method,
                                     "start": start.isoformat() if start else None,
                                     "end": end.isoformat() if end else None},
            "note": "Bing updates these stats weekly; key is the query, or the page URL for GetPageStats"}


# --- Plausible -----------------------------------------------------------------------------------------

def plausible_query(site_id: str, metrics: list[str], dims: list[str], date_range, key: str, *,
                    filters: list | None = None, base: str | None = None, max_rows: int = 0) -> dict:
    base = (base or os.environ.get("PLAUSIBLE_BASE_URL") or PLAUSIBLE_DEFAULT).rstrip("/")
    if not base.startswith("https://"):
        raise UsageError("PLAUSIBLE_BASE_URL must use https")
    url = base + "/api/v2/query"
    rows, offset, calls = [], 0, 0
    while True:
        limit = PLAUSIBLE_PAGE if not max_rows else min(PLAUSIBLE_PAGE, max_rows - len(rows))
        if limit <= 0:
            break
        body = {"site_id": site_id, "metrics": metrics, "date_range": date_range, "dimensions": dims,
                "pagination": {"limit": limit, "offset": offset}}
        if filters:
            body["filters"] = filters
        try:
            data = http_json("POST", url, headers={"Authorization": f"Bearer {key}"}, body=body,
                             what="Plausible Stats API")
        except NoAccess as e:
            if "rejected" not in str(e):
                raise
            raise NoAccess(f"{e}. On Plausible Cloud the Stats API needs the Business plan, and a key reaches "
                           "only the sites of the team it was created in")
        calls += 1
        batch = data.get("results") or []
        for r in batch:
            row = dict(zip(dims, r.get("dimensions", [])))
            row.update(zip(metrics, r.get("metrics", [])))
            rows.append(row)
        if len(batch) < limit or not dims:
            break
        offset += len(batch)
    return {"rows": rows, "calls": calls,
            "params": {"site_id": site_id, "metrics": metrics, "dimensions": dims, "date_range": date_range,
                       "filters": filters or []}}


# --- compare -------------------------------------------------------------------------------------------

def _wmean(pairs) -> float | None:
    imp = sum(i for i, _ in pairs)
    return round(sum(i * p for i, p in pairs) / imp, 2) if imp else None


def summarize(rows: list[dict]) -> dict:
    clicks = sum(r.get("clicks", 0) for r in rows)
    imps = sum(r.get("impressions", 0) for r in rows)
    return {"clicks": clicks, "impressions": imps, "ctr": round(clicks / imps, 4) if imps else None,
            "position": _wmean([(r.get("impressions", 0), r.get("position", 0.0)) for r in rows])}


def pct(a: float, b: float) -> float | None:
    return round((b - a) / a * 100, 1) if a else None


def position_mix(before: list[dict], after: list[dict], key: str = "query") -> dict:
    """Split the change in average position into same-query movement and query-mix change.

    Average position is weighted by impressions, so queries that start (or stop) showing the site at low
    positions move the mean without any ranking change. Common queries are compared with fixed weights.
    """
    b = {}
    for r in before:
        e = b.setdefault(r[key], [0, 0.0])
        e[0] += r["impressions"]
        e[1] += r["impressions"] * r["position"]
    a = {}
    for r in after:
        e = a.setdefault(r[key], [0, 0.0])
        e[0] += r["impressions"]
        e[1] += r["impressions"] * r["position"]
    pos = lambda e: e[1] / e[0] if e[0] else 0.0  # noqa: E731
    all_b = _wmean([(e[0], pos(e)) for e in b.values()])
    all_a = _wmean([(e[0], pos(e)) for e in a.values()])
    common = [q for q in a if q in b and a[q][0] and b[q][0]]
    w = {q: a[q][0] + b[q][0] for q in common}
    com_b = _wmean([(w[q], pos(b[q])) for q in common])
    com_a = _wmean([(w[q], pos(a[q])) for q in common])
    new = [q for q in a if q not in b]
    lost = [q for q in b if q not in a]
    a_imp = sum(e[0] for e in a.values()) or 0
    b_imp = sum(e[0] for e in b.values()) or 0
    out = {
        "position_all": {"before": all_b, "after": all_a,
                         "delta": round(all_a - all_b, 2) if None not in (all_a, all_b) else None},
        "position_same_queries": {"before": com_b, "after": com_a, "queries": len(common),
                                  "delta": round(com_a - com_b, 2) if None not in (com_a, com_b) else None},
        "new_queries": len(new),
        "new_query_impression_share": round(sum(a[q][0] for q in new) / a_imp, 3) if a_imp else None,
        "new_query_position": _wmean([(a[q][0], pos(a[q])) for q in new]),
        "lost_queries": len(lost),
        "lost_query_impression_share": round(sum(b[q][0] for q in lost) / b_imp, 3) if b_imp else None,
        "mix_shift": False,
    }
    d_all, d_com = out["position_all"]["delta"], out["position_same_queries"]["delta"]
    if d_all is not None and d_com is not None and abs(d_all) >= POSITION_EPSILON:
        opposite = (d_all > 0) != (d_com > 0) or abs(d_com) < POSITION_EPSILON
        if opposite:
            out["mix_shift"] = True
            out["explanation"] = (
                f"Average position moved {d_all:+.2f} overall but {d_com:+.2f} on the {len(common)} queries present "
                "in both windows (higher is worse). The overall move comes from queries that appeared or "
                "disappeared, not from ranking changes; read per query.")
    return out


def _by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for r in rows:
        out.setdefault(r.get(key), []).append(r)
    return out


def _gsc_rows(snap: dict, dims: str) -> list[dict] | None:
    src = (snap.get("sources") or {}).get("gsc") or {}
    part = src.get(dims)
    return part.get("rows") if isinstance(part, dict) else None


def _load_list(path: str | None) -> set[str]:
    if not path:
        return set()
    try:
        return {ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.startswith("#")}
    except OSError as e:
        raise UsageError(f"cannot read {path}: {e.strerror}")


def compare_snapshots(before: dict, after: dict, *, by: str = "page", min_impressions: int = DEFAULT_MIN_IMPRESSIONS,
                      treated: set[str] | None = None, control: set[str] | None = None, top: int = 50,
                      change_date: str | None = None) -> dict:
    if by not in ("page", "query"):
        raise UsageError("--by must be page or query")
    warnings, blocking = [], []
    wb, wa = (before.get("meta") or {}).get("window") or {}, (after.get("meta") or {}).get("window") or {}
    if wb.get("days") != wa.get("days"):
        blocking.append(f"unequal windows: {wb.get('days')} vs {wa.get('days')} days")
    elif not wb.get("whole_weeks") and wb.get("start_weekday") != wa.get("start_weekday"):
        blocking.append("windows are not whole weeks and start on different weekdays")
    if (wa.get("days") or 0) < MIN_CLAIM_DAYS:
        blocking.append(f"after-window is {wa.get('days')} days; no effect is claimed from under {MIN_CLAIM_DAYS}")
    if wb.get("inside_lag") or wa.get("inside_lag"):
        blocking.append("a window ends inside the reporting lag; its last days were incomplete when fetched")
    ds_b = (before.get("meta") or {}).get("data_state")
    ds_a = (after.get("meta") or {}).get("data_state")
    if ds_b != ds_a or ds_a != "final":
        warnings.append(f"data state before={ds_b}, after={ds_a}; compare final with final")
    if change_date and wa.get("start") and wa["start"] < change_date:
        blocking.append(f"after-window starts {wa['start']}, before the change on {change_date}")
    if wb.get("end") and wa.get("start") and wa["start"] <= wb["end"]:
        blocking.append("the windows overlap")

    rows_b, rows_a = _gsc_rows(before, by), _gsc_rows(after, by)
    pq_b, pq_a = _gsc_rows(before, "page_query") or [], _gsc_rows(after, "page_query") or []
    if rows_b is None or rows_a is None:
        if not (pq_b and pq_a):
            raise UsageError(f"snapshots hold no Search Console rows by {by}")
        rows_b, rows_a = pq_b, pq_a
        warnings.append(f"no '{by}' rows; totals summed from page_query rows, which omit anonymized queries")
    gb, ga = _by(rows_b, by), _by(rows_a, by)
    pq_gb, pq_ga = _by(pq_b, "page"), _by(pq_a, "page")

    items = []
    for k in set(gb) | set(ga):
        sb, sa = summarize(gb.get(k, [])), summarize(ga.get(k, []))
        item = {by: k, "before": sb, "after": sa, "delta": {
            "clicks": sa["clicks"] - sb["clicks"], "clicks_pct": pct(sb["clicks"], sa["clicks"]),
            "impressions": sa["impressions"] - sb["impressions"],
            "impressions_pct": pct(sb["impressions"], sa["impressions"]),
            "ctr_pp": round((sa["ctr"] - sb["ctr"]) * 100, 2) if None not in (sa["ctr"], sb["ctr"]) else None,
            "position": round(sa["position"] - sb["position"], 2)
            if None not in (sa["position"], sb["position"]) else None}, "flags": []}
        if k not in gb:
            item["flags"].append("new")
        if k not in ga:
            item["flags"].append("lost")
        if min(sb["impressions"], sa["impressions"]) < min_impressions:
            item["flags"].append("insufficient_data")
        if by == "page" and pq_gb.get(k) and pq_ga.get(k):
            mix = position_mix(pq_gb[k], pq_ga[k])
            if mix["mix_shift"]:
                item["flags"].append("position_mix_shift")
                item["position_mix"] = mix
        items.append(item)
    items.sort(key=lambda i: abs(i["delta"]["clicks"]), reverse=True)

    site = {"before": summarize(rows_b), "after": summarize(rows_a)}
    if by == "page":
        site["totals_note"] = "summed over pages (by-page aggregation counts one impression per page)"
    if pq_b and pq_a:
        site["position_mix"] = position_mix(pq_b, pq_a)
        if site["position_mix"]["mix_shift"]:
            warnings.append("site average position is distorted by query mix: " + site["position_mix"]["explanation"])

    did = None
    if treated:
        if not control:
            blocking.append("no control group: give --control with comparable untouched pages")
        tb = summarize([r for r in rows_b if r.get(by) in treated])
        ta = summarize([r for r in rows_a if r.get(by) in treated])
        did = {"treated": {"keys": len(treated), "before": tb, "after": ta,
                           "clicks_pct": pct(tb["clicks"], ta["clicks"]),
                           "impressions_pct": pct(tb["impressions"], ta["impressions"])}}
        if control:
            cb = summarize([r for r in rows_b if r.get(by) in control])
            ca = summarize([r for r in rows_a if r.get(by) in control])
            did["control"] = {"keys": len(control), "before": cb, "after": ca,
                              "clicks_pct": pct(cb["clicks"], ca["clicks"]),
                              "impressions_pct": pct(cb["impressions"], ca["impressions"])}
            for m in ("clicks_pct", "impressions_pct"):
                t, c = did["treated"][m], did["control"][m]
                did[f"difference_in_{m}_points"] = round(t - c, 1) if None not in (t, c) else None
            if min(tb["impressions"], ta["impressions"]) < min_impressions:
                blocking.append("treated group below the impression floor")
            if min(cb["impressions"], ca["impressions"]) < min_impressions:
                blocking.append("control group below the impression floor")
            if treated & control:
                blocking.append("treated and control groups overlap")
    else:
        blocking.append("no --treated set: this is a before/after readout, not an effect estimate")

    return {"by": by, "windows": {"before": wb, "after": wa}, "claimable": not blocking,
            "blocking": blocking, "warnings": warnings, "site": site, "difference_in_differences": did,
            "min_impressions": min_impressions, "items": items[:top] if top else items,
            "items_total": len(items)}


# --- snapshot ------------------------------------------------------------------------------------------

def build_snapshot(label: str, start: dt.date, end: dt.date, *, gsc_site=None, bing_site=None, plausible_site=None,
                   data_state="final", max_rows=100000, lag=GSC_LAG_DAYS) -> dict:
    sources, skipped = {}, {}
    requested = [s for s in (gsc_site, bing_site, plausible_site) if s]
    if not requested:
        raise UsageError("name at least one of --gsc-site, --bing-site, --plausible-site")
    if gsc_site:
        try:
            tok = gsc_token()
            sources["gsc"] = {name: gsc_query(gsc_site, start, end, dims, tok, data_state=data_state,
                                              max_rows=max_rows)
                              for name, dims in (("page", ["page"]), ("query", ["query"]),
                                                 ("page_query", ["page", "query"]))}
        except NoAccess as e:
            skipped["gsc"] = str(e)
    if bing_site:
        try:
            key = secret_from("BING_WEBMASTER_API_KEY", "BING_WEBMASTER_API_KEY_FILE", "bing-api-key", "Bing")
            sources["bing"] = {"page": bing_stats(bing_site, "GetPageStats", key, start, end),
                               "query": bing_stats(bing_site, "GetQueryStats", key, start, end)}
        except NoAccess as e:
            skipped["bing"] = str(e)
    if plausible_site:
        try:
            key = secret_from("PLAUSIBLE_API_KEY", "PLAUSIBLE_API_KEY_FILE", "plausible-api-key", "Plausible")
            rng = [start.isoformat(), end.isoformat()]
            sources["plausible"] = {
                "entry_page": plausible_query(plausible_site, ["visitors", "visits", "bounce_rate"],
                                              ["visit:entry_page"], rng, key),
                "channel": plausible_query(plausible_site, ["visitors", "visits"], ["visit:channel"], rng, key),
                "utm_source": plausible_query(plausible_site, ["visitors"], ["visit:utm_source"], rng, key),
                "goals": plausible_query(plausible_site, ["visitors", "events"], ["event:goal"], rng, key),
            }
        except NoAccess as e:
            skipped["plausible"] = str(e)
    if not sources:
        raise NoAccess("no source could be read: " + "; ".join(f"{k}: {v}" for k, v in skipped.items()))
    return {"meta": {"label": label, "created_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                     "tool": TOOL, "window": window_info(start, end, lag=lag), "data_state": data_state,
                     "timezone": "America/Los_Angeles (Search Console dates)", "skipped": skipped},
            "sources": sources}


def write_snapshot(snap: dict, out_dir: Path, force: bool = False) -> Path:
    text = json.dumps(snap, indent=1, ensure_ascii=False, sort_keys=True)
    if contains_registered_secret(text):
        raise CheckFailed("a credential would have been written to the snapshot; nothing written")
    slug = re.sub(r"[^a-z0-9-]+", "-", snap["meta"]["label"].lower()).strip("-") or "snapshot"
    path = out_dir / f"{snap['meta']['created_at'][:10]}-{slug}.json"
    if path.exists() and not force:
        raise UsageError(f"{path} exists; choose another --label or pass --force")
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(text + "\n", encoding="utf-8")
    return path


def load_json(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as e:
        raise UsageError(f"cannot read {path}: {e.strerror}")
    except ValueError:
        raise UsageError(f"{path} is not JSON")


# --- self-test -----------------------------------------------------------------------------------------

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class _FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, data, timeout):
        self.calls.append({"method": method, "url": url, "headers": headers,
                           "body": json.loads(data) if data and headers.get("Content-Type") == "application/json"
                           else data})
        r = self.responses.pop(0)
        if isinstance(r, Exception):
            raise r
        status, payload = r
        return status, payload if isinstance(payload, bytes) else json.dumps(payload).encode()


def _gsc_page(n, offset=0):
    return 200, {"rows": [{"keys": [f"q{offset + i}"], "clicks": 1, "impressions": 10, "ctr": 0.1, "position": 5.0}
                          for i in range(n)], "responseAggregationType": "byProperty"}


def self_test() -> int:
    global TRANSPORT
    import tempfile
    fails: list[str] = []
    check = lambda ok, msg: ok or fails.append(msg)  # noqa: E731
    saved = TRANSPORT
    try:
        # 1. paging past 25,000 rows, stopping on a short page and on an empty page
        fake = _FakeTransport([_gsc_page(25000), _gsc_page(25000, 25000), _gsc_page(1200, 50000)])
        TRANSPORT = fake
        res = gsc_query("sc-domain:example.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), ["query"], "tok-test-1")
        check(len(res["rows"]) == 51200, f"paging: expected 51200 rows, got {len(res['rows'])}")
        check([c["body"]["startRow"] for c in fake.calls] == [0, 25000, 50000],
              f"paging: startRow sequence {[c['body']['startRow'] for c in fake.calls]}")
        check(all(c["body"]["rowLimit"] == 25000 for c in fake.calls), "paging: rowLimit must be 25000")
        check("sc-domain%3Aexample.com" in fake.calls[0]["url"], "paging: site must be URL-encoded in the path")
        fake = _FakeTransport([_gsc_page(25000), (200, {})])
        TRANSPORT = fake
        res = gsc_query("sc-domain:example.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), ["query"], "tok-test-1")
        check(len(fake.calls) == 2 and len(res["rows"]) == 25000, "paging: must stop on an empty page")
        fake = _FakeTransport([_gsc_page(25000), _gsc_page(5000, 25000)])
        TRANSPORT = fake
        res = gsc_query("sc-domain:example.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), ["query"], "tok-test-1",
                        max_rows=30000)
        check(len(res["rows"]) == 30000 and fake.calls[1]["body"]["rowLimit"] == 5000,
              "paging: --max-rows must cap the last request")

        # 2. date windows respect the lag and keep weekdays aligned
        today = dt.date(2026, 11, 3)
        s, e = lagged_window(28, 3, today)
        check(e == dt.date(2026, 10, 31) and (e - s).days + 1 == 28, f"window: got {s}..{e}")
        ps, pe = prior_window(s, e)
        check(pe == s - dt.timedelta(days=1) and ps.weekday() == s.weekday() and (pe - ps) == (e - s),
              f"prior window: got {ps}..{pe}")
        ys, ye = prior_window(s, e, year_ago=True)
        check(ys.weekday() == s.weekday() and (ye - ys) == (e - s), "year-ago window must keep weekdays")
        check(window_info(s, e, today)["inside_lag"] is False, "window ending at today-3 is outside the lag")
        check(window_info(s, today, today)["inside_lag"] is True, "window ending today is inside the lag")

        # 3. JWT claims without signing
        header, claims = jwt_parts("reader@project.iam.example.com", 1_800_000_000, "kid-1")
        check(header == {"alg": "RS256", "typ": "JWT", "kid": "kid-1"}, f"jwt header {header}")
        check(claims["scope"] == GSC_SCOPE and claims["scope"].endswith(".readonly"), "jwt scope must be read-only")
        check(claims["aud"] == TOKEN_URL and claims["iss"] == "reader@project.iam.example.com", "jwt aud/iss")
        check(claims["exp"] - claims["iat"] == 3600, "jwt lifetime must be 3600 s")
        si = signing_input(header, claims).decode()
        check(si.count(".") == 1 and "=" not in si, "signing input must be two unpadded base64url parts")
        decoded = json.loads(base64.urlsafe_b64decode(si.split(".")[1] + "=="))
        check(decoded == claims, "signing input must encode the claims")
        try:
            jwt_parts("x@example.com", 0, lifetime=7200)
            fails.append("jwt lifetime over 3600 s must be refused")
        except UsageError:
            pass

        # 4. secrets are redacted from errors and kept out of snapshots
        key = "bk_test_key_value_one"
        register_secret(key)
        fake = _FakeTransport([(400, {"ErrorCode": 3, "Message": "InvalidApiKey", "echo": f"apikey={key}"})])
        TRANSPORT = fake
        try:
            bing_stats("https://www.example.com/", "GetQueryStats", key)
            fails.append("bing: invalid key must raise")
        except NoAccess as e:
            check(key not in str(e), "bing: key leaked into the error")
        fake = _FakeTransport([urllib.error.URLError(f"connection refused for https://x/?apikey={key}")])
        TRANSPORT = fake
        try:
            bing_stats("https://www.example.com/", "GetQueryStats", key)
            fails.append("network error must raise NoAccess")
        except NoAccess as e:
            check(key not in str(e) and NoAccess.code == 3, "network error leaked the key or wrong exit code")
        check(key not in redact(f"upstream said: unknown key {key}."),
              "a registered secret must be redacted anywhere")
        pem = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASC\n-----END PRIVATE KEY-----\n"
        msg = redact(json.dumps({"private_key": pem, "access_token": "ya29.a0AfB_test"}) + " Bearer ya29.a0AfB_test")
        check("MIIEvQ" not in msg and "a0AfB_test" not in msg, f"redaction missed a key or token: {msg}")
        fake = _FakeTransport([(500, {"error": {"message": "Bearer tok-secret-123456 bad"}})])
        TRANSPORT = fake
        register_secret("tok-secret-123456")
        try:
            gsc_query("sc-domain:example.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), ["page"],
                      "tok-secret-123456")
            fails.append("HTTP 500 must raise ApiError")
        except ApiError as e:
            check("tok-secret-123456" not in str(e), "token leaked into an API error")
        snap = {"meta": {"label": "leak", "created_at": "2026-11-03T00:00:00+00:00"}, "sources": {"x": key}}
        with tempfile.TemporaryDirectory() as d:
            try:
                write_snapshot(snap, Path(d))
                fails.append("snapshot containing a credential must be refused")
            except CheckFailed:
                check(not any(Path(d).iterdir()), "refused snapshot must not leave a file")

        # 5. key files: mode 600 outside a repo only; missing credentials exit 3
        with tempfile.TemporaryDirectory() as d:
            kf = Path(d) / "plausible-api-key"
            kf.write_text("pk_test_key_value_two\n")
            os.chmod(kf, 0o644)
            try:
                read_secret_file(kf)
                fails.append("a group/world-readable key file must be refused")
            except NoAccess as e:
                check("pk_test_key_value_two" not in str(e), "refusal message leaked the key")
            os.chmod(kf, 0o600)
            try:
                check(read_secret_file(kf) == "pk_test_key_value_two", "mode 600 key file must be read")
            except NoAccess as e:
                fails.append(f"mode 600 key file outside a repo was refused: {e}")
            (Path(d) / "repo" / ".git").mkdir(parents=True)
            kf2 = Path(d) / "repo" / "key"
            kf2.write_text("pk_test_repo_123456")
            os.chmod(kf2, 0o600)
            try:
                read_secret_file(kf2)
                fails.append("a key file inside a git work tree must be refused")
            except NoAccess:
                pass
            env_backup = {k: os.environ.pop(k, None) for k in ("PLAUSIBLE_API_KEY", "PLAUSIBLE_API_KEY_FILE",
                                                                "SEARCH_MEASUREMENT_CONFIG_DIR")}
            os.environ["SEARCH_MEASUREMENT_CONFIG_DIR"] = str(Path(d) / "empty")
            try:
                secret_from("PLAUSIBLE_API_KEY", "PLAUSIBLE_API_KEY_FILE", "plausible-api-key", "Plausible")
                fails.append("missing credentials must raise NoAccess (exit 3)")
            except NoAccess:
                pass
            finally:
                os.environ.pop("SEARCH_MEASUREMENT_CONFIG_DIR", None)
                for k, v in env_backup.items():
                    if v is not None:
                        os.environ[k] = v

        # 6. compare maths, position-mix trap, difference in differences
        before = json.loads((FIXTURES / "snapshot-before.json").read_text(encoding="utf-8"))
        after = json.loads((FIXTURES / "snapshot-after.json").read_text(encoding="utf-8"))
        rep = compare_snapshots(before, after, by="page", min_impressions=100,
                                treated={"https://www.example.com/pricing"},
                                control={"https://www.example.com/features"})
        items = {i["page"]: i for i in rep["items"]}
        pr = items.get("https://www.example.com/pricing")
        check(pr is not None and pr["before"]["clicks"] == 40 and pr["after"]["clicks"] == 60,
              f"compare: pricing clicks {pr and (pr['before']['clicks'], pr['after']['clicks'])}")
        check(pr and pr["delta"]["clicks_pct"] == 50.0, "compare: clicks_pct must be +50.0")
        check(pr and pr["before"]["ctr"] == 0.04 and pr["after"]["ctr"] == 0.04, "compare: CTR = clicks/impressions")
        check(pr and pr["after"]["position"] == 7.6, f"compare: after position {pr and pr['after']['position']}")
        check(pr and "position_mix_shift" in pr["flags"], "compare: pricing must be flagged as a position-mix shift")
        mix = pr and pr.get("position_mix")
        check(bool(mix) and mix["position_all"]["delta"] > 0 > mix["position_same_queries"]["delta"],
              "compare: mix trap needs worse overall and better same-query position")
        check(mix and mix["position_same_queries"]["before"] == 6.0 and mix["position_same_queries"]["after"] == 5.0,
              "compare: same-query positions must use fixed impression weights")
        check(rep["site"]["before"]["position"] == 4.83, f"compare: site position must be impression-weighted: "
                                                         f"{rep['site']['before']['position']}")
        fe = items.get("https://www.example.com/features")
        check(fe and "position_mix_shift" not in fe["flags"], "compare: a genuine slide must not be called mix")
        check(fe and fe["after"]["position"] > fe["before"]["position"], "compare: features got worse")
        bl = items.get("https://www.example.com/blog/tiny")
        check(bl and "insufficient_data" in bl["flags"], "compare: low-impression page must be insufficient_data")
        did = rep["difference_in_differences"]
        check(did and did["difference_in_clicks_pct_points"] == 50.0 - (-10.0),
              f"compare: diff-in-diff {did and did.get('difference_in_clicks_pct_points')}")
        check(rep["claimable"] is True,
              f"compare: equal 28-day windows with control are claimable: {rep['blocking']}")
        short = json.loads(json.dumps(after))
        short["meta"]["window"].update(days=7, end="2026-10-11", whole_weeks=True)
        rep2 = compare_snapshots(before, short, by="page", treated={"https://www.example.com/pricing"},
                                 control={"https://www.example.com/features"})
        check(rep2["claimable"] is False and any("unequal" in b for b in rep2["blocking"]),
              "compare: a 7-day after-window against 28 days must block a claim")
        rep3 = compare_snapshots(before, after, by="page", treated={"https://www.example.com/pricing"})
        check(rep3["claimable"] is False and any("control" in b for b in rep3["blocking"]),
              "compare: no control group must block a claim")
        rep4 = compare_snapshots(before, after, by="page", change_date="2026-10-20",
                                 treated={"https://www.example.com/pricing"},
                                 control={"https://www.example.com/features"})
        check(any("before the change" in b for b in rep4["blocking"]),
              "compare: after-window starting before the change must block")

        seven_b = json.loads(json.dumps(before))
        seven_a = json.loads(json.dumps(after))
        seven_b["meta"]["window"].update(start="2026-09-28", days=7)
        seven_a["meta"]["window"].update(end="2026-10-11", days=7)
        rep5 = compare_snapshots(seven_b, seven_a, treated={"https://www.example.com/pricing"},
                                 control={"https://www.example.com/features"})
        check(any("under 28" in x for x in rep5["blocking"]), "compare: two 7-day windows must block a claim")
        lagged = json.loads(json.dumps(after))
        lagged["meta"]["window"]["inside_lag"] = True
        rep6 = compare_snapshots(before, lagged, treated={"https://www.example.com/pricing"},
                                 control={"https://www.example.com/features"})
        check(any("lag" in x for x in rep6["blocking"]), "compare: a window inside the lag must block")
        overlap = json.loads(json.dumps(after))
        overlap["meta"]["window"]["start"] = "2026-10-01"
        rep7 = compare_snapshots(before, overlap, treated={"https://www.example.com/pricing"},
                                 control={"https://www.example.com/features"})
        check(any("overlap" in x for x in rep7["blocking"]), "compare: overlapping windows must block")
        rep8 = compare_snapshots(before, after)
        check(rep8["claimable"] is False, "compare: without a treated set nothing is claimable")
        fake = _FakeTransport([(403, {"error": {"message": "User does not have sufficient permission"}})])
        TRANSPORT = fake
        try:
            gsc_query("sc-domain:example.com", dt.date(2026, 9, 1), dt.date(2026, 9, 28), ["page"], "tok-test-1")
            fails.append("HTTP 403 must raise NoAccess (exit 3)")
        except NoAccess:
            pass

        # 7. Bing dates, Plausible paging and row mapping
        check(bing_date("/Date(1316156400000-0700)/") == "2011-09-16", "bing: /Date()/ parsing")
        check(bing_date("/Date(1791266400000-0700)/") == "2026-10-05", "bing: date must be read in its own offset")
        fake = _FakeTransport([(200, {"d": [
            {"Date": "/Date(1791270000000-0700)/", "Query": "invoice app", "Clicks": 3, "Impressions": 40,
             "AvgImpressionPosition": 6, "AvgClickPosition": 4},
            {"Date": "/Date(1788850800000-0700)/", "Query": "old", "Clicks": 1, "Impressions": 5,
             "AvgImpressionPosition": 9, "AvgClickPosition": 9}]})])
        TRANSPORT = fake
        b = bing_stats("https://www.example.com/", "GetQueryStats", key, dt.date(2026, 10, 1), dt.date(2026, 10, 31))
        check([r["key"] for r in b["rows"]] == ["invoice app"], f"bing: window filter {b['rows']}")
        check("apikey=" in fake.calls[0]["url"] and fake.calls[0]["method"] == "GET", "bing: key goes in the query")
        page1 = {"results": [{"dimensions": [f"/p{i}"], "metrics": [i, i]} for i in range(PLAUSIBLE_PAGE)]}
        page2 = {"results": [{"dimensions": ["/last"], "metrics": [7, 9]}]}
        fake = _FakeTransport([(200, page1), (200, page2)])
        TRANSPORT = fake
        p = plausible_query("example.com", ["visitors", "visits"], ["visit:entry_page"], "28d",
                            "pk_test_key_value_two",
                            base="https://plausible.example.com")
        check(len(p["rows"]) == PLAUSIBLE_PAGE + 1 and p["rows"][-1] == {"visit:entry_page": "/last", "visitors": 7,
                                                                          "visits": 9}, "plausible: row mapping")
        check(fake.calls[1]["body"]["pagination"] == {"limit": PLAUSIBLE_PAGE, "offset": PLAUSIBLE_PAGE},
              "plausible: second page offset")
        check(fake.calls[0]["headers"]["Authorization"].startswith("Bearer "), "plausible: bearer auth")
        fake = _FakeTransport([(429, {"error": "Too many API requests"})])
        TRANSPORT = fake
        try:
            plausible_query("example.com", ["visitors"], [], "7d", "pk_test_key_value_two",
                            base="https://plausible.example.com")
            fails.append("plausible: 429 must raise ApiError")
        except ApiError as e:
            check(ApiError.code == 4 and "rate limit" in str(e), "plausible: 429 message")

        # 8. URL Inspection stays inside the daily quota and the property
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "usage.json"
            ledger.write_text(json.dumps({"sc-domain:example.com": {"2026-11-03": INSPECT_PER_DAY - 2}}))
            ok = (200, {"inspectionResult": {"indexStatusResult": {
                "verdict": "PASS", "coverageState": "Submitted and indexed",
                "googleCanonical": "https://www.example.com/a",
                "userCanonical": "https://www.example.com/b"}}})
            fake = _FakeTransport([ok, ok, ok])
            TRANSPORT = fake
            naps = []
            urls = [f"https://www.example.com/{c}" for c in "abc"]
            r = inspect_urls("sc-domain:example.com", urls, "tok-test-1", max_n=100, sleep=naps.append,
                             ledger_path=ledger, today=dt.date(2026, 11, 3))
            check(r["inspected"] == 2 and r["not_inspected"] == [urls[2]], f"inspect: quota cap {r['inspected']}")
            check(all(n >= 60 / INSPECT_PER_MIN for n in naps), "inspect: pacing under 600 per minute")
            check(r["results"][0]["canonical_mismatch"] is True, "inspect: canonical mismatch flag")
            check(json.loads(ledger.read_text())["sc-domain:example.com"]["2026-11-03"] == INSPECT_PER_DAY,
                  "inspect: ledger must record usage")
            try:
                inspect_urls("sc-domain:example.com", ["https://other.example.org/x"], "t", ledger_path=ledger)
                fails.append("inspect: URL outside the property must be refused")
            except UsageError:
                pass
    except Exception as e:  # a crash is a failure, reported like one
        fails.append(f"unexpected {e.__class__.__name__}: {e}")
    finally:
        TRANSPORT = saved

    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("measure.py self-test: ok (paging, windows and lag, JWT claims, redaction, key files, compare maths, "
          "position-mix trap, diff-in-diff, claim gates, Bing dates, Plausible paging, inspect quota)")
    return 0


# --- CLI -----------------------------------------------------------------------------------------------

def _window_args(p, days=28):
    p.add_argument("--days", type=int, default=days, help=f"window length ending --lag days ago (default {days})")
    p.add_argument("--lag", type=int, default=GSC_LAG_DAYS, help="days of reporting lag to skip (default 3)")
    p.add_argument("--start", help="YYYY-MM-DD (with --end, overrides --days)")
    p.add_argument("--end", help="YYYY-MM-DD")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="measure.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true", help="run offline checks against fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("gsc", help="Search Analytics rows (pages past 25,000 rows)")
    g.add_argument("--site", required=True, help="URL-prefix property or sc-domain:example.com")
    g.add_argument("--dims", default="page,query", help="comma list: query,page,country,device,searchAppearance,date")
    g.add_argument("--type", default="web", choices=sorted(GSC_TYPES))
    g.add_argument("--filter", action="append", default=[], help="dimension:operator:expression, repeatable")
    g.add_argument("--data-state", default="final", choices=["final", "all"])
    g.add_argument("--max-rows", type=int, default=0, help="stop after N rows (0 = all)")
    _window_args(g)

    i = sub.add_parser("inspect", help="URL Inspection index status, quota-aware")
    i.add_argument("--site", required=True)
    i.add_argument("--url", action="append", default=[])
    i.add_argument("--urls-file", help="one URL per line")
    i.add_argument("--max", type=int, default=100, help=f"URLs this run (default 100, at most {INSPECT_PER_DAY})")

    sm = sub.add_parser("sitemaps", help="sitemaps known to Search Console")
    sm.add_argument("--site", required=True)

    b = sub.add_parser("bing", help="Bing Webmaster query or page stats")
    b.add_argument("--site", required=True, help="site URL as verified in Bing Webmaster Tools")
    b.add_argument("--method", default="GetPageStats", choices=sorted(BING_METHODS))
    _window_args(b)

    pl = sub.add_parser("plausible", help="Plausible Stats API v2 query")
    pl.add_argument("--site-id", required=True)
    pl.add_argument("--metrics", default="visitors,visits")
    pl.add_argument("--dims", default="", help="e.g. visit:entry_page or visit:channel,event:goal")
    pl.add_argument("--range", help="Plausible shorthand such as 28d or month (instead of a window)")
    pl.add_argument("--filter", help='JSON filter list, e.g. [["is","visit:channel",["Organic Search"]]]')
    pl.add_argument("--max-rows", type=int, default=0)
    _window_args(pl)

    s = sub.add_parser("snapshot", help="fetch the standard set and write a dated JSON file")
    s.add_argument("--label", required=True, help="e.g. baseline, pricing-titles-before")
    s.add_argument("--gsc-site")
    s.add_argument("--bing-site")
    s.add_argument("--plausible-site")
    s.add_argument("--out", default="docs/growth/snapshots")
    s.add_argument("--data-state", default="final", choices=["final", "all"])
    s.add_argument("--max-rows", type=int, default=100000)
    s.add_argument("--force", action="store_true", help="overwrite a snapshot with the same date and label")
    _window_args(s)

    c = sub.add_parser("compare", help="per page or query deltas between two snapshots or two live windows")
    c.add_argument("snapshots", nargs="*", help="BEFORE.json AFTER.json")
    c.add_argument("--gsc-site", help="compare two live windows instead of files")
    c.add_argument("--before", help="START:END")
    c.add_argument("--after", help="START:END")
    c.add_argument("--by", default="page", choices=["page", "query"])
    c.add_argument("--min-impressions", type=int, default=DEFAULT_MIN_IMPRESSIONS)
    c.add_argument("--treated", help="file with the changed pages (or queries), one per line")
    c.add_argument("--control", help="file with comparable untouched pages, one per line")
    c.add_argument("--change-date", help="YYYY-MM-DD the change went live (recrawl date if known)")
    c.add_argument("--top", type=int, default=50, help="items to list (0 = all)")

    w = sub.add_parser("window", help="print the lag-safe window and its comparison windows")
    _window_args(w)
    return ap


def _live_snapshot(site: str, span: tuple[dt.date, dt.date], token: str) -> dict:
    start, end = span
    return {"meta": {"window": window_info(start, end), "data_state": "final"},
            "sources": {"gsc": {name: gsc_query(site, start, end, dims, token)
                                for name, dims in (("page", ["page"]), ("query", ["query"]),
                                                   ("page_query", ["page", "query"]))}}}


def run(args) -> dict:
    if args.cmd == "gsc":
        start, end = resolve_window(args)
        res = gsc_query(args.site, start, end, [d for d in args.dims.split(",") if d], gsc_token(),
                        search_type=args.type, filters=parse_filters(args.filter), data_state=args.data_state,
                        max_rows=args.max_rows)
        res["window"] = window_info(start, end, lag=args.lag)
        return res
    if args.cmd == "inspect":
        urls = list(args.url)
        if args.urls_file:
            urls += sorted(_load_list(args.urls_file))
        if not urls:
            raise UsageError("give --url or --urls-file")
        return inspect_urls(args.site, urls, gsc_token(), max_n=args.max)
    if args.cmd == "sitemaps":
        return gsc_sitemaps(args.site, gsc_token())
    if args.cmd == "bing":
        start, end = resolve_window(args)
        key = secret_from("BING_WEBMASTER_API_KEY", "BING_WEBMASTER_API_KEY_FILE", "bing-api-key", "Bing")
        return bing_stats(args.site, args.method, key, start, end)
    if args.cmd == "plausible":
        if args.range:
            rng = args.range
        else:
            start, end = resolve_window(args)
            rng = [start.isoformat(), end.isoformat()]
        try:
            filters = json.loads(args.filter) if args.filter else None
        except ValueError:
            raise UsageError("--filter must be a JSON list")
        key = secret_from("PLAUSIBLE_API_KEY", "PLAUSIBLE_API_KEY_FILE", "plausible-api-key", "Plausible")
        return plausible_query(args.site_id, [m for m in args.metrics.split(",") if m],
                               [d for d in args.dims.split(",") if d], rng, key, filters=filters,
                               max_rows=args.max_rows)
    if args.cmd == "snapshot":
        start, end = resolve_window(args)
        snap = build_snapshot(args.label, start, end, gsc_site=args.gsc_site, bing_site=args.bing_site,
                              plausible_site=args.plausible_site, data_state=args.data_state,
                              max_rows=args.max_rows, lag=args.lag)
        path = write_snapshot(snap, Path(args.out), force=args.force)
        return {"written": str(path), "window": snap["meta"]["window"], "skipped": snap["meta"]["skipped"],
                "sources": sorted(snap["sources"])}
    if args.cmd == "compare":
        if args.gsc_site:
            if not (args.before and args.after):
                raise UsageError("live compare needs --before START:END and --after START:END")
            tok = gsc_token()
            before = _live_snapshot(args.gsc_site, parse_span(args.before), tok)
            after = _live_snapshot(args.gsc_site, parse_span(args.after), tok)
        elif len(args.snapshots) == 2:
            before, after = load_json(args.snapshots[0]), load_json(args.snapshots[1])
        else:
            raise UsageError("give two snapshot files, or --gsc-site with --before and --after")
        return compare_snapshots(before, after, by=args.by, min_impressions=args.min_impressions,
                                 treated=_load_list(args.treated) or None, control=_load_list(args.control) or None,
                                 top=args.top, change_date=args.change_date)
    if args.cmd == "window":
        start, end = resolve_window(args)
        ps, pe = prior_window(start, end)
        ys, ye = prior_window(start, end, year_ago=True)
        return {"window": window_info(start, end, lag=args.lag), "previous": window_info(ps, pe, lag=args.lag),
                "year_ago": window_info(ys, ye, lag=args.lag), "today_pacific": pacific_today().isoformat()}
    raise UsageError("choose a subcommand; see --help")


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        out = run(args)
    except (UsageError, NoAccess, ApiError, CheckFailed) as e:
        print(json.dumps({"error": redact(str(e)), "exit": e.code}), file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    except Exception as e:  # no traceback: frames can hold credentials
        print(json.dumps({"error": redact(f"unexpected {e.__class__.__name__}: {e}"), "exit": 4}), file=sys.stderr)
        return 4
    print(json.dumps(out, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
