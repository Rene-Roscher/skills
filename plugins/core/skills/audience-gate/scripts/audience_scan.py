#!/usr/bin/env python3
"""Find text that was written for the team and reached the reader (an audience leak).

Scans what readers get, not what authors wrote: rendered HTML (a static build directory, single files, or a
live site via its sitemap plus the pages those pages link to), and, as an early warning, locale and content
files (JSON string values, Markdown outside code, YAML, plain text).

For HTML it reads visible text, alt, title, aria-label, aria-description and placeholder attributes, the
title tag, description and Open Graph meta, every string in JSON-LD, and HTML comments. Text inside code and
pre elements is skipped, because code examples may show placeholders on purpose. It also checks that the
document ends exactly once with the closing html tag: bytes after it come from a build that wrote one file
twice at the same time.

Finds, by code (E = error, W = warning):
  P01 E  provenance note: "according to the code", "source: the plan configuration", "checked against the source"
  R01 E  roadmap or process: "coming in phase 3", "in a later version", "not built yet", backlog, MVP, TBD
  R02 W  hedge on current state: "currently still", "derzeit noch"
  V01 W  version threshold: "since version 0.1.5", "ab Version 2" (fine for third-party software, allow it)
  I01 E  feature flag or rollout switch named in reader text
  I02 E  class-like or file-like identifier in prose (BillingService, foo.php)
  I03 W  "internally a", "under the hood", "intern ein"
  X01 E  placeholder or unrendered value: <Version>, {count}, {{ name }}, undefined, NaN, [object Object], lorem ipsum
  X02 E  TODO, FIXME, XXX
  K01 E  a locale key shown as text (exact match with --locale-keys, or a whole value shaped like nav.abuse)
  M01 W  the text talks about itself: "this page lists", "diese Liste kommt direkt aus"
  D01 W  reference to structure that may not exist here: "the second group", "der letzte Punkt", "see below"
  S01 W  server-rendered start state: a lone 0,00 %, "Loading", "wird geladen"
  L01 W  sentence in the other language than the page (en pages with German, de pages with English)
  C01 W  HTML comment with prose in it
  B01 E  bytes after the closing html tag, or more than one closing html tag
  N01 E  a term from --deny (project code names, internal hostnames)

Silence a finding with an allow file (--allow): one regular expression per line, matched against the
finding's snippet, followed by "# reason" (required). Prefix "GLOB :: " to limit it to matching locations.

Usage:
  audience_scan.py PATH|URL [...] [--site URL] [--locale-keys FILE ...] [--allow FILE] [--deny FILE]
                   [--extract DIR] [--chunks N] [--min-html N] [--strict] [--quiet] [--jobs N]
  audience_scan.py --self-test

Output: "location: error|warning CODE message: «snippet»", summary on stderr.
Exit codes: 0 no errors (warnings allowed unless --strict), 1 findings or failed self-test, 2 usage error or
fewer HTML documents than --min-html.
Python 3.9 or later, standard library only.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "audience-scan/1.0"
TEXT_ATTRS = ("alt", "title", "aria-label", "aria-description", "placeholder")
META_NAMES = ("description", "keywords", "twitter:title", "twitter:description", "og:title",
              "og:description", "og:site_name", "og:image:alt", "twitter:image:alt")
SKIP_TEXT = ("script", "style", "code", "pre", "kbd", "samp", "head")
FRAMEWORK_COMMENTS = re.compile(r"^\s*(\[|\]|\[\]|v-if|v-show|teleport (start|end)( anchor)?|teleport anchor|"
                                r"-->|\s*)\s*$", re.I)

# --- rules ---------------------------------------------------------------------------------------------

I = re.I


@dataclass
class Rule:
    code: str
    severity: str  # "error" | "warning"
    message: str
    patterns: list
    kinds: tuple = ("text", "attr", "meta", "title", "jsonld", "source")


RULES = [
    Rule("P01", "error", "provenance note (how the text was sourced or checked)", [
        re.compile(r"\b(laut|gemäß|nach)\s+(dem\s+|der\s+|unserer?\s+)?(Quell)?(Code|Spec|Spezifikation|"
                   r"Konfiguration|Tarifkonfiguration|Config|Seeder|Codebasis)\b", I),
        re.compile(r"\bwie (er|sie|es) im (Quell)?[Cc]ode steh", I),
        re.compile(r"\b(kommt|kommen|stammt|stammen|direkt) aus dem (Quell)?[Cc]ode\b", I),
        re.compile(r"\bgeprüft (am|gegen (den|die|das|unseren?|die eigene)) (Quell)?(code|Code|Tarif|"
                   r"Konfiguration|eigene)", I),
        re.compile(r"\bQuelle(:| ist| sind)\s+(die |der |das )?[\wäöü-]*(konfiguration|feldliste|code)\b", I),
        re.compile(r"\b(according to (the |our )?|per (the |our )|as (it is |they are )?(configured|defined|set|"
                   r"written) in (the |our )?)(code|codebase|source code|spec|config(uration)?|plan configuration|"
                   r"seeder|schema)\b", I),
        re.compile(r"\bchecked against (the |our |[\w-]+'s )?(own )?(source code|code|codebase|plan configuration|"
                   r"config(uration)?)\b", I),
        re.compile(r"\bstraight from the (code|codebase|source)\b", I),
        re.compile(r"\bsource:\s*(the )?([\w-]+ )?(configuration|config|code|field list)\b", I),
    ]),
    Rule("R01", "error", "roadmap or process statement", [
        # "Stufe 1" and "stage 2" stay allowed: products name escalation levels that way.
        re.compile(r"\b(Phase|Ausbaustufe|Meilenstein|Sprint|Iteration|milestone)\s+\d+\b", I),
        re.compile(r"\bkommt (bald|später|demnächst|in Kürze|in (einer|der) (späteren|nächsten)|mit (Version|"
                   r"v?\d|Phase|dem nächsten|der nächsten))", I),
        re.compile(r"\b(in|mit) (einer|der) (späteren|kommenden|nächsten) (Version|Ausbaustufe|Release|Fassung)\b",
                   I),
        re.compile(r"\b(folgt|folgen|kommt|kommen) (bald|später|demnächst|in einer späteren)\b", I),
        re.compile(r"\b(bald|demnächst|in Kürze|später) (verfügbar|erhältlich|da|online|freigeschaltet)\b", I),
        re.compile(r"\b(available|launching|arriving) (soon|later)\b", I),
        re.compile(r"\bnoch nicht (gebaut|implementiert|umgesetzt|fertig|programmiert|freigeschaltet)\b", I),
        re.compile(r"\b(geplant|vorgesehen) (für|ab|in|mit) (Q[1-4]|20\d\d|Version|v?\d|Phase|dem nächsten)", I),
        re.compile(r"\b(auf der|in der|unsere[rn]?) Roadmap\b", I),
        re.compile(r"\b(wandert|wandern|kommt|kommen|landet|landen|steht|stehen|liegt|liegen) (erst ?mal |vorerst "
                   r"|noch )?(in den|im) Backlog\b", I),
        re.compile(r"\bcoming (soon|later|next|in (a|the|version|v?\d|Q[1-4])|with (version|v?\d|phase|the next))",
                   I),
        re.compile(r"\b(in|with) (a|the) (later|future|upcoming|next) (version|release|update|phase)\b", I),
        re.compile(r"\bwill (ship|land|arrive|come|be added|follow) (in (a|the) (later|future|next)|with|later|soon)\b",
                   I),
        re.compile(r"\b(not yet (built|implemented|shipped|wired up|finished)|not (built|implemented|shipped) yet)\b",
                   I),
        re.compile(r"\b(planned|scheduled|slated|targeted) for (Q[1-4]|20\d\d|v?\d|version|phase|the next)", I),
        re.compile(r"\bon (the|our) roadmap\b", I),
        re.compile(r"\b(goes|go|went|is|are|sits|stays|lands) (in|into|on) (the|our) backlog\b", I),
        re.compile(r"\bMVP\b"),
        re.compile(r"\bTBD\b"),
    ]),
    Rule("R02", "warning", "hedge on the current state; describe what happens today", [
        re.compile(r"\b(derzeit|aktuell|momentan|vorerst) noch\b", I),
        re.compile(r"\b(currently|for now|still) (still |not )?(yet|only|counts?|limited)\b", I),
        re.compile(r"\bcurrently still\b", I),
    ]),
    Rule("V01", "warning", "version threshold; fine for third-party software, never for your own release history",
         [re.compile(r"\b(ab|seit|vor|bis) (der )?(Version|Release|v)\s?\d+(\.\d+)*\b", I),
          re.compile(r"\b(since|from|as of|starting (with|from|at)|before|until|prior to) (version|release|v)\s?"
                     r"\d+(\.\d+)*\b", I)]),
    Rule("I01", "error", "feature flag or rollout switch named in reader text", [
        re.compile(r"\b(feature[- ]?flags?|rollout[- ]?(switch|flag|schalter)|kill[- ]?switch|behind a (flag|"
                   r"switch|toggle)|hinter (einem|dem) (Schalter|Flag)|Rollout-Schalter)\b", I),
    ]),
    Rule("I02", "error", "code identifier in prose", [
        re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+(Service|Controller|Action|Job|Resolver|Command|Provider|"
                   r"Repository|Factory|Seeder|Listener|Middleware|Handler|Manager|Builder|Writer)\b"),
        re.compile(r"(?<![\w./-])[\w-]+/[\w./-]+\.(php|go|py|rb|java|kt|vue|tsx?|jsx?)\b"),
    ]),
    Rule("I03", "warning", "implementation view; say what the reader sees instead", [
        re.compile(r"\bintern (ein|eine|als|nur)\b", I),
        re.compile(r"\bunder the hood\b", I),
        re.compile(r"\binternally (a|an|the|stored|modelled|modeled|treated)\b", I),
    ]),
    Rule("X01", "error", "placeholder or unrendered value", [
        re.compile(r"<[A-Za-z][\w-]{1,40}>"),
        re.compile(r"\{\{\s*[\w.$-]+\s*\}\}"),
        re.compile(r"(?<![\w$/])\{[a-z_][\w.]*\}(?!/)"),  # /items/{id}/ is an API path, not a placeholder
        re.compile(r"(?<![\w-])(undefined|NaN)(?![\w-])"),
        re.compile(r"\[object Object\]"),
        re.compile(r"\blorem ipsum\b", I),
        re.compile(r"%[sd]\b|\{\d\}"),
    ]),
    Rule("X02", "error", "work marker", [re.compile(r"\b(TODO|FIXME|XXX)\b")]),
    Rule("M01", "warning", "the text talks about itself instead of the reader's task", [
        re.compile(r"\b(diese|die) (Seite|Liste|Tabelle|Übersicht|Abschnitt)\s+(listet|zeigt|beschreibt|kommt|"
                   r"stammt|wird (automatisch )?(erzeugt|generiert))", I),
        re.compile(r"\b(this|the) (page|list|table|section)\s+(lists|shows|describes|comes|is (auto-?)?generated|"
                   r"was (auto-?)?generated)\b", I),
    ]),
    Rule("D01", "warning", "points at structure that may not exist on this page", [
        re.compile(r"\b(zur|die|der|in der) (ersten|zweiten|dritten|letzten) (Gruppe|Kategorie)\b", I),
        re.compile(r"\bder letzte Punkt\b", I),
        re.compile(r"\b(the|in the) (first|second|third|last) group\b", I),
        re.compile(r"\b(that|the) last point\b", I),
        re.compile(r"\b(wie oben|siehe oben|siehe unten|wie unten)\b", I),
        re.compile(r"\b(as (mentioned |shown |described )?above|see below)\b", I),
    ]),
    Rule("S01", "warning", "server-rendered start state; render the real value", [
        re.compile(r"^\s*0([.,]0+)?\s?%\s*$"),
        re.compile(r"^\s*(Loading|Wird geladen|Lädt|[\w ]+ werden geladen|Loading [\w ]+)\s*(…|\.\.\.)?\s*$", I),
    ], kinds=("text",)),
]

SOURCE_PLACEHOLDERS = [
    re.compile(r"<[A-Z][a-z]{2,30}>"),
    re.compile(r"\[object Object\]"),
    re.compile(r"\blorem ipsum\b", I),
]

DE_WORDS = set("und der die das nicht mit für ist eine ein auf von zu im bei sind wird oder auch nach dass wenn "
               "deine dein du sich als über".split())
EN_WORDS = set("the and of to is with for are this that your you not from on by it be can".split())
HOST_TLDS = set("de com net org io cloud app dev eu co uk at ch fr nl info biz me ai sh tech page".split())
FILE_EXTS = set("tf tfvars txt json yml yaml md toml ini conf env log csv ics pdf html xml js mjs ts sh py php go "
                "rb sql zip png svg webp jpg gif lock".split())
DOTTED = re.compile(r"(?<![\w.])[A-Za-z][\w-]*(?:\.[\w-]+)+(?![\w.])")  # tokens that could be locale keys
PER_DOCUMENT_CAP = 3  # repeated L01/D01 findings in one document are summarised after this many


# --- extraction ----------------------------------------------------------------------------------------

@dataclass
class Segment:
    kind: str
    text: str
    where: str = ""


@dataclass
class Page:
    location: str
    lang: str = ""
    segments: list = field(default_factory=list)
    tail_problem: str = ""
    is_html: bool = False


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.skip = []
        self.in_title = False
        self.in_jsonld = False
        self.buf = []
        self.jsonld = []
        self.segments = []

    def _flush(self):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if text:
            self.segments.append(Segment("text", text))

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"].split("-")[0].lower()
        if tag == "script" and "ld+json" in a.get("type", ""):
            self.in_jsonld = True
            self.jsonld.append("")
        if tag == "title" and not self.skip:
            self.in_title = True
        if tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key in META_NAMES and a.get("content"):
                self.segments.append(Segment("meta", a["content"], key))
        for name in TEXT_ATTRS:
            if a.get(name, "").strip() and tag not in ("meta", "link"):
                self.segments.append(Segment("attr", a[name].strip(), f"{tag}[{name}]"))
        if tag in ("input", "button") and a.get("type") in ("submit", "button") and a.get("value"):
            self.segments.append(Segment("attr", a["value"], f"{tag}[value]"))
        if tag in SKIP_TEXT:
            self._flush()
            self.skip.append(tag)
        elif tag in ("br", "p", "div", "li", "td", "th", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "dt", "dd",
                     "section", "article", "figcaption", "button", "a", "span", "label", "summary", "option"):
            self._flush()

    def handle_endtag(self, tag):
        if tag == "script" and self.in_jsonld:
            self.in_jsonld = False
        if tag == "title":
            self.in_title = False
        if self.skip and self.skip[-1] == tag:
            self.skip.pop()
            return
        if not self.skip:
            self._flush()

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld[-1] += data
        elif self.in_title:
            if data.strip():
                self.segments.append(Segment("title", data.strip(), "title"))
        elif not self.skip:
            self.buf.append(data)

    def handle_comment(self, data):
        if not FRAMEWORK_COMMENTS.match(data):
            self.segments.append(Segment("comment", re.sub(r"\s+", " ", data).strip()))


def jsonld_strings(node, path="jsonld"):
    skip = {"@type", "@id", "@context", "url", "logo", "image", "sameAs", "item", "email", "telephone",
            "inLanguage", "contentUrl", "thumbnailUrl", "embedUrl", "priceCurrency", "addressCountry"}
    if isinstance(node, dict):
        for k, v in node.items():
            if k not in skip:
                yield from jsonld_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from jsonld_strings(v, path)
    elif isinstance(node, str) and node.strip() and not re.match(r"^(https?:|mailto:|/)", node):
        yield path, node


def parse_html(location, raw):
    page = Page(location, is_html=True)
    stripped = raw.rstrip()
    closes = len(re.findall(r"</html\s*>", stripped, re.I))
    if closes > 1:
        page.tail_problem = f"{closes} closing html tags"
    elif closes == 1 and not re.search(r"</html\s*>$", stripped, re.I):
        tail = stripped[re.search(r"</html\s*>", stripped, re.I).end():]
        page.tail_problem = f"bytes after </html>: {tail[:60]!r}"
    ex = Extractor()
    try:
        ex.feed(raw)
        ex.close()
    except Exception as err:  # malformed markup must not stop the scan
        page.segments.append(Segment("comment", f"parser stopped: {err}"))
    ex._flush()
    page.lang = ex.lang
    page.segments = ex.segments + page.segments
    for block in ex.jsonld:
        try:
            data = json.loads(block)
        except ValueError:
            continue
        for where, text in jsonld_strings(data):
            page.segments.append(Segment("jsonld", text, where))
    return page


def lang_from_path(path):
    for part in reversed(Path(path).parts):
        m = re.match(r"^(?:[\w-]*?[-_.])?(de|en)(?:[-_][A-Za-z]{2})?(?:\.\w+)?$", part)
        if m:
            return m.group(1)
    return ""


def parse_source(path):
    page = Page(str(path), lang_from_path(path))
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".json":
        try:
            data = json.loads(text)
        except ValueError as err:
            page.segments.append(Segment("comment", f"invalid JSON: {err}"))
            return page

        def walk(node, key):
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, f"{key}.{k}" if key else k)
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    walk(v, f"{key}[{i}]")
            elif isinstance(node, str):
                page.segments.append(Segment("source", node, key))
        walk(data, "")
        return page
    in_fence = False
    for no, line in enumerate(text.splitlines(), 1):
        if suffix in (".md", ".mdx") and re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", " ", line) if suffix in (".md", ".mdx") else line
        if line.strip():
            page.segments.append(Segment("source", line.strip(), f"line {no}"))
    return page


# --- fetching ------------------------------------------------------------------------------------------

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8", "replace")
    except Exception:
        return ""


def site_urls(site, jobs):
    site = site.rstrip("/")
    found, queue = set(), [site + "/sitemap.xml"]
    while queue:
        xml = fetch(queue.pop())
        for loc in re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml):
            (queue.append(loc) if loc.endswith(".xml") and loc not in found else found.add(loc))
    pages = {u for u in found if not u.endswith(".xml")}
    host = urllib.parse.urlsplit(site).netloc
    extra = set()
    with cf.ThreadPoolExecutor(jobs) as ex:
        for raw in ex.map(fetch, sorted(pages)):
            for href in re.findall(r'href="([^"#?]+)', raw):
                url = urllib.parse.urljoin(site + "/", href)
                parts = urllib.parse.urlsplit(url)
                if parts.netloc == host and not re.search(r"\.(png|svg|webp|jpe?g|gif|ico|xml|zip|css|js|json|"
                                                         r"txt|pdf|webmanifest|woff2?)$", parts.path, re.I):
                    extra.add(url.rstrip("/") or url)
    known = {u.rstrip("/") for u in pages}
    return sorted(pages | {u for u in extra if u.rstrip("/") not in known})


# --- checking ------------------------------------------------------------------------------------------

@dataclass
class Finding:
    location: str
    severity: str
    code: str
    message: str
    snippet: str


def snippet_around(text, m, width=70):
    start, end = max(0, m.start() - width), min(len(text), m.end() + width)
    return ("…" if start else "") + text[start:end] + ("…" if end < len(text) else "")


def language_residue(text, lang):
    words = re.findall(r"[A-Za-zÄÖÜäöüß']+", text.lower())
    if lang == "en" and len(words) >= 6:
        hits = sum(w in DE_WORDS for w in words)
        return hits >= 3 or bool(re.search(r"[äöüß]", text) and hits >= 2)
    if lang == "de" and len(words) >= 8:
        return sum(w in EN_WORDS for w in words) >= 4 and sum(w in DE_WORDS for w in words) <= 1
    return False


def key_shaped(text, keys):
    t = text.strip()
    if keys and t in keys:
        return True
    m = re.fullmatch(r"[a-z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)+", t)
    last = t.rsplit(".", 1)[-1].lower()
    return bool(m) and last not in HOST_TLDS and last not in FILE_EXTS and not re.search(r"\d+\.\d+", t)


def check_page(page, keys, deny):
    out = []
    loc = page.location
    if page.tail_problem:
        out.append(Finding(loc, "error", "B01", "document does not end with one closing html tag",
                           page.tail_problem))
    for seg in page.segments:
        where = f"{loc} [{seg.kind}{' ' + seg.where if seg.where else ''}]"
        if seg.kind == "comment":
            if len(seg.text.split()) >= 3:
                out.append(Finding(where, "warning", "C01", "HTML comment with prose (public in the source)",
                                   seg.text[:160]))
            continue
        for rule in RULES:
            if seg.kind not in rule.kinds:
                continue
            # In locale and content files {name}, {{ name }} and %s are the interpolation the app fills in.
            patterns = SOURCE_PLACEHOLDERS if rule.code == "X01" and seg.kind == "source" else rule.patterns
            for pat in patterns:
                m = pat.search(seg.text)
                if m:
                    out.append(Finding(where, rule.severity, rule.code, rule.message, snippet_around(seg.text, m)))
                    break
        dotted = set(DOTTED.findall(seg.text)) if keys and seg.kind != "source" else set()
        if key_shaped(seg.text, keys) or dotted & keys:
            out.append(Finding(where, "error", "K01", "locale key shown as text", seg.text[:160]))
        for term in deny:
            m = re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", seg.text, re.I)
            if m:
                out.append(Finding(where, "error", "N01", "denied term", snippet_around(seg.text, m)))
        lang = page.lang or lang_from_path(loc)
        if seg.kind in ("text", "jsonld", "meta", "source") and language_residue(seg.text, lang):
            out.append(Finding(where, "warning", "L01", f"sentence not in the page language ({lang})",
                               seg.text[:160]))
    return summarise(out)


def summarise(findings):
    """Drop exact repeats; past PER_DOCUMENT_CAP, fold L01 and D01 of one document into one line."""
    seen, out, counts = set(), [], {}
    for f in findings:
        doc = f.location.split(" [")[0]
        key = (doc, f.code, f.snippet)
        if key in seen:
            continue
        seen.add(key)
        if f.code in ("L01", "D01"):
            counts[(doc, f.code)] = counts.get((doc, f.code), 0) + 1
            if counts[(doc, f.code)] > PER_DOCUMENT_CAP:
                continue
        out.append(f)
    for (doc, code), n in counts.items():
        if n > PER_DOCUMENT_CAP:
            out.append(Finding(doc, "warning", code, f"{n - PER_DOCUMENT_CAP} more like this in this document",
                               "summarised"))
    return out


def load_allow(path):
    rules = []
    if not path:
        return rules
    for no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if " # " not in line and not line.endswith("#"):
            raise SystemExit(f"{path}:{no}: allow entry needs '# reason'")
        body = line.rsplit(" # ", 1)[0].strip()
        glob, _, pattern = body.rpartition(" :: ")
        rules.append((glob.strip() or "*", re.compile(pattern.strip(), re.I)))
    return rules


def allowed(f, rules):
    return any(fnmatch.fnmatch(f.location.split(" [")[0], g) and p.search(f.snippet) for g, p in rules)


def load_keys(paths):
    keys = set()
    for p in paths or []:
        def walk(node, key):
            if isinstance(node, dict):
                for k, v in node.items():
                    walk(v, f"{key}.{k}" if key else k)
            elif key and "." in key and len(key) > 4:
                keys.add(key)
        walk(json.loads(Path(p).read_text(encoding="utf-8")), "")
    return keys


# --- extraction for the full read ----------------------------------------------------------------------

def write_extract(pages, dest, chunks):
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    sizes = []
    for page in pages:
        name = re.sub(r"[^\w.-]+", "_", re.sub(r"^https?://", "", page.location)).strip("_")[:150] or "index"
        body = [s.text for s in page.segments if s.kind == "text"]
        rest = [f"[{s.kind} {s.where}] {s.text}" for s in page.segments if s.kind != "text"]
        content = f"LOCATION {page.location}\nLANG {page.lang}\n\n" + "\n".join(body) + \
                  "\n\n--- ATTRIBUTES, META, JSON-LD, COMMENTS ---\n" + "\n".join(rest) + "\n"
        path = dest / f"{name}.txt"
        path.write_text(content, encoding="utf-8")
        sizes.append((len(content.split()), path))
    if chunks:
        buckets = [[0, []] for _ in range(chunks)]
        for words, path in sorted(sizes, reverse=True):
            b = min(buckets, key=lambda x: x[0])
            b[0] += words
            b[1].append(str(path.resolve()))
        for i, (words, paths) in enumerate(buckets, 1):
            (dest / f"chunk-{i}.list").write_text("\n".join(sorted(paths)) + "\n", encoding="utf-8")
            print(f"chunk-{i}.list: {len(paths)} files, {words} words", file=sys.stderr)


# --- main ----------------------------------------------------------------------------------------------

def collect(targets, site, jobs):
    pages, html_files, sources, urls = [], [], [], []
    for t in targets:
        if re.match(r"^https?://", t):
            urls.append(t)
            continue
        p = Path(t)
        if not p.exists():
            raise SystemExit(f"audience_scan: {t} does not exist")
        files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
        for f in files:
            if any(part in ("node_modules", ".git", "vendor") for part in f.parts):
                continue
            if f.suffix.lower() in (".html", ".htm"):
                html_files.append(f)
            elif f.suffix.lower() in (".json", ".md", ".mdx", ".yml", ".yaml", ".txt"):
                sources.append(f)
    if site:
        urls += site_urls(site, jobs)
    for f in html_files:
        pages.append(parse_html(str(f), f.read_text(encoding="utf-8", errors="replace")))
    for f in sources:
        pages.append(parse_source(f))
    with cf.ThreadPoolExecutor(jobs) as ex:
        for url, raw in zip(urls, ex.map(fetch, urls)):
            if raw:
                pages.append(parse_html(url, raw))
            else:
                print(f"{url}: could not fetch", file=sys.stderr)
    return pages


def run(args):
    pages = collect(args.targets, args.site, args.jobs)
    if not pages:
        print("audience_scan: nothing to check", file=sys.stderr)
        return 2
    html_docs = sum(p.is_html for p in pages)
    if args.min_html and html_docs < args.min_html:
        print(f"audience_scan: only {html_docs} HTML documents, expected at least {args.min_html}; the build or the "
              "crawl did not produce the pages, so a clean result would mean nothing", file=sys.stderr)
        return 2
    keys = load_keys(args.locale_keys)
    deny = [t.strip() for t in Path(args.deny).read_text(encoding="utf-8").splitlines()
            if t.strip() and not t.startswith("#")] if args.deny else []
    allow = load_allow(args.allow)
    findings = [f for page in pages for f in check_page(page, keys, deny) if not allowed(f, allow)]
    for f in findings:
        if not (args.quiet and f.severity == "warning"):
            print(f"{f.location}: {f.severity} {f.code} {f.message}: «{f.snippet}»")
    errors = sum(f.severity == "error" for f in findings)
    warnings = len(findings) - errors
    print(f"audience_scan: {len(pages)} documents, {errors} errors, {warnings} warnings", file=sys.stderr)
    if args.extract:
        write_extract(pages, args.extract, args.chunks)
    return 1 if errors or (args.strict and warnings) else 0


def self_test():
    """Every seeded leak in fixtures/bad must be reported with its code; fixtures/clean must stay silent.

    expected.txt lists one leak per line as "FILE | CODE | text from the snippet", so removing one pattern
    fails the test even when another rule still fires on the same file.
    """
    root = Path(__file__).resolve().parent / "fixtures"
    keys = load_keys([root / "bad" / "locale-keys.json"])
    deny = ["quasar-core"]

    def scan(path):
        page = parse_html(str(path), path.read_text(encoding="utf-8")) if path.suffix == ".html" \
            else parse_source(path)
        return check_page(page, keys, deny)

    ok, cache, cases = True, {}, 0
    for line in (root / "expected.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, code, needle = (part.strip() for part in line.split("|", 2))
        cases += 1
        found = cache.setdefault(name, scan(root / "bad" / name))
        if not any(f.code == code and needle.lower() in f.snippet.lower() for f in found):
            ok = False
            print(f"self-test: {name} did not report {code} for «{needle}»")
    for path in sorted((root / "clean").iterdir()):
        for f in scan(path):
            ok = False
            print(f"self-test: clean {path.name} flagged {f.code}: «{f.snippet}»")
    print(f"self-test: {cases} seeded leaks, " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("targets", nargs="*", help="build directory, HTML or locale/content files, or page URLs")
    ap.add_argument("--site", help="base URL; reads its sitemap and the same-host pages those pages link to")
    ap.add_argument("--locale-keys", nargs="*", help="locale JSON files; their keys must never appear as text")
    ap.add_argument("--allow", help="allow file: 'REGEX # reason' or 'GLOB :: REGEX # reason' per line")
    ap.add_argument("--deny", help="file with one denied term per line (code names, internal hosts)")
    ap.add_argument("--extract", help="write one text file per document here, for the full read")
    ap.add_argument("--chunks", type=int, default=0, help="with --extract: split the files into N reading lists")
    ap.add_argument("--min-html", type=int, default=0,
                    help="exit 2 when fewer HTML documents were found, so an empty build cannot pass")
    ap.add_argument("--strict", action="store_true", help="exit 1 on warnings too")
    ap.add_argument("--quiet", action="store_true", help="print errors only")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.targets and not args.site:
        ap.print_usage(sys.stderr)
        return 2
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
