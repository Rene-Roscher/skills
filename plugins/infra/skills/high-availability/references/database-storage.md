# Database and object storage

## Contents

- Choosing RPO and RTO for the database
- CloudNativePG layout
- Backup: WAL archive, base backups, schedule
- Plugin versus in-tree backup
- Point-in-time recovery
- Replication and durability
- Off-site copy, immutability and object storage
- Monitoring
- Review checklist

## Choosing RPO and RTO for the database

State the numbers first. RPO is driven by WAL archiving and replication mode, RTO by base backup size, number of WAL
files to replay and how fast storage and network are. CloudNativePG states an RPO of five minutes or less with a
configured WAL archive, and says restore tests should measure real recovery time. Source:
https://cloudnative-pg.io/docs/1.30/backup/ (verified 2026-11-01).

| Failure | Covered by | Typical RPO | Typical RTO driver |
|---|---|---|---|
| Pod or node loss | Replicas, automated failover | 0 with synchronous, small otherwise | Failover time |
| Zone loss | Instances in other zones | as above | Failover time, capacity |
| Cluster or region loss | Restore from off-site copy or a replica cluster elsewhere | Archive lag | Provisioning plus restore |
| Operator error (bad migration, deleted table) | PITR from archive | Chosen target time | Restore plus replay |
| Provider or account loss | Copy in another provider | Replication lag of that copy | Provisioning plus restore |

Replication does not cover operator error: it replicates the mistake. Only point-in-time recovery does.

## CloudNativePG layout

- `instances` of at least two, preferably three. The API default is one. Source:
  https://cloudnative-pg.io/docs/1.30/cloudnative-pg.v1 (the `instances` field defaults to 1) (verified 2026-11-01).
- Instances on different nodes and zones, sharing nothing but the network. The operator adds pod anti-affinity by
  default as preferred (`podAntiAffinityType: preferred`, topology key `kubernetes.io/hostname`); `required` can leave
  pods pending when nodes are missing. Sources: https://cloudnative-pg.io/docs/1.30/architecture/,
  https://cloudnative-pg.io/docs/1.30/scheduling/ (verified 2026-11-01).
- Each cluster gets PodDisruptionBudgets from the operator, and the docs recommend leaving them enabled
  (`enablePDB`). Source: https://cloudnative-pg.io/docs/1.30/kubernetes_upgrade/ (verified 2026-11-01).
- Applications connect through the operator's read-write service, never to a pod name, so a failover needs no
  config change.
- The operator manages only its own Kubernetes cluster. Failover between clusters is coordinated by people or
  tooling. Source: https://cloudnative-pg.io/docs/1.30/architecture/ (verified 2026-11-01).

## Backup: WAL archive, base backups, schedule

- Object-store backups always require WAL archiving, support hot backups, take no incremental copies, and support
  retention. Volume snapshots can be incremental and do not require WAL archiving, but archiving is still
  recommended in production. Source: https://cloudnative-pg.io/docs/1.30/backup/ (verified 2026-11-01).
- A WAL archive alone restores nothing; base backups are required. Same source.
- `ScheduledBackup` is the recommended way to run base backups. Its schedule has six fields with seconds first. The
  docs call a weekly base backup sufficient in most cases and say full backups more often than daily are rare. Same
  source.
- By default backups run on the most up-to-date standby and fall back to the primary; with a single instance they
  load the primary. Same source.
- On-demand backups do not include the Kubernetes Secrets for the superuser and the application user. Back those up
  by the cluster-level or secret-manager path. Same source.
- `archive_timeout` defaults to five minutes, so a quiet database still closes and archives segments. Source:
  https://cloudnative-pg.io/docs/1.30/wal_archiving/ (verified 2026-11-01).

## Plugin versus in-tree backup

- Native backup and recovery are being phased out of the core operator in favour of CNPG-I plugins since 1.26. The
  community-supported plugin is the Barman Cloud plugin. Source: https://cloudnative-pg.io/docs/1.30/backup/
  (verified 2026-11-01).
- The in-tree `spec.backup.barmanObjectStore` is deprecated. The WAL archiving page states that 1.31 is the last minor
  release shipping it and that it is removed from 1.32.0. Source: https://cloudnative-pg.io/docs/1.30/wal_archiving/
  (verified 2026-11-01). A cluster still on it needs a migration plan before the operator upgrade; the plugin docs
  carry a migration guide: https://cloudnative-pg.io/plugin-barman-cloud/docs/migration/ (verified 2026-11-01).
- `spec.backup.retentionPolicy` on the Cluster is deprecated too; set `retentionPolicy` on the plugin's
  `ObjectStore` (recovery-window syntax such as `30d`). Sources: https://cloudnative-pg.io/docs/1.30/backup/,
  https://cloudnative-pg.io/plugin-barman-cloud/docs/retention/ (verified 2026-11-01).
