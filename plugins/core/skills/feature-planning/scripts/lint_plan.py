#!/usr/bin/env python3
"""Lint a feature plan written from the feature-planning template.

Usage:
  lint_plan.py PLAN.md [PLAN.md ...] [--multi-tenant] [--template TEMPLATE.md]
  lint_plan.py --self-test

Checks (code, what fails):
  P01  no "Status:" line with Draft, Approved or Superseded
  P02  a required section is missing
  P03  a section is empty
  P04  a template placeholder is left ([feature name], a cell that is only [ ])
  P05  N/A or "not applicable" with fewer than three words of reason on the same line or cell
  P06  TBD, TODO or FIXME, or an answer that is only "later" or "follow-up", without an issue link
  P07  a Problem field is missing or empty (Problem, Personas, Today, Success moment,
       Success metric, Non-goals, Stress moment)
  P08  the Failure modes table header is missing or has fewer than three rows
  P09  the Implementation steps table header is missing or has no row
  P10  Open decisions is not a numbered list, or an item has no "Recommendation:"
  P11  a Data protection trigger is not answered yes or no
  P12  Rollout or Rollback is missing or empty
  P13  multi-tenant plan: no surface in the Tenant isolation table, or no cross-tenant test
  P14  Status is Approved but Approved-by is empty
  P15  a Data model or Dependencies row has no Evidence of verified, reported or inferred

Without --template, the required sections are the ones in the skill's plan template. With --template,
they are the "##" headings of that file; headings marked "(optional)" are not required, and checks
tied to a section run only when the template has that section.

A plan is multi-tenant when --multi-tenant is given or its header says "Multi-tenant: yes".

Output: one finding per line as "path:line: code message". Exit 0 when clean, 1 with findings,
2 on a usage error. Python 3.8 or later, standard library only, no network.
"""

from __future__ import annotations

import argparse
import re
import sys

DEFAULT_SECTIONS = [
    "problem",
    "prior art",
    "ux and states",
    "data model",
    "reuse",
    "api and automation",
    "events, jobs and caching",
    "permissions, limits and audit",
    "tenant isolation",
    "data protection",
    "dependencies",
    "performance budget",
    "failure modes",
    "test plan",
    "rollout and rollback",
    "implementation steps",
    "self-review",
    "open decisions",
]

PROBLEM_FIELDS = [
    "Problem",
    "Personas",
    "Today",
    "Success moment",
    "Success metric",
    "Non-goals",
    "Stress moment",
]

