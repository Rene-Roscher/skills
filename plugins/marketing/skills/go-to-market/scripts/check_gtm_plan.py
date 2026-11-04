#!/usr/bin/env python3
"""Check a go-to-market plan before anything is spent, sent or posted.

Usage:
  check_gtm_plan.py docs/marketing/gtm-plan.md [--root .] [--today YYYY-MM-DD] [--max-unproven 1]
  check_gtm_plan.py --self-test

Findings print as `path:line: error|warning ID message`.
Exit 0: no errors (warnings may remain, explain each in the plan).
Exit 1: at least one error; fix it or report it to the owner, do not act on the plan.
Exit 2: the checker could not run (bad arguments, file not readable).

--root is the repository root that the input links are resolved against (default: current directory).

Ceiling for the cost to win one paying customer:
  contract value per year x gross margin percent / 100 x payback target months / 12

Checks:
  G01 a required section is missing
  G02 'created: YYYY-MM-DD' is missing, invalid or in the future
  G03 an input is missing or still a placeholder; names the skill that produces it
  G04 a linked input file does not exist under --root; names the skill that produces it
  G05 an input number is invalid (contract value above 0, gross margin 1 to 100 percent, payback 1 to 36 months)
  G06 warning: payback target above 12 months
  G07 sales motion is not self-serve, inside or field, or founder-led or reason is missing, or the reason has no number
  G08 sales cost per won deal is not a number or is above the ceiling
  G09 warning: the motion does not match the contract-value band (practice, Janz 2014)
  G10 channels table has no rows, a row with the wrong number of cells, or an unknown status
  G11 a channel has no evidence that the buyer is there
  G12 a channel's target cost per paying customer is not a number
  G13 a channel's target cost per paying customer is above the ceiling
  G14 a channel has no attribution field
  G15 a channel's start or read date is invalid, the read date is not after the start, or before 'created'
  G16 a channel's stop/scale rule is missing or has no number in it
  G17 warning: read date less than 28 days after the start date
  G18 warning: more than --max-unproven channels start within 30 days of each other and none is proven
  G19 warning: the read date has passed while the channel is still planned or running
  G20 outreach table has no rows, a row with the wrong number of cells, an unknown channel or an unknown type
  G21 an outreach row has no two-letter country code
  G22 an outreach row has no known legal basis, or advertising has n/a (letters excepted)
  G23 Germany: the legal basis does not fit the channel (advertising email and similar need consent or
      § 7 Abs. 3 from own customers; calls need consent or presumed B2B; automated calls and fax need consent)
  G24 consent, § 7 Abs. 3 or presumed B2B phone without the place the proof is stored
  G25 recipients come from a cold, purchased, rented or scraped list
  G26 warning: a country other than DE; the legal lines cover Germany only
  G27 warning: presumed B2B phone is case law; counsel reviews before the first call
  G28 launch date set while checklist boxes are open, fewer than 8 checklist items, or an invalid launch date
  G29 owners table empty, an owner missing, or no owner who approves every send
Python standard library only.
"""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import io
import re
import sys
import tempfile
from pathlib import Path

SECTIONS = ["Inputs", "Sales motion", "Channels", "Outreach and mail", "Launch checklist", "Owners"]
INPUTS = {
    "product brief": "product-strategy",
    "pricing model": "pricing-and-unit-economics",
    "currency": "pricing-and-unit-economics",
    "contract value per year": "pricing-and-unit-economics",
    "gross margin percent": "pricing-and-unit-economics",
    "payback target months": "pricing-and-unit-economics",
}
FILE_INPUTS = {"product brief", "pricing model"}
MOTIONS = {"self-serve": "self-serve", "self serve": "self-serve", "selfserve": "self-serve",
           "inside": "inside", "inside sales": "inside", "field": "field", "field sales": "field"}
STATUSES = {"planned", "running", "proven", "stopped"}
ELECTRONIC = {"email", "sms", "messenger", "social-message"}
CHANNELS = ELECTRONIC | {"phone", "automated-call", "fax", "letter"}
TYPES = {"transactional", "advertising"}
BASES = {"consent": "consent", "§7abs.3": "s7-3", "7abs.3": "s7-3", "§7(3)": "s7-3", "7(3)": "s7-3",
         "presumedb2bphone": "presumed", "n/a": "na", "na": "na"}
