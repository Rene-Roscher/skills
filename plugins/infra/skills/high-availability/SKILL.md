---
name: high-availability
description: "Designs and reviews failover and recovery for DNS (octoDNS to two providers), mail (failover chain), Kubernetes hosting, PostgreSQL (CloudNativePG, WAL, PITR) and object storage, with RPO/RTO per component, single-point-of-failure review and restore drills. Use when planning or auditing HA, backups or DR. Not for app retries, single-host dev setups or cost estimates."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
---

# High availability

This skill decides how a product survives the loss of one provider, one node, one zone or one operator mistake, and
how that survival is proven. It covers five components: DNS, mail, hosting, the database and object storage. Vendor
syntax stays with the vendor docs linked below; the skill keeps the decisions, the invariants and the traps. The
failure it prevents: a second provider, replica or backup that exists on paper, shares the failure domain of the
first, or has never been exercised, so the first real outage is also its first test.

## Applies when / does not apply

- Applies: you design, review or audit failover, backups, restores or disaster recovery; a manifest, mail config or
  DNS config is reviewed for single points of failure; someone asks "what happens if X goes down"; a drill or restore
  test is planned.
- Does not apply: retries, timeouts and circuit breakers inside application code; a single-host development
  compose file; capacity or cost estimates; Terraform or YAML syntax questions. Incident handling while an outage is
  running belongs to the incident process, not to this skill.
- Everything here is read-only advice and review. Never apply manifests, run `octodns-sync --doit`, call a cloud CLI
  or trigger a restore against production from this skill. Produce the change and the plan, and let the owner apply.

## Rules

### Objectives and failure domains

- [invariant] Write RPO and RTO per component (DNS, mail, each service tier, database, object storage, secrets) before
  you pick a design, and state which failure each number is meant to survive. Why: without a number, "highly
  available" cannot be checked, and a design is either over-built or silently misses the requirement. Test: ask for
  an HA design with no numbers; the reply opens with a component table that has RPO, RTO and the covered failure
  (node, zone, provider, operator error), or asks for the missing numbers. Source: none; design judgment. The
  CloudNativePG docs tie RPO to WAL archiving and RTO to backup frequency and measured restores:
  https://cloudnative-pg.io/docs/1.30/backup/ (verified 2026-11-01).
- [invariant] Keep a single-point-of-failure inventory: every component, the failure domain it sits in (provider,
  account, region, zone, node, credential, DNS zone, registrar, certificate authority, CI runner), and what stops if it
  fails. A second copy in the same domain is not redundancy. Why: replicas on one node, backups in the same account
  as the data, and two mail providers behind one API key fail together. Test: take a design with two database
  replicas on one node; the inventory lists the node as the shared domain and the design is marked non-redundant.
  Source: none; design judgment. CloudNativePG gives the same advice for instances: different worker nodes, no shared
  storage, different availability zones: https://cloudnative-pg.io/docs/1.30/architecture/ (verified 2026-11-01).
- [invariant] Status pages, uptime monitors, alert routing and the runbooks needed during an outage live in a failure
  domain that is independent of what they watch. Test: the inventory has no row where the monitor, its alert channel
  and the monitored service share a provider account or cluster; if the status page runs in the cluster it reports on,
  flag it. Why: a status page that goes down with the product tells customers nothing exactly when they look.
  Source: none; design judgment.

### DNS

- [invariant] Publish every production zone to at least two independent DNS providers from one source of truth, and
  delegate to both providers' nameservers at the registrar. With octoDNS this means two entries under the zone's
  `targets`. Why: with one provider, its outage or account lockout removes every name, including the names used to
  reach the recovery tooling. Test: `scripts/ha_check.py` reports HA-D01 for a zone with one target and is clean with
  two; a registrar record listing one provider's nameservers fails the review. Source:
  https://octodns.readthedocs.io/en/latest/getting-started.html (any number of sources and targets per zone, example
  with two targets), verified 2026-11-01.
- [invariant] Run `octodns-sync` as a plan first and apply with `--doit` only after a person has read the plan.
  Keep the default change-percentage safety limits; when they trip, read why instead of adding `--force`. Why:
  octoDNS takes ownership of the zone and deletes records it does not know about. The default safety limit is 30
  percent updates or deletes, and it applies only when the zone already has at least 10 records. A change to the root
  NS record always needs `--force`. Test: a plan that deletes 4 of 10 existing records aborts without `--force`; the
  agent reports the abort and does not retry with `--force`. Source:
  https://github.com/octodns/octodns/blob/main/octodns/provider/plan.py,
  https://github.com/octodns/octodns/blob/main/octodns/cmds/sync.py,
  https://octodns.readthedocs.io/en/latest/getting-started.html (verified 2026-11-01).
