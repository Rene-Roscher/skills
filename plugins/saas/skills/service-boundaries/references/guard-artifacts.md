# Guard artifacts

## Contents
- CI guards
- Path-scoped rule
- AGENTS.md line

## CI guards

| Guard | Recipe: input, expected result |
|---|---|
| Extraction ADR | a pull request that adds a new service directory or deploy unit without an ADR from the template: review blocks it |
| Benchmarks | `bench/` holds the load script and a README; numbers in the ADR come from it |
| No database drivers in workers (Go) | `go list -deps ./... \| grep -E 'database/sql\|pgx\|lib/pq\|go-sql-driver'` prints nothing |
| Brain-only states off the wire | a contract test decodes every enum value the worker can send; none of the control-plane-only states is accepted |
| Contract tests | golden fixtures from the producer's real encoder decode in the consumer's suite; generated schemas show no drift |
| Protobuf | `buf breaking` against main runs blocking |
| Shared limits | a literal duplicate of a contract constant in either repo fails the build |
| No `APP_KEY` outside the app | in service repos `git grep -n APP_KEY` prints nothing; in the app, matches only in its own config and env template |
| Dedicated key at boot | starting the app without a configured relationship key fails |
| String path only (PHP) | an architecture test allows the cross-service encrypter only via `encryptString` and `decryptString`; `Crypt::decrypt(`, `decrypt(` on cross-service input fails |
| String path only (other repos) | grep for `\.(En\|De)crypt\(` (Go) or `\b(en\|de)crypt\(` (Node, Rust) finds nothing outside an allowlist with reasons |
| Interop vectors | Laravel encrypts, the other language decrypts, and the reverse, per Laravel major in use |
| Replay | expired payload, wrong purpose and reused `jti` are each rejected |
| Health | liveness independent of downstreams; readiness hysteresis; draining on SIGTERM |
| Bounds | each buffer filled past its cap increments its drop counter; duplicate delivery has one effect |
| Shutdown | in-flight work and a buffered result survive a SIGTERM |

Guard suites run whole with a minimum test count. A filter that matches nothing must fail, not pass.

## Path-scoped rule

Claude Code loads a rule in `.claude/rules/` with a `paths` list when it reads or edits a matching file, and
brace expansion works in the patterns (https://code.claude.com/docs/en/memory, verified 2026-10). The skill sets
no `paths`, because the decision comes before any file exists. Copy this into `.claude/rules/service-boundaries.md`:

```markdown
---
paths:
  - "**/CONTRACT.md"
  - "**/*.proto"
  - "**/buf.yaml"
  - "**/go.mod"
  - "**/Cargo.toml"
  - "**/{worker,workers,probe,agent,sidecar}/**"
  - "**/*{Encrypter,Crypt,Encryption}*.{php,go,rs,ts,js}"
  - "**/{healthz,readyz,health,readiness}*"
---

This file sits on a service boundary. Load the service-boundaries skill before changing contracts, keys,
health endpoints or worker behaviour.
```

## AGENTS.md line

```markdown
- Before proposing a new service, a worker or a rewrite in another language, load the service-boundaries skill.
```