NEEDS_PROOF = {"consent", "s7-3", "presumed"}
EMPTY = {"", "-", "--", "—", "?", "tbd", "todo", "none", "n/a", "na", "missing", "unknown", "not set"}
COLD_RE = re.compile(
    r"\b(cold|purchas\w*|bought|buy|rent\w*|scrap\w*|harvest\w*|crawl\w*|broker\w*|lead list|leads list"
    r"|data provider|list provider|address provider|third-party list|enrich\w*)\b", re.I)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NUM_RE = re.compile(r"^(\d+(?:\.\d+)?|\d{1,3}(?:,\d{3})+(?:\.\d+)?)$")
HAS_NUM_RE = re.compile(r"\d")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
PLACEHOLDER_RE = re.compile(r"\[[^\]]*\]")
BANDS = [(10000, "self-serve"), (100000, "inside"), (float("inf"), "field")]


def parse_date(s: str) -> dt.date | None:
    s = s.strip().strip("`")
    if not DATE_RE.match(s):
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        return None


def parse_num(s: str) -> float | None:
    s = re.sub(r"(?i)\b(EUR|USD|GBP|CHF)\b|[€$£%]", "", s).strip().strip("`")
    if not NUM_RE.match(s) or re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        return None  # 1.200 could mean 1200 or 1.2
    return float(s.replace(",", ""))


def is_placeholder(s: str) -> bool:
    return bool(PLACEHOLDER_RE.search(LINK_RE.sub("", s)))


def blank(s: str) -> bool:
    return s.strip().strip("`").lower() in EMPTY or is_placeholder(s)


def norm_basis(s: str) -> str | None:
    key = re.sub(r"\s+", "", s.lower()).replace("uwg", "")
    return BASES.get(key)


def ceiling_of(cv: float, margin: float, payback: float) -> float:
    return cv * margin / 100 * payback / 12


def band_for(cv: float) -> str:
    for limit, motion in BANDS:
        if cv < limit:
            return motion
    return "field"


def table_rows(lines: list[str], start: int, end: int) -> list[tuple[int, list[str]]]:
    """Rows of the first Markdown table in lines[start:end], without header and separator."""
    rows, seen_sep, i = [], False, start
    while i < end and not lines[i].lstrip().startswith("|"):
        i += 1
    while i < end and lines[i].lstrip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            seen_sep = True
        elif seen_sep:
            rows.append((i + 1, cells))
        i += 1
    return rows