- [default] Use only record types that both providers serve identically. Treat provider-specific features (geo or
  weighted dynamic records, health-checked failover, ALIAS-style apex records) as an exception that needs a static
  fallback value. Trade-off: you give up provider-native traffic steering. Deviate only with an ADR that names this
  trade-off. Test: a dynamic record is pushed to a provider without dynamic support; octoDNS publishes its plain
  `values` instead. Source: https://octodns.readthedocs.io/en/latest/dynamic_records.html (dynamic support differs per
  provider; the top-level values serve providers without dynamic support) (verified 2026-11-01).
- [default] Keep TTLs on records that matter for failover short enough to meet the DNS RTO (and say the value), and
  keep the registrar account on hardware-key MFA with a second named owner. Trade-off: shorter TTLs raise query load
  and resolver traffic. Deviate only with an ADR that names this trade-off. Test: the DNS row of the inventory lists
  TTL, registrar and its owners. Source: none; design judgment.

### Mail

- [invariant] A failover or round-robin mail chain contains only transports that really send. It never contains
  `log`, `array` or `null`, neither as the last member nor anywhere else. Why: those transports always succeed, so
  when both real providers are down the alarm mail is reported as sent and nobody is woken. Laravel documents `log`
  as writing messages to the log files instead of sending them, and Symfony documents that its failover transport
  retries the next member until one succeeds or all fail, so a member that never fails ends the chain with success (the conclusion is an inference from those two
  documented behaviours, and `ha_check.py` flags it for that reason). Test: `scripts/ha_check.py` reports HA-M01 for a
  `failover` mailer whose `mailers` list contains a mailer with transport `log`, and HA-M02 for a Symfony DSN
  `failover(...null://null)`. Source: https://laravel.com/docs/12.x/mail (failover configuration, log driver),
  https://symfony.com/doc/current/mailer.html (failover, `null://null` for disabling delivery), verified 2026-11-01.
- [invariant] When every real transport fails, the failure must be loud: the send raises, the queued job fails and is
  retried, and a failed-job or dead-letter count alerts a human through a channel that does not use that mail path.
  Why: swallowed send errors turn an outage into silent message loss. Test: with both providers stubbed to refuse
  connections, the job ends in the failed-jobs table and the alert fires; no log line is the only trace. Source:
  none; design judgment, behaviour of the chain as documented at the Laravel and Symfony URLs above.
- [default] Use two providers on separate infrastructure and separate credentials, and give them the same verified
  sender domain (SPF, DKIM) before an incident. Use `failover` for availability, not `roundrobin`, which spreads
  load and is not an availability design. Trade-off: two vendor contracts and two reputations to warm up. Deviate only
  with an ADR that names this trade-off. Test: a message sent through the secondary alone passes SPF and DKIM
  alignment checks at a test mailbox. Source: https://laravel.com/docs/12.x/mail (roundrobin is load balancing,
  failover is high availability; verified 2026-11-01).
- [default] Send incident and security alarms over a second path that does not depend on the product's mail
  stack, such as a paging service or SMS. Trade-off: one more tool to keep current. Deviate only with an ADR that
  names this trade-off. Test: the alarm path still fires when the application's mail providers are unreachable.
  Source: none; design judgment.

### Hosting (Kubernetes)

- [invariant] A workload that matters runs at least two replicas, spread over different nodes and, where the cluster
  has them, different zones, and has a PodDisruptionBudget that matches its pods. Use `topologySpreadConstraints`
  or pod anti-affinity for the spread. Why: a Deployment defaults to one replica, and one replica is down at every
  node drain and every crash. Test: `scripts/ha_check.py` reports HA-K01 and HA-K02 for a Deployment with three
  replicas and no budget or spread rule, and HA-K04 for a critical-labelled workload with one replica. Source:
  https://kubernetes.io/docs/concepts/workloads/controllers/deployment/ (replicas default to 1),
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ (verified 2026-11-01).
- [invariant] Read a PodDisruptionBudget for what it covers: it limits voluntary evictions (drains, upgrades through
  the Eviction API), it does not stop crashes or node failure, and deleting a Deployment or Pod bypasses it. A budget
  of `maxUnavailable: 0` or `minAvailable` equal to all replicas makes a node drain hang. Why: teams count the budget
  as protection against outages and then block their own cluster upgrades. Test: a budget with `maxUnavailable: 0` is
  reported as HA-K05; a budget with `maxUnavailable: 1` over three replicas lets a drain proceed one pod at a time.
  Source: https://kubernetes.io/docs/tasks/run-application/configure-pdb/,
  https://kubernetes.io/docs/concepts/workloads/pods/disruptions/ (verified 2026-11-01).
