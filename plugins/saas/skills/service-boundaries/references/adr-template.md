# ADR template: extraction

Copy to `docs/adr/NNNN-extract-[thing].md`. Every section is required; "not applicable" needs a reason.

```markdown
# NNNN: Extract [thing] into [runtime]

Status: proposed | accepted | superseded by NNNN
Date: YYYY-MM-DD
Owner (on-call, patching, release signing): [team or person]

## Measured baseline
Load script: bench/[script] (commit, data volume, concurrency, duration).
p50 / p95 / p99, throughput at plateau, CPU time vs wall time, memory per worker, queue wait, connections.

## Capacity calculation
Little's law with the real worker counts (pm.max_children x pods, Octane workers, queue processes).

## In-runtime fixes tried
| Fix | Result (measured) |

## Why not keep it in the monolith
Answer each: business decision? database bottleneck? distributed transaction? owner? traffic vs tuned capacity?
only language speed?

## Runtime-fit row
Workload, known PHP limit with source, extraction trigger, target runtime.

## Target
The numbers the new service must reach, measured the same way as the baseline.

## Boundary design
Control plane vs worker split; pull-only protocol; CONTRACT.md location; shared limits; key per relationship;
exp / purpose / jti for critical payloads; health semantics; bounds; shutdown order.

## Operational floor
CI tests plus race or sanitizer run; pinned toolchain; signed artifacts and SBOM; vulnerability scanning;
structured logs without personal data; errors-only tracking with PII off; metrics with bounded labels;
correlation ID across the boundary. Link each job.

## Revert criterion
The measured condition under which this moves back into the monolith, and by when it is checked.
```