def check(path: str, text: str, today: dt.date, root: Path, max_unproven: int = 1) -> list[tuple[int, str, str, str]]:
    out: list[tuple[int, str, str, str]] = []
    err = lambda n, c, m: out.append((n, "error", c, m))  # noqa: E731
    warn = lambda n, c, m: out.append((n, "warning", c, m))  # noqa: E731
    lines = text.splitlines()

    heads = [i for i, line in enumerate(lines) if line.startswith("## ")]
    spans: dict[str, tuple[int, int]] = {}
    for k, i in enumerate(heads):
        title = lines[i][3:].strip().lower()
        spans.setdefault(title, (i, heads[k + 1] if k + 1 < len(heads) else len(lines)))
    for title in SECTIONS:
        if title.lower() not in spans:
            err(1, "G01", f"missing section '## {title}'; start from assets/gtm-plan-template.md")

    created = None
    for i, line in enumerate(lines):
        m = re.match(r"^created:\s*(.*)$", line)
        if m:
            created = parse_date(m.group(1))
            if created is None:
                err(i + 1, "G02", "created must be YYYY-MM-DD")
            elif created > today:
                err(i + 1, "G02", f"created {created} is in the future")
                created = None
            break
    else:
        err(1, "G02", "header needs 'created: YYYY-MM-DD'")

    # Inputs
    values: dict[str, float] = {}
    if "inputs" in spans:
        a, b = spans["inputs"]
        found = {}
        for n, cells in table_rows(lines, a + 1, b):
            if len(cells) >= 2:
                found[cells[0].strip().lower()] = (n, cells[1])
        for key, skill in INPUTS.items():
            if key not in found or blank(found[key][1]):
                n = found[key][0] if key in found else a + 1
                err(n, "G03", f"input '{key}' is missing; run the {skill} skill first, then fill it in")
                continue
            n, val = found[key]
            if key in FILE_INPUTS:
                m = LINK_RE.search(val)
                target = (m.group(2) if m else val).strip().strip("`")
                if re.match(r"^[a-z]+://", target, re.I) or not (root / target).is_file():
                    err(n, "G04", f"input '{key}' points to '{target}', which is not a file in the repository;"
                                  f" run the {skill} skill first")
            elif key != "currency":
                num = parse_num(val)
                if num is None:
                    err(n, "G05", f"'{key}' must be plain digits like 1200, got '{val}'")
                elif key == "contract value per year" and num <= 0:
                    err(n, "G05", "contract value per year must be above 0")
                elif key == "gross margin percent" and not 1 <= num <= 100:
                    err(n, "G05", f"gross margin must be a percent between 1 and 100 (80, not 0.8), got {val}")
                elif key == "payback target months" and not 1 <= num <= 36:
                    err(n, "G05", f"payback target must be 1 to 36 months, got {val}")
                else:
                    values[key] = num
                    if key == "payback target months" and num > 12:
                        warn(n, "G06", f"payback of {num:g} months; above 12 months SaaS profitability is"
                                       " called anemic (Skok, SaaS Metrics 2.0)")
    ceiling = None
    if {"contract value per year", "gross margin percent", "payback target months"} <= values.keys():
        ceiling = ceiling_of(values["contract value per year"], values["gross margin percent"],
                             values["payback target months"])

    # Sales motion
    if "sales motion" in spans:
        a, b = spans["sales motion"]
        f = {c[0].strip().lower(): (n, c[1] if len(c) > 1 else "") for n, c in table_rows(lines, a + 1, b)}
        n, val = f.get("motion", (a + 1, ""))
        motion = MOTIONS.get(val.strip().lower())
        if motion is None:
            err(n, "G07", f"motion must be self-serve, inside or field, got '{val}'")
        for key in ("founder-led until", "reason"):
            n2, v2 = f.get(key, (a + 1, ""))
            if blank(v2):
                err(n2, "G07", f"'{key}' is missing")
            elif key == "reason" and not HAS_NUM_RE.search(v2):
                err(n2, "G07", "reason must state the numbers that chose the motion (contract value, sales cost)")
        n3, v3 = f.get("sales cost per won deal", (a + 1, ""))
        cost = parse_num(v3)
        if cost is None:
            err(n3, "G08", f"sales cost per won deal must be plain digits (0 for self-serve), got '{v3}'")
        elif ceiling is not None and cost > ceiling:
            err(n3, "G08", f"sales cost per won deal {cost:g} is above the ceiling {ceiling:g}; move down a motion"
                           " or raise the price (pricing-and-unit-economics)")
        if motion and "contract value per year" in values:
            want = band_for(values["contract value per year"])
            if motion != want:
                warn(n, "G09", f"contract value {values['contract value per year']:g} per year falls in the {want}"
                               f" band, plan says {motion}; give the reason in the plan (practice, Janz 2014)")

    # Channels
    if "channels" in spans:
        a, b = spans["channels"]
        rows = table_rows(lines, a + 1, b)
        if not rows:
            err(a + 1, "G10", "no channel rows")
        starts: list[tuple[dt.date, int]] = []
        proven = False
        for n, cells in rows:
            if len(cells) != 9:
                err(n, "G10", "channel row needs 9 cells: #, Channel, Evidence, Target cost, Attribution field,"
                              " Start date, Read date, Stop/scale rule, Status")
                continue
            _, name, evidence, target, attr, start_s, read_s, rule, status = cells
            status = status.lower()
            if status not in STATUSES:
                err(n, "G10", f"status must be one of {', '.join(sorted(STATUSES))}, got '{cells[8]}'")
            proven = proven or status == "proven"
            if blank(evidence):
                err(n, "G11", f"'{name}': no evidence that the buyer is there (interviews, sign-up source field,"
                              " search demand, communities customers named)")
            t = parse_num(target)
            if t is None:
                err(n, "G12", f"'{name}': target cost per paying customer must be plain digits, got '{target}'")
            elif ceiling is not None and t > ceiling:
                err(n, "G13", f"'{name}': target {t:g} is above the ceiling {ceiling:g}"
                              " (contract value x margin x payback months / 12)")
            if blank(attr):
                err(n, "G14", f"'{name}': no attribution field; set it up with search-measurement before the start")
            sd, rd = parse_date(start_s), parse_date(read_s)
            if sd is None or rd is None:
                err(n, "G15", f"'{name}': start and read date must be YYYY-MM-DD")
            elif rd <= sd:
                err(n, "G15", f"'{name}': read date {rd} is not after start date {sd}")
            elif created is not None and rd < created:
                err(n, "G15", f"'{name}': read date {rd} is before the plan was created ({created})")
            else:
                if (rd - sd).days < 28:
                    warn(n, "G17", f"'{name}': read after {(rd - sd).days} days; less than 28 days rarely holds"
                                   " one paying cohort")
                if rd < today and status in {"planned", "running"}:
                    warn(n, "G19", f"'{name}': read date {rd} has passed; report paying customers and cost per"
                                   " paying customer, then set stop, keep or scale")
            if sd is not None and status in {"planned", "running"}:
                starts.append((sd, n))
            if blank(rule) or not HAS_NUM_RE.search(rule):
                err(n, "G16", f"'{name}': stop/scale rule must contain the number it is judged on")
        if not proven:
            starts.sort()
            for i, (sd, n) in enumerate(starts):
                window = [x for x in starts[i:] if (x[0] - sd).days <= 30]
                if len(window) > max_unproven:
                    warn(n, "G18", f"{len(window)} unproven channels start within 30 days of {sd}; prove one"
                                   " before adding the next")
                    break

    # Outreach and mail
    if "outreach and mail" in spans:
        a, b = spans["outreach and mail"]
        rows = table_rows(lines, a + 1, b)
        if not rows:
            err(a + 1, "G20", "no outreach or mail rows; list at least the transactional mails")
        for n, cells in rows:
            if len(cells) != 8:
                err(n, "G20", "outreach row needs 8 cells: #, Message, Channel, Recipients from, Country, Type,"
                              " Legal basis, Proof stored where")
                continue
            _, msg, chan, source, country, typ, basis_s, proof = cells
            chan, typ, country = chan.strip().lower(), typ.strip().lower(), country.strip().upper()
            if chan not in CHANNELS:
                err(n, "G20", f"'{msg}': channel must be one of {', '.join(sorted(CHANNELS))}, got '{cells[2]}'")
            if typ not in TYPES:
                err(n, "G20", f"'{msg}': type must be transactional or advertising, got '{cells[5]}'")
            if not re.fullmatch(r"[A-Z]{2}", country):
                err(n, "G21", f"'{msg}': country must be a two-letter code such as DE, got '{cells[4]}'")
            elif country != "DE":
                warn(n, "G26", f"'{msg}': {country} is not covered; check it with eu-de-legal-baseline and counsel")
            basis = norm_basis(basis_s)
            if basis is None:
                err(n, "G22", f"'{msg}': legal basis must be consent, § 7 Abs. 3, presumed B2B phone or n/a,"
                              f" got '{basis_s}'")
            elif typ == "advertising" and basis == "na" and chan != "letter":
                err(n, "G22", f"'{msg}': advertising needs a legal basis, n/a is only for transactional mail")
            if COLD_RE.search(source):
                err(n, "G25", f"'{msg}': recipients from '{source}'; cold, bought, rented or scraped lists are not"
                              " a source; use consent-based alternatives")
            if basis in NEEDS_PROOF and blank(proof):
                err(n, "G24", f"'{msg}': name where the proof for '{basis_s}' is stored")
            if basis == "presumed":
                warn(n, "G27", f"'{msg}': presumed consent for B2B calls is case law; counsel reviews before the"
                               " first call")
            if country == "DE" and typ == "advertising" and basis not in {None, "na"} and chan in CHANNELS:
                if chan in ELECTRONIC and basis not in {"consent", "s7-3"}:
                    err(n, "G23", f"'{msg}': advertising by {chan} to DE needs consent or § 7 Abs. 3 UWG")
                elif chan in ELECTRONIC and basis == "s7-3" and "customer" not in source.lower():
                    err(n, "G23", f"'{msg}': § 7 Abs. 3 UWG covers only addresses from your own customers' purchases")
                elif chan == "phone" and basis not in {"consent", "presumed"}:
                    err(n, "G23", f"'{msg}': advertising calls to DE need consent (consumers) or at least presumed"
                                  " consent (businesses)")
                elif chan in {"automated-call", "fax"} and basis != "consent":
                    err(n, "G23", f"'{msg}': automated calls and fax to DE need prior express consent")
            if basis == "presumed" and chan in CHANNELS and chan != "phone":
                err(n, "G23", f"'{msg}': presumed B2B consent applies to phone calls only")
            if basis == "s7-3" and chan in CHANNELS and chan not in ELECTRONIC:
                err(n, "G23", f"'{msg}': § 7 Abs. 3 UWG covers electronic mail only")

    # Launch checklist
    if "launch checklist" in spans:
        a, b = spans["launch checklist"]
        boxes = [(i + 1, line) for i, line in enumerate(lines[a:b], start=a) if re.match(r"^\s*- \[[ xX]\]", line)]
        if len(boxes) < 8:
            err(a + 1, "G28", f"{len(boxes)} checklist items; keep the 8 items of the template")
        for i in range(a, b):
            m = re.match(r"^Launch date:\s*(.*)$", lines[i])
            if not m:
                continue
            val = m.group(1).strip()
            if blank(val):
                break
            if parse_date(val) is None:
                err(i + 1, "G28", f"launch date must be 'not set' or YYYY-MM-DD, got '{val}'")
                break
            open_ = [n for n, line in boxes if re.match(r"^\s*- \[ \]", line)]
            if open_:
                err(i + 1, "G28", f"launch date set while {len(open_)} checklist item(s) are open"
                                  f" (line {open_[0]}); tick them first or set 'not set'")
            break
        else:
            err(a + 1, "G28", "missing 'Launch date:' line")

    # Owners
    if "owners" in spans:
        a, b = spans["owners"]
        rows = table_rows(lines, a + 1, b)
        if not rows:
            err(a + 1, "G29", "no owner rows")
        sends = False
        for n, cells in rows:
            if len(cells) < 2 or blank(cells[1]):
                err(n, "G29", f"area '{cells[0]}' has no owner")
            if "send" in cells[0].lower():
                sends = True
        if rows and not sends:
            err(a + 1, "G29", "no owner who approves every send ('Outreach and mail, approves every send')")
    return out


