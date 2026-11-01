# Load, stress and spike tests

Load when you plan a load, stress or spike test for a service.

## Contents

- The question each test answers
- When a SaaS needs a spike test
- Design
- Reading the result
- Tools

## The question each test answers

Per the k6 documentation (https://grafana.com/docs/k6/latest/testing-guides/test-types/, verified 2026-11-01):

| Test | Question |
|---|---|
| Smoke | Does the script work, and does the system respond correctly at minimal load? |
| Average load | Does the system hold its limits under expected normal use? |
| Stress | How does it behave at its limits, above the average? |
| Soak | Does it stay reliable over hours, with no leak or slow decay? |
| Spike | Does it survive and recover when load jumps suddenly and massively? |
| Breakpoint | Where is the capacity limit? |

The same page says no single type removes all risk, and that names vary between teams. Pick the types by the
failure you fear: a nightly batch that grows needs a soak test, a launch day needs a spike test.

## When a SaaS needs a spike test

A product that sends a campaign mail with a link, opens booking for a popular slot at a fixed time, has a
deadline everyone hits on the last day, or gets listed somewhere with a large audience. Source for the examples
of spike events (sales, launches, deadlines, rushes): the k6 spike testing page,
https://grafana.com/docs/k6/latest/testing-guides/test-types/spike-testing/ (verified 2026-11-01).

If none of those exist, an average-load and stress test are usually enough. Say so in the plan.

## Design

1. Write the question and the limits before the first run: for example, 95% of requests under a stated latency,
   error rate under a stated percentage, and back to normal within a stated time after the spike. Numbers come
   from the product's promises, not from the first measurement.
2. Model the traffic on the processes that spike, not on the whole site. A spike on a booking page hits the slot
   query and the write path, not the settings screens.
3. Shape: a very fast ramp, no plateau or a short one, a fast ramp down. Keep the shape simple; the k6 guide
   advises against repeated ups and downs because they hide the cause.
4. Run against an environment you own, with data volume and configuration like production (same database
   engine, same instance limits where cost allows). Never aim it at a third party's service or at production
   without the approval path in `safe-actions`.
5. Fake or sandbox the third parties the test would otherwise call, and record which parts were faked.
6. Watch the backend while it runs: CPU, memory, connection pool, queue depth, database locks, error logs. The
   k6 page calls backend monitoring a must.
7. Expect errors and a run that does not finish at first. Run, tune, repeat.

## Reading the result

Report per run: the shape, the peak, latency percentiles and error rate against the stated limits, the time to
return to normal after the peak, and the first resource that saturated. A pass on a smaller environment says the
code path survives; it does not say the production size does. State which one you measured.

## Tools

k6 is one example tool; its documentation is at https://grafana.com/docs/k6/latest/. Other load tools exist and
fit the same design. Verify flags and script syntax against the docs of the version you install, and check
availability with `command -v` first. This skill does not restate script syntax.