- Plugin shape: an `ObjectStore` resource defines the bucket, endpoint and credentials; the Cluster references it in
  `spec.plugins` with `isWALArchiver: true` and the `barmanObjectName` parameter. Only one plugin may be the WAL
  archiver. Source: https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/ (verified 2026-11-01).
- Check the version pair (operator, plugin, PostgreSQL image) against the vendor's compatibility notes; this skill
  does not pin versions.

## Point-in-time recovery

- Recovery bootstraps a new cluster from the object store. The old cluster is not touched. The recovery stanza
  references an `externalClusters` entry that names the plugin, the object store and the `serverName` of the
  source. Source: https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/ (verified 2026-11-01).
- `recoveryTarget.targetTime` takes an RFC 3339 timestamp or a PostgreSQL timestamp. A timestamp without a zone is read
  as UTC; always write the zone. With `targetTime` or `targetLSN` the operator picks the closest backup completed
  before the target. Source: https://cloudnative-pg.io/docs/1.30/recovery/ (verified 2026-11-01).
- The restored cluster does not archive WAL unless you add the plugin section next to `externalClusters`. Source:
  https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/ (verified 2026-11-01).
- Target time must be after the end of the chosen base backup. Tablespace changes after the last base backup break
  replay, so take a base backup after such a change. Source: https://cloudnative-pg.io/docs/1.30/recovery/
  (verified 2026-11-01).
- Switching applications to the restored cluster is a separate, deliberate step with its own checks (data, schema
  version, connection strings, sequences).

## Replication and durability

- Synchronous replication is off by default. `postgresql.synchronous` with `method`, `number` and `dataDurability`
  configures it. `required` (the default when synchronous is set) pauses writes when the needed standbys are
  unavailable and gives RPO 0. `preferred` keeps writes going and can lose recent commits. Source:
  https://cloudnative-pg.io/docs/1.30/replication/ (verified 2026-11-01).
- Choose by RPO: financial or ledger data usually wants `required` with three instances so one standby can fail
  without stopping writes; content or telemetry usually accepts `preferred` or asynchronous.
- A replica cluster in another region follows the WAL archive and extends disaster recovery across regions. Source:
  https://cloudnative-pg.io/docs/1.30/backup/ (verified 2026-11-01).

## Off-site copy, immutability and object storage

- The backup target must be outside the failure domain of the data: another provider, or another account and region
  with separate credentials. The cluster's credentials need write access to its own prefix and no permission to
  delete or shorten retention of the off-site copy.
- Two ways to get the second copy: write backups to two object stores (two `ObjectStore` resources, one archiver at a
  time, so the second is usually fed by a copy job), or replicate the first bucket to a second provider or region
  with the vendor's replication or a sync tool. Replication is asynchronous, so the copy lags. Source:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html (verified 2026-11-01).
- With S3 replication, delete markers are not replicated by default under the current configuration schema, and
  lifecycle-created markers are not replicated. Source:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html (verified
  2026-11-01).
- Object Lock: needs versioning; retention periods or legal holds protect single versions; compliance mode cannot be
  shortened or removed by anyone including the account root, governance mode can be bypassed with a specific
  permission and header; a permanent delete of a locked version returns 403, a simple delete adds a delete marker.
  The destination bucket of a replication must also have Object Lock enabled when the source has it. Sources:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html,
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html (verified 2026-11-01).
- Retention in the lock and retention in the backup tool must be consistent: if the tool deletes backups after 30
  days and the lock lasts 90, deletes fail and storage grows; if the lock is shorter, it protects nothing the tool
  can later remove.
- Other S3-compatible services implement Object Lock, versioning and replication with differences. Unverified for any
  given vendor until you read that vendor's docs.
- User uploads and other primary object data: same questions as the database. Versioning on, replication or a second
  copy elsewhere, a restore test, and a stated RPO.

## Monitoring

- Alert on: age of the last completed base backup, age of the last archived WAL segment, backup phase not
  completed, replication lag, ready instances below the target, off-site copy age, and drill age.
- The checks run from outside the cluster that holds the database (see the monitoring rule in SKILL.md).

## Review checklist

- RPO and RTO per data store, with the covered failures.
- At least two instances, spread, budgets on.
- WAL archiving through the plugin (or a documented migration date for the in-tree setting) plus a ScheduledBackup.
- Off-site copy in another domain, delete-proof for the production credentials, locked where it matters.
- PITR tested to a chosen timestamp with an explicit zone, duration recorded.
- Secrets and credentials needed to restore are available without the failed system.