def run(path: str, today: dt.date, root: Path, max_unproven: int) -> int:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"{path}: cannot read: {e}", file=sys.stderr)
        return 2
    findings = check(path, text, today, root, max_unproven)
    for n, level, code, msg in findings:
        print(f"{path}:{n}: {level} {code} {msg}")
    errors = sum(1 for f in findings if f[1] == "error")
    print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if errors else 0


def fixture() -> str:
    return """# Go-to-market plan: booking tool, driving schools

created: 2026-11-04
Owner: Founder
Skills: go-to-market

## Inputs

| Input | Value | Source |
|---|---|---|
| Product brief | docs/product/brief.md | product-strategy |
| Pricing model | [pricing](docs/product/pricing.md) | pricing-and-unit-economics |
| Currency | EUR | pricing model |
| Contract value per year | 1200 | pricing model |
| Gross margin percent | 80 | pricing model |
| Payback target months | 12 | pricing model |

## Sales motion

| Field | Value |
|---|---|
| Motion | self-serve |
| Sales cost per won deal | 0 |
| Founder-led until | first 20 paying customers |
| Reason | 1200 per year is below the 10000 band; no hours per deal fit under the ceiling of 960 |

## Channels

| # | Channel | Evidence buyer is there | Target cost per paying customer | Attribution field | Start date | Read date | Stop/scale rule | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | Marketplace listing | 4 of 10 interviewed schools found tools there | 700 | signup_source=marketplace | 2026-11-10 | 2026-12-31 | stop above 960 after 2 cohorts | running |
| 2 | Comparison pages | 120 searches a month for the problem | 500 | signup_source=search | 2027-01-15 | 2027-03-01 | stop above 960 after 2 cohorts | planned |

## Outreach and mail

| # | Message | Channel | Recipients from | Country | Type | Legal basis | Proof stored where |
|---|---|---|---|---|---|---|---|
| 1 | Sign-up confirmation | email | own sign-up form | DE | transactional | n/a | n/a |
| 2 | Newsletter | email | double opt-in form | DE | advertising | consent | consents table |
| 3 | Win-back | email | own customers' orders | DE | advertising | § 7 Abs. 3 | notice log |

## Launch checklist

Launch date: not set

- [x] one
- [x] two
- [x] three
- [x] four
- [x] five
- [x] six
- [x] seven
- [ ] eight

## Owners

| Area | Owner |
|---|---|
| Plan and budget | Founder |
| Outreach and mail, approves every send | Founder |
"""


