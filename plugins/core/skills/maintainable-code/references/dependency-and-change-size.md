# Dependencies, flags and change size

Load when you add a dependency or a feature flag, or when a change is growing past one review sitting.

## Dependency checklist

Answer each item in the change description. A "no" on the first item ends the check.

1. Need: what exact job does it do, and how many lines would the job take without it? A job that takes a few
   dozen lines of plain code usually means write it (design judgment, no source).
2. Alternatives: the standard library, a dependency already installed, or the framework's own feature.
3. Maintenance: date of the last release and last commit, open security advisories, number of maintainers, how
   issues are answered. A project with a public scorecard (https://scorecard.dev/, an OpenSSF project that
   assesses open source projects for risky practices, verified 2026-11-01) gives a quick second opinion;
   treat it as one input.
4. Licence: compatible with how you distribute the product. Check the packages it pulls in too.
5. Size and weight: install size, transitive dependencies, build time, runtime cost in the bundle or process.
6. Fit: does it match the runtime and framework versions you pin, and the way the project already solves this?
7. Containment: is it behind one adapter or one module, so replacing it touches one place?
8. Exit: what would you do if it were abandoned? Is the data or format portable?
9. Pinning: the lockfile changes in the same change, installed from a clean checkout.

Product-level questions (a payment provider, a mail service, hosting) belong to `build-vs-buy`.

Record the decision in an ADR when the dependency is new in kind (first ORM, first queue client) or replaces an
existing one. A routine small library needs only the checklist answers in the change description.

## Feature flags

A flag is code that has two behaviours and a switch. The Fowler article distinguishes release, experiment,
operations and permission flags (https://martinfowler.com/articles/feature-toggles.html, verified 2026-11-01);
the first two are short-lived and the others may live long.

For each new flag record: name, kind, owner, purpose, default, and either a removal date or the sentence
"long-lived, reason: ...". Put the removal as a task in the backlog in the same change. The same article mentions teams that add a test which fails once a flag is past its expiry date.

Removing a release flag: switch it on everywhere, delete the old branch and the flag, delete tests of the old
path, and delete the configuration entry. Do this in one change.

Keep the number of live flags low. Each one doubles the paths a test has to cover.

## Change size

Source: https://google.github.io/eng-practices/review/developer/small-cls.html (verified 2026-11-01).

- One self-contained change per review: one purpose, with its tests, understandable without future work.
- Refactoring in a separate change from behaviour changes. Small local cleanups (a variable name) can ride
  along.
- Splitting patterns: by layer (data, service, endpoint), by step (prepare the seam, switch one caller, switch
  the rest, delete the old code), or by file group, each leaving the system working.
- If a change has grown past what you could review in one sitting, stop and split it before asking for review.
  Reviewers may reject a change for size alone.
- A mechanical change across many files (a rename, a format, a generated update) is its own change, with the
  command that produced it in the description, so a reviewer checks the command and samples the result.

## Review your own diff

Read it as a reviewer: new patterns, unused code, parameters nobody passes, swallowed errors, comments that
restate code, flags without owners, files that changed only for formatting. Remove them, or explain them.