PRIVACY_TRIGGERS = [
    "New personal-data category",
    "New processor or sub-processor",
    "New retention period",
    "Third-country transfer",
    "Special-category data",
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUM_PREFIX_RE = re.compile(r"^\d+[.)]?\s+")
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
LINK_RE = re.compile(r"https?://\S+|(?<![\w/&])#\d+\b|\b[A-Z][A-Z0-9]+-\d+\b|\[[^\]\n]+\]\([^)\s]+\)")
PLACEHOLDER_RE = re.compile(r"\[(?!\s*\]|x\]|X\])[^\]\n]{1,80}\](?!\()")
NA_RE = re.compile(r"\b(?:N/A|n/a|NA|not applicable)\b", re.I)
TBD_RE = re.compile(r"\b(?:TBD|TBC|TODO|FIXME)\b")
LATER_RE = re.compile(r"^(?:[-*]\s+)?(?:[^:|]{0,60}:\s*)?(?:later|follow[- ]?up|to be decided)\.?\s*$", re.I)
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'-]*")
EVIDENCE_RE = re.compile(r"^\s*(verified|reported|inferred)\b", re.I)


def norm(heading: str) -> str:
    h = NUM_PREFIX_RE.sub("", heading.strip())
    h = re.sub(r"\(optional\)", "", h, flags=re.I)
    return re.sub(r"\s+", " ", h).strip().lower()


class Plan:
    """A plan split into lines, with fenced code and inline code masked."""

    def __init__(self, path: str, text: str) -> None:
        self.path = path
        self.lines = text.splitlines()
        self.clean = []
        in_fence = False
        for line in self.lines:
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                self.clean.append("")
                continue
            self.clean.append("" if in_fence else INLINE_CODE_RE.sub("code", line))
        # sections: name -> (heading line index, body start, body end)
        self.sections = {}
        heads = []
        for i, line in enumerate(self.clean):
            m = HEADING_RE.match(line)
            if m and len(m.group(1)) == 2:
                heads.append((i, norm(m.group(2))))
        for k, (i, name) in enumerate(heads):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(self.clean)
            if name not in self.sections:
                self.sections[name] = (i, i + 1, end)
        self.header_end = heads[0][0] if heads else len(self.clean)

    def body(self, name: str):
        """Return [(line_index, text)] of a section's body, or None if absent."""
        if name not in self.sections:
            return None
        _, start, end = self.sections[name]
        return [(i, self.clean[i]) for i in range(start, end)]


def words(text: str) -> int:
    return len(WORD_RE.findall(text))


def cells(line: str):
    s = line.strip()
    if not s.startswith("|"):
        return None
    parts = s.strip("|").split("|")
    return [p.strip() for p in parts]


def is_separator(line: str) -> bool:
    c = cells(line)
    return bool(c) and all(re.match(r"^:?-{2,}:?$", x) for x in c if x) and any(c)


def table_rows(body, header_re):
    """Find a table whose header matches header_re; return (header_index, rows) or (None, [])."""
    for k, (i, line) in enumerate(body):
        if header_re.match(line.strip()):
            rows = []
            j = k + 1
            if j < len(body) and is_separator(body[j][1]):
                j += 1
            while j < len(body):
                c = cells(body[j][1])
                if c is None:
                    break
                rows.append((body[j][0], c))
                j += 1
            return i, rows
    return None, []


def section_is_na(body) -> bool:
    text = " ".join(t for _, t in body if t.strip())
    m = NA_RE.search(text)
    return bool(m) and m.start() < 5 and words(text[m.end():]) >= 3


class Linter:
    def __init__(self, plan: Plan, required, multi_tenant: bool) -> None:
        self.p = plan
        self.required = required
        self.multi_tenant = multi_tenant
        self.findings = []

    def add(self, idx: int, code: str, msg: str) -> None:
        self.findings.append((idx + 1, code, msg))

    def has(self, name: str) -> bool:
        return name in self.required and name in self.p.sections

    def run(self):
        self.status()
        self.sections()
        self.line_checks()
        if self.has("problem"):
            self.problem()
        if self.has("failure modes"):
            self.failure_table()
        if self.has("implementation steps"):
            self.steps_table()
        if self.has("open decisions"):
            self.decisions()
        if self.has("data protection"):
            self.privacy()
        if self.has("rollout and rollback"):
            self.rollout()
        for name in ("data model", "dependencies"):
            if self.has(name):
                self.evidence(name)
        if self.multi_tenant:
            self.tenancy()
        return sorted(self.findings)

    def status(self) -> None:
        status_idx = None
        status = None
        approved_by = None
        for i in range(self.p.header_end):
            line = self.p.clean[i]
            m = re.match(r"^\s*Status:\s*(\S.*?)\s*$", line)
            if m:
                status_idx, status = i, m.group(1)
            m = re.match(r"^\s*Approved-by:\s*(.*?)\s*$", line)
            if m:
                approved_by = m.group(1)
        if status is None or status.split()[0] not in ("Draft", "Approved", "Superseded"):
            self.add(status_idx or 0, "P01", "header needs 'Status: Draft', 'Status: Approved' or 'Status: Superseded'")
        elif status.split()[0] == "Approved" and not approved_by:
            self.add(status_idx, "P14", "status is Approved but 'Approved-by:' is empty")

    def sections(self) -> None:
        for name in self.required:
            if name not in self.p.sections:
                self.add(0, "P02", f"required section '{name}' is missing")
                continue
            idx = self.p.sections[name][0]
            if not any(t.strip() for _, t in self.p.body(name)):
                self.add(idx, "P03", f"section '{name}' is empty")

    def line_checks(self) -> None:
        for i, line in enumerate(self.p.clean):
            if not line.strip():
                continue
            if HEADING_RE.match(line):
                m = PLACEHOLDER_RE.search(LINK_RE.sub("", line))
                if m:
                    self.add(i, "P04", f"template placeholder left: {m.group(0)}")
                continue
            c = cells(line)
            if c is not None and is_separator(line):
                continue
            units = c if c is not None else [line]
            has_link = bool(LINK_RE.search(line))
            for u in units:
                if u.strip() == "[ ]" or re.search(r":\s*\[ \]\s*$", u):
                    self.add(i, "P04", "empty placeholder '[ ]' left")
            stripped = LINK_RE.sub("", line)
            m = PLACEHOLDER_RE.search(stripped)
            if m:
                self.add(i, "P04", f"template placeholder left: {m.group(0)}")
            for u in units:
                for m in NA_RE.finditer(u):
                    if words(u[m.end():]) < 3:
                        self.add(i, "P05", "N/A without a reason on the same line")
                        break
            if not has_link:
                if TBD_RE.search(line):
                    self.add(i, "P06", "TBD/TODO/FIXME without an issue link on the same line")
                elif any(LATER_RE.match(u.strip()) for u in units if u.strip()):
                    self.add(i, "P06", "'later' or 'follow-up' is not an answer; link a tracked issue")

    def problem(self) -> None:
        body = self.p.body("problem")
        found = {}
        for i, line in body:
            m = re.match(r"^\s*[-*]\s*([A-Za-z -]+?)\s*:\s*(.*)$", line)
            if m:
                found[m.group(1).strip().lower()] = (i, m.group(2).strip())
        head = self.p.sections["problem"][0]
        for field in PROBLEM_FIELDS:
            hit = found.get(field.lower())
            if hit is None:
                self.add(head, "P07", f"Problem field '{field}:' is missing")
            elif not hit[1]:
                self.add(hit[0], "P07", f"Problem field '{field}:' is empty")

    def failure_table(self) -> None:
        body = self.p.body("failure modes")
        head = self.p.sections["failure modes"][0]
        if section_is_na(body):
            self.add(head, "P08", "failure modes can't be N/A")
            return
        hdr = re.compile(r"^\|\s*Failure\s*\|\s*Impact\s*\|\s*Detection\s*\|\s*Reaction\s*\|", re.I)
        idx, rows = table_rows(body, hdr)
        if idx is None:
            self.add(head, "P08", "table header '| Failure | Impact | Detection | Reaction |' is missing")
            return
        filled = [r for r in rows if r[1] and r[1][0]]
        if len(filled) < 3:
            self.add(idx, "P08", f"failure-mode table has {len(filled)} rows; at least 3 needed")

    def steps_table(self) -> None:
        body = self.p.body("implementation steps")
        head = self.p.sections["implementation steps"][0]
        hdr = re.compile(r"^\|\s*Step\s*\|\s*Location\s*\|\s*Done criterion\s*\|\s*Depends on\s*\|", re.I)
        idx, rows = table_rows(body, hdr)
        if idx is None:
            self.add(head, "P09", "table header '| Step | Location | Done criterion | Depends on |' is missing")
        elif not [r for r in rows if r[1] and r[1][0]]:
            self.add(idx, "P09", "implementation table has no rows")

    def decisions(self) -> None:
        body = [(i, t) for i, t in self.p.body("open decisions") if t.strip()]
        head = self.p.sections["open decisions"][0]
        if not body:
            return
        first = body[0][1].strip()
        if re.match(r"^None\b", first, re.I):
            if words(first[4:]) < 3:
                self.add(body[0][0], "P10", "'None' needs a reason")
            return
        items = []
        for i, t in body:
            if re.match(r"^\d+\.\s+\S", t):
                items.append([i, t])
            elif items:
                items[-1][1] += "\n" + t
        if not items:
            self.add(head, "P10", "open decisions must be a numbered list (1. 2. 3.)")
            return
        for i, text in items:
            m = re.search(r"Recommendation:\s*(.*)", text, re.I)
            if not m or words(m.group(1)) < 2:
                self.add(i, "P10", "decision item without a 'Recommendation:' and its reason")

    def privacy(self) -> None:
        body = self.p.body("data protection")
        head = self.p.sections["data protection"][0]
        text = "\n".join(t for _, t in body)
        for trig in PRIVACY_TRIGGERS:
            if not re.search(re.escape(trig) + r"\s*:\s*\**\s*(yes|no)\b", text, re.I):
                self.add(head, "P11", f"'{trig}:' must be answered yes or no")

    def rollout(self) -> None:
        body = self.p.body("rollout and rollback")
        head = self.p.sections["rollout and rollback"][0]
        for label in ("Rollout", "Rollback"):
            hit = None
            for i, t in body:
                m = re.match(r"^\s*[-*]?\s*" + label + r"\s*:\s*(.*)$", t, re.I)
                if m:
                    hit = (i, m.group(1).strip())
                    break
            if hit is None:
                self.add(head, "P12", f"'{label}:' is missing")
            elif words(hit[1]) < 3:
                self.add(hit[0], "P12", f"'{label}:' needs a concrete description")

    def evidence(self, name: str) -> None:
        body = self.p.body(name)
        if section_is_na(body):
            return
        for k, (i, line) in enumerate(body):
            c = cells(line)
            if c is None or k + 1 >= len(body) or not is_separator(body[k + 1][1]):
                continue
            cols = [x.lower() for x in c]
            if "evidence" not in cols:
                self.add(i, "P15", f"the {name} table needs an Evidence column")
                return
            col = cols.index("evidence")
            j = k + 2
            while j < len(body) and cells(body[j][1]) is not None:
                row = cells(body[j][1])
                cell = row[col] if col < len(row) else ""
                if not EVIDENCE_RE.match(cell):
                    self.add(body[j][0], "P15", "Evidence must start with verified, reported or inferred")
                j += 1
            return

    def tenancy(self) -> None:
        if "tenant isolation" in self.p.sections:
            body = self.p.body("tenant isolation")
            head = self.p.sections["tenant isolation"][0]
            hdr = re.compile(r"^\|\s*Surface\s*\|", re.I)
            idx, rows = table_rows(body, hdr)
            filled = [r for r in rows if r[1] and r[1][0] and len(r[1]) > 1 and r[1][1]]
            if idx is None or not filled:
                self.add(head, "P13", "multi-tenant plan: list each surface and its isolation in the '| Surface |' table")
        else:
            self.add(0, "P13", "multi-tenant plan: section 'tenant isolation' is missing")
        tp = self.p.body("test plan")
        if tp is None or not any(re.search(r"cross[- ]tenant", t, re.I) for _, t in tp):
            idx = self.p.sections["test plan"][0] if "test plan" in self.p.sections else 0
            self.add(idx, "P13", "multi-tenant plan: the test plan needs a cross-tenant test")


def required_from_template(path: str):
    """Required sections from a template's "##" headings.

    When the file holds the template in a fenced block (as the skill's reference file does), only
    headings inside fences count; otherwise only headings outside fences count.
    """
    with open(path, encoding="utf-8") as f:
        return required_from_text(f.read())


def required_from_text(text: str):
    lines = text.splitlines()
    inside, outside = [], []
    in_fence = False
    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        m = HEADING_RE.match(line)
        if not m or len(m.group(1)) != 2 or re.search(r"\(optional\)", m.group(2), re.I):
            continue
        (inside if in_fence else outside).append(norm(m.group(2)))
    return inside or outside or DEFAULT_SECTIONS


def lint_file(path: str, required, force_mt: bool):
    with open(path, encoding="utf-8") as f:
        return lint_text(path, f.read(), required, force_mt)


def lint_text(path: str, text: str, required, force_mt: bool):
    plan = Plan(path, text)
    mt = force_mt or bool(re.search(r"^\s*Multi-tenant:\s*yes\b", "\n".join(plan.clean[: plan.header_end]), re.I | re.M))
    return Linter(plan, required, mt).run()


PASSING = """# Plan: Archive projects

Status: Draft
Approved-by:
Date: 2026-03-04
Issue: none
Multi-tenant: yes

## 1. Problem
- Problem: finished projects clutter every list and search, so leads lose time finding active work.
- Personas: project leads, team members, the account owner who pays per active project.
- Today: leads rename finished projects with a "zz-" prefix and ask members to ignore them.
- Success moment: a lead opens the project list on Monday and sees only work in progress.
- Success metric: share of projects renamed with the prefix drops to zero within a month.
- Non-goals: no deletion, no automatic archiving, no export of archived projects.
- Stress moment: the day before a client deadline, with five people searching for the right board.

## 2. Prior art
None found in the plans folder, the tracker (open and closed) and the ADR folder.

## 4. UX and states
| State | What the user sees |
|---|---|
| Empty | "No archived projects" with a link back to active projects |
| Loading | skeleton rows in the archived tab |
| Error | inline message with a retry button; the active list stays usable |
| Partial data | archived tab shows loaded projects and a notice that some failed to load |
| No permission | archive action hidden for members; server refuses with 403 |
| Limit reached | archiving frees an active-project slot; no new limit applies |

## 5. Data model
| Change | Existing data shapes and the behaviour for each | Index and the query it serves | Evidence |
|---|---|---|---|
| nullable archived_at on projects | never set: active, as today | partial index on active projects: list query | verified: schema file line 40 |

## 6. Reuse
- Existing mechanism extended: the project visibility filter in the list query service.
- Where the default lives: the visibility filter, active only unless asked otherwise.

## 7. API and automation
- Endpoints: POST and DELETE on the project archive route, archived flag on the project resource.
- IaC resource: N/A because the product has no infrastructure-as-code provider.

## 8. Events, jobs and caching
- Cache keys and invalidation: the project list cache tag is flushed on archive and restore.

## 9. Permissions, limits and audit
- Permissions: projects.archive, held by leads and owners.
- Audit entries: project archived and restored, with actor and public project ID.

## 10. Tenant isolation
| Surface | How tenant A is kept out of tenant B's data |
|---|---|
| API | archive route resolves the project inside the caller's organization; other IDs return 404 |
| Cache keys | list cache keys carry the organization ID |

## 11. Data protection
- New personal-data category: no
- New processor or sub-processor: no
- New retention period: no
- Third-country transfer: no
- Special-category data: no
- Handed to: N/A because no trigger is answered yes.

## 12. Dependencies
N/A because the feature uses no new library, service or external API.

## 13. Performance budget
- Volume: about 40 archive actions per day across all organizations.
- Queries per request and p95 target: two queries, p95 under 80 ms.

## 14. Failure modes
| Failure | Impact | Detection | Reaction |
|---|---|---|---|
| Database write fails | project stays active | error rate alert | user retries |
| Cache flush fails | archived project still listed | stale-list metric | cache expires in five minutes |
| Double click archives twice | none, the action is idempotent | none needed | none |

- Irreversible: nothing; restore brings a project back.
- Costs money or reaches people if it fires wrongly: nothing sends messages.

## 15. Test plan
- Feature tests for archive, restore and the list filter.
- Cross-tenant test: a lead of another organization gets 404 on archive.

## 16. Rollout and rollback
- Rollout: migration first, then the API, then the UI behind a flag that defaults to off.
- Rollback: turn the flag off; archived_at stays and is ignored by the old list query.

## 17. Implementation steps
| Step | Location | Done criterion | Depends on |
|---|---|---|---|
| 1 | migrations | archived_at exists, old rows unchanged | none |

## 18. Self-review
Peak volume, failure states, isolation, cost and rollback are answered above with numbers.

## 19. Open decisions
1. Should archived projects count toward the active-project limit?
   - Options: A, no; B, yes.
   - Recommendation: A, because archiving is how owners free a slot today by renaming.
"""

FAILING = """# Plan: Weekly digest

Approved-by:

## 1. Problem
- Problem: send a weekly email
- Personas:

## 2. Prior art

## 11. Data protection
- New personal-data category: maybe

## 14. Failure modes
| Failure | Impact | Detection | Reaction |
|---|---|---|---|
| Mail provider down | [ ] | TBD | later |

## 16. Rollout and rollback
- Rollout: N/A

## 19. Open decisions
- choose the send day
"""

EXPECTED_FAIL = {"P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08", "P10", "P11", "P12", "P13"}


def self_test() -> int:
    g = lint_text("pass.md", PASSING, DEFAULT_SECTIONS, False)
    b = lint_text("fail.md", FAILING, DEFAULT_SECTIONS, True)
    t = required_from_text("## 1. Problem\n## 2. Extra (optional)\n## 3. Rollout and rollback\n")
    ok = True
    if g:
        ok = False
        print("self-test: passing fixture has findings:")
        for n, code, msg in g:
            print(f"  pass.md:{n}: {code} {msg}")
    if t != ["problem", "rollout and rollback"]:
        ok = False
        print("self-test: template headings parsed as " + ", ".join(t))
    missing = EXPECTED_FAIL - {code for _, code, _ in b}
    if missing:
        ok = False
        print("self-test: failing fixture did not trigger: " + ", ".join(sorted(missing)))
    print("self-test passed" if ok else "self-test failed")
    return 0 if ok else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        prog="lint_plan.py",
        description=__doc__.split("\n\n", 1)[1],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("plans", nargs="*", help="plan files to check")
    ap.add_argument("--multi-tenant", action="store_true", help="require tenant isolation and a cross-tenant test")
    ap.add_argument("--template", help="take the required sections from this template file")
    ap.add_argument("--self-test", action="store_true", help="run the built-in passing and failing fixtures")
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.plans:
        ap.print_usage(sys.stderr)
        return 2
    required = DEFAULT_SECTIONS
    if args.template:
        try:
            required = required_from_template(args.template)
        except OSError as e:
            print(f"cannot read template: {e}", file=sys.stderr)
            return 2
    total = 0
    for path in args.plans:
        try:
            findings = lint_file(path, required, args.multi_tenant)
        except OSError as e:
            print(f"{path}: cannot read: {e}", file=sys.stderr)
            return 2
        for n, code, msg in findings:
            print(f"{path}:{n}: {code} {msg}")
        total += len(findings)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
