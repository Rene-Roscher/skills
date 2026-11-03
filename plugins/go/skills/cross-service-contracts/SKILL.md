---
name: cross-service-contracts
description: "Designs and enforces wire contracts between repos and languages: one contract file per relationship, protobuf field discipline with buf breaking as a blocking gate, JSON-over-Kafka evolution, producer-made golden fixtures tested by PHP, Go, Rust and Node consumers, encrypted envelopes, pull-only control planes. Use when changing a shared message, schema or worker endpoint. Not for in-repo APIs."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# Cross-service contracts

This skill decides how a message, schema or endpoint shared between independently built repos is written down,
changed and tested, so that both sides keep agreeing without a shared build. It goes deeper than
`service-boundaries`, which decides whether to extract a service and owns the shape of the boundary (dumb worker,
pull-only links, per-service keys). Protobuf, buf and Kafka syntax stay in their docs. The failure it prevents: a
field renamed on one side, both CIs green, and ingestion or registration silently stopping in production.

## Applies when / does not apply

- Applies: a protobuf file, a JSON event on Kafka or another broker, a worker-to-control-plane HTTP endpoint, an
  encrypted token passed between services, a file or table one repo writes and another reads; adding, renaming,
  retyping or removing any field there; writing `CONTRACT.md`; contract tests in CI.
- Does not apply: whether to split a service out (`service-boundaries`); public REST API design for customers;
  routes and payloads inside one repository; Go service internals (`go-service-baseline`); database migrations.

## Rules

Ordered by blast radius. Examples use a control plane in PHP, a Go worker fleet and a Rust ingest service.

### The contract artifact

- [invariant] Each relationship (one producer and its consumers, or one control plane and its workers) has one
  canonical contract file in the producer's repo: transport and auth, every message with field, type, unit,
  nullability and "since" version, status and error semantics, shared limits, versioning and accept band, deploy
  order, and which payloads are critical. Each consumer repo carries a copy that names the contract version it
  implements, and its CI fails when the copy differs from the canonical file at that version.
  Why: without a single written owner, each side documents its own reading and the two drift. Test: edit one line
  of the consumer's copy; the drift check fails and names the file. Source: reproducible with the test above.
