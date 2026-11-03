---
name: observability-and-dr
description: "Sets rules for alerting, telemetry and disaster recovery: SLOs and symptom alerts, tested alert rules (absent(), not count over an empty vector), an external dead-man's switch, logs and error reports without secrets or PII, trace context, timed restore drills, executed DR runbooks and blameless postmortems. Use when writing alert rules, dashboards, runbooks or postmortems. Not for app debugging."
license: Apache-2.0
metadata:
  author: "Rene Roscher"
paths:
  - "**/alertmanager*.y*ml"
  - "**/prometheus*.y*ml"
  - "**/*prometheusrule*.y*ml"
  - "**/runbooks/**"
---

# Observability and disaster recovery

This skill decides what is measured, what wakes a person, what may be written to logs and error trackers, and how
recovery is proven. Prometheus and Alertmanager are the examples; the rules hold for other stacks. Failover design,
RPO and RTO per component and the drill format live in `high-availability`; this skill makes sure the alerts and
the drills actually work. The failure this prevents: a total outage that pages nobody because the alert
expression cannot fire, the alert pipeline itself is dead, or the alert went to a channel nobody reads, followed
by a restore that was never timed.

## Applies when / does not apply

- Applies: SLOs, alert rules, Alertmanager routing, dashboards, log and error-tracker configuration, tracing
  setup, backup monitoring, restore drills, DR runbooks, postmortems and their action items.
- Does not apply: debugging one application error, choosing a monitoring vendor, failover architecture
  (`high-availability`), uptime checks a customer configures in a product.

## Rules

### Objectives and alerts

- [invariant] Every customer-facing service has an SLO (an availability or latency target over a window) and its
  paging alerts fire on symptoms users feel: error rate, latency, the error budget burning. Causes (CPU, disk, a
  single pod) go to tickets or dashboards unless they predict a symptom. Why: the SRE book pages on symptoms and
  keeps "cause-oriented heuristics to serve as aids to debugging". Test: each paging rule names the SLO or
  user-visible symptom it protects in its annotations. Source:
  https://sre.google/sre-book/monitoring-distributed-systems/, verified 2026-11-03.
- [default] Page on multiwindow burn rates: for a 99.9 % SLO, burn rate 14.4 over 1 hour with a 5-minute short
  window, and 6 over 6 hours with 30 minutes; ticket at 1 over 3 days with 6 hours. Trade-off: more rules and
  recording rules than a plain threshold. Deviate only with an ADR that names this trade-off. Source:
  https://sre.google/workbook/alerting-on-slos/, verified 2026-11-03.
- [invariant] Every alert rule has a unit test that makes it fire and one that keeps it quiet, run with
  `promtool test rules` in CI. A "nothing is up" condition uses `absent()` or `absent_over_time()`; never compare
  `count(... == 1) == 0`, because when every target is down the inner filter is empty, `count` of an empty vector
  is empty, and the alert never fires. Why: the rule looks right in review and stays silent in the one outage it
  was written for. Test: the promtool case in [references/alert-rules.md](references/alert-rules.md) shows the
  `count` rule silent and the `absent` rule firing for the same all-down input. Source:
  https://prometheus.io/docs/prometheus/latest/querying/functions/ (`absent` returns a 1-element vector "if the
  vector passed to it has no elements") and
  https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/, verified 2026-11-03; behaviour
  reproduced with promtool from Prometheus 2.53.
- [invariant] Every job that alerting depends on has an `absent()` rule for its own metrics, and gauges that each
  replica exports are aggregated with `max()` or `min()`, not `sum()`. Why: a target that disappears from
  discovery produces no series and no alert; a sum of per-replica copies doubles with the replica count. Test:
  remove the scrape target in a test; the absence alert fires. Source: reproducible with the promtool test above.