- [default] Spread with `topologySpreadConstraints` over `topology.kubernetes.io/zone` and
  `kubernetes.io/hostname`, `maxSkew: 1`, `whenUnsatisfiable: DoNotSchedule` for the zone key on critical workloads.
  Trade-off: a pod stays Pending when a zone is gone and capacity is missing, and `ScheduleAnyway` trades that for
  possible co-location. Deviate only with an ADR that names this trade-off. Test: with one zone drained and
  `DoNotSchedule`, the pending pods are visible as an alert, not discovered by users. Source:
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/ (verified 2026-11-01).
- [invariant] Every serving container has a readiness probe, so a pod receives traffic only while it can serve, and
  shutdown is graceful: the process handles SIGTERM, a `preStop` hook or drain delay covers endpoint removal, and
  `terminationGracePeriodSeconds` is longer than the slowest request or drain. Liveness probes check only the
  process itself, never the database or another service. Why: a liveness probe that depends on the database
  restarts every pod at once when the database blips, which turns a partial outage into a total one. Test:
  `scripts/ha_check.py` reports HA-K03 for a container without `readinessProbe`; during a rolling update a request
  loop against the service shows no failed requests. Source:
  https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/,
  https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/ (verified
  2026-11-01); the liveness-dependency point is design judgment.
- [default] Keep state off the pods: sessions, uploads and queues live in the database, Redis or object storage, and
  the cluster itself is rebuildable from Git. Trade-off: more external services to make highly available themselves.
  Deviate only with an ADR that names this trade-off. Test: delete a pod and a node in a staging cluster; no user
  session or upload is lost. Source: none; design judgment.

### Database (PostgreSQL with CloudNativePG)

- [invariant] A production Cluster runs at least two instances, preferably three, on different nodes and zones,
  with the operator-managed PodDisruptionBudgets left enabled. Why: with `instances: 1` the default, a node loss is an
  outage and a restore. Test: `scripts/ha_check.py` reports HA-C01 for `instances: 1` or an unset value, and HA-C04
  for `enablePDB: false`. Source: https://cloudnative-pg.io/docs/1.30/architecture/,
  https://cloudnative-pg.io/docs/1.30/kubernetes_upgrade/ (operator keeps PDBs per cluster and recommends leaving them
  on), verified 2026-11-01.
- [invariant] Continuous backup means a WAL archive and base backups together, on a schedule, shipped to object
  storage the cluster does not own. A WAL archive alone cannot restore anything. For new clusters use the Barman
  Cloud plugin: the in-tree `barmanObjectStore` is deprecated, 1.31 is documented as the last minor release shipping
  it, and it is removed from 1.32.0. Check the operator version in use before choosing. Why: the archive gives
  point-in-time recovery and an RPO of minutes only when it works and base backups exist. Test:
  `scripts/ha_check.py` reports HA-C02 for a Cluster without a WAL-archiving plugin or backup section, HA-C03 for a
  Cluster no ScheduledBackup names, and warns HA-W01 on in-tree `barmanObjectStore`. Source:
  https://cloudnative-pg.io/docs/1.30/backup/, https://cloudnative-pg.io/docs/1.30/wal_archiving/,
  https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/ (verified 2026-11-01).
- [invariant] A ScheduledBackup uses a six-field cron expression with seconds first; a five-field Unix expression is
  wrong. Why: the schedule you meant and the schedule that runs differ silently. Test: `0 0 2 * * *` means daily at
  02:00:00; reviewing a ScheduledBackup with five fields is a finding. Source:
  https://cloudnative-pg.io/docs/1.30/backup/ (verified 2026-11-01).
