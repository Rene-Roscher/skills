# Self-update and rollout rings

## Contents
- Update sequence
- Offline key handling
- Rollout record
- Rings and halt criteria
- Rollback
- Tests

## Update sequence

```text
1  receive target (version, digest per platform, signature location) from the control plane
2  refuse if target version < running version and no signed rollback flag
3  take an exclusive lock (one updater at a time)
4  download to [install dir]/.agent.new-[random]; cap the size
5  compute SHA-256 while streaming; compare with the target digest
6  verify the signature over that digest with the compiled-in public key; fail closed
7  hardlink or copy the running binary to agent.previous
8  fsync the new file, rename over the live path, fsync the directory
9  restart through the service manager
10 new process reports healthy within the deadline, or the watchdog restores agent.previous and restarts
11 report success, refusal or rollback to the control plane with the reason
```

Steps 5 and 6 come before anything on disk changes. Step 10 needs a watchdog that is not the new binary itself:
the service manager, a small supervisor, or the previous binary started with a "confirm or revert" timer.

## Offline key handling

- The private key lives on a hardware token or in a KMS key whose use needs a human approval.
- CI builds and uploads unsigned candidates; a maintainer signs the digests offline; a second job publishes only
  when every artifact has a valid signature for the compiled-in key.
- The public key is compiled in. Rotation ships a binary that trusts old and new keys, waits until the fleet runs
  it, then signs with the new key only.
- Decide and document whether these signatures go to a public transparency log.

## Rollout record

| Field | Example |
|---|---|
| version | `v1.8.0` |
| artifacts | platform → `sha256:...`, signature reference |
| ring | `canary`, `early`, `broad` |
| share | percentage of hosts in the ring, chosen by a stable hash of the host ID |
| bake time | minimum time before the next ring |
| halt rules | thresholds below |
| previous | the digests to roll back to |

Host selection by a stable hash keeps the same hosts in the early ring across releases, so a problem host shows up
early every time.

## Rings and halt criteria

| Ring | Who | Promote when |
|---|---|---|
| canary | internal and test hosts | bake time passed, no halt rule fired |
| early | a small share of customer hosts | bake time passed, health matches the control group |
| broad | everyone else, possibly in steps | early ring clean |

Halt rules compare the ring with hosts still on the previous version over the same window:

- Update failures and automatic rollbacks above a small absolute count.
- Missed heartbeats or crash restarts above the control group's rate.
- Error or decode-failure counters on the receiving side above the control group's rate.

A halted rollout stays halted until a person resumes or rolls back. Promotion is automatic only when no rule fired.

## Rollback

- Point the ring's rollout record at the previous digests. Hosts treat this as a signed rollback target, so step 2
  of the sequence allows the lower version.
- Never rebuild or re-tag an old version to roll back.
- Hosts with automatic updates turned off by their owner stay where they are; the control plane lists them.

## Tests

| Test | Expected |
|---|---|
| tampered binary, matching checksum from the same origin | refused, running binary unchanged, refusal reported |
| valid signature, wrong digest for the platform | refused |
| older version without rollback flag | refused |
| new binary exits at start | previous binary restored and running |
| two update triggers at once | second waits for or skips on the lock |
| canary health regression | rollout halted, early ring never receives the version |
