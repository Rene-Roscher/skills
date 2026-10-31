# Dependency admission

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

## Admission record

```yaml
- name: vendor/package
  ecosystem: composer
  purpose: Render invoice PDFs from HTML
  platform_first: "No built-in PDF renderer in the framework at the installed version"
  license: MIT
  maintenance: "Last release 2026-09; security policy present; checked 2026-10-31"
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