- [default] Choose synchronous replication per RPO. `dataDurability: required` gives RPO 0 and pauses writes when
  the needed standbys are gone; `preferred` keeps writes available and can lose the last commits. Trade-off: write
  latency and availability against durability. Deviate only with an ADR that names this trade-off. Test: with all
  synchronous standbys stopped, writes block under `required` and continue under `preferred`. Source:
  https://cloudnative-pg.io/docs/1.30/replication/ (verified 2026-11-01).
- [invariant] Recovery targets use an explicit timezone, for example `2026-11-01T08:00:00Z`; a timestamp without one
  is read as UTC. Recovery creates a new Cluster from the object store and leaves the old one untouched, and a
  restored cluster does not archive WAL until the plugin section is added. Why: an unlabelled local time recovers to
  the wrong moment. Test: a review of a recovery manifest with `targetTime: "2026-11-01 08:00:00"` flags it (not covered by
  `ha_check.py`); with a `Z` or offset suffix it passes. Source: https://cloudnative-pg.io/docs/1.30/recovery/,
  https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/ (verified 2026-11-01).

### Object storage and backups

- [invariant] Keep at least one backup copy in a different failure domain than the data: another provider or at
  minimum another account and region, with credentials the production workload cannot use to delete it. Why:
  backups in the same account as production disappear together with it, and with one leaked key. Test: the inventory
  shows the backup bucket's account and provider differ from production, and the production credentials have no
  delete permission on the backup copy. Source: none; design judgment. S3 replication is asynchronous, so a copy
  lags: https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html (verified 2026-11-01).
- [default] Use object lock (WORM) on backup buckets that matter, in compliance mode only when you accept that nobody,
  including the account root, can delete before the date. Object lock needs versioning, protects individual versions,
  and a plain delete only adds a delete marker. Trade-off: storage cost for the retention period, and
  governance mode can still be bypassed by principals with the right permission. Deviate only with an ADR that names
  this trade-off. Test: a permanent delete of a locked version returns 403; a delete without version id returns 200
  and adds a delete marker. Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html
  (verified 2026-11-01). Other S3-compatible vendors differ; read their docs before relying on it.
- [invariant] For replication, the destination bucket needs object lock enabled when the source has it, and delete
  markers are not replicated by default under the current replication configuration schema. Why: replication is
  not a backup, because it copies mistakes and, if enabled, deletions. Test: delete an object in the source of a
  test pair; confirm what the destination shows before relying on the setup. Source:
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html,
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html (verified
  2026-11-01).

### Proof

- [invariant] A backup that was never restored is not a backup. Restore from the off-site copy into an isolated
  namespace or account on a schedule, run a point-in-time restore to a stated target, check row counts or a known
  business record, and record the measured time against the RTO. Why: untested backups fail on missing credentials,
  absent base backups, version mismatches and endless replay. Test: the drill log has a date within the agreed
  interval, the restore source, the target time, the check and the measured duration; no log, no backup claim.
  Source: https://cloudnative-pg.io/docs/1.30/backup/ ("Regularly test restoring from your backups. Measure the time
  required for a full recovery."), verified 2026-11-01.
- [invariant] Alert on the age of the last successful backup and last archived WAL segment, and on drill age, not on
  whether a backup job exists. Why: a job that fails every night still exists. Test: pause the ScheduledBackup in a
  test cluster; the age alert fires within one schedule interval. Source: none; design judgment.
- [default] Run a game day at least once a year and after any architecture change: pick a failure from the failure
  mode table, announce it, inject it in staging or in a production window the owner approved, and compare behaviour
  with the prediction. Trade-off: engineer time and some risk. Deviate only with an ADR that names this trade-off.
  Test: each game day produces a findings list with owners and dates. Source: none; design judgment.

## Procedure

1. Ask for the RPO and RTO of every component and the failures that must be survived. Record them in a table.
2. Build the single-point-of-failure inventory. Mark every shared failure domain, including registrar, credentials
   and the place where monitoring runs. Read [references/dns-mail.md](references/dns-mail.md) for DNS and mail,
   [references/kubernetes.md](references/kubernetes.md) for hosting and
   [references/database-storage.md](references/database-storage.md) for the database and object storage.
3. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/ha_check.py [repo-dir]` over the repository and add its findings to the
   inventory. The script is a heuristic starting point: it reads a fixed set of patterns and cannot see live state,
   cloud settings, Helm templates (it skips them, so render first) or anything outside the repository.
4. Fill the failure mode table from [references/drills.md](references/drills.md): for each failure, the expected
   behaviour, the detection and the recovery step, and mark the rows that were never tested.
5. Propose the smallest set of changes that closes the gaps, as manifests or config diffs and an octoDNS plan. Do not
   apply them. State which finding each change closes and what it costs.
6. Define the drill: restore, failover and game day, with owner, interval and evidence. Read
   [references/drills.md](references/drills.md).
7. Report: component table, inventory, findings by severity, untested claims, and what you did not verify.

## Traps

- A failover chain whose last member is `log` or `array` in a "safe for development" config that production reuses.
- Two DNS providers configured in octoDNS while the registrar still delegates to one.
- Adding `--force` to push through an octoDNS plan that tripped the safety limit.
- A PodDisruptionBudget with `maxUnavailable: 0` that blocks every node drain.
- Three replicas on one node, because the scheduler was only asked to prefer spreading.
- A liveness probe that calls the database.
- A WAL archive with no base backup, or a backup bucket whose retention expires the base backup before the WAL.
- The in-tree `barmanObjectStore` kept past the operator version that removes it.
- Backups and production sharing one cloud account and one key.
- Replication read as backup, so a deletion is copied faithfully.
- A restore that works only because the engineer's personal credentials are still valid.
- A status page hosted in the cluster it reports on.

## Done when

- RPO and RTO exist per component, with the failure each one covers.
- The inventory names the failure domain of every component and none of the critical ones share one.
- DNS publishes to two providers, mail has a chain with no discarding member, workloads have replicas, spread,
  budgets and probes, the database has instances, a WAL archive, base backups and a schedule, and the off-site copy
  lives in another domain.
- A restore drill has been run against the off-site copy with a measured time, or the report says it has not.
- Nothing was applied to production, and every unverified claim is marked.

## References

- [references/dns-mail.md](references/dns-mail.md): read when you review DNS delegation, octoDNS config, sync
  safety or mail failover.
- [references/kubernetes.md](references/kubernetes.md): read when you review Deployments, StatefulSets, budgets,
  spread rules, probes or shutdown behaviour.
- [references/database-storage.md](references/database-storage.md): read when you review CloudNativePG clusters,
  backups, PITR, replication or object storage.
- [references/drills.md](references/drills.md): read when you write the failure mode table, a restore drill or a
  game day.

## Sources

- https://octodns.readthedocs.io/en/latest/getting-started.html: any number of sources and targets per zone, plan
  by default and `--doit` to apply, octoDNS takes ownership of the zone, verified 2026-11-01.
- https://github.com/octodns/octodns/blob/main/octodns/provider/plan.py: default update and delete limits of 30
  percent, minimum of 10 existing records, root NS change always unsafe, verified 2026-11-01.
- https://github.com/octodns/octodns/blob/main/octodns/cmds/sync.py: `--doit`, `--force`, `--checksum` options,
  verified 2026-11-01.
- https://octodns.readthedocs.io/en/latest/dynamic_records.html: dynamic records depend on provider support,
  verified 2026-11-01.
- https://laravel.com/docs/12.x/mail and https://symfony.com/doc/current/mailer.html: failover and round-robin
  transports, `log` and `null` transports, verified 2026-11-01.
- https://cloudnative-pg.io/docs/1.30/backup/, https://cloudnative-pg.io/docs/1.30/wal_archiving/,
  https://cloudnative-pg.io/docs/1.30/recovery/, https://cloudnative-pg.io/docs/1.30/replication/,
  https://cloudnative-pg.io/docs/1.30/architecture/, https://cloudnative-pg.io/docs/1.30/kubernetes_upgrade/,
  https://cloudnative-pg.io/plugin-barman-cloud/docs/usage/: backups, WAL archive, plugin migration and deprecation
  dates, PITR, synchronous replication, PDBs, verified 2026-11-01.
- https://kubernetes.io/docs/tasks/run-application/configure-pdb/,
  https://kubernetes.io/docs/concepts/workloads/pods/disruptions/,
  https://kubernetes.io/docs/concepts/scheduling-eviction/topology-spread-constraints/,
  https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/,
  https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/,
  https://kubernetes.io/docs/concepts/workloads/controllers/deployment/: budgets, spread, probes, shutdown,
  verified 2026-11-01.
- https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html,
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-managing.html,
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication-what-is-isnot-replicated.html,
  https://docs.aws.amazon.com/AmazonS3/latest/userguide/replication.html: Object Lock modes, versioning,
  replication behaviour, verified 2026-11-01.