- [invariant] The alerting pipeline has an external dead-man's switch: an always-firing alert (Watchdog) routed
  to a heartbeat service outside the cluster and outside the alerting provider, which pages when the heartbeat
  stops. Never route it to a null receiver. Why: the runbook says the Watchdog "is meant to ensure that the entire
  alerting pipeline is functional"; without an outside listener, a dead Prometheus or Alertmanager is silent.
  Test: stop Alertmanager in staging; the external service pages within its stated interval. Source:
  https://runbooks.prometheus-operator.dev/runbooks/general/watchdog/, verified 2026-11-03.
- [invariant] Severity follows impact: critical means customers are affected or redundancy is gone and reaches a
  person through a paging path with acknowledgement; warning means failover absorbed it and goes to a ticket or
  channel. Critical alerts reach the operator, not only a customer-facing status. Why: an alert that only changed
  what customers saw once ran for hours before an operator noticed. Test: fire each critical rule in staging; a
  person acknowledges it on the paging path. Source: reproducible with the test above.
- [invariant] After an incident, replay the alert rules against the recorded series of that incident and record
  when each would have fired. Why: thresholds chosen in a meeting often miss the real shape. Test: the postmortem
  lists the replay result per rule. Source: reproducible with `promtool test rules` using the incident's series.

### Dashboards, logs, errors and traces

- [default] One dashboard per service, as code next to the service, with the four golden signals (latency,
  traffic, errors, saturation) and its SLO at the top, and Prometheus retention bounded by size below the disk.
  Trade-off: dashboards change by pull request, not by clicking. Deviate only with an ADR that names this
  trade-off. Source: https://sre.google/sre-book/monitoring-distributed-systems/, verified 2026-11-03.
- [invariant] Logs carry no secrets and no personal data beyond what the purpose needs: no passwords, access
  tokens, session IDs, connection strings, keys or payment data; IP addresses and emails only where the retention
  and legal basis cover them. Redact at the logger, not in the log store. Why: logs are copied, shipped and kept
  longer than the data they describe. Test: a log-scrubbing unit test feeds a request with a bearer token and a
  password field and asserts neither reaches the output. Source:
  https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html ("Data to exclude"), verified
  2026-11-03.
- [invariant] The error tracker scrubs before sending: no default PII, request bodies off for sensitive routes,
  local-variable capture off or filtered, and a `before_send` hook that removes tokens, cookies and authorization
  headers. Server-side scrubbing is a second layer, not the first. Why: in the Python SDK `include_local_variables`
  defaults to `True`, so a token held in a local variable travels with the stack frame. Test: raise an error in a
  function holding a fake token; the event received by a test transport contains no token. Source:
  https://docs.sentry.io/platforms/python/configuration/options/ and
  https://docs.sentry.io/platforms/python/data-management/sensitive-data/, verified 2026-11-03.
- [default] Propagate W3C trace context (`traceparent`) across HTTP and queue boundaries and write the trace ID
  into every log line, with head sampling at a stated rate and errors always kept. Trade-off: header and storage
  cost. Deviate only with an ADR that names this trade-off. Source: https://www.w3.org/TR/trace-context/,
  verified 2026-11-03.

### Recovery

- [invariant] Every backup job exports a last-success timestamp, written only after success, and an alert fires
  when it is older than the schedule allows. Why: one staleness alert catches failed runs and runs that never
  started. Test: disable the job; the alert fires after one missed interval. Source: reproducible with the test
  above.
- [invariant] Restores are drilled on a schedule into a throwaway environment, timed from "start" to "service
  answers correctly", and the time is compared with the RTO; data is checked (row counts, checksums, a known
  record). A backup that was never restored counts as missing. Why: an untested restore fails on credentials,
  versions or missing pieces exactly when it is needed. Test: the drill log has date, operator, duration, data
  check result and RTO verdict. Source: drill format in `high-availability`; reproducible with the drill itself.
- [invariant] A DR runbook is marked "executed" only with the date of a real run and the measured times; a runbook
  that was never run is labelled draft. Runbooks distinguish planned from emergency procedures where the steps
  differ (for example, flipping a mirror reverses its delete direction). Why: a concept document mistaken for a
  tested procedure fails under pressure. Test: every runbook has a status line and a last-run date. Source:
  reproducible with the test above.
