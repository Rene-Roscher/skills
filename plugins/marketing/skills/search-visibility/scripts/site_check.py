#!/usr/bin/env python3
"""Fetch pages the way a crawler without JavaScript sees them and report search-visibility findings.

Per URL: final status, redirect chain, meta refresh, query strings lost in redirects, noindex (meta or
X-Robots-Tag), canonical, hreflang, JSON-LD types, whether the H1 and an expected text are in the server
HTML, the robots.txt verdict for a fixed list of search and AI agents, and duplicate titles across the set.
Python 3.10 or later, standard library only. Read-only: GET requests, no cookies, no credentials.

Usage:
  site_check.py URL [URL ...] [--expect-text TEXT] [--text]
  site_check.py --urls-file FILE          one URL per line; "URL<TAB>expected text" checks that text on that URL
  site_check.py --sitemap https://www.example.com/sitemap.xml [--max-urls 50]
  site_check.py --root-dir dist --base-url https://www.example.com [URL ...]
                checks a built static site from disk before deploy (every *.html when no URL is given;
                no redirects or headers exist in this mode)
  site_check.py --self-test

Options: --max-urls N (default 50, at most 500, counts every page fetched), --delay SECONDS between requests
to one host (default 1.0, at least 0.5 over the network), --timeout SECONDS (default 15), --text for the
finding format of the search-visibility skill instead of JSON.

Exit codes:
  0  no blocker or high finding
  1  at least one blocker or high finding (or a failed self-test)
  2  usage error (arguments, unreadable URL file, missing directory)
  3  network unavailable: no requested URL or sitemap answered at all. Nothing was checked; say so.
  4  internal error

Not covered: JavaScript rendering, CDN or WAF bot rules (they answer per user agent; this script sends its
own), index status (use search-measurement), robots.txt percent-encoding normalisation.
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import html
import http.client
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

TOOL = "site_check.py 1.0"
USER_AGENT = "site-check/1.0 (search visibility audit; fetches HTML only, runs no JavaScript)"
MAX_URLS_DEFAULT = 50
MAX_URLS_HARD = 500
MAX_REDIRECTS = 10
ROBOTS_REDIRECTS = 5          # RFC 9309, "Redirects": follow at least five
ROBOTS_MAX_BYTES = 500 * 1024  # RFC 9309, "Limits": parse at least 500 KiB
MAX_BODY = 5 * 1024 * 1024
MAX_CHILD_SITEMAPS = 20
MIN_DELAY = 0.5
THIN_TEXT = 200
SEVERITIES = ("blocker", "high", "medium", "low")

# Token, purpose, severity when a checked URL is disallowed (None: verdict only, a business decision).
# Sources (verified 2026-11-04): https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers,
# https://blogs.bing.com/webmaster/october-2022/Announcing-user-agent-change-for-Bing-crawler-bingbot,
# https://support.apple.com/en-us/119829, https://developers.openai.com/api/docs/bots,
# https://support.claude.com/en/articles/8896518, https://docs.perplexity.ai/guides/bots
AGENTS = [
    ("Googlebot", "Google Search", "blocker"),
    ("Bingbot", "Bing search, the index behind Copilot answers", "blocker"),
    ("Applebot", "Apple search in Spotlight, Siri and Safari", "medium"),
    ("OAI-SearchBot", "ChatGPT search", "high"),
    ("Claude-SearchBot", "Claude search index", "high"),
    ("PerplexityBot", "Perplexity search", "high"),
    ("ChatGPT-User", "fetch on a ChatGPT user's request", "medium"),
    ("Claude-User", "fetch on a Claude user's request", "medium"),
    ("Perplexity-User", "fetch on a Perplexity user's request; vendor says it generally ignores robots.txt", None),
    ("GPTBot", "OpenAI model training", None),
    ("ClaudeBot", "Anthropic model training", None),
    ("Google-Extended", "token only: Gemini training and grounding, no effect on Search", None),
    ("Applebot-Extended", "token only: Apple model training, does not crawl", None),
]

# ISO 639-1 and ISO 3166-1 alpha-2, the only codes Google supports in hreflang (plus ISO 15924 scripts).
# Source: https://developers.google.com/search/docs/specialty/international/localized-versions (verified 2026-11-04)
LANGS = set(
    "aa ab ae af ak am an ar as av ay az ba be bg bh bi bm bn bo br bs ca ce ch co cr cs cu cv cy da de dv dz ee "
    "el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht hu hy hz ia id ie ig ii ik io is "
    "it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw ky la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms "
    "mt my na nb nd ne ng nl nn no nr nv ny oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se sg si sk "
    "sl sm sn so sq sr ss st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi "
    "yo za zh zu".split())
REGIONS = set(
    "AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY "
    "BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK "
    "FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR "
    "IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK "
    "ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM "
    "PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF "
    "TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW".split())

ORG_TYPES = {
    "Organization", "Corporation", "LocalBusiness", "OnlineBusiness", "OnlineStore", "ProfessionalService",
    "Store", "NGO", "EducationalOrganization", "GovernmentOrganization", "MedicalOrganization",
    "NewsMediaOrganization", "SportsOrganization", "Airline", "WorkersUnion", "Consortium",
}
RETIRED_TYPES = {
    "FAQPage": "FAQ rich results are no longer shown in Google Search (since 2026-05-07)",
    "HowTo": "HowTo rich results were retired in September 2023",
}
APP_SHELL_RE = re.compile(r"<div[^>]+id=[\"'](?:app|root|__next|__nuxt|svelte)[\"'][^>]*>\s*</div>", re.I)
SECRET_PARAM_RE = re.compile(
    r"(?i)([?&](?:token|access_token|key|api_key|apikey|secret|password|pass|sig|signature|auth|session|sid|code)=)"
    r"[^&\s\"'<>#]+")


class UsageError(Exception):
    code = 2


class NoNetwork(Exception):
    code = 3


class NetworkError(Exception):
    """One request failed below HTTP (DNS, TCP, TLS, timeout)."""


class OutOfScope(Exception):
    """A URL outside --base-url in --root-dir mode."""


def redact(text: str) -> str:
    return SECRET_PARAM_RE.sub(r"\1[redacted]", text)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


# --- transport -----------------------------------------------------------------------------------------

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401 (record hops ourselves)
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _headers(msg) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for k, v in (msg.items() if msg is not None else []):
        out.setdefault(k.lower(), []).append(v)
    return out


def urllib_transport(url: str, timeout: float):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
        "Accept-Encoding": "gzip",
    })
    try:
        with _OPENER.open(req, timeout=timeout) as resp:  # noqa: S310 (http and https only, checked by caller)
            return resp.status, _headers(resp.headers), resp.read(MAX_BODY)
    except urllib.error.HTTPError as e:
        try:
            body = e.read(MAX_BODY)
        except Exception:
            body = b""
        return e.code, _headers(e.headers), body
    except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError) as e:
        raise NetworkError(str(getattr(e, "reason", e)))


class LocalTransport:
    """Serves a built static site from disk: 200 for an existing file, 404 otherwise."""

    def __init__(self, root: Path, base_url: str):
        self.root = root.resolve()
        b = urllib.parse.urlsplit(base_url)
        self.scheme, self.host = b.scheme.lower(), b.netloc.lower()

    def resolve(self, url: str) -> Path | None:
        u = urllib.parse.urlsplit(url)
        if u.scheme.lower() != self.scheme or u.netloc.lower() != self.host:
            raise OutOfScope(url)
        rel = urllib.parse.unquote(u.path).lstrip("/")
        cands = [rel + "index.html"] if rel == "" or rel.endswith("/") else [rel, rel + ".html", rel + "/index.html"]
        for c in cands:
            p = (self.root / c).resolve()
            if p != self.root and self.root not in p.parents:
                continue  # traversal outside the build directory
            if p.is_file():
                return p
        return None

    def __call__(self, url: str, timeout: float):
        p = self.resolve(url)
        if p is None:
            return 404, {"content-type": ["text/html"]}, b"<title>Not found</title>"
        ctype = {".xml": "application/xml", ".txt": "text/plain", ".gz": "application/gzip"}.get(
            p.suffix, "text/html; charset=utf-8")
        return 200, {"content-type": [ctype]}, p.read_bytes()[:MAX_BODY]


def local_urls(root: Path, base_url: str, keep_ext: bool) -> list[str]:
    out = []
    base = base_url.rstrip("/")
    for p in sorted(root.rglob("*.html")):
        rel = p.relative_to(root).as_posix()
        if p.name in ("404.html", "500.html"):
            continue
        if p.name == "index.html":
            path = rel[: -len("index.html")]
        else:
            path = rel if keep_ext else rel[:-5]
        out.append(f"{base}/{path}")
    return out


class Fetcher:
    def __init__(self, transport, delay: float, timeout: float, sleep=time.sleep, clock=time.monotonic):
        self.transport, self.delay, self.timeout = transport, delay, timeout
        self.sleep, self.clock = sleep, clock
        self.last: dict[str, float] = {}
        self.requests = 0

    def get(self, url: str):
        host = urllib.parse.urlsplit(url).netloc.lower()
        if host in self.last and self.delay > 0:
            wait = self.delay - (self.clock() - self.last[host])
            if wait > 0:
                self.sleep(wait)
        try:
            return self.transport(url, self.timeout)
        finally:
            self.last[host] = self.clock()
            self.requests += 1


def follow(fetcher: Fetcher, url: str, max_hops: int = MAX_REDIRECTS):
    """Return (chain, headers, body, problem). problem is None, 'loop' or 'network: ...'."""
    chain: list[dict] = []
    seen: set[str] = set()
    cur = url
    while True:
        try:
            status, headers, body = fetcher.get(cur)
        except NetworkError as e:
            chain.append({"url": cur, "status": None})
            return chain, None, None, f"network: {e}"
        loc = first(headers, "location")
        if 300 <= status < 400 and loc:
            nxt = urllib.parse.urljoin(cur, loc.strip())
            chain.append({"url": cur, "status": status, "location": nxt})
            seen.add(cur)
            if nxt in seen or len(chain) > max_hops:
                return chain, headers, body, "loop"
            cur = nxt
            continue
        chain.append({"url": cur, "status": status})
        return chain, headers, body, None


def first(headers: dict | None, name: str) -> str:
    vals = (headers or {}).get(name, [])
    return vals[0] if vals else ""


def decode_body(headers: dict | None, body: bytes | None) -> str:
    body = body or b""
    if "gzip" in first(headers, "content-encoding").lower() or body[:2] == b"\x1f\x8b":
        try:
            body = gzip.GzipFile(fileobj=io.BytesIO(body)).read(MAX_BODY)
        except (OSError, EOFError):
            pass
    m = re.search(r"charset=[\"']?([\w-]+)", first(headers, "content-type"), re.I)
    try:
        return body.decode(m.group(1) if m else "utf-8", "replace")
    except LookupError:
        return body.decode("utf-8", "replace")


# --- parsing -------------------------------------------------------------------------------------------

class PageParser(HTMLParser):
    SKIP = {"script", "style", "template", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titles: list[str] = []
        self._title: list[str] | None = None  # buffer while inside <title>
        self.meta_robots: list[tuple[str, str]] = []
        self.refresh: str | None = None
        self.canonicals: list[str] = []
        self.hreflang: list[tuple[str, str]] = []
        self.h1: list[str] = []
        self._h1_depth = 0
        self._h1_buf: list[str] = []
        self.jsonld: list[str] = []
        self._ld: list[str] | None = None
        self.text: list[str] = []
        self._skip = 0
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "title":
            self._title = []
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name in ("robots", "googlebot", "bingbot"):
                self.meta_robots.append((name, a.get("content", "")))
            if a.get("http-equiv", "").lower() == "refresh":
                self.refresh = a.get("content", "")
        elif tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonicals.append(a.get("href", "").strip())
            if "alternate" in rel and "hreflang" in a:
                self.hreflang.append((a["hreflang"].strip(), a.get("href", "").strip()))
        elif tag == "h1":
            self._h1_depth += 1
            if self._h1_depth == 1:
                self._h1_buf = []
        elif tag in self.SKIP:
            self._skip += 1
            if tag == "script":
                self.scripts += 1
                if "ld+json" in a.get("type", "").lower():
                    self._ld = []

    def handle_endtag(self, tag):
        if tag == "title" and self._title is not None:
            self.titles.append(" ".join("".join(self._title).split()))
            self._title = None
        elif tag == "h1" and self._h1_depth > 0:
            self._h1_depth -= 1
            if self._h1_depth == 0:
                self.h1.append(" ".join("".join(self._h1_buf).split()))
        elif tag in self.SKIP and self._skip > 0:
            self._skip -= 1
            if tag == "script" and self._ld is not None:
                self.jsonld.append("".join(self._ld))
                self._ld = None

    def handle_data(self, data):
        if self._title is not None:
            self._title.append(data)
            return
        if self._ld is not None:
            self._ld.append(data)
        elif self._skip == 0:
            self.text.append(data)
            if self._h1_depth:
                self._h1_buf.append(data)


LINK_HDR_RE = re.compile(r"<([^>]*)>((?:\s*;\s*[^;,]+)*)")


def parse_link_header(values: list[str]):
    for v in values:
        for m in LINK_HDR_RE.finditer(v):
            params = {}
            for p in m.group(2).split(";"):
                if "=" in p:
                    k, val = p.split("=", 1)
                    params[k.strip().lower()] = val.strip().strip('"')
            yield m.group(1).strip(), params


def norm_url(url: str) -> str:
    try:
        u = urllib.parse.urlsplit(url.strip())
        scheme = u.scheme.lower()
        host = (u.hostname or "").lower()
        port = u.port
    except ValueError:
        return url.strip()
    default = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = host + (f":{port}" if port and not default else "")
    return urllib.parse.urlunsplit((scheme, netloc, u.path or "/", u.query, ""))


def strip_query(url: str) -> str:
    u = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, "", ""))


def norm_text(s: str) -> str:
    return " ".join(s.replace(" ", " ").split()).casefold()


def hreflang_problem(code: str) -> str | None:
    c = code.strip()
    if c.lower() == "x-default":
        return None
    if "_" in c:
        return "uses an underscore; codes use a hyphen, e.g. en-GB"
    parts = c.split("-")
    if parts[0].lower() not in LANGS:
        if len(parts) == 1 and parts[0].upper() in REGIONS:
            return "is a region alone; the language comes first, e.g. de-AT"
        return "starts with no ISO 639-1 language code"
    rest = parts[1:]
    if rest and re.fullmatch(r"[A-Za-z]{4}", rest[0]):
        rest = rest[1:]  # ISO 15924 script, e.g. zh-Hant
    if len(rest) > 1:
        return "has more parts than language, script and region"
    if rest:
        r = rest[0].upper()
        if r == "UK":
            return "uses UK, which is not ISO 3166-1; the United Kingdom is GB"
        if r not in REGIONS:
            return "has a region that is not an ISO 3166-1 alpha-2 code"
    return None


def noindex_sources(meta_robots: list[tuple[str, str]], xrt: list[str]) -> list[str]:
    out = []
    for name, content in meta_robots:
        if {t.strip().lower() for t in content.split(",")} & {"noindex", "none"}:
            out.append(f'<meta name="{name}" content="{content}">')
    for v in xrt:
        val = v
        m = re.match(r"\s*([A-Za-z][\w-]*)\s*:\s*(.*)$", v)
        if m and m.group(1).lower() not in ("unavailable_after", "max-snippet", "max-image-preview",
                                            "max-video-preview"):
            val = m.group(2)
        if {t.strip().lower() for t in val.split(",")} & {"noindex", "none"}:
            out.append(f"X-Robots-Tag: {v}")
    return out


def _type_names(node: dict) -> set[str]:
    t = node.get("@type")
    vals = t if isinstance(t, list) else [t]
    return {str(x).rsplit("/", 1)[-1].rsplit(":", 1)[-1] for x in vals if x}


def _walk(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def analyse_jsonld(blocks: list[str]) -> dict:
    types: set[str] = set()
    invalid: list[str] = []
    self_reviews: list[str] = []
    nodes: list[dict] = []
    for i, raw in enumerate(blocks, 1):
        if not raw.strip():
            continue
        try:
            nodes.extend(_walk(json.loads(raw)))
        except ValueError as e:
            invalid.append(f"block {i}: {e}")
    by_id: dict[str, dict] = {}
    for n in nodes:
        if isinstance(n.get("@id"), str) and set(n) - {"@id"}:  # a bare {"@id": ...} is a reference
            by_id.setdefault(n["@id"], n)
    for n in nodes:
        tn = _type_names(n)
        types |= tn
        if tn & ORG_TYPES:
            for key in ("aggregateRating", "review"):
                if n.get(key):
                    self_reviews.append(f"{'/'.join(sorted(tn & ORG_TYPES))} carries {key}")
        if tn & {"Review", "AggregateRating"}:
            item = n.get("itemReviewed")
            if isinstance(item, dict):
                target = by_id.get(item.get("@id"), item) if set(item) <= {"@id"} else item
                if isinstance(target, dict) and _type_names(target) & ORG_TYPES:
                    self_reviews.append(f"{'/'.join(sorted(tn & {'Review', 'AggregateRating'}))} reviews "
                                        f"{'/'.join(sorted(_type_names(target) & ORG_TYPES))}")
    return {"types": sorted(types), "invalid": invalid, "self_reviews": sorted(set(self_reviews))}


# --- robots.txt (RFC 9309) -----------------------------------------------------------------------------

def parse_robots(text: str) -> list[dict]:
    groups: list[dict] = []
    cur = None
    last_agent = False
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key, val = key.strip().lower(), val.strip()
        if key == "user-agent":
            if cur is None or not last_agent:
                cur = {"agents": [], "rules": [], "line": n}
                groups.append(cur)
            cur["agents"].append(val.lower())
            last_agent = True
        elif key in ("allow", "disallow"):
            last_agent = False
            if cur is not None:
                cur["rules"].append((key == "allow", val, n))
    return groups


def _rule_matches(pattern: str, path: str) -> bool:
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    rx = "".join(".*" if ch == "*" else re.escape(ch) for ch in body) + ("$" if anchored else "")
    return re.match(rx, path) is not None


def robots_verdict(groups: list[dict], token: str, path: str):
    """Return (allowed, (allow, pattern, line) or None, group name). Longest match wins; allow wins a tie."""
    t = token.lower()
    sel = [g for g in groups if t in g["agents"]]
    which = token
    if not sel:
        sel = [g for g in groups if "*" in g["agents"]]
        which = "*"
    best = None
    for allow, pat, n in (r for g in sel for r in g["rules"]):
        if pat and _rule_matches(pat, path):
            if best is None or (len(pat), allow) > (len(best[1]), best[0]):
                best = (allow, pat, n)
    return (True if best is None else best[0]), best, which


def robots_path(url: str) -> str:
    u = urllib.parse.urlsplit(url)
    return (u.path or "/") + (f"?{u.query}" if u.query else "")


def fetch_robots(fetcher: Fetcher, origin: str) -> dict:
    url = origin + "/robots.txt"
    rec = {"url": url, "status": None, "state": "", "groups": []}
    try:
        chain, headers, body, problem = follow(fetcher, url, ROBOTS_REDIRECTS)
    except OutOfScope:
        rec["state"] = "not checked (outside --base-url)"
        return rec
    rec["status"] = chain[-1]["status"]
    if problem and problem.startswith("network"):
        rec["state"] = "unreachable"
        rec["error"] = problem
    elif problem == "loop":
        rec["state"] = "allow all (more than five redirects: treated as unavailable)"
    elif rec["status"] == 200:
        rec["groups"] = parse_robots(decode_body(headers, (body or b"")[:ROBOTS_MAX_BYTES]))
        rec["state"] = "parsed"
    elif rec["status"] is not None and 400 <= rec["status"] < 500:
        rec["state"] = "allow all (4xx: unavailable)"
    else:
        rec["state"] = "unreachable"
    return rec


# --- page checks ---------------------------------------------------------------------------------------

def fetch_page(fetcher: Fetcher, target: dict, now) -> dict:
    url = target["url"]
    page = {"url": url, "source": target.get("source", "argument"), "expect": list(target.get("expect", [])),
            "fetched_at": now().strftime("%Y-%m-%d %H:%M"), "chain": [], "status": None, "final_url": url,
            "error": None, "loop": False, "html": False, "out_of_scope": False}
    try:
        chain, headers, body, problem = follow(fetcher, url)
    except OutOfScope:
        page["out_of_scope"] = True
        return page
    page["chain"] = chain
    page["final_url"] = chain[-1]["url"]
    page["status"] = chain[-1]["status"]
    if problem == "loop":
        page["loop"] = True
        return page
    if problem:
        page["error"] = problem
        return page
    page["headers"] = {k: v for k, v in (headers or {}).items() if k in ("content-type", "x-robots-tag", "link")}
    links = list(parse_link_header((headers or {}).get("link", [])))
    page["xrobots"] = (headers or {}).get("x-robots-tag", [])
    ctype = first(headers, "content-type").lower()
    text = decode_body(headers, body)
    page["html"] = "html" in ctype or (not ctype and text.lstrip()[:1] == "<")
    p = PageParser()
    if page["html"]:
        try:
            p.feed(text)
            p.close()
        except Exception as e:  # html.parser rarely raises; keep the page and say so
            page["parse_error"] = str(e)
    base = page["final_url"]
    page["title"] = p.titles[0] if p.titles else None
    page["title_count"] = len(p.titles)
    page["meta_refresh"] = p.refresh
    page["canonicals"] = [urllib.parse.urljoin(base, c) for c in p.canonicals if c] + [
        urllib.parse.urljoin(base, u) for u, prm in links if "canonical" in prm.get("rel", "").lower().split()]
    page["hreflang"] = [(code, urllib.parse.urljoin(base, href)) for code, href in p.hreflang if href] + [
        (prm["hreflang"], urllib.parse.urljoin(base, u)) for u, prm in links
        if "alternate" in prm.get("rel", "").lower().split() and prm.get("hreflang")]
    page["h1"] = p.h1
    page["noindex"] = noindex_sources(p.meta_robots, page["xrobots"])
    page["jsonld"] = analyse_jsonld(p.jsonld)
    visible = " ".join(" ".join(p.text).split())
    page["text_chars"] = len(visible)
    page["_visible"] = norm_text(visible)
    page["_raw"] = norm_text(html.unescape(text))
    page["app_shell"] = bool(APP_SHELL_RE.search(text))
    page["scripts"] = p.scripts
    return page


class Report:
    def __init__(self, now, where: str = "server HTML without JavaScript"):
        self.findings: list[dict] = []
        self.now = now
        self.where = where

    def add(self, sev, check, url, evidence, fix, verify=None, when=None):
        when = when or self.now().strftime("%Y-%m-%d %H:%M")
        self.findings.append({
            "severity": sev, "check": check, "url": url,
            "evidence": f"{evidence} (site_check.py, {when} UTC, {self.where})",
            "fix": fix,
            "verify": verify or f"Re-run site_check.py on this URL after the deploy; the {check} finding is gone.",
        })


def _hops(page) -> list[dict]:
    return [h for h in page["chain"] if "location" in h]


def check_pages(pages: list[dict], index: dict, rep: Report) -> None:
    for page in pages:
        if page["source"] == "hreflang":
            continue
        url, when = page["url"], page["fetched_at"]
        add = lambda *a, **k: rep.add(*a, when=when, **k)  # noqa: E731
        if page["out_of_scope"]:
            continue
        hops = _hops(page)
        chain_txt = " -> ".join(f"{h['url']} ({h['status']})" for h in page["chain"])
        if page["loop"]:
            add("blocker", "redirect-loop", url, f"Redirects never reach a page: {chain_txt}",
                "Point the first URL at the final page with one 301 or 308 and remove the loop.")
            continue
        if page["error"]:
            add("high", "unreachable", url, f"No HTTP answer: {page['error']}",
                "Check DNS, TLS and the server for this host, then re-run from another network to rule out the "
                "auditing machine.")
            continue
        if len(hops) > 1:
            add("medium", "redirect-chain", url, f"{len(hops)} redirect hops: {chain_txt}",
                f"Redirect {url} straight to {page['final_url']} in one hop and update internal links.")
        temp = [h for h in hops if h["status"] in (302, 303, 307)]
        if temp:
            add("medium", "redirect-temporary", url,
                "Temporary redirect: " + ", ".join(f"{h['url']} answers {h['status']}" for h in temp),
                "If the move is permanent, answer 301 or 308; temporary codes keep the old URL as canonical "
                "candidate.")
        down = [h for h in hops if h["url"].startswith("https:") and h["location"].startswith("http:")]
        if down:
            add("high", "redirect-downgrade", url,
                "Redirect from https to http: " + ", ".join(f"{h['url']} -> {h['location']}" for h in down),
                "Redirect to the https URL; behind a TLS-terminating proxy, make the server build https Locations.")
        q = urllib.parse.urlsplit(url).query
        if hops and q:
            names = {k for k, _ in urllib.parse.parse_qsl(q, keep_blank_values=True)}
            kept = {k for k, _ in urllib.parse.parse_qsl(urllib.parse.urlsplit(page["final_url"]).query,
                                                          keep_blank_values=True)}
            lost = sorted(names - kept)
            if lost:
                add("medium", "query-lost", url,
                    f"Query parameters {', '.join(lost)} are dropped on the way to {page['final_url']}",
                    "Keep the query string in the redirect target; otherwise campaign and referral tags never "
                    "reach analytics.")
        if hops and page["source"] == "sitemap":
            add("medium", "sitemap-redirect", url, f"The sitemap lists a redirecting URL: {chain_txt}",
                f"List {page['final_url']} in the sitemap instead.")
        if page["status"] != 200:
            add("blocker", "status", url, f"Final answer HTTP {page['status']}" +
                (f" after {chain_txt}" if hops else "") + (" (listed in the sitemap)" if page["source"] == "sitemap"
                                                          else ""),
                "Serve the page with 200, or redirect it once with 301 or 308 to the closest live page and remove "
                "it from the sitemap and internal links.",
                verify="Re-run site_check.py on this URL; the final status is 200 or a single 301/308 hop.")
            continue
        if page["noindex"]:
            add("blocker", "noindex", url, "noindex set by " + "; ".join(page["noindex"]),
                "Remove noindex if this page should appear in search (set robots directives on the server, not "
                "in JavaScript); if it should not, remove it from the sitemap and internal links instead.",
                verify="Re-run site_check.py; then URL Inspection through search-measurement shows the page as "
                       "indexable after the next crawl.")
        if page.get("meta_refresh") is not None:
            add("high", "meta-refresh", url, f'<meta http-equiv="refresh" content="{page["meta_refresh"]}">',
                "Replace the meta refresh with a server-side 301 or 308 redirect to the target.")
            continue
        if not page["html"]:
            continue
        check_canonical(page, index, add)
        check_content(page, add)
        check_jsonld(page, add)
    check_hreflang(pages, index, rep)
    check_titles(pages, rep)


def check_canonical(page, index, add) -> None:
    url, final = page["url"], page["final_url"]
    cans = list(dict.fromkeys(norm_url(c) for c in page["canonicals"]))
    if not cans:
        add("medium", "canonical-missing", url, "No rel=canonical in the HTML or the Link header",
            f'Add <link rel="canonical" href="{final}"> to the server HTML.')
        return
    if len(cans) > 1:
        add("high", "canonical-multiple", url, "Conflicting canonicals: " + ", ".join(cans),
            "Keep one canonical; with conflicting ones search engines ignore them all.")
        return
    can, me = cans[0], norm_url(final)
    if can in (me, norm_url(strip_query(final))):
        return
    cu, fu = urllib.parse.urlsplit(can), urllib.parse.urlsplit(me)
    codes_self = {c.lower() for c, h in page["hreflang"] if norm_url(h) == me}
    codes_can = {c.lower() for c, h in page["hreflang"] if norm_url(h) == can}
    target = index.get(can)
    if codes_can and not (codes_can & codes_self):
        add("high", "canonical-other-language", url,
            f"Canonical is {can}, the hreflang={'/'.join(sorted(codes_can))} version of this page",
            "Make each language version canonical to itself; hreflang connects them.")
    elif fu.netloc != cu.netloc:
        add("high", "canonical-cross-host", url, f"Canonical points to another host: {can}",
            "Use a self-referencing canonical, unless this page is a deliberate copy of that URL (then the owner "
            "confirms it).")
    elif cu.path in ("", "/") and fu.path not in ("", "/"):
        add("high", "canonical-home", url, f"Canonical points to the home page ({can}) from a page with its own "
            "content", f"Set the canonical to {final}; a home-page canonical drops this page from ranking.")
    else:
        add("medium", "canonical-not-self", url, f"Canonical is {can}, not this URL",
            f"Set the canonical to {final}, unless this page is a named duplicate of {can} (owner decision).")
    if target and not target["out_of_scope"] and (target["status"] != 200 or _hops(target)):
        add("high", "canonical-target-status", url,
            f"Canonical target {can} answers {target['status']}" + (" after a redirect" if _hops(target) else ""),
            "Point the canonical at a URL that answers 200 directly.")


def check_content(page, add) -> None:
    url = page["url"]
    if not page.get("title"):
        add("medium", "title-missing", url, "No <title> text in the server HTML",
            "Add one unique <title> that names the page's single intent.")
    if not page["h1"]:
        extra = f"; visible text {page['text_chars']} characters, {page['scripts']} script tag(s)"
        if page["app_shell"]:
            extra += ", an empty app container in the body"
        add("high", "h1-missing", url, "No <h1> in the server HTML" + extra,
            "Render the headline and the main text on the server (SSR or prerender); crawlers that run no "
            "JavaScript see nothing else.")
    for want in page["expect"]:
        n = norm_text(want)
        if n and n not in page["_visible"]:
            where = ("present only inside <script> or markup, not as visible text" if n in page["_raw"]
                     else "absent from the server HTML")
            add("blocker", "text-missing", url, f'Expected text "{want}" is {where}',
                "Put this text in the server-rendered HTML (not only in JavaScript, JSON-LD or a client-side "
                "accordion).")


def check_jsonld(page, add) -> None:
    url, ld = page["url"], page["jsonld"]
    if ld["invalid"]:
        add("high", "jsonld-invalid", url, "JSON-LD that does not parse: " + "; ".join(ld["invalid"]),
            "Fix the JSON syntax; an invalid block is ignored as a whole.")
    retired = [t for t in ld["types"] if t in RETIRED_TYPES]
    if retired:
        add("low", "jsonld-retired", url, "; ".join(f"{t}: {RETIRED_TYPES[t]}" for t in retired),
            "Leave existing markup or remove it; do not add or extend it for a search result. Keep the answers "
            "as visible text.")
    if ld["self_reviews"]:
        add("high", "jsonld-self-review", url, "Review markup about the site's own organization: " +
            "; ".join(ld["self_reviews"]),
            "Remove review and rating markup about your own organization; Google treats it as self-serving and "
            "ineligible. If the page reviews another organization, ignore this finding.")


def check_hreflang(pages, index, rep: Report) -> None:
    for page in pages:
        if page["source"] == "hreflang" or page["status"] != 200 or not page["html"] or page["out_of_scope"]:
            continue
        entries = page.get("hreflang") or []
        if not entries or page.get("meta_refresh") is not None:
            continue
        url, when = page["url"], page["fetched_at"]
        me = norm_url(page["final_url"])
        # A tracking-parameter variant is judged as its clean URL, as the canonical check does.
        mine = {me, norm_url(strip_query(page["final_url"])), norm_url(page["url"])}
        add = lambda *a, **k: rep.add(*a, when=when, **k)  # noqa: E731
        bad = [(c, hreflang_problem(c)) for c, _ in entries]
        bad = [f'"{c}" {p}' for c, p in bad if p]
        if bad:
            add("high", "hreflang-invalid-code", url, "Invalid hreflang codes: " + "; ".join(bad),
                "Use ISO 639-1 language codes with an optional ISO 3166-1 alpha-2 region (en, en-GB, de-AT) or "
                "x-default.")
        if not any(norm_url(h) in mine for _, h in entries):
            add("high", "hreflang-no-self", url, "hreflang lists " + ", ".join(f"{c}={h}" for c, h in entries) +
                " but not this URL", "Add an hreflang entry for this page itself; each version lists itself and "
                "all others.")
        if not any(c.lower() == "x-default" for c, _ in entries):
            add("low", "hreflang-no-x-default", url, "No hreflang=\"x-default\" in the cluster",
                "Add x-default pointing at the version for visitors whose language matches none.")
        broken, one_way, unchecked = [], [], []
        for code, href in entries:
            t = norm_url(href)
            if t in mine:
                continue
            target = index.get(t)
            if target is None:
                unchecked.append(href)
                continue
            if target["out_of_scope"]:
                continue
            if target["error"] or target["loop"] or target["status"] != 200 or _hops(target):
                how = (f"redirects to {target['final_url']}" if _hops(target) and not target["loop"]
                       else target["error"] or f"answers {target['status']}")
                broken.append(f"{code}={href} {how}")
                continue
            back = {norm_url(h) for _, h in target.get("hreflang") or []}
            if not (mine & back):
                one_way.append(f"{code}={href}")
        if broken:
            add("high", "hreflang-target-status", url, "hreflang targets that do not answer 200: " +
                "; ".join(broken), "Point each hreflang entry at the final URL that answers 200.")
        if one_way:
            add("high", "hreflang-not-reciprocal", url, "These versions do not link back to this URL: " +
                ", ".join(one_way), "Add the return hreflang entries on those pages; one-way annotations are "
                "ignored.")
        if unchecked:
            page["hreflang_unchecked"] = unchecked


def check_titles(pages, rep: Report) -> None:
    groups: dict[str, list[str]] = {}
    for p in pages:
        if p["source"] == "hreflang" or p["status"] != 200 or not p.get("title") or p.get("meta_refresh") is not None:
            continue
        groups.setdefault(norm_text(p["title"]), []).append(p["url"])
    for _, urls in sorted(groups.items()):
        if len(urls) > 1:
            shown = ", ".join(urls[:5]) + (f" and {len(urls) - 5} more" if len(urls) > 5 else "")
            title = next(p["title"] for p in pages if p["url"] == urls[0])
            rep.add("medium", "title-duplicate", shown, f'{len(urls)} URLs share the title "{title}"',
                    "Give each URL a title that names its own intent; if they serve the same intent, merge them "
                    "and redirect (owner decision).",
                    verify="Re-run site_check.py on the set; no title-duplicate finding remains.")


def check_robots(pages, robots: dict, rep: Report, accepted: frozenset = frozenset()) -> dict:
    verdicts: dict[str, dict] = {}
    grouped: dict[tuple, dict] = {}
    for origin, rec in robots.items():
        if rec["state"] == "unreachable":
            rep.add("blocker", "robots-unreachable", rec["url"],
                    f"robots.txt answered {rec['status'] if rec['status'] else rec.get('error', 'nothing')}; "
                    "crawlers then assume the whole site is disallowed (RFC 9309, 'Unreachable Status')",
                    "Serve robots.txt with 200 (or 404 if there are no rules); never 5xx.",
                    verify="Re-run site_check.py; the robots.txt line shows 'parsed' or 'allow all'.")
        verdicts[origin] = {"url": rec["url"], "status": rec["status"], "state": rec["state"], "agents": {}}
    for page in pages:
        if page["source"] == "hreflang" or page["status"] is None or page["out_of_scope"]:
            continue
        final = page["final_url"]
        u = urllib.parse.urlsplit(final)
        origin = f"{u.scheme}://{u.netloc}"
        rec = robots.get(origin)
        if not rec or rec["state"] != "parsed":
            continue
        blocked = []
        for token, purpose, sev in AGENTS:
            allowed, rule, which = robots_verdict(rec["groups"], token, robots_path(final))
            v = verdicts[origin]["agents"].setdefault(token, {"purpose": purpose, "allowed": 0, "disallowed": []})
            if allowed:
                v["allowed"] += 1
                continue
            v["disallowed"].append(final)
            if token in accepted:
                v["accepted_by_adr"] = True
            elif sev:
                blocked.append((SEVERITIES.index(sev), token, f"{token} (`Disallow: {rule[1]}`, line {rule[2]}, "
                                                              f"group {which})"))
        if blocked:
            blocked.sort()
            key = (rec["url"], SEVERITIES[blocked[0][0]], "; ".join(b[2] for b in blocked))
            grouped.setdefault(key, {"urls": [], "when": page["fetched_at"]})["urls"].append(final)
    # One finding per identical block, so a site-wide Disallow is one finding with a URL group.
    for (robots_url, sev, desc), g in grouped.items():
        urls = g["urls"]
        shown = ", ".join(urls[:5]) + (f" and {len(urls) - 5} more" if len(urls) > 5 else "")
        rep.add(sev, "robots-blocked", shown,
                f"{robots_url} disallows {'this URL' if len(urls) == 1 else f'these {len(urls)} URLs'} for {desc}",
                "Allow these agents for this path in robots.txt, or record the block in an ADR. A Googlebot or "
                "Bingbot block removes the page from search; blocking search and user-fetch agents removes it "
                "from AI answers. Check CDN or WAF bot rules for the same agents.",
                when=g["when"])
    return verdicts


# --- inputs --------------------------------------------------------------------------------------------

def check_url_arg(u: str) -> str:
    p = urllib.parse.urlsplit(u.strip())
    if p.scheme not in ("http", "https") or not p.netloc:
        raise UsageError(f"not an http(s) URL: {redact(u)!r}")
    return u.strip()


def read_urls_file(path: str) -> list[dict]:
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise UsageError(f"cannot read {path}: {e.strerror}")
    out = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        url, _, want = line.partition("\t")
        out.append({"url": check_url_arg(url), "source": "argument", "expect": [want.strip()] if want.strip() else []})
    return out


def read_sitemap(fetcher: Fetcher, url: str, limit: int, rep: Report, stats: dict, depth: int = 0) -> list[str]:
    try:
        chain, headers, body, problem = follow(fetcher, url, ROBOTS_REDIRECTS)
    except OutOfScope:
        raise UsageError(f"sitemap {url} is outside --base-url")
    status = chain[-1]["status"]
    if problem and problem.startswith("network"):
        stats["network_failures"] += 1
        rep.add("high", "sitemap-status", url, f"Sitemap not reachable: {problem}",
                "Serve the sitemap with 200 and reference it in robots.txt.")
        return []
    stats["answers"] += 1
    if problem or status != 200:
        rep.add("high", "sitemap-status", url, f"Sitemap answers {status}" + (" (redirect loop)" if problem else ""),
                "Serve the sitemap with 200 at the URL referenced in robots.txt and Search Console.")
        return []
    text = decode_body(headers, body)
    locs = [html.unescape(m) for m in re.findall(r"<loc>\s*(.*?)\s*</loc>", text, re.S | re.I)]
    if re.search(r"<sitemapindex\b", text, re.I):
        out: list[str] = []
        if depth > 0:
            return out
        for child in locs[:MAX_CHILD_SITEMAPS]:
            out.extend(read_sitemap(fetcher, child, limit, rep, stats, depth + 1))
        return out
    return locs


def build_targets(args, fetcher: Fetcher, rep: Report, stats: dict) -> list[dict]:
    targets = [{"url": check_url_arg(u), "source": "argument", "expect": []} for u in args.urls]
    if args.urls_file:
        targets += read_urls_file(args.urls_file)
    for sm in args.sitemap or []:
        for u in read_sitemap(fetcher, check_url_arg(sm), args.max_urls, rep, stats):
            if urllib.parse.urlsplit(u).scheme in ("http", "https"):
                targets.append({"url": u, "source": "sitemap", "expect": []})
    if args.root_dir and not targets and not args.sitemap:
        targets = [{"url": u, "source": "argument", "expect": []}
                   for u in local_urls(Path(args.root_dir), args.base_url, args.keep_html_ext)]
    for t in targets:
        t["expect"] = list(dict.fromkeys(t["expect"] + list(args.expect_text or [])))
    seen, out = set(), []
    for t in targets:
        if t["url"] not in seen:
            seen.add(t["url"])
            out.append(t)
    return out


def check_site(targets: list[dict], fetcher: Fetcher, max_urls: int, rep: Report, stats: dict,
               now=now_utc, accepted: frozenset = frozenset()) -> dict:
    found = len(targets)
    targets = targets[:max_urls]
    pages = [fetch_page(fetcher, t, now) for t in targets]
    answered = [p for p in pages if p["status"] is not None or p["out_of_scope"]]
    if targets and not answered and not stats["answers"]:
        raise NoNetwork("no requested URL answered: " + (pages[0]["error"] or "no HTTP response"))
    if not targets and stats["network_failures"] and not stats["answers"]:
        raise NoNetwork("the sitemap did not answer")
    index: dict[str, dict] = {}
    for p in pages:
        index.setdefault(norm_url(p["url"]), p)
        index.setdefault(norm_url(p["final_url"]), p)
    # Fetch hreflang targets outside the set, within the same cap.
    for p in list(pages):
        for _, href in p.get("hreflang") or []:
            if len(pages) >= max_urls:
                break
            if norm_url(href) not in index and urllib.parse.urlsplit(href).scheme in ("http", "https"):
                extra = fetch_page(fetcher, {"url": href, "source": "hreflang"}, now)
                pages.append(extra)
                index.setdefault(norm_url(extra["url"]), extra)
                index.setdefault(norm_url(extra["final_url"]), extra)
    origins = []
    for p in pages:
        if p["source"] != "hreflang" and p["status"] is not None:
            u = urllib.parse.urlsplit(p["final_url"])
            o = f"{u.scheme}://{u.netloc}"
            if o not in origins:
                origins.append(o)
    robots = {o: fetch_robots(fetcher, o) for o in origins}
    check_pages(pages, index, rep)
    verdicts = check_robots(pages, robots, rep, accepted)
    rep.findings.sort(key=lambda f: (SEVERITIES.index(f["severity"]), f["url"], f["check"]))
    counts = {s: sum(1 for f in rep.findings if f["severity"] == s) for s in SEVERITIES}
    code = 1 if counts["blocker"] or counts["high"] else 0
    public = []
    for p in pages:
        q = {k: v for k, v in p.items() if not k.startswith("_")}
        q["hreflang"] = [{"code": c, "href": h} for c, h in p.get("hreflang") or []]
        public.append(q)
    return {
        "tool": TOOL, "checked_at": now().strftime("%Y-%m-%dT%H:%M:%SZ"), "user_agent": USER_AGENT,
        "urls_found": found, "urls_checked": len(targets), "urls_not_checked": max(0, found - len(targets)),
        "requests": fetcher.requests, "summary": counts, "exit": code, "findings": rep.findings,
        "robots": verdicts, "pages": public,
    }


def render_text(report: dict) -> str:
    out = []
    for f in report["findings"]:
        out += [f"[severity: {f['severity']}] {f['url']}", f"Evidence: {f['evidence']}", f"Fix: {f['fix']}",
                f"Verify: {f['verify']}", ""]
    if not report["findings"]:
        out += ["No findings.", ""]
    out.append("Robots verdicts (robots.txt only; CDN or WAF bot rules are not visible to this script):")
    for r in report["robots"].values():
        out.append(f"  {r['url']}: {r['state']}" + (f" (HTTP {r['status']})" if r["status"] else ""))
        if r["state"].startswith("allow all"):
            out.append("    every agent allowed")
        for token, v in r["agents"].items():
            total = v["allowed"] + len(v["disallowed"])
            line = f"    {token:<18} {v['allowed']}/{total} allowed"
            if v["disallowed"]:
                line += " - disallowed: " + ", ".join(v["disallowed"][:3]) + (" ..." if len(v["disallowed"]) > 3
                                                                              else "")
            out.append(line)
    out.append(f"Checked {report['urls_checked']} of {report['urls_found']} URL(s)" +
               (f"; {report['urls_not_checked']} not checked (--max-urls)." if report["urls_not_checked"] else "."))
    s = report["summary"]
    out.append(f"Summary: {s['blocker']} blocker, {s['high']} high, {s['medium']} medium, {s['low']} low. "
               f"Exit {report['exit']}.")
    return "\n".join(out)


# --- self-test -----------------------------------------------------------------------------------------

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class FakeTransport:
    """Answers from a JSON manifest: URL -> {status, headers, body} or {"network_error": true}."""

    def __init__(self, manifest: dict, down: bool = False):
        self.manifest, self.down, self.calls = manifest, down, []

    def __call__(self, url, timeout):
        self.calls.append(url)
        r = self.manifest.get(url)
        if self.down or (r and r.get("network_error")):
            raise NetworkError("connection refused")
        if r is None:
            return 404, {"content-type": ["text/html"]}, b"<title>Not found</title>"
        hdrs = {k.lower(): (v if isinstance(v, list) else [v]) for k, v in r.get("headers", {}).items()}
        hdrs.setdefault("content-type", ["text/html; charset=utf-8"])
        return r.get("status", 200), hdrs, r.get("body", "").encode()


def _fixed_now():
    return dt.datetime(2026, 11, 4, 9, 30, tzinfo=dt.timezone.utc)


def _run_fake(manifest, argv, down=False):
    args = build_parser().parse_args(argv)
    validate(args)
    fake = FakeTransport(manifest, down)
    naps: list[float] = []
    fetcher = Fetcher(fake, args.delay, 5, sleep=naps.append, clock=lambda: 0.0)
    return run(args, fetcher, now=_fixed_now), fake, naps


def rep_group_findings(manifest: dict) -> list[dict]:
    W = "https://www.example.com"
    m = dict(manifest)
    m[f"{W}/robots.txt"] = {"status": 200, "headers": {"Content-Type": "text/plain"},
                            "body": "User-agent: OAI-SearchBot\nDisallow: /\n"}
    report, _, _ = _run_fake(m, [f"{W}/en/features", f"{W}/de/funktionen", f"{W}/en/plans"])
    return report["findings"]


def self_test() -> int:
    fails: list[str] = []
    check = lambda ok, msg: ok or fails.append(msg)  # noqa: E731
    W = "https://www.example.com"
    try:
        manifest = json.loads((FIXTURES / "site-check-web.json").read_text(encoding="utf-8"))
        targets = [line for line in (FIXTURES / "site-check-urls.txt").read_text(encoding="utf-8").splitlines()]
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            uf = Path(d) / "urls.txt"
            uf.write_text("\n".join(targets) + "\n", encoding="utf-8")
            report, fake, naps = _run_fake(manifest, ["--urls-file", str(uf), "--delay", "1"])
        got = {(f["check"], f["url"]) for f in report["findings"]}
        sev = {(f["check"], f["url"]): f["severity"] for f in report["findings"]}
        expected = {
            ("redirect-chain", f"{W}/en/pricing?utm_source=newsletter"): "medium",
            ("redirect-temporary", f"{W}/en/pricing?utm_source=newsletter"): "medium",
            ("query-lost", f"{W}/en/pricing?utm_source=newsletter"): "medium",
            ("meta-refresh", f"{W}/en/old-pricing"): "high",
            ("noindex", f"{W}/en/blog/launch"): "blocker",
            ("noindex", f"{W}/en/blog/archive"): "blocker",
            ("robots-blocked", f"{W}/en/blog/archive"): "high",
            ("canonical-home", f"{W}/en/integrations"): "high",
            ("canonical-cross-host", f"{W}/en/security"): "high",
            ("canonical-not-self", f"{W}/en/help/setup"): "medium",
            ("h1-missing", f"{W}/en/help/setup"): "high",
            ("text-missing", f"{W}/en/help/setup"): "blocker",
            ("jsonld-invalid", f"{W}/en/compare"): "high",
            ("jsonld-retired", f"{W}/en/compare"): "low",
            ("jsonld-self-review", f"{W}/en/compare"): "high",
            ("canonical-missing", f"{W}/en/compare"): "medium",
            ("jsonld-self-review", f"{W}/en/reviews"): "high",
            ("hreflang-invalid-code", f"{W}/en/rooms"): "high",
            ("hreflang-no-self", f"{W}/en/rooms"): "high",
            ("hreflang-no-x-default", f"{W}/en/rooms"): "low",
            ("hreflang-target-status", f"{W}/en/rooms"): "high",
            ("hreflang-not-reciprocal", f"{W}/en/rooms"): "high",
            ("canonical-other-language", f"{W}/de/preise"): "high",
            ("status", f"{W}/en/gone"): "blocker",
            ("redirect-loop", f"{W}/en/loop"): "blocker",
            ("redirect-downgrade", f"{W}/en/secure"): "high",
            ("robots-blocked", f"{W}/private/old-terms"): "blocker",
            ("robots-unreachable", "https://shop.example.com/robots.txt"): "blocker",
            ("unreachable", "https://down.example.net/"): "high",
            ("title-duplicate", f"{W}/en/integrations, {W}/en/security"): "medium",
            ("canonical-target-status", f"{W}/en/help/setup"): "high",
            ("status", f"{W}/en/help/start"): "blocker",
        }
        for key, s in expected.items():
            check(key in got, f"missing finding {key[0]} on {key[1]}")
            check(key not in got or sev[key] == s, f"{key[0]} on {key[1]}: severity {sev.get(key)}, want {s}")
        clean = {f"{W}/en/features", f"{W}/de/funktionen", f"{W}/en/plans", "https://shop.example.com/",
                 f"{W}/en/token-page?token=abc123secret", f"{W}/private/press"}
        for f in report["findings"]:
            check(f["url"] not in clean, f"false positive {f['check']} on clean page {f['url']}")
            check((f["check"], f["url"]) in expected, f"unexpected finding {f['check']} on {f['url']}")
        check(not any(f["check"] == "robots-blocked" and "shop.example.com" in f["url"] for f in report["findings"]),
              "unreachable robots.txt must not also produce robots-blocked findings")
        rooms = next(f for f in report["findings"] if f["check"] == "hreflang-target-status")
        check("en-GB=https://www.example.com/en-gb/rooms redirects to" in rooms["evidence"] and
              "fr=https://www.example.com/fr/chambres answers 404" in rooms["evidence"],
              f"hreflang targets that redirect or fail must both be named: {rooms['evidence']}")
        check(fake.calls.count(f"{W}/en/loop") == 1, "a redirect loop must stop at the first repeated URL")
        archive = next(f for f in report["findings"] if f["check"] == "robots-blocked" and "archive" in f["url"])
        check("Claude-SearchBot" in archive["evidence"] and "Googlebot" not in archive["evidence"],
              "robots-blocked on the archive must name Claude-SearchBot only")
        uf2 = None
        with tempfile.TemporaryDirectory() as d2:
            uf2 = Path(d2) / "urls.txt"
            uf2.write_text("\n".join(targets) + "\n", encoding="utf-8")
            accepted_report, _, _ = _run_fake(manifest, ["--urls-file", str(uf2), "--delay", "1",
                                                         "--accept-block", "Claude-SearchBot"])
        check(not any(f["check"] == "robots-blocked" and "archive" in f["url"] for f in accepted_report["findings"]),
              "a block named with --accept-block must not be a finding")
        check(any(f["check"] == "noindex" and "archive" in f["url"] for f in accepted_report["findings"]),
              "--accept-block must not hide other findings on the same URL")
        check(sum(1 for f in rep_group_findings(manifest) if f["check"] == "robots-blocked") == 1,
              "the same robots.txt block on several URLs must be one finding with a URL group")
        check(not any(f["check"] == "robots-blocked" and f["url"] == f"{W}/en/blog/launch" for f in report["findings"]),
              "a longer Allow in a second group for the same agent must win")
        ag = report["robots"][W]["agents"]
        check(ag["GPTBot"]["allowed"] == 0 and len(ag["GPTBot"]["disallowed"]) > 0,
              "GPTBot (Disallow: /) must be disallowed everywhere")
        check(not any("GPTBot" in f["evidence"] for f in report["findings"]),
              "training agents are verdicts, not findings")
        check(f"{W}/de/funktionen" not in ag["PerplexityBot"]["disallowed"],
              "Allow and Disallow of equal length: Allow must win")
        check(report["exit"] == 1, f"exit must be 1 with blocker findings, got {report['exit']}")
        text = render_text(report)
        check("abc123secret" not in redact(text) and "abc123secret" not in redact(json.dumps(report)),
              "a token in a query string must be redacted from the output")
        blocks = [b for b in text.split("\n\n") if b.startswith("[severity: ")]
        check(len(blocks) == len(report["findings"]), "text mode must print one block per finding")
        check(all(re.match(r"\[severity: (blocker|high|medium|low)\] \S.*\nEvidence: .+\nFix: .+\nVerify: .+$", b)
                  for b in blocks), "text mode must follow the finding format exactly")
        check("Exit 1." in text, "text mode must end with the exit code")
        check(all(n <= 1.0 for n in naps) and len(naps) > 5, "requests to one host must be spaced by --delay")
        check(fake.calls.count(f"{W}/robots.txt") == 1, "robots.txt must be fetched once per host")
        check(f"{W}/de/zimmer" in fake.calls, "hreflang targets outside the set must be fetched")
        check("@" not in USER_AGENT and "site-check" in USER_AGENT, "User-Agent must name the tool, no email")

        # Cap: counts every page fetched, including hreflang targets.
        with tempfile.TemporaryDirectory() as d:
            uf = Path(d) / "urls.txt"
            uf.write_text("\n".join(targets) + "\n", encoding="utf-8")
            capped, fake2, _ = _run_fake(manifest, ["--urls-file", str(uf), "--max-urls", "3"])
        check(capped["urls_checked"] == 3 and capped["urls_not_checked"] == len(targets) - 3,
              f"--max-urls: checked {capped['urls_checked']}")
        check(len([u for u in fake2.calls if not u.endswith("robots.txt")]) <= 3 + 2 * 3,
              "--max-urls must bound the number of page requests")

        # Sitemap index with a child sitemap; a sitemap entry that redirects.
        sm, _, _ = _run_fake(manifest, ["--sitemap", f"{W}/sitemap.xml"])
        check(sm["urls_found"] == 3, f"sitemap index: expected 3 URLs, got {sm['urls_found']}")
        check(any(f["check"] == "sitemap-redirect" and f["url"] == f"{W}/en/moved" for f in sm["findings"]),
              "a redirecting sitemap entry must be reported")
        sm404, _, _ = _run_fake(manifest, ["--sitemap", f"{W}/missing-sitemap.xml"])
        check(any(f["check"] == "sitemap-status" for f in sm404["findings"]) and sm404["exit"] == 1,
              "a sitemap that answers 404 is a high finding")

        # Network down: exit 3, nothing reported as checked.
        try:
            _run_fake(manifest, [f"{W}/en/features"], down=True)
            fails.append("all requests failing at the network level must raise NoNetwork (exit 3)")
        except NoNetwork:
            pass
        try:
            _run_fake(manifest, ["--sitemap", f"{W}/sitemap.xml"], down=True)
            fails.append("an unreachable sitemap with no other input must raise NoNetwork (exit 3)")
        except NoNetwork:
            pass
        ok, _, _ = _run_fake(manifest, [f"{W}/en/features", f"{W}/de/funktionen"])
        check(ok["exit"] == 0 and not ok["findings"], f"a clean pair must exit 0, got {ok['findings']}")
        variant = dict(manifest)
        variant[f"{W}/en/features?utm_source=x"] = manifest[f"{W}/en/features"]
        ok2, _, _ = _run_fake(variant, [f"{W}/en/features?utm_source=x", f"{W}/de/funktionen"])
        check(not ok2["findings"], "a tracking-parameter variant must be judged as its clean URL: "
              f"{[f['check'] for f in ok2['findings']]}")

        # Usage errors.
        for argv in (["ftp://example.com/x"], ["--max-urls", "501", f"{W}/"], ["--delay", "0.1", f"{W}/"], [],
                     ["--root-dir", str(FIXTURES / "site-check-local")]):
            try:
                args = build_parser().parse_args(argv)
                validate(args)
                fails.append(f"usage error expected for {argv}")
            except UsageError:
                pass

        # Units: hreflang codes, robots matching, URL normalisation, noindex parsing.
        check("GB" in (hreflang_problem("en-UK") or ""), "en-UK must point to GB")
        check("hyphen" in (hreflang_problem("en_US") or ""), "en_US must point to the hyphen")
        for code, want_ok in (("en", True), ("en-GB", True), ("de-AT", True), ("zh-Hant", True), ("zh-Hant-TW", True),
                              ("x-default", True), ("DE", True), ("en-UK", False), ("en_US", False), ("AT", False),
                              ("eng", False), ("en-XX", False), ("en-US-x", False)):
            check((hreflang_problem(code) is None) == want_ok, f"hreflang code {code}: {hreflang_problem(code)}")
        groups = parse_robots("User-agent: *\nDisallow: /private/\nAllow: /private/press$\n"
                              "User-agent: Foo\nUser-agent: Bar\nDisallow: /*.pdf$\nDisallow: /tmp\n")
        check(robots_verdict(groups, "Googlebot", "/private/press")[0] is True, "robots: $-anchored Allow wins")
        check(robots_verdict(groups, "Googlebot", "/private/press-kit")[0] is False, "robots: $ anchors the end")
        check(robots_verdict(groups, "bar", "/a/b.pdf")[0] is False, "robots: * wildcard and grouped agents")
        check(robots_verdict(groups, "Bar", "/a/b.pdf?x=1")[0] is True, "robots: $ must not match before a query")
        check(robots_verdict(groups, "Foo", "/private/x")[0] is True, "robots: a named group replaces *")
        check(robots_verdict(groups, "Foo", "/tmpfiles")[0] is False, "robots: patterns are prefixes")
        check(robots_verdict(parse_robots("User-agent: *\nDisallow:\n"), "x", "/")[0] is True,
              "robots: empty Disallow allows")
        check(norm_url("HTTPS://WWW.Example.com:443") == "https://www.example.com/", "norm_url: case, port, path")
        check(norm_url("https://www.example.com/a#x") == "https://www.example.com/a", "norm_url: fragment")
        check(noindex_sources([], ["googlebot: noindex, nofollow"]) and noindex_sources([], ["none"]) and
              not noindex_sources([], ["max-snippet: 20"]) and noindex_sources([("robots", "NoIndex")], []),
              "noindex parsing")

        # --root-dir: built site from disk, pretty URLs, traversal refused.
        local = FIXTURES / "site-check-local"
        args = build_parser().parse_args(["--root-dir", str(local), "--base-url", W, "--text"])
        validate(args)
        lt = LocalTransport(local, W)
        rep_local = run(args, Fetcher(lt, 0, 5), now=_fixed_now)
        lchecks = {(f["check"], f["url"]) for f in rep_local["findings"]}
        check(("canonical-home", f"{W}/en/features") in lchecks, "local: canonical-home on en/features.html")
        check(("hreflang-not-reciprocal", f"{W}/en/features") in lchecks, "local: one-way hreflang")
        check(("h1-missing", f"{W}/en/pricing") in lchecks, "local: client-rendered pricing page")
        check(("meta-refresh", f"{W}/en/old-pricing") in lchecks, "local: meta refresh")
        check(not any(u.endswith(".html") for _, u in lchecks), "local: URLs are extensionless by default")
        check(lt.resolve(f"{W}/../site-check-web.json") is None and lt.resolve(f"{W}/%2e%2e/site-check-urls.txt") is None,
              "local: paths outside --root-dir must not resolve")
        try:
            lt.resolve("https://other.example.org/")
            fails.append("local: another host must be out of scope")
        except OutOfScope:
            pass
    except Exception as e:  # a crash is a failure, reported like one
        import traceback
        fails.append(f"unexpected {e.__class__.__name__}: {e} {traceback.format_exc(limit=3)}")

    for f in fails:
        print("FAIL", f, file=sys.stderr)
    if fails:
        return 1
    print("site_check.py self-test: ok (redirects, meta refresh, query loss, noindex, canonical, hreflang, JSON-LD, "
          "server-HTML text, robots.txt per agent, duplicate titles, sitemap index, cap, delay, redaction, exit 3, "
          "usage errors, --root-dir)")
    return 0


# --- CLI -----------------------------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="site_check.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="*", help="URLs to check")
    ap.add_argument("--urls-file", help='one URL per line; "URL<TAB>text" also checks that text on that URL')
    ap.add_argument("--sitemap", action="append", help="sitemap or sitemap index URL (repeatable)")
    ap.add_argument("--root-dir", help="built static site to check from disk instead of the network")
    ap.add_argument("--base-url", help="URL that --root-dir is served at, e.g. https://www.example.com")
    ap.add_argument("--keep-html-ext", action="store_true", help="with --root-dir: URLs keep .html")
    ap.add_argument("--expect-text", action="append", help="text that must be in the server HTML of every URL")
    ap.add_argument("--max-urls", type=int, default=MAX_URLS_DEFAULT, help=f"pages to fetch, at most {MAX_URLS_HARD}")
    ap.add_argument("--delay", type=float, default=None, help="seconds between requests to one host (default 1.0)")
    ap.add_argument("--timeout", type=float, default=15.0, help="seconds per request (default 15)")
    ap.add_argument("--accept-block", action="append", metavar="TOKEN",
                    help="user-agent token whose robots.txt block an ADR records; listed as a verdict, not a finding")
    ap.add_argument("--text", action="store_true", help="print findings in the skill's finding format")
    ap.add_argument("--self-test", action="store_true", help="run offline checks against scripts/fixtures and exit")
    return ap


def validate(args) -> None:
    if not (args.urls or args.urls_file or args.sitemap or args.root_dir):
        raise UsageError("give URLs, --urls-file, --sitemap or --root-dir")
    for u in args.urls:
        check_url_arg(u)
    if not 1 <= args.max_urls <= MAX_URLS_HARD:
        raise UsageError(f"--max-urls must be between 1 and {MAX_URLS_HARD}")
    if args.root_dir:
        if not args.base_url:
            raise UsageError("--root-dir needs --base-url")
        check_url_arg(args.base_url)
        if not Path(args.root_dir).is_dir():
            raise UsageError(f"--root-dir {args.root_dir} is not a directory")
        if args.delay is None:
            args.delay = 0.0
    if args.delay is None:
        args.delay = 1.0
    if not args.root_dir and args.delay < MIN_DELAY:
        raise UsageError(f"--delay must be at least {MIN_DELAY} s over the network")


def run(args, fetcher: Fetcher, now=now_utc) -> dict:
    rep = Report(now, "build output in --root-dir, no JavaScript" if args.root_dir else
                 "server HTML without JavaScript")
    stats = {"answers": 0, "network_failures": 0}
    targets = build_targets(args, fetcher, rep, stats)
    return check_site(targets, fetcher, args.max_urls, rep, stats, now=now,
                      accepted=frozenset(args.accept_block or []))


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.self_test:
        return self_test()
    try:
        validate(args)
        if args.root_dir:
            transport = LocalTransport(Path(args.root_dir), args.base_url)
        else:
            transport = urllib_transport
        report = run(args, Fetcher(transport, args.delay, args.timeout))
    except (UsageError, NoNetwork) as e:
        print(json.dumps({"error": redact(str(e)), "exit": e.code}), file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(json.dumps({"error": redact(f"unexpected {e.__class__.__name__}: {e}"), "exit": 4}), file=sys.stderr)
        return 4
    print(redact(render_text(report) if args.text else json.dumps(report, indent=1, ensure_ascii=False)))
    return report["exit"]


if __name__ == "__main__":
    sys.exit(main())
