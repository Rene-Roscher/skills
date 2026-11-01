# Drills, failure modes and game days

## Contents

- Failure mode table
- Restore drill procedure
- Failover drill procedure
- Game day procedure
- Evidence and cadence
- Drill log template

## Failure mode table

Fill one row per failure. Mark the "tested" column honestly: a claim that was never exercised is a hypothesis.

| Failure | Expected behaviour | Detection | Recovery step | Tested (date or never) |
|---|---|---|---|---|
| One pod crashes | Service continues, pod restarts | Restart count alert | none | |
| One node lost | Pods rescheduled, budgets hold | Node not ready alert | Replace node | |
| One zone lost | Replicas in other zones serve, pending pods alerted | Zone alert, pending pods | Add capacity | |
| Database primary lost | Replica promoted, apps reconnect through the service | Failover event, lag alert | Rebuild replica | |
| Database data damaged by a bad change | PITR to a time before the change | Application checks | Restore to new cluster, switch | |
| Whole cluster lost | Rebuild from Git, restore data from off-site | Synthetic check fails | Provision, restore, DNS | |
| Primary DNS provider down | Second provider answers | Probes against both providers' nameservers | none, then repair | |
| Registrar or DNS account locked | Zone source in Git, second provider live | Probe | Re-delegate through registrar | |
| Primary mail provider down | Chain uses the secondary | Failed-send metric | none, then repair | |
| All mail providers down | Sends fail loudly, jobs retry, a human is paged by another channel | Failed-job alert, paging | Fix or add a provider | |
| Object storage region or provider down | Reads from the copy, writes queued or failed loudly | Storage probe | Switch endpoint | |
| Backup credentials leaked or deleted backups | Locked copy survives | Backup age alert, audit log | Restore from locked copy | |
| Certificate expires or CA unreachable | Renewal alert early, spare issuer ready | Expiry alert | Re-issue | |
| Status page host down | Status page on another domain stays up | External probe | none | |
| CI runner or registry down | Last known good image still deployable | Pipeline alert | Alternate registry mirror | |

Add the components of your own system, especially every row of the single-point-of-failure inventory.

## Restore drill procedure

Goal: prove that the off-site copy restores, and measure how long it takes.

1. Pick the scenario: latest state, or a point in time with an explicit timezone (for example, one hour ago).
2. Prepare an isolated target: a separate namespace, cluster or account with no route to production data stores and
   no production credentials beyond read access to the off-site copy.
3. Start the clock. Restore from the off-site copy, not from the primary bucket.
4. For PostgreSQL with CloudNativePG: create a new Cluster whose `bootstrap.recovery` references the object store and,
   for point-in-time recovery, a `recoveryTarget.targetTime`. Do not point it at the production cluster name.
5. Verify: the cluster reaches ready, row counts of key tables match a reference, a known business record from just
   before the target exists and one from just after does not, migrations are at the expected version, and an
   application started against the copy passes a smoke test.
6. Stop the clock. Compare with the RTO. Note the restored point against the RPO.
7. Destroy the target. Record the result in the drill log, including every manual step that was needed and every
   credential that had to be found.
8. File each gap as a tracked item with an owner.

Do not run the restore against production or with production write credentials. A restore into the production
namespace under the production cluster name is an incident, not a drill.

## Failover drill procedure

Goal: prove the automatic paths work.

- Database: in staging (or a window the owner approved), delete the primary pod, then record time to a new primary
  and failed requests. Repeat with a node drain. Check that the replica is rebuilt.
- Workloads: drain a node with the budget in place and watch the request loop; drain a zone in staging and check
  pending pods and alerts.
- DNS: query each provider's nameservers directly for the critical names; remove one provider from the resolver
  path in a test resolver and confirm answers continue.
- Mail: block the primary provider in staging and confirm the secondary delivers; block both and confirm a failed
  job and a page through the independent channel.
- Storage: read through the secondary endpoint.

## Game day procedure

1. Before: choose one row of the failure mode table, write the predicted behaviour and the abort condition, name an
   owner and a scribe, announce the window, and confirm rollback.
2. During: inject the failure, watch the dashboards that an on-call person would use, and write down what actually
   happened with timestamps. If the abort condition is hit, stop and restore.
3. After: compare prediction and result, list surprises, assign owners and dates, update the runbook and the table.
4. Repeat for the next row. Cover every row at least once a year and after any change to the architecture.

## Evidence and cadence

- A drill that leaves no log did not happen.
- Suggested cadence, to adapt to the RPO and RTO: restore drill monthly or quarterly for the database, after every
  backup tooling change, and before any major upgrade; failover drills quarterly; game day yearly. Source: none;
  design judgment, based on the CloudNativePG advice to test restores regularly and measure recovery time
  (https://cloudnative-pg.io/docs/1.30/backup/, verified 2026-11-01).
- Alert on drill age the same way as on backup age.

## Drill log template

```text
Date / owner:
Scenario (failure, target time with timezone):
Source of the copy:
Isolated target:
Start / end / measured duration (RTO target):
Restored point versus RPO target:
Checks run and results:
Manual steps and credentials that were needed:
Gaps found, owner, due date:
```
