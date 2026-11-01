# Adopting an existing repository

## Contents

- Where facts live
- Writing an as-built spec
- The drift table
- Resolving drift
- What not to do

## Where facts live

Read these before any existing document. Each answers a question that docs often answer wrongly.

| Question | Read |
|---|---|
| Which versions run | lockfiles and the runtime pin (`composer.lock`, `package-lock.json`, `go.sum`, `.tool-versions`, the base image tag) |
| What the data looks like | migrations in order, the schema dump, model casts and constraints |
| What a user can reach | the route list from the framework's CLI, API resource classes, middleware groups |
| What runs in the background | job classes, queue config, the scheduler definition, cron files |
| Who may do what | policies, gates, permission enums, middleware |
| What a customer pays and gets | the billing config or plans table, limit checks at the call sites |
| What is stored about people, and how long | migrations, retention config, cleanup jobs, log config |
| What ships and how | CI workflows, Dockerfiles, deploy manifests in the repository that is actually applied |
| What the product promises | public pages, legal texts, API docs, mails; compare with the code above |

When two places name different values (a version in a Dockerfile and in a lockfile, a limit in config and in a
controller), that is drift inside the code. Record it the same way.

## Writing an as-built spec

1. One area at a time. Load the owning skill so that you know what to look for.
2. Write what the code does, not what it should do. Every statement carries `path:line` and a label: verified
   (read in this session), reported (from a doc, ticket, comment or subagent, not re-read) or inferred (reasoned
   from verified facts).
3. Put the paths you read on the `Code:` header line and today's date on `Checked against code:`.
4. Where the code breaks the area skill's rules (an internal ID in a URL, a query without tenant scope), write a
   finding under Open points with a linked issue. Fix nothing in this pass.
5. Set `Status: Implemented` only for statements you verified; the rest of the spec stays Draft.

Numbers from a subagent or a query tool are recounted from the raw data before they go into a spec. A tool that
returns null for a missing key and for a null value cannot tell "the field is nullable" from "this source has no
such field".

## The drift table

One row per disagreement, in the inception record:

```markdown
| # | Document says | Location | Code does | Location | Runs today | Resolution |
|---|---|---|---|---|---|---|
| 1 | API tokens expire after 30 days | `docs/security.md:12` | expiry is 90 days | `config/auth.php:41` | 90 days | Decision 3 |
| 2 | Exports are CSV only | `README.md:30` | CSV and XLSX | `src/export/formats.ts:8` | both | doc fixed |
```

- Locations are `path:line` on both sides.
- "Runs today" is what production does, which is not always what the main branch says; confirm which copy of
  infrastructure is live before writing it.
- Resolution is one of: doc fixed, code issue [link], decision [number].

## Resolving drift

- The document describes behaviour without promising it (a README list of formats, an architecture sketch): fix
  the document, note "doc fixed".
- The document states intent the owner or a customer relies on (a price, a limit, a contract or privacy promise,
  a security property such as token expiry or encryption): the row becomes a numbered open decision with the
  options "change the code", "change the promise" and their consequences. Neither side changes before the answer.
- The code contradicts itself: open a code issue and name both locations; the spec describes what runs and
  points at the issue.

## What not to do

- Copy an existing document into the new tree and call it a spec.
- Compare two documents with each other and report them as consistent.
- Fix code during the as-built pass. Findings become issues; the owner decides the order.
- Trust a folder named like the live infrastructure without confirming it is the one applied.
