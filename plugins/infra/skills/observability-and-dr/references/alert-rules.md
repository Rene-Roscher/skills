# Alert rules that can fire

## Contents

- The empty-vector trap, proven
- Patterns
- Routing and the dead-man's switch

## The empty-vector trap, proven

`rules.yml`:

```yaml
groups:
  - name: edge
    rules:
      - alert: EdgeAllDownBroken          # never fires when all targets are down
        expr: count(up{job="edge"} == 1) == 0
        for: 1m
      - alert: EdgeAllDown
        expr: absent(up{job="edge"} == 1)
        for: 1m
        labels:
          severity: critical
          job: edge
```

`test.yml`:

```yaml
rule_files: [rules.yml]
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:                       # both targets go down after 2 minutes
      - series: 'up{job="edge",instance="a"}'
        values: '1 1 0 0 0 0 0'
      - series: 'up{job="edge",instance="b"}'
        values: '1 1 0 0 0 0 0'
    alert_rule_test:
      - eval_time: 6m
        alertname: EdgeAllDownBroken
        exp_alerts: []                  # silent
      - eval_time: 6m
        alertname: EdgeAllDown
        exp_alerts:
          - exp_labels: {severity: critical, job: edge}
  - interval: 1m
    input_series:                       # the job vanished from discovery
      - series: 'up{job="other",instance="c"}'
        values: '1 1 1 1 1 1 1'
    alert_rule_test:
      - eval_time: 6m
        alertname: EdgeAllDown
        exp_alerts:
          - exp_labels: {severity: critical, job: edge}
```

`promtool test rules test.yml` passes with Prometheus 2.53: the `count` rule stays silent and the `absent` rule
fires in both cases. `absent()` over a comparison returns a series without labels, so the rule sets the labels
that routing needs.

Also correct for "all down": `sum(up{job="edge"}) == 0` fires while the series exist, but not when the job
vanished; pair it with `absent(up{job="edge"})`.

## Patterns

- Absence per job: `absent_over_time(up{job="x"}[5m])` for each job alerting depends on.
- Freshness of a pushed or batch metric: `time() - backup_last_success_timestamp_seconds > [interval × 1.5]`, plus
  `absent(backup_last_success_timestamp_seconds)`.
- Gauges every replica exports (queue depth, a config value): `max by (queue) (...)`, not `sum`.
- Ratios: guard the denominator, `sum(rate(errors[5m])) / sum(rate(requests[5m])) > 0.05 and sum(rate(requests[5m])) > 1`,
  otherwise a quiet night divides by zero and produces no series.
- Every rule: `for:` long enough to skip one scrape failure, `runbook_url` and `summary` annotations, and a test
  that fires and one that stays quiet.

## Routing and the dead-man's switch

- Alertmanager root route sends `severity: critical` to a paging receiver with acknowledgement, a short
  `repeat_interval`, and nothing else on that receiver. Warnings go to a ticket or chat receiver.
- The `Watchdog` alert (always firing) routes to a heartbeat URL at an external service with its own pager, with a
  `repeat_interval` shorter than that service's timeout. Never to `null`.
- Inhibit warnings while the matching critical alert fires, not the other way round.
- Test: `amtool config routes test --config.file=alertmanager.yml severity=critical` shows the paging receiver.
