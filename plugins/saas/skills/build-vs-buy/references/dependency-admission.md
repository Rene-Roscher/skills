# Dependency admission

## Contents

- Checklist
- Health and reach check (`dep_health.py`): sources, thresholds, verdicts, limits of the signals
- Copying a few lines instead of depending
- Admission record
- Audit and license commands
- Optional CI gate

Load when adding any package or provider. The checklist answers the seven points of the admission rule; the
record goes into the PR description, the ADR, or the dependency register.

## Checklist

| Point | Check | Not admissible when |
|---|---|---|
| Platform first | The framework or language docs for the installed version (from the lockfile) | The platform already does it and the package adds nothing you need |
| Maintenance | Recent releases and commits, archived flag, how security reports are answered, open advisories | Archived, or security reports go unanswered |
| License | SPDX identifier in the package metadata and a license file in the source | No license, or a license incompatible with how you ship |
| Supply chain | Lockfile pinning, install or post-install scripts, transitive dependency count, known vulnerabilities, signed releases or provenance | Unexplained install scripts, or known vulnerabilities without a fixed version |
| Blast radius | Where it runs (request path, worker, build only) and what it can reach (network, filesystem, secrets, other tenants' data) | It needs more reach than its job requires |
| Personal data | Whether it sends personal data or visitor IP addresses to a third party | It does, and the compliance checklist is not done |
| Exit | Cost of replacing it; whether it sits behind an adapter | High exit cost on a commodity capability without an adapter |

Activity metrics are signals, not proof. OpenSSF Scorecard's "Maintained" check gives the highest score "if
there is at least one commit per week during the previous 90 days", and its other checks include License,
Pinned-Dependencies, Signed-Releases, Vulnerabilities, Dependency-Update-Tool, Security-Policy and
Binary-Artifacts (https://github.com/ossf/scorecard/blob/main/docs/checks.md, verified 2026-10).

When the agent cannot reach the registry, the repository or the docs, it writes "unverified" next to the
license and maintenance answers and names the command or page that would confirm them. A user's memory ("it
was maintained last year") is a claim to check, not a result.

## Health and reach check

`scripts/dep_health.py` reads maintenance, license, advisory and reach signals from public APIs and prints
each with its source URL and date, then a verdict with every reason. Run it first for any new package; its
JSON output goes into the admission record. It answers part of the maintenance, license and supply-chain
points. Platform first, blast radius, personal data and exit stay manual.

Sources, each checked against its docs and a recorded response on 2026-11-04:

| Source | Signals | Docs |
|---|---|---|
| deps.dev API v3 | versions and publish dates, default version, deprecation, licenses, advisories on the default version, source repository, OpenSSF Scorecard | https://docs.deps.dev/api/v3/ |
| deps.dev v3alpha `:dependents` | direct dependents (npm, Cargo, PyPI; public dependents only, "indicative of relative popularity") | https://github.com/google/deps.dev/blob/main/api/v3alpha/apiv3alpha.proto |
| npm registry, api.npmjs.org | maintainers, license, deprecation; downloads in the last 30 days | https://github.com/npm/registry/blob/main/docs/download-counts.md |
| Packagist API, Composer v2 metadata | monthly downloads, dependents, suggesters, favers, maintainers, abandoned; latest stable version, time, license | https://packagist.org/apidoc |
| PyPI JSON API | license expression, vulnerabilities of the latest release. Download counts are always `-1` there, so PyPI has no download signal | https://docs.pypi.org/api/json/ |
| OSV query | advisories for the latest Packagist version (deps.dev has no Packagist) | https://google.github.io/osv.dev/post-v1-query/ |
| GitHub REST | stars, archived, last push, license, contributors (first 100) | https://docs.github.com/en/rest/repos/repos |

Thresholds, the same table as at the top of the script. "Hard fact" is a recorded state. "Cited" takes its
number from the source. "Practice, unverified" is a working default without a citable source; a project
overlay can set other numbers.

| Threshold | Value | Kind | Effect | Source |
|---|---|---|---|---|
| Repository archived | yes | hard fact | reject | Scorecard Maintained: archived gets the lowest score, https://github.com/ossf/scorecard/blob/main/docs/checks.md (verified 2026-11) |
| Deprecated or abandoned | yes | hard fact | reject | registry flag |
| No license | yes | hard fact | reject | "Verify that every component has a license", OpenSSF Concise Guide, https://best.openssf.org/Concise-Guide-for-Evaluating-Open-Source-Software (verified 2026-11) |
| Advisory on the latest version | 1 or more | hard fact | reject | deps.dev advisory keys or OSV |
| Last release | over 365 days | cited | adopt-with-adr | Concise Guide: "the last release was issued within the previous 12 months" |
| Last push | over 365 days | cited | adopt-with-adr | Concise Guide: "significant recent activity (e.g., commits) ... within the previous 12 months" |
| Bus factor | below 2 | cited | reach floor | Concise Guide: "more than one maintainer"; measured as the CHAOSS Contributor Absence Factor, https://chaoss.community/kb/metric-contributor-absence-factor/ (verified 2026-11) |
| Downloads per month | npm 50,000, Packagist 10,000 | practice, unverified | reach floor | none found |
| Direct dependents | 20 | practice, unverified | reach floor | none found |
| GitHub stars | 100 | practice, unverified | reach floor | none found |
| Needed scope | 300 lines or fewer | practice, unverified | build-in-house | owner's rule |

Verdicts, in this order:

| Verdict | When | Exit |
|---|---|---|
| `reject` | any hard fact above | 1 |
| `build-in-house` | reach is low (more than half of the measured reach floors missed) and `--scope-lines` is at most 300 | 1 |
| `adopt-with-adr` | low reach with a larger or unknown scope, a stale release or push, or an unread archived state, license, advisory list or release date | 1 |
| `adopt` | none of the above | 0 |

Exit 2 is a usage error or an unknown package, exit 3 means the registry or network could not be reached.
`adopt-with-adr` asks the owner to decide and to record the decision; an agent never picks it alone.

Limits of the signals:

- Bus factor counts commit share among the first 100 contributors, bots excluded. Large, healthy projects
  often score 1 because one author holds half the commit history. That is why it is one floor among four
  and never decides alone.
- The registry's maintainer list is who can publish, not who maintains: Packagist listed one maintainer for a
  framework with hundreds of contributors. It is reported, not scored.
- deps.dev counts dependents per version; the default version carries most of them. A count of 0 is treated
  as not read, because deps.dev returned 0 for every version of a widely used Cargo crate.
- Downloads include CI and mirror traffic, and Go and Cargo have no download source in the script. Stars can
  be bought. Read the signals together, as the verdict does.
- Similar names: the Concise Guide asks whether "a similar name is more popular", a sign of typosquatting.
  The script does not check this; look at the registry search before adding a little-known package.

## Copying a few lines instead of depending

Review-ready draft, not legal advice. Scope: copying source code from an open-source package into a
closed-source product; the license text is the primary source.

| License class | Copying the needed lines | Source |
|---|---|---|
| Permissive (MIT, ISC, BSD, 0BSD, Zlib) | permitted; keep the copyright line and license text next to the copied code | MIT: "The above copyright notice and this permission notice shall be included in all copies or substantial portions", https://opensource.org/license/mit (verified 2026-11) |
| Apache-2.0 | permitted; also include the license, mark changed files, keep the notices and the relevant NOTICE content | section 4, https://www.apache.org/licenses/LICENSE-2.0 (verified 2026-11) |
| MPL-2.0, LGPL, EPL | the copied code stays under that license ("The copyleft applies to any files containing MPLed code"); ask the owner | https://www.mozilla.org/en-US/MPL/2.0/FAQ/ (verified 2026-11) |
| GPL, AGPL | do not copy into a closed-source product; write it fresh | license text |
| No license | no rights granted; do not copy, write it fresh without the source open | Concise Guide (license clarity) |

An `OR` expression takes the most permissive branch, an `AND` expression the strictest term. A Composer
license array is a choice ("disjunctive license", https://getcomposer.org/doc/04-schema.md#license, verified
2026-11), so the script reads it as `OR`.

## Admission record

```yaml
- name: vendor/package
  ecosystem: composer
  purpose: Render invoice PDFs from HTML
  platform_first: "No built-in PDF renderer in the framework at the installed version"
  license: MIT
  maintenance: "Last release 2026-09; security policy present; checked 2026-10-31"
  health_check: "dep_health.py adopt, 2026-10-31 (JSON attached)"
  supply_chain: "Pinned in composer.lock; no install scripts; 4 transitive packages; composer audit clean"
  blast_radius: "Queue worker only; no network; writes to a temp directory"
  personal_data: "Invoice content stays in-process"
  exit: "Behind DocumentRenderer interface; a second implementation exists in tests"
  owner: billing team
```

The same fields serve as the dependency register entry when the project keeps one.

## Audit and license commands

Run them at the versions CI uses, and read `--help` there before adding flags.

| Ecosystem | Vulnerabilities | Licenses | Checked |
|---|---|---|---|
| Composer | `composer audit --locked --abandoned=fail` | `composer licenses --locked --format=json` | Composer 2.9.2 `--help`, 2026-10-31 |
| npm | `npm audit --audit-level=high`; `npm audit signatures` for registry signatures | no built-in command; use a license checker and an allowlist | npm 11.6.2 `--help`, 2026-10-31 |
| Go | `govulncheck ./...`, which exits non-zero when it finds vulnerabilities | from module metadata | https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck, 2026-10-31 |
| Several, from lockfiles | `osv-scanner scan source -r .` or `osv-scanner scan -L [lockfile]` | | https://google.github.io/osv-scanner/usage/, 2026-10-31 |

For a deep audit of a dependency tree (advisories, abandoned upstreams, publisher concentration, install
scripts), use a dedicated supply-chain audit tool or skill. This skill decides admission; it does not replace
that audit.

## Optional CI gate

Whether a missing register entry blocks the merge is a project decision; record it in the project overlay.

1. Diff the manifests (`composer.json`, `package.json`, `go.mod`, `pyproject.toml`) between base and head.
2. For each added direct dependency, look up its entry in the register. Fail with the package name when it is
   missing.
3. Run the license command and compare each license with an allowlist. Fail on anything outside it.
4. Run the vulnerability audit per ecosystem. Fail on findings without a recorded exception and expiry date.
