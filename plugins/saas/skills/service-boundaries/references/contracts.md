# Contracts between repos

## Contents
- `CONTRACT.md` skeleton
- Evolution rules
- Tests that keep both sides honest
- Protobuf

Basics only. Protobuf style and lint rules are out of scope here.

## `CONTRACT.md` skeleton

```markdown
# Contract: [producer] -> [consumer]
Read before touching any field, endpoint or limit below. The other side is [repo]; its copy must match.

## Transport and auth
Endpoint(s), method, TLS, auth scheme, timeouts.

## Messages
| Field | Type | Unit | Nullable | Since version | Notes |

## Status semantics
What each HTTP status or error code means and what the client does (retry, back off, drop).

## Shared limits
Max message size, max batch size, interacting timeouts. Defined once in [module]; both sides import it.

## Versioning
Current schema version N. Consumers accept N and N-1.

## Critical payloads
Which payloads carry `exp`, purpose and single-use `jti`.

## Deploy order
1. Consumer accepts the new shape. 2. Producer starts sending it. 3. Old shape removed after [condition].
```

## Evolution rules

- Additive only. Add a field; never rename or retype one. A rename is a new field plus a later removal.
- Consumers ignore unknown fields.
- During a rollout consumers accept both the old and the new shape.
- Removal happens only after every producer in the fleet sends the new shape, checked by a metric, not by date.
- Control plane before data plane: the side that decides accepts new input before the side that executes sends
  it.

## Tests that keep both sides honest

| Test | What it proves |
|---|---|
| Golden fixtures from the producer's real encoder, decoded in the consumer's tests | the consumer reads what the producer actually writes |
| Byte-exact golden tests for encoders that feed another system (ID encoding, UTC timestamps, empty maps versus null) | small serialisation changes are caught |
| Generated schemas or types (JSON Schema, TypeScript) checked for drift in CI | generated artifacts match the source |
| Shared-limit test: a literal duplicate of a contract constant fails | limits cannot diverge |
| Accept-band test: version N-1 messages still decode | rollouts do not break old producers |

Guard tests run as a whole suite with a minimum test count. A filter that matches nothing must fail.

## Protobuf

- Run `buf breaking` against the main branch and keep it blocking, never allowed to fail.
- CI services that run shallow clones lack the main branch. Point `--against` at the remote repository URL or
  check out the base commit separately (https://buf.build/docs/breaking/usage/,
  https://buf.build/docs/bsr/ci-cd/github-actions/, verified 2026-10).
- Two branches from the same main can produce a false positive on the second merge. Merge main into the branch
  before the check (https://buf.build/docs/bsr/ci-cd/setup/, verified 2026-10).
- Check the flags against the installed buf version.