def self_test() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="gtm-check-"))
    (tmp / "docs/product").mkdir(parents=True)
    (tmp / "docs/product/brief.md").write_text("# Brief\n", encoding="utf-8")
    (tmp / "docs/product/pricing.md").write_text("# Pricing\n", encoding="utf-8")
    today = dt.date(2026, 11, 4)
    v = fixture()
    row1 = "| 1 | Marketplace listing | 4 of 10 interviewed schools found tools there | 700 | signup_source=marketplace | 2026-11-10 | 2026-12-31 | stop above 960 after 2 cohorts | running |"
    phone = "| 4 | Intro call | phone | own event sign-ups | DE | advertising | presumed B2B phone | call notes |\n"
    row3 = ("| 3 | Webinar | 30 sign-ups from a partner list | 400 | signup_source=webinar | 2026-11-15 | 2027-01-20 |"
            " stop above 960 after 2 cohorts | planned |\n")
    out2 = "| 2 | Newsletter | email | double opt-in form | DE | advertising | consent | consents table |"
    cases = [
        # (label, text, expected errors, expected warning or None, today, max_unproven, message fragment)
        ("valid", v, set(), set(), today, 1, None),
        ("missing section", v.replace("## Owners", "## People"), {"G01"}, set(), today, 1, None),
        ("no created", v.replace("created: 2026-11-04\n", ""), {"G02"}, set(), today, 1, None),
        ("future created", v.replace("created: 2026-11-04", "created: 2026-12-01"), {"G02"}, set(), today, 1, None),
        ("brief missing", v.replace("| docs/product/brief.md |", "| [path] |"), {"G03"}, set(), today, 1,
         "product-strategy"),
        ("margin missing", v.replace("| Gross margin percent | 80 |", "| Gross margin percent | tbd |"),
         {"G03"}, set(), today, 1, "pricing-and-unit-economics"),
        ("pricing file absent", v.replace("docs/product/pricing.md", "docs/product/price.md"), {"G04"}, set(),
         today, 1, "pricing-and-unit-economics"),
        ("pricing as url", v.replace("[pricing](docs/product/pricing.md)", "https://example.com/p"), {"G04"},
         set(), today, 1, None),
        ("margin fraction", v.replace("| Gross margin percent | 80 |", "| Gross margin percent | 0.8 |"),
         {"G05"}, set(), today, 1, None),
        ("ambiguous number", v.replace("| Contract value per year | 1200 |", "| Contract value per year | 1.200 |"),
         {"G05"}, set(), today, 1, None),
        ("short payback", v.replace("| Payback target months | 12 |", "| Payback target months | 6 |"),
         {"G13"}, set(), today, 1, "480"),
        ("inside in band", v.replace("| Contract value per year | 1200 |", "| Contract value per year | 15000 |")
         .replace("| Motion | self-serve |", "| Motion | inside |"), set(), set(), today, 1, None),
        ("band boundary", v.replace("| Contract value per year | 1200 |", "| Contract value per year | 10000 |"),
         set(), {"G09"}, today, 1, "inside"),
        ("long payback", v.replace("| Payback target months | 12 |", "| Payback target months | 18 |"),
         set(), {"G06"}, today, 1, None),
        ("unknown motion", v.replace("| Motion | self-serve |", "| Motion | growth |"), {"G07"}, set(), today,
         1, None),
        ("reason without numbers", v.replace(v.split("| Reason | ")[1].split(" |")[0], "it feels right"),
         {"G07"}, set(), today, 1, None),
        ("sales cost above ceiling", v.replace("| Sales cost per won deal | 0 |", "| Sales cost per won deal | 2000 |"),
         {"G08"}, set(), today, 1, "960"),
        ("motion off band", v.replace("| Motion | self-serve |", "| Motion | field |"), set(), {"G09"}, today, 1,
         None),
        ("bad status", v.replace("signup_source=search | 2027-01-15 | 2027-03-01 | stop above 960 after 2 cohorts | planned",
                                 "signup_source=search | 2027-01-15 | 2027-03-01 | stop above 960 after 2 cohorts | live"),
         {"G10"}, set(), today, 1, None),
        ("no evidence", v.replace("4 of 10 interviewed schools found tools there", ""), {"G11"}, set(), today, 1,
         None),
        ("target not a number", v.replace("| 700 |", "| low |"), {"G12"}, set(), today, 1, None),
        ("target above ceiling", v.replace("| 700 |", "| 1500 |"), {"G13"}, set(), today, 1, "960"),
        ("no attribution", v.replace("signup_source=marketplace", ""), {"G14"}, set(), today, 1, None),
        ("read before created", v.replace("| 2026-11-10 | 2026-12-31 |", "| 2026-10-01 | 2026-10-30 |"),
         {"G15"}, set(), today, 1, None),
        ("read before start", v.replace("| 2026-11-10 | 2026-12-31 |", "| 2026-11-10 | 2026-11-09 |"),
         {"G15"}, set(), today, 1, None),
        ("rule without number", v.replace("stop above 960 after 2 cohorts | running", "scale if good | running"),
         {"G16"}, set(), today, 1, None),
        ("short read window", v.replace("| 2026-11-10 | 2026-12-31 |", "| 2026-11-10 | 2026-11-24 |"),
         set(), {"G17"}, today, 1, None),
        ("parallel channels", v.replace("2027-01-15 | 2027-03-01", "2026-11-12 | 2027-01-15"), set(), {"G18"},
         today, 1, None),
        ("parallel allowed by flag", v.replace("2027-01-15 | 2027-03-01", "2026-11-12 | 2027-01-15"), set(),
         set(), today, 2, None),
        ("parallel with proven", v.replace("2027-01-15 | 2027-03-01", "2026-11-12 | 2027-01-15")
         .replace("cohorts | running", "cohorts | proven").replace("| planned |\n", "| planned |\n" + row3), set(),
         set(), today, 1, None),
        ("parallel without proven", v.replace("2027-01-15 | 2027-03-01", "2026-11-12 | 2027-01-15")
         .replace("cohorts | running", "cohorts | stopped").replace("| planned |\n", "| planned |\n" + row3), set(),
         {"G18"}, today, 1, None),
        ("read date passed", v, set(), {"G19"}, dt.date(2027, 1, 5), 1, None),
        ("unknown channel", v.replace("| Newsletter | email |", "| Newsletter | carrier pigeon |"), {"G20"},
         set(), today, 1, None),
        ("no outreach rows", v.replace(out2 + "\n", "").replace(
            "| 1 | Sign-up confirmation | email | own sign-up form | DE | transactional | n/a | n/a |\n", "").replace(
            "| 3 | Win-back | email | own customers' orders | DE | advertising | § 7 Abs. 3 | notice log |\n", ""),
         {"G20"}, set(), today, 1, None),
        ("no country", v.replace(out2, out2.replace("| DE |", "|  |")), {"G21"}, set(),
         today, 1, None),
        ("unknown basis", v.replace("| advertising | consent |", "| advertising | legitimate interest |"),
         {"G22"}, set(), today, 1, None),
        ("advertising n/a", v.replace("| advertising | consent | consents table |", "| advertising | n/a | n/a |"),
         {"G22"}, set(), today, 1, None),
        ("DE email presumed", v.replace("| advertising | consent | consents table |",
                                        "| advertising | presumed B2B phone | call notes |"),
         {"G23"}, {"G27"}, today, 1, "consent or § 7 Abs. 3"),
        ("7(3) not customers", v.replace("own customers' orders", "trade fair badge scans"), {"G23"}, set(),
         today, 1, None),
        ("letter presumed", v.replace("| Win-back | email | own customers' orders | DE | advertising | § 7 Abs. 3 |",
                                      "| Win-back | letter | own customers' orders | DE | advertising | presumed B2B phone |"),
         {"G23"}, {"G27"}, today, 1, "phone calls only"),
        ("fax without consent", v.replace("| Win-back | email |", "| Win-back | fax |"), {"G23"}, set(), today,
         1, None),
        ("consent without proof", v.replace("| consent | consents table |", "| consent | [where] |"), {"G24"},
         set(), today, 1, None),
        ("purchased list", v.replace("double opt-in form", "purchased lead list"), {"G25"}, set(), today, 1,
         None),
        ("list provider", v.replace("double opt-in form", "addresses from a list provider"), {"G25"}, set(), today,
         1, None),
        ("cold list abroad", v.replace("double opt-in form | DE", "cold list | AT"), {"G25"}, {"G26"}, today, 1,
         None),
        ("other country", v.replace("double opt-in form | DE", "double opt-in form | AT"), set(), {"G26"},
         today, 1, None),
        ("B2B phone", v.replace("| notice log |\n", "| notice log |\n" + phone), set(), {"G27"}, today, 1,
         None),
        ("launch with open box", v.replace("Launch date: not set", "Launch date: 2026-12-01"), {"G28"}, set(),
         today, 1, None),
        ("checklist cut", v.replace("- [x] seven\n- [ ] eight\n", ""), {"G28"}, set(), today, 1, None),
        ("no send owner", v.replace("| Outreach and mail, approves every send | Founder |\n", ""), {"G29"},
         set(), today, 1, None),
        ("empty owner", v.replace("| Plan and budget | Founder |", "| Plan and budget | [name] |"), {"G29"},
         set(), today, 1, None),
    ]
    failed = 0
    for label, text, want_err, want_warn, day, mu, frag in cases:
        found = check("docs/marketing/gtm-plan.md", text, day, tmp, mu)
        errs = {c for _, lvl, c, _ in found if lvl == "error"}
        warns = {c for _, lvl, c, _ in found if lvl == "warning"}
        ok = errs == want_err and warns == want_warn
        if frag is not None and not any(frag in m for *_, m in found):
            ok = False
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}: errors {sorted(want_err) or 'none'} got {sorted(errs) or 'none'},"
              f" warnings {sorted(want_warn) or 'none'} got {sorted(warns) or 'none'}")
    template = Path(__file__).resolve().parent.parent / "assets" / "gtm-plan-template.md"
    if template.is_file():
        found = check(str(template), template.read_text(encoding="utf-8"), today, tmp)
        errs = {c for _, lvl, c, _ in found if lvl == "error"}
        ok = {"G01"}.isdisjoint(errs) and {"G02", "G03", "G12"} <= errs
        failed += not ok
        print(f"{'ok  ' if ok else 'FAIL'} unfilled template: all sections found, placeholders rejected"
              f" (got {sorted(errs)})")
    else:
        print("FAIL unfilled template: assets/gtm-plan-template.md not found")
        failed += 1
    with contextlib.redirect_stderr(io.StringIO()):
        code = run(str(tmp / "missing.md"), today, tmp, 1)
    ok = code == 2
    failed += not ok
    print(f"{'ok  ' if ok else 'FAIL'} unreadable file exits 2")
    return 1 if failed else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path", nargs="?")
    p.add_argument("--root", default=".", help="repository root for input links, default: current directory")
    p.add_argument("--today", help="YYYY-MM-DD, default: the current date")
    p.add_argument("--max-unproven", type=int, default=1,
                   help="unproven channels allowed to start within 30 days, default 1")
    p.add_argument("--self-test", action="store_true")
    try:
        a = p.parse_args()
    except SystemExit as e:
        return 2 if e.code else 0
    if a.self_test:
        return self_test()
    if not a.path:
        print("path required; see --help", file=sys.stderr)
        return 2
    today = parse_date(a.today) if a.today else dt.date.today()
    if today is None:
        print("--today must be YYYY-MM-DD", file=sys.stderr)
        return 2
    return run(a.path, today, Path(a.root), a.max_unproven)


if __name__ == "__main__":
    sys.exit(main())
