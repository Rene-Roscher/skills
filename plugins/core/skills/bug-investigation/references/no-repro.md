# When it does not reproduce

## Hypotheses

Rank them by likelihood given the facts. Each one needs code evidence and a way to decide it.

```text
| # | Hypothesis | Evidence (path:line) | Confirms it | Refutes it |
|---|---|---|---|---|
| 1 | The waiting worker returns after its timeout without the value | src/reports/cache.py:31 | wait time at or above the timeout in the failing events | value present when the error fires |
| 2 | The builder fails and releases its lock without writing | src/reports/build.py:58 | builder error events at the same time | no builder errors |
| 3 | The entry is evicted between write and read | cache eviction settings | eviction counter rising at that time | no evictions |
```

Use the facts: frequency, release, time pattern, affected tenants. A hypothesis that does not explain why the error
is rare or why it started when it did is weaker.

## Instrumentation

Propose the smallest measurement that separates the top hypotheses:

- A structured log line at the decision point, with the values that matter (durations, sizes, IDs, flags), never
  personal data or secrets.
- Extra context on the error event: a tag or field in the error tracker, so the next occurrence carries it.
- A counter or timer metric at the suspect step, when frequency matters more than single events.
- A capture behind a feature flag, limited to one tenant or a sample, for expensive diagnostics.

For each measurement, say which hypothesis it decides and what result would point where.

## Asking

```text
Could not reproduce: [what was tried, with the environment]
Hypotheses: [ranked table]
Proposed instrumentation: [each item, with the hypothesis it decides]
Needs your decision: deploy the instrumentation, or [other option]
```

## Not a substitute for the cause

- A null check or default value at the crash line. It moves the failure further down.
- A catch around the block, a retry, a longer timeout. They hide the next occurrence.
- A fix for hypothesis 1 "because it is the most likely". Ship it only if a measurement or reproduction confirms
  it, or the owner accepts it explicitly as a guarded experiment with the instrumentation in place.