- [invariant] Evolution is additive. Add fields; never rename, retype or reuse one. A rename is a new field, a
  period in which the producer writes both, and a removal once a metric shows no consumer reads the old one. A new
  field that the consumer requires is a new message version, not an edit. Why: there is no moment at which a fleet
  of independently deployed binaries upgrades at once. Test: the producer's golden test (below) shows the diff,
  and the N-1 fixtures still decode in every consumer. Source: protobuf "Almost never change the type of a field;
  it'll mess up deserialization, same as re-using a tag number"
  (https://protobuf.dev/best-practices/dos-donts/, verified 2026-11).
- [invariant] The deploy order is written in the contract and followed: consumers that accept the new shape ship
  first, producers start sending it second, removal comes last. For control plane and workers, the side that
  decides accepts new input before the side that executes sends it. Why: a producer that ships first sends data no
  deployed consumer can read. Test: the release checklist for a contract change links the consumer release that
  accepts the new shape before the producer change merges. Source: for backward-compatible schemas, "upgrade all
  consumers before you start producing new events"
  (https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html, verified 2026-11).
- [invariant] Numbers both sides must agree on (maximum message size, batch size, interacting timeouts, version
  accept band) are defined once in the contract and generated or imported into each language, never typed twice.
  The sender drops what exceeds a limit; the receiver rejects it. Why: a sender cap four times the receiver's limit
  fails every large batch on arrival. Test: a CI grep finds no literal copy of a contract constant outside the
  generated file. Source: reproducible with the test above.

### Protobuf

- [invariant] Field numbers are permanent: never reused, never renumbered. Deleting a field reserves its number and
  its name. Every enum starts with `[ENUM]_UNSPECIFIED = 0`; receivers treat an unknown or unspecified value as
  unknown (drop or quarantine, count it), never as a meaningful default. A unit test in each language pins the
  field numbers and reserved ranges of every contract message. Why: a reused number makes old and new senders
  decode into the wrong field without an error. Test: renumber one field on a scratch branch; the pin test and
  `buf breaking` both fail. Source: "Never re-use a tag number"; "reserve its tag number so that no one
  accidentally re-uses it"; "Enums should include a default FOO_UNSPECIFIED value as the first value"
  (https://protobuf.dev/best-practices/dos-donts/, verified 2026-11).
- [invariant] `buf lint` and `buf breaking` run on every pull request against the main branch as required checks,
  never with `continue-on-error`. Use the `WIRE_JSON` category when any consumer reads the JSON encoding of these
  messages, and the default `FILE` category when other repos compile the generated code. In shallow CI clones,
  point `--against` at the remote repository or fetch the base branch. Why: an advisory breaking check reports
  only after the break is merged. Test: remove a field without reserving it on a scratch branch; the required check
  is red and blocks the merge. Source: categories FILE (default), PACKAGE, WIRE_JSON, WIRE, and
  `buf breaking --against '.git#branch=main'` (https://buf.build/docs/breaking/); "Many CI services, including
  GitHub Actions, run shallow clones" (https://buf.build/docs/breaking/usage/); both verified 2026-11.
- [default] Messages carry a `schema_version`; receivers accept the current version and the previous one, warn
  down to a published minimum and reject below it. Trade-off: two decode paths during every transition. Deviate
  only with an ADR that names this trade-off. Test: a fixture at `min_supported - 1` is rejected with a counted
  reason; N-1 decodes. Source: reproducible with the test above.

### JSON on a broker

- [invariant] Every JSON event names its type and version (an envelope field or a record header), is keyed by the
  entity whose order matters, encodes 64-bit IDs as strings, timestamps as RFC 3339 UTC, and defines absent versus
  `null` per field. Why: events with one key land in one partition and are read in order, while numbers above
  2^53 − 1 lose precision in JavaScript and some JSON decoders. Test: byte-exact golden fixtures cover a large ID,
  a non-UTC input time normalised to UTC, an empty map and an absent optional field. Source: Kafka "Events with the
  same event key ... are written to the same partition" and are read "in exactly the same order"
  (https://kafka.apache.org/intro); `Number.MAX_SAFE_INTEGER` is 2^53 − 1
  (https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER); both
  verified 2026-11.
- [invariant] Wire consumers ignore unknown fields; only local config parsing rejects them. In Go that means no
  `DisallowUnknownFields` on wire decoders; in PHP, Rust and Node no strict "deny unknown" mode on wire types. Why:
  a consumer that rejects unknown fields turns every additive producer change into an outage. Test: a fixture with
  an extra field decodes in every consumer. Source: Go `encoding/json` "By default, object keys which don't have a
  corresponding struct field are ignored" (https://pkg.go.dev/encoding/json#Unmarshal, verified 2026-11).
- [default] With a schema registry, set each subject's compatibility explicitly to a transitive mode
  (`BACKWARD_TRANSITIVE` when consumers upgrade first, `FULL_TRANSITIVE` when either side may deploy first).
  Without a registry, the kept fixtures of every supported version are the compatibility check. Trade-off: a
  transitive mode blocks changes that are compatible only with the latest version. Deviate only with an ADR that
  names this trade-off. Source: BACKWARD is the default; BACKWARD_TRANSITIVE covers "X, X-1, or X-2"
  (https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html, verified 2026-11).

### Tests in both repos

- [invariant] Golden fixtures are generated by the producer's real encoder, never written by hand: one file per
  message type and version, committed in the producer repo, with a byte-exact producer test that fails when the
  encoder output changes. Fixtures of every still-accepted version are kept. Why: hand-written fixtures prove only
  that a test agrees with itself. Test: change a JSON tag in the producer; the producer's golden test fails until
  the fixture is regenerated and reviewed. Source: reproducible with the test above.
- [invariant] Every consumer (PHP, Go, Rust, Node) has a contract test that decodes each producer fixture for the
  versions it claims and asserts field values, and it runs as a required check in the consumer's CI. The consumer
  pins the producer fixture version it tests against; a scheduled job also tests the producer's main branch to see
  the next change early. Why: without a consumer-side test, a one-sided change leaves both CIs green. Test: update
  the pinned fixtures to a version with a renamed field; the consumer job turns red. Source: reproducible with the
  test above.
- [default] Generated artifacts (JSON Schema, TypeScript types, PHP DTOs, field-number tables) come from one source
  and CI fails when the committed output differs from a fresh generation. Trade-off: a generator step in every
  repo's toolchain. Deviate only with an ADR that names this trade-off. Test: edit a generated file by hand; the
  drift job fails.
  Source: reproducible with the test above.

### Encryption and control planes

- [invariant] Encrypted payloads between services use the string API of a Laravel-compatible encryption package
  with a per-relationship key, wrapped in an interop envelope that names a scope and an expiry; the receiver opens
  with the expected scope. Interop vectors produced by the real counterpart run in CI in both directions. Key
  handling, replay protection and rotation are owned by `service-boundaries`. Why: the serialize path and a shared
  application key turn one compromised service into a compromised application. Test: an envelope opened with the
  wrong scope fails with `scope_mismatch`, an expired one with `expired`, and a vector sealed in PHP opens in Go and
  the reverse. Source: https://github.com/Rene-Roscher/laravel-interop (envelope fields and error kinds),
  https://github.com/Rene-Roscher/laravel-go-encryption (`EncryptString`, `Seal`, `Open`), both verified 2026-11.
- [default] Control planes are pull-only and the contract says so: workers register, pull config by content hash,
  and send heartbeats; the "not modified" answer is spelled out (a status code or a flag, one of them); commands
  ride back on the heartbeat response; the control plane never connects into a worker. States that only the
  control plane computes never appear in the wire enum. Trade-off: a command waits up to one heartbeat interval.
  Deviate only with an ADR that names this trade-off. Test: register, pull, receive "not modified" on an equal
  hash, receive a change on the next pull, receive a drain command on a heartbeat; the wire enum test lists only
  worker-observable states. Source: boundary rules in `service-boundaries`; reproducible with the test above.

## Procedure

1. Gate: does another repo, language or independently deployed binary read this data? If not, stop.
2. Find the canonical contract file and the consumers that implement it. No contract file: write one first
   (references/contract-template.md).
3. Classify the change: additive, rename, retype, removal, new required field, new limit. Use the playbook in the
   template for anything but additive.
4. Protobuf: reserve, pin, run `buf breaking` locally against main.
5. Regenerate golden fixtures with the producer's encoder; keep old versions.
6. Update each consumer's contract test and fixture pin; ship consumers first.
7. Ship the producer; watch the unknown-value and decode-error counters.
8. Remove the old shape only after a metric shows nobody sends or reads it.

## Traps

- `buf breaking` configured but run with `continue-on-error`, or only after merge, or never because the base
  branch is missing from a shallow clone.
- A consumer test that decodes a fixture the consumer team wrote by hand. It passes forever.
- Strict decoding copied from the config loader into a wire decoder.
- An enum that grew a control-plane-only state; old workers decode it as zero and act on it.
- `int64` IDs as JSON numbers: correct in Go and PHP, wrong in a browser or a Node consumer above 2^53 − 1.
- A limit typed as a literal in each repo; it diverges at the next tuning.
- "Both sides deploy together" in a fleet where some workers update hours later or never.
- A second, hand-written decryption of the same envelope next to the library.

## Done when

- One canonical contract file exists; every consumer pins its version and checks its copy for drift.
- Protobuf field numbers are pinned in tests; `buf lint` and `buf breaking` are required checks.
- Producer golden fixtures are byte-exact and generated; every consumer decodes them in a required check.
- The deploy order of the change is written down and the consumer release precedes the producer release.
- Unknown fields are ignored and unknown enum values are counted in every consumer.

## References

- [references/contract-template.md](references/contract-template.md): load when writing a contract file or
  planning a rename, retype, removal or new required field.
- [references/golden-fixtures.md](references/golden-fixtures.md): load when setting up fixture generation,
  distribution and consumer tests in PHP, Go, Rust or Node.
- [references/protobuf-and-buf.md](references/protobuf-and-buf.md): load when adding protobuf contracts, buf
  configuration, the field-pin test or the CI step.

## Sources

- https://protobuf.dev/best-practices/dos-donts/: tag reuse, reserved numbers, type changes, UNSPECIFIED enum
  values, verified 2026-11.
- https://buf.build/docs/breaking/ and https://buf.build/docs/breaking/usage/: categories, `--against`, shallow
  clones, verified 2026-11.
- https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html: compatibility
  modes, consumer-first upgrade order, verified 2026-11.
- https://kafka.apache.org/intro: keys, partitions and per-partition order, verified 2026-11.
- https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER: safe
  integer limit, verified 2026-11.
- https://pkg.go.dev/encoding/json#Unmarshal: unknown fields ignored by default, `DisallowUnknownFields`, verified
  2026-11.
- https://github.com/Rene-Roscher/laravel-interop and https://github.com/Rene-Roscher/laravel-go-encryption:
  envelope format, string API, `Seal`/`Open`, verified 2026-11.