- [invariant] Postmortems are blameless, focus on contributing causes, and end with action items that each have
  an owner, a due date and a tracker link; open items are reviewed until closed. Why: the SRE book asks
  postmortems to "focus on identifying the contributing causes of the incident" and stores them only once
  "those involved are satisfied with the document and its action items". Test: no postmortem older than its due
  dates has an action item without a tracker link. Source: https://sre.google/sre-book/postmortem-culture/,
  verified 2026-11-03.

## Procedure

1. Gate: list the services, their SLOs and the RPO and RTO from `high-availability`. Missing numbers come first.
2. For each SLO, write burn-rate rules and a unit test that fires and one that stays quiet.
3. Add `absent()` rules for every job alerting depends on; replace any `count(...) == 0` pattern.
4. Wire the Watchdog to an external heartbeat and test it by stopping Alertmanager in staging.
5. Check logging and error-tracker config against [references/telemetry-hygiene.md](references/telemetry-hygiene.md).
6. Plan or review the restore drill and runbook status with [references/drills-postmortems.md](references/drills-postmortems.md).
7. Report: rules added with their tests, pipeline checks, scrubbing gaps, drill dates and measured times, and what
   was not verified. Do not change production alerting or run restores against production from this skill.

## Traps

- `count(up{job="x"} == 1) == 0` for "all targets down": silent in exactly that case.
- `absent()` over anything but a plain selector returns no labels, so label-based routing misses it; set
  labels on the rule.
- The Watchdog routed to a `null` receiver.
- Critical alerts that only change a public status and reach no operator.
- `sum()` over a gauge that every replica exports.
- An error tracker capturing frame locals that hold bearer tokens.
- A backup "success" log line written before the upload finished.
- A DR document that says "concept, never run" and is linked from the on-call page as the procedure.
- Action items written in the postmortem and never entered in a tracker.

## Done when

- Every customer-facing service has an SLO, burn-rate alerts and tested rules in CI.
- No rule depends on counting an empty vector; every scraped job has an absence rule.
- An external dead-man's switch pages when alerting stops, proven by a test.
- Log and error-tracker scrubbing is unit-tested.
- Backups alert on staleness; the last restore drill has a measured time within the RTO.
- Runbooks carry status and last-run date; postmortem action items are tracked to closure.

## References

- [references/alert-rules.md](references/alert-rules.md): load when writing or reviewing alert rules, their
  tests or Alertmanager routing.
- [references/telemetry-hygiene.md](references/telemetry-hygiene.md): load when configuring loggers, an error
  tracker or tracing.
- [references/drills-postmortems.md](references/drills-postmortems.md): load when planning a restore drill,
  writing a runbook or a postmortem.

## Sources

- https://sre.google/sre-book/monitoring-distributed-systems/: symptoms over causes, four golden signals, verified
  2026-11-03.
- https://sre.google/workbook/alerting-on-slos/: multiwindow burn-rate parameters, verified 2026-11-03.
- https://prometheus.io/docs/prometheus/latest/querying/functions/: `absent`, `absent_over_time`, verified
  2026-11-03.
- https://prometheus.io/docs/prometheus/latest/configuration/unit_testing_rules/: `promtool test rules`, verified
  2026-11-03.
- https://runbooks.prometheus-operator.dev/runbooks/general/watchdog/: Watchdog purpose, verified 2026-11-03.
- https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html: data to exclude from logs, verified
  2026-11-03.
- https://docs.sentry.io/platforms/python/configuration/options/ and
  https://docs.sentry.io/platforms/python/data-management/sensitive-data/: PII, local variables, `before_send`,
  verified 2026-11-03.
- https://www.w3.org/TR/trace-context/: `traceparent`, `tracestate`, verified 2026-11-03.
- https://sre.google/sre-book/postmortem-culture/: blameless postmortems, verified 2026-11-03.
