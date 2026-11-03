# Contract template and change playbook

## Contents
- Contract file template
- Change playbook
- Consumer copy and drift check

## Contract file template

```markdown
# Contract: [producer] -> [consumer(s)]   (version [N], canonical in [producer repo])

Read before touching any field, endpoint or limit below. Consumers: [repo list]. Each carries a copy that names
the version it implements.

## Transport and auth
Endpoint or topic, method, TLS, auth scheme, timeouts, idempotency key header.

## Messages
| Message | Field | Type | Unit | Nullable / absent | Since | Notes |
|---|---|---|---|---|---|---|

IDs: strings. Timestamps: RFC 3339, UTC. Empty collections: [] or {}, never null.

## Enums
| Enum | Values | Unknown value handling |
Receivers drop and count unknown values. States computed only by the control plane are not listed here.

## Status and error semantics
| Response | Meaning | Client action (retry, back off, drop, quarantine) |
"Not modified" for config pulls: [status code or flag; exactly one].

## Shared limits
| Name | Value | Sender behaviour | Receiver behaviour |
Defined once in [generated file per language].

## Versioning
Current version N. Receivers accept N and N-1, warn down to min_supported, reject below.
Where the version travels: [envelope field | record header | protobuf field].

## Critical payloads
Which payloads are encrypted, their scope names, expiry, single-use id.

## Deploy order
1. Consumers accept the new shape. 2. Producer sends it. 3. Old shape removed after [metric] reads zero for [period].

## Fixtures
Location, generator command, versions kept.
```

## Change playbook

| Change | Steps |
|---|---|
| Add optional field | Producer adds it; fixtures regenerated; consumers may ignore it until they need it. |
| Rename | Add the new field; producer writes both; consumers read the new one with fallback; metric shows the old one unread; producer stops writing the old one; protobuf reserves the old number and name. |
| Retype | Treat as rename: a new field with the new type. Never change the type in place. |
| Remove | Consumers stop reading it first; then the producer stops writing; protobuf reserves number and name. |
| New required field | New message version N+1. Consumers accept N and N+1 before any producer sends N+1. |
| New enum value | Consumers already drop and count unknown values; add the value; then ship the consumer that handles it. |
| Tighten a limit | Receiver keeps the old limit until every sender enforces the new one. |
| Loosen a limit | Receiver loosens first, sender second. |

## Consumer copy and drift check

The consumer repo keeps `CONTRACT.md` with a first line such as `Implements: [producer]@contract-v7`. A CI job
fetches the canonical file at that tag (or reads it from the pinned fixture bundle) and runs `diff`; any difference
fails. Bumping the pin is a reviewed change in the consumer repo, and the same change updates the consumer's
contract tests.
